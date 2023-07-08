ALTER TABLE my_old_table RENAME TO my_new_table;

ALTER TABLE my_existing_table SWAP WITH my_another_table;

ALTER TABLE my_existing_table ADD SEARCH OPTIMIZATION;

ALTER TABLE my_existing_table DROP SEARCH OPTIMIZATION;

ALTER TABLE my_table SET DATA_RETENTION_TIME_IN_DAYS = 30;

ALTER TABLE my_table SET DEFAULT_DDL_COLLATION = 'en-ci';

ALTER TABLE my_table SET COMMENT = 'my table comment';

ALTER TABLE table1 ADD CONSTRAINT constraint1 PRIMARY KEY ( col1 );

ALTER TABLE table1 ADD CONSTRAINT constraint1 FOREIGN KEY ( col1 ) REFERENCES table2 ( col2 );

ALTER TABLE table1 DROP CONSTRAINT constraint1 UNIQUE pk_col, pk_col2;

ALTER TABLE table1 RENAME CONSTRAINT constraint1 TO constraint2;
