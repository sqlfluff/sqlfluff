alter schema if exists schema1 rename to schema2;
alter schema schema1 swap with schema2;
alter schema schema2 enable managed access;
alter schema schema1 set data_retention_time_in_days = 3;
alter schema schema1 set tag tag1 = 'value1', tag2 = 'value2';
alter schema schema1 unset data_retention_time_in_days;
alter schema schema1 unset data_retention_time_in_days, max_data_extension_time_in_days;
alter schema schema1 unset tag foo, bar;

ALTER SCHEMA s1 SET LOG_LEVEL = 'DEBUG';
ALTER SCHEMA s1 SET TRACE_LEVEL = 'ALWAYS' STORAGE_SERIALIZATION_POLICY = OPTIMIZED;
ALTER SCHEMA IF EXISTS s1 SET
    EXTERNAL_VOLUME = 'my_volume'
    CATALOG = 'my_catalog'
    REPLACE_INVALID_CHARACTERS = TRUE
    DEFAULT_STREAMLIT_NOTEBOOK_WAREHOUSE = my_wh;
ALTER SCHEMA s1 SET CONTACT STEWARD = my_db.my_schema.steward_contact;
ALTER SCHEMA s1 UNSET LOG_LEVEL, STORAGE_SERIALIZATION_POLICY, COMMENT;
ALTER SCHEMA s1 UNSET DEFAULT_NOTEBOOK_COMPUTE_POOL_CPU, DEFAULT_NOTEBOOK_COMPUTE_POOL_GPU;
ALTER SCHEMA s1 UNSET CONTACT STEWARD;
ALTER SCHEMA s1 UNSET DCM PROJECT;
