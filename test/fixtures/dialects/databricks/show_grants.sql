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
