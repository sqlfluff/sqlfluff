alter schema if exists schema1 rename to schema2;
alter schema schema1 swap with schema2;
alter schema schema2 enable managed access;
alter schema schema1 set data_retention_time_in_days = 3;
