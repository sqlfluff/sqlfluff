-- Snowflake style WITHIN GROUP window functions
with favourite_fruits as (

    select column1 as name, column2 as colour from
    (values
        ('apple', 'green'),
        ('unripe banana', 'green'),
        ('kiwi', 'green'),
        ('blueberry', 'blue'),
        ('strawberry', 'red'),
        ('grape', 'red')
    )

)

select
    colour,
    listagg(name, ', ')
        within group (order by name) as fruits
from favourite_fruits
group by colour;

SELECT ARRAY_AGG(o_orderkey) WITHIN GROUP (ORDER BY o_orderkey ASC)
FROM orders;

select array_agg(o_orderkey) within group (order by o_orderkey asc)
  from orders
  where o_totalprice > 450000;

select array_agg(distinct o_orderstatus) within group (order by o_orderstatus asc)
  from orders
  where o_totalprice > 450000
  order by o_orderstatus asc;

select
    o_orderstatus,
    array_agg(o_clerk) within group (order by o_totalprice desc)
  from orders
  where o_totalprice > 450000
  group by o_orderstatus
  order by o_orderstatus desc;

select listagg(o_orderkey, ' ')
    from orders where o_totalprice > 450000;

select listagg(distinct o_orderstatus, '|')
    from orders where o_totalprice > 450000;

select o_orderstatus, listagg(o_clerk, ', ') within group (order by o_totalprice desc)
    from orders where o_totalprice > 450000 group by o_orderstatus;

select listagg(spanish_phrase, '|')
        within group (order by collate(spanish_phrase, 'sp'))
    from collation_demo
    group by english_phrase;

select listagg(spanish_phrase, '|')
        within group (order by collate(spanish_phrase, 'utf8'))
    from collation_demo
    group by english_phrase;
