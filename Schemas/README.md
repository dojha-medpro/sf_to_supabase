# Schemas

**Purpose**: single source of truth for database design in Supabase (staging, core, views) and how it evolves.

## Contents
- `staging/`, `core/`, `views/` — schema folders
- `form_submission/`, `contact/`, `job_applicant/`, `placement/` — object folders within schema folders
- `release_notes.md` — human-readable changes across releases
- `data_dictionary.md` — canonical definitions
- `erd/` — diagrams or links to ERD

## Process
1) Propose change → open PR with schema spec + migration notes
2) Update data dictionary + ERD
3) Coordinate changes to `mappings/`, `load_scripts/`, `QA scripts/`
