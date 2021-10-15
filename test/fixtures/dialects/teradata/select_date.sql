SELECT DATE;

CREATE TABLE t1 (f1 DATE);

SELECT DATE (FORMAT 'MMMbdd,bYYYY'); -- (CHAR(12), UC);  -- https://docs.teradata.com/r/S0Fw2AVH8ff3MDA0wDOHlQ/ryoeKJsEr22NqKahaktP5g
-- Disabled CHAR(12, UC) for now, see #1665
