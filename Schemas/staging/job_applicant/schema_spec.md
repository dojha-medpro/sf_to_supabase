# Staging — Job Applicant

**Source report**: https://surestaff.lightning.force.com/lightning/r/Report/00Ocx000005kz5dEAA/view?queryScope=userFolders  
**Grain**: One row per **job applicant**  
**Stable key**: `Job Applicant: Job Applicant ID` → `job_applicant_sfid`  
**Partition key**: `created_at` (from **Created Date/Time**); `_partition_date = created_at::date`  
**Cross-object links**: `job_applicant_sfid` (primary); `candidate` and `account` are descriptive fields in this report (not guaranteed to be IDs)

## Column rename (Salesforce → staging)
- Created Date/Time → `created_at`  
- Job Applicant: Job Applicant ID → `job_applicant_sfid`  
- Job Applicant: ID → `job_applicant_alt_id`  
- Candidate → `candidate`  
- Account → `account`  
- Applicant Source → `applicant_source`  
- Job Title → `job_title`  
- Application Status → `application_status`  
- Application Status Pick → `application_status_pick`  
- Date Offer Received → `date_offer_received`  
- Interview Availability → `interview_availability`  
- Date/Time Submitted to Hiring Manager → `submitted_to_hm_at`  
- Date Submitted to Hiring Manager Ends → `submitted_to_hm_end_date`  
- Stage → `stage_name`  
- Job Applicant: Last Modified Date → `last_modified_at`

> Naming: lower_snake_case; strip/replace `:`, `/`, spaces, and dashes to satisfy Postgres/Supabase rules.

## Coercions & normalizations
- `created_at`, `submitted_to_hm_at`, `last_modified_at`: **timestamptz**  
- `date_offer_received`, `submitted_to_hm_end_date`: **date**  
- `email fields`: *none in this report*  
- `job_title`, `applicant_source`, `application_status`, `application_status_pick`, `stage_name`, `candidate`, `account`: **trim** whitespace  
- `interview_availability`: treat as **text** (free-form / may not be a strict date)

## Null policy
Treat as NULL: `""`, `NULL`, `N/A`, `n/a`, `null`.

## Required at staging
- `job_applicant_sfid` (key)  
- `created_at` (drives `_partition_date`)  
- `_partition_date`, `_file_name`, `_source_report` (operational metadata)

## Duplicate policy (same partition date)
If duplicates exist for `(job_applicant_sfid, _partition_date)`, keep the row with the **greatest `last_modified_at`**. If `last_modified_at` ties or is missing, keep the **last encountered** row.

## Retention (staging)
Keep **90 days** of `_partition_date` partitions; archive older externally.

## Sensitivity
Contains candidate/job context; treat as **confidential** even if direct PII is minimal here.
