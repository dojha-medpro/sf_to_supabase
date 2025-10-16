# Table Design — staging.jobs_and_placements (landing zone)

| Column                         | Type        | Nullable | Description |
|--------------------------------|-------------|----------|-------------|
| job_sfid                       | text        | no       | Salesforce Job Id (18-char) |
| placement_sfid                 | text        | yes      | Salesforce Placement Id (18-char) |
| start_date                     | date        | yes      | Placement/job start date |
| end_date                       | date        | yes      | Placement/job end date |
| original_start_date            | date        | yes      | Original start date |
| original_end_date              | date        | yes      | Original end date |
| original_placement_start_date  | date        | yes      | Original placement start date |
| medpro_department              | text        | yes      | Department label |
| orientation_start_date         | date        | yes      | Orientation start date |
| duration_of_assignment         | integer*    | yes      | Assignment duration (*use text if non-numeric source*) |
| shift                          | text        | yes      | Shift details |
| end_of_assignment_survey_returned | boolean  | yes      | Whether end-of-assignment survey was returned |
| bill_rate_base                 | numeric     | yes      | Base bill rate |
| bill_rate                      | numeric     | yes      | Bill rate (overall) |
| bill_rate_overtime             | numeric     | yes      | Overtime bill rate |
| pay_rate                       | numeric     | yes      | Pay rate (overall) |
| pay_rate_base                  | numeric     | yes      | Base pay rate |
| pay_rate_overtime              | numeric     | yes      | Overtime pay rate |
| bill_rate_holiday              | numeric     | yes      | Holiday bill rate |
| pay_rate_holiday               | numeric     | yes      | Holiday pay rate |
| last_modified_at               | timestamptz | yes      | Salesforce last modified timestamp |
| placement_type                 | text        | yes      | Placement type |
| international_placement_active | boolean     | yes      | International placement active flag |
| _partition_date                | date        | no       | Load snapshot date (ingestion day) |
| _file_name                     | text        | no       | Source filename |
| _source_report                 | text        | no       | Friendly report name |
| _extract_ts                    | timestamptz | yes      | When the report was exported |
| _mapping_version               | text        | yes      | Mapping tag/commit used |
| _raw_hash                      | text        | yes      | Optional checksum of source row |
