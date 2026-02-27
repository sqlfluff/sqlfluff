-- Basic failover group
CREATE FAILOVER GROUP my_fg
  OBJECT_TYPES = DATABASES, ROLES
  ALLOWED_DATABASES = db1, db2
  ALLOWED_ACCOUNTS = my_org.my_account1
  REPLICATION_SCHEDULE = '10 MINUTE';

-- Failover group with shares and integration types
CREATE FAILOVER GROUP IF NOT EXISTS my_fg
  OBJECT_TYPES = DATABASES, SHARES, INTEGRATIONS
  ALLOWED_DATABASES = db1
  ALLOWED_SHARES = share1, share2
  ALLOWED_INTEGRATION_TYPES = SECURITY_INTEGRATIONS
  ALLOWED_ACCOUNTS = my_org.my_account1, my_org.my_account2
  IGNORE_EDITION_CHECK
  REPLICATION_SCHEDULE = 'USING CRON 0 0 * * * America/Los_Angeles';

-- Failover group as replica
CREATE FAILOVER GROUP my_fg_replica
  AS REPLICA OF my_org.my_source_fg;
