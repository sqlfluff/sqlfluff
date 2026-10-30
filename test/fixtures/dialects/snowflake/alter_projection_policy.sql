ALTER PROJECTION POLICY mypolicy RENAME TO proj_policy_acctnumber;

ALTER PROJECTION POLICY IF EXISTS mypolicy SET BODY -> PROJECTION_CONSTRAINT(ALLOW => true);

ALTER PROJECTION POLICY mypolicy SET TAG cost_center = 'sales', my_db.my_schema.owner = 'data_team';

ALTER PROJECTION POLICY mypolicy UNSET TAG cost_center, my_db.my_schema.owner;

ALTER PROJECTION POLICY IF EXISTS mypolicy SET COMMENT = 'updated';

ALTER PROJECTION POLICY mypolicy UNSET COMMENT;
