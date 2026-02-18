-- OAUTH2 type
CREATE SECRET my_oauth_secret
  TYPE = OAUTH2
  API_AUTHENTICATION = my_integration
  OAUTH_SCOPES = ('scope1', 'scope2')
  OAUTH_REFRESH_TOKEN = 'my_token'
  OAUTH_REFRESH_TOKEN_EXPIRY_TIME = '2025-01-01 00:00:00';

-- PASSWORD type
CREATE OR REPLACE SECRET my_password_secret
  TYPE = PASSWORD
  USERNAME = 'my_user'
  PASSWORD = 'my_password'
  COMMENT = 'password secret';

-- GENERIC_STRING type
CREATE SECRET IF NOT EXISTS my_generic_secret
  TYPE = GENERIC_STRING
  SECRET_STRING = 'my_secret_value';
