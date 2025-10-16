# Operational Notes — staging.jobs_and_placements

## Partitioning
- Partition by **load snapshot day**: `_partition_date`
- Use `last_modified_at` in promotion-to-core logic for CDC (new/changed rows)

## De-dup order
- Within a snapshot day, prefer the row with the highest `last_modified_at`; otherwise keep the last seen

## Header management
- Mapping lives at `mappings/jobs_and_placements__<report>.yaml`
- Add a header snapshot in `mappings/header_snapshots/` whenever Salesforce changes report columns

## Currency handling
- Strip `$`, commas, and whitespace from rate fields before casting to numeric
- Keep precision consistent across all rate columns (define in `core`)

## Data quirks
- `duration_of_assignment` can be numeric or textual depending on how the report is configured; standardize downstream if needed
- Some rows may have job IDs without placement IDs (or vice versa); do not enforce referential integrity in staging

## PII & confidentiality
- Contains sensitive rate information and placement context; raw CSVs must remain in the git-ignored `reports/` folder and be shared only via secure storage
