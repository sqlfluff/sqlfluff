-- Basic example of trailing comma
CREATE TABLE t_table (
    col1 STRING,
);

-- Complex example with other variants
CREATE TABLE t_table (
    col1 STRING,
    x INT64 NOT NULL OPTIONS(description="An INTEGER field that is NOT NULL"),
);
