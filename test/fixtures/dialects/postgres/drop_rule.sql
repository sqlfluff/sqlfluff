DROP RULE keep_orders ON orders;

DROP RULE IF EXISTS "Archive Order" ON sales.orders;

DROP RULE notify_orders ON orders CASCADE;

DROP RULE IF EXISTS log_order_insert ON orders RESTRICT;
