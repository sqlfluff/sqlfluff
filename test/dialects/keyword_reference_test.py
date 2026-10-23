"""Keyword and reference checks for dialects that call declare_keyword_sets().

These tests hold each such dialect to two rules:

- Every word has at most one keyword status.
- Every keyword and reference its grammar can reach resolves: keywords,
  segments, bracket pairs, and those inside a Ref's exclude= and terminators=.
  A grammar keyword with no status crashes the parser on any statement that
  reaches the rule using it, even when the statement doesn't contain the word,
  so this is checked here rather than left for a user to find.

Every dialect must opt in, unless it is listed in UNAUDITED_DIALECTS below.

The failure messages are written for someone who has never touched a dialect:
each says which file to change and how. The tests at the end check the checker
itself, so that a gap in it fails rather than quietly checking less.

Run this file directly, ``python test/dialects/keyword_reference_test.py``, for
a report. It never fails anything. It shows what these checks find in each
dialect: for an audited one, the failures pytest would show; for an unaudited
one, what opting in would bring. It also lists, for every dialect, the keywords
no grammar uses: leads to syntax sqlfluff doesn't parse yet, or to words that
can come out of a keyword list. Name dialects as arguments to report on just
those and the dialects that inherit from them, as the parser's "not found in
the ... dialect" errors suggest.
"""

import inspect
import sys
from collections.abc import Iterator
from difflib import get_close_matches
from itertools import combinations

import pytest

from sqlfluff.core.dialects import (
    dialect_readout,
    dialect_selector,
    load_raw_dialect,
)
from sqlfluff.core.dialects.base import (
    KEYWORD_STATUS_CHOICE,
    KEYWORD_STATUS_SETS,
    Dialect,
)
from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.parser.grammar.base import Ref
from sqlfluff.core.parser.grammar.sequence import Sequence

# Dialects that don't call declare_keyword_sets() yet, so these checks don't
# run for them. Every other dialect, including any new one, must opt in. When
# one of these opts in, remove it from here; the tests say so.
UNAUDITED_DIALECTS = {
    "athena",
    "bigquery",
    "clickhouse",
    "databricks",
    "db2",
    "duckdb",
    "exasol",
    "flink",
    "greenplum",
    "hive",
    "impala",
    "materialize",
    "oracle",
    "postgres",
    "redshift",
    "snowflake",
    "soql",
    "sparksql",
    "sqlite",
    "teradata",
    "trino",
    "tsql",
    "vertica",
}

ALL_DIALECTS = sorted(info.label for info in dialect_readout())

AUDITED_DIALECTS = sorted(
    name for name in ALL_DIALECTS if dialect_selector(name).keyword_sets_declared
)

DIALECTS_DIR = "src/sqlfluff/dialects"

# A segment that uses an unresolved reference: (class name, dialect module).
Owner = tuple[str, str]


def _is_grammar_node(item: object) -> bool:
    """Whether item is a grammar element or a segment class to walk into."""
    if inspect.isclass(item):
        return issubclass(item, BaseSegment)
    if isinstance(item, (str, bytes, int, float, bool)) or item is None:
        return False
    return callable(getattr(item, "match", None)) and callable(
        getattr(item, "simple", None)
    )


def _grammar_children(node: object) -> Iterator[object]:
    """The grammar elements and segment classes directly inside node."""
    if inspect.isclass(node):
        match_grammar = getattr(node, "match_grammar", None)
        if match_grammar is not None:
            yield match_grammar
        return
    for value in vars(node).values():
        if isinstance(value, (list, tuple, set, frozenset)):
            items = value
        else:
            items = [value]
        for item in items:
            if _is_grammar_node(item):
                yield item


def _owner(segment: type) -> Owner:
    """A segment's class name and the dialect module that defines it.

    A failure in one dialect often comes from grammar it inherits, so the
    module says where the fix belongs.
    """
    return segment.__name__, segment.__module__.rsplit(".", 1)[-1]


def _defining_module(dialect: Dialect, element_name: str) -> str:
    """The dialect module where a named library element was first defined.

    Dialects inherit their parent's library as is, so the defining dialect is
    the furthest ancestor still holding the very same object.
    """
    try:
        current = load_raw_dialect(dialect.name)
    except KeyError:
        return f"dialect_{dialect.name}"
    element = current._library.get(element_name)
    while current.inherits_from:
        parent = load_raw_dialect(current.inherits_from)
        if parent._library.get(element_name) is not element:
            break
        current = parent
    return f"dialect_{current.name}"


def _reference_uses(dialect: Dialect) -> dict[str, set[Owner]]:
    """Every name the dialect's grammar refers to, and where it is used.

    Walks everything reachable from the dialect's root. Where a name is used
    is the segment whose grammar uses it, or the named grammar (a
    dialect.add() entry) that does.
    """
    uses: dict[str, set[Owner]] = {}
    seen: set[int] = set()
    root = dialect.get_root_segment()
    assert isinstance(root, type)
    stack: list[tuple[Owner, object]] = [(_owner(root), root)]
    while stack:
        owner, node = stack.pop()
        if id(node) in seen:
            continue
        seen.add(id(node))
        if not inspect.isclass(node) and isinstance(node, Ref):
            uses.setdefault(node._ref, set()).add(owner)
            try:
                target = dialect.ref(node._ref)
            except RuntimeError:
                pass
            else:
                if inspect.isclass(target):
                    stack.append((owner, target))
                else:
                    named = (node._ref, _defining_module(dialect, node._ref))
                    stack.append((named, target))
            # A Ref's own exclude= and terminators= are grammar too.
            for child in _grammar_children(node):
                stack.append((owner, child))
            continue
        if inspect.isclass(node):
            child_owner = _owner(node)
        else:
            child_owner = owner
        for child in _grammar_children(node):
            stack.append((child_owner, child))
    return uses


def _unresolved_references(dialect: Dialect) -> dict[str, set[Owner]]:
    """References reachable from the dialect's root that don't resolve.

    Also checks every bracket pair the dialect defines, since the parser
    resolves all of them whenever it looks for brackets.
    """
    unresolved: dict[str, set[Owner]] = {}
    for name, owners in _reference_uses(dialect).items():
        try:
            dialect.ref(name)
        except RuntimeError:
            unresolved[name] = owners
    for bracket_set in ("bracket_pairs", "angle_bracket_pairs"):
        for bracket_type, start, end, _ in dialect.bracket_sets(bracket_set):
            for reference in (start, end):
                try:
                    dialect.ref(reference)
                except RuntimeError:
                    where = (
                        f"the {bracket_set} pair {bracket_type!r}",
                        f"dialect_{dialect.name}",
                    )
                    unresolved.setdefault(reference, set()).add(where)
    return unresolved


def _unimplemented_in_own_grammar(dialect: Dialect) -> dict[str, set[Owner]]:
    """Unimplemented keywords that the dialect's own grammar uses.

    Unimplemented is for grammar a dialect inherits but doesn't have. If the
    dialect's own grammar uses the word, the dialect does have it, and the
    entry switches that grammar off.
    """
    own_module = f"dialect_{dialect.name}"
    uses = _reference_uses(dialect)
    found: dict[str, set[Owner]] = {}
    for word in dialect.sets("unimplemented_keywords"):
        owners = uses.get(word.capitalize() + "KeywordSegment", set())
        own = {owner for owner in owners if owner[1] == own_module}
        if own:
            found[word] = own
    return found


def _keyword_file(module: str) -> str:
    """The file holding a dialect module's keyword lists."""
    return f"{DIALECTS_DIR}/{module}_keywords.py"


def _dialect_file(module: str) -> str:
    """The file holding a dialect module's grammar."""
    return f"{DIALECTS_DIR}/{module}.py"


def _did_you_mean(name: str, candidates: set[str]) -> str:
    """A ' Did you mean X?' hint, or nothing if no candidate is close."""
    matches = get_close_matches(name, candidates, n=1, cutoff=0.8)
    if not matches:
        return ""
    return f" Did you mean {matches[0]}?"


def _segments_and_files(owners: set[Owner]) -> tuple[str, list[str]]:
    """The owning segment names, and the dialect modules defining them."""
    names = ", ".join(sorted(name for name, _ in owners))
    modules = sorted({module for _, module in owners})
    return names, modules


def _dialect_knows(dialect_name: str, word: str) -> bool:
    """Whether a dialect gives the word any status other than unimplemented."""
    try:
        dialect = dialect_selector(dialect_name)
    except KeyError:
        return False
    return any(
        word in dialect.sets(label)
        for label in (
            "reserved_keywords",
            "unreserved_keywords",
            "future_reserved_keywords",
        )
    )


def _missing_keywords_message(dialect: Dialect, keywords: dict[str, set[Owner]]) -> str:
    """Say, for each keyword the dialect doesn't recognize, where to list it.

    A keyword used by grammar the dialect inherits belongs in the keywords of
    the dialect that defines that grammar; the children then follow.
    """
    name = dialect.name
    own_module = f"dialect_{name}"
    # Unimplemented words aren't keywords of this dialect, so they are never
    # suggested as what was meant.
    known: set[str] = set()
    for label in (
        "reserved_keywords",
        "unreserved_keywords",
        "future_reserved_keywords",
    ):
        known.update(dialect.sets(label))
    lines = [
        f"The {name} dialect's grammar uses keywords that {name} doesn't "
        "recognize, so any statement reaching that grammar would crash."
    ]
    for word, owners in sorted(keywords.items()):
        segments, modules = _segments_and_files(owners)
        match = get_close_matches(word, known, n=1, cutoff=0.8)
        if match:
            action = (
                f" Did you mean {match[0]}, which {name} already has? If so, fix "
                "the grammar. If not, add"
            )
        else:
            action = " Add"
        if own_module in modules:
            lines.append(
                f"- {word} (in {segments}, {name}'s own grammar):{action} it "
                f"to {_keyword_file(own_module)}, in the reserved or the "
                f"unreserved list, whichever {name}'s own keyword documentation "
                "says."
            )
            continue
        parents = " and ".join(module.removeprefix("dialect_") for module in modules)
        knowers = sorted(
            module.removeprefix("dialect_")
            for module in modules
            if _dialect_knows(module.removeprefix("dialect_"), word)
        )
        if knowers:
            lines.append(
                f"- {word} (in {segments}, which {name} inherits from {parents}):"
                f" {' and '.join(knowers)} already lists it, so {name}, or a "
                "dialect between them, dropped it when it replaced its keyword "
                f"lists. If {name}'s server has it, add it to "
                f"{_keyword_file(own_module)}, in the reserved or the unreserved "
                "list; if it doesn't, add it to the unimplemented keyword list "
                "there."
            )
            continue
        files = " and ".join(_keyword_file(module) for module in modules)
        lines.append(
            f"- {word} (in {segments}, which {name} inherits from {parents}):"
            f"{action} it to {files}, in the reserved or the unreserved list, "
            f"whichever that database's own keyword documentation says; {name} "
            f"then follows automatically. Only if you know {name}'s server "
            f"doesn't recognize {word}: instead, add it to the unimplemented "
            f"keyword list in {_keyword_file(own_module)}."
        )
    return "\n".join(lines)


def _missing_segments_message(dialect: Dialect, segments: dict[str, set[Owner]]) -> str:
    """Say, for each reference to a segment that doesn't exist, where it is."""
    name = dialect.name
    existing = {
        element
        for element in dialect._library
        if not element.endswith("KeywordSegment")
    }
    lines = [
        f"The {name} dialect's grammar refers to segments or grammars that don't "
        f"exist in {name}, so any statement reaching that grammar would crash. "
        "These are usually typos in a Ref()."
    ]
    for missing, owners in sorted(segments.items()):
        users, modules = _segments_and_files(owners)
        files = " and ".join(_dialect_file(module) for module in modules)
        lines.append(
            f'- Ref("{missing}") (in {users}, in {files}):'
            f"{_did_you_mean(missing, existing)} Fix the name in that Ref(), or "
            f"define {missing}."
        )
    return "\n".join(lines)


def _overlaps(dialect: Dialect) -> dict[str, list[str]]:
    """Each word with more than one keyword status, and those statuses."""
    overlaps: dict[str, list[str]] = {}
    for first, second in combinations(KEYWORD_STATUS_SETS, 2):
        for word in dialect.sets(first) & dialect.sets(second):
            overlaps.setdefault(word, [])
            for label in (first, second):
                if label not in overlaps[word]:
                    overlaps[word].append(label)
    return overlaps


def _overlaps_message(dialect: Dialect, overlaps: dict[str, list[str]]) -> str:
    """Say, for each word with more than one status, how to choose one."""
    name = dialect.name
    lines = [
        f"In the {name} dialect, these words have more than one keyword status. "
        "A word can have only one: remove it from every list but the one the "
        f"database gives it, in {_keyword_file(f'dialect_{name}')}. "
        f"{KEYWORD_STATUS_CHOICE}"
    ]
    for word, labels in sorted(overlaps.items()):
        lines.append(f"- {word}: {' and '.join(labels)}")
    lines.append(
        "If the keyword file lists each of these words only once, then "
        "declare_keyword_sets() accepted the lists (it rejects a word with two "
        "statuses), so something changed dialect.sets(...) afterwards. Look in "
        f"{_dialect_file(f'dialect_{name}')} for a sets(...).add() or "
        ".update() after the declare_keyword_sets() call."
    )
    return "\n".join(lines)


def _opt_in_instructions(name: str) -> str:
    """How a dialect opts in to these keyword and reference checks."""
    return (
        f"The {name} dialect doesn't call declare_keyword_sets(), so its keywords "
        "and grammar references aren't checked, and a keyword its grammar uses "
        "but doesn't list would crash the parser with no test failing. New "
        "dialects should opt in:\n"
        "1. Get the database's own keyword list: its documentation, "
        "information_schema.KEYWORDS, or its parser's source. Note which words "
        "are reserved.\n"
        f"2. In {_keyword_file(f'dialect_{name}')}, write the reserved, "
        "unreserved, future reserved and unimplemented keyword lists (see "
        "dialect_mysql_keywords.py).\n"
        f"3. In {_dialect_file(f'dialect_{name}')}, pass them to "
        f"{name}_dialect.declare_keyword_sets() (see dialect_mysql.py).\n"
        "4. Run this test again: its messages say what still needs fixing, and "
        "how.\n"
        "If you can't get the database's keyword list yet, add "
        f'"{name}" to UNAUDITED_DIALECTS in this file, with a comment saying why.'
    )


def test_new_dialects_are_audited() -> None:
    """Test that every dialect not listed as unaudited opts in."""
    unlisted = sorted(
        name
        for name in ALL_DIALECTS
        if name not in AUDITED_DIALECTS and name not in UNAUDITED_DIALECTS
    )

    assert not unlisted, "\n\n".join(_opt_in_instructions(name) for name in unlisted)


def test_unaudited_dialects_have_not_opted_in() -> None:
    """Test that no dialect on the unaudited list has since opted in."""
    now_audited = sorted(UNAUDITED_DIALECTS & set(AUDITED_DIALECTS))

    assert not now_audited, (
        f"These dialects now call declare_keyword_sets(), so they are checked: "
        f"{now_audited}. Remove them from UNAUDITED_DIALECTS in this file."
    )


def test_unaudited_dialects_all_exist() -> None:
    """Test that the unaudited list names only real dialects."""
    not_dialects = sorted(UNAUDITED_DIALECTS - set(ALL_DIALECTS))

    assert not not_dialects, (
        f"UNAUDITED_DIALECTS names dialects that don't exist: {not_dialects}. "
        "Remove them, or fix the spelling."
    )


def _unimplemented_in_own_grammar_message(
    dialect: Dialect, found: dict[str, set[Owner]]
) -> str:
    """Say, for each such word, why the entry is wrong and what to do."""
    name = dialect.name
    lines = [
        f"These words are in {name}'s unimplemented keyword list, but {name}'s "
        "own grammar uses them, so the entry switches that grammar off. "
        "Unimplemented is only for grammar inherited from a parent dialect."
    ]
    for word, owners in sorted(found.items()):
        segments, _ = _segments_and_files(owners)
        lines.append(
            f"- {word} (in {segments}): if {name} has this keyword, move it from "
            f"the unimplemented list in {_keyword_file(f'dialect_{name}')} to the "
            "reserved or the unreserved list. If it doesn't, the grammar in "
            f"{_dialect_file(f'dialect_{name}')} that uses it is wrong for {name}."
        )
    return "\n".join(lines)


@pytest.mark.parametrize("dialect_name", AUDITED_DIALECTS)
def test_unimplemented_keywords_are_not_in_own_grammar(dialect_name: str) -> None:
    """Test that no unimplemented keyword is used by the dialect's own grammar."""
    dialect = dialect_selector(dialect_name)
    found = _unimplemented_in_own_grammar(dialect)

    assert not found, _unimplemented_in_own_grammar_message(dialect, found)


@pytest.mark.parametrize("dialect_name", AUDITED_DIALECTS)
def test_keyword_statuses_are_disjoint(dialect_name: str) -> None:
    """Test that no word has more than one keyword status."""
    dialect = dialect_selector(dialect_name)
    overlaps = _overlaps(dialect)

    assert not overlaps, _overlaps_message(dialect, overlaps)


@pytest.mark.parametrize("dialect_name", AUDITED_DIALECTS)
def test_grammar_references_resolve(dialect_name: str) -> None:
    """Test that every reference the dialect's grammar can reach resolves."""
    dialect = dialect_selector(dialect_name)
    unresolved = _unresolved_references(dialect)
    keywords = {
        name[: -len("KeywordSegment")].upper(): owners
        for name, owners in unresolved.items()
        if name.endswith("KeywordSegment")
    }
    segments = {
        name: owners
        for name, owners in unresolved.items()
        if not name.endswith("KeywordSegment")
    }

    assert not keywords, _missing_keywords_message(dialect, keywords)
    assert not segments, _missing_segments_message(dialect, segments)


# The tests below check the checker: each builds a dialect with one kind of
# fault and asserts it is found and explained. Without them, a gap in the walk
# would pass silently and simply check less.


class _FaultySegment(BaseSegment):
    """A segment whose grammar has one of each fault the checker must find."""

    type = "select_clause_modifier"
    match_grammar = Sequence(
        Ref.keyword("ZZPLAIN"),
        Ref("NakedIdentifierSegment", exclude=Ref.keyword("ZZEXCLUDED")),
        Sequence("SELECT", terminators=[Ref.keyword("ZZTERMINATOR")]),
        Ref("ZzMissingSegment"),
        Ref.keyword("OPTIMIZER_COST"),
    )


def _faulty_dialect(name: str) -> Dialect:
    """An expanded ansi copy whose grammar reaches _FaultySegment."""
    dialect = load_raw_dialect("ansi").copy_as(name)
    dialect.replace(SelectClauseModifierSegment=_FaultySegment)
    dialect.declare_keyword_sets(
        reserved=load_raw_dialect("ansi").sets("reserved_keywords"),
        unreserved=[],
        future_reserved=[],
        unimplemented=["OPTIMIZER_COSTS"],
    )
    dialect.bracket_sets("bracket_pairs").add(
        ("zz", "ZzStartSegment", "ZzEndSegment", True)
    )
    return dialect.expand()


def test_checker_finds_every_kind_of_unresolved_reference() -> None:
    """Test that the walk reaches plain uses, exclude=, terminators= and brackets."""
    unresolved = _unresolved_references(_faulty_dialect("zzfaulty"))

    for name in (
        "ZzplainKeywordSegment",
        "ZzexcludedKeywordSegment",
        "ZzterminatorKeywordSegment",
        "ZzMissingSegment",
        "ZzStartSegment",
        "ZzEndSegment",
    ):
        assert name in unresolved, name


def test_checker_says_where_inherited_grammar_comes_from() -> None:
    """Test that grammar a dialect inherits sends the reader to the parent."""
    dialect = _faulty_dialect("zzchild")
    unresolved = _unresolved_references(dialect)
    keywords = {"ZZPLAIN": unresolved["ZzplainKeywordSegment"]}

    message = _missing_keywords_message(dialect, keywords)

    # _FaultySegment is defined in this test module, not in zzchild's.
    assert "which zzchild inherits from keyword_reference_test" in message
    assert "unimplemented keyword list in" in message


def test_checker_never_suggests_an_unimplemented_word() -> None:
    """Test that a near miss of an unimplemented word isn't offered as a fix.

    OPTIMIZER_COSTS is unimplemented here, so the dialect doesn't have it and
    "did you mean OPTIMIZER_COSTS, which zzfaulty already has" would be false.
    """
    dialect = _faulty_dialect("zzfaulty")
    unresolved = _unresolved_references(dialect)
    keywords = {"OPTIMIZER_COST": unresolved["Optimizer_costKeywordSegment"]}

    message = _missing_keywords_message(dialect, keywords)

    assert "Did you mean" not in message


def test_checker_suggests_a_close_segment_name() -> None:
    """Test that a misspelt Ref() gets a suggestion and a file to fix."""
    dialect = _faulty_dialect("zzfaulty")
    segments = {"TableReferenceSegmnt": {("SomeSegment", "dialect_zzfaulty")}}

    message = _missing_segments_message(dialect, segments)

    assert "Did you mean TableReferenceSegment?" in message
    assert "src/sqlfluff/dialects/dialect_zzfaulty.py" in message


def test_checker_finds_and_explains_an_overlap() -> None:
    """Test that a word given a second status after declaring is found."""
    dialect = load_raw_dialect("ansi").copy_as("zzoverlap")
    dialect.declare_keyword_sets(
        reserved=["SELECT"], unreserved=[], future_reserved=[], unimplemented=[]
    )
    dialect.sets("unreserved_keywords").add("SELECT")

    overlaps = _overlaps(dialect)
    message = _overlaps_message(dialect, overlaps)

    assert overlaps == {"SELECT": ["reserved_keywords", "unreserved_keywords"]}
    assert "- SELECT: reserved_keywords and unreserved_keywords" in message
    assert "src/sqlfluff/dialects/dialect_zzoverlap.py" in message


def test_checker_explains_a_keyword_in_the_dialects_own_grammar() -> None:
    """Test the advice for grammar the failing dialect defines itself.

    It points at the dialect's own keyword file, offers a close keyword the
    dialect really has, and doesn't offer the unimplemented route.
    """
    dialect = _faulty_dialect("zzfaulty")
    keywords = {
        "SELEECT": {("SomeSegment", "dialect_zzfaulty")},
        "ZZNOTHINGLIKEIT": {("SomeSegment", "dialect_zzfaulty")},
    }

    message = _missing_keywords_message(dialect, keywords)

    assert "- SELEECT (in SomeSegment, zzfaulty's own grammar)" in message
    assert "Did you mean SELECT, which zzfaulty already has?" in message
    assert "src/sqlfluff/dialects/dialect_zzfaulty_keywords.py" in message
    assert "unimplemented" not in message


def test_checker_offers_no_guess_for_an_unlike_segment_name() -> None:
    """Test that a Ref() with no close name gets advice but no guess."""
    dialect = _faulty_dialect("zzfaulty")
    segments = {"QqqqqqSegment": {("SomeSegment", "dialect_zzfaulty")}}

    message = _missing_segments_message(dialect, segments)

    assert "Did you mean" not in message
    assert "Fix the name in that Ref(), or define QqqqqqSegment." in message


class _OwnGrammarSegment(BaseSegment):
    """A segment that the zzown dialect defines itself, using ZZOWNWORD."""

    type = "select_clause_modifier"
    match_grammar = Sequence(Ref.keyword("ZZOWNWORD"))


_OwnGrammarSegment.__module__ = "sqlfluff.dialects.dialect_zzown"


def test_checker_finds_an_unimplemented_word_in_own_grammar() -> None:
    """Test that unimplemented can't switch off the dialect's own grammar.

    The same word used only by inherited grammar is fine: that is what
    unimplemented is for.
    """
    dialect = load_raw_dialect("ansi").copy_as("zzown")
    dialect.replace(SelectClauseModifierSegment=_OwnGrammarSegment)
    dialect.declare_keyword_sets(
        reserved=load_raw_dialect("ansi").sets("reserved_keywords"),
        unreserved=[],
        future_reserved=[],
        unimplemented=["ZZOWNWORD"],
    )
    expanded = dialect.expand()

    found = _unimplemented_in_own_grammar(expanded)
    message = _unimplemented_in_own_grammar_message(expanded, found)

    assert found == {"ZZOWNWORD": {("_OwnGrammarSegment", "dialect_zzown")}}
    assert "- ZZOWNWORD (in _OwnGrammarSegment)" in message

    inherited = _faulty_dialect("zzinherits")
    assert "OPTIMIZER_COSTS" in inherited.sets("unimplemented_keywords")
    assert not _unimplemented_in_own_grammar(inherited)


def test_checker_tells_a_new_dialect_how_to_opt_in() -> None:
    """Test that the opt-in message names the files and the way out."""
    message = _opt_in_instructions("zzdb")

    assert "src/sqlfluff/dialects/dialect_zzdb_keywords.py" in message
    assert "zzdb_dialect.declare_keyword_sets()" in message
    assert 'add "zzdb" to UNAUDITED_DIALECTS' in message


def _keywords_used(dialect: Dialect) -> set[str]:
    """The words the dialect's grammar refers to as keywords."""
    return {
        name[: -len("KeywordSegment")].upper()
        for name in _reference_uses(dialect)
        if name.endswith("KeywordSegment")
    }


def _wrapped(words: list[str], indent: str = "    ") -> list[str]:
    """Words as indented lines of at most 88 characters."""
    lines: list[str] = []
    line = indent
    for word in words:
        if len(line) + len(word) + 1 > 88 and line.strip():
            lines.append(line.rstrip())
            line = indent
        line += word + " "
    if line.strip():
        lines.append(line.rstrip())
    return lines


def _unused_keyword_report(dialect_names: list[str]) -> str:
    """Keywords listed in a dialect's keyword sets that no grammar uses.

    Used means referred to as a keyword. An entry is a lead, not a verdict:
    it may be syntax sqlfluff doesn't parse yet, a word that can go, or a
    function name the function-name parser matches, like ABS.
    """
    lines = [
        "Keywords no grammar uses. Two ways to read this:",
        "- Missing grammar: where a dialect's keyword lists come from the "
        "database's own source, an unused keyword often marks syntax the "
        "database has and sqlfluff doesn't parse yet.",
        "- Clean-up: a word that isn't a keyword of the database at all can go. "
        "Check first: used means referred to as a keyword, so a function name "
        "like ABS, matched as a name, shows up here too, and reserved words "
        "stop names even when no grammar uses them.",
        "",
    ]
    used_anywhere: set[str] = set()
    listed_anywhere: set[str] = set()
    for name in dialect_names:
        dialect = dialect_selector(name)
        used = _keywords_used(dialect)
        used_anywhere |= used
        for label in ("reserved_keywords", "unreserved_keywords"):
            listed_anywhere |= dialect.sets(label)
        unused = sorted(dialect.sets("unreserved_keywords") - used)
        parent_name = load_raw_dialect(name).inherits_from
        inherited: set[str] = set()
        if parent_name:
            parent = dialect_selector(parent_name)
            for label in KEYWORD_STATUS_SETS:
                inherited |= parent.sets(label)
        from_parent = [word for word in unused if word in inherited]
        own = [word for word in unused if word not in inherited]
        lines.append(
            f"{name}: {len(unused)} unreserved keywords its grammar doesn't use"
        )
        if from_parent:
            lines.append(f"  {len(from_parent)} also in {parent_name}'s keywords:")
            lines.extend(_wrapped(from_parent))
        if own:
            lines.append(f"  {len(own)} only in {name}'s keywords:")
            lines.extend(_wrapped(own))
        lines.append("")
    never = sorted(listed_anywhere - used_anywhere)
    lines.append(
        f"{len(never)} reserved or unreserved keywords that no grammar in these "
        "dialects uses:"
    )
    lines.extend(_wrapped(never))
    return "\n".join(lines)


def _with_descendants(dialect_names: list[str]) -> list[str]:
    """These dialects and every dialect that inherits from them, at any depth.

    Grammar added to a dialect reaches its children, so a change is checked
    there too, without the person making it having to know the family tree.
    """
    parents = {name: load_raw_dialect(name).inherits_from for name in ALL_DIALECTS}
    chosen = list(dialect_names)
    for name in ALL_DIALECTS:
        ancestor = parents[name]
        while ancestor is not None and ancestor not in dialect_names:
            ancestor = parents.get(ancestor)
        if ancestor is not None and name not in chosen:
            chosen.append(name)
    return chosen


def test_with_descendants_adds_children_at_any_depth() -> None:
    """Test that naming a parent dialect also checks the dialects below it."""
    assert _with_descendants(["mysql"]) == ["mysql", "doris", "mariadb", "starrocks"]
    assert _with_descendants(["tsql"]) == ["tsql"]
    assert set(_with_descendants(["ansi"])) == set(ALL_DIALECTS)


def _audit_report(dialect_names: list[str]) -> str:
    """What the checks in this file find in each of these dialects.

    For an audited dialect, these are the failures pytest would show. For one
    in UNAUDITED_DIALECTS, they are the problems to fix before opting it in.
    """
    return _audit_report_of({name: dialect_selector(name) for name in dialect_names})


def _audit_report_of(dialects: dict[str, Dialect]) -> str:
    """The audit report for these dialects, by name."""
    lines = [
        "Audit: what the checks in this file find in each dialect. For an "
        "audited dialect, pytest fails on these. For one in UNAUDITED_DIALECTS, "
        "they are what opting in would bring.",
        "",
    ]
    for name, dialect in dialects.items():
        audited = name not in UNAUDITED_DIALECTS
        unresolved = _unresolved_references(dialect)
        keywords = {
            reference[: -len("KeywordSegment")].upper(): owners
            for reference, owners in unresolved.items()
            if reference.endswith("KeywordSegment")
        }
        segments = {
            reference: owners
            for reference, owners in unresolved.items()
            if not reference.endswith("KeywordSegment")
        }
        overlaps = _overlaps(dialect)
        own_unimplemented = _unimplemented_in_own_grammar(dialect)
        if not (keywords or segments or overlaps or own_unimplemented):
            if audited:
                lines.append(f"{name}: audited, nothing to fix.")
            else:
                lines.append(f"{name}: nothing to fix, ready to opt in.")
            lines.append("")
            continue
        if audited:
            lines.append(f"{name} (audited, so pytest fails on these):")
        else:
            lines.append(f"{name} (unaudited):")
        if keywords:
            lines.append(_missing_keywords_message(dialect, keywords))
        if segments:
            lines.append(_missing_segments_message(dialect, segments))
        if overlaps and audited:
            lines.append(_overlaps_message(dialect, overlaps))
        elif overlaps:
            lines.append(
                f"{len(overlaps)} words have more than one keyword status today. "
                "declare_keyword_sets() sorts out those inherited from a parent "
                "dialect; only a word listed twice in this dialect's own keyword "
                "file needs an edit:"
            )
            lines.extend(_wrapped(sorted(overlaps)))
        if own_unimplemented:
            lines.append(
                _unimplemented_in_own_grammar_message(dialect, own_unimplemented)
            )
        lines.append("")
    return "\n".join(lines)


def test_audit_report_covers_audited_and_unaudited_dialects() -> None:
    """Test that the report answers for any dialect it is given."""
    report = _audit_report(["mysql", "tsql"])

    assert "mysql: audited, nothing to fix." in report
    assert "tsql (unaudited):" in report
    assert "MARK" in report


def test_audit_report_covers_ready_dialects_segments_and_overlaps() -> None:
    """Test the report's other parts on a ready and a broken dialect."""
    ready = load_raw_dialect("ansi").copy_as("zzready")
    # The two keywords ansi's GRANT grammar used without listing, so this
    # dialect is ready however ansi itself stands.
    ready.sets("unreserved_keywords").update(["FORMATS", "POLICIES"])
    broken = _faulty_dialect("zzbroken")
    broken.sets("unreserved_keywords").add("SELECT")
    dialects = {"zzready": ready.expand(), "zzbroken": broken}
    UNAUDITED_DIALECTS.update(dialects)
    try:
        report = _audit_report_of(dialects)
    finally:
        UNAUDITED_DIALECTS.difference_update(dialects)

    assert "zzready: nothing to fix, ready to opt in." in report
    assert "refers to segments or grammars that don't exist" in report
    assert "words have more than one keyword status today" in report


def test_audit_report_shows_an_audited_dialect_its_pytest_failures() -> None:
    """Test that a broken audited dialect gets the messages pytest gives it."""
    broken = _faulty_dialect("zzauditedbroken")
    broken.sets("unreserved_keywords").add("SELECT")
    own = load_raw_dialect("ansi").copy_as("zzown")
    own.replace(SelectClauseModifierSegment=_OwnGrammarSegment)
    own.declare_keyword_sets(
        reserved=load_raw_dialect("ansi").sets("reserved_keywords"),
        unreserved=[],
        future_reserved=[],
        unimplemented=["ZZOWNWORD"],
    )

    report = _audit_report_of({"zzauditedbroken": broken, "zzown": own.expand()})

    assert "zzauditedbroken (audited, so pytest fails on these):" in report
    assert "In the zzauditedbroken dialect, these words have more" in report
    assert "zzown (audited, so pytest fails on these):" in report
    assert "- ZZOWNWORD (in _OwnGrammarSegment)" in report


def test_checker_says_when_a_lower_dialect_dropped_a_keyword() -> None:
    """Test the advice when the grammar's own dialect already lists the word.

    The word got lost lower down, when a dialect replaced its keyword lists,
    so the fix belongs in the failing dialect, not in the parent.
    """
    child = load_raw_dialect("ansi").copy_as("zzdropped")
    child.sets("unreserved_keywords").clear()
    expanded = child.expand()
    unresolved = _unresolved_references(expanded)
    keywords = {
        name[: -len("KeywordSegment")].upper(): owners
        for name, owners in unresolved.items()
        if name.endswith("KeywordSegment")
        and any(module == "dialect_ansi" for _, module in owners)
    }
    word = sorted(keywords)[0]

    message = _missing_keywords_message(expanded, {word: keywords[word]})

    assert "ansi already lists it, so zzdropped" in message
    assert "src/sqlfluff/dialects/dialect_zzdropped_keywords.py" in message


def test_unused_keyword_report_has_both_sections() -> None:
    """Test that the report lists per-dialect and cross-dialect unused words."""
    report = _unused_keyword_report(["mariadb"])

    assert "mariadb: " in report
    assert "also in mysql's keywords:" in report
    assert "that no grammar in these dialects uses:" in report


if __name__ == "__main__":  # pragma: no cover
    # With dialect names as arguments, report on those and their descendants.
    unknown = [name for name in sys.argv[1:] if name not in ALL_DIALECTS]
    if unknown:
        sys.exit(
            f"Unknown dialect(s): {', '.join(unknown)}. "
            f"Dialects: {', '.join(ALL_DIALECTS)}."
        )
    chosen = _with_descendants(sys.argv[1:]) if sys.argv[1:] else ALL_DIALECTS
    print(_audit_report(chosen))
    print(_unused_keyword_report(chosen))
