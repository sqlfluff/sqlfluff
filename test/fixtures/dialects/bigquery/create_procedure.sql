CREATE OR REPLACE PROCEDURE `mfrm_working_temp_dataset.temp` (incremental INT64)
BEGIN
    SELECT CURRENT_DATETIME();
END;

CREATE PROCEDURE myProject.myDataset.QueryTable()
BEGIN
  SELECT * FROM anotherDataset.myTable;
END;

CREATE PROCEDURE mydataset.AddDelta(INOUT x INT64, delta INT64)
BEGIN
  SET x = x + delta;
END;

CREATE PROCEDURE mydataset.SelectFromTablesAndAppend(
  target_date DATE, OUT rows_added INT64)
BEGIN
  CREATE TEMP TABLE DataForTargetDate AS
  SELECT t1.id, t1.x, t2.y
  FROM dataset.partitioned_table1 AS t1
  JOIN dataset.partitioned_table2 AS t2
  ON t1.id = t2.id
  WHERE t1.date = target_date
    AND t2.date = target_date;

  SET rows_added = (SELECT COUNT(*) FROM DataForTargetDate);

  SELECT id, x, y, target_date  -- note that target_date is a parameter
  FROM DataForTargetDate;

  DROP TABLE DataForTargetDate;
END;

CREATE OR REPLACE PROCEDURE mydataset.create_customer()
BEGIN
  DECLARE id STRING;
  SET id = GENERATE_UUID();
  INSERT INTO mydataset.customers (customer_id)
    VALUES(id);
  SELECT FORMAT("Created customer %s", id);
END;

CREATE OR REPLACE PROCEDURE mydataset.create_customer(name STRING)
BEGIN
DECLARE id STRING;
SET id = GENERATE_UUID();
INSERT INTO mydataset.customers (customer_id, name)
  VALUES(id, name);
SELECT FORMAT("Created customer %s (%s)", id, name);
END;

CREATE OR REPLACE PROCEDURE mydataset.create_customer(name STRING, OUT id STRING)
BEGIN
SET id = GENERATE_UUID();
INSERT INTO mydataset.customers (customer_id, name)
  VALUES(id, name);
SELECT FORMAT("Created customer %s (%s)", id, name);
END;

CREATE OR REPLACE PROCEDURE mydataset.test_raise_return(error_message STRING)
BEGIN
RETURN;
RAISE;
RAISE USING MESSAGE = "Test";
RAISE USING MESSAGE = error_message;
END;
