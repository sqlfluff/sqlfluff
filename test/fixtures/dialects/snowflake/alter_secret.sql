ALTER SECRET service_now_creds_pw SET COMMENT = 'production secret for servicenow';

ALTER SECRET IF EXISTS my_oauth_secret SET OAUTH_SCOPES = ('api.read', 'api.write');

ALTER SECRET my_oauth_code_secret SET
    OAUTH_REFRESH_TOKEN = 'new_token'
    OAUTH_REFRESH_TOKEN_EXPIRY_TIME = '2027-01-01 00:00:00';

ALTER SECRET aws_secret SET API_AUTHENTICATION = 'my_other_integration';

ALTER SECRET my_basic_secret SET USERNAME = 'svc_user' PASSWORD = 'new_password';

ALTER SECRET my_db.my_schema.my_api_secret SET SECRET_STRING = 'new_api_token';

ALTER SECRET my_secret SET SECRET_STRING = :my_secret_string;
