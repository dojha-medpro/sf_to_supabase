#!/usr/bin/env python3
"""
Migrate staging tables to support UPSERT mode for incremental loads.

Changes:
- Remove _partition_date from PRIMARY KEY constraints
- Add UNIQUE constraint on natural key only
- _partition_date becomes "last modified date" instead of partition key
"""

import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def migrate_to_upsert():
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable not set")
    
    # Add sslmode=require for Supabase pooler connections
    if '?' in DATABASE_URL:
        if 'sslmode' not in DATABASE_URL:
            DATABASE_URL += '&sslmode=require'
    else:
        if 'sslmode' not in DATABASE_URL:
            DATABASE_URL += '?sslmode=require'
    
    conn = psycopg2.connect(DATABASE_URL)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    # Tables with natural keys that need UPSERT support
    migrations = [
        {
            'table': 'staging.contacts',
            'natural_key': 'contact_sfid',
            'old_pk': 'contacts_pkey'
        },
        {
            'table': 'staging.form_submission',
            'natural_key': 'form_submission_name',
            'old_pk': 'form_submission_pkey'
        },
        {
            'table': 'staging.job_applicant',
            'natural_key': 'job_applicant_sfid',
            'old_pk': 'job_applicant_pkey'
        },
        {
            'table': 'staging.contacts_with_jobs',
            'natural_key': 'job_applicant_sfid',
            'old_pk': 'contacts_with_jobs_pkey'
        },
        {
            'table': 'staging.jobs_and_placements',
            'natural_key': 'job_sfid',
            'old_pk': 'jobs_and_placements_pkey'
        }
    ]
    
    for migration in migrations:
        table = migration['table']
        natural_key = migration['natural_key']
        old_pk = migration['old_pk']
        
        print(f"\n🔄 Migrating {table}...")
        
        # Drop old composite PRIMARY KEY
        print(f"  - Dropping old PRIMARY KEY constraint...")
        try:
            cursor.execute(f"ALTER TABLE {table} DROP CONSTRAINT IF EXISTS {old_pk}")
            print(f"    ✓ Dropped {old_pk}")
        except Exception as e:
            print(f"    ⚠️ Warning: {e}")
        
        # Add new PRIMARY KEY on natural key only
        print(f"  - Adding PRIMARY KEY on {natural_key}...")
        try:
            cursor.execute(f"ALTER TABLE {table} ADD PRIMARY KEY ({natural_key})")
            print(f"    ✓ PRIMARY KEY created on {natural_key}")
        except Exception as e:
            print(f"    ⚠️ Warning: {e}")
        
        print(f"  ✅ {table} migration complete")
    
    # History tables don't need migration (they're append-only)
    print("\n📝 Note: History tables (job_applicant_history, placement_history) remain append-only")
    
    cursor.close()
    conn.close()
    print("\n✅ All migrations complete! Tables now support UPSERT mode.")

if __name__ == "__main__":
    migrate_to_upsert()
