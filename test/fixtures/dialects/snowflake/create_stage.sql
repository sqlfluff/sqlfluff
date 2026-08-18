CREATE STAGE my_int_stage
  COPY_OPTIONS = (ON_ERROR='skip_file');
CREATE STAGE my_int_stage
  ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE')
  COPY_OPTIONS = (ON_ERROR='skip_file');
CREATE TEMPORARY STAGE my_temp_int_stage;
CREATE TEMPORARY STAGE my_int_stage
  FILE_FORMAT = my_csv_format;
CREATE STAGE mystage
  DIRECTORY = (ENABLE = TRUE)
  FILE_FORMAT = myformat;
CREATE STAGE my_ext_stage
  URL='s3://load/files/'
  STORAGE_INTEGRATION = myint;
CREATE STAGE my_ext_stage
  URL='s3://load'
  STORAGE_INTEGRATION = myint;
CREATE STAGE my_ext_stage
  URL='s3://load/'
  STORAGE_INTEGRATION = myint;
CREATE STAGE my_ext_stage
  URL='s3://load/files'
  STORAGE_INTEGRATION = myint;
CREATE STAGE my_ext_stage1
  URL='s3://load/files/'
  CREDENTIALS=(AWS_KEY_ID='1a2b3c' AWS_SECRET_KEY='4x5y6z');
CREATE STAGE my_ext_stage2
  URL='s3://load/encrypted_files/'
  CREDENTIALS=(AWS_KEY_ID='1a2b3c' AWS_SECRET_KEY='4x5y6z')
  ENCRYPTION=(MASTER_KEY = 'eSxX0jzYfIamtnBKOEOwq80Au6NbSgPH5r4BDDwOaO8=');
CREATE STAGE my_ext_stage3
  URL='s3://load/encrypted_files/'
  CREDENTIALS=(AWS_KEY_ID='1a2b3c' AWS_SECRET_KEY='4x5y6z')
  ENCRYPTION=(TYPE='AWS_SSE_KMS' KMS_KEY_ID = 'aws/key');
CREATE STAGE my_ext_stage3
  URL='s3://load/encrypted_files/'
  CREDENTIALS=(AWS_ROLE='arn:aws:iam::001234567890:role/mysnowflakerole')
  ENCRYPTION=(TYPE='AWS_SSE_KMS' KMS_KEY_ID = 'aws/key');
CREATE STAGE mystage
  URL='s3://load/files/'
  STORAGE_INTEGRATION = my_storage_int
  DIRECTORY = (
    ENABLE = true
    AUTO_REFRESH = true
  );
CREATE STAGE my_ext_stage
  URL='gcs://load/files/'
  STORAGE_INTEGRATION = myint;
CREATE STAGE mystage
  URL='gcs://load/files/'
  STORAGE_INTEGRATION = my_storage_int
  DIRECTORY = (
    ENABLE = true
    AUTO_REFRESH = true
    NOTIFICATION_INTEGRATION = 'MY_NOTIFICATION_INT'
  );
CREATE STAGE my_ext_stage
  URL='azure://myaccount.blob.core.windows.net/load/files/'
  STORAGE_INTEGRATION = myint;
CREATE STAGE mystage
  URL='azure://myaccount.blob.core.windows.net/mycontainer/files/'
  CREDENTIALS=(AZURE_SAS_TOKEN='?sv=2016-05-31&ss=b&srt=sco&sp=rwdl&se=2018-06-27T10:05:50Z&st=2017-06-27T02:05:50Z&spr=https,http&sig=bgqQwoXwxzuD2GJfagRg7VOS8hzNr3QLT7rhS8OFRLQ%3D')
  ENCRYPTION=(TYPE='AZURE_CSE' MASTER_KEY = 'kPxX0jzYfIamtnJEUTHwq80Au6NbSgPH5r4BDDwOaO8=')
  FILE_FORMAT = my_csv_format;
CREATE STAGE mystage
  URL='azure://myaccount.blob.core.windows.net/load/files/'
  STORAGE_INTEGRATION = my_storage_int
  DIRECTORY = (
    ENABLE = true
    AUTO_REFRESH = true
    NOTIFICATION_INTEGRATION = 'MY_NOTIFICATION_INT'
  );
CREATE OR REPLACE STAGE foo.bar
    URL = 's3://foobar'
    STORAGE_INTEGRATION = foo
    FILE_FORMAT = foo.bar.baz
;
CREATE OR REPLACE STAGE foo.bar
  URL = 's3://foobar'
  STORAGE_INTEGRATION = foo
  FILE_FORMAT = (FORMAT_NAME = foo.bar.baz)
;

CREATE OR REPLACE STAGE your_stage_name
  URL = 's3://your_s3_bucket/your_path_in_s3';

CREATE OR REPLACE STAGE your_stage_name
  URL = 's3://your-s3-bucket/your-path-in-s3';

CREATE STAGE mystage
  URL=$your_variable
  CREDENTIALS=(AZURE_SAS_TOKEN=$your_variable);

CREATE STAGE mystage
  URL=$your_variable
  STORAGE_INTEGRATION=$your_variable;

CREATE OR REPLACE STAGE foo.bar
  URL = 's3://foobar'
  STORAGE_INTEGRATION = foo
  FILE_FORMAT = (
    TYPE = CSV
    PARSE_HEADER = TRUE
  );

CREATE OR ALTER STAGE foo.bar
  URL = 's3://foobar';

CREATE STAGE foo.bar
  STORAGE_INTEGRATION=$your_variable
  URL=$your_variable;

CREATE OR REPLACE STAGE foo.bar
  STORAGE_INTEGRATION = foo
  URL = 's3://foobar'
  FILE_FORMAT = (
    TYPE = CSV
    PARSE_HEADER = TRUE
  );

CREATE STAGE my_ext_stage
  STORAGE_INTEGRATION = myint
  URL='azure://myaccount.blob.core.windows.net/load/files/';

CREATE STAGE mystage
  CREDENTIALS=(AZURE_SAS_TOKEN='?sv=2016-05-31&ss=b&srt=sco&sp=rwdl&se=2018-06-27T10:05:50Z&st=2017-06-27T02:05:50Z&spr=https,http&sig=bgqQwoXwxzuD2GJfagRg7VOS8hzNr3QLT7rhS8OFRLQ%3D')
  ENCRYPTION=(TYPE='AZURE_CSE' MASTER_KEY = 'kPxX0jzYfIamtnJEUTHwq80Au6NbSgPH5r4BDDwOaO8=')
  URL='azure://myaccount.blob.core.windows.net/mycontainer/files/'
  FILE_FORMAT = my_csv_format;

CREATE STAGE mystage
  STORAGE_INTEGRATION = my_storage_int
  DIRECTORY = (
    ENABLE = true
    AUTO_REFRESH = true
    NOTIFICATION_INTEGRATION = 'MY_NOTIFICATION_INT'
  )
  URL='azure://myaccount.blob.core.windows.net/load/files/';

CREATE TEMP STAGE my_temp_stage;

CREATE STAGE my_int_dir_stage
    DIRECTORY = (ENABLE = TRUE AUTO_REFRESH = TRUE);

CREATE STAGE my_s3_dir_stage
    URL = 's3://load/files/'
    STORAGE_INTEGRATION = my_storage_int
    DIRECTORY = (ENABLE = TRUE REFRESH_ON_CREATE = TRUE AUTO_REFRESH = FALSE);

CREATE STAGE my_s3gov_stage
    URL = 's3gov://govbucket/files/'
    STORAGE_INTEGRATION = my_gov_int;

CREATE STAGE my_s3china_stage
    URL = 's3china://cnbucket/files/';

CREATE STAGE my_s3compat_stage
    URL = 's3compat://mybucket/files/'
    ENDPOINT = 'mystorage.example.com'
    CREDENTIALS = (AWS_KEY_ID = 'k' AWS_SECRET_KEY = 's');

CREATE STAGE my_access_point_stage
    URL = 's3://my-access-point-alias/files/'
    AWS_ACCESS_POINT_ARN = 'arn:aws:s3:us-east-1:123456789012:accesspoint/my-ap';

CREATE STAGE my_privatelink_stage
    URL = 's3://privatebucket/files/'
    STORAGE_INTEGRATION = my_storage_int
    USE_PRIVATELINK_ENDPOINT = TRUE;

CREATE STAGE my_gcs_notif_stage
    URL = 'gcs://load/files/'
    STORAGE_INTEGRATION = my_gcs_int
    DIRECTORY = (ENABLE = TRUE AUTO_REFRESH = TRUE NOTIFICATION_INTEGRATION = my_notification_int);

CREATE STAGE my_azure_notif_stage
    URL = 'azure://myaccount.blob.core.windows.net/load/files/'
    DIRECTORY = (ENABLE = TRUE REFRESH_ON_CREATE = TRUE NOTIFICATION_INTEGRATION = 'my_notification_int');
