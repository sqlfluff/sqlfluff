"""Tests specific to the exasol_fs dialect."""
import pytest

from sqlfluff.core.dialects.dialect_exasol_fs import (
    CreateAdapterScriptStatementSegment,
    CreateFunctionStatementSegment,
    CreateScriptingLuaScriptStatementSegment,
    CreateUDFScriptStatementSegment,
)

TEST_DIALECT = "exasol_fs"


# Develop test to check specific elements against specific grammars.
@pytest.mark.parametrize(
    "segmentref,raw",
    [
        (
            "FunctionAssignmentSegment",
            "res := CASE WHEN input_variable < 0 THEN 0 ELSE input_variable END;",
        ),
        ("FunctionAssignmentSegment", "res := 'Hello World';"),
        ("FunctionAssignmentSegment", 'res := CALL.ANOTHER_FUNCTION("MY VALUE");'),
        (
            "FunctionIfBranchSegment",
            """
            IF input_variable = 0 THEN
                res := NULL;
            ELSEIF input_variable = 1 THEN
                res := 'HELLO';
            ELSEIF input_variable = 2 THEN
                res := 'HALLO';
            ELSE
                res := input_variable;
            END IF;
            """,
        ),
        (
            "FunctionForLoopSegment",
            """
            FOR cnt := 1 TO input_variable
            DO
                res := res*2;
            END FOR;
            """,
        ),
        (
            "FunctionForLoopSegment",
            """
            FOR cnt IN 1..10 LOOP
                res := res*2;
            END LOOP;
            """,
        ),
        (
            "FunctionWhileLoopSegment",
            """
            WHILE cnt <= input_variable
            DO
                res := res*2;
                cnt := cnt+1;
            END WHILE;
            """,
        ),
        ("WalrusOperatorSegment", ":="),
        ("VariableNameSegment", "var1"),
    ],
)
def test_dialect_exasol_fs_specific_segment_parses(
    segmentref, raw, caplog, dialect_specific_segment_parses
):
    """Test exasol_fs specific segments."""
    dialect_specific_segment_parses(TEST_DIALECT, segmentref, raw, caplog)


@pytest.mark.parametrize(
    "segment_cls,raw,stmt_count",
    [
        (
            CreateFunctionStatementSegment,
            """
            CREATE OR REPLACE FUNCTION percentage ( fraction DECIMAL,
                                                    entirety DECIMAL)
            RETURN VARCHAR(10)
            IS
                res DECIMAL;
            BEGIN
                res := (100*fraction)/entirety;
                RETURN res || ' %';
            END percentage;
            /
            ----
            CREATE FUNCTION hello () RETURN VARCHAR(10)
            AS
                res DECIMAL;
            BEGIN
                res := hello.world("no");
                RETURN 'HELLO';
            END hello; /
            """,
            2,
        ),
        (
            CreateScriptingLuaScriptStatementSegment,
            """
            CREATE OR REPLACE LUA SCRIPT aschema.hello AS
                return 'HELLO'
            /
            """,
            1,
        ),
        (
            CreateScriptingLuaScriptStatementSegment,
            """
            CREATE OR REPLACE LUA SCRIPT aschema.hello() AS
                return 'HELLO'
            /
            """,
            1,
        ),
        (
            CreateScriptingLuaScriptStatementSegment,
            """
            CREATE SCRIPT insert_low_high (param1, param2, param3) AS
                import('function_lib') -- accessing external function
                lowest, highest = function_lib.min_max(param1, param2, param3)
                query([[INSERT INTO t VALUES (:x, :y)]], {x=lowest, y=highest})
            /
            """,
            1,
        ),
        (
            CreateUDFScriptStatementSegment,
            """
            CREATE LUA SCALAR SCRIPT my_average
                (a DOUBLE, b DOUBLE ORDER BY 1 desc)
            RETURNS DOUBLE AS
                function run(ctx)
                    if ctx.a == nil or ctx.b==nil
                        then return NULL
                    end
                    return (ctx.a+ctx.b)/2
                end
            /
            """,
            1,
        ),
        (
            CreateUDFScriptStatementSegment,
            """
            CREATE LUA SCALAR SCRIPT map_words(w varchar(10000))
            EMITS (words varchar(100)) AS
            function run(ctx)
                local word = ctx.w
                if (word ~= null)
                then
                    for i in unicode.utf8.gmatch(word,'([%w%p]+)')
                    do
                        ctx.emit(i)
                    end
                end
            end
            /
             """,
            1,
        ),
        (
            CreateUDFScriptStatementSegment,
            """
            CREATE OR REPLACE PYTHON3 SCALAR SCRIPT LIB.MYLIB() RETURNS INT AS
            def helloWorld():
              return "Hello Python3 World!"
            /
             """,
            1,
        ),
        (
            CreateUDFScriptStatementSegment,
            """
            CREATE OR REPLACE PYTHON SCALAR SCRIPT TEST.MYHELLOWORLD() RETURNS VARCHAR(2000) AS
            l = exa.import_script('LIB.MYLIB')
            def run(ctx):
                return l.helloWorld()
            /
             """,
            1,
        ),
        (
            CreateUDFScriptStatementSegment,
            """
            CREATE OR REPLACE JAVA SCALAR SCRIPT LIB.MYLIB() RETURNS VARCHAR(2000) AS
            class MYLIB {
                static String helloWorld(){
                       return "Hello Java World!";
                }
            }
            /
            """,
            1,
        ),
        (
            CreateAdapterScriptStatementSegment,
            """
            CREATE JAVA ADAPTER SCRIPT my_script AS
            %jar hive_jdbc_adapter.jar;
            /
            """,
            1,
        ),
    ],
)
def test_exasol_scripts_functions(
    segment_cls, raw, stmt_count, validate_dialect_specific_statements
):
    """Test exasol specific scripts and functions with parse."""
    validate_dialect_specific_statements(TEST_DIALECT, segment_cls, raw, stmt_count)
