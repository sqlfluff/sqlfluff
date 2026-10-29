"""Tests for declare_keyword_sets(), expand() and unimplemented keywords."""

import random
from typing import Any

import pytest

from sqlfluff.core.dialects import dialect_selector, load_raw_dialect
from sqlfluff.core.dialects.base import KEYWORD_STATUS_SETS, Dialect
from sqlfluff.core.parser import KeywordSegment, StringParser
from sqlfluff.core.parser.grammar.base import Nothing


def _child_of_ansi() -> Dialect:
    """A new dialect copied from ansi, with ansi's keyword sets."""
    return load_raw_dialect("ansi").copy_as("declare_keyword_sets_test")


def _declare(
    dialect: Dialect,
    reserved_mode: str = "add",
    reserved: tuple[str, ...] = (),
    unreserved: tuple[str, ...] = (),
    unimplemented: tuple[str, ...] = (),
    future_reserved: tuple[str, ...] = (),
    future_reserved_mode: str = "replace",
) -> None:
    """Call declare_keyword_sets() with empty lists for those not given."""
    dialect.declare_keyword_sets(
        reserved=list(reserved),
        reserved_mode=reserved_mode,
        unreserved=list(unreserved),
        unimplemented=list(unimplemented),
        future_reserved=list(future_reserved),
        future_reserved_mode=future_reserved_mode,
    )


def _status(dialect: Dialect, word: str) -> list[str]:
    """The keyword sets holding word, in a fixed order."""
    return [label for label in KEYWORD_STATUS_SETS if word in dialect.sets(label)]


def test_add_mode_keeps_inherited_reserved_words() -> None:
    """Test that add mode adds to the parent's reserved list."""
    ansi = load_raw_dialect("ansi")
    child = _child_of_ansi()
    _declare(child, "add", reserved=("ZZNEW",))

    assert child.sets("reserved_keywords") == ansi.sets("reserved_keywords") | {"ZZNEW"}
    assert child.sets("unreserved_keywords") == ansi.sets("unreserved_keywords")


def test_replace_mode_demotes_unlisted_inherited_reserved_words() -> None:
    """Test that replace mode keeps only the list, demoting the rest."""
    child = _child_of_ansi()
    _declare(child, "replace", reserved=("SELECT", "ZZNEW"))

    assert child.sets("reserved_keywords") == {"SELECT", "ZZNEW"}
    assert _status(child, "JOIN") == ["unreserved_keywords"]


def test_what_you_list_is_what_you_get() -> None:
    """Test that a listed word leaves the status it inherited, in either mode."""
    for mode in ("add", "replace"):
        child = _child_of_ansi()
        _declare(child, mode, reserved=("ZONE",), unreserved=("ROWS",))

        assert _status(child, "ROWS") == ["unreserved_keywords"], mode
        assert _status(child, "ZONE") == ["reserved_keywords"], mode


@pytest.mark.parametrize(
    "first, second",
    [
        ("reserved", "unreserved"),
        ("reserved", "unimplemented"),
        ("unreserved", "unimplemented"),
        ("reserved", "future_reserved"),
    ],
)
def test_a_call_cant_list_a_word_twice(first: str, second: str) -> None:
    """Test that the call's own lists must not overlap where they exclude."""
    child = _child_of_ansi()
    with pytest.raises(ValueError, match=rf"ZZBOTH \({first} and {second}\)"):
        lists: dict[str, Any] = {first: ("ZZBOTH",), second: ("ZZBOTH",)}
        _declare(child, **lists)


def test_future_reserved_goes_with_unreserved_or_unimplemented() -> None:
    """Test the two overlaps a call may make: they're tags, not statuses."""
    child = _child_of_ansi()
    _declare(
        child,
        unreserved=("ZZSOON",),
        unimplemented=("ZZLATER",),
        future_reserved=("ZZSOON", "ZZLATER"),
        future_reserved_mode="replace",
    )

    assert _status(child, "ZZSOON") == [
        "unreserved_keywords",
        "future_reserved_keywords",
    ]
    assert _status(child, "ZZLATER") == [
        "unimplemented_keywords",
        "future_reserved_keywords",
    ]


@pytest.mark.parametrize("mode", ["add", "replace"])
def test_a_word_listed_only_as_unimplemented_is_just_a_name(mode: str) -> None:
    """Test that unimplemented alone takes away an inherited keyword status.

    This is postgres's "not-keyword": EXECUTION is unreserved in ansi but not
    a PostgreSQL keyword, so RF04 must not flag it (#4269). SELECT stands in
    for an inherited reserved word, which add mode would otherwise keep.
    """
    child = _child_of_ansi()
    _declare(child, mode, unimplemented=("EXECUTION", "SELECT"))

    assert _status(child, "EXECUTION") == ["unimplemented_keywords"]
    assert _status(child, "SELECT") == ["unimplemented_keywords"]


def test_listing_a_keyword_switches_inherited_grammar_back_on() -> None:
    """Test that a child listing a parent's unimplemented word un-tags it."""
    parent = _child_of_ansi()
    _declare(parent, unimplemented=("ZZOFF", "ZZRESOFF"))
    child = parent.copy_as("declare_keyword_sets_grandchild")
    _declare(child, reserved=("ZZRESOFF",), unreserved=("ZZOFF",))

    assert _status(child, "ZZOFF") == ["unreserved_keywords"]
    assert _status(child, "ZZRESOFF") == ["reserved_keywords"]


def test_an_inherited_overlap_resolves_to_unimplemented() -> None:
    """Test that a parent's hand-built overlap gives way to unimplemented.

    A parent that builds its sets without declare_keyword_sets() can leave a
    word both reserved and unimplemented. The child's call can't refuse what
    it didn't list, so it resolves it the way expand() would.
    """
    parent = _child_of_ansi()
    parent.sets("reserved_keywords").add("ZZBOTH")
    parent.sets("unimplemented_keywords").add("ZZBOTH")
    child = parent.copy_as("declare_keyword_sets_grandchild")
    _declare(child)

    assert _status(child, "ZZBOTH") == ["unimplemented_keywords"]


def test_future_reserved_is_never_reserved() -> None:
    """Test that a future reserved word leaves reserved, and may be unreserved."""
    child = _child_of_ansi()
    _declare(child, unreserved=("ZZLATER",), future_reserved=("ZZLATER", "SELECT"))

    assert _status(child, "ZZLATER") == [
        "unreserved_keywords",
        "future_reserved_keywords",
    ]
    # SELECT leaves reserved but keeps a present status.
    assert _status(child, "SELECT") == [
        "unreserved_keywords",
        "future_reserved_keywords",
    ]


@pytest.mark.parametrize("mode", ["add", "replace"])
def test_no_inherited_word_is_dropped(mode: str) -> None:
    """Test that every word the parent knows still has a status afterwards."""
    ansi = load_raw_dialect("ansi")
    known = set().union(*(ansi.sets(label) for label in KEYWORD_STATUS_SETS))
    child = _child_of_ansi()
    _declare(
        child,
        mode,
        reserved=("SELECT",),
        unreserved=("ROWS",),
        unimplemented=("JOIN",),
        future_reserved=("ORDER",),
        future_reserved_mode="replace",
    )
    after = set().union(*(child.sets(label) for label in KEYWORD_STATUS_SETS))

    assert known <= after


def _with_future_parent() -> Dialect:
    """An ansi copy whose own keywords include ZZSOON, only future reserved."""
    parent = _child_of_ansi()
    _declare(parent, unreserved=("ZZLATER",), future_reserved=("ZZSOON", "ZZLATER"))
    return parent


def test_future_reserved_replace_mode_drops_the_parents_tags() -> None:
    """Test that replace keeps only this call's future list.

    Future reserved is a tag, not a present status, so dropping it leaves a
    word's present status alone: ZZLATER stays unreserved, and ZZSOON, which
    only had the tag, ends up with nothing.
    """
    child = _with_future_parent().copy_as("declare_keyword_sets_grandchild")
    _declare(child, future_reserved=("ZZNEW",), future_reserved_mode="replace")

    assert child.sets("future_reserved_keywords") == {"ZZNEW"}
    assert _status(child, "ZZLATER") == ["unreserved_keywords"]
    assert _status(child, "ZZSOON") == []


def test_future_reserved_add_mode_keeps_the_parents_tags() -> None:
    """Test that add keeps the parent's future list and adds to it."""
    child = _with_future_parent().copy_as("declare_keyword_sets_grandchild")
    _declare(child, future_reserved=("ZZNEW",), future_reserved_mode="add")

    assert child.sets("future_reserved_keywords") == {"ZZNEW", "ZZSOON", "ZZLATER"}


@pytest.mark.parametrize("future_mode", ["add", "replace"])
def test_a_future_word_listed_as_reserved_loses_the_tag(future_mode: str) -> None:
    """Test that reserving an inherited future reserved word drops its tag."""
    child = _with_future_parent().copy_as("declare_keyword_sets_grandchild")
    _declare(child, reserved=("ZZSOON",), future_reserved_mode=future_mode)

    assert _status(child, "ZZSOON") == ["reserved_keywords"]


def test_a_reserved_word_listed_as_future_is_unreserved_in_add_mode() -> None:
    """Test that listing an inherited reserved word as future keeps a status.

    Future reserved isn't reserved yet, so the word leaves reserved, and has to
    land somewhere present: unreserved.
    """
    child = _child_of_ansi()
    _declare(child, "add", future_reserved=("SELECT",))

    assert _status(child, "SELECT") == [
        "unreserved_keywords",
        "future_reserved_keywords",
    ]


def test_declare_keyword_sets_refuses_a_bad_mode_and_strings() -> None:
    """Test the argument checks: a known mode, lists not strings, all named."""
    child = _child_of_ansi()
    with pytest.raises(ValueError, match='reserved_mode="add" or "replace"'):
        _declare(child, "merge")
    with pytest.raises(
        ValueError, match='future_reserved_mode="add" or "replace", not .merge.'
    ):
        _declare(child, future_reserved_mode="merge")
    with pytest.raises(TypeError, match="list of words, not a string"):
        child.declare_keyword_sets(
            reserved="SELECT",
            reserved_mode="add",
            unreserved=[],
            unimplemented=[],
            future_reserved=[],
            future_reserved_mode="replace",
        )
    with pytest.raises(TypeError):
        child.declare_keyword_sets(reserved=[], reserved_mode="add")  # type: ignore[call-arg]


def test_error_docs_survive_expand_but_not_inheritance() -> None:
    """Test that keyword_reference_error_docs belongs to one dialect."""
    child = load_raw_dialect("ansi").copy_as(
        "declare_keyword_sets_test", keyword_reference_error_docs="See zz."
    )

    assert child.expand().keyword_reference_error_docs == "See zz."
    assert child.copy_as("zz_grandchild").keyword_reference_error_docs is None


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
    _declare(child, unimplemented=("ZZGONE",))
    expanded = child.expand()

    assert isinstance(expanded.ref("ZzgoneKeywordSegment"), Nothing)
    select = expanded.ref("SelectKeywordSegment")
    assert isinstance(select, StringParser)
    assert select.raw_class is KeywordSegment
    with pytest.raises(RuntimeError, match="ZZTYPO"):
        expanded.ref("ZztypoKeywordSegment")


def test_unimplemented_wins_over_every_other_status() -> None:
    """Test that an unimplemented word never matches, whatever else it is.

    expand() builds keyword parsers for reserved, unreserved and future
    reserved words, so without the unimplemented check first the grammar that
    needs the word would silently stay on. declare_keyword_sets() never leaves
    such an overlap, so this builds the sets by hand, as a dialect that doesn't
    use it might.
    """
    child = _child_of_ansi()
    for label, word in (
        ("reserved_keywords", "ZZRES"),
        ("unreserved_keywords", "ZZUNRES"),
        ("future_reserved_keywords", "ZZNOTYET"),
    ):
        child.sets(label).add(word)
        child.sets("unimplemented_keywords").add(word)
    expanded = child.expand()

    for word in ("Zzres", "Zzunres", "Zznotyet"):
        assert isinstance(expanded.ref(f"{word}KeywordSegment"), Nothing), word


# A small vocabulary, so that random calls collide often: made-up words, and
# ansi words that start reserved (SELECT, JOIN) and unreserved (ZONE, ABORT).
_VOCABULARY = (
    "ZZW0",
    "ZZW1",
    "ZZW2",
    "ZZW3",
    "ZZW4",
    "SELECT",
    "JOIN",
    "ZONE",
    "ABORT",
)
_PRESENT_SETS = ("reserved_keywords", "unreserved_keywords", "unimplemented_keywords")


def _random_call(rng: random.Random) -> dict[str, Any]:
    """Arguments for one valid declare_keyword_sets() call, chosen at random.

    Each word gets at most one present status, and future reserved never goes
    with reserved, so the call is one the function must accept.
    """
    lists: dict[str, list[str]] = {
        "reserved": [],
        "unreserved": [],
        "unimplemented": [],
        "future_reserved": [],
    }
    for word in _VOCABULARY:
        present = rng.choice(["reserved", "unreserved", "unimplemented", None])
        if present:
            lists[present].append(word)
        if present != "reserved" and rng.random() < 0.3:
            lists["future_reserved"].append(word)
    return {
        **lists,
        "reserved_mode": rng.choice(["add", "replace"]),
        "future_reserved_mode": rng.choice(["add", "replace"]),
    }


def _present_words(dialect: Dialect) -> set[str]:
    """Every word with a present status in the dialect."""
    return set().union(*(dialect.sets(label) for label in _PRESENT_SETS))


def test_a_parent_change_never_takes_a_word_from_a_child() -> None:
    """Test, over random parents and children, the promise the function makes.

    However a parent sets its keywords, a child calling declare_keyword_sets()
    keeps every word the parent has with some present status, and its sets
    stay valid: one present status per word, future reserved never reserved.
    Seeded, so a failure repeats; the message has the trial's calls.
    """
    rng = random.Random(8906)
    for trial in range(2000):
        parent = _child_of_ansi()
        parent_call = _random_call(rng)
        parent.declare_keyword_sets(**parent_call)
        child = parent.copy_as("declare_keyword_sets_grandchild")
        child_call = _random_call(rng)
        child.declare_keyword_sets(**child_call)
        context = f"trial {trial}: parent {parent_call}, child {child_call}"

        assert _present_words(parent) <= _present_words(child), context
        for first, second in (
            ("reserved_keywords", "unreserved_keywords"),
            ("reserved_keywords", "unimplemented_keywords"),
            ("unreserved_keywords", "unimplemented_keywords"),
            ("reserved_keywords", "future_reserved_keywords"),
        ):
            assert not child.sets(first) & child.sets(second), context
