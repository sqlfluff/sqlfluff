---- RENAME table
ALTER TABLE Student RENAME TO StudentInfo;

---- RENAME partition
ALTER TABLE Default.StudentInfo PARTITION (
    Age = '10'
) RENAME TO PARTITION (
    Age = '15'
);

-- Add new columns to a table
ALTER TABLE StudentInfo ADD COLUMNS (LastName STRING, DOB TIMESTAMP);

-- ALTER OR CHANGE COLUMNS
ALTER TABLE StudentInfo ALTER COLUMN Name COMMENT "new comment";

ALTER TABLE StudentInfo CHANGE COLUMN Name COMMENT "new comment";

---- Add a new partition to a table
ALTER TABLE StudentInfo ADD IF NOT EXISTS PARTITION (Age = 18);

-- Adding multiple partitions to the table
ALTER TABLE StudentInfo ADD IF NOT EXISTS PARTITION (
    Age = 18
) PARTITION (Age = 20);

-- Drop a partition from the table
ALTER TABLE StudentInfo DROP IF EXISTS PARTITION (Age = 18);

-- SET TABLE PROPERTIES
ALTER TABLE Dbx.Tab1 SET TBLPROPERTIES ('winner' = 'loser');

-- SET TABLE COMMENT Using SET PROPERTIES
ALTER TABLE Dbx.Tab1 SET TBLPROPERTIES ('comment' = 'A table comment.');

-- Alter TABLE COMMENT Using SET PROPERTIES
ALTER TABLE Dbx.Tab1 SET TBLPROPERTIES ('comment' = 'This is a new comment.');

-- DROP TABLE PROPERTIES
ALTER TABLE Dbx.Tab1 UNSET TBLPROPERTIES ('winner');

-- SET SERDE/ SERDE Properties
ALTER TABLE Table_Identifier
SET SERDEPROPERTIES ( "key1" = "val1", "key2" = "val2");

ALTER TABLE Test_Tab SET SERDE
'org.apache.hadoop.hive.serde2.columnar.LazyBinaryColumnarSerDe';

ALTER TABLE Dbx.Tab1 SET SERDE 'org.apache.hadoop'
WITH SERDEPROPERTIES ('k' = 'v', 'kay' = 'vee');

-- Change the fileformat
ALTER TABLE Loc_Orc SET FILEFORMAT ORC;

ALTER TABLE P1 PARTITION (Month = 2, Day = 2) SET FILEFORMAT PARQUET;

-- Change the file Location
ALTER TABLE Dbx.Tab1
SET LOCATION '/path/to/part/ways';

ALTER TABLE Dbx.Tab1 PARTITION (A = '1', B = '2')
SET LOCATION '/path/to/part/ways';

-- Recover Partitions
ALTER TABLE Dbx.Tab1 RECOVER PARTITIONS;
