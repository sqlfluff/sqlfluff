-- CTE with multiple column aliases
WITH t(x, y) AS (
    SELECT
        1,
        2
)

SELECT * FROM t WHERE x = 1 AND y = 2;

-- CTE in CTE definition
WITH t AS (
    WITH t2 AS (SELECT 1)

    SELECT * FROM t2
)

SELECT * FROM t;

-- CTE in subquery
SELECT max(c) FROM (
    WITH t(c) AS (SELECT 1)

    SELECT * FROM t
);

-- CTE in subquery expression
SELECT (
    WITH t AS (SELECT 1)

    SELECT * FROM t
);

-- CTE in CREATE VIEW statement
CREATE VIEW v AS
WITH t(a, b, c, d) AS (
    SELECT
        1,
        2,
        3,
        4
)

SELECT * FROM t;
SELECT * FROM v;

-- If name conflict is detected in nested CTE, then AnalysisException is thrown by default.
-- SET spark.sql.legacy.ctePrecedencePolicy = CORRECTED (which is recommended),
-- inner CTE definitions take precedence over outer definitions.
WITH
t AS (
    SELECT 1
),

t2 AS (
    WITH t AS (SELECT 2)

    SELECT * FROM t
)

SELECT * FROM t2;
