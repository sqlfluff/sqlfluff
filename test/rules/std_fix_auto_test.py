"""Automated tests for fixing violations.

Any files in the test/fixtures/linter/autofix directory will be picked up
and automatically tested against the appropriate dialect.
"""

import json
import logging
import os
import shutil
import tempfile
from typing import Optional

import pytest
import yaml

from sqlfluff.core import FluffConfig, Linter
from sqlfluff.core.config import clear_config_caches

# Construct the tests from the filepath
test_cases = []
base_auto_fix_path = ("test", "fixtures", "linter", "autofix")

# Generate the filenames for each dialect from the parser test directory
for dialect in os.listdir(os.path.join(*base_auto_fix_path)):
    # Ignore documentation
    if dialect.endswith(".md"):
        continue
    # assume that d is now the name of a dialect
    dirlist = os.listdir(os.path.join(*base_auto_fix_path, dialect))
    for test_case in dirlist:
        test_cases.append(
            (
                # The dialect
                dialect,
                # The directory name
                test_case,
            )
        )


def make_dialect_path(dialect, fname):
    """Work out how to find paths given a dialect and a file name."""
    return os.path.join("test", "fixtures", "dialects", dialect, fname)


def auto_fix_test(dialect, folder, caplog):
    """A test for roundtrip testing, take a file buffer, lint, fix and lint.

    This is explicitly different from the linter version of this, in that
    it uses the command line rather than the direct api.
    """
    # Log just the rules logger for this test.
    # NOTE: In debugging it may be instructive to enable some of
    # the other loggers listed here to debug particular issues.
    # Enabling all of them results in very long logs so use
    # wisely.
    # caplog.set_level(logging.DEBUG, logger="sqlfluff.templater")
    # caplog.set_level(logging.DEBUG, logger="sqlfluff.lexer")
    caplog.set_level(logging.DEBUG, logger="sqlfluff.linter")
    caplog.set_level(logging.DEBUG, logger="sqlfluff.rules")

    filename = "testing.sql"
    # Lets get the path of a file to use
    tempdir_path = tempfile.mkdtemp()
    filepath = os.path.join(tempdir_path, filename)
    cfgpath = os.path.join(tempdir_path, ".sqlfluff")
    src_filepath = os.path.join(*base_auto_fix_path, dialect, folder, "before.sql")
    cmp_filepath = os.path.join(*base_auto_fix_path, dialect, folder, "after.sql")
    vio_filepath = os.path.join(*base_auto_fix_path, dialect, folder, "violations.json")
    cfg_filepath = os.path.join(*base_auto_fix_path, dialect, folder, ".sqlfluff")
    test_conf_filepath = os.path.join(
        *base_auto_fix_path, dialect, folder, "test-config.yml"
    )

    # Load the config file for the test:
    with open(test_conf_filepath) as cfg_file:
        cfg = yaml.safe_load(cfg_file)
    print("## Config: ", cfg)
    rules: Optional[str] = ",".join(cfg["test-config"].get("rules")).upper()
    if "ALL" in rules:
        rules = None
    raise_on_non_linting_violations = cfg["test-config"].get(
        "raise_on_non_linting_violations", True
    )

    # Open the example file and write the content to it
    print_buff = ""
    with open(filepath, mode="w") as dest_file:
        with open(src_filepath) as source_file:
            for line in source_file:
                dest_file.write(line)
                print_buff += line
    # Copy the config file too
    try:
        with open(cfgpath, mode="w") as dest_file:
            with open(cfg_filepath) as source_file:
                print("## Config File Found.")
                for line in source_file:
                    dest_file.write(line)
    except FileNotFoundError:
        # No config file? No big deal
        print("## No Config File Found.")
        pass
    print(f"## Input file:\n{print_buff}")
    # Do we need to do a violations check?
    try:
        with open(vio_filepath) as vio_file:
            violations = json.load(vio_file)
    except FileNotFoundError:
        # No violations file. Let's not worry
        violations = None

    # Run the fix command
    overrides = {"dialect": dialect}
    if rules:
        overrides["rules"] = rules

    # Clear config caches before loading. The way we move files around
    # makes the filepath based caching inaccurate, which leads to unstable
    # test cases unless we regularly clear the cache.
    clear_config_caches()
    cfg = FluffConfig.from_root(overrides=overrides)
    lnt = Linter(config=cfg)
    res = lnt.lint_path(filepath, fix=True)

    if not res.files:
        raise ValueError("LintedDir empty: Parsing likely failed.")
    print(f"## Templated file:\n{res.tree.raw}")

    # We call the check_tuples here, even to makes sure any non-linting
    # violations are raised, and the test fails.
    vs = set(
        res.check_tuples(
            raise_on_non_linting_violations=raise_on_non_linting_violations
        )
    )
    # If we have a violations structure, let's enforce it.
    if violations:
        # Format the violations file
        expected_vs = set()
        for rule_key in violations["violations"]["linting"]:
            for elem in violations["violations"]["linting"][rule_key]:
                expected_vs.add((rule_key, *elem))
        assert expected_vs == vs

    # Actually do the fixes
    res = res.persist_changes()
    # Read the fixed file
    with open(filepath) as fixed_file:
        fixed_buff = fixed_file.read()
    # Clear up once read
    shutil.rmtree(tempdir_path)
    # Also clear the config cache again so it's not polluted for later tests.
    clear_config_caches()
    # Read the comparison file
    with open(cmp_filepath) as comp_file:
        comp_buff = comp_file.read()

    # Make sure we were successful
    assert res
    # Assert that we fixed as expected
    assert fixed_buff == comp_buff


@pytest.mark.parametrize("dialect,folder", test_cases)
def test__std_fix_auto(dialect, folder, caplog):
    """Automated Fixing Tests."""
    auto_fix_test(dialect=dialect, folder=folder, caplog=caplog)
