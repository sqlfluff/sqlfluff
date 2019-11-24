"""The Test file for the linter class."""

import pytest

from sqlfluff.linter import Linter, LintingResult
from sqlfluff.config import FluffConfig


def normalise_paths(paths):
    """Test normalising paths.

    NB Paths on difference platforms might look different, so this
    makes them comparable.
    """
    return set([pth.replace("/", '.').replace("\\", ".") for pth in paths])


def test__linter__path_from_paths__dir():
    """Test extracting paths from directories."""
    lntr = Linter(config=FluffConfig())
    paths = lntr.paths_from_path('test/fixtures/lexer')
    assert normalise_paths(paths) == set([
        'test.fixtures.lexer.block_comment.sql',
        'test.fixtures.lexer.inline_comment.sql',
        'test.fixtures.lexer.basic.sql'])


def test__linter__path_from_paths__file():
    """Test extracting paths from a file path."""
    lntr = Linter(config=FluffConfig())
    paths = lntr.paths_from_path('test/fixtures/linter/indentation_errors.sql')
    assert normalise_paths(paths) == set(['test.fixtures.linter.indentation_errors.sql'])


def test__linter__path_from_paths__dot():
    """Test extracting paths from a dot."""
    lntr = Linter(config=FluffConfig())
    paths = lntr.paths_from_path('.')
    # Use set theory to check that we get AT LEAST these files
    assert normalise_paths(paths) >= set(['test.fixtures.lexer.block_comment.sql', 'test.fixtures.lexer.inline_comment.sql', 'test.fixtures.lexer.basic.sql'])


def test__linter__nested_config_tests():
    """Test linting with overriden config in nested paths.

    This test lives with the linter tests rather than the config
    tests mostly because (while it tests configuration) it acts
    mostly like a linter test.
    """
    lntr = Linter(config=FluffConfig(overrides=dict(exclude_rules='L002')))
    lnt = lntr.lint_path('test/fixtures/config/inheritance_b')
    violations = lnt.check_tuples(by_path=True)
    for k in violations:
        if k.endswith('nested\\example.sql'):
            assert ('L003', 1, 1) in violations[k]
            assert ('L009', 1, 12) in violations[k]
            assert 'L002' not in [c[0] for c in violations[k]]
        elif k.endswith('inheritance_b\\example.sql'):
            assert ('L003', 1, 1) in violations[k]
            assert 'L002' not in [c[0] for c in violations[k]]
            assert 'L009' not in [c[0] for c in violations[k]]


def test__linter__lint_file_indentation():
    """Test the linter finds indentation errors."""
    lntr = Linter(config=FluffConfig())
    lnt = lntr.lint_path('test/fixtures/linter/indentation_errors.sql')
    violations = lnt.check_tuples()
    # Check we get the trialing whitespace violation
    assert ('L001', 4, 24) in violations
    # Check we get the mixed indentation errors
    assert ('L002', 3, 1) in violations
    assert ('L002', 4, 1) in violations
    # Check we get the space multiple violations
    assert ('L003', 3, 1) in violations
    # Check we get the mixed indentation errors between lines
    assert ('L004', 5, 1) in violations


def test__linter__lint_file_whitespace():
    """Test the linter finds whitespace errors."""
    lntr = Linter(config=FluffConfig())
    lnt = lntr.lint_path('test/fixtures/linter/whitespace_errors.sql')
    violations = lnt.check_tuples()
    # Check we get comma (with leading space/newline) whitespace errors
    assert ('L005', 2, 9) in violations
    assert ('L005', 3, 33) in violations
    # Check we get comma (with incorrect trailing space) whitespace errors
    assert ('L008', 3, 12) in violations
    # Check for no false positives on line 4 or 5
    assert not any([v[0] == 'L008' and v[1] == 4 for v in violations])
    assert not any([v[1] == 5 for v in violations])


def test__linter__lint_file_operators():
    """Test linting operators."""
    lntr = Linter(config=FluffConfig())
    lnt = lntr.lint_path('test/fixtures/linter/operator_errors.sql')
    violations = lnt.check_tuples()
    # Check we get operator whitespace errors
    assert ('L006', 3, 8) in violations
    assert ('L006', 4, 10) in violations
    assert ('L007', 5, 9) in violations
    # Check it works with brackets
    assert ('L006', 7, 6) in violations
    assert ('L006', 7, 7) in violations
    assert ('L006', 7, 9) in violations
    assert ('L006', 7, 10) in violations
    assert ('L006', 7, 12) in violations
    assert ('L006', 7, 13) in violations


def test__linter__lint_file_operators_negative():
    """Test that negative signs don't get linted wrongly."""
    lntr = Linter(config=FluffConfig(overrides=dict(rules='L006')))
    lnt = lntr.lint_paths(['test/fixtures/linter/operator_errors_negative.sql'])
    violations = lnt.check_tuples()
    # Check we DO get a violation on line 2
    assert ('L006', 2, 6) in violations
    # Check we DON'T get a violation on line 3
    assert not any([v[1] == 3 for v in violations])


def test__linter__lint_file_operators_star():
    """Test the exception to the operator rule, allowing a star in brackets."""
    lntr = Linter(config=FluffConfig())
    lnt = lntr.lint_string("SELECT COUNT(*) FROM tbl\n")
    violations = lnt.check_tuples()
    # Check that this is allowed
    assert violations == []


@pytest.mark.parametrize(
    "path",
    [
        'test/fixtures/linter/indentation_errors.sql',
        'test/fixtures/linter/whitespace_errors.sql'
    ]
)
def test__linter__lint_string_vs_file(path):
    """Test the linter finds the same things on strings and files."""
    with open(path, 'r') as f:
        sql_str = f.read()
    lntr = Linter(config=FluffConfig())
    assert (lntr.lint_string(sql_str).check_tuples()
            == lntr.lint_path(path).check_tuples())


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
    assert lr.combine_dicts(a, b, r) == dict(a=3, b=123, f=876.321, h=19, i=321.0, j=23478, z=22)
