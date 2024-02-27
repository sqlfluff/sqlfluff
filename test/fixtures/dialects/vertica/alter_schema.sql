-- https://docs.vertica.com/latest/en/sql-reference/statements/alter-statements/alter-schema/#examples
ALTER SCHEMA ms OWNER TO dbadmin CASCADE;
ALTER SCHEMA s1, s2 RENAME TO s3, s4;
ALTER SCHEMA s1 DEFAULT INCLUDE SCHEMA PRIVILEGES;
ALTER SCHEMA s1 DEFAULT EXCLUDE SCHEMA PRIVILEGES;
