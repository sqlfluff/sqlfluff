-- Examples from https://spark.apache.org/docs/3.5.0/sql-ref-syntax-qry-select-unpivot.html

-- column names are used as unpivot columns
SELECT * FROM sales_quarterly
    UNPIVOT (
        sales FOR quarter IN (q1, q2, q3, q4)
    );

-- NULL values are excluded by default, they can be included
-- unpivot columns can be alias
-- unpivot result can be referenced via its alias
SELECT up.* FROM sales_quarterly
    UNPIVOT INCLUDE NULLS (
        sales FOR quarter IN (q1 AS Q1, q2 AS Q2, q3 AS Q3, q4 AS Q4)
    ) AS up;

-- multiple value columns can be unpivoted per row
SELECT * FROM sales_quarterly
    UNPIVOT EXCLUDE NULLS (
        (first_quarter, second_quarter)
        FOR half_of_the_year IN (
            (q1, q2) AS H1,
            (q3, q4) AS H2
        )
    );

SELECT *
FROM sales UNPIVOT INCLUDE NULLS
(sales FOR quarter IN (q1       AS `Jan-Mar`,
                    q2       AS `Apr-Jun`,
                    q3       AS `Jul-Sep`,
                    sales.q4 AS `Oct-Dec`)),
        sales UNPIVOT INCLUDE NULLS
(sales FOR quarter IN (q1       AS `Jan-Mar`,
                    q2       AS `Apr-Jun`,
                    q3       AS `Jul-Sep`,
                    sales.q4 AS `Oct-Dec`))
;
