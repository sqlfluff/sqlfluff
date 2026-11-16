-- Temporal PRIMARY KEY / UNIQUE constraints (PostgreSQL 18)
-- https://www.postgresql.org/docs/18/sql-createtable.html
CREATE TABLE reservations (
    room_id int,
    during tstzrange,
    PRIMARY KEY (room_id, during WITHOUT OVERLAPS)
);

CREATE TABLE prices (
    product_id int,
    valid_at daterange,
    price numeric,
    CONSTRAINT prices_unique UNIQUE (product_id, valid_at WITHOUT OVERLAPS)
);

CREATE TABLE t (
    a int,
    b int,
    valid_at daterange,
    UNIQUE NULLS NOT DISTINCT (a, b, valid_at WITHOUT OVERLAPS)
        DEFERRABLE INITIALLY DEFERRED
);

ALTER TABLE reservations
    ADD CONSTRAINT reservations_pk PRIMARY KEY (room_id, during WITHOUT OVERLAPS);

ALTER TABLE prices
    ADD UNIQUE (product_id, valid_at WITHOUT OVERLAPS);

CREATE TABLE bookings (
    room_id int,
    during tstzrange,
    x int,
    PRIMARY KEY (room_id, during WITHOUT OVERLAPS) INCLUDE (x)
);

ALTER TABLE bookings
    ADD CONSTRAINT bookings_uq UNIQUE (room_id, during WITHOUT OVERLAPS)
        INCLUDE (x) WITH (fillfactor = 70) USING INDEX TABLESPACE pg_default;
