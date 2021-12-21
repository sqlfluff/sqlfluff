WITH Produce AS (
  SELECT 'Kale' as product, 51 as Q1, 23 as Q2, 45 as Q3, 3 as Q4 UNION ALL
  SELECT 'Apple', 77, 0, 25, 2)
SELECT * FROM Produce;

SELECT * FROM Produce
UNPIVOT(sales FOR quarter IN (Q1, Q2, Q3, Q4));

SELECT * FROM Produce
UNPIVOT INCLUDE NULLS (sales FOR quarter IN (Q1, Q2, Q3, Q4));

SELECT * FROM Produce
UNPIVOT EXCLUDE NULLS (sales FOR quarter IN (Q1, Q2, Q3, Q4));

SELECT * FROM Produce
UNPIVOT(
  (first_half_sales, second_half_sales)
  FOR semesters
  IN ((Q1, Q2) AS 'semester_1', (Q3, Q4) AS 'semester_2'));
