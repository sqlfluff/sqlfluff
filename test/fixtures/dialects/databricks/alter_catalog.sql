-- Transfer ownership of the catalog to another user
ALTER CATALOG some_cat OWNER TO `alf@melmak.et`;
ALTER CATALOG some_cat OWNER TO my_group;

-- SET is allowed as an optional keyword
ALTER CATALOG some_cat SET OWNER TO `alf@melmak.et`;
ALTER CATALOG some_cat SET OWNER TO my_group;

-- Set and unset catalog tags
ALTER CATALOG some_cat SET TAGS ('tag1'='value1');
ALTER CATALOG some_cat SET TAGS ('tag2'='value2', 'tag3'='value3');
ALTER CATALOG some_cat UNSET TAGS ('tag1');
ALTER CATALOG some_cat UNSET TAGS ('tag2', 'tag3');

-- Enable/Inherit/Disable Predictive Optimization
ALTER CATALOG some_cat ENABLE PREDICTIVE OPTIMIZATION;
ALTER CATALOG some_cat INHERIT PREDICTIVE OPTIMIZATION;
ALTER CATALOG some_cat DISABLE PREDICTIVE OPTIMIZATION;
