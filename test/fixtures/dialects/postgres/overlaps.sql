-- with DATE
select
    start_date,
    end_date
from test_overlaps
where (start_date, end_date) overlaps (DATE '2023-02-15', DATE '2023-03-15');

select
    start_date,
    end_date
from test_overlaps
where (start_date, end_date) overlaps ('2023-02-15', '2023-03-15');

SELECT
    t1.start_date,
    t1.end_date
FROM test_overlaps1 AS t1
LEFT JOIN test_overlaps2 AS t2
WHERE (t1.start_date, t1.end_date) OVERLAPS (t2.start_date, t2.end_date);

SELECT
    start_date,
    end_date
FROM test_overlaps
WHERE (start_date, end_date) OVERLAPS ('2023-12-30T00:00:00'::TIMESTAMP, '2024-01-14T13:01:39.884877'::TIMESTAMP);

SELECT
    start_date,
    end_date
FROM test_overlaps
WHERE ('2023-12-30T00:00:00'::TIMESTAMP, '2024-01-14T13:01:39.884877'::TIMESTAMP) OVERLAPS (start_date, end_date);

SELECT
    start_date,
    end_date
FROM test_overlaps
WHERE (start_date, end_date) OVERLAPS (DATE '2023-12-30', INTERVAL '2 HOURS');

SELECT
    start_date,
    end_date
FROM test_overlaps
WHERE (DATE '2023-12-30', DATE '2024-01-14') OVERLAPS (start_date, end_date);

SELECT
    start_date_1,
    start_date_2,
    end_date
FROM test_overlaps
WHERE (DATE '2023-12-30', DATE '2024-01-14') OVERLAPS (GREATEST(start_date_1, start_date_2), end_date);
