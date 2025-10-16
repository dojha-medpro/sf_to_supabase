# Table Design — staging.job_applicant_history (landing zone)

| Column               | Type        | Nullable | Description |
|----------------------|-------------|----------|-------------|
| job_applicant_sfid   | text        | no       | Salesforce Job Applicant Id (18-char) |
| job_applicant_alt_id | text        | yes      | Alternate ID column from report (if present) |
| candidate            | text        | yes      | Candidate label (not guaranteed to be an ID) |
| field_event          | text        | no       | Field name or event label that changed |
| old_value            | text        | yes      | Previous value (free-form) |
| new_value            | text        | yes      | New value (free-form) |
| edited_at            | timestamptz | no       | When the change occurred (Edit Date) |
| _partition_date      | date        | no       | Derived: `edited_at::date` |
| _file_name           | text        | no       | Source filename (operational metadata) |
| _source_report       | text        | no       | Friendly report name |
| _extract_ts          | timestamptz | yes      | When the report was exported |
| _mapping_version     | text        | yes      | Mapping tag/commit used |
| _raw_hash            | text        | yes      | Optional checksum of the raw row |

**Composite event key**: (`job_applicant_sfid`, `edited_at`, `field_event`)
