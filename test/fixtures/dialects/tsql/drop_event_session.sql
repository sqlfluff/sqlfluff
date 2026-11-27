-- https://learn.microsoft.com/en-us/sql/t-sql/statements/drop-event-session-transact-sql
DROP EVENT SESSION test_session ON SERVER;

DROP EVENT SESSION [test_session] ON DATABASE;

IF EXISTS (SELECT 1 FROM sys.server_event_sessions WHERE name = 'test_session')
    DROP EVENT SESSION test_session ON SERVER;
