-- ClickHouse C-style ternary conditional operator `cond ? then : else`,
-- shorthand for if(cond, then, else).
-- https://clickhouse.com/docs/en/sql-reference/functions/conditional-functions#ternary-operator
SELECT col = '' ? 0 : 1 AS x FROM t;

SELECT a ? b : c AS x FROM t;

-- Right-associative chaining in the else branch.
SELECT a ? b : c ? d : e AS x FROM t;

-- Nested ternary in the then branch.
SELECT a ? b ? c : d : e AS x FROM t;

SELECT number % 2 ? 'odd' : 'even' AS parity FROM numbers(10);
