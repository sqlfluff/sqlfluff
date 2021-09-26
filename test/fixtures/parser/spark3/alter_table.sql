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
-- TODO: ALTER COLUMN SYNTAX THROWS AN ERROR;
-- TODO: BELIEVE IT STARTS TRYING TO MATCH ALTER IN OUTER SCOPE
--ALTER TABLE StudentInfo ALTER COLUMN --Name --COMMENT "new comment";

ALTER TABLE StudentInfo CHANGE COLUMN Name COMMENT "new comment" ;

---- Add a new partition to a table
ALTER TABLE StudentInfo ADD IF NOT EXISTS PARTITION (Age = 18);

---- Drop a partition from the table
--ALTER TABLE StudentInfo DROP IF EXISTS PARTITION (age=18);
--
---- Adding multiple partitions to the table
--ALTER TABLE StudentInfo ADD
--    IF NOT EXISTS PARTITION (age=18) PARTITION (age=20);
--
--
---- Change the fileformat
--ALTER TABLE loc_orc SET fileformat orc;
--
--ALTER TABLE p1 partition (month=2, day=2) SET fileformat parquet;
--
---- Change the file Location
--ALTER TABLE dbx.tab1 PARTITION (a='1', b='2')
--    SET LOCATION '/path/to/part/ways'
--
---- SET SERDE/ SERDE Properties
--ALTER TABLE test_tab SET SERDE
--    'org.apache.hadoop.hive.serde2.columnar.LazyBinaryColumnarSerDe';
--
--ALTER TABLE dbx.tab1 SET SERDE'org.apache.hadoop'
--    WITH SERDEPROPERTIES ('k' = 'v', 'kay' = 'vee')
--
---- SET TABLE PROPERTIES
--ALTER TABLE dbx.tab1 SET TBLPROPERTIES ('winner' = 'loser');
--
---- SET TABLE COMMENT Using SET PROPERTIES
--ALTER TABLE dbx.tab1 SET TBLPROPERTIES ('comment' = 'A table comment.');
--
---- Alter TABLE COMMENT Using SET PROPERTIES
--ALTER TABLE dbx.tab1 SET TBLPROPERTIES ('comment' = 'This is a new comment.');
--
---- DROP TABLE PROPERTIES
--ALTER TABLE dbx.tab1 UNSET TBLPROPERTIES ('winner');
