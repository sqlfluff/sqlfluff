CREATE DOMAIN us_postal_code AS TEXT
CHECK(
   VALUE ~ '^\d{5}$'
OR VALUE ~ '^\d{5}-\d{4}$'
);

create domain oname as text;

CREATE DOMAIN mystr AS text
CONSTRAINT not_empty CHECK (LENGTH(value) > 0)
CONSTRAINT too_big CHECK (LENGTH(value) <= 50000);

-- COLLATE and DEFAULT can come after the constraints, as pg_dump writes them.
CREATE DOMAIN public.posint AS integer NOT NULL DEFAULT 1
CONSTRAINT positive CHECK ((value > 0));

CREATE DOMAIN rating AS integer CHECK (value BETWEEN 1 AND 5) DEFAULT 3;

CREATE DOMAIN code AS text NOT NULL COLLATE "C" DEFAULT 'none';
