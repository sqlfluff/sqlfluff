-- Postgres should work with standard joins
select tbl1.id from tbl1 join tbl2 on tbl1.id = tbl2.id;

-- ... but also with lateral joins
select tbl1.id from tbl1 join lateral tbl2 on tbl1.id = tbl2.id;

-- ... and mixed ones as well!
select tbl1.id from tbl1
full outer join lateral tbl2 on tbl1.id = tbl2.id
cross join tbl3 on tbl1.id = tbl3.id
left join lateral tbl4 on tbl1.id = tbl4.id;
