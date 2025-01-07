-- ADD column
---- Base cases
ALTER TABLE my_table ADD COLUMN my_column INTEGER;
ALTER TABLE my_table ADD COLUMN my_column VARCHAR(5000) NOT NULL;
ALTER TABLE my_table ADD COLUMN IF NOT EXISTS my_column INTEGER;

------ Multiple columns
ALTER TABLE my_table ADD COLUMN column_1 varchar, column_2 integer;
ALTER TABLE my_table ADD COLUMN IF NOT EXISTS column_1 varchar, IF NOT EXISTS column_2 integer;
ALTER TABLE my_table ADD COLUMN IF NOT EXISTS column_1 varchar, column_2 integer;

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
ALTER TABLE t1 alter column c1 drop not null;
ALTER TABLE t1 alter c5 comment '50 character column';

------ Multiple columns/properties
ALTER TABLE t1 modify c2 drop default, c3 set default seq5.nextval ;
ALTER TABLE t1 alter c4 set data type varchar(50), column c4 drop default;

---- Set Masking Policy
------ Single column
ALTER TABLE xxxx.example_table MODIFY COLUMN employeeCode SET MASKING POLICY example_MASKING_POLICY;
ALTER TABLE aschema.atable MODIFY COLUMN acolumn SET MASKING POLICY adatabase.aschema.apolicy;
ALTER TABLE empl_info modify column empl_id set masking policy mask_empl_id;
ALTER TABLE empl_info modify column empl_id set masking policy mask_empl_id using(empl_id, empl_id > 10);

------ Multiple columns
ALTER TABLE empl_info modify
    column empl_id set masking policy mask_empl_id
   , column empl_dob set masking policy mask_empl_dob
;

---- Unset masking policy
------ Single column
ALTER TABLE empl_info modify column empl_id unset masking policy;

------ Multiple columns
ALTER TABLE empl_info modify
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

-- Drop column if exists
ALTER TABLE demo_db.public DROP column IF EXISTS public_name, IF EXISTS description_text, IF EXISTS type_alias;
ALTER TABLE demo_db.public DROP column public_name,  description_text,  type_alias;
ALTER TABLE demo_db.public DROP public_name,  description_text,  type_alias;
ALTER TABLE demo_db.public DROP IF EXISTS public_name, IF EXISTS description_text, IF EXISTS type_alias;

-- IF EXISTS
ALTER TABLE IF EXISTS my_table ADD COLUMN my_column INTEGER;
ALTER TABLE IF EXISTS empl_info DROP COLUMN my_column;
ALTER TABLE IF EXISTS empl_info DROP my_column;
ALTER TABLE IF EXISTS empl_info RENAME COLUMN old_col_name TO new_col_name;

-- DROP PRIMARY KEY
ALTER TABLE my_schema.my_table drop PRIMARY KEY;

-- ADD PRIMARY KEY
ALTER TABLE my_schema.my_table ADD PRIMARY KEY(TABLE_ID);

-- ADD Virtual/Calculated columns
ALTER TABLE some_schema.some_table ADD some_column_upr VARCHAR AS UPPER(some_column) COMMENT 'This is a virtual column';
ALTER TABLE some_schema.some_table ADD column IF NOT EXISTS some_other_column_upr VARCHAR AS UPPER(some_column) || 'some characters' || LOWER(some_column);
ALTER TABLE some_schema.some_table ADD column IF NOT EXISTS some_column_upr VARCHAR AS (UPPER(some_column));
ALTER TABLE some_schema.some_table ADD column IF NOT EXISTS some_event_date_time_utc TIMESTAMP AS (IFF(is_condition_true AND TRY_TO_NUMBER(some_text_value) IS NOT NULL, TO_TIMESTAMP(SUBSTR(some_text_value, 5, 13)), '1900-01-01'));

ALTER TABLE IF EXISTS table1 ADD COLUMN IF NOT EXISTS some_column INTEGER NOT NULL;
