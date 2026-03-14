-- NB This is a pivot expression With and Alias. The alias should be parsed seperately to the pivot.
SELECT * FROM my_tbl
PIVOT (min(f_val) FOR f_id IN (1, 2)) AS f (a, b);

SELECT * FROM my_tbl
UNPIVOT (val FOR col_name IN (a, b));

SELECT * FROM my_tbl
UNPIVOT INCLUDE NULLS (val FOR col_name IN (a, b));

SELECT * FROM my_tbl
UNPIVOT EXCLUDE NULLS (val FOR col_name IN (a, b));

select
*
from table_a
unpivot (a for b in (col_1, col_2, col_3))
unpivot (c for d in (col_a, col_b, col_c))
;

-- from Snowflake's PIVOT docs
SELECT *
FROM quarterly_sales
  PIVOT(SUM(amount) FOR quarter IN (ANY ORDER BY quarter))
ORDER BY empid;


-- from Snowflake's PIVOT docs
SELECT *
FROM quarterly_sales
  PIVOT(SUM(amount) FOR quarter IN (
    SELECT DISTINCT quarter
      FROM ad_campaign_types_by_quarter
      WHERE television = TRUE
      ORDER BY quarter)
  )
ORDER BY empid;

-- from Snowflake's PIVOT docs
SELECT *
FROM quarterly_sales
  PIVOT(SUM(amount) FOR quarter IN (
    '2023_Q1',
    '2023_Q2',
    '2023_Q3',
    '2023_Q4')
  ) AS p (empid_renamed, Q1, Q2, Q3, Q4)
ORDER BY empid_renamed;

-- from Snowflake's PIVOT docs
SELECT *
FROM quarterly_sales
  PIVOT(SUM(amount)
    FOR quarter IN (
      '2023_Q1',
      '2023_Q2',
      '2023_Q3',
      '2023_Q4',
      '2024_Q1')
    DEFAULT ON NULL (0)
  )
ORDER BY empid;


-- https://github.com/sqlfluff/sqlfluff/issues/5876
select *
from to_pivot pivot(sum(val) for col in (any order by col))
order by id;

-- https://github.com/sqlfluff/sqlfluff/issues/7244
SELECT
    empid AS employee_id,
    q1_2023_sales,
    q2_2023_sales,
    q3_2023_sales,
    q4_2023_sales
FROM quarterly_sales
PIVOT (
    SUM(amount) FOR quarter IN (
        '2023_Q1' AS q1_2023_sales,
        '2023_Q2' AS q2_2023_sales,
        '2023_Q3' AS q3_2023_sales,
        '2023_Q4' AS q4_2023_sales
    )
)
WHERE q1_2023_sales IS NOT NULL;
