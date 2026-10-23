"""Tests for Dialect.declare_keyword_sets() and unimplemented keywords."""

from collections.abc import Iterable

import pytest

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.dialects.base import Dialect
from sqlfluff.core.parser import KeywordSegment, StringParser
from sqlfluff.core.parser.grammar.base import Nothing


def _child_of_ansi() -> Dialect:
    """A new dialect copied from ansi, with ansi's keyword sets."""
    return load_raw_dialect("ansi").copy_as("declare_keyword_sets_test")


def _declare(
    dialect: Dialect,
    reserved: Iterable[str] = (),
    unreserved: Iterable[str] = (),
    future_reserved: Iterable[str] = (),
    unimplemented: Iterable[str] = (),
) -> None:
    """Call declare_keyword_sets(), with empty sets for those not given."""
    dialect.declare_keyword_sets(
        reserved=reserved,
        unreserved=unreserved,
        future_reserved=future_reserved,
        unimplemented=unimplemented,
    )


def test_declare_keyword_sets_replaces_reserved_and_keeps_unreserved() -> None:
    """Test that reserved is replaced and inherited unreserved words stay."""
    parent = load_raw_dialect("ansi")
    child = _child_of_ansi()
    inherited_unreserved = set(parent.sets("unreserved_keywords"))

    _declare(child, reserved=["SELECT", "FROM"], unreserved=["ZZWORD"])

    assert child.sets("reserved_keywords") == {"SELECT", "FROM"}
    assert "ZZWORD" in child.sets("unreserved_keywords")
    assert inherited_unreserved - {"SELECT", "FROM"} <= child.sets(
        "unreserved_keywords"
    )


def test_declare_keyword_sets_moves_unlisted_parent_reserved_words() -> None:
    """Test that a parent reserved word the child doesn't list is unimplemented.

    It must not stay reserved, and it must not vanish: a grammar rule the
    child inherits may still refer to it.
    """
    parent = load_raw_dialect("ansi")
    child = _child_of_ansi()
    parent_reserved = set(parent.sets("reserved_keywords"))
    assert "RESPECT" in parent_reserved

    _declare(child, reserved=parent_reserved - {"RESPECT"})

    assert "RESPECT" not in child.sets("reserved_keywords")
    assert "RESPECT" in child.sets("unimplemented_keywords")


def test_declare_keyword_sets_takes_listed_words_out_of_inherited_sets() -> None:
    """Test that a listed word leaves the status it inherited.

    ansi lists ABORT as unreserved; reserving it in the child must leave it in
    one status only.
    """
    child = _child_of_ansi()
    assert "ABORT" in child.sets("unreserved_keywords")

    _declare(child, reserved=["ABORT"])

    assert "ABORT" in child.sets("reserved_keywords")
    assert "ABORT" not in child.sets("unreserved_keywords")


def test_declare_keyword_sets_declares_future_and_unimplemented_words() -> None:
    """Test that words can be declared future reserved or unimplemented."""
    child = _child_of_ansi()

    _declare(
        child, reserved=["SELECT"], future_reserved=["ZZLATER"], unimplemented=["ABORT"]
    )

    assert "ZZLATER" in child.sets("future_reserved_keywords")
    assert "ABORT" in child.sets("unimplemented_keywords")
    assert "ABORT" not in child.sets("unreserved_keywords")


@pytest.mark.parametrize(
    "sets,statuses",
    [
        ({"reserved": ["A"], "unreserved": ["A"]}, "reserved_keywords and unreserved"),
        (
            {"reserved": ["A"], "future_reserved": ["A"]},
            "reserved_keywords and future_reserved",
        ),
        (
            {"unreserved": ["C"], "unimplemented": ["C"]},
            "unreserved_keywords and unimplemented",
        ),
    ],
)
def test_declare_keyword_sets_rejects_a_word_under_two_statuses(
    sets: dict[str, list[str]], statuses: str
) -> None:
    """Test that declaring the same word twice is an error, not a guess."""
    child = _child_of_ansi()

    with pytest.raises(ValueError, match=statuses):
        _declare(child, **sets)


def test_declare_keyword_sets_requires_every_set() -> None:
    """Test that every set must be given, so an empty one is a decision."""
    child = _child_of_ansi()

    with pytest.raises(TypeError, match="unimplemented"):
        child.declare_keyword_sets(  # type: ignore[call-arg]
            reserved=["SELECT"], unreserved=[], future_reserved=[]
        )


def test_declare_keyword_sets_refuses_a_single_string() -> None:
    """Test that a keyword string can't be passed where words are expected.

    Iterating a string gives its characters, so it would declare every letter
    as a keyword.
    """
    child = _child_of_ansi()

    with pytest.raises(TypeError, match="split"):
        _declare(child, reserved="SELECT\nFROM")


def test_keyword_sets_declared_is_kept_by_expand_and_not_inherited() -> None:
    """Test that opting in is per dialect.

    Expanding keeps it, so the dialect tests can see it, but a dialect copied
    from an opted-in one starts opted out.
    """
    child = _child_of_ansi()
    _declare(child, reserved=["SELECT"])

    assert child.expand().keyword_sets_declared
    assert not child.copy_as("grandchild").keyword_sets_declared
    assert not _child_of_ansi().keyword_sets_declared


def test_unimplemented_keyword_resolves_to_nothing() -> None:
    """Test that an unimplemented keyword resolves and never matches.

    A keyword with no status at all still fails to resolve, so a typo in a
    grammar is still caught.
    """
    child = _child_of_ansi()
    _declare(child, reserved=["SELECT"], unimplemented=["ZZGONE"])
    expanded = child.expand()

    assert isinstance(expanded.ref("ZzgoneKeywordSegment"), Nothing)
    select = expanded.ref("SelectKeywordSegment")
    assert isinstance(select, StringParser)
    assert select.raw_class is KeywordSegment
    with pytest.raises(RuntimeError, match="ZZTYPO"):
        expanded.ref("ZztypoKeywordSegment")
