-- https://docs.vertica.com/latest/en/sql-reference/data-types/complex-types/array/
SELECT ARRAY[1, 2, 3];

SELECT ARRAY[ARRAY[1], ARRAY[2]];

CREATE TABLE sal_emp (
    name varchar,
    pay_by_quarter ARRAY[int],
    schedule ARRAY[varchar(50)]
);

SELECT ARRAY[[1, 2], [3, 4]];

-- Need to add support for complex datatypes
-- SELECT ARRAY[row(1, 2), row(1, 3)];

-- SELECT
--     name,
--     num,
--     gpa
-- FROM students
-- WHERE major = ARRAY[row('Science', 'Physics')];

SELECT (ARRAY['a', 'b', 'c', 'd', 'e'])[1];

SELECT (ARRAY['a', 'b', 'c', 'd', 'e', 'f', 'g'])[1:4];

SELECT (ARRAY[ARRAY[1, 2], ARRAY[3, 4]])[0][0];

SELECT ARRAY[1, 3] IS NULL;

SELECT ARRAY[1, 3] <=> NULL;
