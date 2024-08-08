-- Aliasing without AS
-- https://github.com/sqlfluff/sqlfluff/issues/149
SELECT
    (POW(sd2,2) + POW(sd3,2) + POW(sd4,2) + POW(sd4,2)) w1
FROM
    dat;
-- Another Aliasing without AS
SELECT
    CASE
      WHEN order_month = max_month THEN 1
    ELSE
    0
  END
    churn
