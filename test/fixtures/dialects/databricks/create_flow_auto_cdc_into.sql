-- Taken directly from
-- https://docs.databricks.com/aws/en/ldp/cdc#process-scd-type-1-updates

CREATE FLOW flowname AS AUTO CDC INTO
  target
FROM
  stream(cdc_data.users)
KEYS
  (userId)
APPLY AS DELETE WHEN
  operation = "DELETE"
APPLY AS TRUNCATE WHEN
  operation = "TRUNCATE"
SEQUENCE BY
  sequenceNum
COLUMNS * EXCEPT
  (operation, sequenceNum)
STORED AS
  SCD TYPE 1;

-- Taken directly from
-- https://docs.databricks.com/aws/en/ldp/cdc#process-scd-type-2-updates

CREATE FLOW target_flow
AS AUTO CDC INTO
  target
FROM
  stream(cdc_data.users)
KEYS
  (userId)
APPLY AS DELETE WHEN
  operation = "DELETE"
SEQUENCE BY
  sequenceNum
COLUMNS * EXCEPT
  (operation, sequenceNum)
STORED AS
  SCD TYPE 2;

CREATE FLOW target_flow
AS AUTO CDC INTO
  target
FROM
  stream(cdc_data.users)
KEYS
  (userId)
APPLY AS DELETE WHEN
  operation = "DELETE"
SEQUENCE BY
  sequenceNum
COLUMNS * EXCEPT
  (operation, sequenceNum)
STORED AS
  SCD TYPE 2
TRACK HISTORY ON * EXCEPT
  (city);

-- Taken directly from
-- https://docs.databricks.com/aws/en/ldp/developer/ldp-sql-ref-apply-changes-into#examples

CREATE FLOW flow
AS AUTO CDC INTO
  target
FROM stream(cdc_data.users)
  KEYS (userId)
  APPLY AS DELETE WHEN operation = "DELETE"
  SEQUENCE BY sequenceNum
  COLUMNS * EXCEPT (operation, sequenceNum)
  STORED AS SCD TYPE 2
  TRACK HISTORY ON * EXCEPT (city);
