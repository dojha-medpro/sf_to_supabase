# Constraints & Indexes — staging.contact

## Constraints (intent)
- NOT NULL: `contact_sfid`, `_partition_date`, `_file_name`, `_source_report`
- Soft uniqueness (post de-dupe): unique on `(contact_sfid, _partition_date)`

> Staging is a landing zone; prefer **observability over hard failures**. Enforce stricter rules in `core`.

## Indexes
- B-tree on `_partition_date` (common filter)
- B-tree on `contact_sfid`
- Optional composite `(contact_sfid, _partition_date)` for de-dupe/CDC matching
- B-tree on `email` to speed downstream joins

## Quality signals to capture each load
- Duplicate key count per `_partition_date`
- Invalid/blank email count
- Header drift vs. mapping (unexpected/missing columns)
