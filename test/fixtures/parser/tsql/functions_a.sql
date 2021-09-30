SELECT
    DATE(t) AS t_date,
    ROUND(b, 2) AS b_round,
    LEFT(RIGHT(s, 5), LEN(s + 6)) AS compound,
    DATEADD(month, -1, column1) AS column1_lastmonth
FROM tbl_b
