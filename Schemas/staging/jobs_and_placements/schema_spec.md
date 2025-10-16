# Staging — Jobs & Placements (job-centric)

**Source report**: https://surestaff.lightning.force.com/lightning/r/Report/00Ocx000005l3h7EAA/view?queryScope=userFolders  
**Grain**: One row per **job** (with attached placement details)  
**Stable key**: `Job ID` → `job_sfid`  
**Partition key**: `_partition_date` (the **load snapshot date**; we also capture Salesforce `last_modified_at` for CDC)  
**Cross-object links**: `placement_sfid` (placement relationship)

## Column rename (Salesforce → staging)
- Job ID → `job_sfid`  
- Placement ID → `placement_sfid`  
- Start Date → `start_date`  
- End Date → `end_date`  
- Original Start Date → `original_start_date`  
- Original End Date → `original_end_date`  
- Original Placement Start Date → `original_placement_start_date`  
- MedPro Department → `medpro_department`  
- Orientation Start Date → `orientation_start_date`  
- Duration of Assignment → `duration_of_assignment`  
- Shift → `shift`  
- End of Assignment Survey Returned → `end_of_assignment_survey_returned`  
- Bill Rate - Base → `bill_rate_base`  
- Bill Rate → `bill_rate`  
- Bill Rate - Overtime → `bill_rate_overtime`  
- Pay Rate → `pay_rate`  
- Pay Rate - Base → `pay_rate_base`  
- Pay Rate - Overtime → `pay_rate_overtime`  
- Bill Rate - Holiday → `bill_rate_holiday`  
- Pay Rate - Holiday → `pay_rate_holiday`  
- Last Modified Date → `last_modified_at`  
- Placement Type → `placement_type`  
- International Placement Active → `international_placement_active`

> Naming: lower_snake_case; strip/replace `:`, `/`, spaces, and dashes per Postgres/Supabase rules.

## Coercions & normalizations
- Dates: `start_date`, `end_date`, `original_start_date`, `original_end_date`, `original_placement_start_date`, `orientation_start_date` → **date**  
- Timestamps: `last_modified_at` → **timestamptz**  
- Currency/rates: strip currency symbols/commas; cast to **numeric** (money-like)  
  - `bill_rate_base`, `bill_rate`, `bill_rate_overtime`, `pay_rate`, `pay_rate_base`, `pay_rate_overtime`, `bill_rate_holiday`, `pay_rate_holiday`
- Booleans: `end_of_assignment_survey_returned`, `international_placement_active` → **boolean** (accept `True/False`, `Yes/No`, `1/0`)  
- `duration_of_assignment`: prefer **integer** (days/weeks per your org standard); if non-numeric in source, land as text in staging and standardize downstream  
- Text fields (e.g., `medpro_department`, `shift`, `placement_type`): **trim** whitespace

## Null policy
Treat as NULL: `""`, `NULL`, `N/A`, `n/a`, `null`.

## Required at staging
- `job_sfid` (key)  
- `_partition_date`, `_file_name`, `_source_report` (operational metadata)

## Duplicate policy (same snapshot day)
If duplicates exist for `(job_sfid, _partition_date)`, keep the row with the **greatest `last_modified_at`**; if tie/missing, keep the **last encountered**.

## Retention (staging)
Keep **90 days** of `_partition_date` partitions; archive older externally.

## Sensitivity
Contains rate information and placement details; treat as **confidential**.
