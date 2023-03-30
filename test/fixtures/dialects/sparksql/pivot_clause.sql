SELECT a
FROM person
    PIVOT (
        SUM(age) AS a
        FOR name IN ('John' AS john)
    );

SELECT a
FROM person
    PIVOT (
        SUM(age) AS a
        FOR name IN ('John' AS john, 'Mike' AS mike)
    );

SELECT a
FROM person
    PIVOT (
        SUM(age) AS a
        FOR (name) IN ('John' AS john, 'Mike' AS mike)
    );

SELECT a
FROM person
    PIVOT (
        SUM(age) AS a
        FOR name IN ('John' AS john, 'Mike' AS mike)
    );

SELECT
    a,
    c
FROM person
    PIVOT (
        SUM(age) AS a, AVG(class) AS c
        FOR name IN ('John' AS john, 'Mike' AS mike)
    );

SELECT
    a,
    c
FROM person
    PIVOT (
        SUM(age) AS a, AVG(class) AS c
        FOR name IN ('John' AS john, 'Mike' AS mike)
    );

SELECT
    a,
    c
FROM person
    PIVOT (
        SUM(age) AS a, AVG(class) AS c
        FOR name, age IN (('John', 30) AS c1, ('Mike', 40) AS c2)
    );

SELECT
    p.a,
    p.c
FROM person AS p
    PIVOT (
        SUM(age) AS a, AVG(class) AS c
        FOR name, age IN (('John', 30) AS c1, ('Mike', 40) AS c2)
    );

-- Will throw error when executed but should parse
SELECT
    a,
    c
FROM person
    PIVOT (
        SUM(age) AS a, AVG(class) AS c
        FOR (name, age) IN ('John' AS c1, ('Mike', 40) AS c2)
    );


SELECT * FROM (
  some_table
) PIVOT (
  min(timestamp_ns) / 1e9 as min_timestamp_s -- this is the offending line

  FOR run_id in (
    test_run_id as test,
    ctrl_run_id as ctrl
  )
);
