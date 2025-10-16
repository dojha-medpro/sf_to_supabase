# Staging — Placement History (Field/Event log)

**Source report**: https://surestaff.lightning.force.com/lightning/r/Report/00Ocx000005l1AfEAI/view?queryScope=userFolders  
**Grain**: One row per **history event** on a placement  
**Stable key (composite)**: (`placement_sfid`, `edited_at`, `field_event`)  
**Partition key**: `edited_at` (event timestamp) → `_partition_date = edited_at::date`  
**Cross-object link**: `placement_sfid` (primary); `job_applicant` is a descriptive label in this report.

## Column rename (Salesforce → staging)
- Placement: ID → `placement_alt_id`  
- Placement: Placement ID → `placement_sfid`  
- Placement: Owner Name → `owner_name`  
- Placement: Created Date → `placement_created_at`  
- Candidate → `candidate`  
- Job Applicant → `job_applicant`  
- Field / Event → `field_event`  
- Old Value → `old_value`  
- New Value → `new_value`  
- Edit Date → `edited_at`  
- Placement: Last Modified Date → `last_modified_at`  
- Job Applicant Stage → `job_applicant_stage`

> Naming: lower_snake_case; strip/replace `:`, `/`, spaces, and dashes per Postgres/Supabase rules.

## Coercions & normalizations
- `edited_at`, `last_modified_at`: **timestamptz**  
- `placement_created_at`: **date** (or timestamptz if report provides time)  
- `field_event`, `candidate`, `job_applicant`, `owner_name`, `job_applicant_stage`: **trim**  
- `old_value`, `new_value`: **text** (free-form; do not coerce)

## Null policy
Treat as NULL: `""`, `NULL`, `N/A`, `n/a`, `null`.

## Required at staging
- `placement_sfid`, `edited_at`, `field_event` (composite event key)  
- `_partition_date`, `_file_name`, `_source_report` (operational metadata)

## Duplicate policy (same event key)
If duplicates exist for the same (`placement_sfid`, `edited_at`, `field_event`) within a partition:
- Prefer the row with the **longest `new_value`** (heuristic for completeness); if tie, keep the **last encountered**.

## Retention (staging)
Keep **180 days** of `_partition_date` partitions; archive older externally.

## Sensitivity
Contains candidate/placement context and status changes. Treat as **confidential**.
