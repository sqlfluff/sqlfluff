create schema mytestschema_clone_restore clone testschema;
create schema mytestdatabase1.mytestschema_clone_restore clone mytestdatabase2.testschema;
create schema mytestschema_clone_restore clone testschema before (timestamp => to_timestamp(40*365*86400));
create schema mytestschema comment = 'My test schema.';
create schema mytestschema tag (tag1 = 'foo', tag2 = 'bar');
create schema mytestschema with managed access;
create transient schema if not exists mytestschema default_ddl_collation = 'de_DE';
CREATE SCHEMA MYDB.MYSCHEMA COMMENT = "Space for landing my data";
CREATE SCHEMA IF NOT EXISTS MYDB.MYSCHEMA COMMENT = "Space for landing my data";
CREATE OR ALTER SCHEMA MYDB.MYSCHEMA;
CREATE SCHEMA governed_schema WITH CONTACT (STEWARD = my_db.my_schema.contact1, SUPPORT = contact2);
CREATE SCHEMA modern_schema DATA_RETENTION_TIME_IN_DAYS = 5 LOG_LEVEL = 'INFO' OBJECT_VISIBILITY = PRIVILEGED;
CREATE SCHEMA iceberg_schema
    EXTERNAL_VOLUME = 'my_volume'
    CATALOG = 'my_catalog'
    ICEBERG_DEFAULT_DDL_COLLATION = 'en-ci'
    ICEBERG_VERSION_DEFAULT = 2
    ICEBERG_MERGE_ON_READ_BEHAVIOR = 'AUTO'
    ENABLE_ICEBERG_MERGE_ON_READ = FALSE
    REPLACE_INVALID_CHARACTERS = TRUE
    STORAGE_SERIALIZATION_POLICY = OPTIMIZED
    CLASSIFICATION_PROFILE = 'my_profile'
    CATALOG_SYNC = 'my_open_catalog_integration'
    ENABLE_DATA_COMPACTION = TRUE
    OAUTH_AUTHORIZATION_SERVER = my_external_oauth_integration
    OAUTH_SCOPES_SUPPORTED = 'read,write';
