EXPORT tab1 INTO CSV
AT 'ftp://192.168.1.1/' USER 'agent_007' IDENTIFIED BY 'secret'
FILE 'tab1.csv'
COLUMN SEPARATOR = ';'
ENCODING = 'Latin1'
WITH COLUMN NAMES;
----
EXPORT tab1 INTO CSV
AT 'ftp://192.168.1.1/' USER 'agent_007' IDENTIFIED BY 'secret'
FILE 'tab1.csv'
(
    1 FORMAT='DD.MM.YYYY',
    2..3 DELIMIT=NEVER
)
COLUMN SEPARATOR = ';'
ENCODING = 'Latin1'
WITH COLUMN NAMES;
----
EXPORT (SELECT * FROM T WHERE id=3295) INTO FBV
AT my_connection
FILE 't1.fbv' FILE 't2.fbv'
REPLACE;
----
EXPORT (SELECT * FROM my_view) INTO EXA
AT '192.168.6.11..14:8563'
USER 'my_user' IDENTIFIED BY 'my_secret'
TABLE my_schema.my_table
CREATED BY 'CREATE TABLE my_table(order_id INT, price DEC(18,2))';
----
EXPORT tab1 INTO JDBC DRIVER='MSSQL'
AT 'jdbc:sqlserver://dbserver;databaseName=testdb'
USER 'agent_007' IDENTIFIED BY 'secret'
TABLE my_schema.tab1;
----
EXPORT tab1 INTO CSV
AT 'http://HadoopNode:50070/webhdfs/v1/tmp'
FILE 'file.csv?op=CREATE&user.name=user';
----
EXPORT tab1 INTO CSV
AT 'https://testbucket.s3.amazonaws.com'
USER '<AccessKeyID>' IDENTIFIED BY '<SecretAccessKey>'
FILE 'file.csv';
----
EXPORT tab1 INTO SCRIPT etl.export_hcat_table
WITH HCAT_DB = 'default'
        HCAT_TABLE = 'my_hcat_table'
        HCAT_ADDRESS = 'hcatalog-server:50111'
        HDFS_USER = 'hdfs';
----
EXPORT tab1 INTO LOCAL CSV FILE '/tmp/my_table.csv'
COLUMN SEPARATOR = ';';
----
