"""PostgreSQL COPY Bulk Loader - High-performance loading to Supabase."""
import os
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from typing import Optional
from datetime import datetime
from etl.db_connection import connect_with_retry


class BulkLoader:
    """Loads CSV data to PostgreSQL using COPY for high performance."""
    
    def __init__(self):
        self.database_url = os.environ.get('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not set")
    
    def load_csv(self, csv_file: str, table_name: str, 
                 load_date: str, file_name: str, mapping_file: str, 
                 load_id: Optional[int] = None, natural_key: Optional[list] = None) -> int:
        """
        Load a CSV file to a staging table using PostgreSQL COPY.
        
        Returns:
            Number of rows loaded
        """
        allowed_tables = {
            'staging.contacts',
            'staging.form_submission', 
            'staging.job_applicant',
            'staging.jobs_and_placements',
            'staging.contacts_with_jobs',
            'staging.job_applicant_history',
            'staging.placement_history'
        }
        
        if table_name not in allowed_tables:
            raise ValueError(f"Invalid table name: {table_name}")
        
        # Use robust connection with retry logic and keep-alive for automated loads
        conn = connect_with_retry(autocommit=True)
        cursor = conn.cursor()
        
        if load_id is None:
            load_id = self._start_load(cursor, load_date, table_name, file_name, mapping_file)
        
        try:
            # Get column names from CSV header
            with open(csv_file, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                csv_columns = first_line.split(',')
            
            # Determine load strategy based on natural_key
            if natural_key and len(natural_key) > 0:
                # UPSERT MODE: Delete existing records, then insert new ones
                # This works without schema changes (no need to alter PRIMARY KEYs)
                
                self._update_progress(cursor, load_id, 'UPSERT: Loading to temp table', 50)
                
                # Create temp table with same structure as target
                temp_table = f"temp_{table_name.split('.')[-1]}_{load_id}"
                create_temp = sql.SQL("CREATE TEMP TABLE {} AS SELECT * FROM {} WHERE 1=0").format(
                    sql.Identifier(temp_table),
                    sql.Identifier(*table_name.split('.'))
                )
                cursor.execute(create_temp)
                
                # Load CSV to temp table using COPY
                with open(csv_file, 'r', encoding='utf-8') as f:
                    columns_sql = sql.SQL(', ').join([sql.Identifier(col) for col in csv_columns])
                    copy_query = sql.SQL("COPY {} ({}) FROM STDIN WITH CSV HEADER DELIMITER ','").format(
                        sql.Identifier(temp_table),
                        columns_sql
                    )
                    cursor.copy_expert(copy_query.as_string(cursor), f)
                
                self._update_progress(cursor, load_id, 'UPSERT: Removing old records', 65)
                
                # Delete existing records with matching natural keys
                # Build WHERE clause: WHERE (natural_key_col1, natural_key_col2) IN (SELECT ... FROM temp)
                key_cols = sql.SQL(', ').join([sql.Identifier(col) for col in natural_key])
                delete_query = sql.SQL("""
                    DELETE FROM {target} 
                    WHERE ({keys}) IN (
                        SELECT {keys} FROM {temp}
                    )
                """).format(
                    target=sql.Identifier(*table_name.split('.')),
                    keys=key_cols,
                    temp=sql.Identifier(temp_table)
                )
                cursor.execute(delete_query)
                deleted_count = cursor.rowcount
                
                if deleted_count > 0:
                    self._update_progress(cursor, load_id, f'UPSERT: Deleted {deleted_count} old records', 70)
                    print(f"UPSERT: Deleted {deleted_count} existing records")
                
                self._update_progress(cursor, load_id, 'UPSERT: Inserting new records', 75)
                
                # Insert all records from temp table
                insert_query = sql.SQL("""
                    INSERT INTO {target} ({cols})
                    SELECT {cols} FROM {temp}
                """).format(
                    target=sql.Identifier(*table_name.split('.')),
                    cols=columns_sql,
                    temp=sql.Identifier(temp_table)
                )
                cursor.execute(insert_query)
                
                self._update_progress(cursor, load_id, 'UPSERT: Complete', 85)
                print(f"UPSERT MODE: Merged data using natural key: {natural_key}")
                
            else:
                # INSERT MODE: No natural key, just append all records (for history/event tables)
                self._update_progress(cursor, load_id, 'INSERT: Loading to database', 60)
                
                with open(csv_file, 'r', encoding='utf-8') as f:
                    columns_sql = sql.SQL(', ').join([sql.Identifier(col) for col in csv_columns])
                    copy_query = sql.SQL("COPY {} ({}) FROM STDIN WITH CSV HEADER DELIMITER ','").format(
                        sql.Identifier(*table_name.split('.')),
                        columns_sql
                    )
                    cursor.copy_expert(copy_query.as_string(cursor), f)
                
                print(f"INSERT MODE: Appended all records (no natural key)")
                
            self._update_progress(cursor, load_id, 'Counting rows', 85)
            
            count_query = sql.SQL("SELECT COUNT(*) FROM {} WHERE _file_name = %s").format(
                sql.Identifier(*table_name.split('.'))
            )
            cursor.execute(count_query, (file_name,))
            result = cursor.fetchone()
            row_count = result[0] if result else 0
            
            self._update_progress(cursor, load_id, 'Complete', 95)
            self._complete_load(cursor, load_id, row_count, 'success')
            
            cursor.close()
            conn.close()
            
            return row_count
            
        except Exception as e:
            self._complete_load(cursor, load_id, 0, 'failed', str(e))
            cursor.close()
            conn.close()
            raise
    
    def _start_load(self, cursor, load_date: str, table_name: str, 
                   file_name: str, mapping_file: str) -> int:
        """Record load start in load_history."""
        cursor.execute("""
            INSERT INTO load_history 
            (load_date, target_table, file_name, mapping_file, status, current_stage, progress_percent, started_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (load_date, table_name, file_name, mapping_file, 'running', 'Loading to database', 0, datetime.now()))
        
        result = cursor.fetchone()
        if not result:
            raise RuntimeError("Failed to create load_history record")
        return result[0]
    
    def _update_progress(self, cursor, load_id: int, stage: str, progress: int):
        """Update progress in load_history."""
        cursor.execute("""
            UPDATE load_history 
            SET current_stage = %s, progress_percent = %s
            WHERE id = %s
        """, (stage, progress, load_id))
    
    def _complete_load(self, cursor, load_id: int, rows_loaded: int, 
                      status: str, error_message: Optional[str] = None):
        """Record load completion in load_history."""
        cursor.execute("""
            UPDATE load_history 
            SET rows_loaded = %s, status = %s, error_message = %s, completed_at = %s
            WHERE id = %s
        """, (rows_loaded, status, error_message, datetime.now(), load_id))
