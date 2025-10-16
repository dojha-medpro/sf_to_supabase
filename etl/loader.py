"""PostgreSQL COPY Bulk Loader - High-performance loading to Supabase."""
import os
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from typing import Optional
from datetime import datetime


class BulkLoader:
    """Loads CSV data to PostgreSQL using COPY for high performance."""
    
    def __init__(self):
        self.database_url = os.environ.get('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not set")
    
    def load_csv(self, csv_file: str, table_name: str, 
                 load_date: str, file_name: str, mapping_file: str) -> int:
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
        
        conn = psycopg2.connect(self.database_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        load_id = self._start_load(cursor, load_date, table_name, file_name, mapping_file)
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                copy_query = sql.SQL("COPY {} FROM STDIN WITH CSV HEADER DELIMITER ','").format(
                    sql.Identifier(*table_name.split('.'))
                )
                cursor.copy_expert(copy_query.as_string(cursor), f)
            
            count_query = sql.SQL("SELECT COUNT(*) FROM {} WHERE _file_name = %s").format(
                sql.Identifier(*table_name.split('.'))
            )
            cursor.execute(count_query, (file_name,))
            result = cursor.fetchone()
            row_count = result[0] if result else 0
            
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
            (load_date, target_table, file_name, mapping_file, status, started_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (load_date, table_name, file_name, mapping_file, 'running', datetime.now()))
        
        result = cursor.fetchone()
        if not result:
            raise RuntimeError("Failed to create load_history record")
        return result[0]
    
    def _complete_load(self, cursor, load_id: int, rows_loaded: int, 
                      status: str, error_message: Optional[str] = None):
        """Record load completion in load_history."""
        cursor.execute("""
            UPDATE load_history 
            SET rows_loaded = %s, status = %s, error_message = %s, completed_at = %s
            WHERE id = %s
        """, (rows_loaded, status, error_message, datetime.now(), load_id))
