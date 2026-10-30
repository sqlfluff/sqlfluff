ALTER AGGREGATION POLICY my_policy SET BODY -> AGGREGATION_CONSTRAINT(MIN_GROUP_SIZE=>2);

ALTER AGGREGATION POLICY my_policy RENAME TO agg_policy_table1;

ALTER AGGREGATION POLICY IF EXISTS my_policy RENAME TO my_db.my_schema.agg_policy_table1;

ALTER AGGREGATION POLICY my_policy SET TAG cost_center = 'sales', my_db.my_schema.owner = 'data_team';

ALTER AGGREGATION POLICY my_policy UNSET TAG cost_center, my_db.my_schema.owner;

ALTER AGGREGATION POLICY IF EXISTS my_policy SET COMMENT = 'updated';

ALTER AGGREGATION POLICY my_policy UNSET COMMENT;
