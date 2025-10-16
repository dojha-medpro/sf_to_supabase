Purpose: This folder is the landing zone for Salesforce report exports (CSVs) used by daily loads. It is ignored by Git to keep PII/large files out of the repository. Only this README (and optional placeholders/samples) are tracked.

What goes here (and what doesn’t)

✅ Goes here

Daily Salesforce CSV exports used by the load pipeline.

Temporary operator notes for today’s run (non-sensitive).

Optional sample CSVs with fake/scrubbed data (under SAMPLES/).

❌ Doesn’t go here

Real production CSVs committed to Git.

Secrets, API keys, or screenshots with PII.

Header snapshots (store those in mappings/header_snapshots/).
File naming convention

<object>__<report_slug>__YYYY-MM-DD.csv

Examples:

form_submission__lead_intake__2025-10-16.csv

contact__candidate_master__2025-10-16.csv

job_applicant__open_roles__2025-10-16.csv

placement__placements_last_90_days__2025-10-16.csv

CSV format requirements

Encoding: UTF-8

Delimiter: comma, with quoted fields

Header row: required; header must match the mapping file

Dates/times: ISO-8601 preferred (e.g., 2025-10-16T14:37:00Z); otherwise clearly documented

Nulls: leave cells blank (avoid “N/A”, “NULL” strings unless mapping declares them)

No formulas or merged cells (flat text only)

Daily drop workflow (operator checklist)

Export the Salesforce row-level report (no summaries/crosstabs). Include the SFID key column.

Save to reports/RAW/YYYY-MM-DD/ using the naming convention above.

Verify headers match the mapping (mappings/<object>__<report_slug>.yaml).

Run the load per the runbook in loads/ (staging → CDC → core).

QA: confirm the daily QA pack passes (see QA/).

Archive older raw files per retention (below).

If headers changed, update the mapping YAML and header snapshot before loading.

Retention & handling

Keep last 30 days of raw drops locally for quick re-runs.

Archive older files to your approved secure storage (e.g., encrypted bucket) — not to Git.

Don’t email raw CSVs; share via secure storage links with least-privilege access.

If a laptop is replaced or deprovisioned, purge reports/RAW/ securely.

Security notes

These files typically include PII (names, emails, phone numbers). Treat as confidential.

Ensure local disks use full-disk encryption.

Only authorized team members should access this folder and the archive location.

Common issues & quick fixes

Header mismatch: Update mappings/<object>__<report_slug>.yaml and add a new header snapshot under mappings/header_snapshots/.

Weird date formats: Normalize via the mapping coercions; avoid spreadsheet “smart” formatting before export.

Duplicate rows in a file: The load process de-dups per key for the day; still report the issue to the source owner.