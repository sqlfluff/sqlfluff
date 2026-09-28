-- Base form with a fully-qualified project object name.
EXECUTE DBT PROJECT my_database.my_schema.my_dbt_project;

-- dbt command-line arguments.
EXECUTE DBT PROJECT my_db.my_schema.my_project
    ARGS = '--select simple_customers combined_bookings prepped_data --target dev';

-- IF EXISTS plus version override.
EXECUTE DBT PROJECT IF EXISTS my_db.my_schema.my_project
    DBT_VERSION = '1.9.4';

-- External access integrations, environment and writeback.
EXECUTE DBT PROJECT my_db.my_schema.my_project
    EXTERNAL_ACCESS_INTEGRATIONS = (my_integration)
    ENVIRONMENT = 'prod'
    WRITEBACK = FALSE;

-- Workspace variant with environment variable overrides.
EXECUTE DBT PROJECT IF EXISTS FROM WORKSPACE "My dbt Project Workspace"
    ENV_VARS = ('DBT_KEY1' = 'value1', 'DBT_KEY2' = 'value2');

-- Workspace variant with imports and project root.
EXECUTE DBT PROJECT FROM WORKSPACE my_workspace
    IMPORTS = ('@my_stage/target' AS 'state')
    PROJECT_ROOT = 'analytics';

-- System functions are documented inside the IMPORTS list.
EXECUTE DBT PROJECT my_db.my_schema.my_project
    IMPORTS = (SYSTEM$DBT_GET_LAST_SUCCESSFUL_RUN_TARGET() AS 'state');
