"""Automated tests for fixing violations.

Any files in the /tests/fixtures/linter/autofix directoy will be picked up
and automatically tested against the appropriate dialect.
"""

import pytest
import os
import tempfile
import shutil
import json

from sqlfluff.config import FluffConfig
from sqlfluff.cli.commands import do_fixes
from sqlfluff.linter import Linter


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
        spl = test_case.split("_")
        rules = spl[1]
        rule_list = []
        if len(rules) % 4 != 0:
            raise ValueError(
                "Test case {0!r} is incorrectly formatted!".format(test_case)
            )
        for idx in range(0, len(rules) // 4):
            rule_list.append(rules[idx * 4 : (idx + 1) * 4])
        test_cases.append(
            (
                # The dialect
                dialect,
                # The directory name
                test_case,
                # Rules
                ",".join(rule_list),
            )
        )


def make_dialect_path(dialect, fname):
    """Work out how to find paths given a dialect and a file name."""
    return os.path.join("test", "fixtures", "parser", dialect, fname)


def load_file(dialect, fname):
    """Load a file."""
    with open(make_dialect_path(dialect, fname)) as f:
        raw = f.read()
    return raw


def auto_fix_test(rules, dialect, folder):
    """A test for roundtrip testing, take a file buffer, lint, fix and lint.

    This is explicitly different from the linter version of this, in that
    it uses the command line rather than the direct api.
    """
    filename = "testing.sql"
    # Lets get the path of a file to use
    tempdir_path = tempfile.mkdtemp()
    filepath = os.path.join(tempdir_path, filename)
    cfgpath = os.path.join(tempdir_path, ".sqlfluff")
    src_filepath = os.path.join(*base_auto_fix_path, dialect, folder, "before.sql")
    cmp_filepath = os.path.join(*base_auto_fix_path, dialect, folder, "after.sql")
    vio_filepath = os.path.join(*base_auto_fix_path, dialect, folder, "violations.json")
    cfg_filepath = os.path.join(*base_auto_fix_path, dialect, folder, ".sqlfluff")
    # Open the example file and write the content to it
    print_buff = ""
    with open(filepath, mode="w") as dest_file:
        with open(src_filepath, mode="r") as source_file:
            for line in source_file:
                dest_file.write(line)
                print_buff += line
    # Copy the config file too
    try:
        with open(cfgpath, mode="w") as dest_file:
            with open(cfg_filepath, mode="r") as source_file:
                for line in source_file:
                    dest_file.write(line)
    except FileNotFoundError:
        # No config file? No biggie
        pass
    print("## Input file:\n{0}".format(print_buff))
    # Do we need to do a violations check?
    try:
        with open(vio_filepath, mode="r") as vio_file:
            violations = json.load(vio_file)
    except FileNotFoundError:
        # No violations file. Let's not worry
        violations = None

    # Run the fix command
    cfg = FluffConfig.from_root(overrides=dict(rules=rules, dialect=dialect))
    lnt = Linter(config=cfg)
    res = lnt.lint_path(filepath, fix=True)

    # If we have a violations structure, let's enforce it.
    if violations:
        vs = set(res.check_tuples())
        # Format the violations file
        expected_vs = set()
        for rule_key in violations["violations"]["linting"]:
            for elem in violations["violations"]["linting"][rule_key]:
                expected_vs.add((rule_key, *elem))
        assert expected_vs == vs

    # Actually do the fixes
    res = do_fixes(lnt, res)
    # Read the fixed file
    with open(filepath, mode="r") as fixed_file:
        fixed_buff = fixed_file.read()
    # Clearup once read
    shutil.rmtree(tempdir_path)
    # Read the comparison file
    with open(cmp_filepath, mode="r") as comp_file:
        comp_buff = comp_file.read()

    # Make sure we were successful
    assert res
    # Assert that we fixed as expected
    assert fixed_buff == comp_buff


@pytest.mark.parametrize("dialect,folder,rules", test_cases)
def test__std_fix_auto(dialect, folder, rules):
    """Automated Fixing Tests."""
    auto_fix_test(rules=rules, dialect=dialect, folder=folder)
