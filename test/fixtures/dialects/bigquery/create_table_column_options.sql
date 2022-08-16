CREATE TABLE t_table1
(
    x INT64 OPTIONS(description="An INTEGER field")
);

CREATE TABLE t_table1
(
    x INT64 NOT NULL OPTIONS(description="An INTEGER field that is NOT NULL")
);

CREATE TABLE t_table1
(
    x STRUCT<
        col1 INT64 OPTIONS(description="An INTEGER field in a STRUCT")
    >,
    y ARRAY<STRUCT<
        col1 INT64 OPTIONS(description="An INTEGER field in a REPEATED STRUCT")
    >>
);
