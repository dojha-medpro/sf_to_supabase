# Operational Notes — staging.form_submission

## Partitions
- Partitions are organized by **Created Date/Time** → `_partition_date = created_at::date`.
- **Late arrivals** (files delivered days later) should still land under the `_partition_date` derived from the row’s `created_at`. Document any exceptions.

## De-dup order
- Within the same `_partition_date`, if multiple rows share `form_submission_id`, pick the row with the **greatest `last_modified_at`**; if tied or missing, keep the last encountered.

## Header management
- The authoritative header list lives in `mappings/form_submission__<report>.yaml`.
- Any header change in Salesforce requires updating the mapping and adding a header snapshot. Loads should **warn** (or fail) on drift.

## Cross-object linking
- Primary soft link: **email (lowercased)** to Contact/Candidate.
- Expect collisions (shared emails, aliases). Do not enforce uniqueness at staging.

## PII handling
- Treat this dataset as **confidential**; do not commit raw files to Git. Follow `reports/` README guidance.

## Known quirks / risks
- **Partitioning on `created_at`**: if Salesforce backfills or edits historical records, they will land in **past partitions**. Ensure your load pipeline supports backfilled `_partition_date`s and that QA dashboards monitor back-in-time changes.
- **Free-text fields** (`form`, names, cities) may include commas/newlines; ensure CSVs are properly quoted at export.
