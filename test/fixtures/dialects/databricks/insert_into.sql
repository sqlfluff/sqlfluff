-- Standard INSERT INTO
INSERT INTO students VALUES ('Amy Smith', '123 Park Ave', 111111);

-- INSERT INTO with column list
INSERT INTO students (name, address, student_id)
VALUES ('Amy Smith', '123 Park Ave', 111111);

-- INSERT INTO with BY NAME
INSERT INTO target BY NAME
SELECT named_struct('a', 1, 'b', 2) AS s, 0 AS n, 'data' AS text;

-- INSERT OVERWRITE
INSERT OVERWRITE students VALUES ('Ashua Hill', '456 Erica Ct', 111111);

-- INSERT OVERWRITE with PARTITION
INSERT OVERWRITE students PARTITION (student_id = 111111)
SELECT name, address FROM persons WHERE name = 'Amy Smith';

-- INSERT INTO with PARTITION and BY NAME
INSERT INTO students PARTITION (student_id = 222222) BY NAME
SELECT address, name FROM persons WHERE name = 'Dora Williams';

-- INSERT INTO with REPLACE WHERE (no BY NAME)
INSERT INTO sales
REPLACE WHERE tx_date BETWEEN '2022-10-01' AND '2022-10-31'
VALUES (DATE '2022-10-01', 1237), (DATE '2022-10-02', 2378);

-- INSERT INTO with BY NAME and REPLACE WHERE (Databricks-specific combination)
INSERT INTO sales BY NAME
REPLACE WHERE tx_date BETWEEN '2022-10-01' AND '2022-10-31'
SELECT * FROM (
    (
        VALUES (1237, DATE '2022-10-01'), (2378, DATE '2022-10-02')
    ) AS (amount, tx_date)
);

-- INSERT INTO with REPLACE USING (no BY NAME)
INSERT INTO TABLE students
REPLACE USING (country)
SELECT * FROM new_students;

-- INSERT INTO with BY NAME and REPLACE USING (Databricks Runtime 18.1+)
INSERT INTO TABLE students BY NAME
REPLACE USING (country)
SELECT * FROM (
    VALUES ('US', 'Sophie'), ('UK', 'Oliver')
) AS t(country, name);

-- INSERT INTO with REPLACE ON
INSERT INTO TABLE students AS t
REPLACE ON t.name = s.name
SELECT * FROM people;

-- INSERT INTO with REPLACE ON and implicit target alias (no AS)
INSERT INTO TABLE students t
REPLACE ON t.name = s.name
SELECT * FROM people;

-- INSERT INTO with BY NAME and REPLACE ON (Databricks Runtime 18.1+)
INSERT INTO TABLE students AS t BY NAME
REPLACE ON t.name = s.name
SELECT * FROM (
    VALUES ('query', 'Bob'), ('query', 'Charlie')
) AS s(row_origin, name);

-- INSERT INTO with REPLACE ON and source alias
INSERT INTO TABLE students AS t
REPLACE ON t.name = s.name
SELECT * FROM people AS s;

-- INSERT INTO with REPLACE ON and implicit source alias (no AS)
INSERT INTO TABLE students t
REPLACE ON t.name = s.name
SELECT * FROM people s;

-- INSERT WITH SCHEMA EVOLUTION
INSERT WITH SCHEMA EVOLUTION INTO TABLE students
SELECT * FROM new_students;

-- INSERT WITH SCHEMA EVOLUTION and BY NAME
INSERT WITH SCHEMA EVOLUTION INTO TABLE target BY NAME
SELECT named_struct('a', 1, 'b', 2) AS s, 0 AS n;

-- INSERT WITH SCHEMA EVOLUTION and BY NAME REPLACE WHERE
INSERT WITH SCHEMA EVOLUTION INTO sales BY NAME
REPLACE WHERE tx_date BETWEEN '2022-10-01' AND '2022-10-31'
SELECT amount, tx_date FROM new_sales;

-- INSERT OVERWRITE with BY NAME
INSERT OVERWRITE students BY NAME
SELECT address, name, student_id FROM persons;

-- Regression: INSERT INTO TABLE with column list and SELECT
INSERT INTO TABLE students (name, address, student_id)
SELECT name, address, student_id FROM persons;

-- Regression: INSERT using TABLE as source
INSERT INTO students TABLE visiting_students;

INSERT OVERWRITE students TABLE visiting_students;

-- Regression: INSERT using FROM source
INSERT INTO students
FROM persons
SELECT name, address
WHERE qualified = TRUE;

-- Regression: PARTITION with explicit column list (both INTO and OVERWRITE)
INSERT INTO students PARTITION (student_id = 11215017) (address, name)
VALUES ('Hangzhou, China', 'Kent Yao Jr.');

INSERT OVERWRITE students PARTITION (student_id = 11215017) (address, name)
VALUES ('Hangzhou, China', 'Kent Yao Jr.');

-- Regression: OVERWRITE with PARTITION and BY NAME
INSERT OVERWRITE students PARTITION (student_id = 222222) BY NAME
SELECT address, name FROM persons;

-- Regression: INSERT OVERWRITE TABLE with PARTITION and VALUES
INSERT OVERWRITE TABLE students PARTITION (student_id = 333333)
VALUES ('Bob Jones', '789 Main St');

-- WITH SCHEMA EVOLUTION and OVERWRITE (Form 1)
INSERT WITH SCHEMA EVOLUTION OVERWRITE students
SELECT * FROM new_students;

-- WITH SCHEMA EVOLUTION and REPLACE USING
INSERT WITH SCHEMA EVOLUTION INTO TABLE students BY NAME
REPLACE USING (country)
SELECT * FROM new_students;

-- WITH SCHEMA EVOLUTION and REPLACE ON with alias and BY NAME (most complex form)
INSERT WITH SCHEMA EVOLUTION INTO TABLE students AS t BY NAME
REPLACE ON t.name = s.name
SELECT * FROM (
    VALUES ('Alice', 'US'), ('Bob', 'UK')
) AS s(name, country);
