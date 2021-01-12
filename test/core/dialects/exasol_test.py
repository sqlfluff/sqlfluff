"""Tests specific to the exasol dialect."""
import pytest
from sqlfluff.core import Linter
from sqlfluff.core.dialects.dialect_exasol import (
    AlterConnectionSegment,
    AlterSchemaStatementSegment,
    AlterTableColumnSegment,
    AlterTableConstraintSegment,
    AlterTableDistributePartitionSegment,
    AlterVirtualSchemaStatementSegment,
    CommentStatementSegment,
    CreateConnectionSegment,
    CreateRoleSegment,
    CreateSchemaStatementSegment,
    CreateTableStatementSegment,
    CreateViewStatementSegment,
    CreateVirtualSchemaStatementSegment,
    DeleteStatementSegment,
    DropCascadeRestrictStatementSegment,
    DropCascadeStatementSegment,
    DropSchemaStatementSegment,
    DropStatementSegment,
    DropTableStatementSegment,
    AccessStatementSegment,
    ImportStatementSegment,
    InsertStatementSegment,
    MergeStatementSegment,
    RenameStatementSegment,
    TruncateStatmentSegement,
    UpdateStatementSegment,
    ExportStatementSegment,
    CreateUserSegment,
    AlterUserSegment,
    SelectStatementSegment,
)

TEST_DIALECT = "exasol"

# TODO: Test Grammar
# Develop test to check specific elements against specific grammars.


@pytest.mark.parametrize(
    "segment_cls,raw,stmt_count",
    [
        (
            DropCascadeStatementSegment,
            """DROP USER test_user1;DROP USER test_user2 CASCADE;
            DROP ROLE myrole;""",
            3,
        ),
        (
            DropStatementSegment,
            """
            DROP CONNECTION my_connection;
            DROP CONNECTION IF EXISTS my_connection;
            DROP SCRIPT my_script;
            DROP ADAPTER SCRIPT IF EXISTS my_schema.ADAPTER_SCRIPT;
            """,
            4,
        ),
        (
            DropCascadeRestrictStatementSegment,
            """
            DROP VIEW IF EXISTS my_view RESTRICT;
            DROP FUNCTION my_function CASCADE;
            """,
            2,
        ),
        (
            CreateSchemaStatementSegment,
            """
            CREATE SCHEMA TEST;
            CREATE SCHEMA IF NOT EXISTS my_schema;
            """,
            2,
        ),
        (
            CreateVirtualSchemaStatementSegment,
            """
            CREATE VIRTUAL SCHEMA hive
            USING adapter.jdbc_adapter
            WITH
                SQL_DIALECT	     = 'HIVE'
                CONNECTION_STRING   = 'jdbc:hive2://localhost:10000/default'
                SCHEMA_NAME	     = 'default'
                USERNAME	     = 'hive-usr'
                PASSWORD	     = 'hive-pwd'
            """,
            1,
        ),
        (
            AlterSchemaStatementSegment,
            """
            ALTER SCHEMA s1 CHANGE OWNER user1;
            ALTER SCHEMA s1 CHANGE OWNER role1;
            ALTER SCHEMA s1 SET RAW_SIZE_LIMIT = 128*1024*1024;
            """,
            3,
        ),
        (
            AlterVirtualSchemaStatementSegment,
            """
            ALTER VIRTUAL SCHEMA s2
              SET CONNECTION_STRING = 'jdbc:hive2://localhost:10000/default';
            ALTER VIRTUAL SCHEMA s2 REFRESH;
            """,
            2,
        ),
        (
            DropSchemaStatementSegment,
            """
            DROP FORCE SCHEMA my_schema;
            DROP SCHEMA IF EXISTS my_schema;
            DROP SCHEMA my_schema CASCADE;
            DROP VIRTUAL SCHEMA my_virtual_schema;
            """,
            4,
        ),
        (
            CreateViewStatementSegment,
            """
            CREATE VIEW my_view as select x from t COMMENT IS 'nice view';
            CREATE VIEW my_view (col1 ) as (select x from t);
            CREATE OR REPLACE FORCE VIEW my_view as select y from t;
            CREATE OR REPLACE VIEW my_view (col_1 COMMENT IS 'something important',col2) as select max(y) from t;
            """,
            4,
        ),
        (
            CreateTableStatementSegment,
            """
            CREATE TABLE myschema.t1
            (   a VARCHAR(20) UTF8,
                b DECIMAL(24,4) NOT NULL COMMENT IS 'The B column',
                c DECIMAL DEFAULT 122,
                d DOUBLE,
                e TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                f BOOL);
            CREATE TABLE "MYSCHEMA"."T2" AS SELECT * FROM t1 WITH NO DATA;
            CREATE OR REPLACE TABLE "MYSCHEMA".T2 AS SELECT a,b,c+1 AS c FROM t1;
            CREATE TABLE t3 AS SELECT count(*) AS my_count FROM t1 WITH NO DATA;
            CREATE TABLE t4 LIKE t1;
            CREATE TABLE t5 (   id int IDENTITY PRIMARY KEY DISABLE,
                                LIKE t1 INCLUDING DEFAULTS,
                                g DOUBLE,
                                DISTRIBUTE BY a,b
                                );
            CREATE TABLE t6 (   order_id INT,
                                order_price DOUBLE,
                                order_date DATE,
                                country VARCHAR(40),
                                CONSTRAINT t6_pk PRIMARY KEY (order_id),
                                DISTRIBUTE BY order_id, PARTITION BY order_date)
            COMMENT IS 'a great table';
            CREATE OR REPLACE TABLE t8 (ref_id int CONSTRAINT FK_T5 REFERENCES t5 (id) DISABLE, b VARCHAR(20));
            """,
            8,
        ),
        (
            DropTableStatementSegment,
            """
            DROP TABLE my_table;
            DROP TABLE IF EXISTS "MY_SCHEMA"."MY_TABLE" CASCADE CASCADE CONSTRAINTS;
            """,
            2,
        ),
        (
            AlterTableDistributePartitionSegment,
            """
            ALTER TABLE my_table DROP DISTRIBUTION KEYS;
            ALTER TABLE my_table DROP DISTRIBUTION AND PARTITION KEYS;
            ALTER TABLE my_table DISTRIBUTE BY shop_id, PARTITION BY order_date;
            ALTER TABLE my_table PARTITION BY order_date, DISTRIBUTE BY shop_id, branch_no;
            ALTER TABLE my_table PARTITION BY order_date;
            ALTER TABLE my_table DISTRIBUTE BY shop_id, branch_no;
            """,
            6,
        ),
        (
            AlterTableConstraintSegment,
            """
            ALTER TABLE t1 ADD CONSTRAINT my_primary_key PRIMARY KEY (a);
            ALTER TABLE t2 ADD CONSTRAINT my_foreign_key FOREIGN KEY (x) REFERENCES t1;
            ALTER TABLE t2 MODIFY CONSTRAINT my_foreign_key DISABLE;
            ALTER TABLE t2 RENAME CONSTRAINT my_foreign_key TO my_fk;
            ALTER TABLE t2 DROP CONSTRAINT my_fk;
            """,
            5,
        ),
        (
            AlterTableColumnSegment,
            """
            ALTER TABLE t ADD COLUMN IF NOT EXISTS new_dec DECIMAL(18,0);
            ALTER TABLE t ADD (new_char CHAR(10) DEFAULT 'some text');
            ALTER TABLE myschema.t DROP COLUMN i;
            ALTER TABLE t DROP j;
            ALTER TABLE t MODIFY (i DECIMAL(10,2));
            ALTER TABLE t MODIFY (j VARCHAR(5) DEFAULT 'text');
            ALTER TABLE t MODIFY k INTEGER IDENTITY(1000);
            ALTER TABLE t RENAME COLUMN i TO j;
            ALTER TABLE t ALTER COLUMN v SET DEFAULT CURRENT_USER;
            ALTER TABLE "SCHEMA"."TABLE" ALTER COLUMN v DROP DEFAULT;
            ALTER TABLE t ALTER COLUMN id SET IDENTITY 1000;
            ALTER TABLE t ALTER COLUMN id DROP IDENTITY;
            """,
            12,
        ),
        (
            RenameStatementSegment,
            """
            RENAME SCHEMA s1 TO s2;
            RENAME TABLE t1 TO t2;
            RENAME s2.t3 TO t4;
            RENAME s2.t3 TO s2.t4;
            """,
            4,
        ),
        (
            CommentStatementSegment,
            """
            COMMENT ON SCHEMA s1 IS 'My first schema';
            COMMENT ON TABLE a_schema.t1 IS 'My first table';
            COMMENT ON t1 (id IS 'Identity column', zip IS 'Zip code');
            COMMENT ON SCRIPT script1 IS 'My first script';
            COMMENT ON CONSUMER GROUP admin_group IS 'VERY important!!!';
            """,
            5,
        ),
        (
            InsertStatementSegment,
            """
            INSERT INTO t (n1, n2, t1) VALUES (1, 2.34, 'abc');
            INSERT INTO t VALUES (2, 1.56, 'ghi'), (3, 5.92, 'pqr');
            INSERT INTO t VALUES (4, DEFAULT, 'xyz');
            INSERT INTO t (i,k) SELECT * FROM u;
            INSERT INTO t (i) SELECT max(j) FROM u;
            INSERT INTO t DEFAULT VALUES;
            """,
            6,
        ),
        (
            UpdateStatementSegment,
            """
            UPDATE staff SET salary=salary*1.1 WHERE name='SMITH';
            ----
            UPDATE staff AS U SET U.salary=U.salary/1.95583, U.currency='EUR'
            WHERE U.currency='DM';
            ----
            UPDATE staff AS U
            SET U.salary=V.salary, U.currency=V.currency
            FROM staff AS U, staff_updates AS V
            WHERE U.name=V.name;
            ----
            UPDATE order_pos
            SET stocks=stocks*10
            PREFERRING HIGH (order_date) PARTITION BY (shop_id, order_id);
            """,
            4,
        ),
        (
            MergeStatementSegment,
            """
            MERGE INTO staff T
            USING changes U
            ON T.name = U.name
            WHEN MATCHED THEN UPDATE SET T.salary = U.salary,
                                         T.lastChange = CURRENT_DATE
                              WHERE T.salary < U.salary
            WHEN NOT MATCHED THEN INSERT VALUES (U.name,U.salary,CURRENT_DATE);
            ----
            MERGE INTO staff T
            USING (SELECT name FROM X) U
            ON T.name = U.name
            WHEN MATCHED THEN DELETE;
            ---
            """,
            2,
        ),
        (
            DeleteStatementSegment,
            """
            DELETE FROM staff WHERE name='SMITH';
            DELETE * FROM staff;
            DELETE FROM staff PREFERRING (LOW change_date) PARTITION BY emp_no;
            """,
            3,
        ),
        (
            TruncateStatmentSegement,
            """
            TRUNCATE TABLE test;
            """,
            1,
        ),
        (
            ImportStatementSegment,
            """
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
            """,
            11,
        ),
        (
            ExportStatementSegment,
            """
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
            """,
            9,
        ),
        (
            CreateUserSegment,
            """
            CREATE USER user_1 IDENTIFIED BY "h12_xhz";
            CREATE USER user_2 IDENTIFIED AT LDAP
            AS 'cn=user_2,dc=authorization,dc=exasol,dc=com';
            CREATE USER user_3 IDENTIFIED BY KERBEROS PRINCIPAL '<user>@<realm>';
            """,
            3,
        ),
        (
            AlterUserSegment,
            """
            ALTER USER user_1 IDENTIFIED BY "h22_xhz" REPLACE "h12_xhz";
            ALTER USER user_1 IDENTIFIED BY "h12_xhz";
            ALTER USER user_2 IDENTIFIED AT LDAP
            AS 'cn=user_2,dc=authorization,dc=exasol,dc=com';
            ALTER USER user_3 PASSWORD_EXPIRY_POLICY = '42 days';
            ALTER USER user_4 PASSWORD EXPIRE;
            ALTER USER user_5 RESET FAILED LOGIN ATTEMPTS;
            """,
            6,
        ),
        (CreateRoleSegment, "CREATE ROLE test_role;", 1),
        (
            CreateConnectionSegment,
            """
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
            """,
            5,
        ),
        (
            AlterConnectionSegment,
            "ALTER CONNECTION exa_connection TO '192.168.6.11..14:8564';",
            1,
        ),
        (
            AccessStatementSegment,
            """
            -- System privileges
            GRANT CREATE SCHEMA TO role1;
            GRANT SELECT ANY TABLE TO user1 WITH ADMIN OPTION;
            -- Object privileges
            GRANT INSERT ON my_schema.my_table TO user1, role2;
            GRANT SELECT ON VIEW my_schema.my_view TO user1;
            -- Access on my_view for all users
            GRANT SELECT ON my_schema.my_view TO PUBLIC;
            -- Roles
            GRANT role1 TO user1, user2 WITH ADMIN OPTION;
            GRANT role2 TO role1;
            -- Impersonation
            GRANT IMPERSONATION ON user2 TO user1;
            -- Connection
            GRANT CONNECTION my_connection TO user1;
            -- Access to connection details for certain script
            GRANT ACCESS ON CONNECTION my_connection
            FOR SCRIPT script1 TO user1;
            """,
            10,
        ),
        (
            AccessStatementSegment,
            """
            -- System privilege
            REVOKE CREATE SCHEMA FROM role1,user3;
            -- Object privileges
            REVOKE SELECT, INSERT ON my_schema.my_table FROM user1, role2;
            REVOKE ALL PRIVILEGES ON VIEW my_schema.my_view FROM PUBLIC;
            -- Role
            REVOKE role1 FROM user1, user2;
            -- Impersonation
            REVOKE IMPERSONATION ON user2 FROM user1;
            -- Connections
            REVOKE CONNECTION my_connection FROM user1;
            """,
            6,
        ),
        (
            SelectStatementSegment,
            """
            SELECT last_name, employee_id id, manager_id mgr_id,
               CONNECT_BY_ISLEAF leaf, LEVEL,
               LPAD(' ', 2*LEVEL-1)||SYS_CONNECT_BY_PATH(last_name, '/') "PATH"
            FROM employees
            CONNECT BY PRIOR employee_id = manager_id AND dept_no = dno
            START WITH last_name = 'Clark'
            ORDER BY employee_id;
            ----
            SELECT store, SUM(price) AS volume FROM sales GROUP BY store ORDER BY store DESC;
            ----
            SELECT name, SUM(price) AS volume FROM customers JOIN sales USING (c_id)
            GROUP BY name ORDER BY name;
            ----
            WITH tmp_view AS
                (SELECT name, price, store FROM customers, sales
                 WHERE customers.c_id=sales.c_id)
            SELECT sum(price) AS volume, name, store FROM tmp_view
            GROUP BY GROUPING SETS (name,store,());
            ----
            SELECT * FROM (IMPORT INTO (v VARCHAR(1))
            FROM EXA AT my_connection TABLE sys.dual);
            """,
            6,
        ),
    ],
)
def test_exasol_queries(segment_cls, raw, stmt_count, caplog):
    """Test exasol specific queries parse."""
    lnt = Linter(dialect=TEST_DIALECT)
    parsed = lnt.parse_string(raw)
    assert len(parsed.violations) == 0

    # Find any unparsable statements
    typs = parsed.tree.type_set()
    assert "unparsable" not in typs

    # Find the expected type in the parsed segment
    child_segments = [seg for seg in parsed.tree.recursive_crawl(segment_cls.type)]
    assert len(child_segments) == stmt_count

    # Check if all child segments are the correct type
    for c in child_segments:
        assert isinstance(c, segment_cls)
