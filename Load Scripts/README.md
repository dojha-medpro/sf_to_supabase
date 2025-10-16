# Loads Runbook

**Goal**: reliable, idempotent daily loads from Salesforce CSVs → staging → core (+CDC).

## Inputs
- CSVs at `reports/RAW/YYYY-MM-DD/`
- Mapping files in `mappings/`
- Supabase connection (see `env.sample`)

## Parameters
- `LOAD_DATE` (YYYY-MM-DD)
- `OBJECT` (form_submission|contact|job_applicant|placement)
- `FILE_PATH` (absolute or repo-relative)

## Standard Run (per object)
1) **Pre-checks**: file present, non-empty, header matches mapping
2) **Land**: import to staging partition for `LOAD_DATE`
3) **De-dup**: keep latest per key (same-day duplicates)
4) **CDC**: classify new/changed/unchanged; mark soft-deletes after N days
5) **Upsert**: write current + SCD2 history
6) **QA Gate**: run object test pack; proceed only if PASS
7) **Log & Notify**: record run metrics; share summary

## Re-run / Rollback
- Remove staging partition for date; re-run steps 2–7
- Core upserts are idempotent; history preserves prior versions

## Ownership & Schedule
- **Owner**: @team-handle
- **Schedule**: daily at HH:MM (timezone)
