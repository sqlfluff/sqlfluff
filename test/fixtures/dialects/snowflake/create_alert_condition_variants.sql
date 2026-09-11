CREATE ALERT show_alert
    WAREHOUSE = my_warehouse
    SCHEDULE = '60 MINUTE'
    IF (EXISTS (SHOW TABLES))
    THEN CALL my_procedure();

CREATE ALERT call_alert
    WAREHOUSE = my_warehouse
    SCHEDULE = '60 MINUTE'
    IF (EXISTS (CALL my_condition_procedure()))
    THEN CALL my_procedure();
