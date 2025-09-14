-- Create a view filtering the `orders` table which will adjust to schema changes in `orders`.
CREATE OR REPLACE VIEW open_orders WITH SCHEMA EVOLUTION
    AS SELECT * FROM orders WHERE status = 'open';
