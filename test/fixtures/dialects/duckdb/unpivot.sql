-- Simplified UNPIVOT
UNPIVOT monthly_sales
ON jan, feb, mar, apr, may, jun,
INTO
NAME month
VALUE sales;

UNPIVOT monthly_sales
ON COLUMNS (* EXCLUDE (empid, dept))
INTO
NAME month
VALUE sales;

UNPIVOT monthly_sales
ON (jan, feb, mar) AS q1, (apr, may, jun) AS q2
INTO
NAME quarter
VALUE month_1_sales, month_2_sales, month_3_sales,;

WITH unpivot_alias AS (
    UNPIVOT monthly_sales
    ON COLUMNS (* EXCLUDE (empid, dept,))
    INTO
    NAME month
    VALUE sales
)

SELECT * FROM unpivot_alias;

-- Standard UNPIVOT
FROM monthly_sales UNPIVOT (
    sales
    FOR month IN (jan, feb, mar, apr, may, jun)
);

FROM monthly_sales UNPIVOT (
    sales
    FOR month IN (COLUMNS (* EXCLUDE (empid, dept)))
);

FROM monthly_sales
UNPIVOT (
    (month_1_sales, month_2_sales, month_3_sales)
    FOR quarter IN (
        (jan, feb, mar) AS q1,
        (apr, may, jun) AS q2
    )
);

SELECT * FROM monthly_sales
UNPIVOT INCLUDE NULLS (
    (sales, tax,) FOR month IN (jan, feb, mar,)
);