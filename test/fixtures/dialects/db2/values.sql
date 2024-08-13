-- 3 rows of 1 column
VALUES (1), (2), (3);

-- 3 rows of 1 column
VALUES 1, 2, 3;

-- 1 row of 3 columns
VALUES (1, 2, 3);

-- 3 rows of 2 columns
VALUES (1, 21), (2, 22), (3, 23);

-- nested bracketed values
VALUES ('A', ('S')), ('C', 'X');

-- values with sets
VALUES 1, 2
EXCEPT
VALUES 2;

-- post order by
VALUES 1, 2, 3
ORDER BY 1
OFFSET 1 ROWS
FETCH FIRST 1 ROWS ONLY;

-- values use within a CTE
WITH CTE1 (C) AS (
    VALUES 'A', 'B'
)

SELECT *
FROM CTE1;

-- values use within a lateral join
SELECT
    X.NUM,
    D.MY_COL
FROM MY_SCHEMA.MY_TABLE AS D
CROSS JOIN LATERAL(VALUES 0, 1) AS X (NUM);

-- values within an insert statement
INSERT INTO MY_TAB_DFLT
VALUES
(1, 2, 3),
(1, NULL, DEFAULT);

INSERT INTO MY_TAB_DFLT
VALUES DEFAULT;

INSERT INTO MY_TAB_DFLT
VALUES (DEFAULT);

INSERT INTO MY_TAB_DFLT
VALUES DEFAULT, NULL, 1;

INSERT INTO MY_TAB_DFLT
VALUES (DEFAULT), (NULL), (1);
