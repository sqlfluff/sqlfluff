"""Tests specific to the exasol_fs dialect."""
import pytest

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
        ("FunctionVariableNameSegment", "my_function"),
        ("FunctionVariableNameSegment", "my_function2021"),
        ("FunctionVariableNameSegment", "func"),
        ("DoubleDotSegment", ".."),
        (
            "CreateFunctionStatementSegment",
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
            """,
        ),
        (
            "CreateFunctionStatementSegment",
            """
            CREATE FUNCTION hello () RETURN VARCHAR(10)
            AS
                res DECIMAL;
            BEGIN
                RETURN 'HELLO';
            END hello; /
            """,
        ),
        (
            "CreateScriptingScriptStatementSegment",
            """
            CREATE OR REPLACE SCRIPT schema.hello AS
                return 'HELLO'
            /
            """,
        ),
        (
            "CreateScriptingScriptStatementSegment",
            """
            CREATE SCRIPT insert_low_high (param1, param2, param3) AS
                import('function_lib') -- accessing external function
                lowest, highest = function_lib.min_max(param1, param2, param3)
                query([[INSERT INTO t VALUES (:x, :y)]], {x=lowest, y=highest})
            /
            """,
        ),
        (
            "CreateUDFScriptStatementSegment",
            """
            CREATE LUA SCALAR SCRIPT my_average
                (a DOUBLE, b DOUBLE)
            RETURNS DOUBLE AS
                function run(ctx)
                    if ctx.a == nil or ctx.b==nil
                        then return NULL
                    end
                    return (ctx.a+ctx.b)/2
                end
            /
            """,
        ),
        (
            "CreateUDFScriptStatementSegment",
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
        ),
        (
            "CreateUDFScriptStatementSegment",
            """
            CREATE OR REPLACE PYTHON3 SCALAR SCRIPT LIB.MYLIB() RETURNS INT AS
            def helloWorld():
              return "Hello Python3 World!"
            /
            """,
        ),
        (
            "CreateUDFScriptStatementSegment",
            """
            CREATE OR REPLACE PYTHON SCALAR SCRIPT TEST.MYHELLOWORLD() RETURNS VARCHAR(2000) AS
            l = exa.import_script('LIB.MYLIB')
            def run(ctx):
                return l.helloWorld()
            /
            """,
        ),
        (
            "CreateUDFScriptStatementSegment",
            """
            CREATE OR REPLACE JAVA SCALAR SCRIPT LIB.MYLIB() RETURNS VARCHAR(2000) AS
            class MYLIB {
                static String helloWorld(){
                       return "Hello Java World!";
                }
            }
            /
            """,
        ),
        (
            "CreateAdapterScriptStatementSegment",
            """
            CREATE JAVA ADAPTER SCRIPT my_script AS
            %jar hive_jdbc_adapter.jar;
            /
            """,
        ),
    ],
)
def test__dialect__exasol_fs_specific_segment_parses(
    segmentref, raw, caplog, dialect_specific_segment_parses
):
    """Test exasol_fs specific segments."""
    dialect_specific_segment_parses(TEST_DIALECT, segmentref, raw, caplog)
