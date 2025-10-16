# Table Design — staging.contacts_with_jobs (landing zone)

| Column                      | Type        | Nullable | Description |
|----------------------------|-------------|----------|-------------|
| job_applicant_sfid         | text        | no       | Primary Salesforce Job Applicant Id (18-char) |
| job_applicant_alt_id       | text        | yes      | Duplicate/alternate Job Applicant Id column from report |
| contact_sfid               | text        | yes      | Salesforce Contact/Candidate Id (18-char) |
| full_name                  | text        | yes      | Contact full name (label) |
| email                      | text        | yes      | Candidate email (lowercased) |
| account_name               | text        | yes      | Account name (label) |
| applicant_source           | text        | yes      | Applicant Source |
| job_title                  | text        | yes      | Job Title |
| job_status                 | text        | yes      | Job Status |
| submitted_to_hm_at         | timestamptz | yes      | Date/Time Submitted to Hiring Manager |
| days_with_hiring_manager   | integer*    | yes      | Count of days HM has had the req (*store as text if source not numeric) |
| time_am_to_hiring_manager  | text        | yes      | Duration metric (AM → HM) as reported |
| time_sa_to_hiring_manager  | text        | yes      | Duration metric (SA → HM) as reported |
| date_offer_received        | date        | yes      | Date offer received |
| interview_availability     | text        | yes      | Free-form availability |
| job_city_state             | text        | yes      | City/State descriptor |
| job_source                 | text        | yes      | Job Source |
| last_modified_at           | timestamptz | yes      | Salesforce last modified timestamp |
| _partition_date            | date        | no       | Load snapshot date (ingestion day) |
| _file_name                 | text        | no       | Source filename |
| _source_report             | text        | no       | Friendly report name |
| _extract_ts                | timestamptz | yes      | When the report was exported |
| _mapping_version           | text        | yes      | Mapping tag/commit used |
| _raw_hash                  | text        | yes      | Optional checksum of source row |

**Cross-object links**: `job_applicant_sfid` (primary), `contact_sfid` (contact relationship).
