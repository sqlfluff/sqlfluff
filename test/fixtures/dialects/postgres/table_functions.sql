select * from unnest(array['123', '456']);

select * from unnest(array['123', '456']) as a(val, row_num);

select * from unnest(array['123', '456']) with ordinality;

select * from unnest(array['123', '456']) with ordinality as a(val, row_num);

SELECT * FROM table_1
WHERE utc_activity_start_dttm + make_interval(mins := activity_dur_mnt)
    BETWEEN '2024-01-07T00:00:00'::timestamp AND '2024-01-14T23:59:59.999999'::timestamp;

SELECT ARRAY(SELECT UNNEST(list_field_1) INTERSECT SELECT UNNEST(list_field_2)) FROM table_1;
