-- Single Row Insert Using a VALUES Clause
INSERT INTO TABLE students VALUES
('Amy Smith', '123 Park Ave, San Jose', 111111);

INSERT INTO students VALUES
('Amy Smith', '123 Park Ave, San Jose', 111111);

INSERT OVERWRITE students VALUES
('Amy Smith', '123 Park Ave, San Jose', 111111);

-- Multi-Row Insert Using a VALUES Clause
INSERT INTO students VALUES
('Bob Brown', '456 Taylor St, Cupertino', 222222),
('Cathy Johnson', '789 Race Ave, Palo Alto', 333333);

INSERT OVERWRITE students VALUES
('Bob Brown', '456 Taylor St, Cupertino', 222222),
('Cathy Johnson', '789 Race Ave, Palo Alto', 333333);

-- Insert Using a SELECT Statement
INSERT INTO students PARTITION (student_id = 444444)
SELECT
    name,
    address
FROM persons WHERE name = "Dora Williams";

INSERT OVERWRITE students PARTITION (student_id = 444444)
SELECT
    name,
    address
FROM persons WHERE name = "Dora Williams";

-- Insert Using a TABLE Statement
INSERT INTO students TABLE visiting_students;

INSERT OVERWRITE students TABLE visiting_students;

-- Insert Using a FROM Statement
INSERT INTO students
FROM applicants
SELECT
name, address, id
WHERE qualified = TRUE;

INSERT OVERWRITE students
FROM applicants
SELECT
name, address, id
WHERE qualified = TRUE;

-- Insert Using a Typed Date Literal for a Partition Column Value
INSERT INTO students PARTITION (birthday = DATE '2019-01-02')
VALUES ('Amy Smith', '123 Park Ave, San Jose');

INSERT OVERWRITE students PARTITION (birthday = DATE '2019-01-02')
VALUES ('Amy Smith', '123 Park Ave, San Jose');

-- Insert with both a partition spec and a column list
INSERT INTO students PARTITION (student_id = 11215017) (address, name) VALUES
('Hangzhou, China', 'Kent Yao Jr.');

INSERT OVERWRITE students
PARTITION (student_id = 11215017) (address, name)
VALUES ('Hangzhou, China', 'Kent Yao Jr.');
