UPDATE staff SET salary=salary*1.1 WHERE name='SMITH';
----
UPDATE staff AS U SET U.salary=U.salary/1.95583, U.currency='EUR'
WHERE U.currency='DM';
----
UPDATE staff AS U
SET U.salary=V.salary, U.currency=V.currency
FROM staff AS U, staff_updates AS V
WHERE U.name=V.name;
----
UPDATE order_pos
SET stocks=stocks*10
PREFERRING HIGH (order_date) PARTITION BY (shop_id, order_id);
