-- REPAIR TABLE with all optional syntax
MSCK TABLE table_identifier ADD PARTITIONS;
MSCK TABLE table_identifier DROP PARTITIONS;
MSCK TABLE table_identifier SYNC PARTITIONS;

-- REPAIR TABLE with no optional syntax
MSCK TABLE table_identifier;

-- run MSCK REPAIR TABLE to recovers all the partitions
MSCK TABLE t1;

MSCK TABLE emp_part DROP PARTITIONS;
