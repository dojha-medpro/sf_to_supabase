# Constraints & Indexes — staging.form_submission

## Constraints (intent)
- **NOT NULL**: form_submission_id, created_at, _partition_date, _file_name, _source_report
- **Soft uniqueness expectation**: (form_submission_id, _partition_date) should be unique **after** same-day de-duping.

> Staging is a landing zone; we prefer to **observe** issues rather than block loads. Enforce stricter rules in `core`.

## Indexing (for performance)
- B-tree on **_partition_date** (common partition filter)
- B-tree on **form_submission_id**
- Optional composite: **(form_submission_id, _partition_date)** for fast de-dupe/lookups
- B-tree on **email** (to accelerate downstream linking)

## Quality signals to capture each load
- Duplicate keys found per `_partition_date`
- Rows with unparseable timestamps
- Header drift vs. mapping
