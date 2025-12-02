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
                                            ("whitespace", " "),
                                            (
                                                "unparsable",
                                                (
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
    segments, vs = lex.lex(raw)
    assert not vs
    # Strip the end of file token if it's there. It will
    # confuse most segments.
    if segmentref and segments[-1].is_type("end_of_file"):
        segments = segments[:-1]

    ctx = ParseContext.from_config(config)

    # Match against the segment.
    match = Seg.match(segments, 0, ctx)
    result = match.apply(segments)

    assert len(result) == 1
    parsed = result[0]
    assert isinstance(parsed, Seg)

    assert parsed.to_tuple(show_raw=True) == structure
