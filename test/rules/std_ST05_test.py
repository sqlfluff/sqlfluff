"""Tests specific to ST05."""

from sqlfluff.core.dialects import dialect_selector
from sqlfluff.rules.structure.ST05 import _CTEBuilder


def test__rules__std_ST05_allocates_generated_alias_iteratively() -> None:
    """A long run of reserved aliases does not exhaust Python's call stack."""
    reserved_names = {f"prep_{index}" for index in range(1, 2001)}

    assert _CTEBuilder().create_cte_alias(
        None,
        dialect=dialect_selector("ansi"),
        reserved_names=reserved_names,
    ) == ("prep_2001", True)
