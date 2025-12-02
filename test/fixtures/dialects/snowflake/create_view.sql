
create view another_view comment = 'a great description' as select col_1, col_2 from other_table;

CREATE VIEW basic_view AS SELECT col1, col2 FROM src_table;

CREATE TEMPORARY VIEW view_with_comments
COMMENT = 'my comment' AS SELECT col1, col2 FROM src_table;

CREATE OR REPLACE VIEW view_with_replace_and_comment
COMMENT = 'my comment' AS SELECT col1, col2 FROM src_table;

CREATE OR REPLACE SECURE RECURSIVE VIEW IF NOT EXISTS secure_recursive_view_with_comment
COMMENT = 'my comment' AS SELECT col1, col2 FROM src_table;

CREATE OR REPLACE VIEW view_with_comment_and_copy_grants
COMMENT = 'my comment'
COPY GRANTS
AS SELECT col1, col2 FROM src_table;

CREATE OR REPLACE VIEW view_with_tags_and_copy_grants
WITH TAG (foo = 'bar', hello = 'world')
COPY GRANTS
AS SELECT col1, col2 FROM src_table;

CREATE OR REPLACE VIEW view_with_tags_and_copy_grants
WITH TAG (foo = "bar", hello = "world")
COPY GRANTS
AS SELECT col1, col2 FROM src_table;

CREATE OR REPLACE VIEW view_with_column_comment
(
    col1,
    col2 COMMENT 'some comment'
)
AS SELECT col1, col2 FROM src_table;

CREATE OR REPLACE SECURE RECURSIVE VIEW IF NOT EXISTS view_with_all_implemented_features
    COMMENT = 'table-level comment'
    (
        col1,
        col2 COMMENT 'some comment'
    )
AS
WITH cte AS (SELECT col1 FROM table_1)
SELECT col1, col2
FROM table_2
INNER JOIN my_cte ON table_1.pk = table_2.pk;

CREATE OR REPLACE VIEW vw_appt_latest AS (
  WITH most_current as (
      SELECT
            da.*
      FROM dim_appt da
      WHERE da.current_appt_id IS NULL
      )
  SELECT * from most_current
);

CREATE OR REPLACE VIEW IF NOT EXISTS view_with_rls
(
    COL1,
    COL2
) WITH ROW ACCESS POLICY my_db.my_schema.my_policy ON (COL1) AS (
  SELECT
    COL1,
    COL2
  FROM my_table
);


CREATE OR REPLACE VIEW IF NOT EXISTS view_with_rls
(
    COL1 WITH MASKING POLICY my_db.my_schema.my_policy,
    COL2
) WITH ROW ACCESS POLICY my_db.my_schema.my_policy ON (COL1) AS (
  SELECT
    COL1,
    COL2
  FROM my_table
);

CREATE OR REPLACE MATERIALIZED VIEW IF NOT EXISTS view_with_rls
(
    COL1,
    COL2
) WITH ROW ACCESS POLICY my_db.my_schema.my_policy ON (COL1) AS (
  SELECT
    COL1,
    COL2
  FROM my_table
);

CREATE OR REPLACE VIEW IF NOT EXISTS view_with_column_tags
(
    COL1 WITH TAG (my_db.my_schema.my_policy='MY_TAG'),
    COL2
) AS (
  SELECT
    COL1,
    COL2
  FROM my_table
);

CREATE OR ALTER VIEW view_with_column_comment
(
    col1
)
AS SELECT col1
FROM src_table;
