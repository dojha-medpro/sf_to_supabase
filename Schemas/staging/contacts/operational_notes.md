# Operational Notes — staging.contact

## Partitioning
- Partitioned by **load snapshot day**: `_partition_date`
- Historical field dates (`application_date`, `contract_effective_date`, etc.) are preserved in columns
- Late files land under the day they are processed; CDC uses `last_modified_at` to classify changes

## De-dup order
- For duplicate keys within a day, keep row with highest `last_modified_at`; if tied/missing, keep last seen

## Header management
- Mapping lives in `mappings/contact__<report>.yaml`
- Add a header snapshot under `mappings/header_snapshots/` whenever Salesforce changes the report

## PII handling
- Contains PII; never commit raw CSVs to Git (`reports/` is git-ignored)
- Share/retain raw files only in approved secure storage

## Known quirks
- Free-text fields may include commas/newlines—ensure CSV exports are quoted
- `email_opt_out` may appear as `True/False`, `Yes/No`, or `1/0`; normalize during load
