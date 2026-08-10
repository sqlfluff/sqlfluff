"""Tests for the Linter class and LintingResult class."""

import logging
import os
import pickle
from unittest.mock import patch

import pytest

from sqlfluff.cli.formatters import OutputStreamFormatter
from sqlfluff.cli.outputstream import OutputPolicy, make_output_stream
from sqlfluff.core import FluffConfig, Linter
from sqlfluff.core.errors import (
    SQLBaseError,
    SQLFluffSkipFile,
    SQLLexError,
    SQLLintError,
    SQLParseError,
    SQLTemplaterError,
)
from sqlfluff.core.linter import runner
from sqlfluff.core.linter.common import DeferredRenderTask, RenderedLintTask
from sqlfluff.core.linter.linter import TemplaterSession
from sqlfluff.core.linter.linting_result import combine_dicts, sum_dicts
from sqlfluff.core.linter.runner import get_runner
from sqlfluff.core.templaters import RawTemplater, TemplatedFile
from sqlfluff.utils.testing.logging import fluff_log_catcher

try:
    from sqlfluffrs import RsSQLLexerError

    SQLLexErrorClass = (SQLLexError, RsSQLLexerError)
except ImportError:
    SQLLexErrorClass = (SQLLexError,)


class DummyLintError(SQLBaseError):
    """Fake lint error used by tests, similar to SQLLintError."""

    def __init__(self, line_no: int, code: str = "LT01"):
        self._code = code
        super().__init__(line_no=line_no)


class DuplicateViolationTemplater(RawTemplater):
    """Test templater which emits duplicate templater violations per variant."""

    name = "duplicate_violation_test"

    def process_with_variants(
        self,
        *,
        in_str: str,
        fname: str,
        config=None,
        formatter=None,
    ):
        """Yield the same templated file twice with duplicate errors."""
        for _ in range(2):
            yield (
                TemplatedFile(in_str, fname=fname),
                [
                    SQLTemplaterError(
                        "Repeated templater issue",
                        line_no=1,
                        line_pos=1,
                    )
                ],
            )


def normalise_paths(paths):
    """Test normalising paths.

    NB Paths on difference platforms might look different, so this
    makes them comparable.
    """
    return {pth.replace("/", ".").replace("\\", ".") for pth in paths}


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
    "byte_lim, raises",
    [
        (0, False),
        (None, False),
        (200, False),
        ("200", False),
        ("Not a Valid value", True),
        ("None", True),
        ([1], True),
    ],
)
def test__linter__large_file_skip_byte_limit__setting(byte_lim, raises):
    """Test custom values for large_file_skip_byte_limit.

    Linter should raise an error only in cases
    where the value really is invalid
    """
    config = FluffConfig(
        overrides={"large_file_skip_byte_limit": byte_lim, "dialect": "ansi"}
    )

    try:
        Linter.load_raw_file_and_config(
            "test/fixtures/linter/indentation_errors.sql", config
        )
        assert not raises
    except (ValueError, TypeError):
        assert raises


@pytest.mark.parametrize(
    "rules,num_violations", [(None, 7), ("CP01", 2), (("LT01", "LT12"), 1)]
)
def test__linter__get_violations_filter_rules(rules, num_violations):
    """Test filtering violations by which rules were violated."""
    lntr = Linter(dialect="ansi")
    lint_result = lntr.lint_string("select a, b FROM tbl c order BY d")

    assert len(lint_result.get_violations(rules=rules)) == num_violations


def test__linter__linting_result__sum_dicts():
    """Test the summing of dictionaries in the linter."""
    i = {}
    a = dict(a=3, b=123, f=876.321)
    b = dict(a=19, b=321.0, g=23478)
    r = dict(a=22, b=444.0, f=876.321, g=23478)
    assert sum_dicts(a, b) == r
    # Check the identity too
    assert sum_dicts(r, i) == r


def test__linter__linting_result__combine_dicts():
    """Test the combination of dictionaries in the linter."""
    a = dict(a=3, b=123, f=876.321)
    b = dict(h=19, i=321.0, j=23478)
    r = dict(z=22)
    assert combine_dicts(a, b, r) == dict(
        a=3, b=123, f=876.321, h=19, i=321.0, j=23478, z=22
    )


def test__linter__linting_result_check_tuples():
    """Test that a LintingResult can partition violations by the source files."""
    lntr = Linter()
    result = lntr.lint_paths(
        (
            "test/fixtures/linter/comma_errors.sql",
            "test/fixtures/linter/whitespace_errors.sql",
        )
    )
    check_tuples = result.check_tuples()
    isinstance(check_tuples, list)
    assert check_tuples == [
        ("LT09", 2, 1),
        ("LT04", 4, 5),
        ("LT02", 5, 1),
        ("LT04", 5, 1),
        ("LT02", 6, 1),
        ("AL02", 6, 5),
        ("LT01", 6, 6),
        ("CP01", 8, 1),
        ("LT09", 1, 1),
        ("LT01", 2, 9),
        ("LT01", 3, 12),
        ("LT02", 4, 1),
        ("CP01", 6, 10),
    ]


def test__linter__linting_result_check_tuples_by_path():
    """Test that a LintingResult can partition violations by the source files."""
    lntr = Linter()
    result = lntr.lint_paths(
        (
            "test/fixtures/linter/comma_errors.sql",
            "test/fixtures/linter/whitespace_errors.sql",
        )
    )
    check_tuples = result.check_tuples_by_path()
    isinstance(check_tuples, dict)
    # Normalise the paths in the keys.
    check_tuples = {k.replace("\\", "/"): v for k, v in check_tuples.items()}
    assert check_tuples == {
        "test/fixtures/linter/comma_errors.sql": [
            ("LT09", 2, 1),
            ("LT04", 4, 5),
            ("LT02", 5, 1),
            ("LT04", 5, 1),
            ("LT02", 6, 1),
            ("AL02", 6, 5),
            ("LT01", 6, 6),
            ("CP01", 8, 1),
        ],
        "test/fixtures/linter/whitespace_errors.sql": [
            ("LT09", 1, 1),
            ("LT01", 2, 9),
            ("LT01", 3, 12),
            ("LT02", 4, 1),
            ("CP01", 6, 10),
        ],
    }


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
    result = lntr.lint_paths((f"test/fixtures/linter/exit_codes/{path}",))
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

                def terminate(self):
                    pass

                def join(self):
                    pass

            return ErrorPool()

        monkeypatch.setattr(runner.MultiProcessRunner, "_create_pool", _create_pool)

    config = FluffConfig(overrides={"dialect": "ansi"})
    output_stream = make_output_stream(config, None, os.devnull)
    lntr = Linter(
        formatter=OutputStreamFormatter(output_stream, False, OutputPolicy()),
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


def test__linter__templates_in_worker_default():
    """RawTemplater (and subclasses) should have templates_in_worker=True."""
    assert RawTemplater().templates_in_worker is True


def test__parallel_runner__iter_partials_deferred():
    """iter_partials emits DeferredRenderTask items when templates_in_worker=True."""
    config = FluffConfig(overrides={"dialect": "ansi"})
    lntr = Linter(dialect="ansi")
    thd_runner = runner.MultiThreadRunner(lntr, config, processes=1)
    partials = list(
        thd_runner.iter_partials(
            ["test/fixtures/linter/passing.sql"],
            fix=False,
        )
    )
    assert len(partials) == 1
    fname, task = partials[0]
    assert isinstance(task, DeferredRenderTask)
    assert task.fname == "test/fixtures/linter/passing.sql"
    assert task.fix is False


def test__parallel_runner__iter_partials_non_worker_path(monkeypatch):
    """iter_partials falls back to callables when templates_in_worker=False.

    Simulates the behaviour of a main-process-only templater such as dbt.
    """
    config = FluffConfig(overrides={"dialect": "ansi"})
    lntr = Linter(dialect="ansi")
    # Force the flag off (mirrors what DbtTemplater sets)
    monkeypatch.setattr(RawTemplater, "templates_in_worker", False)
    thd_runner = runner.MultiThreadRunner(lntr, config, processes=1)
    partials = list(
        thd_runner.iter_partials(
            ["test/fixtures/linter/passing.sql"],
            fix=False,
        )
    )
    assert len(partials) == 1
    _fname, task = partials[0]
    assert isinstance(task, RenderedLintTask)


def test__parallel_runner__apply_deferred_task():
    """_apply with a DeferredRenderTask should render and return a LintedFile."""
    from sqlfluff.core.linter import LintedFile

    config = FluffConfig(overrides={"dialect": "ansi"})
    config = pickle.loads(pickle.dumps(config))
    task = DeferredRenderTask(
        fname="test/fixtures/linter/passing.sql",
        root_config=config,
        fix=False,
    )
    result = runner.ParallelRunner._apply(("test/fixtures/linter/passing.sql", task))
    assert isinstance(result, LintedFile)


def test__parallel_runner__apply_rendered_task(monkeypatch):
    """_apply lints a main-process rendered task without a bound Linter."""
    from sqlfluff.core.linter import LintedFile

    config = FluffConfig(overrides={"dialect": "ansi"})
    lntr = Linter(dialect="ansi")
    # Simulate a main-process-only templater (e.g. dbt) that disables
    # worker-side rendering.
    monkeypatch.setattr(RawTemplater, "templates_in_worker", False)
    thd_runner = runner.MultiThreadRunner(lntr, config, processes=1)
    partials = list(
        thd_runner.iter_partials(
            ["test/fixtures/linter/passing.sql"],
            fix=False,
        )
    )
    fname, task = partials[0]
    assert isinstance(task, RenderedLintTask)
    result = runner.ParallelRunner._apply((fname, task))
    assert isinstance(result, LintedFile)


def test__parallel_runner__apply_skip_file():
    """_apply wraps a SQLFluffSkipFile raised during render into DelayedException.

    Uses a byte limit of 5, which is below the size of passing.sql (16 bytes),
    so render_file raises SQLFluffSkipFile.
    """
    config = FluffConfig(overrides={"large_file_skip_byte_limit": 5, "dialect": "ansi"})
    task = DeferredRenderTask(
        fname="test/fixtures/linter/passing.sql",
        root_config=config,
        fix=False,
    )
    result = runner.ParallelRunner._apply(("test/fixtures/linter/passing.sql", task))
    assert isinstance(result, runner.DelayedException)
    assert isinstance(result.ee, SQLFluffSkipFile)


def test__parallel_runner__skip_file_handled_in_run():
    """SQLFluffSkipFile in a deferred worker logs a plain skip warning.

    Uses a byte limit of 5, which is below the size of passing.sql (16 bytes),
    so render_file raises SQLFluffSkipFile.
    The runner should not emit the "Unable to lint … Please report" error
    message — that is reserved for genuine unexpected failures.
    """
    config = FluffConfig(overrides={"large_file_skip_byte_limit": 5, "dialect": "ansi"})
    lntr = Linter(config=config)
    with fluff_log_catcher(logging.WARNING, "sqlfluff.linter") as caplog:
        # Consume the iterator — errors surface only when results are consumed.
        list(
            runner.MultiThreadRunner(lntr, config, processes=1).run(
                ["test/fixtures/linter/passing.sql"],
                fix=False,
            )
        )
    # The skip message must appear in the warning output.
    assert "over the limit of 5" in caplog.text
    # The "please report" message must NOT appear — a skip is not a bug.
    assert "Please report" not in caplog.text


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


def test__linter__lint_paths_closes_runner_iterator_on_early_break(monkeypatch):
    """Ensure lint_paths closes runner iterator when loop exits early."""
    test_path = os.path.normpath("test/fixtures/linter/passing.sql")

    class ClosableIterator:
        """Simple iterator tracking whether close() gets called."""

        def __init__(self, item):
            self.item = item
            self.closed = False
            self._yielded = False

        def __iter__(self):
            return self

        def __next__(self):
            if self._yielded:
                raise StopIteration
            self._yielded = True
            return self.item

        def close(self):
            self.closed = True

    class StubRunner:
        """Runner that returns a pre-created iterator."""

        def __init__(self, iterator):
            self.iterator = iterator
            self.skipped_file_count = 0

        def run(self, fnames, fix):
            return self.iterator

    fatal_error = DummyLintError(line_no=1)
    fatal_error.fatal = True
    linted_file = runner.LintedFile(
        path=test_path,
        violations=[fatal_error],
        timings=None,
        tree=None,
        ignore_mask=None,
        templated_file=None,
        encoding="utf8",
    )
    closable_iterator = ClosableIterator(linted_file)

    monkeypatch.setattr(
        runner,
        "get_runner",
        lambda *args, **kwargs: (StubRunner(closable_iterator), 2),
    )

    lntr = Linter(dialect="ansi")
    lntr.lint_paths((test_path,), processes=2)

    assert closable_iterator.closed


def test__parallel_runner__pool_join_called_on_cleanup(monkeypatch):
    """Ensure ParallelRunner.run() calls pool.terminate() and pool.join().

    Without pool.join(), worker processes may still be alive when Python's
    resource_tracker runs at shutdown, causing "leaked semaphore" warnings
    from the named POSIX semaphores used by the pool's internal queues.
    """

    class TrackingPool:
        """Fake pool that records terminate/join calls."""

        def __init__(self):
            self.terminated = False
            self.joined = False

        def imap_unordered(self, func, iterable):
            yield from ()

        def imap(self, func, iterable):
            yield from ()

        def terminate(self):
            self.terminated = True

        def join(self):
            self.joined = True

    tracking_pool = TrackingPool()

    monkeypatch.setattr(
        runner.MultiThreadRunner,
        "_create_pool",
        classmethod(lambda cls, *a, **kw: tracking_pool),
    )

    config = FluffConfig(overrides={"dialect": "ansi"})
    lntr = Linter(config=config)
    # Consume the generator to trigger the finally block.
    list(runner.MultiThreadRunner(lntr, config, processes=1).run([], fix=False))

    assert tracking_pool.terminated, "pool.terminate() was not called"
    assert tracking_pool.joined, "pool.join() was not called"


def test__parallel_runner__pool_join_called_on_generator_close(monkeypatch):
    """pool.join() is called even when the generator is closed early."""

    class TrackingPool:
        """Fake pool that records terminate/join calls."""

        def __init__(self):
            self.terminated = False
            self.joined = False

        def imap_unordered(self, func, iterable):
            # Yield a sentinel so the generator suspends at yield.
            for item in iterable:
                yield func(item)

        def imap(self, func, iterable):
            for item in iterable:
                yield func(item)

        def terminate(self):
            self.terminated = True

        def join(self):
            self.joined = True

    tracking_pool = TrackingPool()

    monkeypatch.setattr(
        runner.MultiThreadRunner,
        "_create_pool",
        classmethod(lambda cls, *a, **kw: tracking_pool),
    )

    config = FluffConfig(overrides={"dialect": "ansi"})
    lntr = Linter(config=config)
    gen = runner.MultiThreadRunner(lntr, config, processes=1).run(
        ["test/fixtures/linter/passing.sql"], fix=False
    )
    # Advance to the first yield, then close early.
    next(gen, None)
    gen.close()

    assert tracking_pool.terminated, "pool.terminate() was not called"
    assert tracking_pool.joined, "pool.join() was not called"


def test__linter__empty_file():
    """Test linter behaves nicely with an empty string.

    Much of this test is about making sure that ParsedString is
    instantiated appropriately.
    """
    lntr = Linter(dialect="ansi")
    # Make sure no exceptions raised and no violations found in empty file.
    parsed = lntr.parse_string("")
    # There should still be a parsed variant
    assert parsed.parsed_variants
    assert len(parsed.parsed_variants) == 1
    root_variant = parsed.parsed_variants[0]
    # That root variant should still have a templated file and a parsed tree
    # (although that parsed tree will likely just be an end of file marker).
    assert root_variant.templated_file
    assert root_variant.tree
    # No violations
    assert not parsed.violations


def test__linter__parse_fail():
    """Test linter behaves as expected with an unparsable string.

    Much of this test is about making sure that ParsedString is
    instantiated appropriately.
    """
    lntr = Linter(dialect="ansi")
    # Try and parse something which obviously isn't SQL
    parsed = lntr.parse_string("THIS IS NOT SQL")
    # There should still be a parsed variant
    assert parsed.parsed_variants
    assert len(parsed.parsed_variants) == 1
    root_variant = parsed.parsed_variants[0]
    # That root variant should still have a templated file and a parsed tree...
    assert root_variant.templated_file
    assert root_variant.tree
    # ...but that tree should contain an unparsable segment.
    assert "unparsable" in root_variant.tree.type_set()
    # There *should* be violations because there should be a parsing fail.
    assert parsed.violations
    assert any(isinstance(v, SQLParseError) for v in parsed.violations)


def test__linter__templating_fail():
    """Test linter behaves as expected with invalid jinja template.

    Much of this test is about making sure that ParsedString is
    instantiated appropriately.
    """
    lntr = Linter(dialect="ansi")
    # Try and parse something which breaks Jinja templating.
    parsed = lntr.parse_string("{% if foo %}")
    # For a templating fail, there won't be a parsed variant.
    assert not parsed.parsed_variants
    # There *should* be violations because there should be a templating fail.
    assert parsed.violations
    assert any(isinstance(v, SQLTemplaterError) for v in parsed.violations)


def test__linter__variant_limit_surfaces_additional_branch_violations():
    """Verify linting alternate variants surfaces branch-specific violations."""
    sql = """select
    {% if True %}
        a as foo
    {% else %}
        b as foo
    {% endif %}
from example_table
{% if False %}
where col_one between 1 and 2
{% elif True %}
where col_one between 2 and 3
{% else %}
where col_one between 3 and 4
{% endif %}
"""

    single_variant = Linter(
        config=FluffConfig(
            configs={
                "core": {
                    "dialect": "ansi",
                    "rules": "CP01",
                    "render_variant_limit": 1,
                },
                "rules": {
                    "capitalisation.keywords": {"capitalisation_policy": "upper"}
                },
            }
        )
    ).lint_string(sql)

    multi_variant = Linter(
        config=FluffConfig(
            configs={
                "core": {
                    "dialect": "ansi",
                    "rules": "CP01",
                    "render_variant_limit": 6,
                },
                "rules": {
                    "capitalisation.keywords": {"capitalisation_policy": "upper"}
                },
            }
        )
    ).lint_string(sql)

    assert single_variant.check_tuples() == [
        ("CP01", 1, 1),
        ("CP01", 3, 11),
        ("CP01", 7, 1),
        ("CP01", 11, 1),
        ("CP01", 11, 15),
        ("CP01", 11, 25),
    ]
    assert multi_variant.check_tuples() == [
        ("CP01", 1, 1),
        ("CP01", 3, 11),
        ("CP01", 5, 11),
        ("CP01", 7, 1),
        ("CP01", 9, 1),
        ("CP01", 9, 15),
        ("CP01", 9, 25),
        ("CP01", 11, 1),
        ("CP01", 11, 15),
        ("CP01", 11, 25),
        ("CP01", 13, 1),
        ("CP01", 13, 15),
        ("CP01", 13, 25),
    ]


def test__linter__ignores_alternate_variant_parse_errors_when_root_variant_parses():
    """Alternate variant parse errors should not fail a valid root variant."""
    sql = """-- This file combines product data from individual brands into a staging table
{% set products =  [
  'table1',
  'table2'] %}

{% for product in products %}
SELECT
  brand,
  country_code,
  category,
  name,
  id
FROM
  {{ product }}
{% if not loop.last -%} UNION ALL {%- endif %}
{% endfor %}
"""

    linted = Linter(
        config=FluffConfig(
            configs={
                "core": {
                    "dialect": "ansi",
                    "rules": "LT02",
                    "render_variant_limit": 5,
                }
            }
        )
    ).lint_string(sql, fix=True)

    assert not any(isinstance(v, SQLParseError) for v in linted.violations)
    assert linted.check_tuples() == [
        ("LT02", 7, 1),
        ("LT02", 8, 1),
        ("LT02", 9, 1),
        ("LT02", 10, 1),
        ("LT02", 11, 1),
        ("LT02", 12, 1),
        ("LT02", 13, 1),
        ("LT02", 14, 1),
        ("LT02", 15, 1),
    ]


def test__parsed_string__ignores_alternate_variant_parse_errors_with_valid_root():
    """ParsedString.violations should follow root-variant semantics."""
    sql = """-- This file combines product data from individual brands into a staging table
{% for product in ['table1', 'table2'] %}
    SELECT
        brand,
        country_code,
        category,
        name,
        id
    FROM
        {{ product }}
    {% if not loop.last -%} UNION ALL {%- endif %}
{% endfor %}
"""

    cfg = FluffConfig(overrides={"dialect": "ansi", "rules": "LT02"})
    linter = Linter(config=cfg)
    rendered = linter.render_string(sql, fname="<STR>", config=cfg, encoding="utf-8")
    parsed = linter.parse_rendered(rendered)

    assert len(parsed.parsed_variants) == 1
    assert parsed.root_variant() is not None
    assert not parsed.violations


def test__linter__fix_string_merges_non_conflicting_patches_across_variants():
    """fix_string() should merge safe source edits from all parsed variants."""
    sql = """{% if False %}
SELECT 1
{% else %}
SELECT c
FROM t
WHERE c < 0
{% endif %}"""
    expected = """{% if False %}
    SELECT 1
{% else %}
    SELECT c
    FROM t
    WHERE c < 0
{% endif %}
"""
    config = FluffConfig(
        configs={
            "core": {
                "dialect": "ansi",
                "templater": "jinja",
                "rules": "LT02,LT12",
                "render_variant_limit": 5,
            }
        }
    )

    linted = Linter(config=config).lint_string(sql, fname="test.sql", fix=True)
    fixed_sql, changed = linted.fix_string()

    assert changed
    assert fixed_sql == expected


def test__linter__deduplicates_duplicate_templater_violations_in_linted_output(
    monkeypatch,
):
    """Verify duplicate templater errors from variants collapse in lint output."""
    config = FluffConfig(
        overrides={
            "dialect": "ansi",
            "rules": "CP01",
        }
    )
    linter = Linter(config=config)
    templater = DuplicateViolationTemplater()
    monkeypatch.setattr(config, "get_templater", lambda: templater)

    parsed = linter.parse_string("SELECT 1\n")
    monkeypatch.setattr(config, "get_templater", DuplicateViolationTemplater)
    linted = linter.lint_string("SELECT 1\n")

    assert len(parsed.templating_violations) == 2
    assert [
        (violation.rule_code(), violation.line_no, violation.line_pos, violation.desc())
        for violation in linted.violations
    ] == [("TMP", 1, 1, "Repeated templater issue")]


@pytest.mark.parametrize(
    "path,rules,ignore_templated_areas,check_tuples",
    [
        (
            "test/fixtures/templater/jinja_h_macros/jinja.sql",
            "L006",
            True,
            [("LT01", 3, 39), ("LT01", 3, 40)],
        ),
        (
            "test/fixtures/templater/jinja_h_macros/jinja.sql",
            "L006",
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
        (
            "test/fixtures/linter/jinja_variants/simple_CP01.sql",
            "CP01",
            False,
            [
                # We should get violations from both sides of the if
                # statement without doubling up on the one outside.
                ("CP01", 2, 10),
                ("CP01", 2, 34),
                ("CP01", 2, 52),
            ],
        ),
        (
            "test/fixtures/linter/jinja_variants/branching_cp01.sql",
            "CP01",
            False,
            [
                # Nested IF/ELIF blocks should surface keyword violations
                # from every variant we render.
                ("CP01", 3, 1),
                ("CP01", 5, 11),
                ("CP01", 7, 11),
                ("CP01", 9, 1),
                ("CP01", 11, 1),
                ("CP01", 11, 15),
                ("CP01", 11, 25),
                ("CP01", 13, 1),
                ("CP01", 13, 15),
                ("CP01", 13, 25),
                ("CP01", 15, 1),
                ("CP01", 15, 15),
                ("CP01", 15, 25),
            ],
        ),
    ],
)
def test__linter__mask_templated_violations(
    path, rules, ignore_templated_areas, check_tuples
):
    """Test linter masks files properly around templated content.

    NOTE: this also tests deduplication of fixes which have the same
    source position. i.e. `LintedFile.deduplicate_in_source_space()`.
    """
    lntr = Linter(
        config=FluffConfig(
            overrides={
                "rules": rules,
                "ignore_templated_areas": ignore_templated_areas,
                "dialect": "ansi",
            }
        )
    )
    linted = lntr.lint_path(path=path)
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
    result = lntr.lint_paths((fname,))
    assert lexerror == any(
        True for v in result.get_violations() if type(v) in SQLLexErrorClass
    )


def test_delayed_exception():
    """Test that DelayedException stores and reraises a stored exception."""
    ve = ValueError()
    de = runner.DelayedException(ve)
    with pytest.raises(ValueError):
        de.reraise()


def test__linter__uses_stateful_templater_from_file_config(monkeypatch):
    """Test a stateful templater can be selected by a file configuration."""
    initial_config = FluffConfig(
        configs={"core": {"templater": "jinja", "dialect": "ansi"}}
    )
    lntr = Linter(config=initial_config)
    updated_config = FluffConfig(
        configs={
            "core": {"templater": "python", "dialect": "ansi"},
            "templater": {"python": {"context": {"table": "table"}}},
        }
    )
    updated_templater = updated_config.get("templater_obj")
    monkeypatch.setattr(updated_templater, "templates_in_worker", False)

    rendered = lntr.render_string(
        in_str="select * from {table}",
        fname="test.sql",
        config=updated_config,
        encoding="utf-8",
    )

    assert rendered.templated_variants[0].templated_str == "select * from table"


def test__templater_session_does_not_mutate_or_close_config_templaters():
    """A session leaves caller-owned configuration templaters untouched."""

    class TrackingTemplater(RawTemplater):
        name = "tracking"

        def __init__(self):
            self.close_count = 0

        def close(self):
            self.close_count += 1

    first_templater = TrackingTemplater()
    second_templater = TrackingTemplater()
    first_config = FluffConfig(overrides={"dialect": "ansi"})
    second_config = FluffConfig(overrides={"dialect": "ansi"})
    first_config._configs["core"]["templater_obj"] = first_templater
    second_config._configs["core"]["templater_obj"] = second_templater
    session = TemplaterSession(lambda config: config.get_templater())

    assert session.borrow(first_config, first_templater) is first_templater
    assert session.borrow(second_config, second_templater) is first_templater
    assert session.borrow(second_config, second_templater) is first_templater
    assert second_templater.close_count == 0

    session.close()
    assert first_templater.close_count == 0
    assert first_config.get("templater_obj") is first_templater
    assert second_config.get("templater_obj") is second_templater


def test__templater_session_factory_owns_created_templaters():
    """A session closes templaters returned by its explicit factory."""

    class TrackingTemplater(RawTemplater):
        def __init__(self):
            self.closed = False

        def close(self):
            self.closed = True

    templater = TrackingTemplater()
    config = FluffConfig(overrides={"dialect": "ansi"})
    session = TemplaterSession(lambda _: templater)

    assert session.get(config) is templater
    session.close()

    assert templater.closed


@pytest.mark.parametrize("operation", ["render", "lint"])
def test__linter__uses_fresh_templater_for_repeated_string_operations(
    monkeypatch, operation
):
    """Each public string operation gets a usable templater instance."""

    class SingleUseTemplater(RawTemplater):
        def __init__(self):
            self.closed = False

        def process(self, **kwargs):
            assert not self.closed
            return super().process(**kwargs)

        def close(self):
            self.closed = True

    config = FluffConfig(overrides={"dialect": "ansi"})
    linter = Linter(config=config)
    instances = []

    def get_templater():
        templater = SingleUseTemplater()
        instances.append(templater)
        return templater

    config._configs["core"]["templater_obj"] = None
    monkeypatch.setattr(config, "get_templater", get_templater)

    if operation == "render":
        linter.render_string("SELECT 1", "first.sql", config, "utf-8")
        linter.render_string("SELECT 2", "second.sql", config, "utf-8")
    else:
        linter.lint_string("SELECT 1", fname="first.sql")
        linter.lint_string("SELECT 2", fname="second.sql")

    assert len(instances) == 2
    assert all(templater.closed for templater in instances)


def test__linter__shares_stateless_templater_with_different_configs(tmp_path):
    """One run shares a stateless templater across per-file configurations."""
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"
    first_dir.mkdir()
    second_dir.mkdir()
    first_file = first_dir / "query.sql"
    second_file = second_dir / "query.sql"
    first_file.write_text("SELECT :value\n", encoding="utf-8")
    second_file.write_text("SELECT {value}\n", encoding="utf-8")
    first_dir.joinpath(".sqlfluff").write_text(
        """[sqlfluff]
dialect = ansi
templater = placeholder

[sqlfluff:templater:placeholder]
param_style = colon
""",
        encoding="utf-8",
    )
    second_dir.joinpath(".sqlfluff").write_text(
        """[sqlfluff]
dialect = ansi
templater = placeholder

[sqlfluff:templater:placeholder]
param_regex = \\{(?P<param_name>\\w+)\\}
""",
        encoding="utf-8",
    )

    config = FluffConfig(overrides={"dialect": "ansi"})
    linter = Linter(config=config)

    result = linter.lint_paths(
        (str(first_file), str(second_file)),
        processes=2,
    )

    assert not result.get_violations()
    rendered_files = {
        linted_file.path: linted_file.templated_file.templated_str
        for linted_path in result.paths
        for linted_file in linted_path.files
    }
    assert rendered_files == {
        str(first_file): "SELECT value\n",
        str(second_file): "SELECT value\n",
    }


@pytest.mark.parametrize("processes", [1, 2])
@pytest.mark.parametrize("fix", [False, True])
def test__linter__uses_templater_from_file_config(processes, fix):
    """Lint files using different built-in templaters in one invocation."""
    config = FluffConfig.from_path("test/fixtures/linter/mixed_templaters")
    linter = Linter(config=config)

    result = linter.lint_paths(
        ("test/fixtures/linter/mixed_templaters",),
        fix=fix,
        processes=processes,
    )

    assert not result.get_violations()


def test__linter__mixed_templaters_preserve_file_order(tmp_path):
    """Sequential templater grouping preserves discovery order."""
    nested = tmp_path / "placeholder"
    nested.mkdir()
    tmp_path.joinpath(".sqlfluff").write_text(
        "[sqlfluff]\ndialect = ansi\ntemplater = jinja\n", encoding="utf-8"
    )
    nested.joinpath(".sqlfluff").write_text(
        "[sqlfluff]\ntemplater = placeholder\n\n"
        "[sqlfluff:templater:placeholder]\nparam_style = colon\n",
        encoding="utf-8",
    )
    paths = (
        tmp_path / "first.sql",
        nested / "second.sql",
        tmp_path / "third.sql",
    )
    for path in paths:
        path.write_text("SELECT 1\n", encoding="utf-8")
    string_paths = tuple(str(path) for path in paths)
    linter = Linter(config=FluffConfig.from_path(str(tmp_path)))

    result = linter.lint_paths(string_paths, processes=1)

    assert [file.path for path in result.paths for file in path.files] == list(
        string_paths
    )


def test__sequential_runner__streams_worker_safe_files(tmp_path, monkeypatch):
    """Sequential linting completes each worker-safe file before loading the next."""
    first_file = tmp_path / "first.sql"
    second_file = tmp_path / "second.sql"
    first_file.write_text("SELECT 1\n", encoding="utf-8")
    second_file.write_text("SELECT 2\n", encoding="utf-8")
    linter = Linter(dialect="ansi")
    events = []
    original_load = linter.load_raw_file
    original_lint = linter.lint_rendered

    def tracking_load(fname, config):
        events.append(("load", fname))
        return original_load(fname, config)

    def tracking_lint(rendered, rule_pack, fix, formatter):
        events.append(("lint", rendered.fname))
        return original_lint(rendered, rule_pack, fix, formatter)

    monkeypatch.setattr(linter, "load_raw_file", tracking_load)
    monkeypatch.setattr(linter, "lint_rendered", tracking_lint)

    linter.lint_paths((str(first_file), str(second_file)), processes=1)

    assert events == [
        ("load", str(first_file)),
        ("lint", str(first_file)),
        ("load", str(second_file)),
        ("lint", str(second_file)),
    ]


def test__linter__discovers_extensions_from_nested_config(tmp_path):
    """Directory discovery uses file extensions from nested configuration."""
    nested = tmp_path / "nested"
    nested.mkdir()
    tmp_path.joinpath(".sqlfluff").write_text(
        "[sqlfluff]\ndialect = ansi\ntemplater = jinja\n", encoding="utf-8"
    )
    nested.joinpath(".sqlfluff").write_text(
        "[sqlfluff]\ntemplater = placeholder\nsql_file_exts = .bq\n\n"
        "[sqlfluff:templater:placeholder]\nparam_style = colon\n",
        encoding="utf-8",
    )
    nested_file = nested / "query.bq"
    nested_file.write_text("SELECT :value\n", encoding="utf-8")
    linter = Linter(config=FluffConfig.from_path(str(tmp_path)))

    result = linter.lint_paths((str(tmp_path),))

    assert [file.path for path in result.paths for file in path.files] == [
        str(nested_file)
    ]


def test__linter__parse_path_uses_nested_templaters():
    """Path parsing uses effective templaters and operation cleanup."""
    root = "test/fixtures/linter/mixed_templaters"
    linter = Linter(config=FluffConfig.from_path(root))

    parsed = list(linter.parse_path(root))

    assert len(parsed) == 2
    assert not [violation for result in parsed for violation in result.violations]


def test__linter__render_string_closes_owned_templater_after_error(monkeypatch):
    """Direct rendering closes its templater without masking the render error."""

    class FailingTemplater(RawTemplater):
        """Templater that fails rendering and records cleanup."""

        def __init__(self):
            super().__init__()
            self.closed = False

        def process_with_variants(self, **kwargs):
            raise ValueError("render failed")
            yield  # pragma: no cover

        def close(self):
            self.closed = True
            raise RuntimeError("close failed")

    config = FluffConfig(overrides={"dialect": "ansi"})
    templater = FailingTemplater()
    config._configs["core"]["templater_obj"] = None
    monkeypatch.setattr(config, "get_templater", lambda: templater)
    linter = Linter(config=config)

    with pytest.raises(ValueError, match="render failed"):
        linter.render_string("SELECT 1", "test.sql", config, "utf-8")

    assert templater.closed


def test__linter__variant_cleanup_does_not_mask_render_error(monkeypatch):
    """Variant iterator cleanup preserves the active rendering exception."""

    class FailingVariants:
        def __iter__(self):
            return self

        def __next__(self):
            raise ValueError("render failed")

        def close(self):
            raise RuntimeError("variant close failed")

    class FailingTemplater(RawTemplater):
        def process_with_variants(self, **kwargs):
            return FailingVariants()

    config = FluffConfig(overrides={"dialect": "ansi"})
    templater = FailingTemplater()
    monkeypatch.setattr(config, "get_templater", lambda: templater)

    with pytest.raises(ValueError, match="render failed"):
        Linter(config=config).render_string("SELECT 1", "test.sql", config, "utf-8")


def test__linter__closing_parse_path_releases_session():
    """Closing a partially consumed path parser permits another operation."""
    root = "test/fixtures/linter/mixed_templaters"
    linter = Linter(config=FluffConfig.from_path(root))
    parsed = linter.parse_path(root)

    assert next(parsed).tree
    parsed.close()

    assert not linter.lint_paths((root,)).get_violations()


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


@pytest.mark.parametrize(
    "fix_even_unparsable",
    [False, True],
)
def test_unparsable_fix_output(fix_even_unparsable):
    """Tests functionality and logging output with unparsable sections.

    NOTE: While we cover different paths, the result for this test is the
    same for both values of `fix_even_unparsable`. We probably need a better
    test case at some point so that we can actually see the difference.
    """
    config = FluffConfig(
        overrides={"fix_even_unparsable": fix_even_unparsable, "dialect": "ansi"}
    )
    linter = Linter(config=config)
    # Attempt to fix it, capturing the logging output.
    with fluff_log_catcher(logging.WARNING, "sqlfluff.linter") as caplog:
        result = linter.lint_paths(
            ("test/fixtures/linter/parse_error_2.sql",),
            fix=True,
            apply_fixes=True,
            fixed_file_suffix=f"_{fix_even_unparsable}_fix",
            fix_even_unparsable=fix_even_unparsable,
        )
    # Assert that it parsed (i.e. we found a select_statement), but with an
    # unparsable section in there too.
    assert result.tree
    assert "select_statement" in result.tree.descendant_type_set
    assert "unparsable" in result.tree.descendant_type_set
    # We should still find linting issues too
    assert result.check_tuples(raise_on_non_linting_violations=False) == [
        ("CP01", 2, 7),  # `a as b` - capitalisation of AS
        ("AL03", 3, 5),  # 42 is an expression without an alias
        # The unparsable section is (wrongly) detected as an indentation issue.
        ("LT02", 4, 1),
        ("CP01", 5, 1),  # `from` is uncapitalised
    ]
    # We should make sure that the warning that asks users to report a bug is
    # NOT present. i.e. the warning which could happen in `lint_fix_parsed()`.`
    assert "Please report this as a bug" not in caplog.text
    # Also not the `fix not applied`. The one in `_warn_unfixable()`
    assert "it would re-cause the same error" not in caplog.text
    # In fact, there shouldn't be any warnings at all.
    assert not caplog.text.strip()
    # In both cases, the final capitalisation and the `a as b` sections should have
    # been fixed (because they aren't in the unparsable section).
    assert "from cte" not in result.tree.raw
    assert "FROM cte" in result.tree.raw
    assert "a as b" not in result.tree.raw
    assert "a AS b" in result.tree.raw
    # Check whether the file was persisted. If `fix_even_unparsable` was set, then
    # there should be a file, and it should have the fixes from above in it. If not
    # then there should be no fixed file, as the persist will have been aborted due
    # to the parsing issues.
    predicted_fix_path = (
        f"test/fixtures/linter/parse_error_2_{fix_even_unparsable}_fix.sql"
    )
    if fix_even_unparsable:
        with open(predicted_fix_path, "r") as f:
            fixed_sql = f.read()
        assert result.tree.raw == fixed_sql
    else:
        with pytest.raises(FileNotFoundError):
            open(predicted_fix_path, "r")


def test__linter__skip_large_bytes__files_skipped_count():
    """Verify that files_skipped is tracked in LintingResult when files are skipped."""
    # Use a very low byte limit so the file is always skipped.
    config = FluffConfig(overrides={"large_file_skip_byte_limit": 5, "dialect": "ansi"})
    lntr = Linter(config)
    result = lntr.lint_paths(
        ("test/fixtures/linter/indentation_errors.sql",),
    )
    assert result.files_skipped == 1
    assert not result.get_violations()


def test__linter__no_skip__files_skipped_zero():
    """Verify files_skipped is 0 when no files are skipped."""
    config = FluffConfig(overrides={"large_file_skip_byte_limit": 0, "dialect": "ansi"})
    lntr = Linter(config)
    result = lntr.lint_paths(
        ("test/fixtures/linter/indentation_errors.sql",),
    )
    assert result.files_skipped == 0
    assert result.get_violations()


def test__parallel_runner__skip_file_tracked_in_runner():
    """Verify skipped_file_count is incremented on the runner for parallel runs."""
    config = FluffConfig(overrides={"large_file_skip_byte_limit": 5, "dialect": "ansi"})
    lntr = Linter(config=config)
    r = runner.MultiThreadRunner(lntr, config, processes=1)
    # Consume the iterator so the skip logic fires.
    list(r.run(["test/fixtures/linter/passing.sql"], fix=False))
    assert r.skipped_file_count == 1


@pytest.mark.parametrize(
    "large_file_skip_fail,expected_would_fail",
    [
        (True, True),
        (False, False),
    ],
)
def test__linter__large_file_skip_fail_config(
    large_file_skip_fail, expected_would_fail
):
    """Verify that large_file_skip_fail config controls whether skipped files fail.

    This simulates the exit-code logic in the CLI: when files are skipped
    and large_file_skip_fail is True, the exit code should be non-zero.
    """
    config = FluffConfig(
        overrides={
            "large_file_skip_byte_limit": 5,
            "large_file_skip_fail": large_file_skip_fail,
            "dialect": "ansi",
        }
    )
    lntr = Linter(config)
    result = lntr.lint_paths(
        ("test/fixtures/linter/indentation_errors.sql",),
    )
    # The file should be skipped regardless of large_file_skip_fail.
    assert result.files_skipped == 1
    assert not result.get_violations()

    # Simulate CLI exit code logic:
    # exit_code from stats should be 0 (no violations).
    exit_code = result.stats(1, 0)["exit code"]
    assert exit_code == 0  # No violations means stats returns success.

    # But if large_file_skip_fail is set, the CLI would bump this to 1.
    would_fail = bool(result.files_skipped and config.get("large_file_skip_fail"))
    assert would_fail == expected_would_fail
