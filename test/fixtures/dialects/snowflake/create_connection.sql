-- Basic connection
CREATE CONNECTION my_connection;

-- Connection with comment
CREATE CONNECTION IF NOT EXISTS my_connection
  COMMENT = 'primary connection';

-- Connection as replica
CREATE CONNECTION my_replica_connection
  AS REPLICA OF my_org.my_account.my_connection;
