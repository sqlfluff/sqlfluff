-- Some more complicated Postgres function creations.

CREATE FUNCTION add(integer, integer) RETURNS integer
    AS 'select $1 + $2;'
    LANGUAGE SQL;

CREATE OR REPLACE FUNCTION increment(i integer) RETURNS integer AS '
    BEGIN
        RETURN i + 1;
    END;
' LANGUAGE plpgsql VOLATILE;

CREATE OR REPLACE FUNCTION increment(i integer) RETURNS integer AS '
    BEGIN
        RETURN i + 1;
    END;
' LANGUAGE plpgsql WINDOW IMMUTABLE STABLE LEAKPROOF RETURNS NULL ON NULL INPUT EXTERNAL SECURITY DEFINER
ROWS 5 SET test_param = 3;

CREATE OR REPLACE FUNCTION increment(i integer) RETURNS integer AS 'C:\\my_file.c', 'symlink_c'
LANGUAGE plpgsql WINDOW IMMUTABLE STABLE NOT LEAKPROOF CALLED ON NULL INPUT EXTERNAL SECURITY DEFINER COST 123
ROWS 5 SET test_param = 3 WITH (isStrict);

CREATE OR REPLACE FUNCTION increment(i integer) RETURNS integer PARALLEL UNSAFE AS $$
    BEGIN
        RETURN i + 1;
    END;
$$ LANGUAGE plpgsql SUPPORT my_function;