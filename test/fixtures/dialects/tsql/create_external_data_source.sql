CREATE EXTERNAL DATA SOURCE MyOracleServer
WITH (
  LOCATION = 'oracle://145.145.145.145:1521',
  CREDENTIAL = OracleProxyAccount,
  PUSHDOWN = ON
);

CREATE EXTERNAL DATA SOURCE [OracleSalesSrvr]
WITH (
  LOCATION = 'oracle://145.145.145.145:1521',
  CONNECTION_OPTIONS = 'ImpersonateUser=%CURRENT_USER',
  CREDENTIAL = [OracleProxyCredential]
);

CREATE EXTERNAL DATA SOURCE [external_data_source_name]
WITH (
  LOCATION = N'oracle://XE',
  CREDENTIAL = [OracleCredentialTest],
  CONNECTION_OPTIONS = N'TNSNamesFile=C:\Temp\tnsnames.ora;ServerName=XE'
);
