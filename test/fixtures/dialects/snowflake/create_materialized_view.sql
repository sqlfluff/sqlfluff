-- CREATE MATERIALIZED VIEW
-- https://docs.snowflake.com/en/sql-reference/sql/create-materialized-view

CREATE MATERIALIZED VIEW mv1 AS SELECT a, b FROM t;

CREATE MATERIALIZED VIEW mv_cluster CLUSTER BY (a, b) AS SELECT a, b FROM t;

CREATE OR REPLACE MATERIALIZED VIEW mv_cluster_expr
CLUSTER BY (TO_DATE(ts), a)
AS
SELECT
    ts,
    a
FROM t;

CREATE SECURE INTERACTIVE MATERIALIZED VIEW mv_interactive AS SELECT a FROM t;

CREATE INTERACTIVE MATERIALIZED VIEW IF NOT EXISTS mv_interactive2 AS SELECT a FROM t;

CREATE SECURE MATERIALIZED VIEW mv_full (
    id COMMENT 'the id',
    email WITH MASKING POLICY email_mask
)
COPY GRANTS
COMMENT = 'a materialized view with most clauses'
WITH ROW ACCESS POLICY my_rap ON (id)
CLUSTER BY (id)
WITH TAG (cost_center = 'sales')
AS
SELECT
    id,
    email
FROM t;

-- RECURSIVE is documented after the temporary keywords
CREATE SECURE TEMPORARY RECURSIVE VIEW v_recursive_after_temp AS SELECT a FROM t;

CREATE SECURE RECURSIVE VIEW v_recursive_before_temp AS SELECT a FROM t;
