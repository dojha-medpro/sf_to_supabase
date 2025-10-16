# Staging — Job Applicant History (Field/Event log)

**Source report**: (https://surestaff.lightning.force.com/lightning/r/Report/00Ocx000005kwXZEAY/view?queryScope=userFolders) 
**Grain**: One row per **history event** for a job applicant  
**Stable key (composite)**: (`job_applicant_sfid`, `edited_at`, `field_event`)  
**Partition key**: `edited_at` (event timestamp); `_partition_date = edited_at::date`  
**Cross-object link**: `job_applicant_sfid`

## Column rename (Salesforce → staging)
- Job Applicant: ID → `job_applicant_alt_id`  
- Job Applicant: Job Applicant ID → `job_applicant_sfid`  
- Candidate → `candidate`  
- Field / Event → `field_event`  
- Old Value → `old_value`  
- New Value → `new_value`  
- Edit Date → `edited_at`

> Naming: lower_snake_case; strip/replace `:`, `/`, spaces, and dashes to satisfy Postgres/Supabase rules.

## Coercions & normalizations
- `edited_at`: **timestamptz** (Salesforce org TZ → store with timezone)  
- `field_event`: trim  
- `old_value`, `new_value`: **text** (free-form; may contain numbers/dates—do not coerce)  
- `candidate`: trim (label only)

## Null policy
Treat as NULL: `""`, `NULL`, `N/A`, `n/a`, `null`.

## Required at staging
- `job_applicant_sfid`, `edited_at`, `field_event` (composite event key)  
- `_partition_date`, `_file_name`, `_source_report` (operational metadata)

## Duplicate policy (same event key)
If duplicates exist for the same (`job_applicant_sfid`, `edited_at`, `field_event`) within a partition:
- Prefer the row with the **longest `new_value`** (heuristic for completeness); if tie, keep the **last encountered**.

## Retention (staging)
Keep **180 days** of `_partition_date` partitions (history is high-value for audits); archive older externally.

## Sensitivity
Contains candidate context and potentially sensitive status changes. Treat as **confidential**.
