-- Set value list
ALTER NETWORK RULE my_rule SET VALUE_LIST = ('192.168.1.0/24', '10.0.0.0/8');

-- Set comment
ALTER NETWORK RULE my_rule SET COMMENT = 'updated rule';

-- Unset comment
ALTER NETWORK RULE my_rule UNSET COMMENT;
