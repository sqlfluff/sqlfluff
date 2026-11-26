SELECT * FROM addresses LIMIT 10%;

SELECT * FROM addresses LIMIT 10 PERCENT;

SELECT * FROM addresses LIMIT 12.5%;

SELECT * FROM addresses LIMIT 2 * 5%;

SELECT * FROM addresses LIMIT (25)%;

SELECT * FROM addresses LIMIT 10% OFFSET 2;

SELECT * FROM addresses LIMIT 50 PERCENT OFFSET 2;

SELECT * FROM addresses OFFSET 2 LIMIT 10%;

-- A `%` between two values is a modulo: a limit of 1 row.
SELECT * FROM addresses LIMIT 10 % 3;
