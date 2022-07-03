-- string literals
SELECT 'Hello, World!' AS col;
SELECT 'SPARK SQL' AS col;
SELECT "it's $10." AS col;

-- binary literal
SELECT X'123456' AS col;

-- null literal
SELECT NULL AS col;

-- boolean literal
SELECT TRUE AS col;
SELECT FALSE AS col;

-- numeric literal
SELECT -2147483648 AS col;
SELECT 9223372036854775807l AS col;
SELECT -32Y AS col;
SELECT 482S AS col;

-- fractional literals
SELECT 12.578 AS col;
SELECT -0.1234567 AS col;
SELECT -.1234567 AS col;
SELECT 123. AS col;
SELECT 123.BD AS col;
SELECT 5E2 AS col;
SELECT 5D AS col;
SELECT -5BD AS col;
SELECT 12.578e-2d AS col;
SELECT -.1234567E+2BD AS col;
SELECT +3.e+3 AS col;
SELECT -3.E-3D AS col;

-- datetime literal
SELECT DATE '1997' AS col;
SELECT DATE '1997-01' AS col;
SELECT DATE '2011-11-11' AS col;
SELECT TIMESTAMP '1997-01-31 09:26:56.123' AS col;
SELECT TIMESTAMP '1997-01-31 09:26:56.66666666UTC+08:00' AS col;
SELECT TIMESTAMP '1997-01' AS col;

-- ansi interval literal
SELECT INTERVAL '2-3' YEAR TO MONTH AS col;
SELECT INTERVAL -'20 15:40:32.99899999' DAY TO SECOND AS col;

-- multi-units interval syntax
SELECT INTERVAL 3 YEAR AS col;
SELECT INTERVAL -2 HOUR '3' MINUTE AS col;
SELECT INTERVAL '1 YEAR 2 DAYS 3 HOURS';
SELECT INTERVAL
    1 YEARS
    2 MONTH
    3 WEEK
    4 DAYS
    5 HOUR
    6 MINUTES
    7 SECOND
    8 MILLISECOND
    9 MICROSECONDS
    AS col;
