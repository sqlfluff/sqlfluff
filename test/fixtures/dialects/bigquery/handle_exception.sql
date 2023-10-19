-- Basic block
BEGIN
  SELECT * FROM one_table;
END;

-- Block showcasing use of in-scope variables
DECLARE x INT64 DEFAULT 10;
BEGIN
  DECLARE y INT64;
  SET y = x;
  SELECT y;
END;
SELECT x;

-- Basic exception block
BEGIN
  SELECT 1/0;
EXCEPTION WHEN ERROR THEN
  RAISE USING MESSAGE = "An error happened";
END;

-- Exception block utilising @error
BEGIN
  SELECT 100/0;
EXCEPTION WHEN ERROR THEN
  RAISE USING MESSAGE = FORMAT("Something went wrong: %s", @@error.message);
END;

-- More complicated block with multiple statements
BEGIN
  EXPORT DATA OPTIONS(
    uri='gs://bucket/folder/*.csv',
    format='CSV',
    overwrite=true,
    header=true,
    field_delimiter=';'
  ) AS (
    SELECT field1, field2 FROM mydataset.table1 ORDER BY field1 LIMIT 10
  );

  SELECT 1/0;
EXCEPTION WHEN ERROR THEN
  DELETE FROM mydataset.table1 WHERE field1 = '1';

  RAISE USING MESSAGE = FORMAT("Something went wrong: %s", @@error.message);

  RETURN;
END;
