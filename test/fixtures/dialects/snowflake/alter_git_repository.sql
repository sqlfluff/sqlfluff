ALTER GIT REPOSITORY snowflake_extensions FETCH;

ALTER GIT REPOSITORY IF EXISTS my_db.my_schema.my_repo FETCH;

ALTER GIT REPOSITORY my_repo SET
    GIT_CREDENTIALS = new_git_secret
    API_INTEGRATION = other_git_api_integration
    COMMENT = 'rotated credentials';

ALTER GIT REPOSITORY my_repo SET TAG cost_center = 'data_eng', env = 'prod';

ALTER GIT REPOSITORY my_repo UNSET TAG cost_center, env;

ALTER GIT REPOSITORY my_repo UNSET GIT_CREDENTIALS;

ALTER GIT REPOSITORY my_repo UNSET GIT_CREDENTIALS, COMMENT;
