CREATE DATABASE db_name ENGINE = engine() COMMENT 'Comment';

CREATE DATABASE db_comment ENGINE = Memory COMMENT 'The temporary database';
SELECT name, comment FROM system.databases WHERE name = 'db_comment';
