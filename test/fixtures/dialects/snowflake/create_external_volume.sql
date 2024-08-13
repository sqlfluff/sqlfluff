CREATE OR REPLACE EXTERNAL VOLUME exvol
  STORAGE_LOCATIONS =
      (
        (
            NAME = 'my-s3-us-west-2'
            STORAGE_PROVIDER = 'S3'
            STORAGE_BASE_URL = 's3://MY_EXAMPLE_BUCKET/'
            STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::123456789012:role/myrole'
            ENCRYPTION=(TYPE='AWS_SSE_KMS' KMS_KEY_ID='1234abcd-12ab-34cd-56ef-1234567890ab')
        )
      )
;

CREATE EXTERNAL VOLUME exvol
  STORAGE_LOCATIONS =
    (
      (
        NAME = 'my-us-east-1'
        STORAGE_PROVIDER = 'GCS'
        STORAGE_BASE_URL = 'gcs://mybucket1/path1/'
        ENCRYPTION=(TYPE='GCS_SSE_KMS' KMS_KEY_ID = '1234abcd-12ab-34cd-56ef-1234567890ab')
      )
    );

CREATE EXTERNAL VOLUME exvol
  STORAGE_LOCATIONS =
    (
      (
        NAME = 'my-azure-northeurope'
        STORAGE_PROVIDER = 'AZURE'
        STORAGE_BASE_URL = 'azure://exampleacct.blob.core.windows.net/my_container_northeurope/'
        AZURE_TENANT_ID = 'a123b4c5-1234-123a-a12b-1a23b45678c9'
      )
    );

CREATE EXTERNAL VOLUME IF NOT EXISTS exvol
  STORAGE_LOCATIONS =
      (
        (
            NAME = 'my-s3-us-west-2'
            STORAGE_PROVIDER = 'S3'
            STORAGE_BASE_URL = 's3://MY_EXAMPLE_BUCKET/'
            STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::123456789012:role/myrole'
            ENCRYPTION=(TYPE='AWS_SSE_KMS' KMS_KEY_ID='1234abcd-12ab-34cd-56ef-1234567890ab')
        ),
        (
            NAME = 'my-s3-us-west-3'
            STORAGE_PROVIDER = 'S3'
            STORAGE_BASE_URL = 's3://MY_EXAMPLE_BUCKET_2/'
            STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::123456789012:role/myrole'
            ENCRYPTION=(TYPE='AWS_SSE_KMS' KMS_KEY_ID='1234abcd-12ab-34cd-56ef-1234567890ab')
        )
      )
  ALLOW_WRITES=FALSE
  COMMENT='foo'
;
