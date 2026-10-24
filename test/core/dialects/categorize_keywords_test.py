"""Tests for keyword categorizing, exhaustive claims and unimplemented keywords."""

import pytest

from sqlfluff.core.dialects import dialect_selector, load_raw_dialect
from sqlfluff.core.dialects.base import Dialect, ExhaustiveReservedClaim
from sqlfluff.core.parser import KeywordSegment, StringParser
from sqlfluff.core.parser.grammar.base import Nothing


def _child_of_ansi() -> Dialect:
    """A new dialect copied from ansi, with ansi's keyword sets."""
    return load_raw_dialect("ansi").copy_as("categorize_keywords_test")


def _status(dialect: Dialect, word: str) -> list[str]:
    """The keyword sets holding word, in a fixed order."""
    return [
        label
        for label in (
            "reserved_keywords",
            "unreserved_keywords",
            "unimplemented_keywords",
            "future_reserved_keywords",
        )
        if word in dialect.sets(label)
    ]


def test_categorize_keywords_keeps_unlisted_inherited_statuses() -> None:
    """Test that words not listed keep the status they inherited."""
    ansi = load_raw_dialect("ansi")
    child = _child_of_ansi()
    child.categorize_keywords(reserved=["ZZNEW"])

    assert child.sets("reserved_keywords") == ansi.sets("reserved_keywords") | {"ZZNEW"}
    assert child.sets("unreserved_keywords") == ansi.sets("unreserved_keywords")


def test_categorize_keywords_moves_a_word_out_of_its_other_statuses() -> None:
    """Test that each status takes the word out of the ones it can't share."""
    child = _child_of_ansi()
    assert _status(child, "SELECT") == ["reserved_keywords"]

    child.categorize_keywords(unreserved=["SELECT"])
    assert _status(child, "SELECT") == ["unreserved_keywords"]

    child.categorize_keywords(unimplemented=["SELECT"])
    assert _status(child, "SELECT") == ["unimplemented_keywords"]

    child.categorize_keywords(reserved=["SELECT"])
    assert _status(child, "SELECT") == ["reserved_keywords"]


def test_categorize_keywords_future_reserved_is_a_tag() -> None:
    """Test that future reserved leaves only reserved, and reserved leaves it."""
    child = _child_of_ansi()
    child.categorize_keywords(unreserved=["ZZLATER"], future_reserved=["ZZLATER"])
    assert _status(child, "ZZLATER") == [
        "unreserved_keywords",
        "future_reserved_keywords",
    ]

    child.categorize_keywords(future_reserved=["SELECT"])
    assert _status(child, "SELECT") == ["future_reserved_keywords"]

    child.categorize_keywords(reserved=["ZZLATER"])
    assert _status(child, "ZZLATER") == ["reserved_keywords"]


def test_categorize_keywords_upper_cases_words() -> None:
    """Test that words are stored upper-cased, as keyword lookups expect."""
    child = _child_of_ansi()
    child.categorize_keywords(unreserved=["zzlower"])

    assert _status(child, "ZZLOWER") == ["unreserved_keywords"]


@pytest.mark.parametrize(
    "statuses",
    [
        {"reserved": ["ZZTWICE"], "unreserved": ["ZZTWICE"]},
        {"reserved": ["ZZTWICE"], "unimplemented": ["ZZTWICE"]},
        {"unreserved": ["ZZTWICE"], "unimplemented": ["ZZTWICE"]},
        {"reserved": ["ZZTWICE"], "future_reserved": ["ZZTWICE"]},
    ],
)
def test_categorize_keywords_rejects_two_statuses_in_one_call(
    statuses: dict[str, list[str]],
) -> None:
    """Test that a word given two statuses that can't go together is refused."""
    with pytest.raises(ValueError, match="ZZTWICE"):
        _child_of_ansi().categorize_keywords(**statuses)


@pytest.mark.parametrize("argument", ["reserved", "unreserved", "unimplemented"])
def test_categorize_keywords_refuses_a_string(argument: str) -> None:
    """Test that a string, which would be read one letter at a time, is refused."""
    with pytest.raises(TypeError, match=r"list of words, not a string"):
        _child_of_ansi().categorize_keywords(**{argument: "LIBRARY"})


def test_categorize_keywords_takes_keyword_arguments_only() -> None:
    """Test that statuses must be named, so lists can't be swapped by position."""
    with pytest.raises(TypeError):
        _child_of_ansi().categorize_keywords(["ZZPOSITIONAL"])  # type: ignore[call-arg]


def test_claim_exhaustive_reserved_records_and_changes_nothing() -> None:
    """Test that the claim is stored, upper-cased, and leaves the sets alone."""
    child = _child_of_ansi()
    before = set(child.sets("reserved_keywords"))
    child.claim_exhaustive_reserved(["zzonly"], source="zz 1.0")

    assert child.exhaustive_reserved_claim == ExhaustiveReservedClaim(
        frozenset({"ZZONLY"}), "zz 1.0"
    )
    assert child.sets("reserved_keywords") == before


def test_claim_exhaustive_reserved_needs_a_source_and_a_list() -> None:
    """Test that the claim needs a source and refuses a string of words."""
    child = _child_of_ansi()
    with pytest.raises(ValueError, match="needs a source"):
        child.claim_exhaustive_reserved(["SELECT"], source=" ")
    with pytest.raises(TypeError, match="claim_exhaustive_reserved"):
        child.claim_exhaustive_reserved("SELECT", source="zz")


def test_claim_and_error_docs_survive_expand_but_not_inheritance() -> None:
    """Test that the claim and docs belong to one dialect, expanded or not."""
    child = load_raw_dialect("ansi").copy_as(
        "categorize_keywords_test", keyword_reference_error_docs="See zz."
    )
    child.claim_exhaustive_reserved(["SELECT"], source="zz")
    expanded = child.expand()

    assert expanded.exhaustive_reserved_claim == child.exhaustive_reserved_claim
    assert expanded.keyword_reference_error_docs == "See zz."
    grandchild = child.copy_as("categorize_keywords_grandchild")
    assert grandchild.exhaustive_reserved_claim is None
    assert grandchild.keyword_reference_error_docs is None


@pytest.mark.parametrize("name", ["ansi", "mysql", "mariadb", "tsql"])
def test_expand_keeps_the_dialects_identity(name: str) -> None:
    """Test that an expanded dialect is the same dialect, parent included.

    expand() copies the dialect with copy_as(), which on its own would make the
    copy look like a child of the original.
    """
    raw = load_raw_dialect(name)
    expanded = dialect_selector(name)

    assert expanded.inherits_from == raw.inherits_from
    assert expanded.formatted_name == raw.formatted_name
    assert expanded.docstring == raw.docstring


def test_unimplemented_keyword_resolves_to_nothing() -> None:
    """Test that an unimplemented keyword resolves and never matches.

    A keyword with no status at all still fails to resolve, so a typo in a
    grammar is still caught.
    """
    child = _child_of_ansi()
    child.categorize_keywords(unimplemented=["ZZGONE"])
    expanded = child.expand()

    assert isinstance(expanded.ref("ZzgoneKeywordSegment"), Nothing)
    select = expanded.ref("SelectKeywordSegment")
    assert isinstance(select, StringParser)
    assert select.raw_class is KeywordSegment
    with pytest.raises(RuntimeError, match="ZZTYPO"):
        expanded.ref("ZztypoKeywordSegment")


def test_unimplemented_wins_over_future_reserved() -> None:
    """Test that a word not a keyword yet, but future reserved, never matches.

    expand() builds keyword parsers for future reserved words, so without the
    unimplemented check first the grammar would silently stay on.
    """
    child = _child_of_ansi()
    child.categorize_keywords(unimplemented=["ZZNOTYET"], future_reserved=["ZZNOTYET"])

    assert isinstance(child.expand().ref("ZznotyetKeywordSegment"), Nothing)
