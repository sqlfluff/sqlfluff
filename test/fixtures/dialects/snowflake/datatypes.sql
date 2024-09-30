select
    blob:content::array(integer) as field1,
    cast(blob:content as array(integer)) as field2,
from foo
;

CREATE TABLE IF NOT EXISTS table_name (
   col1 ARRAY(NUMBER),
   col2 ARRAY(NUMBER NOT NULL)
);

CREATE OR REPLACE FUNCTION my_udtf(check BOOLEAN)
  RETURNS TABLE(col1 ARRAY(VARCHAR))
  AS
  $$
  ...
  $$;

CREATE OR REPLACE PROCEDURE my_procedure(values ARRAY(INTEGER))
  RETURNS ARRAY(INTEGER)
  LANGUAGE SQL
  AS
  $$
    ...
  $$;
