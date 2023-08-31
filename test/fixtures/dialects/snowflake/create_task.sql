-- Examples from the documentation

CREATE TASK t1
    SCHEDULE = 'USING CRON 0 9-17 * * SUN America/Los_Angeles'
    TIMESTAMP_INPUT_FORMAT = 'YYYY-MM-DD HH24'
    USER_TASK_MANAGED_INITIAL_WAREHOUSE_SIZE = 'XSMALL'
AS
    INSERT INTO mytable(ts) VALUES(1);

CREATE TASK mytask_hour
    WAREHOUSE = mywh
    SCHEDULE = 'USING CRON 0 9-17 * * SUN America/Los_Angeles'
    TIMESTAMP_INPUT_FORMAT = 'YYYY-MM-DD HH24'
AS
    INSERT INTO mytable(ts) VALUES(1, 2, 3);

-- All possible optional clauses
CREATE OR REPLACE TASK IF NOT EXISTS t1
    SCHEDULE = 'USING CRON 0 9-17 * * SUN America/Los_Angeles'
    ALLOW_OVERLAPPING_EXECUTION = TRUE
    TIMESTAMP_INPUT_FORMAT = 'YYYY-MM-DD HH24'
    USER_TASK_TIMEOUT_MS = 25
    USER_TASK_MANAGED_INITIAL_WAREHOUSE_SIZE = 'XSMALL'
    COPY GRANTS
    COMMENT = 'Hello world'
    AFTER dependency_task
AS
    INSERT INTO mytable(ts) VALUES(1);

-- Only mandatory clauses
CREATE TASK t1
AS
    INSERT INTO mytable(ts) VALUES(1);

-- Real life examples
CREATE OR REPLACE TASK insert_session
    WAREHOUSE = eng_wh
    SCHEDULE = 'USING CRON 45 6 * * * UTC'
AS
    INSERT INTO sch.s_session
    SELECT
        *,
        sum(break) OVER (PARTITION BY serial ORDER BY datetime) AS session_id
    FROM
        (
            SELECT *
            FROM base_table
        )
;


CREATE OR REPLACE TASK update_session
    WAREHOUSE = eng_wh
    AFTER insert_session
AS
    UPDATE sch.s_session
    SET lag_datetime = v.lag_datetime, row_number = v.row_number
    FROM
        (
            SELECT
                *,
                (
                    sum(break) OVER (PARTITION BY serial ORDER BY datetime)
                ) AS session_id
            FROM
                (
                    SELECT *
                    FROM derived_table
                )
            ORDER BY serial, datetime
        ) AS v
    WHERE sch.s_session.event_id = v.event_id
;

CREATE OR REPLACE TASK sch.truncate_session
    WAREHOUSE = eng_wh
    AFTER sch.update_session
AS
    CALL sch.session_agg_insert();

CREATE OR REPLACE TASK insert__agg
    WAREHOUSE = eng_wh
    SCHEDULE = 'USING CRON 15 7 2 * * UTC'
AS
    CALL auto_device_insert();

CREATE OR REPLACE TASK SCH.MY_TASK
	WAREHOUSE = MY_WH
	SCHEDULE = 'USING CRON 15 7 2 * * UTC'
	USER_TASK_TIMEOUT_MS = 10800000
WHEN
    SYSTEM$STREAM_HAS_DATA('SCH.MY_STREAM')
    AND 1=1
AS
    CALL SCH.MY_SPROC();
