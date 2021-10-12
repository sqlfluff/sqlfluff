CREATE OR REPLACE FUNCTION
qs(
    y ANY TYPE
) AS (
    CASE
        WHEN y = 1 THEN 'low'
        WHEN y = 2 THEN 'midlow'
        WHEN y = 3 THEN 'mid'
        WHEN y = 4 THEN 'midhigh'
        WHEN y = 5 THEN 'high'
        ELSE "unknown"
    END
)
