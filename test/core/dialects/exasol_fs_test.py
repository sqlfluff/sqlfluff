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
    ],
)
def test__dialect__exasol_fs_specific_segment_parses(
    segmentref, raw, caplog, dialect_specific_segment_parses
):
    """Test exasol_fs specific segments."""
    dialect_specific_segment_parses(TEST_DIALECT, segmentref, raw, caplog)
