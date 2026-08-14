-- Basic CREATE DBT PROJECT
CREATE DBT PROJECT my_dbt_project;
CREATE DBT PROJECT IF NOT EXISTS my_dbt_project;
CREATE OR REPLACE DBT PROJECT my_dbt_project;

-- With FROM source location
CREATE DBT PROJECT my_dbt_project
    FROM 'https://github.com/my-org/my-dbt-repo.git';

-- With COMMENT
CREATE DBT PROJECT my_dbt_project
    COMMENT = 'My dbt project';

-- With DBT_VERSION
CREATE DBT PROJECT my_dbt_project
    DBT_VERSION = 1.8;

-- With DEFAULT_TARGET
CREATE DBT PROJECT my_dbt_project
    DEFAULT_TARGET = prod;

-- With EXTERNAL_ACCESS_INTEGRATIONS
CREATE DBT PROJECT my_dbt_project
    EXTERNAL_ACCESS_INTEGRATIONS = (my_integration);

CREATE DBT PROJECT my_dbt_project
    EXTERNAL_ACCESS_INTEGRATIONS = (integration_a, integration_b);

-- Full example
CREATE OR REPLACE DBT PROJECT my_dbt_project
    FROM 'https://github.com/my-org/my-dbt-repo.git'
    COMMENT = 'Full dbt project example'
    DBT_VERSION = 1.8
    DEFAULT_TARGET = prod
    EXTERNAL_ACCESS_INTEGRATIONS = (my_github_integration);
