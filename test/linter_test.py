""" The Test file for SQLFluff """

from sqlfluff.linter import Linter


# ############## LINTER TESTS

def normalise_paths(paths):
    # NB Paths on difference platforms might look different, so this makes them comparable
    return set([pth.replace("/", '.').replace("\\", ".") for pth in paths])


def test__linter__path_from_paths__dir():
    lntr = Linter()
    paths = lntr.paths_from_path('test/fixtures/lexer')
    # NB This test might fail on Linux or Mac - should probably correct...
    assert normalise_paths(paths) == set(['test.fixtures.lexer.block_comment.sql', 'test.fixtures.lexer.inline_comment.sql', 'test.fixtures.lexer.basic.sql'])


def test__linter__path_from_paths__file():
    lntr = Linter()
    paths = lntr.paths_from_path('test/fixtures/linter/indentation_errors.sql')
    assert normalise_paths(paths) == set(['test.fixtures.linter.indentation_errors.sql'])


def test__linter__path_from_paths_dot():
    lntr = Linter()
    paths = lntr.paths_from_path('.')
    # Use set theory to check that we get AT LEAST these files
    assert normalise_paths(paths) >= set(['test.fixtures.lexer.block_comment.sql', 'test.fixtures.lexer.inline_comment.sql', 'test.fixtures.lexer.basic.sql'])


def test__linter__lint_file_indentation():
    lntr = Linter()
    lnt = lntr.lint_path('test/fixtures/linter/indentation_errors.sql')
    violations = lnt.check_tuples()
    # Check we get the trialing whitespace violation
    assert ('L001', 4, 23) in violations
    # Check we get the mixed indentation errors
    assert ('L002', 3, 0) in violations
    assert ('L002', 4, 0) in violations
    # Check we get the space multiple violations
    assert ('L003', 3, 0) in violations
    # Check we get the mixed indentation errors between lines
    assert ('L004', 5, 0) in violations


def test__linter__lint_file_whitespace():
    lntr = Linter()
    lnt = lntr.lint_path('test/fixtures/linter/whitespace_errors.sql')
    violations = lnt.check_tuples()
    # Check we get comma whitespace errors
    assert ('L005', 2, 11) in violations
    assert ('L005', 5, 0) in violations
