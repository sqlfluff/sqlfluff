ALTER USER my_service_user SET
  WORKLOAD_IDENTITY = (
    TYPE = GCP
    SUBJECT = '117253954487186628372'
  );

ALTER USER my_service_user SET WORKLOAD_IDENTITY = (
  TYPE = AWS
  ARN = 'arn:aws:iam::123456789012:role/my-role'
);

ALTER USER my_service_user SET WORKLOAD_IDENTITY = (
  TYPE = AZURE
  ISSUER = 'https://login.microsoftonline.com/00000000-0000-0000-0000-000000000000/v2.0'
  SUBJECT = '00000000-0000-0000-0000-000000000000'
);

ALTER USER my_service_user SET WORKLOAD_IDENTITY = (
  TYPE = OIDC
  ISSUER = 'https://oidc.example.com'
  SUBJECT = 'system:serviceaccount:my-namespace:my-service-account'
  OIDC_AUDIENCE_LIST = ('https://example.snowflakecomputing.com', 'my-audience')
);

ALTER USER my_service_user UNSET WORKLOAD_IDENTITY;

CREATE USER IF NOT EXISTS my_service_user
  DEFAULT_ROLE = my_role
  WORKLOAD_IDENTITY = (
    TYPE = GCP
    SUBJECT = '117253954487186628372'
  )
  COMMENT = 'service user authenticating via workload identity federation';
