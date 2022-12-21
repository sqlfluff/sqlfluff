-- add columns
ALTER TABLE table_name ADD COLUMNS col_name STRING;

ALTER TABLE table_name ADD COLUMNS (col_name STRING);

ALTER TABLE table_name ADD COLUMNS col_name STRING, col_name2 INT;

ALTER TABLE table_name ADD COLUMNS col_name STRING COMMENT "col_comment" FIRST;

ALTER TABLE table_name ADD COLUMNS
    col_name STRING COMMENT "col_comment" FIRST,
    col_name2 INT COMMENT "col_2_comment" AFTER col_b_name;

-- change column comment/ordering
ALTER TABLE table_name CHANGE col_name_old col_name_new STRING;

ALTER TABLE table_name CHANGE COLUMN col_name_old col_name_new STRING;

ALTER TABLE table_name CHANGE COLUMN
    col_name_old col_name_new STRING COMMENT "new_col_comment";

ALTER TABLE table_name CHANGE COLUMN
    col_name_old col_name_new STRING COMMENT "new_col_comment" FIRST;

ALTER TABLE table_name CHANGE COLUMN
    col_name_old col_name_new STRING COMMENT "new_col_comment" AFTER col_a_name;

---- change column comment/ordering in a nested field
ALTER TABLE table_name CHANGE
    col_name_1.nested_col_name nested_col_name_new STRING;

ALTER TABLE table_name CHANGE COLUMN
    col_name_1.nested_col_name nested_col_name_new STRING;

ALTER TABLE table_name CHANGE COLUMN
    col_name_1.nested_col_name nested_col_name_new STRING
    COMMENT "new_col_comment";

ALTER TABLE table_name CHANGE COLUMN
    col_name_1.nested_col_name
    nested_col_name_new STRING
    COMMENT "new_col_comment" FIRST;

ALTER TABLE table_name CHANGE COLUMN
    col_name_1.nested_col_name
    nested_col_name_new STRING
    COMMENT "new_col_comment" AFTER col_a_name;

ALTER TABLE boxes CHANGE COLUMN col_b.a_key_name a_new_key_name STRING FIRST;

-- replace columns
ALTER TABLE table_name REPLACE COLUMNS (
    col_name1 STRING COMMENT "col_comment1"
);

ALTER TABLE boxes REPLACE COLUMNS (
    col_c STRING,
    col_b STRUCT<key2:STRING, nested:STRING, key1:STRING>,
    col_a STRING
);
