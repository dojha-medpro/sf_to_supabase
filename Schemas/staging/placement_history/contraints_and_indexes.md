# Constraints & Indexes — staging.placement_history

## Constraints (intent)
- NOT NULL: `placement_sfid`, `field_event`, `edited_at`, `_partition_date`, `_file_name`, `_source_report`
- Soft uniqueness (post de-dupe): unique on (`placement_sfid`, `edited_at`, `field_event`)

> Staging favors **observability**; enforce stricter guarantees in `core`.

## Indexes
- B-tree on `_partition_date` (common filter)
- B-tree on `placement_sfid`
- Composite B-tree on (`placement_sfid`, `edited_at`)
- B-tree on `field_event`
- Optional B-tree on `job_applicant_stage` for event-stage analytics

## Quality signals per load
- Duplicate event key count per `_partition_date`
- Rows with unparseable `edited_at`
- Spikes in a single `field_event` (possible systemic change)
- Header drift vs. mapping (unexpected/missing columns)
