-- Some more complicated Postgres function creations.

CREATE FUNCTION add(integer, integer) RETURNS integer
    AS 'select $1 + $2;'
    LANGUAGE SQL;

-- Quoted language options are deprecated but still supported
CREATE FUNCTION add(integer, integer) RETURNS integer
    AS 'select $1 + $2;'
    LANGUAGE 'sql';

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

CREATE FUNCTION add(integer, integer) RETURNS integer
    AS 'select $1 + $2;'
    LANGUAGE SQL
    IMMUTABLE
    RETURNS NULL ON NULL INPUT;

CREATE OR REPLACE FUNCTION increment(i integer) RETURNS integer AS $$
        BEGIN
                RETURN i + 1;
        END;
$$ LANGUAGE plpgsql;


CREATE FUNCTION dup(in int, out f1 int, out f2 text)
    AS $$ SELECT $1, CAST($1 AS text) || ' is text' $$
    LANGUAGE SQL;

SELECT * FROM dup(42);


CREATE TYPE dup_result AS (f1 int, f2 text);

CREATE FUNCTION dup(int) RETURNS dup_result
    AS $$ SELECT $1, CAST($1 AS text) || ' is text' $$
    LANGUAGE SQL;

SELECT * FROM dup(42);

CREATE FUNCTION dup(int) RETURNS TABLE(f1 int, f2 text)
    AS $$ SELECT $1, CAST($1 AS text) || ' is text' $$
    LANGUAGE SQL;

CREATE FUNCTION dup(int) RETURNS TABLE("f1" int, "f2" text)
    AS $$ SELECT $1, CAST($1 AS text) || ' is text' $$
    LANGUAGE SQL;


SELECT * FROM dup(42);

CREATE FUNCTION check_password(uname TEXT, pass TEXT)
RETURNS BOOLEAN AS $$
DECLARE passed BOOLEAN;
BEGIN
        SELECT  (pwd = $2) INTO passed
        FROM    pwds
        WHERE   username = $1;

        RETURN passed;
END;
$$  LANGUAGE plpgsql
    SECURITY DEFINER
    SET search_path = admin, pg_temp;


BEGIN;
CREATE FUNCTION check_password(uname TEXT, pass TEXT)
RETURNS BOOLEAN AS $$
DECLARE passed BOOLEAN;
BEGIN
        SELECT  (pwd = $2) INTO passed
        FROM    pwds
        WHERE   username = $1;

        RETURN passed;
END;
$$  LANGUAGE plpgsql
    SECURITY DEFINER;
REVOKE ALL ON FUNCTION check_password(uname TEXT, pass TEXT) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION check_password(uname TEXT, pass TEXT) TO admins;
COMMIT;

CREATE OR REPLACE FUNCTION public.setof_test()
RETURNS SETOF text
LANGUAGE sql
STABLE STRICT
AS $function$
select unnest(array['hi', 'test'])
$function$
;

CREATE OR REPLACE FUNCTION public.foo(_a TEXT, _$b INT)
RETURNS FLOAT AS
$$
  RETURN 0.0
$$ LANGUAGE plpgsql STABLE PARALLEL SAFE;

CREATE FUNCTION _add(integer, integer) RETURNS integer
    AS 'select $1 + $2;'
    LANGUAGE SQL;

CREATE FUNCTION _$add(integer, integer) RETURNS integer
    AS 'select $1 + $2;'
    LANGUAGE SQL;

create function test2(
  x date = current_date
)
returns date
as $$
  begin
    return x;
  end;
$$;

create function test3(
  x date default current_date
)
returns date
as $$
  begin
    return x;
  end;
$$;

CREATE OR REPLACE FUNCTION data_wrapper()
RETURNS SETOF data
STABLE PARALLEL SAFE LEAKPROOF
BEGIN ATOMIC
  SELECT *
  FROM data;
END;

create or replace function tz_date(timestamp with time zone, text) returns date
    language sql
    immutable strict
    return ($1 at time zone $2)::date;

CREATE FUNCTION storage.insert_dimension
(in_ordinality int, in_fieldname varchar, in_default_val varchar,
 in_valid_from timestamp, in_valid_until timestamp)
returns storage.dimensions language sql
BEGIN ATOMIC
    UPDATE storage.dimensions
       SET ordinality = ordinality + 1
     WHERE ordinality >= in_ordinality;

    INSERT INTO storage.dimensions
                (ordinality, fieldname, default_val, valid_from, valid_until)
         VALUES (in_ordinality, in_fieldname,
                coalesce(in_default_val, 'notexist'),
                coalesce(in_valid_from, '-infinity'),
                coalesce(in_valid_until, 'infinity'))
    RETURNING *;
END;

CREATE OR REPLACE FUNCTION time_bucket(
    _time timestamp without time zone,
    _from timestamp without time zone,
    _to timestamp without time zone,
    _buckets integer DEFAULT 200,
    _offset integer DEFAULT 0
)
RETURNS timestamp without time zone
IMMUTABLE PARALLEL SAFE
BEGIN ATOMIC
SELECT date_bin(((_to - _from) / greatest((_buckets - 1), 1)), _time, _from) + ((_to - _from) / greatest((_buckets - 1), 1)) * (_offset + 1);
END;

CREATE OR REPLACE FUNCTION time_bucket_limited(_time timestamp, _from timestamp, _to timestamp, _buckets int = 200)
    RETURNS timestamp
    IMMUTABLE PARALLEL SAFE
BEGIN ATOMIC
    RETURN CASE WHEN _time <= _from THEN _from
      WHEN _time >= _to THEN _to
      ELSE DATE_BIN((_to - _from) / GREATEST(_buckets - 1, 1), _time, _from) + ((_to - _from) / GREATEST(_buckets - 1, 1))
    end;
END;

CREATE OR REPLACE FUNCTION time_series(
    _from timestamp without time zone,
    _to timestamp without time zone,
    _buckets integer DEFAULT 200
)
RETURNS TABLE ("time" timestamp without time zone)
IMMUTABLE PARALLEL SAFE
BEGIN ATOMIC
-- ATTENTION: use integer to generate series, since with timestamps there are rounding issues
SELECT time_bucket(_from, _from, _to, _buckets, g.ofs - 1)
FROM generate_series(0, greatest((_buckets - 1), 1)) AS g (ofs);
END;
