# Table Design — staging.form_submission (landing zone)

| Column               | Type        | Nullable | Description                                                  |
|----------------------|-------------|----------|--------------------------------------------------------------|
| form_submission_id   | text        | no       | Submission key from Salesforce report                        |
| form_submission_name | text        | yes       | Submission name from Salesforce report                        |
| created_at           | timestamptz | no       | Created Date/Time from report (also the partition key)       |
| contact_candidate    | text        | yes      | Contact/Candidate (as shown in report)                       |
| application          | text        | yes      | Application reference shown in report                        |
| job                  | text        | yes      | Job reference shown in report                                |
| record_type          | text        | yes      | Form Submission record type                                  |
| first_name           | text        | yes      | Your First                                                   |
| last_name            | text        | yes      | Your Last                                                    |
| email                | text        | yes      | Your Email (normalized lowercase)                            |
| form_type            | text        | yes      | Form Type                                                    |
| phone                | text        | yes      | Your Phone (stored as text to preserve formatting)           |
| city                 | text        | yes      | City                                                         |
| zip_code             | text        | yes      | Zip Code (text to keep leading zeros)                        |
| job_city             | text        | yes      | Job City                                                     |
| job_state            | text        | yes      | Job State (e.g., "FL")                                       |
| form                 | text        | yes      | Form (label/path as reported)                                |
| utm_source           | text        | yes      | utm_source                                                   |
| utm_medium           | text        | yes      | utm_medium                                                   |
| utm_campaign         | text        | yes      | utm_campaign                                                 |
| source               | text        | yes      | Source                                                       |
| marketing_campaign   | text        | yes      | Marketing Campaign                                           |
| area_of_assignment   | text        | yes      | Area of Assignment                                           |
| last_modified_at     | timestamptz | yes      | Last Modified Date from report                               |
| _partition_date      | date        | no       | **Derived**: `created_at::date` for partition naming         |
| _file_name           | text        | no       | Source filename (operational metadata)                       |
| _source_report       | text        | no       | Human-friendly report name                                   |
| _extract_ts          | timestamptz | yes      | When the report was exported                                 |
| _mapping_version     | text        | yes      | Mapping tag/commit used                                      |
| _raw_hash            | text        | yes      | Optional checksum of the raw row                             |

**Notes**
- We maintain `_partition_date` (date-only) alongside `created_at` to keep partition folder names predictable.
- Cross-object joins downstream should use **email (lowercased)** as a soft link; expect non-uniqueness and collisions—final identity resolution happens in core.
