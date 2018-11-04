""" The Test file for SQLFluff """

from sqlfluff.linter import Linter


# ############## LINTER TESTS
def test__linter__path_from_paths():
    lntr = Linter()
    paths = lntr.paths_from_path('test/fixtures')
    # NB This test might fail on Linux or Mac - should probably correct...
    assert paths == set(['test\\fixtures\\lexer\\block_comment.sql', 'test\\fixtures\\lexer\\inline_comment.sql', 'test\\fixtures\\lexer\\basic.sql'])


def test__linter__path_from_paths_dot():
    lntr = Linter()
    paths = lntr.paths_from_path('.')
    # NB This test might fail on Linux or Mac - should probably correct...
    assert paths == set(['test\\fixtures\\lexer\\block_comment.sql', 'test\\fixtures\\lexer\\inline_comment.sql', 'test\\fixtures\\lexer\\basic.sql'])


def test__linter__lint_file():
    lntr = Linter()
    lnt = lntr.lint_path('test/fixtures/lexer/block_comment.sql')
    # Bit of an odd test, but for now it checks no exceptions raised
    assert lnt is None
