# Staging — Form Submission

**Source report**: (https://surestaff.lightning.force.com/lightning/r/Report/00Ocx000005kkjJEAQ/view?queryScope=userFolders)
**Grain**: One row per **form submission**  
**Stable key**: `Form Submission: Form Submission Name` (treated as the submission key)  
**Partition key**: `Created Date/Time` (daily partitions anchored to the submission’s created timestamp)  
**Cross-object link**: `Your Email` (used to associate with Contact/Candidate by normalized email)

## Column rename (Salesforce → staging column)
- Form Submission: ID -> **form_submission_id**
- Form Submission: Form Submission Name → **form_submission_name**
- Created Date/Time → **created_at**
- Contact/Candidate → **contact_candidate**
- Application → **application**
- Job → **job**
- Form Submission: Record Type → **record_type**
- Your First → **first_name**
- Your Last → **last_name**
- Your Email → **email**
- Form Type → **form_type**
- Your Phone → **phone**
- City → **city**
- Zip Code → **zip_code**
- Job City → **job_city**
- Job State → **job_state**
- Form → **form**
- utm_source → **utm_source**
- utm_medium → **utm_medium**
- utm_campaign → **utm_campaign**
- Source → **source**
- Marketing Campaign → **marketing_campaign**
- Area of Assignment → **area_of_assignment**
- Form Submission: Last Modified Date → **last_modified_at**

> Note: Supabase/Postgres disallow `:` `/` in identifiers; all names are lower_snake_case.

## Coercions & normalizations
- **email**: lowercase + trimmed.
- **first_name / last_name / city / job_city / job_state / marketing_campaign / source / form_type / area_of_assignment**: trimmed.
- **phone**: store as text; optionally strip non-digits downstream.
- **zip_code**: keep as text (preserve leading zeros).
- **created_at / last_modified_at**: parsed to timestamp with timezone.

## Null policy
Treat the following as NULL on load: `""`, `NULL`, `N/A`, `n/a`, `null`.

## Required-at-staging
- **form_submission_id** (key)
- **created_at** (drives partition)
All other fields nullable in staging (validated later).

## Duplicate policy (same key within a day)
If multiple rows share the same **form_submission_name** in the same partition (Created Date), keep the **latest by last_modified_at**; if `last_modified_at` is missing, keep the last encountered row.

## Retention (staging)
Keep **90 days** of partitions; older can be archived externally.

## Sensitivity
Contains PII (names, email, phone). Handle per data-protection guidelines.

