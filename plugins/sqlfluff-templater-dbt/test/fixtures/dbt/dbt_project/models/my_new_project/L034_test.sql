-- L034 should ignore this as one of the select targets uses a macro

select
    {{ dbt_utils.surrogate_key(['spots', 'moos']) }} as spot_moo_id,
    date(birth_date) as birth_date,
    name
from cows
