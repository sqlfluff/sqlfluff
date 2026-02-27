alter view view1 rename to view2;

alter view view1 set secure;

alter view view1 unset secure;

-- single column

alter view user_info_v modify column ssn_number set masking policy ssn_mask_v;

-- multiple columns

alter view user_info_v modify
    column ssn_number set masking policy ssn_mask_v
  , column dob set masking policy dob_mask_v
;

-- single column

alter view user_info_v modify column ssn_number unset masking policy;

-- multiple columns

alter view user_info_v modify
    column ssn_number unset masking policy
  , column dob unset masking policy
;

alter view v1
  add row access policy rap_v1 on (empl_id);

alter view v1
  drop row access policy rap_v1;

alter view v1
  drop row access policy rap_v1_version_1,
  add row access policy rap_v1_version_2 on (empl_id),
  add row access policy rap_v1_version_3 on ("empl_id");

alter view v1
  modify column foo set masking policy my.scoped.policy;

ALTER VIEW "my_table" ALTER COLUMN "my_column" SET MASKING POLICY my_masking_policy FORCE;

-- SET CHANGE_TRACKING
ALTER VIEW v1 SET CHANGE_TRACKING = TRUE;

ALTER VIEW IF EXISTS v1 SET CHANGE_TRACKING = FALSE;

-- SET/UNSET AGGREGATION POLICY
ALTER VIEW v1 SET AGGREGATION POLICY my_policy;

ALTER VIEW v1 SET AGGREGATION POLICY my_policy ENTITY KEY (col1, col2) FORCE;

ALTER VIEW v1 UNSET AGGREGATION POLICY;

-- ADD/DROP DATA METRIC FUNCTION
ALTER VIEW v1 ADD DATA METRIC FUNCTION my_dmf ON (col1);

ALTER VIEW v1 DROP DATA METRIC FUNCTION my_dmf ON (col1, col2);

ALTER VIEW v1 MODIFY DATA METRIC FUNCTION my_dmf ON (col1) SUSPEND;

ALTER VIEW v1 ALTER DATA METRIC FUNCTION my_dmf ON (col1) RESUME;

-- Column-level PROJECTION POLICY
ALTER VIEW v1 ALTER COLUMN col1 SET PROJECTION POLICY my_proj_policy;

ALTER VIEW v1 MODIFY COLUMN col1 SET PROJECTION POLICY my_proj_policy FORCE;

ALTER VIEW v1 ALTER COLUMN col1 UNSET PROJECTION POLICY;
