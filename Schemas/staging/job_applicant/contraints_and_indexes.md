# Constraints & Indexes — staging.job_applicant

## Constraints (intent)
- NOT NULL: `job_applicant_sfid`, `created_at`, `_partition_date`, `_file_name`, `_source_report`
- Soft uniqueness (post de-dupe): unique on `(job_applicant_sfid, _partition_date)`

> Staging favors **observability over hard failures**; strict enforcement happens in `core`.

## Indexes
- B-tree on `_partition_date` (frequent filter)
- B-tree on `job_applicant_sfid`
- Optional composite `(job_applicant_sfid, _partition_date)` to speed de-dupe and CDC matching
- B-tree on `stage_name` if stage analytics in staging need acceleration

## Quality signals per load
- Duplicate key count per `_partition_date`
- Rows with unparseable timestamps/dates
- Header drift vs. mapping (unexpected/missing columns)
