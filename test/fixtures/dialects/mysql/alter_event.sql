ALTER EVENT no_such_event
    ON SCHEDULE
        EVERY '2:3' DAY_HOUR;

ALTER EVENT myevent
    ON SCHEDULE
      EVERY 12 HOUR
    STARTS CURRENT_TIMESTAMP + INTERVAL 4 HOUR;

ALTER EVENT myevent
    ON SCHEDULE
      AT CURRENT_TIMESTAMP + INTERVAL 1 DAY
    DO
      TRUNCATE TABLE myschema.mytable;

ALTER EVENT myevent
    DISABLE;

ALTER EVENT myevent
    RENAME TO yourevent;

ALTER EVENT olddb.myevent
    RENAME TO newdb.myevent;
