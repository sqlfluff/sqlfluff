-- Adding and removing application-time periods with ALTER TABLE.
-- https://mariadb.com/kb/en/application-time-periods/

ALTER TABLE rooms ADD PERIOD FOR p(checkin, checkout);

ALTER TABLE rooms ADD PERIOD IF NOT EXISTS FOR p(checkin, checkout);

ALTER TABLE rooms DROP PERIOD FOR p;

ALTER TABLE rooms DROP PERIOD IF EXISTS FOR p;
