-- COPY INTO. https://docs.databricks.com/aws/en/sql/language-manual/delta-copy-into
COPY INTO t FROM 's3://example-bucket/p' FILEFORMAT = CSV;

COPY INTO t BY POSITION FROM 's3://example-bucket/p' FILEFORMAT = CSV;

COPY INTO t (a, b) FROM 's3://example-bucket/p' FILEFORMAT = CSV;

COPY INTO t FROM (SELECT a, b FROM 's3://example-bucket/p') FILEFORMAT = CSV;

COPY INTO t FROM 's3://example-bucket/p' FILEFORMAT = CSV VALIDATE ALL;

COPY INTO t FROM 's3://example-bucket/p' FILEFORMAT = CSV VALIDATE 10 ROWS;

COPY INTO t FROM 's3://example-bucket/p' FILEFORMAT = CSV FILES = ('a.csv', 'b.csv');

COPY INTO t FROM 's3://example-bucket/p' FILEFORMAT = CSV PATTERN = '*.csv';

COPY INTO t FROM 's3://example-bucket/p' FILEFORMAT = CSV FORMAT_OPTIONS (header = 'true');

COPY INTO t FROM 's3://example-bucket/p' FILEFORMAT = CSV COPY_OPTIONS (force = 'true');

COPY INTO t FROM 's3://example-bucket/p' WITH (CREDENTIAL cred) FILEFORMAT = CSV;

COPY INTO t FROM 's3://example-bucket/p' WITH (CREDENTIAL (AWS_ACCESS_KEY = 'k', AWS_SECRET_KEY = 's')) FILEFORMAT = CSV;

COPY INTO t FROM 's3://example-bucket/p' WITH (ENCRYPTION (TYPE = 'AWS_SSE_C', MASTER_KEY = 'k')) FILEFORMAT = CSV;

COPY INTO t FROM 's3://example-bucket/p' WITH (CREDENTIAL cred ENCRYPTION (TYPE = 'AWS_SSE_C')) FILEFORMAT = CSV;

COPY INTO t (a) FROM 's3://example-bucket/p' FILEFORMAT = CSV VALIDATE 5 ROWS FILES = ('a.csv') FORMAT_OPTIONS (header = 'true') COPY_OPTIONS (force = 'true');
