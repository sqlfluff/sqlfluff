ALTER TABLE target_table ADD PARTITION (partition_code = '202601');

ALTER TABLE target_table DROP PARTITION (partition_code = '202601');

ALTER TABLE target_table RECOVER PARTITIONS;
