WITH cd AS (SELECT DISTINCT (customer_city) city, customer_state, customer_region FROM customer_dimension)
SELECT customer_region Region, LISTAGG(city||', '||customer_state USING PARAMETERS separator=' | ')
   WITHIN GROUP (ORDER BY city) CityAndState FROM cd GROUP BY region ORDER BY region;

select
    percentile_cont(0.9) within group (
            order by extract(millisecond from (col1 - col2))
        ) over (
            partition by
                col3,
                col4
        ) as result_column
from tab_name;
