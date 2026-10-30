ALTER PROJECTION POLICY my_proj_policy
    SET BODY -> PROJECTION_CONSTRAINT(ALLOW => true);

ALTER PROJECTION POLICY IF EXISTS my_proj_policy RENAME TO new_proj_policy;

ALTER PROJECTION POLICY my_proj_policy SET TAG governance.tags.owner = 'data_team';

ALTER PROJECTION POLICY my_proj_policy UNSET TAG governance.tags.owner;

ALTER PROJECTION POLICY my_proj_policy SET COMMENT = 'updated';

ALTER PROJECTION POLICY my_proj_policy UNSET COMMENT;
