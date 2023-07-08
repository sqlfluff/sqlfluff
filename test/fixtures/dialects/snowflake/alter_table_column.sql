-- Add column
---- Base cases
ALTER TABLE my_table ADD COLUMN my_column INTEGER;
ALTER TABLE my_table ADD COLUMN my_column VARCHAR(5000) NOT NULL;

------ Multiple columns
ALTER TABLE my_table ADD COLUMN column_1 varchar, column_2 integer;

---- Default, auto-increment & identity
ALTER TABLE my_table ADD COLUMN my_column INTEGER DEFAULT 1;
ALTER TABLE my_table ADD COLUMN my_column INTEGER AUTOINCREMENT;
ALTER TABLE my_table ADD COLUMN my_column INTEGER IDENTITY;
ALTER TABLE my_table ADD COLUMN my_column INTEGER AUTOINCREMENT (10000, 1);
ALTER TABLE my_table ADD COLUMN my_column INTEGER IDENTITY START 10000 INCREMENT 1;

---- Masking Policy
ALTER TABLE my_table ADD COLUMN my_column INTEGER MASKING POLICY my_policy;
ALTER TABLE my_table ADD COLUMN my_column INTEGER WITH MASKING POLICY my_policy;
ALTER TABLE my_table ADD COLUMN my_column INTEGER WITH MASKING POLICY adatabase.aschema.apolicy;
ALTER TABLE my_table ADD COLUMN my_column INTEGER WITH MASKING POLICY my_policy USING(my_column, my_column > 10);

-- comment
ALTER TABLE reporting_tbl ADD COLUMN reporting_group VARCHAR
  COMMENT 'internal reporting group defined by DE team';

-- without the word COLUMN
ALTER TABLE rpt_enc_table ADD encounter_count INTEGER COMMENT 'count of encounters past year' ;

-- Rename column
ALTER TABLE empl_info RENAME COLUMN old_col_name TO new_col_name;


-- Alter-modify column(s)
---- Base cases
------ Single column
alter table t1 alter column c1 drop not null;
alter table t1 alter c5 comment '50 character column';

------ Multiple columns/properties
alter table t1 modify c2 drop default, c3 set default seq5.nextval ;
alter table t1 alter c4 set data type varchar(50), column c4 drop default;

---- Set Masking Policy
------ Single column
ALTER TABLE xxxx.example_table MODIFY COLUMN employeeCode SET MASKING POLICY example_MASKING_POLICY;
ALTER TABLE aschema.atable MODIFY COLUMN acolumn SET MASKING POLICY adatabase.aschema.apolicy;
alter table empl_info modify column empl_id set masking policy mask_empl_id;
alter table empl_info modify column empl_id set masking policy mask_empl_id using(empl_id, empl_id > 10);

------ Multiple columns
alter table empl_info modify
    column empl_id set masking policy mask_empl_id
   , column empl_dob set masking policy mask_empl_dob
;

---- Unset masking policy
------ Single column
alter table empl_info modify column empl_id unset masking policy;

------ Multiple columns
alter table empl_info modify
    column empl_id unset masking policy
  , column empl_dob unset masking policy
;

--- Set Tag
ALTER TABLE my_table MODIFY COLUMN my_column SET TAG my_tag = 'tagged';

--- Unset Tag
ALTER TABLE my_table MODIFY COLUMN my_column UNSET TAG my_tag;

-- Drop column
ALTER TABLE empl_info DROP COLUMN my_column;
ALTER TABLE some_schema.empl_info DROP COLUMN my_column;
ALTER TABLE my_table DROP COLUMN column_1, column_2, column_3;

-- IF EXISTS
ALTER TABLE IF EXISTS my_table ADD COLUMN my_column INTEGER;
ALTER TABLE IF EXISTS empl_info DROP COLUMN my_column;
ALTER TABLE IF EXISTS empl_info DROP my_column;
ALTER TABLE IF EXISTS empl_info RENAME COLUMN old_col_name TO new_col_name;

-- DROP PRIMARY KEY
ALTER TABLE my_schema.my_table drop PRIMARY KEY;

-- ADD PRIMARY KEY
ALTER TABLE my_schema.my_table add PRIMARY KEY(TABLE_ID);
