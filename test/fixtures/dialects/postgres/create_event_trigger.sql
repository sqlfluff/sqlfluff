CREATE EVENT TRIGGER abort_ddl ON ddl_command_start
EXECUTE FUNCTION abort_any_command();

CREATE EVENT TRIGGER log_drops ON sql_drop
EXECUTE PROCEDURE log_drop();

CREATE EVENT TRIGGER no_table_ddl ON ddl_command_end
WHEN TAG IN ('CREATE TABLE', 'ALTER TABLE', 'DROP TABLE')
EXECUTE FUNCTION abort_any_command();

CREATE EVENT TRIGGER rewrite_watch ON table_rewrite
WHEN tag IN ('ALTER TABLE', 'ALTER TYPE')
EXECUTE FUNCTION abort_any_command();

CREATE EVENT TRIGGER on_login ON login
EXECUTE FUNCTION on_login_fn();
