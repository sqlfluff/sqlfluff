CREATE VIRTUAL SCHEMA hive
USING adapter.jdbc_adapter
WITH
    SQL_DIALECT	     = 'HIVE'
    CONNECTION_STRING   = 'jdbc:hive2://localhost:10000/default'
    SCHEMA_NAME	     = 'default'
    USERNAME	     = 'hive-usr'
    PASSWORD	     = 'hive-pwd';
