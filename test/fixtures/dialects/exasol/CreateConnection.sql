CREATE CONNECTION ftp_connection
TO 'ftp://192.168.1.1/'
USER 'agent_007'
IDENTIFIED BY 'secret';
----
CREATE CONNECTION exa_connection TO '192.168.6.11..14:8563';
----
CREATE CONNECTION ora_connection TO '(DESCRIPTION =
    (ADDRESS = (PROTOCOL = TCP)(HOST = 192.168.6.54)(PORT = 1521))
    (CONNECT_DATA = (SERVER = DEDICATED)(SERVICE_NAME = orcl)))';
----
CREATE CONNECTION jdbc_connection_1
        TO 'jdbc:mysql://192.168.6.1/my_db';
----
CREATE CONNECTION jdbc_connection_2
        TO 'jdbc:postgresql://192.168.6.2:5432/my_db?stringtype=unspecified';
