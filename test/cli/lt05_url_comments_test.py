"""End-to-end coverage for the LT05 URL comment configuration."""

import json
import subprocess
import sys

import pytest


@pytest.mark.parametrize("ignore_urls", [False, True])
def test_cli_ignore_url_comment_lines(tmp_path, ignore_urls):
    """Read config from disk and preserve ordinary long-line diagnostics."""
    config = tmp_path / ".sqlfluff"
    config.write_text(
        "[sqlfluff]\ndialect = ansi\nrules = LT05\nmax_line_length = 30\n"
        + (
            "[sqlfluff:rules:layout.long_lines]\nignore_url_comment_lines = True\n"
            if ignore_urls
            else ""
        )
    )
    url = "https://example.com/a/long/reference"
    url_file = tmp_path / "url.sql"
    url_sql = f"-- {url}\nSELECT 1;\n"
    url_file.write_text(url_sql)
    other_file = tmp_path / "other.sql"
    other_file.write_text(
        "-- This ordinary comment is still too long.\n"
        f"-- See {url}\n"
        f"-- {url} for details\n"
        f"SELECT 1; -- {url}\n"
        f"SELECT 1; /* {url} */\n"
        f"/* {url} */ SELECT 1;\n"
        f"SELECT '-- {url}';\n"
        f"{{% set value = 1 %}}-- {url}\n"
        f"{{{{ '-- {url}' }}}}\n"
    )

    def run_cli(command, *args):
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "sqlfluff",
                command,
                "--ignore-local-config",
                "--config",
                str(config),
                *args,
            ],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            check=False,
        )

    linted = run_cli("lint", "--format", "json", str(tmp_path))
    assert linted.returncode == 1, linted.stderr
    results = {result["filepath"]: result for result in json.loads(linted.stdout)}
    url_violations = results[str(url_file)]["violations"]
    assert [v["code"] for v in url_violations] == ([] if ignore_urls else ["LT05"])
    other_violations = results[str(other_file)]["violations"]
    assert [(v["code"], v["start_line_no"]) for v in other_violations] == [
        ("LT05", line) for line in range(1, 10)
    ]

    # Fixing an exempt URL must leave its bytes intact, and linting the
    # resulting file must succeed. Without the option it remains unfixable.
    fixed = run_cli("fix", "--force", str(url_file))
    assert fixed.returncode == (0 if ignore_urls else 1), fixed.stdout + fixed.stderr
    assert url_file.read_text() == url_sql
    linted_again = run_cli("lint", "--format", "json", str(url_file))
    assert linted_again.returncode == (0 if ignore_urls else 1)
