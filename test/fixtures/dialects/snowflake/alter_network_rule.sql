ALTER NETWORK RULE my_rule SET VALUE_LIST = ('192.168.1.0/24');

ALTER NETWORK RULE IF EXISTS my_rule SET
    VALUE_LIST = ('example.com:443', 'example.com:80')
    COMMENT = 'egress to example.com';

ALTER NETWORK RULE my_rule UNSET COMMENT;

ALTER NETWORK RULE my_rule UNSET VALUE_LIST;
