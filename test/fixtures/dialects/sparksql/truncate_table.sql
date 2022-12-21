-- Removes all rows from the table in the partition specified
TRUNCATE TABLE Student PARTITION(Age = 10);

-- Removes all rows from the table from all partitions
TRUNCATE TABLE Student;
