DESCRIBE RESULT 'f2f07bdb-6a08-4689-9ad8-a1ba968a44b6';
DESC RESULT 'f2f07bdb-6a08-4689-9ad8-a1ba968a44b6';

DESCRIBE RESULT LAST_QUERY_ID();
DESC RESULT LAST_QUERY_ID();

DESCRIBE NETWORK POLICY my_policy;
DESC NETWORK POLICY my_policy;

DESCRIBE SHARE sales_s;
DESC SHARE sales_s;

DESCRIBE SHARE ab67890.sales_s;
DESC SHARE ab67890.sales_s;

DESCRIBE USER test_user;
DESC USER test_user;

DESCRIBE WAREHOUSE my_warehouse;
DESC WAREHOUSE my_warehouse;

DESCRIBE WAREHOUSE "my warehouse";
DESC WAREHOUSE "my warehouse";

DESCRIBE DATABASE my_database;
DESC DATABASE my_database;

DESCRIBE API INTEGRATION my_integration;
DESC API INTEGRATION my_integration;

DESCRIBE NOTIFICATION INTEGRATION my_integration;
DESC NOTIFICATION INTEGRATION my_integration;

DESCRIBE SECURITY INTEGRATION my_integration;
DESC SECURITY INTEGRATION my_integration;

DESCRIBE STORAGE INTEGRATION my_integration;
DESC STORAGE INTEGRATION my_integration;

DESCRIBE INTEGRATION my_integration;
DESC INTEGRATION my_integration;

DESCRIBE SESSION POLICY my_session_policy;
DESC SESSION POLICY my_session_policy;

DESCRIBE SCHEMA my_schema;
DESC SCHEMA my_schema;

DESCRIBE SCHEMA my_database.my_schema;
DESC SCHEMA my_database.my_schema;

DESCRIBE TABLE my_table;
DESC TABLE my_table;

DESCRIBE TABLE my_database.my_schema.my_table;
DESC TABLE my_database.my_schema.my_table;

DESCRIBE TABLE my_table TYPE = COLUMNS;
DESC TABLE my_table TYPE = COLUMNS;

DESCRIBE TABLE my_table TYPE = STAGE;
DESC TABLE my_table TYPE = STAGE;

DESCRIBE EXTERNAL TABLE my_table;
DESC EXTERNAL TABLE my_table;

DESCRIBE EXTERNAL TABLE my_table TYPE = COLUMNS;
DESC EXTERNAL TABLE my_table TYPE = COLUMNS;

DESCRIBE EXTERNAL TABLE my_table TYPE = STAGE;
DESC EXTERNAL TABLE my_table TYPE = STAGE;

DESCRIBE VIEW my_view;
DESC VIEW my_view;

DESCRIBE VIEW my_database.my_schema.my_view;
DESC VIEW my_database.my_schema.my_view;

DESCRIBE MATERIALIZED VIEW my_view;
DESC MATERIALIZED VIEW my_view;

DESCRIBE MATERIALIZED VIEW my_database.my_schema.my_view;
DESC MATERIALIZED VIEW my_database.my_schema.my_view;

DESCRIBE SEQUENCE my_sequence;
DESC SEQUENCE my_sequence;

DESCRIBE MASKING POLICY my_masking_policy;
DESC MASKING POLICY my_masking_policy;

DESCRIBE ROW ACCESS POLICY my_row_access_policy;
DESC ROW ACCESS POLICY my_row_access_policy;

DESCRIBE FILE FORMAT my_file_format;
DESC FILE FORMAT my_file_format;

DESCRIBE STAGE my_stage;
DESC STAGE my_stage;

DESCRIBE PIPE my_pipe;
DESC PIPE my_pipe;

DESCRIBE STREAM my_stream;
DESC STREAM my_stream;

DESCRIBE TASK my_task;
DESC TASK my_task;

DESCRIBE FUNCTION multiply(NUMBER, NUMBER);
DESC FUNCTION multiply(NUMBER, NUMBER);

DESCRIBE PROCEDURE my_pi();
DESC PROCEDURE my_pi();

DESCRIBE PROCEDURE area_of_circle(FLOAT);
DESC PROCEDURE area_of_circle(FLOAT);
