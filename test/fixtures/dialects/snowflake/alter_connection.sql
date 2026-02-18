-- Enable failover
ALTER CONNECTION my_connection ENABLE FAILOVER TO ACCOUNTS my_org.my_account1, my_org.my_account2;

-- Disable failover
ALTER CONNECTION my_connection DISABLE FAILOVER TO ACCOUNTS my_org.my_account1;

-- Promote to primary
ALTER CONNECTION my_connection PRIMARY;

-- Set comment
ALTER CONNECTION my_connection COMMENT = 'updated connection';

-- Unset comment
ALTER CONNECTION my_connection UNSET COMMENT;
