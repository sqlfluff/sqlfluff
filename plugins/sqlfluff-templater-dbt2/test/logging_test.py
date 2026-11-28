"""Report batch compilation through SQLFluff's normal CLI output controls."""

import json
import logging
import subprocess
from unittest.mock import Mock

import pytest
from click.testing import CliRunner
from sqlfluff_templater_dbt2.templater import Dbt2Templater

from sqlfluff.cli.commands import lint
from sqlfluff.cli.formatters import OutputStreamFormatter
from sqlfluff.cli.outputstream import OutputPolicy, TqdmOutput
from sqlfluff.core import FluffConfig
from sqlfluff.core.errors import SQLTemplaterError
from sqlfluff.core.formatter import FormatterInterface

START = "=== [dbt2 templater] Compiling dbt project..."
DONE = "=== [dbt2 templater] Project Compiled."
FAILED = "=== [dbt2 templater] Compilation Failed."


def setup_output(paths):
    """Use the real CLI formatter for a two-file pass."""
    config = FluffConfig(
        configs={
            "core": {"dialect": "ansi", "templater": "dbt2"},
            "templater": {"dbt2": {"project_dir": str(paths[0].parent)}},
        }
    )
    formatter = OutputStreamFormatter(TqdmOutput(config), True, OutputPolicy())
    return config, formatter


def test_batch_progress_precedes_compile_and_is_not_repeated(
    batch_runtime, monkeypatch, capsys, caplog
):
    """A slow batch is announced before subprocess startup, once for all files."""
    paths, calls, _ = batch_runtime
    config, formatter = setup_output(paths)
    run = subprocess.run

    def during_compile(*args, **kwargs):
        assert capsys.readouterr().out == START + "\n"
        return run(*args, **kwargs)

    monkeypatch.setattr(subprocess, "run", during_compile)
    templater = Dbt2Templater()
    with caplog.at_level(logging.DEBUG, logger="sqlfluff.templater"):
        templater.sequence_files(list(map(str, paths)), config, formatter)
        assert capsys.readouterr().out == DONE + "\n"
        for path in paths:
            templater.process(
                in_str=path.read_text(),
                fname=str(path),
                config=config,
                formatter=formatter,
            )
    assert capsys.readouterr().out == ""
    assert len(calls) == 1
    assert "for 2 selected files" in caplog.text
    assert "Loaded dbt2 render artifacts for 2 source files" in caplog.text
    assert caplog.text.count("Using batched dbt2 render trace for") == 2
    assert "dbt2 stdout:\ndbt compile output" in caplog.text
    assert "dbt2 stderr:\ndbt compile diagnostic" in caplog.text


def test_failed_batch_has_no_success_header(batch_runtime, capsys):
    """Report one failed compilation, retaining normal per-file templater errors."""
    paths, calls, failures = batch_runtime
    failures.append(True)
    config, formatter = setup_output(paths)
    templater = Dbt2Templater()
    templater.sequence_files(list(map(str, paths)), config, formatter)
    assert capsys.readouterr().out.splitlines() == [START, FAILED]
    for path in paths:
        with pytest.raises(SQLTemplaterError, match="compile failed"):
            templater.process(
                in_str=path.read_text(),
                fname=str(path),
                config=config,
                formatter=formatter,
            )
    assert capsys.readouterr().out == ""
    assert len(calls) == 1


def test_direct_process_reports_compilation(batch_runtime, capsys):
    """The individual-file fallback uses the same progress messages."""
    paths, _, _ = batch_runtime
    config, formatter = setup_output(paths)
    Dbt2Templater().process(
        in_str=paths[0].read_text(),
        fname=str(paths[0]),
        config=config,
        formatter=formatter,
    )
    assert capsys.readouterr().out.splitlines() == [START, DONE]


@pytest.mark.parametrize("empty", [False, True])
def test_api_and_empty_pass_have_no_stdout(batch_runtime, capsys, empty):
    """Library calls without a formatter and empty selections stay silent."""
    paths, calls, _ = batch_runtime
    config, formatter = setup_output(paths)
    templater = Dbt2Templater()
    if empty:
        templater.sequence_files([], config, formatter)
        assert not calls
    else:
        templater.sequence_files(list(map(str, paths)), config)
        templater.process(
            in_str=paths[0].read_text(), fname=str(paths[0]), config=config
        )
    assert capsys.readouterr() == ("", "")


def test_formatter_without_compilation_headers(batch_runtime, capsys):
    """Custom core formatters need not implement the CLI's compilation extension."""
    paths, _, _ = batch_runtime
    config, _ = setup_output(paths)
    formatter = Mock(spec=FormatterInterface)
    templater = Dbt2Templater()
    templater.sequence_files(list(map(str, paths)), config, formatter)
    templater.process(
        in_str=paths[0].read_text(),
        fname=str(paths[0]),
        config=config,
        formatter=formatter,
    )
    assert capsys.readouterr() == ("", "")


@pytest.mark.parametrize(
    "options,visible", [([], True), (["--quiet"], False), (["--format", "json"], False)]
)
@pytest.mark.parametrize("failure", [False, True])
def test_cli_output_policy(batch_runtime, monkeypatch, options, visible, failure):
    """Human output gets progress; quiet and JSON output retain their contracts."""
    paths, calls, failures = batch_runtime
    if failure:
        failures.append(True)
    project = paths[0].parent
    ini = project / "lint.ini"
    ini.write_text(
        "[sqlfluff]\ntemplater = dbt2\ndialect = ansi\nrules = CP01\n"
        f"[sqlfluff:templater:dbt2]\nproject_dir = {project}\n",
        encoding="utf-8",
    )
    # The CLI configures logging globally. Restore it after each invocation.
    for name in ("sqlfluff", "sqlfluff.parser"):
        logger = logging.getLogger(name)
        for attr in ("handlers", "level", "propagate"):
            monkeypatch.setattr(
                logger, attr, [] if attr == "handlers" else getattr(logger, attr)
            )
    result = CliRunner().invoke(
        lint,
        [
            "--ignore-local-config",
            "--config",
            str(ini),
            "--nocolor",
            *options,
            *map(str, paths),
        ],
    )
    assert result.exit_code == (1 if failure else 0), (result.output, result.exception)
    assert len(calls) == 1
    assert (START in result.stdout) is visible
    assert (DONE in result.stdout) is (visible and not failure)
    assert (FAILED in result.stdout) is (visible and failure)
    assert "dbt compile output" not in result.output
    assert "dbt compile diagnostic" not in result.output
    if "json" in options:
        records = json.loads(result.stdout)
        assert len(records) == 2
        if failure:
            assert all(record["violations"][0]["code"] == "TMP" for record in records)
    if failure:
        assert "compile failed" in result.stdout
