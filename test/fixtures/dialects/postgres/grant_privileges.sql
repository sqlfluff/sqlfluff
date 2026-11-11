GRANT USAGE ON SCHEMA api TO web_anon;
GRANT EXECUTE ON FUNCTION api.test TO web_anon;
GRANT web_anon TO my_user;
GRANT CONNECT, CREATE, TEMP, TEMPORARY ON DATABASE my_db TO app;
GRANT TRIGGER ON ALL TABLES IN SCHEMA my_schema TO app;
GRANT USAGE ON DOMAIN my_domain TO my_user;
GRANT USAGE ON FOREIGN DATA WRAPPER my_fdw TO my_user;
GRANT USAGE ON FOREIGN SERVER fs TO my_user;
GRANT EXECUTE ON PROCEDURE fn TO my_user;
GRANT EXECUTE ON ROUTINE fn TO my_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA my_schema TO my_user;
GRANT EXECUTE ON ALL PROCEDURES IN SCHEMA my_schema TO my_user;
GRANT EXECUTE ON ALL ROUTINES IN SCHEMA my_schema TO my_user;
GRANT USAGE ON LANGUAGE my_lang TO my_user;
GRANT SELECT ON LARGE OBJECT 564182 TO my_user;
GRANT ALL ON TABLESPACE my_tblspc TO my_user;
GRANT USAGE ON TYPE my_type TO my_role;
GRANT my_user TO my_group WITH ADMIN OPTION GRANTED BY CURRENT_USER;
GRANT my_user TO my_group GRANTED BY SESSION_USER;
GRANT my_user TO my_group WITH ADMIN OPTION GRANTED BY my_new_role;
GRANT CONNECT, CREATE, TEMP, TEMPORARY ON DATABASE my_db TO xyz;
GRANT CONNECT, CREATE, TEMP, TEMPORARY ON DATABASE my_db TO my_user, my_other_user WITH GRANT OPTION;
GRANT SELECT ON abc TO xyz, mno;
GRANT EXECUTE ON ALL ROUTINES IN SCHEMA my_schema TO my_user, my_other_user;
GRANT EXECUTE ON FUNCTION test(a IN TEXT, b OUT TEXT, INOUT c TEXT, VARIADIC d TEXT) TO my_user;
GRANT EXECUTE ON FUNCTION test(a TEXT, b my_table.my_column%type) TO my_user;

-- Role membership options (PostgreSQL 16+). OPTION is a synonym for TRUE, and
-- several options can be given as a comma-separated list.
-- https://www.postgresql.org/docs/16/sql-grant.html
GRANT my_user TO my_group WITH ADMIN TRUE;
GRANT my_user TO my_group WITH ADMIN FALSE;
GRANT my_user TO my_group WITH INHERIT TRUE;
GRANT my_user TO my_group WITH INHERIT FALSE;
GRANT my_user TO my_group WITH SET OPTION;
GRANT my_user TO my_group WITH SET FALSE;
GRANT my_user TO my_group WITH INHERIT TRUE, SET FALSE;
GRANT my_user TO my_group WITH ADMIN OPTION, INHERIT FALSE, SET TRUE
    GRANTED BY CURRENT_ROLE;
