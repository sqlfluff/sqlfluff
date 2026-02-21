-- Set with OAuth
ALTER CATALOG INTEGRATION my_catalog SET
  REST_AUTHENTICATION = (
    OAUTH_CLIENT_SECRET = 'my_secret'
  )
  REFRESH_INTERVAL_SECONDS = 60
  COMMENT = 'updated catalog';

-- Set with bearer token
ALTER CATALOG INTEGRATION IF EXISTS my_catalog SET
  REST_AUTHENTICATION = (
    BEARER_TOKEN = 'my_token'
  );
