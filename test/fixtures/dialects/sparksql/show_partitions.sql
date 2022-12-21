-- Lists all partitions for table `customer`
SHOW PARTITIONS customer;

-- Lists all partitions for the qualified table `customer`
SHOW PARTITIONS salesdb.customer;

-- Specify a full partition spec to list specific partition
SHOW PARTITIONS customer PARTITION (state = 'CA', city = 'Fremont');

-- Specify a partial partition spec to list the specific partitions
SHOW PARTITIONS customer PARTITION (state = 'CA');

-- Specify a partial spec to list specific partition
SHOW PARTITIONS customer PARTITION (city = 'San Jose');
