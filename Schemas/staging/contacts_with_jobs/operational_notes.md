# Operational Notes — staging.contacts_with_jobs

## Partitioning
- Partition by **load snapshot day**: `_partition_date`
- This report lacks a reliable “Created Date” for the applicant; use `last_modified_at` for CDC when promoting to `core`

## De-dup order
- For duplicate keys within a day, prefer the row with the highest `last_modified_at`; otherwise keep the last seen

## Header management
- Authoritative mapping lives at `mappings/contacts_with_jobs__<report>.yaml`
- Add a header snapshot in `mappings/header_snapshots/` whenever Salesforce changes the report headers
- Note there are **two** “Job Applicant ID” columns; keep both mapped as `job_applicant_sfid` and `job_applicant_alt_id`

## Data quirks
- Duration fields (`time_am_to_hiring_manager`, `time_sa_to_hiring_manager`) may be formatted inconsistently; store as text unless you standardize units
- `days_with_hiring_manager` may be computed in Salesforce; validate it remains numeric

## PII & security
- Contains PII; raw CSVs remain in `reports/` (git-ignored) and should be shared only via secure storage
