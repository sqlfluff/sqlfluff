ALTER TABLE default.people10m CHANGE COLUMN middle_name DROP NOT NULL;

ALTER TABLE default.people10m
    ADD CONSTRAINT date_within_range CHECK (birthDate > '1900-01-01');

ALTER TABLE default.people10m DROP CONSTRAINT date_within_range;

ALTER TABLE default.people10m
    ADD CONSTRAINT valid_ids CHECK (id > 1 and id < 99999999);
