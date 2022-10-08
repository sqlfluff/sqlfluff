create network policy mypolicy1 allowed_ip_list=('192.168.1.0/24')
                                blocked_ip_list=('192.168.1.99');

CREATE OR REPLACE NETWORK POLICY TEST_NW_POLICY
ALLOWED_IP_LIST=('xx.xxx.xxx.xx/xx','xx.xxx.xxx.xx/xx')  COMMENT='NW Policy' ;
