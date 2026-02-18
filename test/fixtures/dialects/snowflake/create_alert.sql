-- Basic CREATE ALERT with warehouse and schedule
CREATE ALERT my_alert
  WAREHOUSE = my_warehouse
  SCHEDULE = '1 MINUTE'
  IF(EXISTS(SELECT 1 FROM my_table WHERE status = 'ERROR'))
  THEN INSERT INTO alert_log VALUES (CURRENT_TIMESTAMP());

-- CREATE OR REPLACE ALERT with CRON schedule
CREATE OR REPLACE ALERT IF NOT EXISTS my_cron_alert
  WAREHOUSE = my_warehouse
  SCHEDULE = 'USING CRON 0 9 * * * America/Los_Angeles'
  COMMENT = 'Daily check alert'
  IF(EXISTS(SELECT COUNT(*) FROM events WHERE event_date = CURRENT_DATE()))
  THEN INSERT INTO notifications VALUES ('alert triggered');

-- Serverless alert (no warehouse)
CREATE ALERT serverless_alert
  SCHEDULE = '5 MINUTE'
  IF(EXISTS(SELECT 1 FROM errors))
  THEN DELETE FROM errors WHERE resolved = TRUE;
