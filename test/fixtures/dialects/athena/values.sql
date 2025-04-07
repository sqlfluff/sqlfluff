VALUES 1, 2, 3;

VALUES
(1, 'a'),
(2, 'b'),
(3, 'c');

SELECT * FROM (
    VALUES
    (1, 'a'),
    (2, 'b'),
    (3, 'c')
) AS t (id, name);

CREATE TABLE customers AS
SELECT * FROM (
    VALUES
    (1, 'a'),
    (2, 'b'),
    (3, 'c')
) AS t (id, name);
