# Salesforce to Supabase ETL Pipeline

## Overview
Production-ready Python Flask ETL application for loading Salesforce CSV exports into Supabase staging tables. Supports both manual uploads and **automated daily processing via CloudMailin email webhooks**. Features real-time progress tracking, YAML-based transformations, QA validation, high-performance PostgreSQL COPY loading, and comprehensive error handling with quarantine system.

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

### 5. CloudMailin Webhook Integration (NEW - 2025-10-16)
- **Automated email processing**: Receives Salesforce CSV exports via CloudMailin
- **Webhook endpoint**: `/webhook/cloudmailin` with token-based authentication
- **Auto-detection**: Automatically detects mapping based on CSV filename patterns
- **Dual attachment support**: Handles both base64-encoded and cloud storage URLs
- **Production security**:
  - Token authentication (CLOUDMAILIN_WEBHOOK_TOKEN env var) - fails closed
  - Strict HTTPS-only URL validation with domain allowlist
  - SSRF protection: validates hostnames against S3, GCS, Azure, CloudMailin
  - 100 MB size limit and 30-second timeout on downloads
- **See**: `CLOUDMAILIN_SETUP.md` for complete setup guide

## Deployment
- **Development**: Flask dev server on port 5000
- **Production**: Gunicorn with autoscale deployment configured
- **Database**: Supabase PostgreSQL via DATABASE_URL environment variable
- **Webhook**: CloudMailin integration for automated daily processing

## Future Enhancements (Planned)
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
- 2025-10-16: **Fixed critical encoding bug for all file types**:
  - Changed ALL encodings (Windows-1252, ISO-8859-1, etc.) to use 'replace' mode instead of 'strict'
  - Previously: only tested 100KB sample with 'strict' mode → crashed on bad bytes in full file
  - Now: uses 'replace' mode universally → substitutes bad characters with � instead of crashing
  - Handles corrupt/mixed-encoding CSVs gracefully without quarantining valid data
- 2025-10-16: **Successfully loaded production data**:
  - form_submission: 317,360 rows ✅
  - contacts (candidates): 252,919 rows ✅
  - job_applicant: 62,448 rows ✅
  - contacts_with_jobs: 62,444 rows ✅
  - job_applicant_history: 646,729 rows ✅
- 2025-10-16: **Removed natural key validation for history tables**:
  - job_applicant_history and placement_history now allow duplicate events (correct behavior)
  - Database PRIMARY KEY constraints removed to support legitimate duplicate historical events
- 2025-10-16: **Fixed jobs_and_placements mapping**:
  - Changed end_of_assignment_survey_returned from boolean to date (stores actual date, not yes/no)
  - Removed natural key validation (jobs can have multiple placements or no placements)
- 2025-10-16: **Completed CloudMailin webhook integration for automated daily processing**:
  - Created `/webhook/cloudmailin` endpoint to receive email webhooks
  - Auto-detects YAML mapping from CSV filename patterns (contact→contacts.yaml, job_applicant→job_applicants.yaml, etc.)
  - Supports both base64 attachments and cloud storage URLs (S3, GCS, Azure)
  - **Production-grade security**:
    - Token authentication with X-CloudMailin-Token header (fails closed if not configured)
    - Strict HTTPS-only URL validation with hostname parsing
    - Domain allowlist prevents SSRF attacks (only trusted cloud storage domains)
    - 100 MB size limit and 30-second timeout
  - Reuses existing ETL pipeline (validator, transformer, loader)
  - Complete setup guide in CLOUDMAILIN_SETUP.md
  - Test script provided: test_cloudmailin_webhook.py

## User Preferences
- Flask framework preferred over Streamlit
- Focus on bulk loading first, Outlook automation later
- Failed files should be quarantined with notifications

## Test Data
- Sample CSV available: `test_contacts_sample.csv` (3 rows)
- Mapping: `Mappings/contacts.yaml`
