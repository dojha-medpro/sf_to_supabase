# Operational Notes — staging.job_applicant

## Partitioning
- Partition on **record creation time**: `_partition_date = created_at::date`
- **Late backfills** from Salesforce will land in **past partitions**; ensure your loader supports inserting older partitions and your QA monitors back-in-time changes

## De-dup order
- Within a partition day, prefer the row with the highest `last_modified_at`; otherwise keep the last encountered

## Header management
- Authoritative mapping lives at `mappings/job_applicant__<report>.yaml`
- Add a header snapshot in `mappings/header_snapshots/` whenever Salesforce changes the report headers

## CDC interplay
- `last_modified_at` is captured to classify **new vs. changed** records when promoting to `core`
- `stage_name` and status fields can be used in downstream wide/long views, but **CDC logic** should hinge on checksums of selected columns in `core`

## Known quirks
- `interview_availability` is free-form; keep as text to avoid parse errors
- Some orgs emit both `Application Status` and a picklist label; keep both (`application_status`, `application_status_pick`)
