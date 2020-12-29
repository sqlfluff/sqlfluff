-- Some more complicated Postgres function creations.

CREATE FUNCTION add(integer, integer) RETURNS integer
    AS 'select $1 + $2;'
    LANGUAGE SQL;

CREATE OR REPLACE FUNCTION increment(i integer) RETURNS integer AS '
    BEGIN
        RETURN i + 1;
    END;
' LANGUAGE plpgsql;
