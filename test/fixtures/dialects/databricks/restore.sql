-- RESTORE with optional TABLE/TO and an arithmetic timestamp.
-- https://docs.databricks.com/aws/en/sql/language-manual/delta-restore
RESTORE TABLE employee TO VERSION AS OF 1;

RESTORE employee TO VERSION AS OF 1;

RESTORE TABLE employee VERSION AS OF 1;

RESTORE TABLE employee TO TIMESTAMP AS OF current_timestamp() - INTERVAL '1' HOUR;

RESTORE TABLE IDENTIFIER('employee') TO VERSION AS OF 1;
