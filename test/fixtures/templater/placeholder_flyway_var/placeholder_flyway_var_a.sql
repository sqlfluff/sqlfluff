USE ${flyway:database}.test_schema;

CREATE OR REPLACE STAGE stg_data_export_${env_name}
URL = 's3://${s3_data_lake_bucket}/${env_name}/exports/stg_data_export'
STORAGE_INTEGRATION = s3_integ_main;
