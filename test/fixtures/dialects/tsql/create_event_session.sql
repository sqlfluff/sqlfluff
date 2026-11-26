-- https://learn.microsoft.com/en-us/sql/t-sql/statements/create-event-session-transact-sql
CREATE EVENT SESSION test_session ON SERVER
ADD EVENT sqlserver.rpc_starting;

CREATE EVENT SESSION batch_trace ON SERVER
ADD EVENT sqlserver.rpc_completed,
ADD EVENT sqlserver.sql_batch_completed,
ADD EVENT sqlserver.attention
ADD TARGET package0.event_file (
    SET filename = N'D:\traces\batch_trace.xel',
        max_file_size = 100,
        max_rollover_files = 5
)
WITH (MAX_MEMORY = 8 MB);

CREATE EVENT SESSION [long_queries] ON SERVER
ADD EVENT [sqlserver].[sql_statement_completed] (
    SET collect_statement = (1)
    ACTION ([sqlserver].[sql_text], [sqlserver].[session_id])
    WHERE (
        [sqlserver].[database_id] = (5)
        AND [package0].[greater_than_uint64]([duration], (1000000))
    )
)
ADD TARGET [package0].[ring_buffer] (SET max_memory = (1024));

CREATE EVENT SESSION app_errors ON DATABASE
ADD EVENT sqlserver.error_reported (
    ACTION (sqlserver.client_app_name, sqlserver.username)
    WHERE severity >= 16
        AND NOT (sqlserver.client_app_name = N'Monitor' OR sqlserver.username = 'svc')
),
ADD EVENT sqlserver.sql_batch_completed (
    WHERE sqlserver.like_i_sql_unicode_string(batch_text, N'%DELETE%')
        OR batch_text NOT LIKE N'%SELECT%'
),
ADD EVENT [CE79811F-1A80-40E1-8F5D-7445A3F375E7].sqlserver.rpc_completed;

CREATE EVENT SESSION deadlocks ON SERVER
ADD EVENT sqlserver.lock_deadlock
ADD TARGET package0.event_counter,
ADD TARGET package0.histogram (
    SET filtering_event_name = N'sqlserver.lock_deadlock',
        source = N'database_id',
        source_type = 0
)
WITH (
    MAX_MEMORY = 4096 KB,
    EVENT_RETENTION_MODE = ALLOW_SINGLE_EVENT_LOSS,
    MAX_DISPATCH_LATENCY = 30 SECONDS,
    MAX_EVENT_SIZE = 0 KB,
    MEMORY_PARTITION_MODE = NONE,
    TRACK_CAUSALITY = OFF,
    STARTUP_STATE = ON
);

CREATE EVENT SESSION waits ON SERVER
ADD EVENT sqlos.wait_info
WITH (
    EVENT_RETENTION_MODE = ALLOW_MULTIPLE_EVENT_LOSS,
    MAX_DISPATCH_LATENCY = INFINITE,
    MEMORY_PARTITION_MODE = PER_NODE,
    TRACK_CAUSALITY = ON
);

CREATE EVENT SESSION waits ON SERVER
ADD EVENT sqlos.wait_info
WITH (
    MAX_MEMORY=4096KB, MAX_EVENT_SIZE=4MB, EVENT_RETENTION_MODE=NO_EVENT_LOSS,
    MAX_DISPATCH_LATENCY=5SECONDS, MEMORY_PARTITION_MODE=PER_CPU, STARTUP_STATE=OFF
);
