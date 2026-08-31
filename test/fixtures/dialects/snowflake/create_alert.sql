CREATE OR REPLACE ALERT my_alert
    WAREHOUSE = my_warehouse
    SCHEDULE = '60 MINUTE'
    IF (EXISTS (SELECT gauge_value FROM gauge WHERE gauge_value > 200))
    THEN INSERT INTO gauge_value_exceeded_history VALUES (CURRENT_TIMESTAMP());
