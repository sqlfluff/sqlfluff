CREATE TABLE IF NOT EXISTS foo (
    col1 string,
    col2 float
)
CLUSTERED BY (col2) SORTED BY (col1 DESC) INTO 5 BUCKETS;
