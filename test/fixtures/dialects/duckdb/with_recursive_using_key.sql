-- Recursive CTE with USING KEY
WITH RECURSIVE tbl(a, b) USING KEY (a) AS (
    SELECT 1, 3
    UNION
    SELECT a + 1, b FROM tbl WHERE a < 3
)
SELECT * FROM tbl;

-- USING KEY with several key columns and UNION ALL
WITH RECURSIVE tbl(a, b, c) USING KEY (a, b) AS (
    SELECT 1, 1, 0
    UNION ALL
    SELECT a, b, c + 1 FROM tbl WHERE c < 3
)
SELECT * FROM tbl;

-- Aggregates over payload columns in USING KEY
WITH RECURSIVE tbl(a, b) USING KEY (a, max(b)) AS (
    SELECT 1, 5
    UNION ALL
    SELECT a, b - 1 FROM tbl WHERE b > 1
)
SELECT * FROM tbl;

-- VALUES as the anchor
WITH RECURSIVE tbl(a, b) USING KEY (a) AS (
    VALUES (1, 3), (2, 4)
    UNION
    SELECT a, b - 1 FROM tbl WHERE b > 3
)
SELECT * FROM tbl;

-- The recurring table of a USING KEY CTE
WITH RECURSIVE comp(id, c) USING KEY (id) AS (
    SELECT i, i FROM range(3) AS r(i)
    UNION
    (
        SELECT r.id, least(r.c, 0)
        FROM recurring.comp AS r
        WHERE r.c > 0
    )
)
SELECT * FROM comp;
