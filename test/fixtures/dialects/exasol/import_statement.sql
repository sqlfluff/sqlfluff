IMPORT INTO table_3 (col1, col2, col4) FROM ORA
AT my_oracle
USER 'agent_008' IDENTIFIED BY 'secret'
STATEMENT ' SELECT * FROM orders WHERE order_state=''OK'' '
ERRORS INTO error_table (CURRENT_TIMESTAMP)
REJECT LIMIT 10
;
----
IMPORT INTO table_3 (col1, col2, col4) FROM ORA
AT my_oracle
USER 'agent_008' IDENTIFIED BY 'secret'
TABLE a.tab (c1,c2,c3)
ERRORS INTO error_table (CURRENT_TIMESTAMP) REJECT LIMIT 10
;
----
IMPORT INTO table_1 FROM CSV
AT 'http://192.168.1.1:8080/' USER 'agent_007' IDENTIFIED BY 'secret'
FILE 'tab1_part1.csv' FILE 'tab1_part2.csv'
(
    1 FORMAT='DD-MM-YYYY',
    2..4 FORMAT='YYYYMMDD'
)
COLUMN SEPARATOR = ';'
SKIP = 5;
----
IMPORT INTO table_2 FROM FBV
AT my_fileserver
FILE 'tab2_part1.fbv'
(
    SIZE=8 PADDING='+' ALIGN=RIGHT,
    SIZE=4,
    SIZE=8,
    SIZE=32 FORMAT='DD-MM-YYYY'
)
TRIM
;
----
IMPORT INTO table_7 FROM SCRIPT etl.import_hcat_table
AT my_oracle USER 'agent_008' IDENTIFIED BY 'secret'
WITH   HCAT_DB = 'default'
        HCAT_TABLE = 'my_hcat_table'
        HCAT_ADDRESS = 'hcatalog-server:50111'
        HDFS_USER = 'hdfs';
----
IMPORT INTO table_4
FROM JDBC DRIVER='MSSQL'
AT 'jdbc:sqlserver://dbserver;databaseName=testdb'
USER 'agent_008' IDENTIFIED BY 'secret'
STATEMENT ' SELECT * FROM orders WHERE order_state=''OK'' ';
----
IMPORT INTO table_5 FROM CSV
AT 'http://HadoopNode:50070/webhdfs/v1/tmp'
FILE 'file.csv?op=OPEN&user.name=user';
----
IMPORT INTO table_6 FROM EXA
AT my_exasol
TABLE MY_SCHEMA.MY_TABLE;
----
IMPORT INTO (LIKE CAT) FROM EXA
AT my_exa_conn
STATEMENT ' SELECT OBJECT_NAME, OBJECT_TYPE FROM EXA_USER_OBJECTS WHERE OBJECT_TYPE IN (''TABLE'', ''VIEW'') ';
----
IMPORT INTO table_8
FROM LOCAL CSV FILE '~/my_table.csv'
COLUMN SEPARATOR = ';' SKIP = 5;
----
IMPORT INTO table_1 FROM CSV
AT 'https://<bucketname>.s3-<region>.amazonaws.com/'
USER '<AccessKeyID>' IDENTIFIED BY '<SecretAccessKey>'
FILE 'file.csv';
