CREATE OR REPLACE SECRET mysecret
    TYPE = OAUTH2
    API_AUTHENTICATION = mysecurityintegration
    OAUTH_SCOPES = ('useraccount')
    COMMENT = 'secret for the service now connector';

CREATE SECRET IF NOT EXISTS my_db.my_schema.oauth_secret
    TYPE = OAUTH2
    API_AUTHENTICATION = my_integration
    OAUTH_SCOPES = ('api.read', 'api.write');

CREATE SECRET service_now_creds_oauth_code
    TYPE = OAUTH2
    OAUTH_REFRESH_TOKEN = '34n;vods4nQsdg09wee4qnfvadH'
    OAUTH_REFRESH_TOKEN_EXPIRY_TIME = '2022-01-06 20:00:00'
    API_AUTHENTICATION = sn_oauth;

CREATE SECRET aws_secret
    TYPE = CLOUD_PROVIDER_TOKEN
    API_AUTHENTICATION = 'my_aws_iam_integration'
    ENABLED = TRUE;

CREATE SECRET service_now_creds_pw
    TYPE = PASSWORD
    USERNAME = 'jsmith1'
    PASSWORD = 'W3dr@fg*7B1c4j';

CREATE OR REPLACE SECRET my_api_token
    TYPE = GENERIC_STRING
    SECRET_STRING = 'abc123'
    COMMENT = 'token for the weather api';

CREATE SECRET my_key
    TYPE = SYMMETRIC_KEY
    ALGORITHM = GENERIC;

CREATE OR REPLACE SECRET my_secret
    TYPE = GENERIC_STRING
    SECRET_STRING = :my_secret_string
    COMMENT = 'secret from a bind variable';

CREATE SECRET my_password_secret
    TYPE = PASSWORD
    USERNAME = :my_username
    PASSWORD = :my_password;
