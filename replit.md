# Salesforce to Supabase ETL Pipeline

## Overview
Production-ready Python Flask application for bulk loading Salesforce report CSVs into Supabase staging tables. Features automated transformation, QA validation, high-performance PostgreSQL COPY loading, and comprehensive error handling with quarantine system.

## Project Type
ETL Data Pipeline Application (Python Flask + PostgreSQL)

## Structure
- **etl/**: Core ETL modules (mapper, transformer, validator, loader, notifications)
- **Schemas/**: Database design documentation for staging tables
- **Mappings/**: YAML transformation rules mapping Salesforce → Supabase columns
- **templates/**: Flask HTML templates for upload UI and history dashboard
- **uploads/**: Temporary storage for uploaded CSVs (gitignored)
- **quarantine/**: Failed files storage with error logging (gitignored)

## Features Implemented (2025-10-16)

### 1. Database Schema
- Created 7 staging tables in Supabase:
  - `staging.contacts` - Contact/candidate master data
  - `staging.form_submission` - Form submission events
  - `staging.job_applicant` - Job applicant records
  - `staging.jobs_and_placements` - Jobs and placement data
  - `staging.contacts_with_jobs` - Job applicant-centric view with contact context
  - `staging.job_applicant_history` - Field/event history for job applicants
  - `staging.placement_history` - Field/event history for placements
- Each table includes operational metadata: `_partition_date`, `_file_name`, `_source_report`, `_loaded_at`
- `load_history` table tracks all ETL runs with status and error details

### 2. ETL Pipeline Components
- **YAML Mapping Parser**: Reads transformation rules from Mappings/ directory
- **CSV Transformer**: Applies header renames, data coercions (trim, lowercase, boolean, date, numeric)
- **QA Validator**: Header validation, duplicate detection, required field checks
- **Bulk Loader**: PostgreSQL COPY for high-performance inserts (SQL injection protected)
- **Notification Service**: Logs failures and successes to `etl_notifications.log`

### 3. Web Interface
- Upload page with file selector, mapping dropdown, partition date picker
- **Real-time progress tracking**: Visual progress bar shows current stage (upload, validation, transformation, loading) with percentage
- AJAX polling updates progress every 500ms during processing
- Load history dashboard showing past runs with status and error details
- Beautiful gradient UI with responsive design
- Flash messages for user feedback

### 4. Security & Safety
- SQL injection prevention using `psycopg2.sql.Identifier` and table whitelist
- File upload validation (100 MB limit, CSV only)
- Quarantine system for failed files with timestamped storage
- Comprehensive error logging and traceability

## How to Use

### Initial Bulk Load
1. Navigate to the Upload page
2. Select a Salesforce CSV export
3. Choose the matching YAML mapping (e.g., `contacts.yaml` for contact reports)
4. Set the partition date (defaults to today)
5. Click "Upload & Process"

### Pipeline Flow
1. **Upload** → File saved to uploads/
2. **QA Validation** → Headers checked, duplicates detected, required fields verified
3. **Transform** → CSV headers renamed, data coerced per mapping rules
4. **Load** → Bulk insert to Supabase staging table via PostgreSQL COPY
5. **Success** → Files cleaned up, success notification logged
6. **Failure** → File quarantined, error logged, user notified

### View History
- Go to History page to see all past loads
- View status (success/failed/running), row counts, errors, duration

## Deployment
- **Development**: Flask dev server on port 5000
- **Production**: Gunicorn with autoscale deployment configured
- **Database**: Supabase PostgreSQL via DATABASE_URL environment variable

## Future Enhancements (Planned)
- Daily Outlook automation via Microsoft Graph API
- Email notifications (SMTP or SendGrid integration)
- Native PostgreSQL table partitioning for better performance
- Enhanced CDC (Change Data Capture) processing
- Data dictionary and ERD generation

## Recent Changes
- 2025-10-16: Built complete bulk load ETL pipeline
- 2025-10-16: Created 7 Supabase staging tables (contacts, form_submission, job_applicant, jobs_and_placements, contacts_with_jobs, job_applicant_history, placement_history)
- 2025-10-16: Implemented QA validation framework
- 2025-10-16: Added SQL injection protection with table whitelist
- 2025-10-16: Configured deployment with gunicorn
- 2025-10-16: Connected to user's Supabase project (lkmtcqgoytxqpqhhfoon.supabase.co)
- 2025-10-16: **Completed real-time progress tracking** with:
  - Visual progress bar showing current stage (upload, validation, transformation, loading) and percentage
  - AJAX polling updates every 500ms during processing
  - JSON-based responses for all validation paths (consistent error handling)
  - Single load_history record per job with status transitions (running → success/failed)
  - BulkLoader accepts load_id parameter to update existing records (no duplicates)
  - Graceful error handling with visual feedback for all failure scenarios
- 2025-10-16: **Optimized validator for large files (317K+ rows)**:
  - Single-pass validation (was reading file 4x, now reads only 1x) - massive performance improvement
  - Progress updates every 50K rows during validation (user sees "Validating row 50,000..." messages)
  - Reduced validation time from 10+ minutes to ~1-2 minutes for large files
  - Memory-efficient: only stores minimal bookkeeping data
- 2025-10-16: **Fixed encoding detection bottleneck**:
  - Was reading entire 50+ MB file for encoding detection (VERY slow)
  - Now reads only first 100KB sample (0.028 seconds vs minutes)
  - Uses 'replace' mode for UTF-8 to gracefully handle any encoding issues
  - Improved frontend error handling to show error messages properly

## User Preferences
- Flask framework preferred over Streamlit
- Focus on bulk loading first, Outlook automation later
- Failed files should be quarantined with notifications

## Test Data
- Sample CSV available: `test_contacts_sample.csv` (3 rows)
- Mapping: `Mappings/contacts.yaml`
