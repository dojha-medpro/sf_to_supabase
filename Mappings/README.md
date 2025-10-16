# Mappings

**Purpose**: declarative map from Salesforce report headers → staging/core columns, with coercions and null rules.

## Files
- `<object>__<report_slug>.yaml` — one per report
- `change_log.md` — header/logic changes
- `samples/` — 5–10 row CSVs
- `header_snapshots/` — exact header lines by date for drift checks

## Change Flow
1) Update YAML when Salesforce headers/logic change
2) Add a matching sample CSV + header snapshot
3) Note change in `change_log.md`
