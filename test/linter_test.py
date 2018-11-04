""" The Test file for SQLFluff """

from sqlfluff.linter import Linter


# ############## LINTER TESTS
def test__linter__path_from_paths():
    lntr = Linter()
    paths = lntr.paths_from_path('test/fixtures')
    # NB This test might fail on Linux or Mac - should probably correct...
    assert paths == set(['test\\fixtures\\lexer\\block_comment.sql', 'test\\fixtures\\lexer\\inline_comment.sql', 'test\\fixtures\\lexer\\basic.sql'])
