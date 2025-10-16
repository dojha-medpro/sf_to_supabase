# Table Design — staging.placement_history (landing zone)

| Column               | Type        | Nullable | Description |
|----------------------|-------------|----------|-------------|
| placement_sfid       | text        | no       | Salesforce Placement Id (18-char) |
| placement_alt_id     | text        | yes      | Alternate Placement ID column from report |
| owner_name           | text        | yes      | Placement owner (label) |
| placement_created_at | date        | yes      | Placement created date (from report) |
| candidate            | text        | yes      | Candidate label (not guaranteed to be an ID) |
| job_applicant        | text        | yes      | Job Applicant label (not guaranteed to be an ID) |
| field_event          | text        | no       | Field name or event label that changed |
| old_value            | text        | yes      | Previous value (free-form) |
| new_value            | text        | yes      | New value (free-form) |
| edited_at            | timestamptz | no       | When the change occurred (Edit Date) |
| last_modified_at     | timestamptz | yes      | Placement last modified timestamp |
| job_applicant_stage  | text        | yes      | Stage label captured with the event |
| _partition_date      | date        | no       | Derived: `edited_at::date` |
| _file_name           | text        | no       | Source filename (operational metadata) |
| _source_report       | text        | no       | Friendly report name |
| _extract_ts          | timestamptz | yes      | When the report was exported |
| _mapping_version     | text        | yes      | Mapping tag/commit used |
| _raw_hash            | text        | yes      | Optional checksum of raw row |

**Composite event key**: (`placement_sfid`, `edited_at`, `field_event`)
