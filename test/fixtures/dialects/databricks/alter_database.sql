-- Transfer ownership of the schema to another user
ALTER SCHEMA some_cat OWNER TO `alf@melmak.et`;
ALTER SCHEMA some_cat OWNER TO my_group;

-- SET is allowed as an optional keyword
ALTER SCHEMA some_cat SET OWNER TO `alf@melmak.et`;
ALTER SCHEMA some_cat SET OWNER TO my_group;

-- DATABASE IS ALLOWED INSTEAD OF SCHEMA
ALTER DATABASE some_cat OWNER TO `alf@melmak.et`;
ALTER DATABASE some_cat SET OWNER TO `alf@melmak.et`;
ALTER DATABASE some_cat OWNER TO my_group;
ALTER DATABASE some_cat SET OWNER TO my_group;

-- Set and unset schema tags
ALTER SCHEMA some_cat SET TAGS ('tag1'='value1');
ALTER DATABASE some_cat SET TAGS ('tag2'='value2', 'tag3'='value3');
ALTER DATABASE some_cat UNSET TAGS ('tag1');
ALTER SCHEMA some_cat UNSET TAGS ('tag2', 'tag3');

-- Enable/Inherit/Disable Predictive Optimization
ALTER SCHEMA some_cat ENABLE PREDICTIVE OPTIMIZATION;
ALTER DATABASE some_cat INHERIT PREDICTIVE OPTIMIZATION;
ALTER SCHEMA some_cat DISABLE PREDICTIVE OPTIMIZATION;

-- -- Add some schema properties
ALTER SCHEMA some_cat SET DBPROPERTIES ('Edited-by'='John Doe', 'Edit-date'='2020-01-01');
