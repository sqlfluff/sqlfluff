SELECT 1 AS _;

SELECT 1 AS __;

SELECT a
FROM (
VALUES ('a'), ('b')
) AS _(a);

SELECT a
FROM (
VALUES ('a'), ('b')
) AS __(a);
