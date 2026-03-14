-- VARCHAR with mandatory length (valid)
CREATE TABLE test_varchar (
    id INT,
    name VARCHAR(100)
);

-- CHAR with mandatory length (valid)
CREATE TABLE test_char (
    id INT,
    code CHAR(10)
);

-- CHARACTER with mandatory length (valid)
CREATE TABLE test_character (
    id INT,
    code CHARACTER(10)
);

-- DECIMAL with optional length (valid)
CREATE TABLE test_decimal_no_length (
    id INT,
    amount DECIMAL
);

-- DECIMAL with length (valid)
CREATE TABLE test_decimal_with_length (
    id INT,
    amount DECIMAL(10, 2)
);

-- NUMERIC with optional length (valid)
CREATE TABLE test_numeric (
    id INT,
    amount NUMERIC
);

-- DEC with optional length (valid)
CREATE TABLE test_dec (
    id INT,
    amount DEC
);
