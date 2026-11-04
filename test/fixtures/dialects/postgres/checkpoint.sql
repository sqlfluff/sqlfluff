CHECKPOINT;
checkpoint;

-- CHECKPOINT remains a statement beside ordinary queries.
SELECT checkpoint FROM maintenance_log;
CHECKPOINT /* operator-requested maintenance */;
SELECT 1;
