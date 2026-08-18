DEFINE STAGE FINANCE_DB.RAW.TASTY_BYTES_ORDERS
  COMMENT='Internal stage for uploading files';

DEFINE STAGE my_db.my_schema.gcs_events_stage
  URL = 'gcs://my-bucket/'
  STORAGE_INTEGRATION = my_gcs_int
  FILE_FORMAT = (FORMAT_NAME = 'my_db.my_schema.my_json_format')
  COMMENT = 'events GCS stage';

DEFINE STAGE my_db.my_schema.s3_stage
  URL = 's3://my-bucket/files/'
  STORAGE_INTEGRATION = my_s3_int
  DIRECTORY = (ENABLE = TRUE AUTO_REFRESH = TRUE);

DEFINE STAGE my_db.my_schema.azure_stage
  URL = 'azure://myaccount.blob.core.windows.net/mycontainer/files/'
  STORAGE_INTEGRATION = my_azure_int
  DIRECTORY = (ENABLE = TRUE NOTIFICATION_INTEGRATION = my_notification_int);
