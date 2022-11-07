ALTER PROCEDURE insert_data(integer, integer) RENAME TO insert_record;
ALTER PROCEDURE insert_data(integer, integer) OWNER TO joe;
ALTER PROCEDURE insert_data(integer, integer) OWNER TO CURRENT_USER;
ALTER PROCEDURE insert_data(integer, integer) SET SCHEMA accounting;
ALTER PROCEDURE insert_data(integer, integer) DEPENDS ON EXTENSION myext;
ALTER PROCEDURE check_password(text) SET search_path = admin, pg_temp;
ALTER PROCEDURE check_password(text) RESET search_path;
