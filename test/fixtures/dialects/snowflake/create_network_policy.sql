create network policy mypolicy1 allowed_ip_list=('192.168.1.0/24')
                                blocked_ip_list=('192.168.1.99');

CREATE OR REPLACE NETWORK POLICY TEST_NW_POLICY
ALLOWED_IP_LIST=('xx.xxx.xxx.xx/xx','xx.xxx.xxx.xx/xx')  COMMENT='NW Policy' ;

CREATE NETWORK POLICY np
  ALLOWED_NETWORK_RULE_LIST = ('blabla','blabla2','blabla3')
  COMMENT='comment'
  ;

CREATE NETWORK POLICY np
  BLOCKED_NETWORK_RULE_LIST = ('blabla','blabla2','blabla3')
  COMMENT='comment'
  ;
