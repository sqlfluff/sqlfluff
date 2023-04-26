-- DROP DATABASE
DROP DATABASE db;
DROP DATABASE IF EXISTS db;
DROP DATABASE db ON CLUSTER cluster;
DROP DATABASE db SYNC;


-- DROP TABLE
DROP TABLE db_name;
DROP TABLE db.name;
DROP TABLE IF EXISTS db_name;
DROP TABLE db_name ON CLUSTER cluster;
DROP TABLE db_name SYNC;
DROP TEMPORARY TABLE db_name;

-- DROP DICTIONARY
DROP DICTIONARY dict_name;
DROP DICTIONARY IF EXISTS dict_name;
DROP DICTIONARY dict_name SYNC;

-- DROP USER
DROP USER user_name;
DROP USER IF EXISTS user_name;
DROP USER user_name ON CLUSTER cluster_name;

-- DROP ROLE
DROP ROLE role_name;
DROP ROLE IF EXISTS role_name;
DROP ROLE role_name ON CLUSTER cluster_name;

-- DROP ROW POLICY
-- DROP [ROW] POLICY [IF EXISTS] name [,...] ON [database.]table [,...] [ON CLUSTER cluster_name]

-- DROP QUOTA
DROP QUOTA quota_name;
DROP QUOTA IF EXISTS quota_name;
DROP QUOTA quota_name ON CLUSTER cluster_name;

-- DROP SETTINGS PROFILE
DROP setting_name PROFILE profile_name;
DROP setting_name PROFILE IF EXISTS profile_name;
DROP setting_name PROFILE profile_name ON CLUSTER cluster_name;
DROP setting_name1,setting_name2 PROFILE profile_name;

-- DROP VIEW
DROP VIEW view_name;
DROP VIEW db.view_name;
DROP VIEW IF EXISTS view_name;
DROP VIEW view_name ON CLUSTER cluster;
DROP VIEW view_name SYNC;

-- DROP FUNCTION
DROP FUNCTION function_name;
DROP FUNCTION IF EXISTS function_name;
DROP FUNCTION function_name on CLUSTER cluster;
