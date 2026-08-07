-- Application-time periods.
-- https://mariadb.com/kb/en/application-time-periods/

-- A named period over two date columns.
CREATE TABLE t1 (
   name VARCHAR(50),
   date_1 DATE,
   date_2 DATE,
   PERIOD FOR date_period(date_1, date_2)
);

-- WITHOUT OVERLAPS in a UNIQUE constraint.
CREATE TABLE rooms (
   room_number INT,
   guest_name VARCHAR(255),
   checkin DATE,
   checkout DATE,
   PERIOD FOR p(checkin, checkout),
   UNIQUE (room_number, p WITHOUT OVERLAPS)
);

-- WITHOUT OVERLAPS in a PRIMARY KEY constraint.
CREATE TABLE bookings (
   room_number INT,
   checkin DATE,
   checkout DATE,
   PERIOD FOR p(checkin, checkout),
   PRIMARY KEY (room_number, p WITHOUT OVERLAPS)
);
