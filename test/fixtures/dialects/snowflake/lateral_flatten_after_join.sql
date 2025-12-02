select
    value as p_id,
    name,
    iff(
        rank() over (
            partition by id
            order by t_id desc
        ) = 1
        , true, false
    ) as most_recent

from a
inner join b
    on (b.c_id = a.c_id)
, lateral flatten (input => b.cool_ids)
