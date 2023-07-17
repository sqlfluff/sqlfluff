select
    state,
    city,
    sum(retail_price * quantity) as gross_revenue
from sales
group by all;
