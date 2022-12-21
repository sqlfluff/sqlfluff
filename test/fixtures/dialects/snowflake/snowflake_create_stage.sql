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
