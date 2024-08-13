-- https://docs.vertica.com/latest/en/admin/working-with-native-tables/altering-table-definitions/
ALTER TABLE public.store_orders ADD COLUMN expected_ship_date date;
ALTER TABLE public.store_orders
ADD COLUMN delivery_date date PROJECTIONS (store_orders_p);
ALTER TABLE x ALTER COLUMN b DROP DEFAULT;
ALTER TABLE t DROP COLUMN y;
ALTER TABLE x DROP COLUMN a CASCADE;
ALTER TABLE t DROP COLUMN x RESTRICT;
ALTER TABLE t DROP x CASCADE;
ALTER TABLE public.new_sales ALTER CONSTRAINT C_PRIMARY ENABLED;
ALTER TABLE s1.t1, s1.t2 RENAME TO u1, u2;
ALTER TABLE t1, t2, temp RENAME TO temp, t1, t2;
ALTER TABLE s1.t1 SET SCHEMA s2;
ALTER TABLE t33 OWNER TO Alice;
