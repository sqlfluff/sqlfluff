""" The Test file for SQLFluff """

from six import StringIO

from sqlfluff.linter import Linter, LintingResult


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
    # Check we get comma (with leading space) whitespace errors
    assert ('L005', 2, 8) in violations
    assert ('L005', 4, 0) in violations
    # Check we get comma (with incorrect trailing space) whitespace errors
    assert ('L008', 3, 11) in violations
    # Check for no false positives on line 4 or 5
    assert not any([v[0] == 'L008' and v[1] == 4 for v in violations])
    assert not any([v[1] == 5 for v in violations])


def test__linter__lint_file_operators():
    lntr = Linter()
    lnt = lntr.lint_path('test/fixtures/linter/operator_errors.sql')
    # Check the Num violations command while we're here
    assert lnt.num_violations() == 3
    violations = lnt.check_tuples()
    # Check we get comma whitespace errors
    assert ('L006', 3, 9) in violations
    assert ('L006', 4, 8) in violations
    assert ('L007', 5, 8) in violations


def test__linter__lint_file_operators_paths():
    """ Same as the above test, but called via lint_paths """
    lntr = Linter()
    lnt = lntr.lint_paths(['test/fixtures/linter/operator_errors.sql'])
    # Check the Num violations command while we're here
    assert lnt.num_violations() == 3
    violations = lnt.check_tuples()
    # Check we get comma whitespace errors
    assert ('L006', 3, 9) in violations
    assert ('L006', 4, 8) in violations
    assert ('L007', 5, 8) in violations


def test__linter__lint_file_operators_negative():
    lntr = Linter()
    f = StringIO(u"SELECT\n    a  -  b as c,\n    -2 as d\n    a - b as e\nFROM tbl\n")
    lnt = lntr.lint_file(f)
    violations = lnt.check_tuples()
    # Check we only get one violation and it's the first
    assert violations == [('L006', 2, 7)]


def test__linter__lint_file_operators_star():
    """ Test the exception to the operator rule, allowing a star in brackets """
    lntr = Linter()
    f = StringIO(u"SELECT COUNT(*) FROM tbl")
    lnt = lntr.lint_file(f)
    violations = lnt.check_tuples()
    # Check that this is allowed
    assert violations == []


def test__linter__linting_result__sum_dicts():
    lr = LintingResult()
    i = {}
    a = dict(a=3, b=123, f=876.321)
    b = dict(a=19, b=321.0, g=23478)
    r = dict(a=22, b=444.0, f=876.321, g=23478)
    assert lr.sum_dicts(a, b) == r
    # Check the identity too
    assert lr.sum_dicts(r, i) == r


def test__linter__linting_result__combine_dicts():
    lr = LintingResult()
    a = dict(a=3, b=123, f=876.321)
    b = dict(h=19, i=321.0, j=23478)
    r = dict(z=22)
    assert lr.combine_dicts(a, b, r) == dict(a=3, b=123, f=876.321, h=19, i=321.0, j=23478, z=22)
