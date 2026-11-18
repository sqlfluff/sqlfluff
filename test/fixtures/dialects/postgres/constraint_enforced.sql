-- [ ENFORCED | NOT ENFORCED ] constraint attribute (PostgreSQL 18)
-- https://www.postgresql.org/docs/18/sql-createtable.html
-- https://www.postgresql.org/docs/18/sql-altertable.html

-- Column constraints
CREATE TABLE orders (
    id integer PRIMARY KEY,
    customer_id integer REFERENCES customers (id) NOT ENFORCED,
    quantity integer CHECK (quantity > 0) ENFORCED,
    price numeric CONSTRAINT price_positive CHECK (price > 0) NOT ENFORCED
);

CREATE TABLE line_items (
    order_id integer REFERENCES orders (id)
        DEFERRABLE INITIALLY DEFERRED NOT ENFORCED
);

-- Table constraints
CREATE TABLE shipments (
    id integer,
    order_id integer,
    weight numeric,
    CONSTRAINT shipments_order_fk FOREIGN KEY (order_id)
        REFERENCES orders (id) NOT ENFORCED,
    CONSTRAINT shipments_weight_check CHECK (weight >= 0) ENFORCED
);

ALTER TABLE shipments
    ADD CONSTRAINT shipments_id_check CHECK (id > 0) NOT ENFORCED;

ALTER TABLE shipments
    ADD CONSTRAINT shipments_order_fk2 FOREIGN KEY (order_id)
        REFERENCES orders (id) ON DELETE CASCADE NOT ENFORCED;

-- ALTER CONSTRAINT
ALTER TABLE shipments ALTER CONSTRAINT shipments_order_fk ENFORCED;

ALTER TABLE shipments ALTER CONSTRAINT shipments_order_fk NOT ENFORCED;

ALTER TABLE shipments
    ALTER CONSTRAINT shipments_order_fk DEFERRABLE INITIALLY IMMEDIATE ENFORCED;
