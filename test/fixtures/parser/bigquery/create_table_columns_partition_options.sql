CREATE TABLE newtable (
    x TIMESTAMP,
    y INT64
)
PARTITION BY DATE(x)
CLUSTER BY x, y
OPTIONS(description="foo")
