-- Column STORAGE (PostgreSQL 16+) and COMPRESSION (PostgreSQL 14+) in a
-- column definition.
-- https://www.postgresql.org/docs/17/sql-createtable.html
CREATE TABLE storage_test (
    a text STORAGE PLAIN,
    b text STORAGE EXTERNAL,
    c text STORAGE EXTENDED,
    d text STORAGE MAIN,
    e text STORAGE DEFAULT
);

CREATE TABLE compression_test (
    a text COMPRESSION pglz,
    b text COMPRESSION lz4,
    c text COMPRESSION default
);

CREATE TABLE combined_test (
    a text STORAGE MAIN COMPRESSION lz4 COLLATE "C" NOT NULL,
    b jsonb STORAGE EXTERNAL DEFAULT '{}'
);

-- STORAGE and COMPRESSION are non-reserved, so they still work as column names.
CREATE TABLE kw_names (storage text, compression int);

