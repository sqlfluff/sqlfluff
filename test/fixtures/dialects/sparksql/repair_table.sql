-- REPAIR TABLE with all optional syntax
MSCK REPAIR TABLE table_identifier ADD PARTITIONS;
MSCK REPAIR TABLE table_identifier DROP PARTITIONS;
MSCK REPAIR TABLE table_identifier SYNC PARTITIONS;

-- REPAIR TABLE with no optional syntax
MSCK REPAIR TABLE table_identifier;

-- run MSCK REPAIR TABLE to recovers all the partitions
MSCK REPAIR TABLE t1;
