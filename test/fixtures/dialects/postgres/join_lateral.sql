-- Postgres should work with standard joins
select tbl1.id from tbl1 join tbl2 on tbl1.id = tbl2.id;

-- ... but also with lateral joins
select tbl1.id from tbl1 join lateral (SELECT * FROM tbl2) AS foo ON tbl1.id = foo.id;

-- ... and mixed ones as well!
select tbl1.id from tbl1
full outer join lateral (SELECT * FROM tbl2) AS tbl2 on tbl1.id = tbl2.id
cross join tbl3
left join lateral (SELECT * FROM tbl4) AS tbl4 on tbl1.id = tbl4.id;

-- lateral with comma cross join syntax
SELECT X.NUM, D.id FROM tbl1 AS D, LATERAL (values (0), (1)) AS X (NUM);

-- lateral with function
SELECT m.name AS mname, pname
FROM manufacturers m, LATERAL get_product_names(m.id) pname;

SELECT m.name AS mname, pname
FROM manufacturers m LEFT JOIN LATERAL get_product_names(m.id) pname ON true;

SELECT X.NUM
FROM LATERAL (values (0), (1)) AS X (NUM);
