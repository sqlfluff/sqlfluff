-- ALTER SECRET for OAUTH2
ALTER SECRET my_oauth_secret SET
  OAUTH_REFRESH_TOKEN = 'new_token'
  OAUTH_REFRESH_TOKEN_EXPIRY_TIME = '2026-01-01 00:00:00';

-- ALTER SECRET for PASSWORD
ALTER SECRET my_password_secret SET
  USERNAME = 'new_user'
  PASSWORD = 'new_password';

-- ALTER SECRET for GENERIC_STRING
ALTER SECRET my_generic_secret SET
  SECRET_STRING = 'new_value'
  COMMENT = 'updated secret';
