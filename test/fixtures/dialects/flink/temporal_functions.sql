SELECT
    FLOOR(event_time TO SECOND) AS bucket_sec,
    FLOOR(event_time + INTERVAL '1' MINUTE TO SECOND) AS shifted_sec,
    FLOOR(PROCTIME() TO MINUTE) AS proc_min,
    CEIL(event_time TO HOUR) AS ceil_hour,
    CEILING(event_time TO DAY) AS ceil_day,
    FLOOR(3.14) AS num_floor,
    CEIL(3.14) AS num_ceil,
    TIMESTAMPADD(DAY, 1, event_time) AS next_day,
    TIMESTAMPADD(SECOND, -30, event_time) AS prev_30s,
    TIMESTAMPADD(SQL_TSI_HOUR, 2, event_time) AS plus_2h
FROM events
GROUP BY FLOOR(event_time TO SECOND);
