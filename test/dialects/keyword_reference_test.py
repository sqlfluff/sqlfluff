"""Keyword and reference checks for the dialects, and how to set up keywords.

How to set up a dialect's keywords
==================================

Every keyword has a status: reserved (never a name), unreserved (a keyword
that can also be a name), or unimplemented (the dialect's server doesn't have
it). These don't overlap. Future reserved is a tag that can go with unreserved
or unimplemented. A dialect sets its statuses with one call to
declare_keyword_sets() (see its docstring in src/sqlfluff/core/dialects/
base.py). A word the grammar uses with no status at all crashes the parser.

The essentials. You get these almost for free by using declare_keyword_sets(),
and for an audited dialect (every dialect not in UNAUDITED_DIALECTS below) the
audit tests lock them in, in CI.

1. Get the reserved keywords from the docs, or better, from the server's own
   grammar or keyword table: docs can be wrong. Pass them as reserved=, with
   reserved_mode="replace", so the list is exhaustive and any reserved word
   you inherit and don't list becomes unreserved.

2. Get the unreserved keywords the same way and pass them as unreserved=.
   Also add any words sqlfluff's grammar needs that aren't in the docs.
   Postgres manages this well internally (dialect_postgres_keywords.py), but
   other ways are fine; it's up to the dialect.

   Too many unreserved words costs almost nothing: RF04 and RF06 (both off by
   default) treat them as keywords and may flag names they arguably needn't.

This is a good place to stop. You never have to do step 3 or later, but if you
want RF04 cleaned up, or you know for sure your server doesn't use a word, do
step 3 too.

Optional.

3. When the docs, or anything else you know about this server, show that it
   doesn't implement a word, pass it in unimplemented=. That does two things:
   if the parent dialect adds grammar that uses the word, that grammar won't
   match in your dialect, and RF04 is more accurate, if anyone turns it on.
   Only do this with evidence. A word missing from a vendor's grammar file
   isn't evidence: the server may still accept it as a plain identifier.

Even more optional.

4. Run ``python test/dialects/keyword_reference_test.py <dialect> --level
   notice`` to see the inherited grammar your unimplemented words switch off.
   If you picked those words correctly, every entry is right. If you didn't,
   this finds grammar support that a wrong choice is hiding. Check each one:

   - If your server supports it, move the word from unimplemented= to
     unreserved=.
   - If it doesn't, you can override that grammar in your own dialect, with
     Nothing() or with a copy of the parent's grammar minus the parts your
     server lacks, so anyone reading the code later can see it was on
     purpose. The word then drops off the notice list, which makes the next
     audit easy after the parent dialect (usually ansi) changes.

5. Update your keyword lists from the server's docs or source at least every
   few years, to keep the dialect current.

To make the above work, the audit can't encourage dialects to remove words
from unimplemented if the dialect's grammar doesn't use them. A dialect that
has really researched a word may have overridden the grammar that needed it
with Nothing(), or with a custom version of the parent's minus the unsupported
parts; then no grammar uses the word, and that's correct. db2's NATURAL is an
example. Few dialects will get that far, and none has to.

If you have to guess to stop a crash, as clickhouse and db2 do, say so in a
comment at the call. The lists aren't great and need help.

Why declare_keyword_sets():

1. When a parent dialect adds a keyword, it never crashes a child with a
   missing ref, and a poorly kept child puts no burden on whoever adds the
   feature. To see where a keyword isn't supported, run the audit with
   --level notice or --level info.
2. It gives every dialect a clear path toward better keyword lists, without
   making that work the price of not crashing.

What this file checks
=====================

An audited dialect is held to these rules, checked on its final keyword sets
however it built them:

- No word has two statuses that exclude each other: reserved and unreserved,
  unimplemented and either of those, or reserved and future reserved.
- Every keyword and reference its grammar can reach resolves: keywords,
  segments, bracket pairs, and those inside a Ref's exclude= and terminators=.
  One that doesn't crashes the parser on any statement that reaches the rule
  using it, even when the statement doesn't contain the word. A keyword the
  grammar uses can't be only future reserved, which says nothing about what it
  is now.
- Every keyword its grammar uses is one token to its lexer, so it can match.
- Its keyword lists hold only words, or words joined by - or a space.
- Its own grammar doesn't use its unimplemented words.

The failure messages are written for someone who has never touched the
dialect, usually because they changed its parent: each says what is wrong,
where, and what has to become true. The tests at the end check the checker
itself, so that a gap in it fails rather than quietly checking less.

The report
==========

Run this file directly, ``python test/dialects/keyword_reference_test.py``, for
a report, which ends in PASS or FAIL and exits 1 on FAIL. Passing means nothing
crashes and no check fails, not that the keyword lists are right. It shows
what these checks find in each dialect: for an audited one, the failures
pytest would show; for an unaudited one, what auditing it would bring, and
when it passes, that it can come off the list. As notices, it also lists
inherited grammar that unimplemented words switch off; as info, the keywords no
grammar uses. --level error,
warning, notice or info sets how much is shown. Name dialects as arguments to
report on just those and the dialects that inherit from them, as the parser's
"not found in the ... dialect" errors suggest.
"""

import contextlib
import functools
import inspect
import os
import re
import signal
import sys
import textwrap
from collections.abc import Iterator, Mapping
from difflib import get_close_matches
from typing import NamedTuple, cast
from weakref import WeakKeyDictionary

import pytest

from sqlfluff.core.dialects import (
    dialect_readout,
    dialect_selector,
    load_raw_dialect,
)
from sqlfluff.core.dialects.base import (
    KEYWORD_STATUS_SETS,
    Dialect,
)
from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.parser.grammar.base import Ref
from sqlfluff.core.parser.grammar.sequence import Sequence
from sqlfluff.core.parser.lexer import PyLexer
from sqlfluff.core.parser.matchable import Matchable

# Dialects these checks don't run for yet. Every other dialect, including any
# new one, is audited. To audit one of these, run this file with its name as
# an argument, fix what the report shows, and remove it from here.
UNAUDITED_DIALECTS = {
    "athena",
    "bigquery",
    "databricks",
    "duckdb",
    "flink",
    "greenplum",
    "hive",
    "impala",
    "materialize",
    "oracle",
    "postgres",
    "redshift",
    "snowflake",
    "tsql",
    "vertica",
}

ALL_DIALECTS = sorted(info.label for info in dialect_readout())

AUDITED_DIALECTS = sorted(set(ALL_DIALECTS) - UNAUDITED_DIALECTS)

# What a missing keyword does, said wherever one is reported.
CRASH_EFFECT = (
    "Any statement that reaches that grammar crashes the parser, and the whole "
    "file is dropped from the output, even when the statement doesn't contain "
    "the word."
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


# One walk per dialect object: the checks each need it, and a walk takes
# hundreds of milliseconds. Keyed weakly, so a dialect built for one test is
# forgotten with it. The walk follows the library, which doesn't change after
# expand(), so later changes to keyword sets don't make it stale.
_WALKS: "WeakKeyDictionary[Dialect, list[tuple[Owner, Ref]]]" = WeakKeyDictionary()


def _reference_walk(dialect: Dialect) -> list[tuple[Owner, Ref]]:
    """Every Ref the dialect's grammar can reach, with where it is used.

    Walks everything reachable from the dialect's root. Where a Ref is used is
    the segment whose grammar uses it, or the named grammar (a dialect.add()
    entry) that does.
    """
    cached = _WALKS.get(dialect)
    if cached is not None:
        return cached
    found = _walk_references(dialect)
    _WALKS[dialect] = found
    return found


def _walk_references(dialect: Dialect) -> list[tuple[Owner, Ref]]:
    """The walk behind _reference_walk(), uncached."""
    found: list[tuple[Owner, Ref]] = []
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
            found.append((owner, node))
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
    return found


def _reference_uses(dialect: Dialect) -> dict[str, set[Owner]]:
    """Every name the dialect's grammar refers to, and where it is used."""
    uses: dict[str, set[Owner]] = {}
    for owner, ref in _reference_walk(dialect):
        uses.setdefault(ref._ref, set()).add(owner)
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


def _direct_references(grammar: object) -> set[str]:
    """The names a grammar refers to itself, without following its Refs."""
    names: set[str] = set()
    seen: set[int] = set()
    stack = [grammar]
    while stack:
        node = stack.pop()
        if id(node) in seen or inspect.isclass(node):
            continue
        seen.add(id(node))
        if isinstance(node, Ref):
            names.add(node._ref)
        stack.extend(_grammar_children(node))
    return names


def _parent_uses(parent: Dialect, element_name: str) -> set[str]:
    """The names the parent's element of that name refers to directly."""
    element = parent._library.get(element_name)
    if inspect.isclass(element):
        element = getattr(element, "match_grammar", None)
    if element is None:
        return set()
    return _direct_references(element)


def _unimplemented_in_own_grammar(dialect: Dialect) -> dict[str, set[Owner]]:
    """Unimplemented keywords that the dialect's own grammar uses.

    Unimplemented is for grammar a dialect inherits but doesn't have. If the
    dialect's own grammar uses the word, the dialect does have it, and the
    entry switches that grammar off.

    Own means written for this dialect. A dialect's segment often reuses its
    parent's grammar (match_grammar.copy(...), or OneOf(parent.X.match_grammar,
    ...)), and the parent's keywords inside it are still inherited. So a use is
    own only if the parent's element of the same name doesn't use that keyword.
    """
    own_module = f"dialect_{dialect.name}"
    parent = None
    if dialect.inherits_from:
        parent = load_raw_dialect(dialect.inherits_from)
    unimplemented = {
        word.capitalize() + "KeywordSegment": word
        for word in dialect.sets("unimplemented_keywords")
    }
    # A segment is registered under its library name, which may differ from
    # its class name; the parent's element is found by the library name.
    library_names = {
        element.__name__: name
        for name, element in dialect._library.items()
        if isinstance(element, type)
    }
    found: dict[str, set[Owner]] = {}
    for owner, ref in _reference_walk(dialect):
        word = unimplemented.get(ref._ref)
        if not word or owner[1] != own_module:
            continue
        element_name = library_names.get(owner[0], owner[0])
        if parent is not None and ref._ref in _parent_uses(parent, element_name):
            continue
        found.setdefault(word, set()).add(owner)
    return found


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
        dialect = _report_dialect(dialect_name)
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


def _docs_line(dialect: Dialect) -> str:
    """The dialect's own advice on looking keywords up, if it gives any."""
    docs = dialect.keyword_reference_error_docs
    if not docs:
        return ""
    return f"\nHow to look up a {dialect.name} keyword: {docs}"


def _status_needed(dialect: Dialect) -> str:
    """What a word without a status needs to become, without saying how.

    Dialects build their keyword sets in different ways (by hand, generated
    from vendor source, computed), so messages say what has to be true and
    where the dialect sets its keywords, and leave the method to whoever
    fixes it.
    """
    name = dialect.name
    vendor = dialect.formatted_name
    return (
        f"Each needs a status in {name}: unreserved if {vendor} has it as a "
        f"keyword (reserved if it can never be a name there), or unimplemented "
        f"if {vendor}'s server doesn't implement it, which stops the parts of "
        "grammar that need it from matching. If you can't check, unreserved "
        f"keeps the grammar working, as the rest of what {name} inherits does. "
        f"{name} sets its keywords in {_dialect_file(f'dialect_{name}')}."
    )


# A bare string in grammar is a keyword reference, so punctuation or a number
# written that way is a bug: the segment it probably meant.
_SYMBOL_SEGMENTS = {
    ",": "CommaSegment",
    "=": "EqualsSegment",
    ".": "DotSegment",
    ";": "SemicolonSegment",
    "*": "StarSegment",
    "(": "StartBracketSegment",
    ")": "EndBracketSegment",
}


def _not_a_word(word: str) -> str:
    """The hint for a "keyword" that isn't a word at all, or nothing."""
    if WORD.match(word):
        return ""
    if KEYWORD_LIST_ENTRY.match(word):
        return (
            f" {word!r} is several tokens to the lexer, so no keyword can match "
            "it. Each keyword reference has to name one token."
        )
    meant = _SYMBOL_SEGMENTS.get(word)
    if meant:
        guess = f'Ref("{meant}")'
    elif word.isdigit():
        guess = "a numeric literal segment"
    else:
        guess = "a symbol or literal segment"
    return (
        f" {word!r} isn't a word: a bare string in grammar is a keyword "
        f"reference, so this probably means {guess}."
    )


# A keyword is matched against one word token: letters, digits, _ and $, not
# starting with a digit. Anything else in grammar is a bug.
WORD = re.compile(r"^[A-Za-z_][A-Za-z0-9_$]*$")

# A keyword list may also hold words joined by - or a space, as vendors publish
# them (the SQL standard's END-EXEC, T-SQL's WITHIN GROUP). No grammar can
# match one, but RF04 still flags it as a quoted identifier ("END-EXEC").
# Anything else in a keyword list is a bug.
KEYWORD_LIST_ENTRY = re.compile(
    r"^[A-Za-z_][A-Za-z0-9_$]*(?:[- ][A-Za-z_][A-Za-z0-9_$]*)*$"
)


# One lexer per dialect object, built from that dialect's own lexer matchers.
_LEXERS: "WeakKeyDictionary[Dialect, PyLexer]" = WeakKeyDictionary()


def _lexed_as(dialect: Dialect, word: str) -> list[str]:
    """The tokens the dialect's lexer makes of the word on its own.

    PyLexer takes its matchers from a config's dialect, and a dialect built in
    a test has no config, so it is given the dialect's matchers directly. The
    Rust lexer is generated from the same matchers.
    """
    lexer = _LEXERS.get(dialect)
    if lexer is None:
        lexer = PyLexer(dialect="ansi")
        lexer.lexer_matchers = dialect.get_lexer_matchers()
        _LEXERS[dialect] = lexer
    segments, _ = lexer.lex(word)
    return [segment.raw for segment in segments if segment.raw.strip()]


def _unmatchable_keywords(dialect: Dialect) -> dict[str, tuple[list[str], set[Owner]]]:
    """Keywords the grammar uses that the dialect's lexer never makes one token.

    A keyword matches one token whose text is the word. If the lexer makes
    anything else of the word, no input can match it, and the grammar that
    needs it is dead. A keyword with no status is left to the missing keyword
    check, which already fails for it.
    """
    found: dict[str, tuple[list[str], set[Owner]]] = {}
    for name, owners in _reference_uses(dialect).items():
        if not name.endswith("KeywordSegment"):
            continue
        word = name[: -len("KeywordSegment")].upper()
        tokens = _lexed_as(dialect, word)
        if [token.upper() for token in tokens] == [word]:
            continue
        try:
            dialect.ref(name)
        except RuntimeError:
            continue
        found[word] = (tokens, owners)
    return found


def _unmatchable_keywords_message(
    dialect: Dialect, found: dict[str, tuple[list[str], set[Owner]]]
) -> str:
    """Say which grammar keywords can never match, and what the lexer makes of them."""
    name = dialect.name
    own_module = f"dialect_{name}"
    lines = [
        f"{name}'s grammar uses keywords that {name}'s lexer never makes into one "
        "token, so the grammar that needs them can never match. Nothing "
        "crashes, but those parts of the grammar are dead: input that needs "
        "them is unparsable."
    ]
    for word, (tokens, owners) in sorted(found.items()):
        segments, modules = _segments_and_files(owners)
        if own_module in modules:
            where = f"{name}'s own grammar"
        else:
            where = "defined in " + " and ".join(
                module.removeprefix("dialect_") for module in modules
            )
        lines.append(
            f"- {word!r} (in {segments}: {where}): the lexer makes "
            f"{', '.join(tokens) or 'nothing'} of it."
        )
    lines.append(
        "  Each keyword reference has to name one token. A phrase is separate "
        'keywords in sequence, e.g. Sequence("WITHIN", "GROUP"). A word the '
        "server reads as one token needs the lexer to produce that token first."
    )
    return "\n".join(lines)


def _missing_keywords_message(dialect: Dialect, keywords: dict[str, set[Owner]]) -> str:
    """Say which keywords the dialect's grammar uses without a status, and where.

    Words a parent still lists, that this dialect lost, are grouped: one
    cause, one fix. The rest are listed one by one, with a guess when a close
    keyword or a symbol was probably meant.
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
        f"{name}'s grammar uses keywords that have no status in {name}. {CRASH_EFFECT}"
    ]
    dropped: dict[str, list[tuple[str, str]]] = {}
    singles: list[tuple[str, str, str]] = []
    for word, owners in sorted(keywords.items()):
        segments, modules = _segments_and_files(owners)
        listers = sorted(
            module.removeprefix("dialect_")
            for module in modules
            if module != own_module
            and _dialect_knows(module.removeprefix("dialect_"), word)
        )
        if listers:
            dropped.setdefault(" and ".join(listers), []).append((word, segments))
            continue
        if own_module in modules:
            where = f"{name}'s own grammar"
        else:
            defined = " and ".join(m.removeprefix("dialect_") for m in modules)
            where = f"defined in {defined}"
        hint = _not_a_word(word)
        if not hint:
            match = get_close_matches(word, known, n=1, cutoff=0.8)
            if match:
                hint = f" Did you mean {match[0]}, which {name} has?"
        singles.append((word, f"{segments}: {where}", hint))
    for word, where, hint in singles:
        lines.append(f"- {word} (in {where}):{hint or ' no close keyword.'}")
    if singles:
        lines.append(f"  {_status_needed(dialect)}")
    for listed_by, words in sorted(dropped.items()):
        width = max(len(word) for word, _ in words)
        lines.append(
            f"- {len(words)} that {listed_by} lists, lost in {name}. {name}'s "
            "keyword setup drops words it inherits; declare_keyword_sets() "
            "never drops them, in either mode:"
        )
        for word, segments in words:
            lines.append(f"    {word.ljust(width)}  in {segments}")
        lines.append(f"  {_status_needed(dialect)}")
    return "\n".join(lines) + _docs_line(dialect)


def _missing_segments_message(dialect: Dialect, segments: dict[str, set[Owner]]) -> str:
    """Say, for each reference to a segment that doesn't exist, where it is."""
    name = dialect.name
    lines = [
        f"{name}'s grammar refers to segments or grammars that don't exist in "
        f"{name}. {CRASH_EFFECT.replace('the word', 'the name')} These are "
        "usually typos in a Ref()."
    ]
    for missing, owners in sorted(segments.items()):
        users, modules = _segments_and_files(owners)
        files = " and ".join(_dialect_file(module) for module in modules)
        lines.append(
            f'- Ref("{missing}") (in {users}, in {files}):'
            f"{_keyword_meant(dialect, missing)}"
        )
    return "\n".join(lines)


def _keyword_meant(dialect: Dialect, missing: str) -> str:
    """The advice for one missing Ref(), spotting a keyword written as a segment.

    Segment names are CamelCase, so an all-capitals name like Ref("COLUMN") is
    almost always a keyword that should have been Ref.keyword("COLUMN"). Without
    this, the advice would be to define a COLUMN segment, which is wrong.
    """
    if not missing.isupper():
        existing = {
            element
            for element in dialect._library
            if not element.endswith("KeywordSegment")
        }
        return (
            f"{_did_you_mean(missing, existing)} Fix the name in that Ref(), or "
            f"define {missing}."
        )
    name = dialect.name
    known = any(
        missing in dialect.sets(label)
        for label in (
            "reserved_keywords",
            "unreserved_keywords",
            "future_reserved_keywords",
        )
    )
    if known:
        return (
            f" {missing} is a {name} keyword, so this is probably meant to be "
            f'Ref.keyword("{missing}"), or just "{missing}".'
        )
    return (
        " this looks like a keyword written as a segment: "
        f'Ref.keyword("{missing}"), or just "{missing}" (a bare string in '
        f"grammar is a keyword reference). {missing} then needs a status in "
        f"{name}."
    )


def _overlaps(dialect: Dialect) -> dict[str, list[str]]:
    """Each word in two statuses that can't go together, and those statuses.

    A word is reserved or unreserved, not both, and a future reserved word is
    never reserved. Unimplemented is a tag that may go with anything.
    """
    pairs = [
        ("reserved_keywords", "unreserved_keywords"),
        ("reserved_keywords", "future_reserved_keywords"),
    ]
    overlaps: dict[str, list[str]] = {}
    for first, second in pairs:
        for word in dialect.sets(first) & dialect.sets(second):
            overlaps.setdefault(word, [])
            for label in (first, second):
                if label not in overlaps[word]:
                    overlaps[word].append(label)
    return overlaps


def _overlaps_message(dialect: Dialect, overlaps: dict[str, list[str]]) -> str:
    """Say which words have two statuses, how they behave, and what's needed."""
    name = dialect.name
    lines = [
        f"These words have two statuses that can't go together in {name}. They "
        "behave as reserved: keywords that can't be names. Nothing crashes. Each "
        "needs one status; declare_keyword_sets() never leaves a word in both, "
        f"so something set these directly. {name} sets its keywords in "
        f"{_dialect_file(f'dialect_{name}')}."
    ]
    for word, labels in sorted(overlaps.items()):
        lines.append(f"- {word}: {' and '.join(labels)}")
    return "\n".join(lines) + _docs_line(dialect)


def _known_keywords(dialect: Dialect) -> set[str]:
    """Every word the dialect gives any status."""
    known: set[str] = set()
    for label in KEYWORD_STATUS_SETS:
        known.update(dialect.sets(label))
    return known


def _future_only_uses(dialect: Dialect) -> dict[str, set[Owner]]:
    """Keywords the grammar uses whose only status is future reserved."""
    current: set[str] = set()
    for label in (
        "reserved_keywords",
        "unreserved_keywords",
        "unimplemented_keywords",
    ):
        current.update(dialect.sets(label))
    uses = _reference_uses(dialect)
    found: dict[str, set[Owner]] = {}
    for word in dialect.sets("future_reserved_keywords") - current:
        owners = uses.get(word.capitalize() + "KeywordSegment")
        if owners:
            found[word] = owners
    return found


def _future_only_message(dialect: Dialect, found: dict[str, set[Owner]]) -> str:
    """Say which grammar keywords have only the future reserved tag."""
    name = dialect.name
    lines = [
        f"{name}'s grammar uses these words as keywords, but their only status "
        "is future reserved, which says what the vendor plans, not what the word "
        "is now. Each needs a status for now as well, usually unreserved, keeping "
        f"the future tag. {name} sets its keywords in "
        f"{_dialect_file(f'dialect_{name}')}."
    ]
    for word, owners in sorted(found.items()):
        segments, _ = _segments_and_files(owners)
        lines.append(f"- {word}: in {segments}")
    return "\n".join(lines) + _docs_line(dialect)


def _non_word_keywords(dialect: Dialect) -> dict[str, list[str]]:
    """Entries in the dialect's keyword sets that aren't words or phrases."""
    found: dict[str, list[str]] = {}
    for label in KEYWORD_STATUS_SETS:
        for entry in dialect.sets(label):
            if not KEYWORD_LIST_ENTRY.match(entry):
                found.setdefault(entry, []).append(label)
    return found


def _introduced_by(dialect: Dialect, entry: str, label: str) -> str:
    """The dialect that first put an entry in that keyword set.

    Walks up the parents while they hold the same entry in the same set; the
    last one that does is where it was written.
    """
    origin = dialect.name
    parent_name = dialect.inherits_from
    while parent_name:
        parent = load_raw_dialect(parent_name)
        if entry not in parent.sets(label):
            break
        origin = parent_name
        parent_name = parent.inherits_from
    return origin


def _keyword_source_file(dialect_name: str) -> str:
    """Where a dialect's keyword lists are written: its keyword file if any."""
    keyword_file = f"{DIALECTS_DIR}/dialect_{dialect_name}_keywords.py"
    if os.path.exists(keyword_file):
        return keyword_file
    return _dialect_file(f"dialect_{dialect_name}")


def _non_word_keywords_message(dialect: Dialect, found: dict[str, list[str]]) -> str:
    """Say which keyword list entries aren't words, and where to delete them.

    A non-word can't be referenced by any grammar, so deleting it can't crash
    anything; the only question is where it was written.
    """
    name = dialect.name
    lines = [
        f"These entries in {name}'s keyword sets aren't words. A keyword list "
        "holds words, or words joined by - or a space as a vendor publishes "
        "them (END-EXEC, WITHIN GROUP). These are neither, so they are bugs in "
        "the lists. Nothing crashes, and since no grammar can refer to them, "
        "deleting them can't break anything."
    ]
    for entry, labels in sorted(found.items()):
        for label in labels:
            origin = _introduced_by(dialect, entry, label)
            status = label.removesuffix("_keywords")
            where = (
                f"in {name}'s own lists"
                if origin == name
                else f"inherited from {origin}"
            )
            lines.append(
                f"- {entry!r} ({status}, {where}): delete it from {origin}'s "
                f"{status} list in {_keyword_source_file(origin)}"
                + (
                    "; every dialect that inherits it is fixed too."
                    if origin != name
                    else "."
                )
            )
    return "\n".join(lines)


@pytest.mark.parametrize("dialect_name", ALL_DIALECTS)
def test_grammar_keywords_can_match(dialect_name: str) -> None:
    """Test that every keyword the grammar uses is one token to the lexer.

    Every dialect passes, so this runs for all of them, audited or not.
    """
    dialect = _report_dialect(dialect_name)
    found = _unmatchable_keywords(dialect)

    assert not found, _unmatchable_keywords_message(dialect, found)


@pytest.mark.parametrize("dialect_name", AUDITED_DIALECTS)
def test_keyword_lists_hold_only_words(dialect_name: str) -> None:
    """Test that every keyword set entry is a single word."""
    dialect = _report_dialect(dialect_name)
    found = _non_word_keywords(dialect)

    assert not found, _non_word_keywords_message(dialect, found)


def test_settled_unimplemented_words_are_info() -> None:
    """Test that an unimplemented word no grammar uses is info, not a notice.

    ZONE is used by inherited ansi grammar (AT TIME ZONE), so it switches that
    off and stays a notice; ZZSETTLED is used by nothing.
    """
    dialect = load_raw_dialect("ansi").copy_as("zzsettled")
    _declare(dialect, unimplemented=["ZONE", "ZZSETTLED"])
    findings = _audit_findings("zzsettled", dialect.expand())
    settled = [
        f for f in findings if f.title == "Unimplemented keywords no grammar uses"
    ]

    assert [f.level for f in settled] == ["info"]
    assert "ZZSETTLED" in settled[0].message
    assert "ZONE" not in settled[0].message


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
    """Say which tagged words the dialect's own grammar needs."""
    name = dialect.name
    vendor = dialect.formatted_name
    lines = [
        f"{name}'s own grammar uses these words, but they're tagged "
        f"unimplemented in {name} ({vendor}'s server doesn't implement them), so "
        "that grammar never matches. Unimplemented is for grammar inherited "
        f"from a parent. Either {vendor} does implement them, and they need a "
        "keyword status instead of the tag, or the grammar that uses them is "
        f"wrong for {name}. {name} sets its keywords in "
        f"{_dialect_file(f'dialect_{name}')}."
    ]
    for word, owners in sorted(found.items()):
        segments, _ = _segments_and_files(owners)
        lines.append(f"- {word}: in {segments}")
    return "\n".join(lines)


@pytest.mark.parametrize("dialect_name", AUDITED_DIALECTS)
def test_unimplemented_keywords_are_not_in_own_grammar(dialect_name: str) -> None:
    """Test that no unimplemented keyword is used by the dialect's own grammar."""
    dialect = _report_dialect(dialect_name)
    found = _unimplemented_in_own_grammar(dialect)

    assert not found, _unimplemented_in_own_grammar_message(dialect, found)


@pytest.mark.parametrize("dialect_name", AUDITED_DIALECTS)
def test_keyword_statuses_are_disjoint(dialect_name: str) -> None:
    """Test that no word has two statuses that can't go together."""
    dialect = _report_dialect(dialect_name)
    overlaps = _overlaps(dialect)

    assert not overlaps, _overlaps_message(dialect, overlaps)


@pytest.mark.parametrize("dialect_name", AUDITED_DIALECTS)
def test_grammar_keywords_are_not_only_future_reserved(dialect_name: str) -> None:
    """Test that a keyword the grammar uses has a status for now."""
    dialect = _report_dialect(dialect_name)
    found = _future_only_uses(dialect)

    assert not found, _future_only_message(dialect, found)


@pytest.mark.parametrize("dialect_name", AUDITED_DIALECTS)
def test_grammar_references_resolve(dialect_name: str) -> None:
    """Test that every reference the dialect's grammar can reach resolves."""
    dialect = _report_dialect(dialect_name)
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


def _declare(dialect: Dialect, mode: str = "add", **lists: list[str]) -> None:
    """Call declare_keyword_sets() with empty lists for those not given."""
    dialect.declare_keyword_sets(
        reserved=lists.get("reserved", []),
        reserved_mode=mode,
        unreserved=lists.get("unreserved", []),
        unimplemented=lists.get("unimplemented", []),
        future_reserved=lists.get("future_reserved", []),
        future_reserved_mode="replace",
    )


def _faulty_dialect(name: str) -> Dialect:
    """An expanded ansi copy whose grammar reaches _FaultySegment."""
    dialect = load_raw_dialect("ansi").copy_as(name)
    dialect.replace(SelectClauseModifierSegment=_FaultySegment)
    _declare(dialect, unimplemented=["OPTIMIZER_COSTS"])
    dialect.bracket_sets("bracket_pairs").add(
        ("zz", "ZzStartSegment", "ZzEndSegment", True)
    )
    return dialect.expand()


def _ready_dialect(name: str) -> Dialect:
    """An expanded ansi copy that passes every check."""
    dialect = load_raw_dialect("ansi").copy_as(name)
    # The two keywords ansi's GRANT grammar used without listing, so this
    # dialect is ready however ansi itself stands.
    dialect.sets("unreserved_keywords").update(["FORMATS", "POLICIES"])
    return dialect.expand()


def _failing_dialect(name: str) -> Dialect:
    """A _faulty_dialect that also has a warning: SELECT in two statuses."""
    dialect = _faulty_dialect(name)
    dialect.sets("unreserved_keywords").add("SELECT")
    return dialect


@contextlib.contextmanager
def _unaudited(*names: str) -> Iterator[None]:
    """Treat these test dialects as not required to pass, for a while."""
    UNAUDITED_DIALECTS.update(names)
    try:
        yield
    finally:
        UNAUDITED_DIALECTS.difference_update(names)


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
    assert (
        "- ZZPLAIN (in _FaultySegment: defined in keyword_reference_test):" in message
    )
    assert (
        "zzchild sets its keywords in src/sqlfluff/dialects/dialect_zzchild.py."
        in message
    )


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
    _declare(dialect, reserved=["SELECT"], future_reserved=["ZZLATER"])
    dialect.sets("unreserved_keywords").add("SELECT")
    dialect.sets("future_reserved_keywords").add("SELECT")
    # A future reserved word may also be unreserved.
    dialect.sets("unreserved_keywords").add("ZZLATER")

    overlaps = _overlaps(dialect)
    message = _overlaps_message(dialect, overlaps)

    assert overlaps == {
        "SELECT": [
            "reserved_keywords",
            "unreserved_keywords",
            "future_reserved_keywords",
        ]
    }
    assert (
        "- SELECT: reserved_keywords and unreserved_keywords and "
        "future_reserved_keywords" in message
    )
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

    assert "- SELEECT (in SomeSegment: zzfaulty's own grammar):" in message
    assert "Did you mean SELECT, which zzfaulty has?" in message
    assert (
        "- ZZNOTHINGLIKEIT (in SomeSegment: zzfaulty's own grammar): no close"
        in message
    )
    assert (
        "zzfaulty sets its keywords in src/sqlfluff/dialects/dialect_zzfaulty.py."
        in message
    )


def test_checker_spots_a_keyword_written_as_a_segment() -> None:
    """Test that Ref("COLUMN") is read as a keyword, not a missing segment.

    The advice must not be to define a COLUMN segment.
    """
    dialect = _faulty_dialect("zzfaulty")
    known = {"SELECT": {("SomeSegment", "dialect_zzfaulty")}}
    unknown = {"ZZNOWORD": {("SomeSegment", "dialect_zzfaulty")}}

    known_message = _missing_segments_message(dialect, known)
    unknown_message = _missing_segments_message(dialect, unknown)

    assert (
        'SELECT is a zzfaulty keyword, so this is probably meant to be Ref.keyword("SELECT")'
        in known_message
    )
    assert "define SELECT" not in known_message
    assert (
        'this looks like a keyword written as a segment: Ref.keyword("ZZNOWORD")'
        in unknown_message
    )
    assert "ZZNOWORD then needs a status in zzfaulty." in unknown_message
    assert "define ZZNOWORD" not in unknown_message


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
    _declare(dialect, unimplemented=["ZZOWNWORD"])
    expanded = dialect.expand()

    found = _unimplemented_in_own_grammar(expanded)
    message = _unimplemented_in_own_grammar_message(expanded, found)

    assert found == {"ZZOWNWORD": {("_OwnGrammarSegment", "dialect_zzown")}}
    assert "- ZZOWNWORD: in _OwnGrammarSegment" in message

    inherited = _faulty_dialect("zzinherits")
    assert "OPTIMIZER_COSTS" in inherited.sets("unimplemented_keywords")
    assert not _unimplemented_in_own_grammar(inherited)


def _ansi_select_modifier_grammar() -> Matchable:
    """Ansi's SelectClauseModifierSegment grammar, for segments that reuse it."""
    segment = load_raw_dialect("ansi")._library["SelectClauseModifierSegment"]
    assert isinstance(segment, type) and issubclass(segment, BaseSegment)
    return cast(type[BaseSegment], segment).match_grammar


class _WrappingSegment(BaseSegment):
    """A zzwrap segment that wraps ansi grammar and adds its own ZZOWNWORD."""

    type = "select_clause_modifier"
    match_grammar = Sequence(_ansi_select_modifier_grammar(), Ref.keyword("ZZOWNWORD"))


_WrappingSegment.__module__ = "sqlfluff.dialects.dialect_zzwrap"


class _CopyingSegment(BaseSegment):
    """A zzcopy segment that copies ansi's grammar and inserts ZZOWNWORD."""

    type = "select_clause_modifier"
    match_grammar = _ansi_select_modifier_grammar().copy(
        insert=[Ref.keyword("ZZOWNWORD")]
    )


_CopyingSegment.__module__ = "sqlfluff.dialects.dialect_zzcopy"


def test_checker_counts_copied_parent_grammar_as_inherited() -> None:
    """Test that keywords in a .copy() of the parent's grammar are inherited."""
    dialect = load_raw_dialect("ansi").copy_as("zzcopy")
    dialect.replace(SelectClauseModifierSegment=_CopyingSegment)
    _declare(dialect, unimplemented=["DISTINCT", "ZZOWNWORD"])

    found = _unimplemented_in_own_grammar(dialect.expand())

    assert set(found) == {"ZZOWNWORD"}


def test_checker_counts_wrapped_parent_grammar_as_inherited() -> None:
    """Test that parent grammar inside a dialect's own segment is inherited.

    ansi's SelectClauseModifierSegment uses DISTINCT; marking it unimplemented
    switches off inherited grammar, which is allowed. ZZOWNWORD is the
    dialect's own, so marking it unimplemented is not.
    """
    dialect = load_raw_dialect("ansi").copy_as("zzwrap")
    dialect.replace(SelectClauseModifierSegment=_WrappingSegment)
    _declare(dialect, unimplemented=["DISTINCT", "ZZOWNWORD"])

    found = _unimplemented_in_own_grammar(dialect.expand())

    assert set(found) == {"ZZOWNWORD"}


def test_checker_reads_direct_references_only() -> None:
    """Test that the direct walk names each Ref once and stops at segments."""
    shared = Ref.keyword("ZZSHARED")
    grammar = Sequence(shared, Sequence(shared), _FutureSegment)

    assert _direct_references(grammar) == {"ZzsharedKeywordSegment"}
    assert _parent_uses(load_raw_dialect("ansi"), "ZzNoSuchSegment") == set()


def test_checker_says_a_symbol_or_number_is_not_a_keyword() -> None:
    """Test the hint for a bare string in grammar that isn't a word."""
    dialect = load_raw_dialect("ansi").copy_as(
        "zzsymbol", keyword_reference_error_docs="See the zz manual."
    )
    owners = {("SomeSegment", "dialect_zzsymbol")}
    keywords = {"=": owners, "1": owners, "->": owners}

    message = _missing_keywords_message(dialect.expand(), keywords)

    assert """'=' isn't a word""" in message
    assert 'probably means Ref("EqualsSegment")' in message
    assert "'1' isn't a word" in message and "numeric literal segment" in message
    assert "'->' isn't a word" in message and "a symbol or literal segment" in message
    assert "How to look up a zzsymbol keyword: See the zz manual." in message


def test_checker_finds_keyword_list_entries_that_are_not_words() -> None:
    """Test that punctuation in keyword lists is reported, and phrases aren't."""
    ansi = load_raw_dialect("ansi")
    # A non-word in ansi's own set, so the message has to trace it back there.
    ansi.sets("unreserved_keywords").add("ZZ,")
    try:
        dialect = ansi.copy_as("zzlists")
        _declare(
            dialect,
            reserved=["=", "WITHIN GROUP"],
            unreserved=["Arrow", "ZZ-PHRASE"],
        )
        found = _non_word_keywords(dialect)
        message = _non_word_keywords_message(dialect, found)
    finally:
        ansi.sets("unreserved_keywords").discard("ZZ,")

    assert set(found) == {"=", "ZZ,"}
    flat = _flat(message)
    assert "'=' (reserved, in zzlists's own lists)" in flat
    assert "delete it from zzlists's reserved list" in flat
    assert "'ZZ,' (unreserved, inherited from ansi)" in flat
    assert "delete it from ansi's unreserved list" in flat


class _FutureSegment(BaseSegment):
    """A segment whose grammar uses the future reserved word ZZFUTURE."""

    type = "select_clause_modifier"
    match_grammar = Sequence(Ref.keyword("ZZFUTURE"))


def _future_dialect(name: str, also_unreserved: bool) -> Dialect:
    """An ansi copy whose grammar uses ZZFUTURE, tagged future reserved."""
    dialect = load_raw_dialect("ansi").copy_as(name)
    dialect.replace(SelectClauseModifierSegment=_FutureSegment)
    if also_unreserved:
        _declare(dialect, unreserved=["ZZFUTURE"], future_reserved=["ZZFUTURE"])
    else:
        _declare(dialect, future_reserved=["ZZFUTURE"])
    return dialect.expand()


def test_checker_finds_a_grammar_keyword_that_is_only_future_reserved() -> None:
    """Test that future reserved alone isn't enough for a grammar keyword."""
    only_future = _future_dialect("zzfuture", also_unreserved=False)
    with_status = _future_dialect("zzfuture", also_unreserved=True)

    found = _future_only_uses(only_future)
    message = _future_only_message(only_future, found)

    assert set(found) == {"ZZFUTURE"}
    assert "- ZZFUTURE: in _FutureSegment" in message
    assert "usually unreserved, keeping the future tag" in _flat(message)
    assert not _future_only_uses(with_status)
    finding_titles = [f.title for f in _audit_findings("zzfuture", only_future)]
    assert "Grammar keywords only future reserved" in finding_titles


class _SharedUnmatchableSegment(BaseSegment):
    """A segment from another module whose grammar uses WITHIN GROUP."""

    type = "zz_shared_unmatchable"
    match_grammar = Sequence(Ref.keyword("WITHIN GROUP"))


class _UnmatchableSegment(BaseSegment):
    """A dialect's own segment whose grammar uses END-EXEC as a keyword."""

    type = "select_clause_modifier"
    match_grammar = Sequence(
        Ref.keyword("END-EXEC"),
        Ref("ZzSharedUnmatchableSegment"),
        Ref.keyword("ZZ-NO-STATUS"),
    )


_UnmatchableSegment.__module__ = "sqlfluff.dialects.dialect_zzunmatchable"


def test_checker_finds_grammar_keywords_that_can_never_match() -> None:
    """Test that a keyword the lexer splits is reported, with the split.

    END-EXEC has a status (ansi lists it), so it resolves and silently never
    matches. ZZ-NO-STATUS has none, so the missing keyword check owns it and
    names it as several tokens instead.
    """
    dialect = load_raw_dialect("ansi").copy_as("zzunmatchable")
    dialect.replace(SelectClauseModifierSegment=_UnmatchableSegment)
    dialect.add(ZzSharedUnmatchableSegment=_SharedUnmatchableSegment)
    _declare(dialect, unreserved=["WITHIN GROUP"])
    expanded = dialect.expand()

    found = _unmatchable_keywords(expanded)
    message = _flat(_unmatchable_keywords_message(expanded, found))

    assert set(found) == {"END-EXEC", "WITHIN GROUP"}
    assert "'END-EXEC' (in _UnmatchableSegment: zzunmatchable's own grammar)" in message
    assert "the lexer makes END, -, EXEC of it." in message
    assert (
        "'WITHIN GROUP' (in _SharedUnmatchableSegment: defined in "
        "keyword_reference_test): the lexer makes WITHIN, GROUP of it."
    ) in message
    assert "is several tokens to the lexer" in _not_a_word("ZZ-NO-STATUS")

    dialects = {"zzunmatchable": expanded}
    UNAUDITED_DIALECTS.update(dialects)
    try:
        report = _audit_report_of(dialects).text
    finally:
        UNAUDITED_DIALECTS.difference_update(dialects)
    assert "-- Grammar keywords that can never match (2) [warning] --" in report


def _keywords_used(dialect: Dialect) -> set[str]:
    """The words the dialect's grammar refers to as keywords."""
    return {
        name[: -len("KeywordSegment")].upper()
        for name in _reference_uses(dialect)
        if name.endswith("KeywordSegment")
    }


def _wrapped(words: list[str], indent: str = "    ", width: int = 88) -> list[str]:
    """Words as indented lines of at most width characters."""
    lines: list[str] = []
    line = indent
    for word in words:
        if len(line) + len(word) + 1 > width and line.strip():
            lines.append(line.rstrip())
            line = indent
        line += word + " "
    if line.strip():
        lines.append(line.rstrip())
    return lines


def _word_rows(words: list[str]) -> list[str]:
    """Words as rows under a message item.

    The report indents rows by six, two more than the message's four, so they
    are wrapped two characters short to stay within the report width.
    """
    return _wrapped(words, indent="    ", width=REPORT_WIDTH - 2)


def _unused_finding(name: str, dialect: Dialect) -> "Finding | None":
    """The dialect's unreserved keywords no grammar it can reach uses.

    Used means referred to as a keyword. An entry is a lead, not a verdict:
    it may be syntax sqlfluff doesn't parse yet, a word that can go, or a
    function name the function-name parser matches, like ABS.
    """
    unreserved = dialect.sets("unreserved_keywords")
    unused = sorted(unreserved - _keywords_used(dialect))
    if not unused:
        return None
    inherited: set[str] = set()
    parent_name = dialect.inherits_from
    if parent_name:
        inherited = _known_keywords(load_raw_dialect(parent_name))
    from_parent = [word for word in unused if word in inherited]
    own = [word for word in unused if word not in inherited]
    lines = [
        "These do no harm: nothing refers to them, so they can't change any "
        "parse. RF04 (off by default) treats them as keywords. This is an "
        "inventory: syntax sqlfluff may not parse yet, or words that can come "
        "out of a list."
    ]
    if from_parent:
        lines.append(f"- {len(from_parent)} also in {parent_name}'s keywords:")
        lines.extend(_word_rows(from_parent))
    if own:
        lines.append(f"- {len(own)} only in {name}'s keywords:")
        lines.extend(_word_rows(own))
    return Finding(
        "Keywords no grammar uses",
        "info",
        len(unused),
        "\n".join(lines),
        f"{len(unused)} of {len(unreserved)} unreserved",
    )


def _never_used_finding(dialects: dict[str, Dialect]) -> "Finding | None":
    """Listed keywords that no grammar in any of these dialects uses."""
    used: set[str] = set()
    listed: set[str] = set()
    for dialect in dialects.values():
        used |= _keywords_used(dialect)
        for label in ("reserved_keywords", "unreserved_keywords"):
            listed |= dialect.sets(label)
    never = sorted(listed - used)
    if not never:
        return None
    message = "\n".join(
        [
            "Reserved or unreserved in at least one of these dialects, and used "
            "by the grammar of none of them.",
            "- the words:",
            *_word_rows(never),
        ]
    )
    return Finding(
        "Keywords no grammar in these dialects uses", "info", len(never), message
    )


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


def _audit_report(
    dialect_names: list[str],
    level: str = "warning",
    named: frozenset[str] = frozenset(),
) -> "AuditReport":
    """What the checks in this file find in each of these dialects.

    For an audited dialect, errors and warnings are the failures pytest would
    show. For one in UNAUDITED_DIALECTS, they are the problems to fix before
    auditing it.
    """
    return _audit_report_of(
        {name: _report_dialect(name) for name in dialect_names}, level, named
    )


@functools.lru_cache(maxsize=None)
def _report_dialect(name: str) -> Dialect:
    """A real dialect for the report, expanded once and shared.

    Expanding a dialect makes a new object, so without this every report would
    walk every dialect again. The report never changes a dialect it reads.
    """
    return dialect_selector(name)


def _switched_off(dialect: Dialect) -> dict[str, set[Owner]]:
    """Unimplemented words that grammar the dialect can reach uses."""
    uses = _reference_uses(dialect)
    found: dict[str, set[Owner]] = {}
    for word in dialect.sets("unimplemented_keywords"):
        owners = uses.get(word.capitalize() + "KeywordSegment")
        if owners:
            found[word] = owners
    return found


def _settled_unimplemented(dialect: Dialect) -> list[str]:
    """Unimplemented words that no grammar the dialect can reach uses.

    The end state for a word the server lacks: researched, and the grammar
    that needed it overridden or never inherited.
    """
    return sorted(
        set(dialect.sets("unimplemented_keywords")) - set(_switched_off(dialect))
    )


def _settled_unimplemented_message(name: str, words: list[str]) -> str:
    """List unimplemented words that no longer hide any grammar."""
    return "\n".join(
        [
            f"Tagged unimplemented in {name}, and no grammar {name} reaches uses "
            "them: grammar that needed them is overridden, or was never "
            "inherited. This is where a word the server lacks should end up.",
            "- the words:",
            *_word_rows(words),
        ]
    )


REPORT_WIDTH = 88


def _heading(text: str, rule: str) -> list[str]:
    """A heading line padded with a rule to the report width."""
    return [f"{rule}{rule} {text} ".ljust(REPORT_WIDTH, rule)]


def _paragraph(text: str, indent: str) -> list[str]:
    """Text wrapped to the report width, keeping words (and pasted calls) whole."""
    return textwrap.wrap(
        text,
        width=REPORT_WIDTH,
        initial_indent=indent,
        subsequent_indent=indent,
        break_long_words=False,
        break_on_hyphens=False,
    )


def _render_message(message: str) -> list[str]:
    """A check's message laid out for reading: paragraphs, then one item each.

    The messages are written for pytest: an introduction, items starting "- "
    (a word or reference and its advice), rows indented by four spaces (a
    list under an item), lines indented by two (more advice for the item),
    and closing notes. Here each item gets its own block, separated by blank
    lines, wrapped with hanging indents.
    """
    lines: list[str] = []
    for line in message.splitlines():
        if line.startswith("    "):
            lines.append("      " + line.strip())
        elif line.startswith("  "):
            lines.extend(_paragraph(line.strip(), "      "))
        elif line.startswith("- "):
            item = line[2:]
            if item.endswith(":"):
                head, rest = item, ""
            elif "): " in item:
                head, _, rest = item.partition("): ")
                head += "):"
            else:
                head, _, rest = item.partition(": ")
                head += ":"
            lines.append("")
            lines.extend(
                textwrap.wrap(
                    f"* {head}",
                    width=REPORT_WIDTH,
                    initial_indent="  ",
                    subsequent_indent="    ",
                    break_long_words=False,
                    break_on_hyphens=False,
                )
            )
            if rest:
                lines.extend(_paragraph(rest, "      "))
        else:
            lines.append("")
            lines.extend(_paragraph(line, "  "))
    return lines


LEVELS = ("error", "warning", "notice", "info")

# How the footer names each level's hidden findings.
_LEVEL_PLURALS = {
    "error": "Errors",
    "warning": "Warnings",
    "notice": "Notices",
    "info": "Info",
}


class Finding(NamedTuple):
    """One kind of problem, or lead, found in a dialect.

    error: a statement reaching the grammar crashes. warning: the audit fails
    on it, but nothing crashes. notice: a lead worth a person's look, not a
    problem. info: an inventory of facts about the dialect.
    """

    title: str
    level: str
    number: int
    message: str
    number_text: str = ""


def _switched_off_message(name: str, switched_off: dict[str, set[Owner]]) -> str:
    """List inherited grammar that stops matching because of unimplemented words."""
    lines = [
        f"These words are tagged unimplemented in {name}: its server doesn't "
        "implement them, so the parts of inherited grammar that need them stop "
        "matching. Check that these are features the server really lacks. A "
        "large group can be right when the server lacks a whole feature, such "
        "as stored procedures. Words that don't share a reason are the "
        "suspicious ones; they often mean a keyword list was copied or "
        "replaced wholesale, not checked word by word. Step 4 of the guide "
        "at the top of test/dialects/keyword_reference_test.py says what to "
        "do with each."
    ]
    for word, owners in sorted(switched_off.items()):
        users, _ = _segments_and_files(owners)
        lines.append(f"- {word}: {users}")
    return "\n".join(lines)


def _audit_findings(name: str, dialect: Dialect) -> list[Finding]:
    """Everything found in a dialect, most severe first."""
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
    future_only = _future_only_uses(dialect)
    own_unimplemented = _unimplemented_in_own_grammar(dialect)
    switched_off = _switched_off(dialect)
    findings: list[Finding] = []
    if keywords:
        findings.append(
            Finding(
                "Missing keywords",
                "error",
                len(keywords),
                _missing_keywords_message(dialect, keywords),
            )
        )
    if segments:
        findings.append(
            Finding(
                "Missing segments",
                "error",
                len(segments),
                _missing_segments_message(dialect, segments),
            )
        )
    if own_unimplemented:
        findings.append(
            Finding(
                "Unimplemented words in own grammar",
                "warning",
                len(own_unimplemented),
                _unimplemented_in_own_grammar_message(dialect, own_unimplemented),
            )
        )
    unmatchable = _unmatchable_keywords(dialect)
    if unmatchable:
        findings.append(
            Finding(
                "Grammar keywords that can never match",
                "warning",
                len(unmatchable),
                _unmatchable_keywords_message(dialect, unmatchable),
            )
        )
    non_words = _non_word_keywords(dialect)
    if non_words:
        findings.append(
            Finding(
                "Keyword list entries that aren't words",
                "warning",
                len(non_words),
                _non_word_keywords_message(dialect, non_words),
            )
        )
    if overlaps:
        findings.append(
            Finding(
                "Two statuses",
                "warning",
                len(overlaps),
                _overlaps_message(dialect, overlaps),
            )
        )
    if future_only:
        findings.append(
            Finding(
                "Grammar keywords only future reserved",
                "warning",
                len(future_only),
                _future_only_message(dialect, future_only),
            )
        )
    if switched_off:
        findings.append(
            Finding(
                "Inherited grammar that stops matching",
                "notice",
                len(switched_off),
                _switched_off_message(name, switched_off),
            )
        )
    settled = _settled_unimplemented(dialect)
    if settled:
        findings.append(
            Finding(
                "Unimplemented keywords no grammar uses",
                "info",
                len(settled),
                _settled_unimplemented_message(name, settled),
            )
        )
    unused = _unused_finding(name, dialect)
    if unused:
        findings.append(unused)
    return findings


def _level_counts(findings: list[Finding]) -> dict[str, int]:
    """How many findings of each level, by number of items."""
    counts = dict.fromkeys(LEVELS, 0)
    for finding in findings:
        counts[finding.level] += finding.number
    return counts


def _level_count(count: int, level: str) -> str:
    """A count of findings at a level: '2 notices', '631 info'."""
    if level == "info":
        return f"{count} info"
    return _plural(count, level)


def _plural(count: int, word: str) -> str:
    """A count and a word, plural unless the count is one."""
    return f"{count} {word}" if count == 1 else f"{count} {word}s"


class AuditReport(NamedTuple):
    """The report's text, and whether an audited dialect failed."""

    text: str
    failed: bool


def _problem_counts(found: list[Finding]) -> str:
    """'5 errors, 39 warnings', leaving out notices, info and zero counts."""
    counts = _level_counts(found)
    return ", ".join(
        _plural(counts[lvl], lvl) for lvl in ("error", "warning") if counts[lvl]
    )


def _verdict(
    findings: dict[str, list[Finding]], named: set[str]
) -> tuple[list[str], bool]:
    """The pass or fail lines for the report, and whether it failed.

    Named dialects are what was asked about, so they decide, whether or not
    they are required to pass this audit yet. With none named, the dialects
    required to pass decide; the rest would fail it forever, so they are
    counted on a line of their own.
    """

    def has_problems(name: str) -> bool:
        return any(finding.level in ("error", "warning") for finding in findings[name])

    if named:
        judged = [name for name in findings if name in named]
        what = "named dialects"
    else:
        judged = [name for name in findings if name not in UNAUDITED_DIALECTS]
        what = "dialects required to pass this audit"
    failing = [name for name in judged if has_problems(name)]
    if not judged:
        lines = ["*** NO VERDICT *** no dialect in this run is required to pass."]
    elif failing:
        detail = ", ".join(
            f"{name} ({_problem_counts(findings[name])})" for name in failing
        )
        if len(judged) == 1:
            lines = [f"*** FAIL *** {detail}."]
        else:
            lines = [
                f"*** FAIL *** {len(failing)} of {len(judged)} {what} "
                f"{'has' if len(failing) == 1 else 'have'} errors or warnings: "
                f"{detail}."
            ]
    elif len(judged) == 1:
        lines = [f"*** PASS *** {judged[0]} has no errors or warnings."]
    else:
        lines = [f"*** PASS *** the {len(judged)} {what} have no errors or warnings."]
    not_required = [name for name in judged if name in UNAUDITED_DIALECTS]
    for name in not_required:
        if has_problems(name):
            lines.append(
                f"{name} isn't required to pass this audit yet (it's in "
                "UNAUDITED_DIALECTS), so its tests don't fail on these."
            )
    others = [
        f"{name} {_problem_counts(findings[name])}"
        for name in findings
        if name not in judged and has_problems(name)
    ]
    if others:
        label = (
            "Also shown, not part of the verdict"
            if named
            else "Not required to pass this audit yet"
        )
        lines.append(f"{label}:")
        lines.extend(f"  {other}" for other in others)
    return lines, bool(failing)


def _audit_report_of(
    dialects: dict[str, Dialect],
    level: str = "warning",
    named: frozenset[str] = frozenset(),
) -> AuditReport:
    """The audit report for these dialects, by name, down to a level.

    named are the dialects asked about, which decide the verdict; with none,
    the dialects required to pass this audit decide. Findings below the level
    are counted in a footer, never silently dropped.
    """
    shown_levels = LEVELS[: LEVELS.index(level) + 1]
    findings = {name: _audit_findings(name, d) for name, d in dialects.items()}
    never = _never_used_finding(dialects)
    verdict_lines, failed = _verdict(findings, set(named))
    verdict = [
        wrapped
        for line in verdict_lines
        for wrapped in textwrap.wrap(line, REPORT_WIDTH, subsequent_indent="  ")
    ]
    lines = list(verdict)
    lines.append("")
    lines.extend(_heading("Keyword audit", "="))
    lines.extend(
        _paragraph(
            "What the checks in test/dialects/keyword_reference_test.py find in "
            "each dialect. Errors crash the parser; warnings fail the audit "
            "without crashing; notices are leads worth a look, not problems; info "
            "is an inventory. Passing means nothing crashes and no check fails; "
            "it doesn't mean a dialect's keyword lists match its server. For a "
            "dialect required to pass this audit, its tests fail on errors and "
            "warnings. How to set up a dialect's keywords, and reconcile them "
            "with its server as far as you want to go, is in the docstring at "
            "the top of test/dialects/keyword_reference_test.py.",
            "",
        )
    )
    lines.append("")
    width = max(len(name) for name in dialects)
    for name, found in findings.items():
        status = "not yet" if name in UNAUDITED_DIALECTS else "required"
        counts = _level_counts(found)
        passes = not counts["error"] and not counts["warning"]
        # Errors and warnings decide, so they are always shown, zeros too;
        # notices and info only when there are some.
        parts = [
            _level_count(counts[lvl], lvl)
            for lvl in LEVELS
            if lvl in ("error", "warning") or counts[lvl]
        ]
        lines.extend(
            textwrap.wrap(
                f"{name.ljust(width)}  {status:8}  {'PASS' if passes else 'FAIL'}  "
                f"{', '.join(parts)}",
                width=REPORT_WIDTH,
                initial_indent="  ",
                subsequent_indent=" " * (2 + width + 2 + 8 + 2 + 4 + 2),
                break_long_words=False,
            )
        )
    ready: list[str] = []
    hidden: dict[str, list[str]] = {}
    for name, found in findings.items():
        audited = name not in UNAUDITED_DIALECTS
        counts = _level_counts(found)
        lines.append("")
        lines.append("")
        requirement = "required to pass" if audited else "not required to pass yet"
        lines.extend(_heading(f"{name} ({requirement})", "="))
        if not counts["error"] and not counts["warning"]:
            lines.append("")
            if audited:
                lines.append("  No errors or warnings.")
            else:
                lines.extend(
                    _paragraph(
                        f'{name} passes every check. Lock it in: remove "{name}" '
                        "from UNAUDITED_DIALECTS in "
                        "test/dialects/keyword_reference_test.py. Its tests then "
                        "require it to pass this audit.",
                        "  ",
                    )
                )
                ready.append(name)
        for finding in found:
            if finding.level not in shown_levels:
                hidden.setdefault(finding.level, []).append(
                    f"{finding.number_text or finding.number} "
                    f"{finding.title.lower()} in {name}"
                )
                continue
            count = finding.number_text or str(finding.number)
            lines.append("")
            lines.extend(_heading(f"{finding.title} ({count}) [{finding.level}]", "-"))
            lines.extend(_render_message(finding.message))
        if "warning" not in shown_levels and counts["warning"]:
            lines.append("")
            lines.extend(
                _paragraph(
                    f"The audit would also fail on "
                    f"{_plural(counts['warning'], 'warning')} not shown here. Run "
                    "with --level warning to see them.",
                    "  ",
                )
            )
    if never:
        if never.level in shown_levels:
            lines.append("")
            lines.append("")
            lines.extend(
                _heading(f"{never.title} ({never.number}) [{never.level}]", "=")
            )
            lines.extend(_render_message(never.message))
        else:
            hidden.setdefault(never.level, []).append(
                f"{never.number} {never.title.lower()}"
            )
    if ready:
        lines.append("")
        lines.append("")
        lines.extend(
            _paragraph(
                f"Ready to audit: {', '.join(ready)}. Remove "
                f"{'it' if len(ready) == 1 else 'them'} from UNAUDITED_DIALECTS in "
                "test/dialects/keyword_reference_test.py.",
                "",
            )
        )
    if hidden:
        lines.append("")
        lines.append("")
    # Each line starts with what the hidden findings are, so a reader scanning
    # the footer doesn't take notices for warnings. A blank line separates the
    # levels.
    groups_written = 0
    for hidden_level in LEVELS:
        items = hidden.get(hidden_level)
        if items:
            if groups_written:
                lines.append("")
            groups_written += 1
            lines.append(
                f"{_LEVEL_PLURALS[hidden_level]} not shown ({len(items)}). Show them "
                f"with --level {hidden_level}:"
            )
            for item in items:
                lines.extend(_paragraph(item, "  "))
    lines.append("")
    lines.append("")
    lines.extend(verdict)
    return AuditReport("\n".join(lines), failed)


def _parse_args(argv: list[str]) -> tuple[list[str], str]:
    """The dialect names and the level from the command line.

    Usage: keyword_reference_test.py [--level error|warning|notice|info] [dialect ...]
    """
    level = "warning"
    names: list[str] = []
    args = iter(argv)
    for arg in args:
        if arg == "--level":
            level = next(args, "")
            if level not in LEVELS:
                raise SystemExit(f"--level takes one of: {', '.join(LEVELS)}.")
        elif arg.startswith("--level="):
            level = arg.split("=", 1)[1]
            if level not in LEVELS:
                raise SystemExit(f"--level takes one of: {', '.join(LEVELS)}.")
        else:
            names.append(arg)
    unknown = [name for name in names if name not in ALL_DIALECTS]
    if unknown:
        raise SystemExit(
            f"Unknown dialect(s): {', '.join(unknown)}. "
            f"Dialects: {', '.join(ALL_DIALECTS)}."
        )
    return names, level


def _flat(text: str) -> str:
    """Text with every run of whitespace as one space, to match across wraps."""
    return " ".join(text.split())


def test_audit_report_covers_audited_and_unaudited_dialects() -> None:
    """Test that the report answers for any dialect it is given."""
    dialects = {
        "zzclean": _ready_dialect("zzclean"),
        "zzfailing": _failing_dialect("zzfailing"),
    }
    with _unaudited("zzfailing"):
        report = _audit_report_of(dialects).text

    assert "== zzclean (required to pass) ==" in report
    assert "  No errors or warnings." in report
    assert "== zzfailing (not required to pass yet) ==" in report
    assert "ZZPLAIN (in _FaultySegment" in report
    assert "zzclean    required  PASS  0 errors, 0 warnings, " in report
    assert re.search(r"zzclean    required  PASS  [^\n]* \d+ info\b", report)
    assert re.search(r"zzfailing  not yet   FAIL  \d+ errors?, \d+ warnings?", report)


def test_audit_report_covers_ready_dialects_segments_and_overlaps() -> None:
    """Test the report's other parts on a ready and a broken dialect."""
    ready = load_raw_dialect("ansi").copy_as("zzready")
    # The two keywords ansi's GRANT grammar used without listing, so this
    # dialect is ready however ansi itself stands.
    ready.sets("unreserved_keywords").update(["FORMATS", "POLICIES"])
    broken = _faulty_dialect("zzbroken")
    broken.sets("unreserved_keywords").add("SELECT")
    # ZONE is used by inherited ansi grammar (AT TIME ZONE).
    broken.sets("unimplemented_keywords").add("ZONE")
    broken.sets("unreserved_keywords").add("ZZ,")
    dialects = {"zzready": ready.expand(), "zzbroken": broken}
    UNAUDITED_DIALECTS.update(dialects)
    try:
        report = _audit_report_of(dialects, level="notice").text
    finally:
        UNAUDITED_DIALECTS.difference_update(dialects)

    flat = _flat(report)

    assert 'zzready passes every check. Lock it in: remove "zzready"' in flat
    assert "Its tests then require it to pass this audit." in flat
    assert "Ready to audit: zzready." in flat
    assert "refers to segments or grammars that don't exist" in flat
    assert "two statuses that can't go together" in flat
    assert "-- Inherited grammar that stops matching (1) [notice] --" in report
    assert "* ZONE:" in report
    assert "-- Keyword list entries that aren't words (1) [warning] --" in report


def test_audit_report_shows_an_audited_dialect_its_pytest_failures() -> None:
    """Test that a broken audited dialect gets the messages pytest gives it."""
    broken = _faulty_dialect("zzauditedbroken")
    broken.sets("unreserved_keywords").add("SELECT")
    own = load_raw_dialect("ansi").copy_as("zzown")
    own.replace(SelectClauseModifierSegment=_OwnGrammarSegment)
    _declare(own, unimplemented=["ZZOWNWORD"])

    result = _audit_report_of({"zzauditedbroken": broken, "zzown": own.expand()})
    report = result.text
    flat = _flat(report)

    assert result.failed
    assert report.startswith(
        "*** FAIL *** 2 of 2 dialects required to pass this audit have errors"
    )

    assert "== zzauditedbroken (required to pass) ==" in report
    assert "These words have two statuses that can't go together in" in flat
    assert "== zzown (required to pass) ==" in report
    assert "* ZZOWNWORD:\n      in _OwnGrammarSegment" in report


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

    assert "- 1 that ansi lists, lost in zzdropped." in message
    assert f"    {word}  in " in message


def test_audit_report_lists_unused_keywords_as_info() -> None:
    """Test that unused keywords are an inventory, shown only at info level."""
    dialect = load_raw_dialect("ansi").copy_as("zzunused")
    dialect.sets("unreserved_keywords").update(["FORMATS", "POLICIES", "ZZNOGRAMMAR"])
    dialects = {"zzunused": dialect.expand()}
    shown = _audit_report_of(dialects, level="info").text
    hidden = _audit_report_of(dialects, level="notice").text

    assert "-- Keywords no grammar uses (" in shown
    assert "unreserved) [info] --" in shown
    assert "also in ansi's keywords:" in shown
    assert "only in zzunused's keywords:" in shown
    assert re.search(
        r"== Keywords no grammar in these dialects uses \(\d+\) \[info\]", shown
    )
    assert "These do no harm" in _flat(shown)
    assert "Keywords no grammar uses (" not in hidden
    assert re.search(
        r"\nInfo not shown \(\d+\)\. Show them with --level info:\n  \d", hidden
    )


def test_unused_findings_are_absent_when_everything_is_used() -> None:
    """Test that a dialect whose keywords are all used has no unused notice."""
    dialect = load_raw_dialect("ansi").copy_as("zzallused").expand()
    used = _keywords_used(dialect)
    dialect.sets("unreserved_keywords").intersection_update(used)

    assert _unused_finding("zzallused", dialect) is None
    assert _never_used_finding({}) is None


def test_audit_report_at_error_level_still_mentions_warnings() -> None:
    """Test that hiding warnings never makes a failing dialect look clean."""
    with _unaudited("zzfailing"):
        report = _audit_report_of(
            {"zzfailing": _failing_dialect("zzfailing")}, level="error"
        ).text
    flat = _flat(report)

    assert "[error]" in report
    assert "[warning]" not in report
    assert "The audit would also fail on" in flat
    assert "Warnings not shown (" in flat
    assert "Show them with --level warning:" in flat
    assert "Info not shown (" in flat
    # Each hidden level is its own block, a blank line before the next.
    assert re.search(r"\n  \d[^\n]*\n\nInfo not shown \(", report)


def test_audit_report_reads_real_dialects_by_name() -> None:
    """Test the by-name entry point the command line uses.

    Only the shape is checked, so no dialect has to be in any state for it.
    """
    report = _audit_report(["ansi"], level="info").text

    assert "== ansi (" in report
    assert re.search(r"\*\*\* (PASS|FAIL) \*\*\*", report)


def test_audit_verdict_judges_what_was_asked() -> None:
    """Test the verdict: named dialects decide; with none, the required ones."""
    clean = {"zzclean": _ready_dialect("zzclean")}
    failing = {"zzfailing": _failing_dialect("zzfailing")}
    with _unaudited("zzfailing"):
        one = _audit_report_of(clean, named=frozenset({"zzclean"}))
        named_failing = _audit_report_of(failing, named=frozenset({"zzfailing"}))
        everything = _audit_report_of(clean | failing)
        nothing = _audit_report_of(failing)

    assert not one.failed
    assert one.text.startswith("*** PASS *** zzclean has no errors or warnings.")
    assert one.text.rstrip().endswith("*** PASS *** zzclean has no errors or warnings.")
    assert named_failing.failed
    assert named_failing.text.startswith("*** FAIL *** zzfailing (")
    assert "zzfailing isn't required to pass this audit yet" in named_failing.text
    assert not everything.failed
    assert everything.text.startswith("*** PASS *** zzclean has no errors or warnings.")
    assert "Not required to pass this audit yet:\n  zzfailing " in everything.text
    assert nothing.text.startswith("*** NO VERDICT ***")


def test_audit_verdict_counts_several_named_dialects() -> None:
    """Test the wording when several named dialects pass or one fails."""
    clean = {"zzclean": _ready_dialect("zzclean"), "zztidy": _ready_dialect("zztidy")}
    failing = {"zzfailing": _failing_dialect("zzfailing")}
    with _unaudited("zzfailing"):
        passing = _audit_report_of(clean, named=frozenset(clean))
        mixed = _audit_report_of(
            {"zzclean": clean["zzclean"]} | failing,
            named=frozenset({"zzclean", "zzfailing"}),
        )
        with_children = _audit_report_of(
            {"zzclean": clean["zzclean"]} | failing, named=frozenset({"zzclean"})
        )

    assert passing.text.startswith("*** PASS *** the 2 named dialects have no")
    assert mixed.text.startswith("*** FAIL *** 1 of 2 named dialects has errors")
    assert "Also shown, not part of the verdict:\n  zzfailing " in with_children.text


def test_parse_args_reads_names_and_level() -> None:
    """Test the command line: dialect names, --level, and their errors."""
    assert _parse_args([]) == ([], "warning")
    assert _parse_args(["mysql", "--level", "notice"]) == (["mysql"], "notice")
    assert _parse_args(["--level=error", "tsql"]) == (["tsql"], "error")
    with pytest.raises(SystemExit, match="--level takes one of"):
        _parse_args(["--level", "loud"])
    with pytest.raises(SystemExit, match="--level takes one of"):
        _parse_args(["--level=loud"])
    with pytest.raises(SystemExit, match="Unknown dialect"):
        _parse_args(["tsq"])


# ANSI colours for the verdict markers, red for FAIL and green for PASS.
_VERDICT_COLOURS = {"*** FAIL ***": "\033[1;31m", "*** PASS ***": "\033[1;32m"}


def _coloured(text: str) -> str:
    """The report with its verdict markers coloured, for a terminal."""
    for marker, colour in _VERDICT_COLOURS.items():
        text = text.replace(marker, f"{colour}{marker}\033[0m")
    return text


def _use_colour(stream: object, environ: Mapping[str, str]) -> bool:
    """Whether to colour output: only on a terminal, and not under NO_COLOR."""
    isatty = getattr(stream, "isatty", None)
    return bool(isatty and isatty()) and "NO_COLOR" not in environ


def test_verdict_colour_only_on_a_terminal() -> None:
    """Test that colour is added on a terminal and nowhere else."""

    class _Terminal:
        def isatty(self) -> bool:
            return True

    assert _use_colour(_Terminal(), {})
    assert not _use_colour(_Terminal(), {"NO_COLOR": "1"})
    assert not _use_colour(object(), {})
    coloured = _coloured("*** FAIL *** x\n*** PASS *** y")
    assert "\033[1;31m*** FAIL ***\033[0m x" in coloured
    assert "\033[1;32m*** PASS ***\033[0m y" in coloured


if __name__ == "__main__":  # pragma: no cover
    # Piped into head or less, end quietly when the reader stops, like any
    # Unix tool, instead of Python's BrokenPipeError.
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    # With dialect names as arguments, report on those and their descendants.
    names, level = _parse_args(sys.argv[1:])
    chosen = _with_descendants(names) if names else ALL_DIALECTS
    report = _audit_report(chosen, level, frozenset(names))
    if _use_colour(sys.stdout, os.environ):
        print(_coloured(report.text))
    else:
        print(report.text)
    sys.exit(1 if report.failed else 0)
