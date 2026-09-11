-- ALTER PROCEDURE options and CALL ... INTO
-- https://docs.snowflake.com/en/sql-reference/sql/alter-procedure
-- https://docs.snowflake.com/en/sql-reference/sql/call

ALTER PROCEDURE p(FLOAT) EXECUTE AS RESTRICTED CALLER;

ALTER PROCEDURE p(VARCHAR) SET METRIC_LEVEL = ALL;

ALTER PROCEDURE p(VARCHAR) SET METRIC_LEVEL = 'ALL';

ALTER PROCEDURE p() SET AUTO_EVENT_LOGGING = 'TRACING';

ALTER PROCEDURE p() SET AUTO_EVENT_LOGGING = ALL;

ALTER PROCEDURE p(INT) SET LOG_LEVEL = 'INFO';

ALTER PROCEDURE p(INT) SET TRACE_LEVEL = 'ON_EVENT';

ALTER PROCEDURE p(INT) SET LOG_LEVEL = 'INFO', TRACE_LEVEL = 'ALWAYS';

CALL sv_proc1('Manitoba', 127.4) INTO :ret1;

CALL my_db.my_schema.sv_proc1() INTO :result;

CALL sv_proc1(a => 1, b => 'x') INTO :ret1;
