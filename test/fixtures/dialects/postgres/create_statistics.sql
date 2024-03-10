CREATE STATISTICS s3 (ndistinct) ON date_trunc('month', a), date_trunc('day', a) FROM t3;
CREATE STATISTICS my_statistic (dependencies) ON foo, bar FROM baz;
CREATE STATISTICS IF NOT EXISTS s3 (ndistinct, mcv, dependencies) ON date_trunc('month', a), date_trunc('day', a) FROM t3;
