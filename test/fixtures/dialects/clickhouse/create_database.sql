CREATE DATABASE db_name;
CREATE DATABASE db_name COMMENT 'SingleQuoted';
CREATE DATABASE db_name COMMENT "DoubleQuoted";
CREATE DATABASE db_name COMMENT 'SingleQuoted three words';
CREATE DATABASE db_name COMMENT "DoubleQuoted three words";
CREATE DATABASE db_name COMMENT 'Weird characters: !@#$%^&*()_+{}|:"<>?';
CREATE DATABASE db_name ON CLUSTER cluster;
CREATE DATABASE db_name ON CLUSTER "cluster";
CREATE DATABASE db_name ON CLUSTER "underscore_cluster";
CREATE DATABASE db_name ON CLUSTER 'cluster';
CREATE DATABASE db_name ON CLUSTER 'underscore_cluster';

CREATE DATABASE db_name ENGINE = Lazy() COMMENT 'Comment';

CREATE DATABASE db_comment ENGINE = Lazy() COMMENT 'The temporary database';
SELECT name, comment FROM system.databases WHERE name = 'db_comment';

-- https://clickhouse.com/docs/en/engines/database-engines/atomic
CREATE DATABASE test;
CREATE DATABASE test ENGINE = Atomic;

-- https://clickhouse.com/docs/en/engines/database-engines/lazy
CREATE DATABASE testlazy;
CREATE DATABASE testlazy ENGINE = Lazy(expiration_time_in_seconds);

-- https://clickhouse.com/docs/en/engines/database-engines/replicated
CREATE DATABASE testdb;
CREATE DATABASE testdb ENGINE = Replicated('zoo_path', 'shard_name', 'replica_name');
CREATE DATABASE testdb ENGINE = Replicated('zoo_path', 'shard_name', 'replica_name') SETTINGS key1 = value1;
CREATE DATABASE testdb ENGINE = Replicated('zoo_path', 'shard_name', 'replica_name') SETTINGS key1 = 1, key2 = 2;

CREATE DATABASE r ENGINE=Replicated('some/path/r','shard1','replica1');
CREATE DATABASE r ENGINE=Replicated('some/path/r','shard1','other_replica');
CREATE DATABASE r ENGINE=Replicated('some/path/r','other_shard','{replica}');
CREATE DATABASE r ENGINE=Replicated('some/path/r','other_shard','r2');

-- https://clickhouse.com/docs/en/engines/database-engines/postgresql
CREATE DATABASE test_database ENGINE = PostgreSQL('postgres1:5432', 'test_database', 'postgres');
CREATE DATABASE test_database ENGINE = PostgreSQL('postgres1:5432', 'test_database', 'postgres', 'mysecretpassword');
CREATE DATABASE test_database ENGINE = PostgreSQL('postgres1:5432', 'test_database', 'postgres', 'mysecretpassword', 'schema_name');
CREATE DATABASE test_database ENGINE = PostgreSQL('postgres1:5432', 'test_database', 'postgres', 'mysecretpassword', 'schema_name', 1);

-- https://clickhouse.com/docs/en/engines/database-engines/mysql
CREATE DATABASE IF NOT EXISTS mysql_db ENGINE = MySQL('localhost:3306', 'test', 'my_user', 'user_password');
CREATE DATABASE mysql_db ON CLUSTER cluster ENGINE = MySQL('localhost:3306', 'test', 'my_user', 'user_password');
CREATE DATABASE mysql_db ENGINE = MySQL('localhost:3306', 'my_user', 'user_password');
CREATE DATABASE mysql_db ENGINE = MySQL('localhost:3306', test, 'my_user', 'user_password');
CREATE DATABASE mysql_db ENGINE = MySQL('localhost:3306', 'test', 'my_user', 'user_password');
CREATE DATABASE mysql_db ENGINE = MySQL('localhost:3306', 'test', 'my_user', 'user_password') SETTINGS read_write_timeout=10000;
CREATE DATABASE mysql_db ENGINE = MySQL('localhost:3306', 'test', 'my_user', 'user_password') SETTINGS read_write_timeout=10000, connect_timeout=100;

-- https://clickhouse.com/docs/en/engines/database-engines/sqlite
CREATE DATABASE sqlite_db ENGINE = SQLite('sqlite.db');

-- https://clickhouse.com/docs/en/engines/database-engines/materialized-postgresql
CREATE DATABASE postgres_db ENGINE = MaterializedPostgreSQL('postgres1:5432', 'postgres_database', 'postgres_user', 'postgres_password');
CREATE DATABASE postgres_database ENGINE = MaterializedPostgreSQL('postgres1:5432', 'postgres_database', 'postgres_user', 'postgres_password') SETTINGS materialized_postgresql_schema = 'postgres_schema';
CREATE DATABASE database1 ENGINE = MaterializedPostgreSQL('postgres1:5432', 'postgres_database', 'postgres_user', 'postgres_password') SETTINGS materialized_postgresql_tables_list = 'schema1.table1,schema2.table2,schema1.table3', materialized_postgresql_tables_list_with_schema = 1;
CREATE DATABASE database1 ENGINE = MaterializedPostgreSQL('postgres1:5432', 'postgres_database', 'postgres_user', 'postgres_password') SETTINGS materialized_postgresql_schema_list = 'schema1,schema2,schema3';
CREATE DATABASE database1 ENGINE = MaterializedPostgreSQL('postgres1:5432', 'postgres_database', 'postgres_user', 'postgres_password') SETTINGS materialized_postgresql_tables_list = 'table1,table2,table3';
CREATE DATABASE demodb ENGINE = MaterializedPostgreSQL('postgres1:5432', 'postgres_database', 'postgres_user', 'postgres_password') SETTINGS materialized_postgresql_replication_slot = 'clickhouse_sync', materialized_postgresql_snapshot = '0000000A-0000023F-3', materialized_postgresql_tables_list = 'table1,table2,table3';

CREATE DATABASE IF NOT EXISTS db_name ENGINE = MaterializedPostgreSQL('host:port', 'database', 'user', 'password');
CREATE DATABASE db_name ON CLUSTER cluster ENGINE = MaterializedPostgreSQL('host:port', 'database', 'user', 'password');
CREATE DATABASE IF NOT EXISTS db_name ON CLUSTER cluster ENGINE = MaterializedPostgreSQL('host:port', 'database', 'user', 'password');
CREATE DATABASE IF NOT EXISTS db_name ENGINE = MaterializedPostgreSQL('host:port', 'database', 'user', 'password') SETTINGS materialized_postgresql_schema = 'postgres_schema';
CREATE DATABASE db_name ON CLUSTER cluster ENGINE = MaterializedPostgreSQL('host:port', 'database', 'user', 'password') SETTINGS materialized_postgresql_schema = 'postgres_schema';
CREATE DATABASE IF NOT EXISTS db_name ON CLUSTER cluster ENGINE = MaterializedPostgreSQL('host:port', 'database', 'user', 'password') SETTINGS materialized_postgresql_schema = 'postgres_schema';

-- https://clickhouse.com/docs/en/engines/database-engines/materialized-mysql
CREATE DATABASE IF NOT EXISTS db_name ENGINE = MaterializedMySQL('localhost:3306', 'db', 'user', '***') TABLE OVERRIDE table1 (id UInt32, name String) TABLE OVERRIDE;
CREATE DATABASE IF NOT EXISTS db_name ENGINE = MaterializedMySQL('localhost:3306', 'db', 'user', '***') TABLE OVERRIDE table1 (id UInt32, name String) TABLE OVERRIDE table2 (id UInt32, name String);
CREATE DATABASE IF NOT EXISTS db_name ENGINE = MaterializedMySQL('localhost:3306', 'db', 'user', '***');
CREATE DATABASE IF NOT EXISTS db_name ON CLUSTER cluster ENGINE = MaterializedMySQL('localhost:3306', 'db', 'user', '***');
CREATE DATABASE IF NOT EXISTS db_name ON CLUSTER cluster ENGINE = MaterializedMySQL('localhost:3306', 'db', 'user', '***') TABLE OVERRIDE table1 (id UInt32, name String) TABLE OVERRIDE table2 (id UInt32, name String);
CREATE DATABASE IF NOT EXISTS db_name ON CLUSTER cluster ENGINE = MaterializedMySQL('localhost:3306', 'db', 'user', '***') SETTINGS materialized_mysql_database_engine = 'InnoDB';
CREATE DATABASE IF NOT EXISTS db_name ON CLUSTER cluster ENGINE = MaterializedMySQL('localhost:3306', 'db', 'user', '***') SETTINGS materialized_mysql_database_engine = 'InnoDB' TABLE OVERRIDE table1 (id UInt32, name String) TABLE OVERRIDE table2 (id UInt32, name String);

CREATE DATABASE db_name ON CLUSTER cluster ENGINE = MaterializedMySQL('localhost:3306', 'db', 'user', '***');
CREATE DATABASE db_name ON CLUSTER cluster ENGINE = MaterializedMySQL('localhost:3306', 'db', 'user', '***') TABLE OVERRIDE table1 (id UInt32, name String) TABLE OVERRIDE table2 (id UInt32, name String);
CREATE DATABASE db_name ON CLUSTER cluster ENGINE = MaterializedMySQL('localhost:3306', 'db', 'user', '***') SETTINGS materialized_mysql_database_engine = 'InnoDB';
CREATE DATABASE db_name ON CLUSTER cluster ENGINE = MaterializedMySQL('localhost:3306', 'db', 'user', '***') SETTINGS materialized_mysql_database_engine = 'InnoDB' TABLE OVERRIDE table1 (id UInt32, name String) TABLE OVERRIDE table2 (id UInt32, name String);

CREATE DATABASE db_name ENGINE = MaterializedMySQL('localhost:3306', 'db', 'user', '***') SETTINGS materialized_mysql_database_engine = 'InnoDB';
CREATE DATABASE db_name ENGINE = MaterializedMySQL('localhost:3306', 'db', 'user', '***') SETTINGS materialized_mysql_database_engine = 'InnoDB' TABLE OVERRIDE table1 (id UInt32, name String) TABLE OVERRIDE table2 (id UInt32, name String);
CREATE DATABASE db_name ON CLUSTER cluster ENGINE = MaterializedMySQL('localhost:3306', 'db', 'user', '***') SETTINGS materialized_mysql_database_engine = 'InnoDB';
CREATE DATABASE db_name ON CLUSTER cluster ENGINE = MaterializedMySQL('localhost:3306', 'db', 'user', '***') SETTINGS materialized_mysql_database_engine = 'InnoDB' TABLE OVERRIDE table1 (id UInt32, name String) TABLE OVERRIDE table2 (id UInt32, name String);

CREATE DATABASE mysql ENGINE = MaterializedMySQL('localhost:3306', 'db', 'user', '***') SETTINGS allows_query_when_mysql_lost=true, max_wait_time_when_mysql_unavailable=10000;
