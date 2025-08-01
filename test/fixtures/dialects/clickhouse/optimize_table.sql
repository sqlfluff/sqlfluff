-- Test OPTIMIZE TABLE statements

OPTIMIZE TABLE test_table;

OPTIMIZE TABLE test_table ON CLUSTER my_cluster;

OPTIMIZE TABLE test_table FINAL;

OPTIMIZE TABLE test_table PARTITION 'partition_key';

OPTIMIZE TABLE test_table PARTITION (2023, 1);

OPTIMIZE TABLE test_table FINAL SETTINGS optimize_skip_merged_partitions=1;

OPTIMIZE TABLE test_table ON CLUSTER my_cluster FINAL;

OPTIMIZE TABLE test_table PARTITION 'partition_key' SETTINGS optimize_skip_merged_partitions=1;