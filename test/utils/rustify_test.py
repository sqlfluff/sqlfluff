"""Ensure dialect generation uses the source checkout in isolated builds."""

import os
import subprocess
import sys
from pathlib import Path

from utils.rustify import SOURCE_DIR, generator_command


def test_generator_imports_checkout_when_another_sqlfluff_is_on_path(tmp_path: Path):
    """A released sqlfluff in the build environment must not replace main."""
    other = tmp_path / "other"
    package = other / "sqlfluff"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("", encoding="utf-8")
    generator = tmp_path / "generator.py"
    generator.write_text("import sqlfluff; print(sqlfluff.__file__)", encoding="utf-8")

    env = {**os.environ, "PYTHONPATH": str(other)}
    baseline = subprocess.run(
        [sys.executable, str(generator)],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    assert Path(baseline.stdout.strip()).resolve() == package / "__init__.py"

    # The entry point must select the checkout before importing dialect_readout.
    entry = subprocess.run(
        [sys.executable, str(SOURCE_DIR.parent / "utils/rustify.py"), "--help"],
        capture_output=True,
        text=True,
        env=env,
    )
    assert entry.returncode == 0, entry.stderr

    result = subprocess.run(
        generator_command(generator, []),
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    assert Path(result.stdout.strip()).resolve() == SOURCE_DIR / "sqlfluff/__init__.py"
