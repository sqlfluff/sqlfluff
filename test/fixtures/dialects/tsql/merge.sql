merge 
	schema1.table1 dst
using
	schema1.table1 src
on
	src.rn = 1
	and dst.e_date_to is null
	and dst.cc_id = src.cc_id
when matched
	then update
		set
			dst.l_id = src.l_id,
			dst.e_date_to = src.e_date_from
;
