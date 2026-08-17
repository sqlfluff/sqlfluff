copy into 'azure://myaccount.blob.core.windows.net/mycontainer/unload/'
  from mytable
  credentials=(azure_sas_token='xxxx')
file_format = (format_name = my_csv_format);

COPY INTO 'gcs://mybucket/unload/'
FROM mytable
STORAGE_INTEGRATION = my_gcs_int
ENCRYPTION = (TYPE = 'GCS_SSE_KMS' KMS_KEY_ID = 'my_kms_key')
FILE_FORMAT = (TYPE = PARQUET);
