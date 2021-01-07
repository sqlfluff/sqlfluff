"""Tests specific to the exasol dialect."""
import pytest

from sqlfluff.core import Linter
from sqlfluff.core.dialects.dialect_exasol import (
    CreateSchemaStatementSegment,
    CreateVirtualSchemaStatementSegment,
    AlterSchemaStatementSegment,
    AlterVirtualSchemaStatementSegment,
    DropSchemaStatementSegment,
    CreateViewStatementSegment,
    CreateTableStatementSegment,
    AlterTableColumnSegment,
    AlterTableConstraintSegment,
    AlterTableDistributePartitionSegment,
    DropTableStatementSegment,
    DropCascadeStatementSegment,
    DropStatementSegment,
    DropCascadeRestrictStatementSegment,
    RenameStatementSegment,
    CommentStatementSegment,
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
            CREATE VIEW my_view as select x from t;
            CREATE OR REPLACE FORCE VIEW my_view as select y from t;
            CREATE OR REPLACE VIEW my_view (col_1 COMMENT IS 'something important',col2) as select max(y) from t;
            """,
            3,
        ),
        (
            CreateTableStatementSegment,
            """
            CREATE TABLE myschema.t1
            (   a VARCHAR(20),
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
    ],
)
# def test__dialect__exasol_specific_segment_parses(
#     segmentref, raw, caplog, dialect_specific_segment_parses
# ):
#     """Test exasol_fs specific segments."""
#     dialect_specific_segment_parses(TEST_DIALECT, segmentref, raw, caplog)
def test_exasol_queries(segment_cls, raw, stmt_count, caplog):
    """Test snowflake specific queries parse."""
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
