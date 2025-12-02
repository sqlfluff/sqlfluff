select
    dataset_id,
    (percentile_cont(0.20) within group (
        order by tract_percent_below_poverty asc
    ) over(partition by dataset_id)) as percentile_20,
    percentile_cont(0.40)
    within group (order by tract_percent_below_poverty asc)
    over(partition by dataset_id) as percentile_40
from dataset_with_census
