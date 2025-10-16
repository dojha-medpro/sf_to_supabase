import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_staging_tables():
    """Create all staging tables in Supabase based on schema documentation."""
    
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable not set")
    
    conn = psycopg2.connect(DATABASE_URL)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    print("Creating staging schema if not exists...")
    cursor.execute("CREATE SCHEMA IF NOT EXISTS staging")
    
    tables = {
        "staging.contacts": """
            CREATE TABLE IF NOT EXISTS staging.contacts (
                contact_sfid text NOT NULL,
                record_type text,
                account_id text,
                first_name text,
                last_name text,
                email text,
                email_opt_out boolean,
                applicant_history text,
                application_date date,
                specialty text,
                candidate_status text,
                employment_status text,
                green_card_filing_status text,
                initial_documents_status text,
                intl_employment_status text,
                lead_status text,
                licensure_status text,
                medpro_department text,
                intl_pipeline_summary text,
                intl_stage_contract_returned text,
                intl_healthcare_vendor text,
                intl_interviewer text,
                contract_effective_date date,
                date_deployed date,
                last_modified_at timestamptz,
                _partition_date date NOT NULL,
                _file_name text NOT NULL,
                _source_report text NOT NULL,
                _extract_ts timestamptz,
                _mapping_version text,
                _raw_hash text,
                _loaded_at timestamptz DEFAULT NOW(),
                PRIMARY KEY (contact_sfid, _partition_date)
            )
        """,
        
        "staging.form_submission": """
            CREATE TABLE IF NOT EXISTS staging.form_submission (
                form_submission_id text NOT NULL,
                form_submission_name text,
                created_at timestamptz NOT NULL,
                contact_candidate text,
                application text,
                job text,
                record_type text,
                first_name text,
                last_name text,
                email text,
                form_type text,
                phone text,
                city text,
                zip_code text,
                job_city text,
                job_state text,
                form text,
                utm_source text,
                utm_medium text,
                utm_campaign text,
                source text,
                marketing_campaign text,
                area_of_assignment text,
                last_modified_at timestamptz,
                _partition_date date NOT NULL,
                _file_name text NOT NULL,
                _source_report text NOT NULL,
                _extract_ts timestamptz,
                _mapping_version text,
                _raw_hash text,
                _loaded_at timestamptz DEFAULT NOW(),
                PRIMARY KEY (form_submission_id, _partition_date)
            )
        """,
        
        "staging.job_applicant": """
            CREATE TABLE IF NOT EXISTS staging.job_applicant (
                job_applicant_sfid text NOT NULL,
                job_applicant_alt_id text,
                created_at timestamptz NOT NULL,
                candidate text,
                account text,
                applicant_source text,
                job_title text,
                application_status text,
                application_status_pick text,
                date_offer_received date,
                interview_availability text,
                submitted_to_hm_at timestamptz,
                submitted_to_hm_end_date date,
                stage_name text,
                last_modified_at timestamptz,
                _partition_date date NOT NULL,
                _file_name text NOT NULL,
                _source_report text NOT NULL,
                _extract_ts timestamptz,
                _mapping_version text,
                _raw_hash text,
                _loaded_at timestamptz DEFAULT NOW(),
                PRIMARY KEY (job_applicant_sfid, _partition_date)
            )
        """,
        
        "staging.jobs_and_placements": """
            CREATE TABLE IF NOT EXISTS staging.jobs_and_placements (
                job_sfid text NOT NULL,
                placement_sfid text,
                start_date date,
                end_date date,
                original_start_date date,
                original_end_date date,
                original_placement_start_date date,
                medpro_department text,
                orientation_start_date date,
                duration_of_assignment text,
                shift text,
                end_of_assignment_survey_returned boolean,
                bill_rate_base numeric,
                bill_rate numeric,
                bill_rate_overtime numeric,
                pay_rate numeric,
                pay_rate_base numeric,
                pay_rate_overtime numeric,
                bill_rate_holiday numeric,
                pay_rate_holiday numeric,
                last_modified_at timestamptz,
                placement_type text,
                international_placement_active boolean,
                _partition_date date NOT NULL,
                _file_name text NOT NULL,
                _source_report text NOT NULL,
                _extract_ts timestamptz,
                _mapping_version text,
                _raw_hash text,
                _loaded_at timestamptz DEFAULT NOW(),
                PRIMARY KEY (job_sfid, _partition_date)
            )
        """,
        
        "staging.contacts_with_jobs": """
            CREATE TABLE IF NOT EXISTS staging.contacts_with_jobs (
                job_applicant_sfid text NOT NULL,
                job_applicant_alt_id text,
                contact_sfid text,
                full_name text,
                email text,
                account_name text,
                applicant_source text,
                job_title text,
                job_status text,
                submitted_to_hm_at timestamptz,
                days_with_hiring_manager integer,
                time_am_to_hiring_manager text,
                time_sa_to_hiring_manager text,
                date_offer_received date,
                interview_availability text,
                job_city_state text,
                job_source text,
                last_modified_at timestamptz,
                _partition_date date NOT NULL,
                _file_name text NOT NULL,
                _source_report text NOT NULL,
                _extract_ts timestamptz,
                _mapping_version text,
                _raw_hash text,
                _loaded_at timestamptz DEFAULT NOW(),
                PRIMARY KEY (job_applicant_sfid, _partition_date)
            )
        """,
        
        "staging.job_applicant_history": """
            CREATE TABLE IF NOT EXISTS staging.job_applicant_history (
                job_applicant_sfid text NOT NULL,
                job_applicant_alt_id text,
                candidate text,
                field_event text NOT NULL,
                old_value text,
                new_value text,
                edited_at timestamptz NOT NULL,
                _partition_date date NOT NULL,
                _file_name text NOT NULL,
                _source_report text NOT NULL,
                _extract_ts timestamptz,
                _mapping_version text,
                _raw_hash text,
                _loaded_at timestamptz DEFAULT NOW(),
                PRIMARY KEY (job_applicant_sfid, edited_at, field_event, _partition_date)
            )
        """,
        
        "staging.placement_history": """
            CREATE TABLE IF NOT EXISTS staging.placement_history (
                placement_sfid text NOT NULL,
                placement_alt_id text,
                owner_name text,
                placement_created_at timestamptz,
                candidate text,
                job_applicant text,
                field_event text NOT NULL,
                old_value text,
                new_value text,
                edited_at timestamptz NOT NULL,
                last_modified_at timestamptz,
                job_applicant_stage text,
                _partition_date date NOT NULL,
                _file_name text NOT NULL,
                _source_report text NOT NULL,
                _extract_ts timestamptz,
                _mapping_version text,
                _raw_hash text,
                _loaded_at timestamptz DEFAULT NOW(),
                PRIMARY KEY (placement_sfid, edited_at, field_event, _partition_date)
            )
        """
    }
    
    for table_name, ddl in tables.items():
        print(f"Creating {table_name}...")
        cursor.execute(ddl)
        print(f"✓ {table_name} created successfully")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS load_history (
            id SERIAL PRIMARY KEY,
            load_date date NOT NULL,
            target_table text NOT NULL,
            file_name text NOT NULL,
            mapping_file text NOT NULL,
            rows_loaded integer,
            status text NOT NULL,
            error_message text,
            started_at timestamptz DEFAULT NOW(),
            completed_at timestamptz,
            quarantine_path text
        )
    """)
    print("✓ load_history table created successfully")
    
    cursor.close()
    conn.close()
    print("\n✅ All staging tables created successfully!")

if __name__ == "__main__":
    create_staging_tables()
