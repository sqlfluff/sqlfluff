-- Examples from https://spark.apache.org/docs/latest/sql-ref-syntax-qry-select-pivot.html

SELECT * FROM person
    PIVOT (
        SUM(age) AS a, AVG(class) AS c
        FOR name IN ('John' AS john, 'Mike' AS mike)
    );

SELECT * FROM person
    PIVOT (
        SUM(age) AS a, AVG(class) AS c
        FOR (name, age) IN (('John', 30) AS c1, ('Mike', 40) AS c2)
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
