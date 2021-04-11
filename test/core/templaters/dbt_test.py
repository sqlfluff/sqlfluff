"""Tests for the dbt templater."""

import os
import pytest
import logging

from sqlfluff.core import FluffConfig, Lexer, Linter
from sqlfluff.core.templaters.dbt import DbtTemplater
from test.fixtures.dbt.templater import (  # noqa
    DBT_FLUFF_CONFIG,
    dbt_templater,
    in_dbt_project_dir,
)


def test__templater_dbt_missing(dbt_templater):  # noqa
    """Check that a nice error is returned when dbt module is missing."""
    try:
        import dbt  # noqa: F401

        pytest.skip(msg="dbt is installed")
    except ModuleNotFoundError:
        pass

    with pytest.raises(ModuleNotFoundError, match=r"pip install sqlfluff\[dbt\]"):
        dbt_templater.process(
            in_str="",
            fname="models/my_new_project/test.sql",
            config=FluffConfig(configs=DBT_FLUFF_CONFIG),
        )


@pytest.mark.dbt
def test__templater_dbt_profiles_dir_expanded(dbt_templater):  # noqa
    """Check that the profiles_dir is expanded."""
    dbt_templater.sqlfluff_config = FluffConfig(
        configs={"templater": {"dbt": {"profiles_dir": "~/.dbt"}}}
    )
    profiles_dir = dbt_templater._get_profiles_dir()
    assert profiles_dir == os.path.expanduser("~/.dbt")


@pytest.mark.parametrize(
    "fname",
    [
        # dbt_utils
        "use_dbt_utils.sql",
        # macro calling another macro
        "macro_in_macro.sql",
        # config.get(...)
        "use_headers.sql",
        # var(...)
        "use_var.sql",
    ],
)
@pytest.mark.dbt
def test__templater_dbt_templating_result(
    in_dbt_project_dir, dbt_templater, fname  # noqa
):
    """Test that input sql file gets templated into output sql file."""
    templated_file, _ = dbt_templater.process(
        in_str="",
        fname="models/my_new_project/" + fname,
        config=FluffConfig(configs=DBT_FLUFF_CONFIG),
    )
    # the dbt compiler gets rid of new lines
    assert str(templated_file) == open("../dbt/" + fname).read()


@pytest.mark.dbt
@pytest.mark.parametrize(
    "raw_file,templated_file,result",
    [
        (
            "select * from a",
            """
with dbt__CTE__INTERNAL_test as (
select * from a
)select count(*) from dbt__CTE__INTERNAL_test
""",
            # The unwrapper should trim the ends.
            [
                ("literal", slice(0, 15, None), slice(0, 15, None)),
            ],
        )
    ],
)
def test__templater_dbt_slice_file_wrapped_test(
    raw_file, templated_file, result, caplog
):
    """Test that wrapped queries are sliced safely using _check_for_wrapped()."""
    with caplog.at_level(logging.DEBUG, logger="sqlfluff.templater"):
        _, resp, _ = DbtTemplater.slice_file(
            raw_file,
            templated_file,
        )
    assert resp == result


@pytest.mark.dbt
def test__templater_dbt_templating_test_lex(in_dbt_project_dir, dbt_templater):  # noqa
    """A test to demonstrate _tests_as_models works on dbt tests by temporarily making them models."""
    lexer = Lexer(config=FluffConfig(configs=DBT_FLUFF_CONFIG))
    templated_file, _ = dbt_templater.process(
        in_str="",
        fname="tests/test.sql",
        config=FluffConfig(configs=DBT_FLUFF_CONFIG),
    )
    tokens, lex_vs = lexer.lex(templated_file)
    assert templated_file.source_str == "select * from a\n"
    assert templated_file.templated_str == "select * from a\n"


@pytest.mark.parametrize(
    "fname",
    [
        "use_var.sql",
        "incremental.sql",
    ],
)
@pytest.mark.dbt
def test__templated_sections_do_not_raise_lint_error(in_dbt_project_dir, fname):  # noqa
    """Test that templated sections in dbt model does not raise a linting error."""
    lntr = Linter(config=FluffConfig(configs=DBT_FLUFF_CONFIG))
    lnt = lntr.lint_path(path="models/my_new_project/" + fname)
    violations = lnt.check_tuples()
    print(violations)
    assert len(violations) == 0


@pytest.mark.parametrize(
    "fname",
    [
        "single_trailing_newline.sql",
    ],
)
@pytest.mark.dbt
def test__single_trailing_newline_at_file_end_does_not_raise_lint_error(in_dbt_project_dir, fname):  # noqa
    """Test that dbt model with a single trailing newline at end of file does not raise a linting error."""
    lntr = Linter(config=FluffConfig(configs=DBT_FLUFF_CONFIG))
    lnt = lntr.lint_path(path="models/my_new_project/" + fname)
    violations = lnt.check_tuples()
    print(violations)
    assert len(violations) == 0


@pytest.mark.dbt
def test__dbt_templater_maintains_single_trailing_newline_at_file_end(in_dbt_project_dir, dbt_templater):  # noqa
    """A test to demonstrate that using the dbt templater maintains a single trailing newline at the end of a dbt model."""
    lexer = Lexer(config=FluffConfig(configs=DBT_FLUFF_CONFIG))
    templated_file, _ = dbt_templater.process(
        in_str="",
        fname="models/my_new_project/single_trailing_newline.sql",
        config=FluffConfig(configs=DBT_FLUFF_CONFIG),
    )
    tokens, lex_vs = lexer.lex(templated_file)
    assert templated_file.source_str == "select a\nfrom table_a\n"
    assert templated_file.templated_str == "select a\nfrom table_a\n"


@pytest.mark.parametrize(
    "fname",
    [
        "multiple_trailing_newline.sql",
    ],
)
@pytest.mark.dbt
def test__mulitple_trailing_newlines_at_file_end_does_not_raise_lint_error(in_dbt_project_dir, fname):  # noqa
    """Test that dbt model with a multiple trailing newlines at end of file does not raise a linting error."""
    lntr = Linter(config=FluffConfig(configs=DBT_FLUFF_CONFIG))
    lnt = lntr.lint_path(path="models/my_new_project/" + fname)
    violations = lnt.check_tuples()
    print(violations)
    assert len(violations) == 0


@pytest.mark.dbt
def test__dbt_templater_maintains_multiple_trailing_newlines_at_file_end(in_dbt_project_dir, dbt_templater):  # noqa
    """A test to demonstrate that using the dbt templater maintains multiple trailing newline at the end of a dbt model."""
    lexer = Lexer(config=FluffConfig(configs=DBT_FLUFF_CONFIG))
    templated_file, _ = dbt_templater.process(
        in_str="",
        fname="models/my_new_project/multiple_trailing_newline.sql",
        config=FluffConfig(configs=DBT_FLUFF_CONFIG),
    )
    tokens, lex_vs = lexer.lex(templated_file)
    assert templated_file.source_str == "select a\nfrom table_a\n\n"
    assert templated_file.templated_str == "select a\nfrom table_a\n\n"


@pytest.mark.dbt
def test__templater_dbt_templating_absolute_path(
    in_dbt_project_dir, dbt_templater  # noqa
):
    """Test that absolute path of input path does not cause RuntimeError."""
    try:
        dbt_templater.process(
            in_str="",
            fname=os.path.abspath("models/my_new_project/use_var.sql"),
            config=FluffConfig(configs=DBT_FLUFF_CONFIG),
        )
    except Exception as e:
        pytest.fail(f"Unexpected RuntimeError: {e}")


@pytest.mark.parametrize(
    "fname,exception_msg",
    [
        (
            "compiler_error.sql",
            "dbt compilation error on file 'models/my_new_project/compiler_error.sql', Unexpected end of template. Jinja was looking for the following tags: 'endfor'",
        ),
        ("exception_connect_database.sql", "dbt tried to connect to the database"),
    ],
)
@pytest.mark.dbt
def test__templater_dbt_handle_exceptions(
    in_dbt_project_dir, dbt_templater, fname, exception_msg  # noqa
):
    """Test that exceptions during compilation are returned as violation."""
    from dbt.adapters.factory import get_adapter

    src_fpath = "../dbt/error_models/" + fname
    target_fpath = "models/my_new_project/" + fname
    # We move the file that throws an error in and out of the project directory
    # as dbt throws an error if a node fails to parse while computing the DAG
    os.rename(src_fpath, target_fpath)
    try:
        _, violations = dbt_templater.process(
            in_str="",
            fname=target_fpath,
            config=FluffConfig(configs=DBT_FLUFF_CONFIG),
        )
    finally:
        get_adapter(dbt_templater.dbt_config).connections.release()
        os.rename(target_fpath, src_fpath)
    assert violations
    # NB: Replace slashes to deal with different plaform paths being returned.
    assert violations[0].desc().replace("\\", "/").startswith(exception_msg)
