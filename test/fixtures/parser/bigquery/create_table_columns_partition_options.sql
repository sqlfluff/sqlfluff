CREATE TABLE newtable (
    x INT64,
    y INT64
)
PARTITION BY x, y
CLUSTER BY x, y
OPTIONS(description="foo")
