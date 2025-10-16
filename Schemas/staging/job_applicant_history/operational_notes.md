# Operational Notes — staging.job_applicant_history

## Partitioning
- Partition by **event time**: `_partition_date = edited_at::date`
- Late backfills from Salesforce properly land in **past partitions**; ensure the loader supports inserting older partitions and QA monitors back-in-time spikes

## De-dup order
- For duplicate composite keys, keep the row with the **longest `new_value`**; if tie, keep the **last seen**. (Adjust the heuristic if you prefer `latest by _extract_ts`.)

## Header management
- Mapping lives at `mappings/job_applicant_history__<report>.yaml`
- Add a header snapshot in `mappings/header_snapshots/` whenever Salesforce changes the report headers

## CDC interplay
- This table is already **event-level**; in `core`, you can:
  - Build an **event log** as-is
  - Or **pivot/rollup** to reconstruct current state by applying latest `new_value` per field
- Be mindful that `old_value/new_value` are free-form strings; type casting should be done in curated views for specific fields only

## Known quirks
- `field_event` names may evolve; map aliases if Salesforce admins rename fields
- Some edits can produce multiple events with identical timestamps; the composite key still disambiguates via `field_event`
- Values may include commas/newlines; ensure CSV quotes are preserved

## PII & security
- Do not commit raw CSVs; follow `reports/` guidance. Restrict access due to potential visibility into sensitive status changes.
