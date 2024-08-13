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

-- double pivot
SELECT *
  FROM (select year, quarter, sales from sales) AS s
  PIVOT (sum(sales) AS total, avg(sales) AS avg
    FOR quarter
    IN (1 AS q1, 2 AS q2, 3 AS q3, 4 AS q4))
  PIVOT (sum(q1_avg) AS total
    FOR year
    IN (2018, 2019));
