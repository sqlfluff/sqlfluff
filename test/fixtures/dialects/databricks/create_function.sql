-- Create FUNCTION with all optional syntax
CREATE OR REPLACE TEMPORARY FUNCTION IF NOT EXISTS
function_name AS "class_name" USING FILE "resource_locations";

-- Create a permanent function called `simple_udf`.
CREATE FUNCTION simple_udf AS 'SimpleUdf'
USING JAR '/tmp/SimpleUdf.jar';

-- Created a temporary function.
CREATE TEMPORARY FUNCTION simple_temp_udf AS 'SimpleUdf'
USING JAR '/tmp/SimpleUdf.jar';

-- Replace the implementation of `simple_udf`
CREATE OR REPLACE FUNCTION simple_udf AS 'SimpleUdfR'
USING JAR '/tmp/SimpleUdfR.jar';

-- Create a permanent function `test_avg`
CREATE FUNCTION test_avg
AS 'org.apache.hadoop.hive.ql.udf.generic.GenericUDAFAverage';

---- Create Temporary function `test_avg`
CREATE TEMPORARY FUNCTION test_avg
AS 'org.apache.hadoop.hive.ql.udf.generic.GenericUDAFAverage';

-- Create a temporary function with no parameter
CREATE TEMPORARY FUNCTION hello()
RETURNS STRING RETURN 'Hello World!';

-- Create a temporary function with no parameter.
CREATE OR REPLACE TEMPORARY FUNCTION function_name()
RETURNS TIMESTAMP LANGUAGE SQL
RETURN SELECT MAX(time) AS time FROM my_table;

-- Create a permanent function with parameters
CREATE FUNCTION area(x DOUBLE, y DOUBLE)
RETURNS DOUBLE
RETURN x * y;

-- Compose SQL functions.
CREATE FUNCTION square(x DOUBLE)
RETURNS DOUBLE
RETURN area(x, x);

-- Create a CTE function
CREATE FUNCTION cte_function(x INT)
RETURNS string
LANGUAGE SQL
RETURN
WITH cte AS (SELECT x AS y)
SELECT * FROM cte;

-- Create a non-deterministic function
CREATE FUNCTION roll_dice()
    RETURNS INT
    NOT DETERMINISTIC
    CONTAINS SQL
    COMMENT 'Roll a single 6 sided die'
    RETURN (rand() * 6)::INT + 1;


-- Create a non-deterministic function with parameters and defaults
CREATE FUNCTION roll_dice(num_dice  INT DEFAULT 1 COMMENT 'number of dice to roll (Default: 1)',
                            num_sides INT DEFAULT 6 COMMENT 'number of sides per die (Default: 6)')
    RETURNS INT
    NOT DETERMINISTIC
    CONTAINS SQL
    COMMENT 'Roll a number of n-sided dice'
    RETURN aggregate(sequence(1, roll_dice.num_dice, 1),
                     0,
                     (acc, x) -> (rand() * roll_dice.num_sides)::int,
                     acc -> acc + roll_dice.num_dice);

-- Create Python functions
CREATE FUNCTION main.default.greet(s STRING)
  RETURNS STRING
  LANGUAGE PYTHON
  AS $$
    def greet(name):
      return "Hello " + name + "!"

    return greet(s) if s else None
  $$;

-- Created Table Valued Function simple
CREATE FUNCTION return_table()
RETURNS TABLE
RETURN
SELECT time FROM my_table
;

-- Created Table Valued Function with column spec + comment
CREATE FUNCTION return_table()
RETURNS TABLE (col_a string, col_b string comment "asdf")
RETURN
SELECT col_a, col_b FROM my_table
;


-- backticked identifier
create or replace function `catalog`.`schema`.`name` (
    param int
)
returns int
return
select param
;
