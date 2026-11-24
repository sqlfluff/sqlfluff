CREATE STAGE china_stage URL = 's3china://example-bucket/path/';
CREATE STAGE gov_stage URL = 's3gov://example-bucket/path/';
ALTER STAGE china_stage SET URL = 's3china://example-bucket/other/';
ALTER STAGE gov_stage SET URL = 's3gov://example-bucket/other/';

CREATE STORAGE INTEGRATION china_int TYPE = EXTERNAL_STAGE
  STORAGE_PROVIDER = 'S3CHINA' ENABLED = TRUE
  STORAGE_AWS_ROLE_ARN = 'arn:aws-cn:iam::123456789012:role/example'
  STORAGE_ALLOWED_LOCATIONS = ('s3china://example-bucket/path/')
  STORAGE_BLOCKED_LOCATIONS = ('s3china://example-bucket/path/private/');
CREATE STORAGE INTEGRATION gov_int TYPE = EXTERNAL_STAGE
  STORAGE_PROVIDER = 'S3GOV' ENABLED = TRUE
  STORAGE_AWS_ROLE_ARN = 'arn:aws-us-gov:iam::123456789012:role/example'
  STORAGE_ALLOWED_LOCATIONS = ('s3gov://example-bucket/path/')
  STORAGE_BLOCKED_LOCATIONS = ('s3gov://example-bucket/path/private/');
ALTER STORAGE INTEGRATION china_int SET
  STORAGE_ALLOWED_LOCATIONS = ('s3china://example-bucket/path/')
  STORAGE_BLOCKED_LOCATIONS = ('s3china://example-bucket/path/private/');
ALTER STORAGE INTEGRATION gov_int SET
  STORAGE_ALLOWED_LOCATIONS = ('s3gov://example-bucket/path/')
  STORAGE_BLOCKED_LOCATIONS = ('s3gov://example-bucket/path/private/');

COPY INTO example FROM 's3china://example-bucket/path/';
COPY INTO example FROM 's3gov://example-bucket/path/';
COPY INTO 's3china://example-bucket/path/' FROM example;
COPY INTO 's3gov://example-bucket/path/' FROM example;
