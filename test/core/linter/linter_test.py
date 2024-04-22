"""Tests for the Linter class and LintingResult class."""

import logging
import os
from unittest.mock import patch

import pytest

from sqlfluff.cli.formatters import OutputStreamFormatter
from sqlfluff.cli.outputstream import make_output_stream
from sqlfluff.core import FluffConfig, Linter
from sqlfluff.core.errors import (
    SQLBaseError,
    SQLFluffSkipFile,
    SQLFluffUserError,
    SQLLexError,
    SQLLintError,
)
from sqlfluff.core.linter import LintingResult, runner
from sqlfluff.core.linter.runner import get_runner
from sqlfluff.utils.testing.logging import fluff_log_catcher


class DummyLintError(SQLBaseError):
    """Fake lint error used by tests, similar to SQLLintError."""

    def __init__(self, line_no: int, code: str = "LT01"):
        self._code = code
        super().__init__(line_no=line_no)


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
    assert "test.fixtures.linter.passing_cap_extension.SQL" in paths
    assert "test.fixtures.linter.discovery_file.txt" not in paths


def test__linter__path_from_paths__exts():
    """Test configuration of file discovery."""
    lntr = Linter(
        config=FluffConfig(overrides={"sql_file_exts": ".txt", "dialect": "ansi"})
    )
    paths = normalise_paths(lntr.paths_from_path("test/fixtures/linter"))
    assert "test.fixtures.linter.passing.sql" not in paths
    assert "test.fixtures.linter.passing_cap_extension.SQL" not in paths
    assert "test.fixtures.linter.discovery_file.txt" in paths


def test__linter__path_from_paths__file():
    """Test extracting paths from a file path."""
    lntr = Linter()
    paths = lntr.paths_from_path("test/fixtures/linter/indentation_errors.sql")
    assert normalise_paths(paths) == {"test.fixtures.linter.indentation_errors.sql"}


@pytest.mark.parametrize("filesize,raises_skip", [(0, False), (5, True), (2000, False)])
def test__linter__skip_large_bytes(filesize, raises_skip):
    """Test extracting paths from a file path."""
    config = FluffConfig(
        overrides={"large_file_skip_byte_limit": filesize, "dialect": "ansi"}
    )
    # First check the function directly
    if raises_skip:
        with pytest.raises(SQLFluffSkipFile) as excinfo:
            Linter.load_raw_file_and_config(
                "test/fixtures/linter/indentation_errors.sql", config
            )
        assert "Skipping" in str(excinfo.value)
        assert f"over the limit of {filesize}" in str(excinfo.value)
    # If NOT raises, then we'll catch the raise an error and the test will fail.

    # Then check that it either is or isn't linted appropriately via lint_paths.
    lntr = Linter(config)
    result = lntr.lint_paths(
        ("test/fixtures/linter/indentation_errors.sql",),
    )
    if raises_skip:
        assert not result.get_violations()
    else:
        assert result.get_violations()

    # Same again via parse_path, which is the other entry point.
    result = list(
        lntr.parse_path(
            "test/fixtures/linter/indentation_errors.sql",
        )
    )
    if raises_skip:
        assert not result
    else:
        assert result


def test__linter__path_from_paths__not_exist():
    """Test that the right errors are raise when a file doesn't exist."""
    lntr = Linter()
    with pytest.raises(SQLFluffUserError):
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


def test__linter__path_from_paths__sqlfluffignore_current_directory():
    """Test that .sqlfluffignore in the current directory is read when dir given."""
    oldcwd = os.getcwd()
    try:
        os.chdir("test/fixtures/linter/sqlfluffignore")
        lntr = Linter()
        paths = lntr.paths_from_path(
            "path_a/",
            ignore_non_existent_files=True,
            ignore_files=True,
            working_path="test/fixtures/linter/sqlfluffignore/",
        )
        assert len(paths) == 0
    finally:
        os.chdir(oldcwd)


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
    with open(path) as f:
        sql_str = f.read()
    lntr = Linter(dialect="ansi")
    assert (
        lntr.lint_string(sql_str).check_tuples() == lntr.lint_path(path).check_tuples()
    )


@pytest.mark.parametrize(
    "rules,num_violations", [(None, 6), ("CP01", 2), (("LT01", "LT12"), 1)]
)
def test__linter__get_violations_filter_rules(rules, num_violations):
    """Test filtering violations by which rules were violated."""
    lntr = Linter(dialect="ansi")
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


@pytest.mark.parametrize(
    "path,stats",
    [
        (
            "multifile_a",
            {
                "avg per file": 2.5,
                "clean": 0,
                "clean files": 0,
                "exit code": 111,
                "files": 2,
                "status": "FAIL",
                "unclean": 2,
                "unclean files": 2,
                "unclean rate": 1.0,
                "violations": 5,
            },
        ),
        (
            "multifile_b",
            {
                "avg per file": 2.0,
                "clean": 0,
                "clean files": 0,
                "exit code": 111,
                "files": 2,
                "status": "FAIL",
                "unclean": 2,
                "unclean files": 2,
                "unclean rate": 1.0,
                "violations": 4,
            },
        ),
    ],
)
def test__linter__linting_result_stats(path, stats):
    """Test that a LintingResult can get the right stats with multiple files.

    https://github.com/sqlfluff/sqlfluff/issues/5673
    """
    lntr = Linter()
    result = lntr.lint_paths([f"test/fixtures/linter/exit_codes/{path}"])
    # NOTE: We're using fake return codes for testing purposes.
    assert result.stats(111, 222) == stats


@pytest.mark.parametrize("processes", [1, 2])
def test__linter__linting_result_get_violations(processes):
    """Test that we can get violations from a LintingResult."""
    lntr = Linter()
    result = lntr.lint_paths(
        (
            "test/fixtures/linter/comma_errors.sql",
            "test/fixtures/linter/whitespace_errors.sql",
        ),
        processes=processes,
    )

    all([isinstance(v, SQLLintError) for v in result.get_violations()])


@pytest.mark.parametrize("force_error", [False, True])
def test__linter__linting_parallel_thread(force_error, monkeypatch):
    """Run linter in parallel mode using threads.

    Similar to test__linter__linting_result_get_violations but uses a thread
    pool of 1 worker to test parallel mode without subprocesses. This lets the
    tests capture code coverage information for the backend parts of parallel
    execution without having to jump through hoops.
    """
    if not force_error:
        monkeypatch.setattr(Linter, "allow_process_parallelism", False)

    else:

        def _create_pool(*args, **kwargs):
            class ErrorPool:
                def __enter__(self):
                    return self

                def __exit__(self, exc_type, exc_val, exc_tb):
                    pass

                def imap_unordered(self, *args, **kwargs):
                    yield runner.DelayedException(ValueError())

            return ErrorPool()

        monkeypatch.setattr(runner.MultiProcessRunner, "_create_pool", _create_pool)

    config = FluffConfig(overrides={"dialect": "ansi"})
    output_stream = make_output_stream(config, None, os.devnull)
    lntr = Linter(
        formatter=OutputStreamFormatter(output_stream, False, verbosity=0),
        dialect="ansi",
    )
    result = lntr.lint_paths(
        # NOTE: Lint more than one file to make sure we enabled the multithreaded
        # code path.
        (
            "test/fixtures/linter/comma_errors.sql",
            "test/fixtures/linter/whitespace_errors.sql",
        ),
        processes=2,
    )

    all([isinstance(v, SQLLintError) for v in result.get_violations()])


@patch("sqlfluff.core.linter.Linter.lint_rendered")
def test_lint_path_parallel_wrapper_exception(patched_lint):
    """Tests the error catching behavior of _lint_path_parallel_wrapper().

    Test on MultiThread runner because otherwise we have pickling issues.
    """
    patched_lint.side_effect = ValueError("Something unexpected happened")
    for result in runner.MultiThreadRunner(
        Linter(), FluffConfig(overrides={"dialect": "ansi"}), processes=1
    ).run(
        ["test/fixtures/linter/passing.sql"],
        fix=False,
    ):
        assert isinstance(result, runner.DelayedException)
        with pytest.raises(ValueError):
            result.reraise()


@pytest.mark.parametrize(
    "mock_cpu,in_processes,exp_processes",
    [
        # Make the mocked cpu count a really high value which is
        # unlikely to collide with the real value. We can then
        # test all the different combos.
        (512, 1, 1),
        (512, 0, 512),
        (512, -12, 500),
        (512, 5, 5),
        # Check that we can't go lower than 1 in a 1 cpu case
        (1, -1, 1),
    ],
)
@patch("multiprocessing.cpu_count")
def test__linter__get_runner_processes(
    patched_cpu_count, mock_cpu, in_processes, exp_processes
):
    """Test that get_runner handles processes correctly."""
    # Make the mocked cpu count a really high value which is
    # unlikely to collide with the real value.
    patched_cpu_count.return_value = mock_cpu
    _, return_processes = get_runner(
        linter=Linter(),
        config=FluffConfig(overrides={"dialect": "ansi"}),
        processes=in_processes,
    )
    assert return_processes == exp_processes


@patch("sqlfluff.core.linter.runner.linter_logger")
@patch("sqlfluff.core.linter.Linter.lint_rendered")
def test__linter__linting_unexpected_error_handled_gracefully(
    patched_lint, patched_logger
):
    """Test that an unexpected internal error returns the issue-surfacing file."""
    patched_lint.side_effect = Exception("Something unexpected happened")
    lntr = Linter()
    lntr.lint_paths(("test/fixtures/linter/passing.sql",))
    assert (
        "Unable to lint test/fixtures/linter/passing.sql due to an internal error."
        # NB: Replace is to handle windows-style paths.
        in patched_logger.warning.call_args[0][0].replace("\\", "/")
        and "Exception: Something unexpected happened"
        in patched_logger.warning.call_args[0][0]
    )


def test__linter__empty_file():
    """Test linter behaves nicely with an empty string."""
    lntr = Linter(dialect="ansi")
    # Make sure no exceptions raised and no violations found in empty file.
    parsed = lntr.parse_string("")
    assert not parsed.violations


@pytest.mark.parametrize(
    "ignore_templated_areas,check_tuples",
    [
        (True, [("LT01", 3, 39), ("LT01", 3, 40)]),
        (
            False,
            [
                # there are still two of each because LT01 checks
                # for both *before* and *after* the operator.
                # The deduplication filter makes sure there aren't 4.
                ("LT01", 3, 16),
                ("LT01", 3, 16),
                ("LT01", 3, 39),
                ("LT01", 3, 40),
            ],
        ),
    ],
)
def test__linter__mask_templated_violations(ignore_templated_areas, check_tuples):
    """Test linter masks files properly around templated content.

    NOTE: this also tests deduplication of fixes which have the same
    source position. i.e. `LintedFile.deduplicate_in_source_space()`.
    """
    lntr = Linter(
        config=FluffConfig(
            overrides={
                "rules": "L006",
                "ignore_templated_areas": ignore_templated_areas,
                "dialect": "ansi",
            }
        )
    )
    linted = lntr.lint_path(path="test/fixtures/templater/jinja_h_macros/jinja.sql")
    assert linted.check_tuples() == check_tuples


@pytest.mark.parametrize(
    "fname,config_encoding,lexerror",
    [
        (
            "test/fixtures/linter/encoding-utf-8.sql",
            "autodetect",
            False,
        ),
        (
            "test/fixtures/linter/encoding-utf-8-sig.sql",
            "autodetect",
            False,
        ),
        (
            "test/fixtures/linter/encoding-utf-8.sql",
            "utf-8",
            False,
        ),
        (
            "test/fixtures/linter/encoding-utf-8-sig.sql",
            "utf-8",
            True,
        ),
        (
            "test/fixtures/linter/encoding-utf-8.sql",
            "utf-8-sig",
            False,
        ),
        (
            "test/fixtures/linter/encoding-utf-8-sig.sql",
            "utf-8-sig",
            False,
        ),
    ],
)
def test__linter__encoding(fname, config_encoding, lexerror):
    """Test linter deals with files with different encoding."""
    lntr = Linter(
        config=FluffConfig(
            overrides={
                "rules": "LT01",
                "encoding": config_encoding,
                "dialect": "ansi",
            }
        )
    )
    result = lntr.lint_paths([fname])
    assert lexerror == (SQLLexError in [type(v) for v in result.get_violations()])


def test_delayed_exception():
    """Test that DelayedException stores and reraises a stored exception."""
    ve = ValueError()
    de = runner.DelayedException(ve)
    with pytest.raises(ValueError):
        de.reraise()


def test__attempt_to_change_templater_warning():
    """Test warning when changing templater in .sqlfluff file in subdirectory."""
    initial_config = FluffConfig(
        configs={"core": {"templater": "jinja", "dialect": "ansi"}}
    )
    lntr = Linter(config=initial_config)
    updated_config = FluffConfig(
        configs={"core": {"templater": "python", "dialect": "ansi"}}
    )
    with fluff_log_catcher(logging.WARNING, "sqlfluff.linter") as caplog:
        lntr.render_string(
            in_str="select * from table",
            fname="test.sql",
            config=updated_config,
            encoding="utf-8",
        )
    assert "Attempt to set templater to " in caplog.text


def test_advanced_api_methods():
    """Test advanced API methods on segments."""
    # These aren't used by the simple API, which returns
    # a simple JSON representation of the parse tree, but
    # are available for advanced API usage and within rules.
    sql = """
    WITH cte AS (
        SELECT * FROM tab_a
    )
    SELECT
        cte.col_a,
        tab_b.col_b
    FROM cte
    INNER JOIN tab_b;
    """
    linter = Linter(dialect="ansi")
    parsed = linter.parse_string(sql)

    # CTEDefinitionSegment.get_identifier
    cte_segment = next(parsed.tree.recursive_crawl("common_table_expression"))
    assert cte_segment.get_identifier().raw == "cte"

    # BaseFileSegment.get_table_references & StatementSegment.get_table_references
    assert parsed.tree.get_table_references() == {"tab_a", "tab_b"}


def test_normalise_newlines():
    """Test normalising newlines to unix-style line endings."""
    in_str = "SELECT\r\n foo\n FROM \r \n\r bar;"
    out_str = "SELECT\n foo\n FROM \n \n\n bar;"
    assert out_str == Linter._normalise_newlines(in_str)
