CREATE ALIAS my_alias FOR my_table;

CREATE OR REPLACE ALIAS my_alias FOR my_schema.my_table;

CREATE PUBLIC ALIAS my_public_alias FOR my_table;

CREATE OR REPLACE PUBLIC ALIAS my_public_alias FOR my_schema.my_table;

CREATE ALIAS my_table_alias FOR TABLE my_table;

CREATE ALIAS my_module_alias FOR MODULE my_module;

CREATE ALIAS my_sequence_alias FOR SEQUENCE my_sequence;

DROP ALIAS my_alias;

DROP PUBLIC ALIAS my_public_alias;

DROP ALIAS my_module_alias FOR MODULE;

CREATE SYNONYM my_synonym FOR my_table;

CREATE OR REPLACE SYNONYM my_synonym FOR my_schema.my_table;

CREATE PUBLIC SYNONYM my_public_synonym FOR my_table;

CREATE SYNONYM my_table_synonym FOR TABLE my_table;

CREATE SYNONYM my_sequence_synonym FOR SEQUENCE my_sequence;

DROP SYNONYM my_synonym;

DROP PUBLIC SYNONYM my_public_synonym;

DROP SYNONYM my_table_synonym FOR TABLE;
