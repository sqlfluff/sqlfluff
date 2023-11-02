SELECT suppliers.supplier_id,
       suppliers.supplier_name,
       orders.order_date
FROM   suppliers,
       orders
WHERE  suppliers.supplier_id (+) = orders.supplier_id;

SELECT suppliers.supplier_id,
       suppliers.supplier_name,
       orders.order_date
FROM   suppliers,
       orders
WHERE  suppliers.supplier_id = orders.supplier_id(+);

SELECT suppliers.supplier_id,
       suppliers.supplier_name,
       orders.order_date
FROM   suppliers,
       orders,
       customers
WHERE  suppliers.supplier_id = orders.supplier_id
AND    orders.customer_id = customers.customer_id (+);

SELECT *
FROM   table_a,
       table_b
WHERE  column_a(+) = nvl(column_b, 1);

SELECT *
FROM   table_a,
       table_b
WHERE  nvl(column_b, 1) = column_a(+);
