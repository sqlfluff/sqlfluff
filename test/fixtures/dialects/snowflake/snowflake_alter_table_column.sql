-- SET/DROP column properties
-- Single column
alter table t1 alter column c1 drop not null;
alter table t1 alter c5 comment '50 character column';

-- Multiple columns/properties
alter table t1 modify c2 drop default, c3 set default seq5.nextval ;
alter table t1 alter c4 set data type varchar(50), column c4 drop default;


-- SET Masking Policy
-- Single column
ALTER TABLE xxxx.example_table MODIFY COLUMN employeeCode SET MASKING POLICY example_MASKING_POLICY;
alter table empl_info modify column empl_id set masking policy mask_empl_id;

-- Multiple columns
alter table empl_info modify
    column empl_id set masking policy mask_empl_id
   , column empl_dob set masking policy mask_empl_dob
;


-- UNSET masking policy
-- Single column
alter table empl_info modify column empl_id unset masking policy;

-- Multiple columns
alter table empl_info modify
    column empl_id unset masking policy
  , column empl_dob unset masking policy
;

-- DROP COLUMN
ALTER TABLE empl_info DROP COLUMN my_column;
ALTER TABLE some_schema.empl_info DROP COLUMN my_column;
