CREATE DOMAIN us_postal_code AS TEXT
CHECK(
   VALUE ~ '^\d{5}$'
OR VALUE ~ '^\d{5}-\d{4}$'
);

create domain oname as text;

CREATE DOMAIN mystr AS text
CONSTRAINT not_empty CHECK (LENGTH(value) > 0)
CONSTRAINT too_big CHECK (LENGTH(value) <= 50000);
