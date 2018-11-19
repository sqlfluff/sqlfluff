""" The Test file for SQLFluff """

from six import StringIO

from sqlfluff.linter import LintedFile
from sqlfluff.chunks import PositionedChunk, PositionedCorrection


def test__linter__linted_file__apply_corrections_to_fileobj():
    chunk = PositionedChunk('foofoofoo', 9, 2, None)
    fo = StringIO("12345678\n123456789foofoofoo654fish\n1234567")
    LintedFile.apply_corrections_to_fileobj(fo, [PositionedCorrection(chunk, 'bar')])
    assert fo.getvalue() == "12345678\n123456789bar654fish\n1234567"
