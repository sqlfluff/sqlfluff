CREATE GIT REPOSITORY my_repo
    API_INTEGRATION = git_api_integration
    ORIGIN = 'https://github.com/my-account/my-repo.git';

CREATE OR REPLACE GIT REPOSITORY IF NOT EXISTS my_db.my_schema.my_repo
    ORIGIN = 'https://github.com/my-account/my-repo.git'
    API_INTEGRATION = git_api_integration
    GIT_CREDENTIALS = my_db.my_schema.git_secret
    COMMENT = 'Repository for dbt models'
    WITH TAG (cost_center = 'data', env = 'prod');

ALTER GIT REPOSITORY my_repo FETCH;

ALTER GIT REPOSITORY IF EXISTS my_repo SET
    GIT_CREDENTIALS = git_secret
    API_INTEGRATION = git_api_integration
    COMMENT = 'Updated comment';

ALTER GIT REPOSITORY my_repo UNSET GIT_CREDENTIALS, COMMENT;

ALTER GIT REPOSITORY my_repo SET TAG cost_center = 'data', env = 'prod';

ALTER GIT REPOSITORY my_repo UNSET TAG cost_center, env;

SHOW GIT REPOSITORIES;

SHOW GIT REPOSITORIES LIKE 'my%' IN SCHEMA my_db.my_schema;

SHOW GIT BRANCHES IN my_repo;

SHOW GIT BRANCHES LIKE 'main%' IN GIT REPOSITORY my_db.my_schema.my_repo;

SHOW GIT TAGS IN GIT REPOSITORY my_repo;

DESCRIBE GIT REPOSITORY my_repo;

DESC GIT REPOSITORY my_db.my_schema.my_repo;

DROP GIT REPOSITORY my_repo;

DROP GIT REPOSITORY IF EXISTS my_db.my_schema.my_repo;

GRANT READ ON GIT REPOSITORY my_repo TO ROLE my_role;

GRANT WRITE ON GIT REPOSITORY my_db.my_schema.my_repo TO ROLE my_role;

GRANT READ ON ALL GIT REPOSITORIES IN SCHEMA my_db.my_schema TO ROLE my_role;

GRANT READ ON FUTURE GIT REPOSITORIES IN DATABASE my_db TO ROLE my_role;

REVOKE READ ON GIT REPOSITORY my_repo FROM ROLE my_role;
