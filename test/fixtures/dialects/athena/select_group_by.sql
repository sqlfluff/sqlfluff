select
    as_of_date,
    channel,
    sum(total_count) as cnt
from agg.aggregate_total
group by cube (as_of_date, channel);

select
    as_of_date,
    channel,
    sum(total_count) as cnt
from agg.aggregate_total
group by rollup (as_of_date, channel);

select
    as_of_date,
    channel,
    sum(total_count) as cnt
from agg.aggregate_total
group by grouping sets (as_of_date, channel);

-- complex sets
select
    as_of_date,
    channel,
    sum(total_count) as cnt
from agg.aggregate_total
group by grouping sets ((as_of_date, channel), (as_of_date), ());
