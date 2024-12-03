-- ALTER TABLE examples from Databricks documentation
-- https://docs.databricks.com/en/sql/language-manual/sql-ref-syntax-ddl-alter-table.html

ALTER TABLE Student RENAME TO StudentInfo;

ALTER TABLE default.StudentInfo PARTITION (age='10') RENAME TO PARTITION (age='15');

ALTER TABLE StudentInfo ADD columns (LastName string, DOB timestamp);

ALTER TABLE StudentInfo DROP COLUMN (DOB);

ALTER TABLE StudentInfo DROP COLUMNS IF EXISTS (LastName, DOB);

ALTER TABLE StudentInfo ADD IF NOT EXISTS PARTITION (age=18);

ALTER TABLE StudentInfo DROP IF EXISTS PARTITION (age=18);

ALTER TABLE StudentInfo ADD IF NOT EXISTS PARTITION (age=18) PARTITION (age=20);

ALTER TABLE StudentInfo RECOVER PARTITIONS;

ALTER TABLE StudentInfo ALTER COLUMN name COMMENT "new comment";

ALTER TABLE StudentInfo RENAME COLUMN name TO FirstName;

-- Change the file Location
ALTER TABLE dbx.tab1 PARTITION (a='1', b='2') SET LOCATION '/path/to/part/ways';

-- SET SERDE/ SERDE Properties (DBR only)
ALTER TABLE test_tab SET SERDE 'org.apache.hadoop.hive.serde2.columnar.LazyBinaryColumnarSerDe';

ALTER TABLE dbx.tab1 SET SERDE 'org.apache.hadoop' WITH SERDEPROPERTIES ('k' = 'v', 'kay' = 'vee');

-- SET TABLE PROPERTIES
ALTER TABLE dbx.tab1 SET TBLPROPERTIES ('winner' = 'loser');

-- DROP TABLE PROPERTIES
ALTER TABLE dbx.tab1 UNSET TBLPROPERTIES ('winner');

-- Drop the "deletion vectors" from a Delta table
ALTER TABLE my_table DROP FEATURE deletionVectors;

-- 24 hours later
ALTER TABLE my_table DROP FEATURE deletionVectors TRUNCATE HISTORY;

-- Applies three tags to the table named `test`.
ALTER TABLE test SET TAGS ('tag1' = 'val1', 'tag2' = 'val2', 'tag3' = 'val3');

-- Removes three tags from the table named `test`.
ALTER TABLE test UNSET TAGS ('tag1', 'tag2', 'tag3');

-- Applies three tags to table `main.schema1.test` column `col1`.
ALTER TABLE main.schema1.test ALTER COLUMN col1 SET TAGS ('tag1' = 'val1', 'tag2' = 'val2', 'tag3' = 'val3');

-- Removes three tags from table `main.schema1.test` column `col1`.
ALTER TABLE main.schema1.test ALTER COLUMN col1 UNSET TAGS ('tag1', 'tag2', 'tag3');

-- Enables predictive optimization for my_table
ALTER TABLE my_table ENABLE PREDICTIVE OPTIMIZATION;

ALTER TABLE sales SET ROW FILTER us_filter ON ();

ALTER TABLE sales SET ROW FILTER us_filter ON (region);

ALTER TABLE sales DROP ROW FILTER;

ALTER TABLE users ALTER COLUMN ssn SET MASK ssn_mask;

ALTER TABLE users ALTER COLUMN ssn SET MASK ssn_mask USING COLUMNS (ssn_value);

ALTER TABLE users ALTER COLUMN ssn DROP MASK;

ALTER TABLE persons ADD CONSTRAINT persons_pk PRIMARY KEY(first_name, last_name);

ALTER TABLE pets ADD CONSTRAINT pets_persons_fk
    FOREIGN KEY(owner_first_name, owner_last_name) REFERENCES persons
    NOT ENFORCED RELY;

ALTER TABLE pets ADD CONSTRAINT pets_name_not_cute_chk CHECK (length(name) < 20);

ALTER TABLE pets DROP CONSTRAINT pets_name_not_cute_chk;

ALTER TABLE persons DROP CONSTRAINT persons_pk RESTRICT;

ALTER TABLE pets DROP FOREIGN KEY IF EXISTS  (owner_first_name, owner_last_name);

ALTER TABLE persons DROP PRIMARY KEY CASCADE;

ALTER TABLE rocks DROP COLUMN rock;

ALTER TABLE rocks DROP COLUMN rock, loc;

ALTER TABLE rocks DROP COLUMN IF EXISTS rock, loc;

ALTER TABLE rocks DROP COLUMN IF EXISTS (rock, loc);
