/* Examples from https://duckdb.org/docs/sql/statements/create_table */

-- create a table with two integer columns (i and j)
CREATE TABLE t1 (i INTEGER, j INTEGER);

-- create a table with a primary key
CREATE TABLE t1 (id INTEGER PRIMARY KEY, j VARCHAR);

-- create a table with a composite primary key
CREATE TABLE t1 (id INTEGER, j VARCHAR, PRIMARY KEY (id, j));

-- create a table with various different types and constraints
CREATE TABLE t1 (
    i INTEGER NOT NULL,
    decimalnr DOUBLE CHECK (decimalnr < 10),
    date DATE UNIQUE,
    time TIMESTAMP
);

-- create a table from the result of a query
CREATE TABLE t1 AS SELECT
    42 AS i,
    84 AS j;

-- create a table from a CSV file using AUTO-DETECT (i.e., automatically detecting column names and types)
CREATE TABLE t1 AS SELECT * FROM read_csv_auto('path/file.csv');

-- we can use the FROM-first syntax to omit 'SELECT *'
CREATE TABLE t1 AS FROM read_csv_auto('path/file.csv');

-- create a temporary table from a CSV file (automatically detecting column names and types)
CREATE TEMP TABLE t1 AS SELECT * FROM read_csv('path/file.csv');

-- create a table with two integer columns (i and j) even if t1 already exists
CREATE OR REPLACE TABLE t1 (i INTEGER, j INTEGER);

-- create a table with two integer columns (i and j) only if t1 does not exist yet.
CREATE TABLE IF NOT EXISTS t1 (i INTEGER, j INTEGER);

CREATE TABLE t1 (
    id INTEGER PRIMARY KEY,
    percentage INTEGER CHECK (0 <= percentage AND percentage <= 100)
);

CREATE TABLE t2 (id INTEGER PRIMARY KEY, x INTEGER, y INTEGER CHECK (x < y));

CREATE TABLE t3 (
    id INTEGER PRIMARY KEY,
    x INTEGER,
    y INTEGER,
    CONSTRAINT x_smaller_than_y CHECK (x < y)
);

CREATE TABLE t1 (id INTEGER PRIMARY KEY, j VARCHAR);
CREATE TABLE t2 (
    id INTEGER PRIMARY KEY,
    t1_id INTEGER,
    FOREIGN KEY (t1_id) REFERENCES t1 (id)
);

CREATE TABLE t3 (id INTEGER, j VARCHAR, PRIMARY KEY (id, j));
CREATE TABLE t4 (
    id INTEGER PRIMARY KEY, t3_id INTEGER, t3_j VARCHAR,
    FOREIGN KEY (t3_id, t3_j) REFERENCES t3 (id, j)
);

CREATE TABLE t5 (id INTEGER UNIQUE, j VARCHAR);
CREATE TABLE t6 (
    id INTEGER PRIMARY KEY,
    t5_id INTEGER,
    FOREIGN KEY (t5_id) REFERENCES t5 (id)
);

-- The simplest syntax for a generated column.
-- The type is derived from the expression, and the variant defaults to VIRTUAL
CREATE TABLE t1 (x FLOAT, two_x AS (2 * x));

-- Fully specifying the same generated column for completeness
CREATE TABLE t1 (x FLOAT, two_x FLOAT GENERATED ALWAYS AS (2 * x) VIRTUAL);


CREATE TABLE t_values AS VALUES (1);

CREATE TABLE t_dflt_int (id INTEGER DEFAULT 0);

CREATE OR REPLACE TABLE t_dflt_dt (dt DATE DEFAULT CURRENT_DATE);

CREATE TABLE t (
    s STRUCT(
        val STRING
    )
);

CREATE TABLE t (
    s STRUCT(
        val STRING,
        s1 STRUCT(
            ival INT,
            jval INT
        )
    )
);

CREATE TABLE map (tags MAP(VARCHAR, VARCHAR));
