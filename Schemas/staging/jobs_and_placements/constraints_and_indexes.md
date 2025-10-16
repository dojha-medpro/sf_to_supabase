# Constraints & Indexes — staging.jobs_and_placements

## Constraints (intent)
- NOT NULL: `job_sfid`, `_partition_date`, `_file_name`, `_source_report`
- Soft uniqueness (post de-dupe): unique on `(job_sfid, _partition_date)`

> Staging is a landing zone; keep it permissive and enforce stricter guarantees in `core`.

## Indexes
- B-tree on `_partition_date` (frequent filter)
- B-tree on `job_sfid`
- Optional composite `(job_sfid, _partition_date)` to speed de-dupe/CDC match
- B-tree on `placement_sfid` (join helper)
- Optional B-tree on `last_modified_at` if you frequently filter by recency

## Quality signals per load
- Duplicate key count per `_partition_date`
- Currency parse failures (non-numeric after stripping symbols)
- Rows with unparseable dates/timestamps
- Header drift vs. mapping (unexpected/missing columns)
