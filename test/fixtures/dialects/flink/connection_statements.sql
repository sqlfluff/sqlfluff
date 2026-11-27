CREATE CONNECTION IF NOT EXISTS my_conn
COMMENT 'external http endpoint'
WITH (
    'type' = 'http',
    'endpoint' = 'https://api.example.com'
);

CREATE TEMPORARY SYSTEM CONNECTION IF NOT EXISTS sys_conn
WITH (
    'type' = 'openai'
);

ALTER CONNECTION IF EXISTS my_conn SET ('timeout' = '30s');

ALTER CONNECTION my_conn RESET ('timeout');

ALTER CONNECTION my_conn RENAME TO my_conn_v2;

DROP CONNECTION IF EXISTS my_conn_v2;

DROP TEMPORARY SYSTEM CONNECTION IF EXISTS sys_conn;
