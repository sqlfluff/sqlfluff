SELECT
    COUNT(*) FILTER (WHERE c_expires > CURRENT_TIMESTAMP) AS c_active
FROM t_test;
