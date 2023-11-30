CREATE TABLE tablename
(
    id_column INT,
    othercolumn STRING
)
USING DELTA
LOCATION "s3://someplace"
CLUSTER BY (id_column);
OPTIMIZE tablename;


OPTIMIZE tablename
WHERE date >= current_timestamp() - INTERVAL 1 day
ZORDER BY (eventType, eventTime);
