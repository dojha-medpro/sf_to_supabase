# Staging — Contacts With Jobs (job-applicant centric)

**Source report**: https://surestaff.lightning.force.com/lightning/r/Report/00Ocx000005n9bxEAA/view?queryScope=userFolders  
**Grain**: One row per **job applicant** (contact joined to job context)  
**Stable key**: `Job Applicant ID` → `job_applicant_sfid`  
**Partition key**: `_partition_date` (the **load snapshot date**; we also capture Salesforce `last_modified_at` for CDC)  
**Cross-object links**: `job_applicant_sfid` (primary), `contact_sfid` (contact link)

## Column rename (Salesforce → staging)
- Full Name → `full_name`  
- Contact/Candidate ID → `contact_sfid`  
- Job Applicant ID → `job_applicant_sfid`  
- Job Applicant ID (duplicate column) → `job_applicant_alt_id`  
- Candidate Email → `email`  
- Account Name → `account_name`  
- Applicant Source → `applicant_source`  
- Job Title → `job_title`  
- Job Status → `job_status`  
- Date/Time Submitted to Hiring Manager → `submitted_to_hm_at`  
- Days with Hiring Manager → `days_with_hiring_manager`  
- Time: AM to Hiring Manager → `time_am_to_hiring_manager`  
- Time: SA to Hiring Manager → `time_sa_to_hiring_manager`  
- Date Offer Received → `date_offer_received`  
- Interview Availability → `interview_availability`  
- Job City State → `job_city_state`  
- Job Source → `job_source`  
- Last Modified Date → `last_modified_at`

> Naming: lower_snake_case; strip/replace `:`, `/`, spaces, and dashes to satisfy Postgres/Supabase rules.  
> Note: The report includes **two** “Job Applicant ID” columns; we keep both (`job_applicant_sfid`, `job_applicant_alt_id`) for traceability.

## Coercions & normalizations
- `email`: lowercase + trim  
- `submitted_to_hm_at`, `last_modified_at`: **timestamptz**  
- `date_offer_received`: **date**  
- `days_with_hiring_manager`: prefer **integer** if the report emits a number; otherwise store as text  
- `time_am_to_hiring_manager`, `time_sa_to_hiring_manager`: **text** (durations that may not be consistent)  
- Text fields (`full_name`, `account_name`, `applicant_source`, `job_title`, `job_status`, `job_source`, `job_city_state`, `interview_availability`): **trim** whitespace

## Null policy
Treat as NULL: `""`, `NULL`, `N/A`, `n/a`, `null`.

## Required at staging
- `job_applicant_sfid` (key)  
- `_partition_date`, `_file_name`, `_source_report` (operational metadata)

## Duplicate policy (same snapshot day)
If duplicates exist for `(job_applicant_sfid, _partition_date)`, keep the row with the **greatest `last_modified_at`**; if tie/missing, keep the **last encountered**.

## Retention (staging)
Keep **90 days** of `_partition_date` partitions; archive older externally.

## Sensitivity
Contains PII and job context. Treat as **confidential**.
