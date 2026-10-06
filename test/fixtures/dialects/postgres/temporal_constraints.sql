CREATE TABLE room_reservation (
    room_id int,
    valid_at tstzrange,
    PRIMARY KEY (room_id, valid_at WITHOUT OVERLAPS)
);

CREATE TABLE room_booking (
    room_id int,
    booking_id int,
    valid_at daterange,
    CONSTRAINT room_booking_pk PRIMARY KEY (room_id, booking_id, valid_at WITHOUT OVERLAPS),
    CONSTRAINT room_booking_uq UNIQUE (booking_id, valid_at WITHOUT OVERLAPS)
);

CREATE TABLE room_hold (
    room_id int,
    valid_at tsrange,
    UNIQUE NULLS NOT DISTINCT (room_id, valid_at WITHOUT OVERLAPS) INCLUDE (room_id)
);

CREATE TABLE availability (
    valid_at daterange,
    PRIMARY KEY (valid_at WITHOUT OVERLAPS)
);

ALTER TABLE room_reservation
ADD CONSTRAINT room_reservation_uq UNIQUE (room_id, valid_at WITHOUT OVERLAPS);

ALTER TABLE room_reservation ADD PRIMARY KEY (room_id, valid_at WITHOUT OVERLAPS);
