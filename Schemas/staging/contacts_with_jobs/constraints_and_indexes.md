# Constraints & Indexes — staging.contacts_with_jobs

## Constraints (intent)
- NOT NULL: `job_applicant_sfid`, `_partition_date`, `_file_name`, `_source_report`
- Soft uniqueness (post de-dupe): unique on `(job_applicant_sfid, _partition_date)`

> Staging is a landing zone; prefer **observability** and handle strict rules in `core`.

## Indexes
- B-tree on `_partition_date` (frequent filter)
- B-tree on `job_applicant_sfid`
- Optional composite `(job_applicant_sfid, _partition_date)` for fast de-dupe/CDC match
- B-tree on `contact_sfid` (join helper)
- Optional B-tree on `job_status` if you explore stage metrics directly in staging

## Quality signals per load
- Duplicate key count per `_partition_date`
- Rows with unparseable timestamps/dates
- Non-numeric `days_with_hiring_manager` rate (if expecting integers)
- Header drift vs. mapping (unexpected/missing columns)
