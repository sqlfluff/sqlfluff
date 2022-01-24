-- Assuming the students table is in '/user/hive/warehouse/'
LOAD DATA LOCAL INPATH '/user/hive/warehouse/students'
OVERWRITE INTO TABLE test_load;

-- Assuming the test_partition table is in '/user/hive/warehouse/'
LOAD DATA LOCAL INPATH '/user/hive/warehouse/test_partition/c2=2/c3=3'
OVERWRITE INTO TABLE test_load_partition PARTITION (c2 = 2, c3 = 3);

-- Assuming the students table is in '/user/hive/warehouse/'
LOAD DATA INPATH '/user/hive/warehouse/students'
OVERWRITE INTO TABLE test_load;

-- Assuming the test_partition table is in '/user/hive/warehouse/'
LOAD DATA LOCAL INPATH '/user/hive/warehouse/test_partition/c2=2/c3=3'
INTO TABLE test_load_partition PARTITION (c2 = 2, c3 = 3);

-- Assuming the test_partition table is in '/user/hive/warehouse/'
LOAD DATA INPATH '/user/hive/warehouse/test_partition/c2=2/c3=3'
INTO TABLE test_load_partition PARTITION (c2 = 2, c3 = 3);
