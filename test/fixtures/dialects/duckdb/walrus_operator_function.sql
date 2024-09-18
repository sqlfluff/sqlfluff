create view v as
select
    t.id,
    struct_pack(
        val := t.val
    ) as s
from
    t;


select struct_insert({ 'a': 1 }, b := 2);
