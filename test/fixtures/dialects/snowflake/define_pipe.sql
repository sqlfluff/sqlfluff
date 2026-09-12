DEFINE PIPE my_db.my_schema.my_pipe
AS
  COPY INTO my_db.my_schema.my_table
  FROM @my_db.my_schema.my_stage;

DEFINE PIPE my_db.my_schema.gcs_auto_ingest_pipe
  AUTO_INGEST = TRUE
  INTEGRATION = 'MY_NOTIFICATION_INT'
  COMMENT = 'auto-ingest pipe for event files'
AS
  COPY INTO my_db.my_schema.event_histories (
    payload,
    _file_name,
    _file_row,
    _loaded_at
  )
  FROM (
    SELECT
      $1,
      metadata$filename,
      metadata$file_row_number,
      CURRENT_TIMESTAMP
    FROM @my_db.my_schema.my_stage/events/histories
  )
  FILE_FORMAT = (FORMAT_NAME = 'my_db.my_schema.my_json_format')
  PATTERN = '.*\.json$';

DEFINE PIPE my_db.my_schema.s3_pipe
  AUTO_INGEST = TRUE
  ERROR_INTEGRATION = my_error_int
  AWS_SNS_TOPIC = 'arn:aws:sns:us-west-2:001234567890:s3_mybucket'
AS
  COPY INTO my_db.my_schema.my_table
  FROM @my_db.my_schema.my_s3_stage
  FILE_FORMAT = (TYPE = 'JSON');
