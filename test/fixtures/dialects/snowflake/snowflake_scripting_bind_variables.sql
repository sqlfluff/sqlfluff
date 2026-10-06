-- Snowflake Scripting bind variables used in SQL statements.
-- https://docs.snowflake.com/en/developer-guide/snowflake-scripting/variables#using-a-variable-in-a-sql-statement-binding
-- https://github.com/sqlfluff/sqlfluff/issues/5427

-- Bind variables in DML value positions.
INSERT INTO some_db.some_schema.debug_log (process, msg) VALUES (:process, 'START RUN');

SELECT :process;

SELECT a FROM t WHERE a = :process;

UPDATE t SET a = :new_value WHERE id = :target_id;

DELETE FROM t WHERE id = :target_id;

-- The reproduction case from the issue (schema renamed to avoid the
-- unrelated reserved-keyword clash on INPUT).
CREATE OR REPLACE PROCEDURE some_db.some_schema.i_am_a_procedure()
RETURNS BOOLEAN
LANGUAGE SQL
AS
BEGIN
    LET process VARCHAR := 'THIS_PROCEDURE_PROCESS_KEY';
    INSERT INTO some_db.some_schema.debug_log (process, msg) VALUES (:process, 'START RUN');
END;
