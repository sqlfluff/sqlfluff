CREATE TABLE tablename
(
    id_column INT,
    othercolumn STRING
)
USING DELTA
LOCATION "s3://someplace"
CLUSTER BY (id_column);
OPTIMIZE tablename;
