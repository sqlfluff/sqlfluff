-- Fetch updates
ALTER GIT REPOSITORY my_repo FETCH;

-- Set properties
ALTER GIT REPOSITORY IF EXISTS my_repo SET
  GIT_CREDENTIALS = new_secret
  API_INTEGRATION = new_integration
  COMMENT = 'updated repo';

-- Unset properties
ALTER GIT REPOSITORY my_repo UNSET GIT_CREDENTIALS, COMMENT;

-- Set tag
ALTER GIT REPOSITORY my_repo SET
  TAG my_tag = 'value';

-- Unset tag
ALTER GIT REPOSITORY my_repo UNSET TAG my_tag;
