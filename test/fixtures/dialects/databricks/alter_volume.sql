-- Rename a volume
ALTER VOLUME some_vol RENAME TO some_new_vol;

-- Transfer ownership of the volume to another user
ALTER VOLUME some_vol OWNER TO `alf@melmak.et`;
ALTER VOLUME some_vol OWNER TO my_group;

-- SET is allowed as an optional keyword
ALTER VOLUME some_vol SET OWNER TO `alf@melmak.et`;
ALTER VOLUME some_vol SET OWNER TO my_group;

-- Set and unset volume tags
ALTER VOLUME some_vol SET TAGS ('tag1'='value1');
ALTER VOLUME some_vol SET TAGS ('tag2'='value2', 'tag3'='value3');
ALTER VOLUME some_vol UNSET TAGS ('tag1');
ALTER VOLUME some_vol UNSET TAGS ('tag2', 'tag3');
