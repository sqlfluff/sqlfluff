CREATE EVENT myevent
    ON SCHEDULE AT CURRENT_TIMESTAMP + INTERVAL 1 HOUR
    DO
      UPDATE myschema.mytable SET mycol = mycol + 1;

CREATE EVENT e_totals
    ON SCHEDULE AT '2006-02-10 23:59:00'
    DO INSERT INTO test.totals VALUES (NOW());

CREATE EVENT e_hourly
    ON SCHEDULE
      EVERY 1 HOUR
    COMMENT 'Clears out sessions table each hour.'
    DO
      DELETE FROM site_activity.sessions;

CREATE EVENT e_daily
    ON SCHEDULE
      EVERY 1 DAY
    COMMENT 'Saves total number of sessions then clears the table each day'
    DO
      BEGIN
        INSERT INTO site_activity.totals (time, total)
          SELECT CURRENT_TIMESTAMP, COUNT(*)
            FROM site_activity.sessions;
        DELETE FROM site_activity.sessions;
      END;

CREATE EVENT e_call_myproc
    ON SCHEDULE
      AT CURRENT_TIMESTAMP + INTERVAL 1 DAY
    DO CALL myproc(5, 27);

CREATE EVENT e
  ON SCHEDULE EVERY interval SECOND
  STARTS CURRENT_TIMESTAMP + INTERVAL 10 SECOND
  ENDS CURRENT_TIMESTAMP + INTERVAL 2 MINUTE
  ON COMPLETION PRESERVE
  DO
    INSERT INTO d.t1 VALUES ROW(NULL, NOW(), FLOOR(RAND()*100));
