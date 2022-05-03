CREATE EXTENSION amazing_extension
    with schema schema1
    VERSION 2.0
    FROM 1.0;

CREATE EXTENSION IF NOT EXISTS amazing_extension
    with schema schema1
    VERSION 2.0
    FROM 1.0;


DROP EXTENSION amazing_extension;

DROP EXTENSION IF EXISTS amazing_extension;
