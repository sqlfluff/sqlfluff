-- Comparison operator in `WHERE` clause.
SELECT
    name,
    age
FROM person WHERE id > 200 ORDER BY id;

-- Comparison and logical operators in `WHERE` clause.
SELECT
    name,
    age
FROM person WHERE id = 200 OR id = 300 ORDER BY id;

-- Function expression in `WHERE` clause.
SELECT
    name,
    age
FROM person WHERE length(name) > 3 ORDER BY id;

-- `BETWEEN` expression in `WHERE` clause.
SELECT
    name,
    age
FROM person WHERE id BETWEEN 200 AND 300 ORDER BY id;

-- Scalar Subquery in `WHERE` clause.
SELECT
    name,
    age
FROM person WHERE age > (SELECT avg(age) FROM person);

-- Correlated Subquery in `WHERE` clause.
SELECT
    name,
    age
FROM person
WHERE EXISTS (
        SELECT 1 FROM person
        WHERE person.id = person.id AND person.age IS NULL
    );

SELECT
    name,
    age
FROM person
WHERE person.id is distinct from person.age;

SELECT
    name,
    age
FROM person
WHERE person.id is not distinct from person.age
