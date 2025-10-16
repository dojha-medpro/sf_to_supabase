# Table Design — staging.job_applicant (landing zone)

| Column                   | Type        | Nullable | Description |
|--------------------------|-------------|----------|-------------|
| job_applicant_sfid       | text        | no       | Salesforce Job Applicant Id (18-char) |
| job_applicant_alt_id     | text        | yes      | Alternate ID shown in report (if present) |
| created_at               | timestamptz | no       | Created Date/Time from report |
| candidate                | text        | yes      | Candidate (label from report; not guaranteed to be an ID) |
| account                  | text        | yes      | Account (label from report) |
| applicant_source         | text        | yes      | Applicant Source |
| job_title                | text        | yes      | Job Title |
| application_status       | text        | yes      | Application Status (text) |
| application_status_pick  | text        | yes      | Application Status (picklist label) |
| date_offer_received      | date        | yes      | Date Offer Received |
| interview_availability   | text        | yes      | Free-form interview availability |
| submitted_to_hm_at       | timestamptz | yes      | Date/Time Submitted to Hiring Manager |
| submitted_to_hm_end_date | date        | yes      | Date Submitted to Hiring Manager (end date) |
| stage_name               | text        | yes      | Stage name (pipeline stage) |
| last_modified_at         | timestamptz | yes      | Salesforce Last Modified Date |
| _partition_date          | date        | no       | Derived: `created_at::date` |
| _file_name               | text        | no       | Source filename (operational metadata) |
| _source_report           | text        | no       | Friendly report name |
| _extract_ts              | timestamptz | yes      | When the report was exported |
| _mapping_version         | text        | yes      | Mapping tag/commit used |
| _raw_hash                | text        | yes      | Optional checksum of the raw row |

**Cross-object link field**: `job_applicant_sfid` (primary link used downstream).
