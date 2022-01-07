"""Tests for the dbt templater."""

import os
from unittest import mock

import pytest

from sqlfluff.core import FluffConfig, Linter
from sqlfluff_templater_dbt.templater import DBT_VERSION_TUPLE
from test.fixtures.dbt.templater import (  # noqa: F401
    DBT_FLUFF_CONFIG,
    dbt_templater,
    project_dir,
)
from sqlfluff_templater_dbt.templater import DbtFailedToConnectException


@pytest.mark.parametrize(
    "fname",
    [
        "incremental.sql",
        "single_trailing_newline.sql",
    ],
)
def test__dbt_templated_models_do_not_raise_lint_error(
    project_dir, fname  # noqa: F811
):
    """Test that templated dbt models do not raise a linting error."""
    lntr = Linter(config=FluffConfig(configs=DBT_FLUFF_CONFIG))
    lnt = lntr.lint_path(
        path=os.path.join(project_dir, "models/my_new_project/", fname)
    )
    violations = lnt.check_tuples()
    assert len(violations) == 0


@pytest.mark.parametrize(
    "fname,exception_msg",
    [
        (
            "compiler_error.sql",
            "dbt compilation error on file 'models/my_new_project/compiler_error.sql', "
            "Unexpected end of template. Jinja was looking for the following tags: 'endfor'",
        ),
    ],
)
def test__templater_dbt_handle_exceptions(
    project_dir, dbt_templater, fname, exception_msg  # noqa: F811
):
    """Test that exceptions during compilation are returned as violation."""
    from dbt.adapters.factory import get_adapter

    src_fpath = "plugins/sqlfluff-templater-dbt/test/fixtures/dbt/error_models/" + fname
    target_fpath = os.path.abspath(
        os.path.join(project_dir, "models/my_new_project/", fname)
    )
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


@mock.patch("dbt.adapters.postgres.impl.PostgresAdapter.set_relations_cache")
@pytest.mark.dbt_connection_failure
def test__templater_dbt_handle_database_connection_failure(
    set_relations_cache, project_dir, dbt_templater  # noqa: F811
):
    """Test the result of a failed database connection."""
    from dbt.adapters.factory import get_adapter

    set_relations_cache.side_effect = DbtFailedToConnectException("dummy error")

    src_fpath = "plugins/sqlfluff-templater-dbt/test/fixtures/dbt/error_models/exception_connect_database.sql"
    target_fpath = os.path.abspath(
        os.path.join(
            project_dir, "models/my_new_project/exception_connect_database.sql"
        )
    )
    dbt_fluff_config_fail = DBT_FLUFF_CONFIG.copy()
    dbt_fluff_config_fail["templater"]["dbt"][
        "profiles_dir"
    ] = "plugins/sqlfluff-templater-dbt/test/fixtures/dbt/profiles_yml_fail"
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
    assert (
        violations[0]
        .desc()
        .replace("\\", "/")
        .startswith("dbt tried to connect to the database")
    )
