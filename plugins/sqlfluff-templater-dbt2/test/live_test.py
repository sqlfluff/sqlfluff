"""Opt-in end-to-end validation against an installed dbt#16870 runtime build."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from sqlfluff_templater_dbt2.templater import Dbt2Templater

from sqlfluff.core import FluffConfig, Linter
from sqlfluff.core.errors import SQLParseError, SQLTemplaterError

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.environ.get("SQLFLUFF_DBT2_INTEGRATION") != "1",
        reason="Set SQLFLUFF_DBT2_INTEGRATION=1 with a dbt#16870 build installed",
    ),
]


def test_live_lint_fix_and_cli(tmp_path, monkeypatch):
    """Compile a project, fix Jinja source, recompile and persist fixes through the CLI."""
    monkeypatch.setattr("tempfile.tempdir", str(tmp_path))
    project = tmp_path / "project"
    shutil.copytree(Path(__file__).parent / "fixtures/project", project)
    model = project / "models/probe.sql"
    source = model.read_text(encoding="utf-8")
    settings = {"project_dir": str(project), "profiles_dir": str(project)}
    config = FluffConfig(
        configs={
            "core": {
                "dialect": "duckdb",
                "templater": "dbt2",
                "rules": "CP01",
                "use_rust_parser": False,
            },
            "templater": {"dbt2": settings},
            "rules": {"capitalisation.keywords": {"capitalisation_policy": "upper"}},
        }
    )
    trace = Dbt2Templater()._runtime(source, str(model), settings)
    assert "99 as base_value" not in trace["rendered"]
    assert trace["source"] == source
    linter = Linter(config=config)
    result = linter.lint_string(source, fname=str(model), fix=True)
    assert not result.get_violations(types=(SQLTemplaterError, SQLParseError))
    fixed = result.fix_string()[0]
    expected = (
        source.replace("select ", "SELECT ")
        .replace(" as ", " AS ")
        .replace(" from ", " FROM ")
        .replace("union all", "UNION ALL")
    )
    assert fixed == expected
    model.write_text(fixed, encoding="utf-8")
    again = linter.lint_string(fixed, fname=str(model), fix=True)
    assert not again.get_violations()
    assert again.fix_string()[0] == fixed

    model.write_text(source, encoding="utf-8")
    ini = project / "lint.ini"
    ini.write_text(
        "[sqlfluff]\ntemplater = dbt2\ndialect = duckdb\nrules = CP01\n"
        f"[sqlfluff:templater:dbt2]\nproject_dir = {project}\nprofiles_dir = {project}\n"
        "[sqlfluff:rules:capitalisation.keywords]\ncapitalisation_policy = upper\n",
        encoding="utf-8",
    )
    # Use the same writable temp parent in the fresh CLI process.
    run = subprocess.run(
        [
            sys.executable,
            "-m",
            "sqlfluff",
            "fix",
            "--ignore-local-config",
            "--config",
            str(ini),
            str(model),
        ],
        capture_output=True,
        encoding="utf-8",
        timeout=300,
        env={
            **os.environ,
            "TMP": str(tmp_path),
            "TEMP": str(tmp_path),
            "TMPDIR": str(tmp_path),
        },
    )
    assert run.returncode == 0, (run.stdout, run.stderr)
    assert model.read_text(encoding="utf-8") == expected
