CREATE OR REPLACE API INTEGRATION aws
  API_PROVIDER = aws_api_gateway
  API_AWS_ROLE_ARN = 'arn:aws:iam::123456789012:role/my_cloud_account_role'
  API_ALLOWED_PREFIXES = ('https://xyz.execute-api.us-west-2.amazonaws.com/production')
  ENABLED = TRUE;

CREATE OR REPLACE API INTEGRATION aws2
  API_PROVIDER = aws_private_api_gateway
  API_AWS_ROLE_ARN = 'arn:aws:iam::123456789012:role/my_cloud_account_role'
  API_ALLOWED_PREFIXES = ('https://xyz.execute-api.us-west-2.amazonaws.com/production')
  API_KEY='123'
  ENABLED = FALSE
  COMMENT='blabla';

CREATE OR REPLACE API INTEGRATION aws3
  API_PROVIDER = aws_gov_api_gateway
  API_AWS_ROLE_ARN = 'arn:aws:iam::123456789012:role/my_cloud_account_role'
  API_ALLOWED_PREFIXES = ('https://xyz.execute-api.us-west-2.amazonaws.com/production')
  ENABLED = TRUE;

CREATE OR REPLACE API INTEGRATION aws4
API_PROVIDER = aws_gov_private_api_gateway
API_AWS_ROLE_ARN = 'arn:aws:iam::123456789012:role/my_cloud_account_role'
API_ALLOWED_PREFIXES = ('https://xyz.execute-api.us-west-2.amazonaws.com/production')
ENABLED = TRUE;

CREATE OR REPLACE API INTEGRATION azure
API_PROVIDER = azure_api_management
AZURE_TENANT_ID = '<tenant_id>'
AZURE_AD_APPLICATION_ID = '<azure_application_id>'
API_KEY = '<api_key>'
API_ALLOWED_PREFIXES = ( 'go' )
API_BLOCKED_PREFIXES = ( 'do_not_go' )
ENABLED = TRUE;

CREATE OR REPLACE API INTEGRATION google
API_PROVIDER = google_api_gateway
GOOGLE_AUDIENCE = '<google_audience_claim>'
API_ALLOWED_PREFIXES = ( 'go' )
ENABLED = TRUE;

CREATE OR REPLACE API INTEGRATION git
API_PROVIDER = git_https_api
GOOGLE_AUDIENCE = '<google_audience_claim>'
API_ALLOWED_PREFIXES = ( 'go' )
ALLOWED_AUTHENTICATION_SECRETS = ( 'pedo mellon a minno' )
;

CREATE OR REPLACE API INTEGRATION git2
API_PROVIDER = git_https_api
GOOGLE_AUDIENCE = '<google_audience_claim>'
ALLOWED_AUTHENTICATION_SECRETS = ( all )
;


CREATE OR REPLACE API INTEGRATION git3
API_PROVIDER = git_https_api
GOOGLE_AUDIENCE = '<google_audience_claim>'
API_ALLOWED_PREFIXES = ( 'go' )
ALLOWED_AUTHENTICATION_SECRETS = ( none )
;

CREATE OR REPLACE API INTEGRATION git2
API_PROVIDER = git_https_api
GOOGLE_AUDIENCE = '<google_audience_claim>'
ALLOWED_AUTHENTICATION_SECRETS = ('pedo','mellon a','minno')
;
