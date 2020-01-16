"""The Test file for the linter class."""

import pytest

from sqlfluff.linter import Linter, LintingResult
from sqlfluff.config import FluffConfig


def normalise_paths(paths):
    """Test normalising paths.

    NB Paths on difference platforms might look different, so this
    makes them comparable.
    """
    return {pth.replace("/", '.').replace("\\", ".") for pth in paths}


def test__linter__path_from_paths__dir():
    """Test extracting paths from directories."""
    lntr = Linter(config=FluffConfig())
    paths = lntr.paths_from_path('test/fixtures/lexer')
    assert normalise_paths(paths) == {
        'test.fixtures.lexer.block_comment.sql',
        'test.fixtures.lexer.inline_comment.sql',
        'test.fixtures.lexer.basic.sql'
    }


def test__linter__path_from_paths__file():
    """Test extracting paths from a file path."""
    lntr = Linter(config=FluffConfig())
    paths = lntr.paths_from_path('test/fixtures/linter/indentation_errors.sql')
    assert normalise_paths(paths) == {'test.fixtures.linter.indentation_errors.sql'}


def test__linter__path_from_paths__dot():
    """Test extracting paths from a dot."""
    lntr = Linter(config=FluffConfig())
    paths = lntr.paths_from_path('.')
    # Use set theory to check that we get AT LEAST these files
    assert normalise_paths(paths) >= {
        'test.fixtures.lexer.block_comment.sql',
        'test.fixtures.lexer.inline_comment.sql',
        'test.fixtures.lexer.basic.sql'
    }


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
