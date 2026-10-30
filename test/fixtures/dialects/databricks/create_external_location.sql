-- CREATE EXTERNAL LOCATION. https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-location
CREATE EXTERNAL LOCATION s3_remote URL 's3://us-east-1/location' WITH (STORAGE CREDENTIAL s3_remote_cred);

CREATE EXTERNAL LOCATION s3_remote URL 's3://us-east-1/location' WITH (STORAGE CREDENTIAL s3_remote_cred) COMMENT 'Default source';

CREATE EXTERNAL LOCATION IF NOT EXISTS s3_remote URL 's3://us-east-1/location' WITH (STORAGE CREDENTIAL c);

CREATE EXTERNAL LOCATION `s3-remote` URL 's3://us-east-1/location' WITH (STORAGE CREDENTIAL `s3-remote-cred`);

CREATE EXTERNAL LOCATION IF NOT EXISTS `s3-remote` URL 's3://us-east-1/location' WITH (STORAGE CREDENTIAL `s3-remote-cred`) COMMENT 'x';
