-- Basic git repository
CREATE GIT REPOSITORY my_repo
  ORIGIN = 'https://github.com/my-org/my-repo.git'
  API_INTEGRATION = my_git_integration;

-- Full git repository
CREATE OR REPLACE GIT REPOSITORY IF NOT EXISTS my_db.my_schema.my_repo
  ORIGIN = 'https://github.com/my-org/my-repo.git'
  API_INTEGRATION = my_git_integration
  GIT_CREDENTIALS = my_secret
  COMMENT = 'main repo'
  TAG (team = 'data');
