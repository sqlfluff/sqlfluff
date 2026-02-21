-- Basic replication group
CREATE REPLICATION GROUP my_rg
  OBJECT_TYPES = DATABASES, ROLES
  ALLOWED_DATABASES = db1, db2
  ALLOWED_ACCOUNTS = my_org.my_account1;

-- Replication group as replica
CREATE REPLICATION GROUP my_rg_replica
  AS REPLICA OF my_org.my_source_rg;
