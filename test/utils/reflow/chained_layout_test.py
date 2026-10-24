"""Check shared layout helpers outside a rule configuration context."""

import pytest

from sqlfluff.core.errors import SQLFluffUserError
from sqlfluff.core.parser import (
    BaseSegment,
    CommentSegment,
    NewlineSegment,
    WhitespaceSegment,
)
from sqlfluff.utils.reflow.chained_layout import preceding_gap, validate_style


@pytest.mark.parametrize("value", [None, True, "one-liner"])
def test_layout_helper_rejects_unknown_styles(value: str | bool | None) -> None:
    """Direct helper callers must get the same allowed-value contract as rules."""
    with pytest.raises(SQLFluffUserError, match="writing_style must be one of"):
        validate_style(value)


def test_gap_without_preceding_code_preserves_all_segments() -> None:
    """A leading non-code prefix must retain its comments, whitespace and order."""
    prefix: list[BaseSegment] = [
        WhitespaceSegment("  "),
        CommentSegment("-- keep", type="inline_comment"),
        NewlineSegment(),
    ]
    assert preceding_gap(prefix) == prefix
