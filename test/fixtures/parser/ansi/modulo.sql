SELECT
    CASE
        WHEN (year_number % 400 = 0)
            OR (year_number % 4 = 0 AND year_number % 100 != 0)
            THEN TRUE ELSE FALSE
    END AS is_leap_year
FROM mytable
