# Operational Notes — staging.placement_history

## Partitioning
- Partition by **event time**: `_partition_date = edited_at::date`
- Late backfills will land in **past partitions**; ensure loader supports inserting older partitions and QA monitors back-in-time spikes

## De-dup order
- For duplicate composite keys, keep the row with the **longest `new_value`**; if tie, keep **last seen** (or switch to “latest by `_extract_ts`” if you capture that reliably)

## Header management
- Mapping lives at `mappings/placement_history__<report>.yaml`
- Capture a header snapshot in `mappings/header_snapshots/` whenever Salesforce changes report columns

## CDC interplay
- This dataset is itself an **event log**. In `core`, you can:
  - Keep an append-only event table for audits
  - Build **current placement state** by applying the latest `new_value` per `field_event`
  - Derive **stage transition timelines** using `job_applicant_stage` and relevant field changes

## Data quirks
- `old_value`/`new_value` may contain commas/newlines—ensure CSV exports are properly quoted
- `job_applicant` and `candidate` are labels in this report; don’t treat as IDs at staging

## PII & confidentiality
- Contains sensitive operational details. Do not commit raw CSVs; follow `reports/` folder guidance and secure storage practices.
