"""The Test file for the linter class."""

import pytest
from typing import List
from unittest.mock import patch

from sqlfluff.core import Linter, FluffConfig
from sqlfluff.core.errors import SQLBaseError, SQLLintError, SQLParseError
from sqlfluff.core.linter import LintingResult, NoQaDirective
import sqlfluff.core.linter as linter
from sqlfluff.core.parser import FilePositionMarker


class DummyLintError(SQLBaseError):
    """Fake lint error used by tests, similar to SQLLintError."""

    def __init__(self, pos: FilePositionMarker, code: str = "L001"):
        self.pos = pos
        self._code = code
        super(DummyLintError, self).__init__()


def normalise_paths(paths):
    """Test normalising paths.

    NB Paths on difference platforms might look different, so this
    makes them comparable.
    """
    return {pth.replace("/", ".").replace("\\", ".") for pth in paths}


def test__linter__path_from_paths__dir():
    """Test extracting paths from directories."""
    lntr = Linter()
    paths = lntr.paths_from_path("test/fixtures/lexer")
    assert normalise_paths(paths) == {
        "test.fixtures.lexer.block_comment.sql",
        "test.fixtures.lexer.inline_comment.sql",
        "test.fixtures.lexer.basic.sql",
    }


def test__linter__path_from_paths__default():
    """Test .sql files are found by default."""
    lntr = Linter()
    paths = normalise_paths(lntr.paths_from_path("test/fixtures/linter"))
    assert "test.fixtures.linter.passing.sql" in paths
    assert "test.fixtures.linter.discovery_file.txt" not in paths


def test__linter__path_from_paths__exts():
    """Test configuration of file discovery."""
    lntr = Linter(config=FluffConfig(overrides={"sql_file_exts": ".txt"}))
    paths = normalise_paths(lntr.paths_from_path("test/fixtures/linter"))
    assert "test.fixtures.linter.passing.sql" not in paths
    assert "test.fixtures.linter.discovery_file.txt" in paths


def test__linter__path_from_paths__file():
    """Test extracting paths from a file path."""
    lntr = Linter()
    paths = lntr.paths_from_path("test/fixtures/linter/indentation_errors.sql")
    assert normalise_paths(paths) == {"test.fixtures.linter.indentation_errors.sql"}


def test__linter__path_from_paths__not_exist():
    """Test extracting paths from a file path."""
    lntr = Linter()
    with pytest.raises(IOError):
        lntr.paths_from_path("asflekjfhsakuefhse")


def test__linter__path_from_paths__not_exist_ignore():
    """Test extracting paths from a file path."""
    lntr = Linter()
    paths = lntr.paths_from_path("asflekjfhsakuefhse", ignore_non_existent_files=True)
    assert len(paths) == 0


def test__linter__path_from_paths__explicit_ignore():
    """Test ignoring files that were passed explicitly."""
    lntr = Linter()
    paths = lntr.paths_from_path(
        "test/fixtures/linter/sqlfluffignore/path_a/query_a.sql",
        ignore_non_existent_files=True,
        ignore_files=True,
        working_path="test/fixtures/linter/sqlfluffignore/",
    )
    assert len(paths) == 0


def test__linter__path_from_paths__dot():
    """Test extracting paths from a dot."""
    lntr = Linter()
    paths = lntr.paths_from_path(".")
    # Use set theory to check that we get AT LEAST these files
    assert normalise_paths(paths) >= {
        "test.fixtures.lexer.block_comment.sql",
        "test.fixtures.lexer.inline_comment.sql",
        "test.fixtures.lexer.basic.sql",
    }


@pytest.mark.parametrize(
    "path",
    [
        "test/fixtures/linter/sqlfluffignore",
        "test/fixtures/linter/sqlfluffignore/",
        "test/fixtures/linter/sqlfluffignore/.",
    ],
)
def test__linter__path_from_paths__ignore(path):
    """Test extracting paths from a dot."""
    lntr = Linter()
    paths = lntr.paths_from_path(path)
    # We should only get query_b, because of the sqlfluffignore files.
    assert normalise_paths(paths) == {
        "test.fixtures.linter.sqlfluffignore.path_b.query_b.sql"
    }


@pytest.mark.parametrize(
    "path",
    [
        "test/fixtures/linter/indentation_errors.sql",
        "test/fixtures/linter/whitespace_errors.sql",
    ],
)
def test__linter__lint_string_vs_file(path):
    """Test the linter finds the same things on strings and files."""
    with open(path, "r") as f:
        sql_str = f.read()
    lntr = Linter()
    assert (
        lntr.lint_string(sql_str).check_tuples() == lntr.lint_path(path).check_tuples()
    )


@pytest.mark.parametrize(
    "rules,num_violations", [(None, 7), ("L010", 2), (("L001", "L009", "L031"), 2)]
)
def test__linter__get_violations_filter_rules(rules, num_violations):
    """Test filtering violations by which rules were violated."""
    lntr = Linter()
    lint_result = lntr.lint_string("select a, b FROM tbl c order BY d")

    assert len(lint_result.get_violations(rules=rules)) == num_violations


def test__linter__linting_result__sum_dicts():
    """Test the summing of dictionaries in the linter."""
    lr = LintingResult()
    i = {}
    a = dict(a=3, b=123, f=876.321)
    b = dict(a=19, b=321.0, g=23478)
    r = dict(a=22, b=444.0, f=876.321, g=23478)
    assert lr.sum_dicts(a, b) == r
    # Check the identity too
    assert lr.sum_dicts(r, i) == r


def test__linter__linting_result__combine_dicts():
    """Test the combination of dictionaries in the linter."""
    lr = LintingResult()
    a = dict(a=3, b=123, f=876.321)
    b = dict(h=19, i=321.0, j=23478)
    r = dict(z=22)
    assert lr.combine_dicts(a, b, r) == dict(
        a=3, b=123, f=876.321, h=19, i=321.0, j=23478, z=22
    )


@pytest.mark.parametrize("by_path,result_type", [(False, list), (True, dict)])
def test__linter__linting_result_check_tuples_by_path(by_path, result_type):
    """Test that a LintingResult can partition violations by the source files."""
    lntr = Linter()
    result = lntr.lint_paths(
        [
            "test/fixtures/linter/comma_errors.sql",
            "test/fixtures/linter/whitespace_errors.sql",
        ]
    )
    check_tuples = result.check_tuples(by_path=by_path)
    isinstance(check_tuples, result_type)


def test__linter__linting_result_get_violations():
    """Test that we can get violations from a LintingResult."""
    lntr = Linter()
    result = lntr.lint_paths(
        [
            "test/fixtures/linter/comma_errors.sql",
            "test/fixtures/linter/whitespace_errors.sql",
        ]
    )

    all([type(v) == SQLLintError for v in result.get_violations()])


@patch("sqlfluff.core.linter.linter_logger")
@patch("sqlfluff.core.Linter.lint_string")
def test__linter__linting_unexpected_error_handled_gracefully(
    patched_lint_string, patched_logger
):
    """Test that an unexpected internal error is handled gracefully and returns the issue-surfacing file."""
    patched_lint_string.side_effect = Exception("Something unexpected happened")
    lntr = Linter()
    lntr.lint_paths(("test/fixtures/linter/passing.sql",))
    assert (
        "Unable to lint test/fixtures/linter/passing.sql due to an internal error."
        # NB: Replace is to handle windows-style paths.
        in patched_logger.warning.call_args[0][0].replace("\\", "/")
        and "Exception: Something unexpected happened"
        in patched_logger.warning.call_args[0][0]
    )


def test__linter__raises_malformed_noqa():
    """A badly formatted noqa gets raised as a parsing error."""
    lntr = Linter()
    result = lntr.lint_string_wrapped("select 1 --noqa missing semicolon")

    with pytest.raises(SQLParseError):
        result.check_tuples()


def test__linter__empty_file():
    """Test linter behaves nicely with an empty string."""
    lntr = Linter()
    # Make sure no exceptions raised and no violations found in empty file.
    parsed = lntr.parse_string("")
    assert not parsed.violations


@pytest.mark.parametrize(
    "ignore_templated_areas,check_tuples",
    [
        (True, [("L006", 3, 27), ("L006", 3, 28)]),
        (
            False,
            [
                ("L006", 3, 17),
                ("L006", 3, 18),
                ("L006", 3, 19),
                ("L006", 3, 20),
                ("L006", 3, 27),
                ("L006", 3, 28),
            ],
        ),
    ],
)
def test__linter__mask_templated_violations(ignore_templated_areas, check_tuples):
    """Test linter masks files properly around templated content."""
    lntr = Linter(
        config=FluffConfig(
            overrides={
                "rules": "L006",
                "ignore_templated_areas": ignore_templated_areas,
            }
        )
    )
    linted = lntr.lint_path(path="test/fixtures/templater/jinja_h_macros/jinja.sql")
    assert linted.check_tuples() == check_tuples


@pytest.mark.parametrize(
    "input,expected",
    [
        ("", None),
        ("noqa", NoQaDirective(0, None, None)),
        ("noqa?", SQLParseError),
        ("noqa:", NoQaDirective(0, None, None)),
        ("noqa:L001,L002", NoQaDirective(0, ("L001", "L002"), None)),
        ("noqa: enable=L005", NoQaDirective(0, ("L005",), "enable")),
        ("noqa: disable=L010", NoQaDirective(0, ("L010",), "disable")),
        ("noqa: disable=all", NoQaDirective(0, None, "disable")),
        ("noqa: disable", SQLParseError),
    ],
)
def test_parse_noqa(input, expected):
    """Test correct of "noqa" comments."""
    result = Linter.parse_noqa(input, 0)
    if not isinstance(expected, type):
        assert result == expected
    else:
        # With exceptions, just check the type, not the contents.
        assert isinstance(result, expected)


@pytest.mark.parametrize(
    "noqa,violations,expected",
    [
        [
            [],
            [DummyLintError(FilePositionMarker(statement_index=None, line_no=1))],
            [
                0,
            ],
        ],
        [
            [dict(comment="noqa: L001", line_no=1)],
            [DummyLintError(FilePositionMarker(statement_index=None, line_no=1))],
            [],
        ],
        [
            [dict(comment="noqa: L001", line_no=2)],
            [DummyLintError(FilePositionMarker(statement_index=None, line_no=1))],
            [0],
        ],
        [
            [dict(comment="noqa: L002", line_no=1)],
            [DummyLintError(FilePositionMarker(statement_index=None, line_no=1))],
            [0],
        ],
        [
            [dict(comment="noqa: enable=L001", line_no=1)],
            [DummyLintError(FilePositionMarker(statement_index=None, line_no=1))],
            [0],
        ],
        [
            [dict(comment="noqa: disable=L001", line_no=1)],
            [DummyLintError(FilePositionMarker(statement_index=None, line_no=1))],
            [],
        ],
        [
            [
                dict(comment="noqa: disable=L001", line_no=2),
                dict(comment="noqa: enable=L001", line_no=4),
            ],
            [DummyLintError(FilePositionMarker(statement_index=None, line_no=1))],
            [0],
        ],
        [
            [
                dict(comment="noqa: disable=L001", line_no=2),
                dict(comment="noqa: enable=L001", line_no=4),
            ],
            [DummyLintError(FilePositionMarker(statement_index=None, line_no=2))],
            [],
        ],
        [
            [
                dict(comment="noqa: disable=L001", line_no=2),
                dict(comment="noqa: enable=L001", line_no=4),
            ],
            [DummyLintError(FilePositionMarker(statement_index=None, line_no=3))],
            [],
        ],
        [
            [
                dict(comment="noqa: disable=L001", line_no=2),
                dict(comment="noqa: enable=L001", line_no=4),
            ],
            [DummyLintError(FilePositionMarker(statement_index=None, line_no=4))],
            [0],
        ],
        [
            [
                dict(comment="noqa: disable=all", line_no=2),
                dict(comment="noqa: enable=all", line_no=4),
            ],
            [DummyLintError(FilePositionMarker(statement_index=None, line_no=1))],
            [0],
        ],
        [
            [
                dict(comment="noqa: disable=all", line_no=2),
                dict(comment="noqa: enable=all", line_no=4),
            ],
            [DummyLintError(FilePositionMarker(statement_index=None, line_no=2))],
            [],
        ],
        [
            [
                dict(comment="noqa: disable=all", line_no=2),
                dict(comment="noqa: enable=all", line_no=4),
            ],
            [DummyLintError(FilePositionMarker(statement_index=None, line_no=3))],
            [],
        ],
        [
            [
                dict(comment="noqa: disable=all", line_no=2),
                dict(comment="noqa: enable=all", line_no=4),
            ],
            [DummyLintError(FilePositionMarker(statement_index=None, line_no=4))],
            [0],
        ],
        [
            [
                dict(comment="noqa: disable=L001", line_no=2),
                dict(comment="noqa: enable=all", line_no=4),
            ],
            [
                DummyLintError(
                    FilePositionMarker(statement_index=None, line_no=2), code="L001"
                ),
                DummyLintError(
                    FilePositionMarker(statement_index=None, line_no=2), code="L002"
                ),
                DummyLintError(
                    FilePositionMarker(statement_index=None, line_no=4), code="L001"
                ),
                DummyLintError(
                    FilePositionMarker(statement_index=None, line_no=4), code="L002"
                ),
            ],
            [1, 2, 3],
        ],
        [
            [
                dict(comment="noqa: disable=all", line_no=2),
                dict(comment="noqa: enable=L001", line_no=4),
            ],
            [
                DummyLintError(
                    FilePositionMarker(statement_index=None, line_no=2), code="L001"
                ),
                DummyLintError(
                    FilePositionMarker(statement_index=None, line_no=2), code="L002"
                ),
                DummyLintError(
                    FilePositionMarker(statement_index=None, line_no=4), code="L001"
                ),
                DummyLintError(
                    FilePositionMarker(statement_index=None, line_no=4), code="L002"
                ),
            ],
            [2],
        ],
    ],
    ids=[
        "1_violation_no_ignore",
        "1_violation_ignore_specific_line",
        "1_violation_ignore_different_specific_line",
        "1_violation_ignore_different_specific_rule",
        "1_violation_ignore_enable_this_range",
        "1_violation_ignore_disable_this_range",
        "1_violation_line_1_ignore_disable_specific_2_3",
        "1_violation_line_2_ignore_disable_specific_2_3",
        "1_violation_line_3_ignore_disable_specific_2_3",
        "1_violation_line_4_ignore_disable_specific_2_3",
        "1_violation_line_1_ignore_disable_all_2_3",
        "1_violation_line_2_ignore_disable_all_2_3",
        "1_violation_line_3_ignore_disable_all_2_3",
        "1_violation_line_4_ignore_disable_all_2_3",
        "4_violations_two_types_disable_specific_enable_all",
        "4_violations_two_types_disable_all_enable_specific",
    ],
)
def test_linted_file_ignore_masked_violations(
    noqa: dict, violations: List[SQLBaseError], expected
):
    """Test that _ignore_masked_violations() correctly filters violations."""
    ignore_mask = [Linter.parse_noqa(**c) for c in noqa]
    lf = linter.LintedFile(
        path="",
        violations=violations,
        time_dict={},
        tree=None,
        ignore_mask=ignore_mask,
        templated_file=linter.TemplatedFile(""),
    )
    result = lf._ignore_masked_violations(violations)
    expected_violations = [v for i, v in enumerate(violations) if i in expected]
    assert expected_violations == result


def test_linter_noqa():
    """Test "noqa" feature at the higher "Linter" level."""
    lntr = Linter(
        config=FluffConfig(
            overrides={
                "rules": "L012",
            }
        )
    )
    sql = """
    SELECT
        col_a a,
        col_b b, --noqa: disable=L012
        col_c c,
        col_d d, --noqa: enable=L012
        col_e e,
        col_f f,
        col_g g,  --noqa
        col_h h,
        col_i i, --noqa:L012
        col_j j,
        col_k k, --noqa:L013
        col_l l,
        col_m m,
        col_n n, --noqa: disable=all
        col_o o,
        col_p p --noqa: enable=all
    FROM foo
        """
    result = lntr.lint_string(sql)
    violations = result.get_violations()
    assert {3, 6, 7, 8, 10, 12, 13, 14, 15, 18} == {v.line_no() for v in violations}
