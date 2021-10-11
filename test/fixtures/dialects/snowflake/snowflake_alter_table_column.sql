alter table t1 alter column c1 drop not null;

alter table t1 modify c2 drop default, c3 set default seq5.nextval ;

alter table t1 alter c4 set data type varchar(50), column c4 drop default;

alter table t1 alter c5 comment '50 character column';

ALTER TABLE xxxx.example_table MODIFY COLUMN employeeCode SET MASKING POLICY example_MASKING_POLICY;

alter table empl_info modify column empl_id set masking policy mask_empl_id;

-- multiple columns

alter table empl_info modify
    column empl_id set masking policy mask_empl_id
   , column empl_dob set masking policy mask_empl_dob
;

-- single column

alter table empl_info modify column empl_id unset masking policy;

-- multiple columns

alter table empl_info modify
    column empl_id unset masking policy
  , column empl_dob unset masking policy
;
