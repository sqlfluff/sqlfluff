-- https://learn.microsoft.com/en-us/sql/t-sql/statements/alter-event-session-transact-sql
ALTER EVENT SESSION test_session ON SERVER STATE = START;

ALTER EVENT SESSION [test_session] ON DATABASE STATE = STOP;

ALTER EVENT SESSION test_session ON SERVER
ADD EVENT sqlserver.lock_escalation,
ADD EVENT sqlserver.lock_timeout (
    ACTION (sqlserver.session_id)
    WHERE sqlserver.is_system = 0
);

ALTER EVENT SESSION test_session ON SERVER
DROP EVENT sqlserver.rpc_starting,
DROP EVENT sqlserver.sql_batch_starting
WITH (MAX_DISPATCH_LATENCY = 10 SECONDS);

ALTER EVENT SESSION test_session ON SERVER
ADD TARGET package0.ring_buffer (SET max_events_limit = 1000, max_memory = 4096);

ALTER EVENT SESSION test_session ON SERVER
DROP TARGET package0.ring_buffer;

ALTER EVENT SESSION test_session ON SERVER
WITH (STARTUP_STATE = ON, TRACK_CAUSALITY = OFF);

ALTER EVENT SESSION test_session ON SERVER DROP TARGET package0.event_file
ALTER EVENT SESSION test_session ON SERVER
ADD TARGET package0.event_file (SET filename = N'test_session.xel')
