copy into mytable
from @my_int_stage;

copy into mytable
from @my_int_stage
file_format = (type = csv);

copy into mytable from @my_int_stage
file_format = (format_name = 'mycsv');

copy into mytable
from @my_int_stage
  file_format = (type = 'CSV')
  pattern='.*/.*/.*[.]csv[.]gz';

copy into mytable
from @my_int_stage
  file_format = (format_name = myformat)
  pattern='.*sales.*[.]csv';

copy into mytable
from @my_int_stage
  file_format = (format_name = myformat)
  pattern=$my_var;

copy into mytable;

copy into mytable
from @%mytable;

copy into mytable
from @~/data_files;

copy into mytable
from @mydb.myschema.mystage;

copy into mytable
from @mydatabase.myschema.%mytable;

copy into mytable purge = true;

copy into mytable validation_mode = 'RETURN_ERRORS';

copy into mytable validation_mode = 'RETURN_2_ROWS';

copy into mytable validation_mode = 'RETURN_3_ROWS';

COPY INTO target_table
FROM (
  SELECT $1
  FROM @source_stage
);

copy into mytable1 (column1)
    from 's3://bucket/source'
    file_format = (TYPE = JSON);

copy into mytable1
    from (select column1 from @ext.stage/path1)
    file_format = (TYPE = JSON);

copy into mytable1
    from 's3://bucket/source'
    file_format = (type=csv SKIP_HEADER=1);

copy into mytable1 (column1)
    from @public.stage/sub-folder/myfile-1.csv
    file_format = (TYPE = JSON);

copy into mytable1 (column1)
    from @public.stage/subfolder/
    file_format = (TYPE = JSON);

COPY INTO table1 FROM @stage1
MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
INCLUDE_METADATA = (
    ingestdate = METADATA$START_SCAN_TIME, filename = METADATA$FILENAME);

COPY INTO table1 FROM @stage1
MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
FILE_FORMAT = (TYPE = JSON)
LOAD_UNCERTAIN_FILES = TRUE
INCLUDE_METADATA = (
    ingestdate = METADATA$START_SCAN_TIME, filename = METADATA$FILENAME);

COPY INTO test.transactions_all
FROM @rawdata.STITCH_STAGE_NETSUITE/transactions/
FILE_FORMAT = rawdata.json_format
MATCH_BY_COLUMN_NAME = 'case_insensitive';

copy into mytable1
    from 's3://bucket/source'
    file_format = (type=csv MULTI_LINE=FALSE);

COPY INTO t1 FROM @stage1 LOAD_MODE = ADD_FILES_COPY;

COPY INTO t1 FROM @stage1 LOAD_MODE = FULL_INGEST CLUSTER_AT_INGEST_TIME = TRUE;

COPY INTO doc_table
FROM @docs_stage
FILE_PROCESSOR = (
    SCANNER = 'document_ai'
    SCANNER_OPTIONS = (project_name = 'DEMO', model_name = 'my_model', model_version = 1)
);

-- The docs mix comma and space separated scanner options.
COPY INTO doc_table
FROM @docs_stage
FILE_PROCESSOR = (
    SCANNER = 'document_ai'
    SCANNER_OPTIONS = (project_name = 'DEMO0200', model_name = 'predict' model_version = '1')
);

COPY INTO parsed_data
FROM 'gcs://mybucket/data/files'
STORAGE_INTEGRATION = my_gcs_int
ENCRYPTION = (TYPE = 'GCS_SSE_KMS' KMS_KEY_ID = 'my_kms_key')
FILE_FORMAT = (TYPE = CSV);

COPY INTO t1 FROM @stage1 VALIDATION_MODE = RETURN_ROWS;
