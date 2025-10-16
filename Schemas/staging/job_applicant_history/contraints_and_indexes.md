# Constraints & Indexes — staging.job_applicant_history

## Constraints (intent)
- NOT NULL: `job_applicant_sfid`, `field_event`, `edited_at`, `_partition_date`, `_file_name`, `_source_report`
- Soft uniqueness (post de-dupe): unique on (`job_applicant_sfid`, `edited_at`, `field_event`)

> Staging favors **observability**; strict enforcement happens in `core`.

## Indexes
- B-tree on `_partition_date` (common filter)
- B-tree on `job_applicant_sfid`
- Composite B-tree on (`job_applicant_sfid`, `edited_at`)
- B-tree on `field_event` (handy for targeted QA and filtering)

## Quality signals per load
- Duplicate event key count per `_partition_date`
- Rows with unparseable `edited_at`
- High-volume changes on the same `field_event` (possible systemic issue)
- Header drift vs. mapping (unexpected/missing columns)
