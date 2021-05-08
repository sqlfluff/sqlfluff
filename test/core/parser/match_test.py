"""The Test file for The New Parser (MatchResult Classes)."""

import pytest

from sqlfluff.core.parser.match_result import MatchResult
from sqlfluff.core.parser import RawSegment, FilePositionMarker


@pytest.fixture(scope="module")
def raw_seg():
    """Construct a raw segment as a fixture."""
    fp = FilePositionMarker().advance_by("abc")
    return RawSegment("foobar", fp)


# A set of generator functions to make thing to use Matches with
input_funcs = [
    lambda x: (x,),  # tuple
    lambda x: [x],  # list
    lambda x: x,  # segment
    lambda x: (elem for elem in [x]),  # generator
]


@pytest.mark.parametrize("method", ["from_unmatched", "from_matched"])
@pytest.mark.parametrize("input_func", input_funcs)
def test__parser__match_construct(method, input_func, raw_seg):
    """Test construction of MatchResults."""
    # Let's make our input
    src = input_func(raw_seg)
    # Test construction
    getattr(MatchResult, method)(src)


def test__parser__match_construct_from_empty():
    """Test construction of MatchResults from empty."""
    m = MatchResult.from_empty()
    assert len(m) == 0


@pytest.mark.parametrize("input_func", input_funcs)
def test__parser__match_add(input_func, raw_seg):
    """Test construction of MatchResults."""
    m1 = MatchResult.from_matched([raw_seg])
    # Test adding
    m2 = m1 + input_func(raw_seg)
    # Check it's a match result
    assert isinstance(m2, MatchResult)
    # In all cases, it should also be of length 2
    assert len(m2) == 2
