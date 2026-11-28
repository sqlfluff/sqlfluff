"""Tests for declare_keyword_sets(), expand() and unimplemented keywords."""

import random
from typing import Any

import pytest

from sqlfluff.core.dialects import dialect_selector, load_raw_dialect
from sqlfluff.core.dialects.base import KEYWORD_STATUS_SETS, Dialect
from sqlfluff.core.parser import KeywordSegment, StringParser
from sqlfluff.core.parser.grammar.base import Nothing


def _parent() -> Dialect:
    """An ansi copy that adds keywords of known status for these tests to use.

    ZZRES1 and ZZRES2 are reserved, ZZUNRES1 and ZZUNRES2 unreserved. The tests
    rely on these, not on the status of any word ansi lists, so changing ansi's
    keywords can't break them.
    """
    parent = load_raw_dialect("ansi").copy_as("declare_keyword_sets_parent")
    parent.declare_keyword_sets(
        reserved=["ZZRES1", "ZZRES2"],
        reserved_mode="add",
        unreserved=["ZZUNRES1", "ZZUNRES2"],
        unimplemented=[],
        future_reserved=[],
        future_reserved_mode="replace",
        unspecified_parent_keywords="unreserved",
    )
    return parent


def _child() -> Dialect:
    """A new dialect copied from _parent(), with its keyword sets."""
    return _parent().copy_as("declare_keyword_sets_test")


def _declare(
    dialect: Dialect,
    reserved_mode: str = "add",
    reserved: tuple[str, ...] = (),
    unreserved: tuple[str, ...] = (),
    unimplemented: tuple[str, ...] = (),
    future_reserved: tuple[str, ...] = (),
    future_reserved_mode: str = "replace",
    unspecified_parent_keywords: str = "unreserved",
) -> None:
    """Call declare_keyword_sets() with empty lists for those not given."""
    dialect.declare_keyword_sets(
        reserved=list(reserved),
        reserved_mode=reserved_mode,
        unreserved=list(unreserved),
        unimplemented=list(unimplemented),
        future_reserved=list(future_reserved),
        future_reserved_mode=future_reserved_mode,
        unspecified_parent_keywords=unspecified_parent_keywords,
    )


def _status(dialect: Dialect, word: str) -> list[str]:
    """The keyword sets holding word, in a fixed order."""
    return [label for label in KEYWORD_STATUS_SETS if word in dialect.sets(label)]


def test_add_mode_keeps_inherited_reserved_words() -> None:
    """Test that reserved_mode="add" adds to the parent's reserved list."""
    parent = _parent()
    child = parent.copy_as("declare_keyword_sets_test")
    _declare(child, "add", reserved=("ZZNEW",))

    assert child.sets("reserved_keywords") == parent.sets("reserved_keywords") | {
        "ZZNEW"
    }
    assert child.sets("unreserved_keywords") == parent.sets("unreserved_keywords")


def test_replace_mode_demotes_unlisted_inherited_reserved_words() -> None:
    """Test that reserved_mode="replace" keeps only the list, demoting the rest."""
    child = _child()
    _declare(child, "replace", reserved=("ZZRES1", "ZZNEW"))

    assert child.sets("reserved_keywords") == {"ZZRES1", "ZZNEW"}
    assert _status(child, "ZZRES2") == ["unreserved_keywords"]


def test_what_you_list_is_what_you_get() -> None:
    """Test that a listed word leaves the status it inherited, in either mode."""
    for mode in ("add", "replace"):
        child = _child()
        _declare(child, mode, reserved=("ZZUNRES1",), unreserved=("ZZRES1",))

        assert _status(child, "ZZRES1") == ["unreserved_keywords"], mode
        assert _status(child, "ZZUNRES1") == ["reserved_keywords"], mode


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
    child = _child()
    with pytest.raises(ValueError, match=rf"ZZBOTH \({first} and {second}\)"):
        lists: dict[str, Any] = {first: ("ZZBOTH",), second: ("ZZBOTH",)}
        _declare(child, **lists)


def test_future_reserved_goes_with_unreserved_or_unimplemented() -> None:
    """Test the two overlaps a call may make: future reserved with a present status."""
    child = _child()
    _declare(
        child,
        unreserved=("ZZSOON",),
        unimplemented=("ZZLATER",),
        future_reserved=("ZZSOON", "ZZLATER"),
        future_reserved_mode="replace",
        unspecified_parent_keywords="unreserved",
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

    This is postgres's "not-keyword": a word unreserved in its parent but not
    a PostgreSQL keyword, which RF04 must not flag (#4269). ZZUNRES1 is that
    word; ZZRES1 stands in for an inherited reserved word, which
    reserved_mode="add" would otherwise keep.
    """
    child = _child()
    _declare(child, mode, unimplemented=("ZZUNRES1", "ZZRES1"))

    assert _status(child, "ZZUNRES1") == ["unimplemented_keywords"]
    assert _status(child, "ZZRES1") == ["unimplemented_keywords"]


def test_listing_a_keyword_switches_inherited_grammar_back_on() -> None:
    """Test that a child listing a parent's unimplemented word implements it."""
    parent = _child()
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
    parent = _child()
    parent.sets("reserved_keywords").add("ZZBOTH")
    parent.sets("unimplemented_keywords").add("ZZBOTH")
    child = parent.copy_as("declare_keyword_sets_grandchild")
    _declare(child)

    assert _status(child, "ZZBOTH") == ["unimplemented_keywords"]


def test_future_reserved_is_never_reserved() -> None:
    """Test that a future reserved word leaves reserved, and may be unreserved."""
    child = _child()
    _declare(child, unreserved=("ZZLATER",), future_reserved=("ZZLATER", "ZZRES1"))

    assert _status(child, "ZZLATER") == [
        "unreserved_keywords",
        "future_reserved_keywords",
    ]
    # ZZRES1 leaves reserved but keeps a present status.
    assert _status(child, "ZZRES1") == [
        "unreserved_keywords",
        "future_reserved_keywords",
    ]


@pytest.mark.parametrize("mode", ["add", "replace"])
def test_no_inherited_word_is_dropped(mode: str) -> None:
    """Test that every word the parent knows still has a status afterwards."""
    parent = _parent()
    known = set().union(*(parent.sets(label) for label in KEYWORD_STATUS_SETS))
    child = parent.copy_as("declare_keyword_sets_test")
    _declare(
        child,
        mode,
        reserved=("ZZUNRES1",),
        unreserved=("ZZRES1",),
        unimplemented=("ZZRES2",),
        future_reserved=("ZZUNRES2",),
        future_reserved_mode="replace",
        unspecified_parent_keywords="unreserved",
    )
    after = set().union(*(child.sets(label) for label in KEYWORD_STATUS_SETS))

    assert known <= after


def _with_future_parent() -> Dialect:
    """A _child() whose own keywords include ZZSOON, only future reserved."""
    parent = _child()
    _declare(parent, unreserved=("ZZLATER",), future_reserved=("ZZSOON", "ZZLATER"))
    return parent


def test_future_reserved_replace_mode_drops_the_parents_future_words() -> None:
    """Test that replace keeps only this call's future list.

    Future reserved is a future status, not a present one, so dropping it
    leaves a word's present status alone: ZZLATER stays unreserved, and ZZSOON,
    which was only future reserved, ends up with nothing.
    """
    child = _with_future_parent().copy_as("declare_keyword_sets_grandchild")
    _declare(child, future_reserved=("ZZNEW",), future_reserved_mode="replace")

    assert child.sets("future_reserved_keywords") == {"ZZNEW"}
    assert _status(child, "ZZLATER") == ["unreserved_keywords"]
    assert _status(child, "ZZSOON") == []


def test_future_reserved_add_mode_keeps_the_parents_future_words() -> None:
    """Test that add keeps the parent's future list and adds to it."""
    child = _with_future_parent().copy_as("declare_keyword_sets_grandchild")
    _declare(child, future_reserved=("ZZNEW",), future_reserved_mode="add")

    assert child.sets("future_reserved_keywords") == {"ZZNEW", "ZZSOON", "ZZLATER"}


@pytest.mark.parametrize("future_mode", ["add", "replace"])
def test_a_future_word_listed_as_reserved_is_no_longer_future(future_mode: str) -> None:
    """Test that reserving an inherited future reserved word drops future reserved."""
    child = _with_future_parent().copy_as("declare_keyword_sets_grandchild")
    _declare(child, reserved=("ZZSOON",), future_reserved_mode=future_mode)

    assert _status(child, "ZZSOON") == ["reserved_keywords"]


def test_a_reserved_word_listed_as_future_is_unreserved_in_add_mode() -> None:
    """Test that listing an inherited reserved word as future keeps a status.

    The call's list takes priority, and reserved with future reserved would be
    redundant, so the word leaves reserved. With reserved_mode="add" it lands
    on unreserved; only reserved_mode="replace" can send it to unimplemented,
    through unspecified_parent_keywords="unimplemented".
    """
    child = _child()
    _declare(child, "add", future_reserved=("ZZRES1",))

    assert _status(child, "ZZRES1") == [
        "unreserved_keywords",
        "future_reserved_keywords",
    ]


def test_keywords_set_from_multiline_string_reads_one_word_per_line() -> None:
    """Test that lines, not spaces, separate entries, and blanks are skipped."""
    words = Dialect.keywords_set_from_multiline_string(
        """
        select
        WITHIN GROUP

        End-Exec
        """
    )

    assert words == {"SELECT", "WITHIN GROUP", "END-EXEC"}


def test_keywords_set_from_multiline_string_refuses_a_repeated_word() -> None:
    """Test that a word listed twice is refused instead of merged away."""
    with pytest.raises(ValueError, match="listed more than once: SELECT"):
        Dialect.keywords_set_from_multiline_string("SELECT\nJOIN\nselect")


def test_declare_keyword_sets_refuses_a_bad_mode_and_strings() -> None:
    """Test the argument checks: a known mode, lists not strings, all named."""
    child = _child()
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
            unspecified_parent_keywords="unreserved",
        )
    with pytest.raises(
        ValueError,
        match='unspecified_parent_keywords="unreserved" or "unimplemented", not .drop.',
    ):
        _declare(child, unspecified_parent_keywords="drop")
    with pytest.raises(TypeError):
        child.declare_keyword_sets(reserved=[], reserved_mode="add")  # type: ignore[call-arg]


def test_unspecified_parent_keywords_unimplemented_needs_replace_mode() -> None:
    """Test that complete lists and kept inherited reserved words are refused.

    unspecified_parent_keywords="unimplemented" says the lists are complete;
    reserved_mode="add" keeps reserved words they don't list. Both can't hold.
    """
    child = _child()
    with pytest.raises(ValueError, match='Use reserved_mode="replace"'):
        _declare(child, "add", unspecified_parent_keywords="unimplemented")


def test_unspecified_parent_keywords_unimplemented_takes_the_lists_as_complete() -> (
    None
):
    """Test that inherited keywords the call doesn't list become unimplemented.

    The parent's ZZRES and ZZUN aren't listed, so they become unimplemented, as
    does ZZSOON, listed only as future reserved, which is no present status.
    Listed words get what they're listed as, and the parent's unimplemented
    ZZOFF stays so.
    """
    parent = _child()
    _declare(
        parent,
        reserved=("ZZRES", "ZZRESKEEP"),
        unreserved=("ZZUN", "ZZUNKEEP", "ZZSOON"),
        unimplemented=("ZZOFF",),
    )
    child = parent.copy_as("declare_keyword_sets_grandchild")
    _declare(
        child,
        "replace",
        reserved=("ZZRESKEEP",),
        unreserved=("ZZUNKEEP",),
        future_reserved=("ZZSOON",),
        unspecified_parent_keywords="unimplemented",
    )

    assert _status(child, "ZZRES") == ["unimplemented_keywords"]
    assert _status(child, "ZZUN") == ["unimplemented_keywords"]
    assert _status(child, "ZZSOON") == [
        "unimplemented_keywords",
        "future_reserved_keywords",
    ]
    assert _status(child, "ZZRESKEEP") == ["reserved_keywords"]
    assert _status(child, "ZZUNKEEP") == ["unreserved_keywords"]
    assert _status(child, "ZZOFF") == ["unimplemented_keywords"]
    assert _status(child, "ZZRES1") == ["unimplemented_keywords"]


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
    child = _child()
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

    expand() builds keyword parsers for reserved and unreserved words, so
    without the unimplemented check first the grammar that needs the word
    would silently stay on. declare_keyword_sets() never leaves
    such an overlap, so this builds the sets by hand, as a dialect that doesn't
    use it might.
    """
    child = _child()
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
# _parent()'s words that start reserved (ZZRES1, ZZRES2) and unreserved
# (ZZUNRES1, ZZUNRES2).
_VOCABULARY = (
    "ZZW0",
    "ZZW1",
    "ZZW2",
    "ZZW3",
    "ZZW4",
    "ZZRES1",
    "ZZRES2",
    "ZZUNRES1",
    "ZZUNRES2",
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
    reserved_mode = rng.choice(["add", "replace"])
    # "unimplemented" needs complete lists, so it only goes with "replace".
    unspecified = ["unreserved"]
    if reserved_mode == "replace":
        unspecified.append("unimplemented")
    return {
        **lists,
        "reserved_mode": reserved_mode,
        "future_reserved_mode": rng.choice(["add", "replace"]),
        "unspecified_parent_keywords": rng.choice(unspecified),
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
        parent = _child()
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


def test_a_word_that_is_only_future_reserved_does_not_resolve() -> None:
    """Test that future reserved alone gives a word no keyword parser.

    Future reserved is a future status, not a present one: grammar that uses
    such a word fails to resolve, so the audit reports it, and lint rules
    still see the word in the future reserved set.
    """
    child = _child()
    _declare(child, unreserved=("ZZSOON",), future_reserved=("ZZSOON", "ZZLATER"))
    expanded = child.expand()

    assert isinstance(expanded.ref("ZzsoonKeywordSegment"), StringParser)
    with pytest.raises(RuntimeError, match="ZZLATER"):
        expanded.ref("ZzlaterKeywordSegment")
    assert "ZZLATER" in expanded.sets("future_reserved_keywords")
