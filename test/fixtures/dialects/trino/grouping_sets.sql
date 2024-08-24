
WITH tmp_view AS
    (SELECT name, price, store FROM customers, sales
        WHERE customers.c_id=sales.c_id)
SELECT sum(price) AS volume, name, store FROM tmp_view
GROUP BY GROUPING SETS (name,store,());
