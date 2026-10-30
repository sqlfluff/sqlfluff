ALTER AGGREGATION POLICY my_agg_policy
    SET BODY -> AGGREGATION_CONSTRAINT(MIN_GROUP_SIZE => 10);

ALTER AGGREGATION POLICY IF EXISTS my_agg_policy RENAME TO new_agg_policy;

ALTER AGGREGATION POLICY my_agg_policy SET TAG governance.tags.owner = 'data_team';

ALTER AGGREGATION POLICY my_agg_policy UNSET TAG governance.tags.owner;

ALTER AGGREGATION POLICY my_agg_policy SET COMMENT = 'updated';

ALTER AGGREGATION POLICY my_agg_policy UNSET COMMENT;
