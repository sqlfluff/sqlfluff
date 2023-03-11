WITH Produce AS (
  SELECT 'Kale' as product, 51 as Q1, 23 as Q2, 45 as Q3, 3 as Q4 UNION ALL
  SELECT 'Apple', 77, 0, 25, 2)
SELECT * FROM Produce;

SELECT * FROM Produce
UNPIVOT(sales FOR quarter IN (Q1, Q2, Q3, Q4));

SELECT * FROM Produce
UNPIVOT(sales FOR quarter IN (Q1 AS 1, Q2 AS 2, Q3 AS 3, Q4 AS 4));

SELECT * FROM Produce
UNPIVOT INCLUDE NULLS (sales FOR quarter IN (Q1, Q2, Q3, Q4));

SELECT * FROM Produce
UNPIVOT EXCLUDE NULLS (sales FOR quarter IN (Q1, Q2, Q3, Q4));

SELECT * FROM Produce
UNPIVOT(
  (first_half_sales, second_half_sales)
  FOR semesters
  IN ((Q1, Q2) AS 'semester_1', (Q3, Q4) AS 'semester_2'));

SELECT
    a AS 'barry'
FROM model
UNPIVOT(
    (A, B)
    FOR year
    IN ((C, D) AS "year_2011", (E, F) AS "year_2012"));

SELECT
    *
FROM
    foo
UNPIVOT(
    (bar2, bar3, bar4)
    FOR year
    IN ((foo1, foo2, foo3) AS 1,
       (foo4, foo5, foo6) AS 2,
       (foo7, foo8, foo9) AS 3));
