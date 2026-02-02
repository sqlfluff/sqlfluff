"""Test the BaseSegment class."""

import pickle

import pytest

from sqlfluff.core.parser import BaseSegment, PositionMarker, RawSegment
from sqlfluff.core.parser.segments.base import PathStep
from sqlfluff.core.rules.base import LintFix
from sqlfluff.core.templaters import TemplatedFile


def test__parser__base_segments_type(DummySegment):
    """Test the .is_type() method."""
    assert BaseSegment.class_is_type("base")
    assert not BaseSegment.class_is_type("foo")
    assert not BaseSegment.class_is_type("foo", "bar")
    assert DummySegment.class_is_type("dummy")
    assert DummySegment.class_is_type("base")
    assert DummySegment.class_is_type("base", "foo", "bar")


def test__parser__base_segments_class_types(DummySegment):
    """Test the metaclass ._class_types attribute."""
    assert DummySegment._class_types == {"dummy", "base"}


def test__parser__base_segments_descendant_type_set(
    raw_segments, DummySegment, DummyAuxSegment
):
    """Test the .descendant_type_set() method."""
    test_seg = DummySegment([DummyAuxSegment(raw_segments)])
    assert test_seg.descendant_type_set == {"raw", "base", "dummy_aux"}


def test__parser__base_segments_direct_descendant_type_set(
    raw_segments, DummySegment, DummyAuxSegment
):
    """Test the .direct_descendant_type_set() method."""
    test_seg = DummySegment([DummyAuxSegment(raw_segments)])
    assert test_seg.direct_descendant_type_set == {"base", "dummy_aux"}


def test__parser__base_segments_to_tuple_a(raw_segments, DummySegment, DummyAuxSegment):
    """Test the .to_tuple() method."""
    test_seg = DummySegment([DummyAuxSegment(raw_segments)])
    assert test_seg.to_tuple() == (
        "dummy",
        (("dummy_aux", (("raw", ()), ("raw", ()))),),
    )


def test__parser__base_segments_to_tuple_b(raw_segments, DummySegment, DummyAuxSegment):
    """Test the .to_tuple() method."""
    test_seg = DummySegment(
        [DummyAuxSegment(raw_segments + (DummyAuxSegment(raw_segments[:1]),))]
    )
    assert test_seg.to_tuple() == (
        "dummy",
        (("dummy_aux", (("raw", ()), ("raw", ()), ("dummy_aux", (("raw", ()),)))),),
    )


def test__parser__base_segments_to_tuple_c(raw_segments, DummySegment, DummyAuxSegment):
    """Test the .to_tuple() method with show_raw=True."""
    test_seg = DummySegment(
        [DummyAuxSegment(raw_segments + (DummyAuxSegment(raw_segments[:1]),))]
    )
    assert test_seg.to_tuple(show_raw=True) == (
        "dummy",
        (
            (
                "dummy_aux",
                (
                    ("raw", "foobar"),
                    ("raw", ".barfoo"),
                    ("dummy_aux", (("raw", "foobar"),)),
                ),
            ),
        ),
    )


def test__parser__base_segments_as_record_a(
    raw_segments, DummySegment, DummyAuxSegment
):
    """Test the .as_record() method.

    NOTE: In this test, note that there are lists, as some segment types
    are duplicated within their parent segment.
    """
    test_seg = DummySegment([DummyAuxSegment(raw_segments)])
    assert test_seg.as_record() == {
        "dummy": {"dummy_aux": [{"raw": None}, {"raw": None}]}
    }


def test__parser__base_segments_as_record_b(
    raw_segments, DummySegment, DummyAuxSegment
):
    """Test the .as_record() method.

    NOTE: In this test, note that there are no lists, every segment type
    is unique within it's parent segment, and so there is no need.
    """
    test_seg = DummySegment(
        [DummyAuxSegment(raw_segments[:1] + (DummyAuxSegment(raw_segments[:1]),))]
    )
    assert test_seg.as_record() == {
        "dummy": {"dummy_aux": {"raw": None, "dummy_aux": {"raw": None}}}
    }


def test__parser__base_segments_as_record_c(
    raw_segments, DummySegment, DummyAuxSegment
):
    """Test the .as_record() method with show_raw=True.

    NOTE: In this test, note that there are no lists, every segment type
    is unique within it's parent segment, and so there is no need.
    """
    test_seg = DummySegment(
        [DummyAuxSegment(raw_segments[:1] + (DummyAuxSegment(raw_segments[:1]),))]
    )
    assert test_seg.as_record(show_raw=True) == {
        "dummy": {"dummy_aux": {"raw": "foobar", "dummy_aux": {"raw": "foobar"}}}
    }


def test__parser__base_segments_count_segments(
    raw_segments, DummySegment, DummyAuxSegment
):
    """Test the .count_segments() method."""
    test_seg = DummySegment([DummyAuxSegment(raw_segments)])
    assert test_seg.count_segments() == 4
    assert test_seg.count_segments(raw_only=True) == 2


@pytest.mark.parametrize(
    "list_in, result",
    [
        (["foo"], False),
        (["foo", " "], True),
        ([" ", "foo", " "], True),
        ([" ", "foo"], True),
        ([" "], True),
        (["foo", " ", "foo"], False),
    ],
)
def test__parser_base_segments_validate_non_code_ends(
    generate_test_segments, DummySegment, list_in, result
):
    """Test BaseSegment.validate_non_code_ends()."""
    if result:
        # Assert that it _does_ raise an exception.
        with pytest.raises(AssertionError):
            # Validation happens on instantiation.
            seg = DummySegment(segments=generate_test_segments(list_in))
    else:
        # Check that it _doesn't_ raise an exception...
        seg = DummySegment(segments=generate_test_segments(list_in))
        # ...even when explicitly validating.
        seg.validate_non_code_ends()


def test__parser__base_segments_path_to(raw_segments, DummySegment, DummyAuxSegment):
    """Test the .path_to() method."""
    test_seg_a = DummyAuxSegment(raw_segments)
    test_seg_b = DummySegment([test_seg_a])
    # With a direct parent/child relationship we only get
    # one element of path.
    # NOTE: All the dummy segments return True for .is_code()
    # so that means the do appear in code_idxs.
    assert test_seg_b.path_to(test_seg_a) == [PathStep(test_seg_b, 0, 1, (0,))]
    # With a three segment chain - we get two path elements.
    assert test_seg_b.path_to(raw_segments[0]) == [
        PathStep(test_seg_b, 0, 1, (0,)),
        PathStep(test_seg_a, 0, 2, (0, 1)),
    ]
    assert test_seg_b.path_to(raw_segments[1]) == [
        PathStep(test_seg_b, 0, 1, (0,)),
        PathStep(test_seg_a, 1, 2, (0, 1)),
    ]


def test__parser__base_segments_stubs():
    """Test stub methods that have no implementation in base class."""
    template = TemplatedFile.from_string("foobar")
    rs1 = RawSegment("foobar", PositionMarker(slice(0, 6), slice(0, 6), template))
    base_segment = BaseSegment(segments=[rs1])

    with pytest.raises(NotImplementedError):
        base_segment.edit("foo")


def test__parser__base_segments_raw(raw_seg):
    """Test raw segments behave as expected."""
    # Check Segment Return
    assert raw_seg.segments == ()
    assert raw_seg.raw == "foobar"
    # Check Formatting and Stringification
    assert str(raw_seg) == repr(raw_seg) == "<CodeSegment: ([L:  1, P:  1]) 'foobar'>"
    assert (
        raw_seg.stringify(ident=1, tabsize=2)
        == "[L:  1, P:  1]      |  raw:                                                "
        "        'foobar'\n"
    )
    # Check tuple
    assert raw_seg.to_tuple() == ("raw", ())
    # Check tuple
    assert raw_seg.to_tuple(show_raw=True) == ("raw", "foobar")


def test__parser__base_segments_base(raw_segments, fresh_ansi_dialect, DummySegment):
    """Test base segments behave as expected."""
    base_seg = DummySegment(raw_segments)
    # Check we assume the position correctly
    assert (
        base_seg.pos_marker.start_point_marker()
        == raw_segments[0].pos_marker.start_point_marker()
    )
    assert (
        base_seg.pos_marker.end_point_marker()
        == raw_segments[-1].pos_marker.end_point_marker()
    )

    # Check that we correctly reconstruct the raw
    assert base_seg.raw == "foobar.barfoo"
    # Check tuple
    assert base_seg.to_tuple() == (
        "dummy",
        (raw_segments[0].to_tuple(), raw_segments[1].to_tuple()),
    )
    # Check Formatting and Stringification
    assert str(base_seg) == repr(base_seg) == "<DummySegment: ([L:  1, P:  1])>"
    assert base_seg.stringify(ident=1, tabsize=2) == (
        "[L:  1, P:  1]      |  dummy:\n"
        "[L:  1, P:  1]      |    raw:                                                 "
        "     'foobar'\n"
        "[L:  1, P:  7]      |    raw:                                                 "
        "     '.barfoo'\n"
    )


def test__parser__base_segments_raw_compare():
    """Test comparison of raw segments."""
    template = TemplatedFile.from_string("foobar")
    rs1 = RawSegment("foobar", PositionMarker(slice(0, 6), slice(0, 6), template))
    rs2 = RawSegment("foobar", PositionMarker(slice(0, 6), slice(0, 6), template))
    assert rs1 == rs2


def test__parser__base_segments_base_compare(DummySegment, DummyAuxSegment):
    """Test comparison of base segments."""
    template = TemplatedFile.from_string("foobar")
    rs1 = RawSegment("foobar", PositionMarker(slice(0, 6), slice(0, 6), template))
    rs2 = RawSegment("foobar", PositionMarker(slice(0, 6), slice(0, 6), template))

    ds1 = DummySegment([rs1])
    ds2 = DummySegment([rs2])
    dsa2 = DummyAuxSegment([rs2])

    # Check for equality
    assert ds1 == ds2
    # Check a different match on the same details are not the same
    assert ds1 != dsa2


def test__parser__base_segments_pickle_safe(raw_segments):
    """Test pickling and unpickling of BaseSegment."""
    test_seg = BaseSegment([BaseSegment(raw_segments)])
    test_seg.set_as_parent()
    pickled = pickle.dumps(test_seg)
    result_seg = pickle.loads(pickled)
    assert test_seg == result_seg
    # Check specifically the treatment of the parent position.
    assert result_seg.segments[0].get_parent()[0] is result_seg


def test__parser__base_segments_copy_isolation(DummySegment, raw_segments):
    """Test copy isolation in BaseSegment.

    First on one of the raws and then on the dummy segment.
    """
    # On a raw
    a_seg = raw_segments[0]
    a_copy = a_seg.copy()
    assert a_seg is not a_copy
    assert a_seg == a_copy
    assert a_seg.pos_marker is a_copy.pos_marker
    a_copy.pos_marker = None
    assert a_copy.pos_marker is None
    assert a_seg.pos_marker is not None

    # On a base
    b_seg = DummySegment(segments=raw_segments)
    b_copy = b_seg.copy()
    assert b_seg is not b_copy
    assert b_seg == b_copy
    assert b_seg.pos_marker is b_copy.pos_marker
    b_copy.pos_marker = None
    assert b_copy.pos_marker is None
    assert b_seg.pos_marker is not None

    # On addition to a lint Fix
    fix = LintFix("replace", a_seg, [b_seg])
    for s in fix.edit:
        assert not s.pos_marker
    assert b_seg.pos_marker


def test__parser__base_segments_parent_ref(DummySegment, raw_segments):
    """Test getting and setting parents on BaseSegment."""
    # Check initially no parent (because not set)
    assert not raw_segments[0].get_parent()
    # Add it to a segment (which also sets the parent value)
    seg = DummySegment(segments=raw_segments)
    # The DummySegment shouldn't have a parent.
    assert seg.get_parent() is None
    assert seg.segments[0].get_parent()[0] is seg
    assert seg.segments[1].get_parent()[0] is seg
    # Remove segment from parent, but don't unset.
    # Should still check an return None.
    seg_0 = seg.segments[0]
    seg.segments = seg.segments[1:]
    assert seg_0 not in seg.segments
    assert not seg_0.get_parent()
    # Check the other still works.
    assert seg.segments[0].get_parent()[0]


def test__parser__raw_segment_raw_normalized():
    """Test comparison of raw segments."""
    template = TemplatedFile.from_string('"a"""."e"')
    rs1 = RawSegment(
        '"a"""',
        PositionMarker(slice(0, 5), slice(0, 5), template),
        quoted_value=(r'"((?:[^"]|"")*)"', 1),
        escape_replacements=[('""', '"')],
        casefold=str.upper,
    )
    rs2 = RawSegment(
        ".",
        PositionMarker(slice(6, 7), slice(6, 7), template),
    )
    rs3 = RawSegment(
        '"e"',
        PositionMarker(slice(8, 10), slice(8, 10), template),
        quoted_value=(r'"((?:[^"]|"")*)"', 1),
        escape_replacements=[('""', '"')],
        casefold=str.upper,
    )
    bs1 = BaseSegment(
        (
            rs1,
            rs2,
            rs3,
        ),
        PositionMarker(slice(0, 10), slice(0, 10), template),
    )
    assert rs1.raw == '"a"""'
    assert rs1.raw_normalized(False) == 'a"'
    assert rs1.raw_normalized() == 'A"'
    assert rs2.raw == "."
    assert rs2.raw_normalized(False) == "."
    assert rs2.raw_normalized() == "."
    assert rs3.raw == '"e"'
    assert rs3.raw_normalized(False) == "e"
    assert rs3.raw_normalized() == "E"
    assert bs1.raw == '"a"""."e"'
    assert bs1.raw_normalized() == 'A".E'


def test__parser__base_segments_structural_simplify_with_position():
    """Test structural_simplify with 3-element tuple (with position)."""
    # This covers lines 603 and 614 in base.py
    pos_info = {"start_line_no": 1}
    elem = ("key", "value", pos_info)
    result = BaseSegment.structural_simplify(elem)
    assert result == {"key": "value", "start_line_no": 1}

    # Also test with nested structure
    elem_nested = ("parent", (("child", "val", pos_info),), pos_info)
    result_nested = BaseSegment.structural_simplify(elem_nested)
    assert result_nested["start_line_no"] == 1
    assert result_nested["parent"]["child"] == "val"
    assert result_nested["parent"]["start_line_no"] == 1
