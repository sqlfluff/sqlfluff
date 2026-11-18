CREATE OR REPLACE GIT REPOSITORY snowflake_extensions
    API_INTEGRATION = git_api_integration
    GIT_CREDENTIALS = git_secret
    ORIGIN = 'https://github.com/my-account/snowflake-extensions.git';

CREATE GIT REPOSITORY IF NOT EXISTS my_db.my_schema.my_repo
    ORIGIN = 'https://github.com/my-account/my-repo.git'
    API_INTEGRATION = git_api_integration
    COMMENT = 'public repository, no credentials';

CREATE GIT REPOSITORY my_repo
    ORIGIN = 'https://github.com/my-account/my-repo.git'
    API_INTEGRATION = git_api_integration
    WITH TAG (cost_center = 'data_eng', env = 'dev');
