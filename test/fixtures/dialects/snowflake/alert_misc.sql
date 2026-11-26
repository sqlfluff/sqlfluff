EXECUTE ALERT my_alert;

EXECUTE ALERT my_db.my_schema.my_alert;

DESCRIBE ALERT my_alert;

DESC ALERT my_db.my_schema.my_alert;

SHOW ALERTS;

SHOW TERSE ALERTS;

SHOW ALERTS LIKE 'my%' IN SCHEMA my_db.my_schema;

SHOW ALERTS IN ACCOUNT STARTS WITH 'my' LIMIT 10 FROM 'my_alert';
