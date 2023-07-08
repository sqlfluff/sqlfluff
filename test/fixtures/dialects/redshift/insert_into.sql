INSERT INTO s1.t1 (
    SELECT
        col1,
        col2,
        col3
    FROM testtable
  );

INSERT INTO s1.t1 (col1, col2) (
    select
        col1,
        col2,
        col3
    from testtable
);

INSERT INTO schema1.t1
    SELECT
        col1,
        col2,
        col3
    FROM testtable
;

INSERT INTO schema1.t1
    DEFAULT VALUES
;

INSERT INTO s1.t1 (col1, col2) VALUES
    ('V1', 1),
    ('V2', 2)
;
