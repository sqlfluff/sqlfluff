ALTER EXTERNAL VOLUME exvol1
  ADD STORAGE_LOCATION =
    (
      NAME = 'my-s3-us-central-2'
      STORAGE_PROVIDER = 'S3'
      STORAGE_BASE_URL = 's3://my_bucket_us_central-1/'
      STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::123456789012:role/myrole'
    );

ALTER EXTERNAL VOLUME exvol2
  ADD STORAGE_LOCATION =
    (
      NAME = 'my-gcs-europe-west4'
      STORAGE_PROVIDER = 'GCS'
      STORAGE_BASE_URL = 'gcs://my_bucket_europe-west4/'
    );

ALTER EXTERNAL VOLUME exvol3
  ADD STORAGE_LOCATION =
    (
      NAME = 'my-azure-japaneast'
      STORAGE_PROVIDER = 'AZURE'
      STORAGE_BASE_URL = 'azure://sfcdev1.blob.core.windows.net/my_container_japaneast/'
      AZURE_TENANT_ID = 'a9876545-4321-987b-b23c-2kz436789d0'
    );

ALTER EXTERNAL VOLUME exvol4 REMOVE STORAGE_LOCATION 'foo';

ALTER EXTERNAL VOLUME exvol5 SET ALLOW_WRITES = TRUE;

ALTER EXTERNAL VOLUME IF EXISTS exvol6 SET COMMENT = 'bar';
