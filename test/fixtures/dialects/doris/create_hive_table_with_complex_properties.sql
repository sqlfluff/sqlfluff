CREATE TABLE hive_catalog.hive_db.complex_table
(
    user_id BIGINT,
    username STRING,
    age INT,
    score DECIMAL(10, 2),
    create_time DATETIME,
    is_active BOOLEAN
)
ENGINE=hive
PROPERTIES (
    'file_format' = 'orc',
    'hive.metastore.uris' = 'thrift://127.0.0.1:9083',
    'fs.defaultFS' = 'hdfs://namenode:9000',
    'hadoop.username' = 'hive',
    'hive.metastore.kerberos.principal' = 'hive/_HOST@EXAMPLE.COM',
    'hive.metastore.kerberos.keytab' = '/path/to/hive.keytab'
);
