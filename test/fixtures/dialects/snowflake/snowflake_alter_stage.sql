ALTER STAGE my_int_stage RENAME TO new_int_stage;
ALTER STAGE my_ext_stage SET
    URL='s3://loading/files/new/'
    COPY_OPTIONS = (ON_ERROR='skip_file');
ALTER STAGE my_ext_stage SET STORAGE_INTEGRATION = myint;
ALTER STAGE my_ext_stage SET
    CREDENTIALS=(AWS_KEY_ID='d4c3b2a1' AWS_SECRET_KEY='z9y8x7w6');
ALTER STAGE my_ext_stage3 SET
    ENCRYPTION=(TYPE='AWS_SSE_S3');
ALTER STAGE mystage REFRESH;
ALTER STAGE mystage REFRESH SUBPATH = 'data';
