CREATE EXTENSION amazing_extension
    with schema schema1
    VERSION '2.0.1.2'
    FROM '1.0';

CREATE EXTENSION IF NOT EXISTS amazing_extension
    with schema schema1
    VERSION '1.2.3a4'
    FROM '1.0';

CREATE EXTENSION amazing_extension
    with schema schema1
    VERSION version_named
    FROM from_named;

DROP EXTENSION amazing_extension;

DROP EXTENSION IF EXISTS amazing_extension;
