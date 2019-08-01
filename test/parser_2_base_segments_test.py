""" The Test file for The New Parser (Base Segment Classes) """

from sqlfluff.parser_2.markers import FilePositionMarker
from sqlfluff.parser_2.base_segments import RawSegment


def test__parser_2__base_segments_raw():
    fp = FilePositionMarker.from_fresh()
    raw_seg = RawSegment('foobar', fp)
    # Check Segment Return
    assert raw_seg.segments == []
    assert raw_seg.raw == 'foobar'
    # Check Formatting and Stringification
    assert str(raw_seg) == repr(raw_seg) == "<RawSegment: ([0](1, 1, 1)) 'foobar'>"
    assert (raw_seg.stringify(ident=1, tabsize=2, pos_idx=20, raw_idx=35)
            == "  RawSegment:       [0](1, 1, 1)   'foobar'\n")
