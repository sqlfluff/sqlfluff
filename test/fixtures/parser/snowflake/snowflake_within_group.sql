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
group by colour
