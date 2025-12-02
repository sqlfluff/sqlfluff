alter schema if exists schema1 rename to schema2;
alter schema schema1 swap with schema2;
alter schema schema2 enable managed access;
alter schema schema1 set data_retention_time_in_days = 3;
alter schema schema1 set tag tag1 = 'value1', tag2 = 'value2';
alter schema schema1 unset data_retention_time_in_days;
alter schema schema1 unset data_retention_time_in_days, max_data_extension_time_in_days;
alter schema schema1 unset tag foo, bar;
