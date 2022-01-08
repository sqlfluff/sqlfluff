-- Removes all rows from the table in the partition specified
TRUNCATE TABLE Student partition(age=10);

-- Removes all rows from the table from all partitions
TRUNCATE TABLE Student;
