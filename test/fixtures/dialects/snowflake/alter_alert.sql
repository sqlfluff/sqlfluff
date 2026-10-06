ALTER ALERT my_alert RESUME;

ALTER ALERT IF EXISTS my_alert SUSPEND;

ALTER ALERT my_alert SET
    WAREHOUSE = my_warehouse
    SCHEDULE = '5 MINUTE'
    COMMENT = 'updated comment'
    CONFIG = '{"key": "value"}'
    RUNBOOK = 'https://example.com/runbook'
    SUSPEND_ALERT_AFTER_NUM_FAILURES = 2;

ALTER ALERT my_alert UNSET WAREHOUSE, COMMENT;

ALTER ALERT my_alert UNSET CONFIG, RUNBOOK, SUSPEND_ALERT_AFTER_NUM_FAILURES;

ALTER ALERT my_alert SET TAG cost_center = 'finance';

ALTER ALERT my_alert UNSET TAG cost_center;

ALTER ALERT my_alert MODIFY CONDITION EXISTS (SELECT gauge_value FROM gauge);

ALTER ALERT my_alert MODIFY ACTION INSERT INTO gauge_history VALUES (1);
