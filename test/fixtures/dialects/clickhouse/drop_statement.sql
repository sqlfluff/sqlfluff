-- drop database
DROP DATABASE db;
DROP DATABASE IF EXISTS db;
DROP DATABASE db ON CLUSTER cluster;
DROP DATABASE db SYNC;


-- -- drop table
DROP TABLE db_name;
DROP TABLE db.name;
DROP TABLE IF EXISTS db_name;
DROP TABLE db_name ON CLUSTER cluster;
DROP TABLE db_name SYNC;
DROP TEMPORARY TABLE db_name;

-- -- drop dictionary
DROP DICTIONARY dict_name;
DROP DICTIONARY IF EXISTS dict_name;
DROP DICTIONARY dict_name SYNC;

-- -- drop user
DROP USER user_name;
DROP USER IF EXISTS user_name;
DROP USER user_name ON CLUSTER cluster_name;

-- -- drop role
DROP ROLE role_name;
DROP ROLE IF EXISTS role_name;
DROP ROLE role_name ON CLUSTER cluster_name;
