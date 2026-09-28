-- Basic privileges
GRANT SELECT ON db_name TO user_name;
GRANT INSERT ON db_name.* TO user_name;
GRANT DELETE ON db_name TO user_name;
GRANT UPDATE ON db_name TO user_name;

-- ALTER privileges
GRANT ALTER ON db_name TO user_name;
GRANT ALTER TABLE ON db_name TO user_name;
GRANT ALTER DELETE ON db_name TO user_name;
GRANT ALTER UPDATE ON db_name TO user_name;
GRANT ALTER ADD COLUMN ON db_name TO user_name;
GRANT ALTER DROP COLUMN ON db_name TO user_name;

-- CREATE privileges
GRANT CREATE ON db_name TO user_name;
GRANT CREATE TABLE ON db_name TO user_name;

-- Multiple privileges
GRANT SELECT, INSERT ON db_name TO user_name;
GRANT ALTER DELETE, ALTER UPDATE ON db_name TO user_name;

-- ALL PRIVILEGES
GRANT ALL ON db_name TO user_name;

-- https://fiddle.clickhouse.com/20ab59f5-aaf3-4cb7-9bd0-68d18763fe63
GRANT ALTER PROJECTION ON default.test_table TO user_name;
GRANT ALTER ADD PROJECTION ON *.* TO user_name;
GRANT ALTER MODIFY PROJECTION ON test_table TO user_name;
GRANT ALTER DROP PROJECTION ON *.* TO user_name;
GRANT ALTER MATERIALIZE PROJECTION ON default.test_table TO user_name;
GRANT ALTER CLEAR PROJECTION ON test_table TO user_name;
GRANT ALTER ADD PROJECTION, ALTER MATERIALIZE PROJECTION, ALTER PROJECTION ON default.test_table TO user_name;
