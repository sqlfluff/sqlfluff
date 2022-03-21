-- simple
select array[a, b, c] as arr
from sch.tbl;

-- bit harder
select t.a
from unnest(array[1, 3, 6, 12]) as t(f);

-- complex
select map_from_entries(array[
    row('pending.freebet', pending_fb),
    row('bonus.balance', bonus)
])
from sch.tbl;

-- string consts
select array['a', 'b', 'c'] as arr
from sch.tbl;

-- null
select array['a', null] as arr
from sch.tbl;

-- empty array
select array[] as arr
from sch.tbl;
