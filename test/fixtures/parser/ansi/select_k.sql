-- Interval literals
-- https://github.com/alanmcruickshank/sqlfluff/issues/148
SELECT
    DATE_ADD(CURRENT_DATE('America/New_York'), INTERVAL 1 year)