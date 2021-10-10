select
	t.column1
from
	sch.table1 as t
where
	t.b_year in (year(getdate()) , year(getdate()) - 1);
