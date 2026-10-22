-- A bare division operator inside a CREATE VIEW body must not be
-- mistaken for a SQL*Plus slash-buffer terminator (issue #8373).
CREATE VIEW division_view AS
SELECT
    1 / 100 AS pct,
    nvl(bytes, 0) / 1024 / 1024 AS size_mb,
    (1 / 24) AS parenthesised
FROM
    sample_table
WHERE
    sample_time > sysdate - 1 / 24
/

-- A division operator may be the first code token on its line.
CREATE VIEW line_start_division_view AS
SELECT
    1
    / 100 AS pct
FROM
    dual
/

-- A slash alone on a line still terminates the batch.
CREATE VIEW plain_view AS
SELECT
    col_a
FROM
    sample_table
/
