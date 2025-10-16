# Table Design — staging.contact (landing zone)

| Column                       | Type        | Nullable | Description |
|-----------------------------|-------------|----------|-------------|
| contact_sfid                | text        | no       | Salesforce Contact/Candidate Id (18-char) |
| record_type                 | text        | yes      | Contact/Candidate record type |
| account_id                  | text        | yes      | Salesforce Account Id |
| first_name                  | text        | yes      | First name (trimmed) |
| last_name                   | text        | yes      | Last name (trimmed) |
| email                       | text        | yes      | Lowercased email |
| email_opt_out               | boolean     | yes      | True if opted out |
| applicant_history           | text        | yes      | Free-text/history from report |
| application_date            | date        | yes      | Application date (from report) |
| specialty                   | text        | yes      | Candidate specialty |
| candidate_status            | text        | yes      | Current candidate status |
| employment_status           | text        | yes      | Employment status |
| green_card_filing_status    | text        | yes      | GC filing status |
| initial_documents_status    | text        | yes      | Initial documents status |
| intl_employment_status      | text        | yes      | International employment status |
| lead_status                 | text        | yes      | Lead status |
| licensure_status            | text        | yes      | Licensure status |
| medpro_department           | text        | yes      | Department (Domestic/International/etc.) |
| intl_pipeline_summary       | text        | yes      | Pipeline summary |
| intl_stage_contract_returned| text        | yes      | Stage marker/flag |
| intl_healthcare_vendor      | text        | yes      | Vendor name |
| intl_interviewer            | text        | yes      | Interviewer name |
| contract_effective_date     | date        | yes      | Contract effective date |
| date_deployed               | date        | yes      | Deployment date |
| last_modified_at            | timestamptz | yes      | Salesforce last modified timestamp |
| _partition_date             | date        | no       | Load snapshot date (ingestion day) |
| _file_name                  | text        | no       | Source filename |
| _source_report              | text        | no       | Friendly report name |
| _extract_ts                 | timestamptz | yes      | When the report was exported |
| _mapping_version            | text        | yes      | Mapping tag/commit used |
| _raw_hash                   | text        | yes      | Optional checksum of source row |

**Cross-object link fields**: `contact_sfid` (primary), `email` (soft link), `account_id` (org link).
