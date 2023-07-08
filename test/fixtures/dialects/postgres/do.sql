-- postgres_do.sql
/* Postgres DO statements (https://www.postgresql.org/docs/14/sql-do.html). */

-- From Issue #2018 (https://github.com/sqlfluff/sqlfluff/issues/2018)
DO $$DECLARE r record;
BEGIN
    FOR r IN SELECT table_schema, table_name FROM information_schema.tables
             WHERE table_type = 'VIEW' AND table_schema = 'public'
    LOOP
        EXECUTE 'GRANT ALL ON ' || quote_ident(r.table_schema) || '.' || quote_ident(r.table_name) || ' TO webuser';
    END LOOP;
END$$;

-- can put language before code block
DO LANGUAGE plpgsql $$
DECLARE r record;
BEGIN
    FOR r IN SELECT table_schema, table_name FROM information_schema.tables
             WHERE table_type = 'VIEW' AND table_schema = 'public'
    LOOP
        EXECUTE 'GRANT ALL ON ' || quote_ident(r.table_schema) || '.' || quote_ident(r.table_name) || ' TO webuser';
    END LOOP;
END$$;

-- can put language after code block
DO $$
DECLARE r record;
BEGIN
    FOR r IN SELECT table_schema, table_name FROM information_schema.tables
             WHERE table_type = 'VIEW' AND table_schema = 'public'
    LOOP
        EXECUTE 'GRANT ALL ON ' || quote_ident(r.table_schema) || '.' || quote_ident(r.table_name) || ' TO webuser';
    END LOOP;
END$$
LANGUAGE plpgsql;

-- code block can be any string literal
DO E'
DECLARE r record;
BEGIN
    FOR r IN SELECT table_schema, table_name FROM information_schema.tables
             WHERE table_type = \'VIEW\' AND table_schema = \'public\'
    LOOP
        EXECUTE \'GRANT ALL ON \' || quote_ident(r.table_schema) || \'.\' || quote_ident(r.table_name) || \' TO webuser\';
    END LOOP;
END';

DO 'DECLARE r record;';

DO U&'\0441\043B\043E\043D';

DO 'SELECT foo'
'bar';
