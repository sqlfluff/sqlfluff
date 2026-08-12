-- CREATE STREAM clauses
-- https://docs.snowflake.com/en/sql-reference/sql/create-stream

CREATE OR REPLACE STREAM s WITH TAG (cost_center = 'sales') COPY GRANTS ON TABLE t;

CREATE STREAM s TAG (cost_center = 'sales', team = 'data') ON TABLE t;

CREATE STREAM s ON TABLE t AT (STREAM => 'oldstream');

CREATE STREAM s ON TABLE t BEFORE (STREAM => 'oldstream');

CREATE STREAM s ON EVENT TABLE et;

CREATE STREAM IF NOT EXISTS s ON EVENT TABLE my_db.my_schema.et COMMENT = 'event table stream';

CREATE OR REPLACE STREAM s CLONE s2 COPY GRANTS;

CREATE STREAM s CLONE s2 AT (OFFSET => -60) COPY GRANTS;

CREATE OR ALTER STREAM s ON TABLE t APPEND_ONLY = TRUE;

CREATE OR ALTER STREAM s ON TABLE t APPEND_ONLY = TRUE COMMENT = 'append only stream';

-- AT ( STREAM => ... ) is also valid in time travel queries
SELECT * FROM mytable AT (STREAM => 'mystream');

SELECT * FROM mytable BEFORE (STREAM => 'mystream');
