"""Test the behaviour of the unparsable routines."""

import pytest
import logging

from typing import Optional, Any

from sqlfluff.core import FluffConfig, Linter
from sqlfluff.core.parser import Lexer, BaseSegment, RawSegment
from sqlfluff.core.parser.context import ParseContext


# NOTE: Being specific on the segment ref helps to avoid crazy nesting.
@pytest.mark.parametrize(
    "segmentref,dialect,raw,structure",
    [
        (
            # The first here makes sure all of this works from the outer
            # segment, but for other tests we should aim to be more specific.
            None,
            "ansi",
            "SELECT 1 1",
            (
                "file",
                (
                    (
                        "statement",
                        (
                            (
                                "select_statement",
                                (
                                    (
                                        "select_clause",
                                        (
                                            ("keyword", "SELECT"),
                                            ("whitespace", " "),
                                            (
                                                "select_clause_element",
                                                (("numeric_literal", "1"),),
                                            ),
                                            (
                                                "unparsable",
                                                (
                                                    ("whitespace", " "),
                                                    ("numeric_literal", "1"),
                                                ),
                                            ),
                                        ),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
        ),
        (
            "SelectClauseSegment",
            "ansi",
            "SELECT 1 1",
            (
                "select_clause",
                (
                    ("keyword", "SELECT"),
                    ("whitespace", " "),
                    (
                        "select_clause_element",
                        (("numeric_literal", "1"),),
                    ),
                    # We should get a single unparsable section
                    # here at the end.
                    (
                        "unparsable",
                        (
                            ("whitespace", " "),
                            ("numeric_literal", "1"),
                        ),
                    ),
                ),
            ),
        ),
    ],
)
def test_dialect_unparsable(
    segmentref: Optional[str], dialect: str, raw: str, structure: Any
):
    """Test the structure of unparsables."""
    config = FluffConfig(overrides=dict(dialect=dialect))

    # Get the referenced object (if set, otherwise root)
    if segmentref:
        Seg = config.get("dialect_obj").ref(segmentref)
    else:
        Seg = config.get("dialect_obj").get_root_segment()
    # We only allow BaseSegments as matchables in this test.
    assert issubclass(Seg, BaseSegment)
    assert not issubclass(Seg, RawSegment)

    # Lex the raw string.
    lex = Lexer(config=config)
    seg_list, vs = lex.lex(raw)
    assert not vs
    print(seg_list)

    # Construct an unparsed segment
    seg = Seg(seg_list, pos_marker=seg_list[0].pos_marker)
    # Perform the match (THIS IS THE MEAT OF THE TEST)
    ctx = ParseContext.from_config(config)
    result = seg.parse(parse_context=ctx)

    print(result)
    assert len(result) == 1
    parsed = result[0]
    assert isinstance(parsed, Seg)

    assert parsed.to_tuple(show_raw=True) == structure
