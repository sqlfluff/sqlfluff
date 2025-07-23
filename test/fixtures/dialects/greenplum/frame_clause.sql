SELECT
    SUM(field_1) OVER (
        PARTITION BY field_2
        ORDER BY
            field_3
        RANGE BETWEEN INTERVAL '1' MONTH PRECEDING AND CURRENT ROW
    ) AS field_1
FROM table_1;

SELECT
    SUM(field_1) OVER (
        PARTITION BY field_2
        ORDER BY
            field_3
        RANGE BETWEEN INTERVAL '1 month' PRECEDING AND CURRENT ROW
    ) AS field_1
FROM table_1;

SELECT
    COUNT(*) OVER (
        PARTITION BY field_1
        ORDER BY field_3
        RANGE BETWEEN
        field_2 PRECEDING AND
        CURRENT ROW
    )
FROM table_1;
