""" The Test file for SQLFluff """

from sqlfluff.linter import Linter


# ############## LINTER TESTS
def test__linter__path_from_paths():
    lntr = Linter()
    paths = lntr.paths_from_path('test/fixtures/lexer')
    # NB This test might fail on Linux or Mac - should probably correct...
    assert paths == set(['test\\fixtures\\lexer\\block_comment.sql', 'test\\fixtures\\lexer\\inline_comment.sql', 'test\\fixtures\\lexer\\basic.sql'])


def test__linter__path_from_paths_dot():
    lntr = Linter()
    paths = lntr.paths_from_path('.')
    # NB This test might fail on Linux or Mac - should probably correct...
    # Use set theory to check that we get AT LEAST these files
    assert set(paths) >= set(['test\\fixtures\\lexer\\block_comment.sql', 'test\\fixtures\\lexer\\inline_comment.sql', 'test\\fixtures\\lexer\\basic.sql'])


def test__linter__lint_file():
    lntr = Linter()
    lnt = lntr.lint_path('test/fixtures/linter/indentation_errors.sql')
    # lets make an object of the codes, line numbers and positions of violations
    violations = [(v.rule.code, v.chunk.line_no, v.chunk.start_pos) for v in lnt]
    # Check we get the trialing whitespace violation
    assert ('L001', 4, 22) in violations
    # Check we get the mixed indentation errors
    assert ('L002', 3, 0) in violations
    assert ('L002', 4, 0) in violations
    # Check we get the space multiple violations
    assert ('L003', 3, 0) in violations
