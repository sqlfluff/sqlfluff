-- https://www.postgresql.org/docs/current/sql-altertype.html
ALTER TYPE foo RENAME TO bar;
ALTER TYPE foo OWNER TO CURRENT_USER;
ALTER TYPE foo OWNER TO new_owner;
ALTER TYPE foo SET SCHEMA new_schema;
