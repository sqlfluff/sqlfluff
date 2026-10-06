CREATE ALERT IF NOT EXISTS my_alert
    WITH TAG (cost_center = 'finance')
    SCHEDULE = 'USING CRON 0 0 * * * UTC'
    WAREHOUSE = my_warehouse
    COMMENT = 'alerts when the gauge is too high'
    CONFIG = '{"key": "value"}'
    RUNBOOK = 'https://example.com/runbook'
    SUSPEND_ALERT_AFTER_NUM_FAILURES = 3
    IF (EXISTS (SELECT gauge_value FROM gauge WHERE gauge_value > 200))
    THEN CALL my_procedure();
