SELECT
    TIMESTAMP_TRUNC(TIMESTAMP_ADD(session_start.eventTimestamp, INTERVAL cast(TIMESTAMP_DIFF(session_end.eventTimestamp, session_start.eventTimestamp, SECOND)/2 AS int64) second), HOUR) AS avgAtHour,
    TIME_ADD(time1, INTERVAL 10 MINUTE) AS after,
    DATE_SUB(time2, INTERVAL 5 YEAR) AS before
FROM dummy;
