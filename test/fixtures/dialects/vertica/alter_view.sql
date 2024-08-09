-- https://docs.vertica.com/latest/en/sql-reference/statements/alter-statements/alter-view/#examples
ALTER VIEW view1, view2 RENAME TO view3, view4;
ALTER VIEW view1 OWNER TO Alice;
ALTER VIEW view1 SET SCHEMA s1;
ALTER VIEW view1 INCLUDE SCHEMA PRIVILEGES;
