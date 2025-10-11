SELECT * FROM (SELECT 1, 2, 3, 4) AS dt;
SELECT * FROM (SELECT 1, 2, 3, 4) AS `dt`;
SELECT * FROM (SELECT 1, 2, 3, 4) AS dt (a, b, c, d);
SELECT * FROM (SELECT 1, 2, 3, 4) AS `dt` (a, b, c, d);

INSERT INTO test
(col1, col2)
SELECT *
FROM (
    VALUES
    (1, "a"),
    (2, "b")
) AS temp(col1, col2) WHERE NOT EXISTS (
        SELECT NULL FROM test
    );
