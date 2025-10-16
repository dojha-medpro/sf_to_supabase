# Staging — Contact (a.k.a. Contact/Candidate)

**Source report**: https://surestaff.lightning.force.com/lightning/r/Report/00Ocx000005kthlEAA/view?queryScope=userFolders  
**Grain**: One row per **contact**  
**Stable key**: `Contact/Candidate ID` → `contact_sfid`  
**Partition key**: `_partition_date` (the **load snapshot date**; we also keep Salesforce `last_modified_at` for CDC)  
**Cross-object links**: `contact_sfid` (primary), `email` (soft link), `account_id`

## Column rename (Salesforce → staging)
- Contact/Candidate Record Type → `record_type`  
- Account ID → `account_id`  
- Contact/Candidate ID → `contact_sfid`  
- First Name → `first_name`  
- Last Name → `last_name`  
- Email → `email`  
- Email Opt Out → `email_opt_out`  
- Applicant History → `applicant_history`  
- Application Date → `application_date`  
- Specialty → `specialty`  
- Candidate Status → `candidate_status`  
- Employment Status → `employment_status`  
- Green Card Filing Status → `green_card_filing_status`  
- Initial Documents Status → `initial_documents_status`  
- Intl Employment Status → `intl_employment_status`  
- Lead Status → `lead_status`  
- Licensure Status → `licensure_status`  
- MedPro Department → `medpro_department`  
- Intl Pipeline Summary → `intl_pipeline_summary`  
- Intl Stage - Contract Returned → `intl_stage_contract_returned`  
- Intl Healthcare Vendor → `intl_healthcare_vendor`  
- Intl Interviewer → `intl_interviewer`  
- Contract Effective Date → `contract_effective_date`  
- Date Deployed → `date_deployed`  
- Last Modified Date → `last_modified_at`

> Naming: lower_snake_case; strip/replace `:`, `/`, `-` to satisfy Postgres/Supabase rules.

## Coercions & normalizations
- `email`: lowercase + trim  
- `email_opt_out`: boolean (accept `True/False`, `Yes/No`, `1/0`)  
- Names/status/vendor/interviewer/department: trim  
- `application_date`, `contract_effective_date`, `date_deployed`: **date**  
- `last_modified_at`: **timestamptz**

## Null policy
Treat as NULL: `""`, `NULL`, `N/A`, `n/a`, `null`.

## Required at staging
- `contact_sfid` (key)  
- `_partition_date`, `_file_name`, `_source_report` (operational metadata)

## Duplicate policy (same day)
If duplicates exist for `(contact_sfid, _partition_date)`, keep the row with the **greatest `last_modified_at`**; if tie/missing, keep the **last encountered**.

## Retention (staging)
Keep **90 days** of `_partition_date` partitions; archive older externally.

## Sensitivity
Contains PII (names, emails). Follow data-protection guidance.
