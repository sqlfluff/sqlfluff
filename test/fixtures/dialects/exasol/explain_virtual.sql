SELECT pushdown_id, pushdown_involved_tables, pushdown_sql FROM
(EXPLAIN VIRTUAL SELECT * FROM vs_impala.sample_07 WHERE total_emp>10000);
EXPLAIN VIRTUAL SELECT * FROM vs_impala.sample_07 WHERE total_emp>10000;
