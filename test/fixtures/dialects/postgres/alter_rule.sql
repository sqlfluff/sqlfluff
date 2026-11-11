ALTER RULE protect_orders ON orders RENAME TO keep_orders;

ALTER RULE archive_order ON sales.orders RENAME TO "Archive Order";
