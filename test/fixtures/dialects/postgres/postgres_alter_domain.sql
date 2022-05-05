ALTER DOMAIN zipcode SET NOT NULL;

ALTER DOMAIN zipcode DROP NOT NULL;

ALTER DOMAIN zipcode ADD CONSTRAINT zipchk CHECK (char_length(VALUE) = 5);

ALTER DOMAIN zipcode DROP CONSTRAINT zipchk;

ALTER DOMAIN zipcode RENAME CONSTRAINT zipchk TO zip_check;

ALTER DOMAIN zipcode SET SCHEMA customers;

alter domain oname add constraint "test" check (length(value) <  512);
