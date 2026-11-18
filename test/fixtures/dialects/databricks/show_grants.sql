-- https://docs.databricks.com/aws/en/sql/language-manual/security-show-grant

SHOW GRANTS ON TABLE my_table;

SHOW GRANTS ON demo.schema.names;

SHOW GRANTS ON SCHEMA my_schema;

SHOW GRANTS ON CATALOG main;

SHOW GRANTS ON VIEW my_view;

SHOW GRANTS ON METASTORE;

SHOW GRANTS `alf@melmak.et` ON SCHEMA my_schema;

SHOW GRANTS alf ON TABLE my_table;

-- "You can also use GRANT as an alternative for GRANTS."
SHOW GRANT ON TABLE my_table;

SHOW GRANT `alf@melmak.et` ON TABLE my_table;

-- The rest of the Unity Catalog securable list.
SHOW GRANTS ON CATALOG;

SHOW GRANTS ON CONNECTION my_connection;

SHOW GRANTS ON CLEAN ROOM my_clean_room;

SHOW GRANTS ON EXTERNAL LOCATION my_location;

SHOW GRANTS ON EXTERNAL METADATA my_metadata;

SHOW GRANTS ON PROCEDURE my_procedure;

SHOW GRANTS ON SHARE my_share;

SHOW GRANTS ON STORAGE CREDENTIAL my_credential;

SHOW GRANTS ON SERVICE CREDENTIAL my_credential;

SHOW GRANTS ON CREDENTIAL my_credential;
