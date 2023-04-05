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
