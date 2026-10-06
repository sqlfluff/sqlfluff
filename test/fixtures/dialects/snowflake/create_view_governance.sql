-- Data governance clauses on CREATE VIEW
-- https://docs.snowflake.com/en/sql-reference/sql/create-view

CREATE VIEW v_projection (c1 WITH PROJECTION POLICY pp1) AS SELECT c1 FROM t;

CREATE VIEW v_projection_no_with (c1 PROJECTION POLICY pp1) AS SELECT c1 FROM t;

CREATE VIEW v_column_mix (
    c1 WITH MASKING POLICY mp1 USING (c1, c2) WITH PROJECTION POLICY pp1 COMMENT 'a column',
    c2 WITH TAG (my_tag = 'my value')
)
AS
SELECT
    c1,
    c2
FROM t;

CREATE VIEW v_aggregation WITH AGGREGATION POLICY ap1 AS SELECT a FROM t;

CREATE VIEW v_aggregation_entity_key
WITH AGGREGATION POLICY my_db.my_schema.ap1 ENTITY KEY (a, b)
AS
SELECT
    a,
    b
FROM t;

CREATE VIEW v_join WITH JOIN POLICY jp1 AS SELECT a FROM t;

CREATE VIEW v_join_keys WITH JOIN POLICY jp1 ALLOWED JOIN KEYS (a, b) AS SELECT a, b FROM t;

CREATE VIEW v_copy_tags COPY GRANTS COPY TAGS AS SELECT a FROM t;

CREATE VIEW v_contact WITH CONTACT (STEWARD = c1) AS SELECT a FROM t;

CREATE VIEW v_contacts
WITH CONTACT (STEWARD = my_db.my_schema.c1, SUPPORT = c2)
AS
SELECT
    a
FROM t;
