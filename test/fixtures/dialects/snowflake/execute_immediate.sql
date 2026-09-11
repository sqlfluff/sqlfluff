EXECUTE IMMEDIATE 'select 1';

EXECUTE IMMEDIATE $$
  SELECT PI();
$$;

SET pie =
$$
  SELECT PI();
$$
;

SET one = 1;
SET two = 2;

EXECUTE IMMEDIATE $pie;
EXECUTE IMMEDIATE $pie USING (one, two);

SET three = 'select ? + ?';
EXECUTE IMMEDIATE :three;
EXECUTE IMMEDIATE :three USING (one, two);

EXECUTE IMMEDIATE FROM './insert-inventory.sql';

EXECUTE IMMEDIATE FROM @my_stage/scripts/create-inventory.sql;

-- The statement string can also be an arbitrary expression that evaluates
-- to a string, e.g. built up via concatenation.
EXECUTE IMMEDIATE 'CREATE OR REPLACE TABLE ' || :backup_table_name || ' AS SELECT * FROM t';
