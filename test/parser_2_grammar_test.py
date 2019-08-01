""" The Test file for The New Parser (Marker Classes)"""

from sqlfluff.parser_2.markers import FilePositionMarker


def test__parser_2__common_marker():
    # test making one from fresh
    fp1 = FilePositionMarker.from_fresh()
    fp2 = fp1.advance_by('abc')
    fp3 = fp2.advance_by('def\nghi\njlk')
    fp4 = fp3.advance_by('mno', idx=1)
    # check comparisons
    assert fp1 == FilePositionMarker(1, 1, 1, 0)
    assert fp4 > fp3 > fp2 > fp1
    assert fp1 < fp2 < fp3 < fp4
    # Check advance works without newline
    assert fp2 == FilePositionMarker(1, 1, 4, 3)
    assert fp3 == FilePositionMarker(1, 3, 4, 14)
    assert fp4 == FilePositionMarker(2, 3, 7, 17)


def test__parser_2__common_marker_format():
    fp1 = FilePositionMarker(1, 2, 3, 0)
    # Check Formatting Style
    assert str(fp1) == "[0](1, 2, 3)"
