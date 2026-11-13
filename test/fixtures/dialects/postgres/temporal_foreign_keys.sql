-- PostgreSQL 18 temporal foreign keys.
CREATE TABLE bookings (
    room_id integer,
    valid_at tstzrange,
    FOREIGN KEY (room_id, PERIOD valid_at)
        REFERENCES rooms (room_id, PERIOD valid_at)
);

CREATE TABLE appointments (
    site_id integer,
    doctor_id integer,
    valid_at daterange,
    CONSTRAINT appointments_period_fk FOREIGN KEY (site_id, doctor_id, PERIOD valid_at)
        REFERENCES availability (site_id, doctor_id, PERIOD valid_at)
);

ALTER TABLE bookings ADD CONSTRAINT bookings_room_fk
    FOREIGN KEY (room_id, PERIOD valid_at)
    REFERENCES public.rooms (room_id, PERIOD valid_at)
    ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;

-- The referenced columns may be omitted, using the parent's primary key.
ALTER TABLE bookings ADD FOREIGN KEY (room_id, PERIOD valid_at) REFERENCES rooms;

-- PERIOD remains usable as an ordinary, unquoted column name.
CREATE TABLE period_references (
    period integer REFERENCES periods (period),
    valid_at daterange,
    FOREIGN KEY (period, PERIOD valid_at)
        REFERENCES periods (period, PERIOD valid_at)
);

ALTER TABLE bookings ADD FOREIGN KEY (room_id, PERIOD "valid time")
    REFERENCES "Room Availability" (room_id, PERIOD "valid time");
