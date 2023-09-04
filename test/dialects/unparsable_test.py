"""Test the behaviour of the unparsable routines."""

from typing import Any, Optional

import pytest

from sqlfluff.core import FluffConfig
from sqlfluff.core.parser import BaseSegment, Lexer, RawSegment
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
                                            ("whitespace", " "),
                                            (
                                                "unparsable",
                                                (("numeric_literal", "1"),),
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
                    ("whitespace", " "),
                    # We should get a single unparsable section
                    # here at the end.
                    (
                        "unparsable",
                        (("numeric_literal", "1"),),
                    ),
                ),
            ),
        ),
        # This more complex example looks a little strange, but does
        # reflect current unparsable behaviour. During future work
        # on the parser, the structure of this result may change
        # but it should still result in am unparsable section _within_
        # the brackets, and not just a totally unparsable statement.
        (
            "SelectClauseSegment",
            "ansi",
            "SELECT 1 + (2 2 2)",
            (
                "select_clause",
                (
                    ("keyword", "SELECT"),
                    ("whitespace", " "),
                    (
                        "select_clause_element",
                        (
                            (
                                "expression",
                                (
                                    ("numeric_literal", "1"),
                                    ("whitespace", " "),
                                    ("binary_operator", "+"),
                                    ("whitespace", " "),
                                    (
                                        "bracketed",
                                        (
                                            ("start_bracket", "("),
                                            ("expression", (("numeric_literal", "2"),)),
                                            (
                                                "unparsable",
                                                (
                                                    ("whitespace", " "),
                                                    ("numeric_literal", "2"),
                                                    ("whitespace", " "),
                                                    ("numeric_literal", "2"),
                                                ),
                                            ),
                                            ("end_bracket", ")"),
                                        ),
                                    ),
                                ),
                            ),
                        ),
                    ),
                    # This is a bit odd but it reflects current
                    # behaviour. Ideally it should not be present.
                    (
                        "unparsable",
                        (),
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

    # Construct an unparsed segment
    seg = Seg(seg_list, pos_marker=seg_list[0].pos_marker)
    # Perform the match (THIS IS THE MEAT OF THE TEST)
    ctx = ParseContext.from_config(config)
    result = seg.parse(parse_context=ctx)

    assert len(result) == 1
    parsed = result[0]
    assert isinstance(parsed, Seg)

    assert parsed.to_tuple(show_raw=True) == structure
