CREATE CATALOG INTEGRATION glue_int
  CATALOG_SOURCE = GLUE
  TABLE_FORMAT = ICEBERG
  GLUE_AWS_ROLE_ARN = 'arn'
  GLUE_CATALOG_ID = 'catalog_id'
  GLUE_REGION = 'region.us.east'
  CATALOG_NAMESPACE = 'namespace'
  ENABLED = true
  REFRESH_INTERVAL_SECONDS = 10
  COMMENT = 'comment';


CREATE OR REPLACE CATALOG INTEGRATION IF NOT EXISTS glue_int_2
  CATALOG_SOURCE = GLUE
  TABLE_FORMAT = ICEBERG
  GLUE_AWS_ROLE_ARN = 'arn'
  GLUE_CATALOG_ID = 'catalog_id'
  ENABLED = false;



CREATE CATALOG INTEGRATION object_storage_int_iceberg
  CATALOG_SOURCE = OBJECT_STORE
  TABLE_FORMAT = ICEBERG
  ENABLED = TRUE
  REFRESH_INTERVAL_SECONDS = 10
  COMMENT = '<string_literal>';

CREATE CATALOG INTEGRATION object_storage_int_iceberg
  CATALOG_SOURCE = OBJECT_STORE
  TABLE_FORMAT = DELTA
  ENABLED = FALSE;



CREATE OR REPLACE CATALOG INTEGRATION snow_open_catalog_int
  CATALOG_SOURCE = POLARIS
  TABLE_FORMAT = ICEBERG
  CATALOG_NAMESPACE = 'my_catalog_namespace'
  REST_CONFIG = (
    CATALOG_URI = 'https://my_org_name-my_snowflake_open_catalog_account_name.snowflakecomputing.com/polaris/api/catalog'
    CATALOG_NAME = 'my_catalog_name'
  )
  REST_AUTHENTICATION = (
    TYPE = OAUTH
    OAUTH_CLIENT_ID = 'my_client_id'
    OAUTH_CLIENT_SECRET = 'my_client_secret'
    OAUTH_ALLOWED_SCOPES = ('PRINCIPAL_ROLE:ALL')
  )
  ENABLED = TRUE;


CREATE OR REPLACE CATALOG INTEGRATION snow_open_catalog_2_int
  CATALOG_SOURCE = POLARIS
  TABLE_FORMAT = ICEBERG
  CATALOG_NAMESPACE = 'my_catalog_namespace'
  REST_CONFIG = (
    CATALOG_URI = 'https://my_org_name-my_snowflake_open_catalog_account_name.snowflakecomputing.com/polaris/api/catalog'
    CATALOG_NAME = 'my_catalog_name'
  )
  REST_AUTHENTICATION = (
    TYPE = OAUTH
    OAUTH_CLIENT_ID = 'my_client_id'
    OAUTH_CLIENT_SECRET = 'my_client_secret'
    OAUTH_ALLOWED_SCOPES = ('PRINCIPAL_ROLE:ALL', 'OTHER_ROLE:ALL')
  )
  ENABLED = TRUE;



CREATE CATALOG INTEGRATION apache_iceberg_rest_tabular_int
  CATALOG_SOURCE = ICEBERG_REST
  TABLE_FORMAT = ICEBERG
  CATALOG_NAMESPACE = '<namespace>'
  REST_CONFIG = (
    CATALOG_URI = 'https://api.tabular.io/ws'
    CATALOG_NAME = '<tabular_warehouse_name>'
  )
  REST_AUTHENTICATION = (
    TYPE = OAUTH
    OAUTH_TOKEN_URI = 'https://api.tabular.io/ws/v1/oauth/tokens'
    OAUTH_CLIENT_ID = '<oauth_client_id>'
    OAUTH_CLIENT_SECRET = '<oauth_client_secret>'
    OAUTH_ALLOWED_SCOPES = ('catalog')
  )
  ENABLED = TRUE
  REFRESH_INTERVAL_SECONDS = 10
  COMMENT = '<string_literal>';

CREATE CATALOG INTEGRATION apache_iceberg_rest_sigv4_int
  CATALOG_SOURCE = ICEBERG_REST
  TABLE_FORMAT = ICEBERG
  CATALOG_NAMESPACE = '<namespace>'
  REST_CONFIG = (
    CATALOG_URI = 'https://glue.us-west-2.amazonaws.com/iceberg'
    CATALOG_API_TYPE = AWS_GLUE
    CATALOG_NAME = '123456789012'
  )
  REST_AUTHENTICATION = (
    TYPE = SIGV4
    SIGV4_IAM_ROLE = 'arn:aws:iam::123456789012:role/my-role'
    SIGV4_SIGNING_REGION = 'us-west-2'
  )
  ENABLED = TRUE
  REFRESH_INTERVAL_SECONDS = 10
  COMMENT = '<string_literal>';

CREATE CATALOG INTEGRATION apache_iceberg_rest_bearer_int
  CATALOG_SOURCE = ICEBERG_REST
  TABLE_FORMAT = ICEBERG
  CATALOG_NAMESPACE = '<namespace>'
  REST_CONFIG = (
    CATALOG_URI = 'https://glue.us-west-2.amazonaws.com/iceberg'
    CATALOG_API_TYPE = AWS_GLUE
    CATALOG_NAME = '123456789012'
  )
  REST_AUTHENTICATION = (
    TYPE = BEARER
    BEARER_TOKEN = 'bearer-token'
  )
  ENABLED = TRUE
  REFRESH_INTERVAL_SECONDS = 10
  COMMENT = '<string_literal>';

