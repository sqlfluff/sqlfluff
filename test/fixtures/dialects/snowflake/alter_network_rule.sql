ALTER NETWORK RULE cloud_network SET VALUE_LIST = ('47.88.25.32/27', '47.88.25.64/27');

ALTER NETWORK RULE IF EXISTS my_db.my_schema.external_access_rule SET
    VALUE_LIST = ('example.com', 'example.com:443')
    COMMENT = 'egress to example.com';

ALTER NETWORK RULE cloud_network UNSET VALUE_LIST;

ALTER NETWORK RULE IF EXISTS cloud_network UNSET COMMENT;
