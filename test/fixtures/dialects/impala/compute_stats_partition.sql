COMPUTE STATS target_table;

COMPUTE INCREMENTAL STATS target_table PARTITION (partition_code = '202601');
