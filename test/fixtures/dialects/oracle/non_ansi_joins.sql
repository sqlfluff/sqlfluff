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
