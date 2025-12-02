SELECT 1 AS _;

SELECT 1 AS __;

SELECT 1 AS __TEST;

SELECT a
FROM (
VALUES ('a'), ('b')
) AS _(a);

SELECT a
FROM (
VALUES ('a'), ('b')
) AS __(a);
