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
  add row access policy rap_v1_version_2 on (empl_id);

alter view v1
  modify column foo set masking policy my.scoped.policy;
