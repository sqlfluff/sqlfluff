"""Defines the base dialect class."""

import sys
from collections.abc import Iterable
from itertools import combinations
from typing import Any, Optional, Union, cast

from sqlfluff.core.parser import (
    BaseSegment,
    KeywordSegment,
    SegmentGenerator,
    StringParser,
)
from sqlfluff.core.parser.client_commands import ClientCommandRules
from sqlfluff.core.parser.grammar.base import BaseGrammar, Nothing
from sqlfluff.core.parser.lexer import LexerType
from sqlfluff.core.parser.matchable import Matchable
from sqlfluff.core.parser.types import BracketPairTuple, DialectElementType

# The statuses a dialect can give a keyword. In a dialect that calls
# declare_keyword_sets(), each word has at most one; the dialect tests check this.
#
#   reserved      A keyword everywhere: never a bare name.
#   unreserved    A keyword in some positions, an ordinary name elsewhere.
#   future        Not reserved yet, but the vendor says it will be.
#   unimplemented Not a keyword on this dialect's server, though grammar the
#                 dialect inherits uses it as one.
#
# Reserved, unreserved and future words are matched as keywords, and lint
# rules treat them as keywords. Only reserved words are kept from being names.
#
# An unimplemented word records that inherited grammar using that literal
# word doesn't apply to this dialect: its server has no such keyword. Only
# the part of a rule that needs the word stops matching, which is the right
# behaviour, and it doesn't crash either; the rest of the rule still applies.
# The word is an ordinary name. Doris inherits MySQL's FLUSH grammar, but
# Doris has no OPTIMIZER_COSTS, so FLUSH OPTIMIZER_COSTS doesn't parse in
# Doris while FLUSH TABLES and FLUSH PRIVILEGES still do. "Not a keyword"
# isn't "missing": MariaDB has DENSE_RANK() as a function, but DENSE_RANK
# isn't a MariaDB keyword.
#
# A word that grammar needs but that has no status at all is a bug, usually a
# typo ("SELEECT"). Looking it up fails, and the dialect tests report it.
#
# Most unimplemented words come from declare_keyword_sets(): the parent's reserved
# words a dialect doesn't list move there. List one by hand for inherited
# grammar the dialect's server doesn't have.
#
# The checks are in test/dialects/keyword_reference_test.py. Run it directly,
# with dialect names as arguments, for a report on any dialect, including one
# that doesn't call declare_keyword_sets() yet.
KEYWORD_STATUS_SETS = (
    "reserved_keywords",
    "unreserved_keywords",
    "future_reserved_keywords",
    "unimplemented_keywords",
)

# How to choose a word's status, for error messages that ask someone to.
KEYWORD_STATUS_CHOICE = (
    "If the database reserves the word, it's reserved. If it's a keyword "
    "but can also be a name, it's unreserved. If the vendor says it will "
    "become reserved but it isn't yet, it's future reserved. If the "
    "database doesn't recognize it at all, but grammar inherited from a "
    "parent dialect uses it, it's unimplemented."
)


def _reference_audit_tip(dialect_name: str) -> str:
    """Point someone changing the dialect at the report of every such problem.

    Only someone working in a sqlfluff checkout has the test file, so the
    message says so.
    """
    return (
        "\n\nIf you are changing this dialect in a sqlfluff checkout, run "
        f"`python test/dialects/keyword_reference_test.py {dialect_name}`. "
        "It lists every keyword and segment that grammar refers to but a "
        f"dialect doesn't have, in {dialect_name} and in the dialects that "
        "inherit from it, and what to do about each."
    )


def _keyword_set(words: Iterable[str], argument: str) -> set[str]:
    """The upper-cased keywords in words, refusing a single string.

    A string is itself iterable, one character at a time, so passing a
    multi-line keyword string where words are expected would quietly declare
    every letter as a keyword.
    """
    if isinstance(words, str):
        raise TypeError(
            f"declare_keyword_sets() takes {argument} as a collection of words, "
            "not "
            "one string: for a multi-line keyword string, pass keywords.split()."
        )
    return {word.strip().upper() for word in words if word.strip()}


class Dialect:
    """Serves as the basis for runtime resolution of Grammar.

    Args:
        name (:obj:`str`): The name of the dialect, used for lookup.
        lexer_matchers (iterable of :obj:`StringLexer`): A structure defining
            the lexing config for this dialect.

    """

    def __init__(
        self,
        name: str,
        root_segment_name: str,
        lexer_matchers: Optional[list[LexerType]] = None,
        library: Optional[dict[str, DialectElementType]] = None,
        sets: Optional[dict[str, set[Union[str, BracketPairTuple]]]] = None,
        inherits_from: Optional[str] = None,
        formatted_name: Optional[str] = None,
        docstring: Optional[str] = None,
        client_commands: Optional[ClientCommandRules] = None,
    ) -> None:
        self._library = library or {}
        self.name = name
        self.lexer_matchers = lexer_matchers
        self.client_commands = client_commands
        self.expanded = False
        self._sets = sets or {}
        self.inherits_from = inherits_from
        self.root_segment_name = root_segment_name
        # Attributes for documentation
        self.formatted_name: str = formatted_name or name
        self.docstring = docstring or f"The dialect for {self.formatted_name}."
        # Set by declare_keyword_sets(). Not inherited: each dialect opts in to
        # the keyword status checks in the dialect tests itself.
        self.keyword_sets_declared = False

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Dialect: {self.name}>"

    def expand(self) -> "Dialect":
        """Expand any callable references to concrete ones.

        This must be called before using the dialect. But
        allows more flexible definitions to happen at runtime.

        NOTE: This method returns a copy of the current dialect
        so that we don't pollute the original dialect and get
        dependency issues.


        Returns:
            :obj:`Dialect`: a copy of the given dialect but
                with expanded references.
        """
        # Are we already expanded?
        if self.expanded:  # pragma: no cover
            raise ValueError("Attempted to re-expand an already expanded dialect.")

        expanded_copy = self.copy_as(name=self.name)
        expanded_copy.keyword_sets_declared = self.keyword_sets_declared
        # Expand any callable elements of the dialect.
        for key in expanded_copy._library:
            seg_gen = expanded_copy._library[key]
            if isinstance(seg_gen, SegmentGenerator):
                # If the element is callable, call it passing the current
                # dialect and store the result in its place.
                # Use the .replace() method for its error handling.
                expanded_copy.replace(**{key: seg_gen.expand(expanded_copy)})
        # Expand any keyword sets.
        for keyword_set in [
            "unreserved_keywords",
            "reserved_keywords",
            "future_reserved_keywords",
        ]:  # e.g. reserved_keywords, (JOIN, ...)
            # Make sure the values are available as KeywordSegments
            keyword_sets = expanded_copy.sets(keyword_set)
            for kw in keyword_sets:
                n = kw.capitalize() + "KeywordSegment"
                if n not in expanded_copy._library:
                    expanded_copy._library[n] = StringParser(kw.lower(), KeywordSegment)
        # An unimplemented keyword resolves, so that inherited grammar which
        # uses it doesn't crash, but to something that never matches.
        for kw in expanded_copy.sets("unimplemented_keywords"):
            n = kw.capitalize() + "KeywordSegment"
            if n not in expanded_copy._library:
                expanded_copy._library[n] = Nothing()
        expanded_copy.expanded = True
        return expanded_copy

    def sets(self, label: str) -> set[str]:
        """Allows access to sets belonging to this dialect.

        These sets belong to the dialect and are copied for sub
        dialects. These are used in combination with late-bound
        dialect objects to create some of the bulk-produced rules.

        """
        assert label not in (
            "bracket_pairs",
            "angle_bracket_pairs",
        ), f"Use `bracket_sets` to retrieve {label} set."

        if label not in self._sets:
            self._sets[label] = set()
        return cast(set[str], self._sets[label])

    def bracket_sets(self, label: str) -> set[BracketPairTuple]:
        """Allows access to bracket sets belonging to this dialect."""
        assert label in (
            "bracket_pairs",
            "angle_bracket_pairs",
        ), "Invalid bracket set. Consider using `sets` instead."

        if label not in self._sets:
            self._sets[label] = set()
        return cast(set[BracketPairTuple], self._sets[label])

    def update_keywords_set_from_multiline_string(
        self, set_label: str, values: str
    ) -> None:
        """Special function to update a keywords set from a multi-line string."""
        self.sets(set_label).update(
            [n.strip().upper() for n in values.strip().split("\n")]
        )

    def declare_keyword_sets(
        self,
        *,
        reserved: Iterable[str],
        unreserved: Iterable[str],
        future_reserved: Iterable[str],
        unimplemented: Iterable[str],
    ) -> None:
        """Declare this dialect's keyword sets, each a collection of words.

        Every set must be given, even if empty, so that an empty one is a
        decision rather than an omission. Each argument can be any
        collection of words (a set, a list, the result of str.split()); the
        words are upper-cased into new sets, so the caller's collections are
        never stored or changed.

        This replaces the reserved keywords and adds to the inherited
        unreserved, future reserved and unimplemented ones, keeping every
        word in exactly one status:

        - A word listed here leaves any status it inherited.
        - An inherited reserved word that isn't listed here moves into
          unimplemented_keywords, so inherited grammar that uses it stops
          matching instead of crashing.
        - unimplemented lists words this dialect's server is known not to
          recognize, for inherited grammar this dialect doesn't have.

        Listing a word under more than one status is an error.

        Calling this also opts the dialect in to the keyword and reference
        checks in test/dialects/keyword_reference_test.py. Run that file
        directly, ``python test/dialects/keyword_reference_test.py <dialect>``,
        to see what they find in a dialect before opting it in.

        Only call this once the dialect's keyword lists come from its own
        server or vendor documentation, and its maintainers want the checks.
        A dialect that is still borrowing its parent's keywords shouldn't
        call it: inherited reserved words it doesn't list would stop
        matching, which would switch off grammar it inherits. Without this
        call, a dialect keeps its parent's keywords as they are.
        """
        declared_sets = {
            "reserved_keywords": _keyword_set(reserved, "reserved"),
            "unreserved_keywords": _keyword_set(unreserved, "unreserved"),
            "future_reserved_keywords": _keyword_set(
                future_reserved, "future_reserved"
            ),
            "unimplemented_keywords": _keyword_set(unimplemented, "unimplemented"),
        }
        for first, second in combinations(KEYWORD_STATUS_SETS, 2):
            both = declared_sets[first] & declared_sets[second]
            if both:
                raise ValueError(
                    f"The {self.name} dialect declares these keywords as both "
                    f"{first} and {second}: {sorted(both)}. A word can have "
                    "only one status: remove each from all but one of the "
                    "lists passed to declare_keyword_sets(), usually in "
                    f"dialect_{self.name}_keywords.py. {KEYWORD_STATUS_CHOICE}"
                )

        declared: set[str] = set()
        for words in declared_sets.values():
            declared.update(words)
        inherited_reserved = set(self.sets("reserved_keywords"))
        for label in KEYWORD_STATUS_SETS:
            self.sets(label).difference_update(declared)
        self.sets("reserved_keywords").clear()
        for label, words in declared_sets.items():
            self.sets(label).update(words)

        still_known: set[str] = set()
        for label in KEYWORD_STATUS_SETS:
            still_known.update(self.sets(label))
        self.sets("unimplemented_keywords").update(inherited_reserved - still_known)
        self.keyword_sets_declared = True

    def copy_as(
        self,
        name: str,
        formatted_name: Optional[str] = None,
        docstring: Optional[str] = None,
    ) -> "Dialect":
        """Copy this dialect and create a new one with a different name.

        This is the primary method for inheritance, after which, the
        `replace` method can be used to override particular rules.
        """
        # Are we already expanded?
        if self.expanded:  # pragma: no cover
            # If we copy an already expanded dialect then any SegmentGenerators
            # won't respond. This is most likely a mistake.
            raise ValueError("Attempted to copy an already expanded dialect.")

        # Copy sets if they are passed, so they can be mutated independently
        new_sets = {}
        for label in self._sets:
            new_sets[label] = self._sets[label].copy()

        assert self.lexer_matchers

        return self.__class__(
            name=name,
            library=self._library.copy(),
            lexer_matchers=self.lexer_matchers.copy(),
            client_commands=self.client_commands,
            sets=new_sets,
            inherits_from=self.name,
            root_segment_name=self.root_segment_name,
            # NOTE: We don't inherit the documentation fields.
            formatted_name=formatted_name,
            docstring=docstring,
        )

    def add(self, **kwargs: DialectElementType) -> None:
        """Add a segment to the dialect directly.

        This is the alternative to the decorator route, most useful for segments
        defined using `make`. Segments are passed in as kwargs.

        e.g.
        dialect.add(SomeSegment=StringParser("blah", KeywordSegment))

        Note that multiple segments can be added in the same call as this method
        will iterate through the kwargs
        """
        for n in kwargs:
            if n in self._library:  # pragma: no cover
                raise ValueError(f"{n!r} is already registered in {self!r}")
            self._library[n] = kwargs[n]

    def replace(self, **kwargs: DialectElementType) -> None:
        """Override a segment on the dialect directly.

        Usage is very similar to add, but elements specified must already exist.
        """
        for n in kwargs:
            if n not in self._library:  # pragma: no cover
                raise ValueError(f"{n!r} is not already registered in {self!r}")
            replacement = kwargs[n]
            # If trying to replace with same, just skip.
            if self._library[n] is replacement:
                continue
            # Check for replacement with a new but identical class.
            # This would be a sign of redundant definitions in the dialect.
            elif self._library[n] == replacement:
                raise ValueError(
                    f"Attempted unnecessary identical redefinition of {n!r} in {self!r}"
                )  # pragma: no cover

            # To replace a segment, the replacement must either be a
            # subclass of the original, *or* it must have the same
            # public methods and/or fields as it.
            # NOTE: Other replacements aren't validated.
            subclass = False
            if isinstance(self._library[n], type) and not isinstance(
                # NOTE: The exception here is we _are_ allowed to replace a
                # segment with a `Nothing()` grammar, which shows that a segment
                # has been disabled.
                replacement,
                Nothing,
            ):
                assert isinstance(replacement, type), (
                    f"Cannot replace {n!r} with {replacement}"
                )
                old_seg = cast(type["BaseSegment"], self._library[n])
                new_seg = cast(type["BaseSegment"], replacement)
                assert issubclass(old_seg, BaseSegment)
                assert issubclass(new_seg, BaseSegment)
                subclass = issubclass(new_seg, old_seg)
                if not subclass:
                    if old_seg.type != new_seg.type:
                        raise ValueError(  # pragma: no cover
                            f"Cannot replace {n!r} because 'type' property does not "
                            f"match: {new_seg.type} != {old_seg.type}"
                        )
                    base_dir = set(dir(self._library[n]))
                    cls_dir = set(dir(new_seg))
                    missing = {
                        n for n in base_dir.difference(cls_dir) if not n.startswith("_")
                    }
                    if missing:
                        raise ValueError(  # pragma: no cover
                            f"Cannot replace {n!r} because it's not a subclass and "
                            f"is missing these from base: {', '.join(missing)}"
                        )

            self._library[n] = replacement

    def add_update_segments(self, module_dct: dict[str, Any]) -> None:
        """Scans module dictionary, adding or replacing segment definitions."""
        for k, v in module_dct.items():
            if isinstance(v, type) and issubclass(v, BaseSegment):
                if k not in self._library:
                    self.add(**{k: v})
                else:
                    non_seg_v = cast(Union[Matchable, SegmentGenerator], v)
                    self.replace(**{k: non_seg_v})

    def get_grammar(self, name: str) -> BaseGrammar:
        """Allow access to grammars pre-expansion.

        This is typically for dialect inheritance. This method
        also validates that the result is a grammar.
        """
        if name not in self._library:  # pragma: no cover
            raise ValueError(f"Element {name} not found in dialect.")
        grammar = self._library[name]
        if not isinstance(grammar, BaseGrammar):  # pragma: no cover
            raise TypeError(
                f"Attempted to fetch non grammar [{name}] with get_grammar."
            )
        return grammar

    def get_segment(self, name: str) -> type["BaseSegment"]:
        """Allow access to segments pre-expansion.

        This is typically for dialect inheritance. This method
        also validates that the result is a segment.
        """
        if name not in self._library:  # pragma: no cover
            raise ValueError(f"Element {name} not found in dialect.")
        segment = cast(type["BaseSegment"], self._library[name])

        if issubclass(segment, BaseSegment):
            return segment
        else:  # pragma: no cover
            raise TypeError(
                f"Attempted to fetch non segment [{name}] "
                f"with get_segment - type{type(segment)}"
            )

    def ref(self, name: str) -> Matchable:
        """Return an object which acts as a late binding reference to the element named.

        NB: This requires the dialect to be expanded, and only returns Matchables
        as a result.

        """
        if not self.expanded:  # pragma: no cover
            raise RuntimeError("Dialect must be expanded before use.")

        if name in self._library:
            res = self._library[name]
            if res:
                assert not isinstance(res, SegmentGenerator)
                return res
            else:  # pragma: no cover
                raise ValueError(
                    "Unexpected Null response while fetching {!r} from {}".format(
                        name, self.name
                    )
                )
        elif name.endswith("KeywordSegment"):  # pragma: no cover
            keyword = name[0:-14]
            keyword_tip = (
                "\n\nThe syntax in the query is not (yet?) supported. Try to"
                " narrow down your query to a minimal, reproducible case and"
                " raise an issue on GitHub.\n\n"
                "Or, even better, see this guide on how to help contribute"
                " keyword and/or dialect updates:\n"
                "https://docs.sqlfluff.com/en/stable/perma/contribute_dialect_keywords.html"
                f"{_reference_audit_tip(self.name)}"
            )
            # Keyword errors are common so avoid printing the whole, scary,
            # traceback as not that useful and confusing to people.
            sys.tracebacklimit = 0
            raise RuntimeError(
                "Grammar refers to the "
                "{!r} keyword which was not found in the {} dialect.{}".format(
                    keyword.upper(), self.name, keyword_tip
                )
            )
        else:  # pragma: no cover
            raise RuntimeError(
                "Grammar refers to {!r} which was not found in the {} dialect.{}".format(
                    name, self.name, _reference_audit_tip(self.name)
                )
            )

    def set_lexer_matchers(self, lexer_matchers: list[LexerType]) -> None:
        """Set the lexer struct for the dialect.

        This is what is used for base dialects. For derived dialects
        (which don't exist yet) the assumption is that we'll introduce
        some kind of *patch* function which could be used to mutate
        an existing `lexer_matchers`.
        """
        self.lexer_matchers = lexer_matchers

    def get_lexer_matchers(self) -> list[LexerType]:
        """Fetch the lexer struct for this dialect."""
        if self.lexer_matchers:
            return self.lexer_matchers
        else:  # pragma: no cover
            raise ValueError(f"Lexing struct has not been set for dialect {self}")

    def patch_lexer_matchers(self, lexer_patch: list[LexerType]) -> None:
        """Patch an existing lexer struct.

        Used to edit the lexer of a sub-dialect.
        """
        buff = []
        if not self.lexer_matchers:  # pragma: no cover
            raise ValueError("Lexer struct must be defined before it can be patched!")

        # Make a new data struct for lookups
        patch_dict = {elem.name: elem for elem in lexer_patch}

        for elem in self.lexer_matchers:
            if elem.name in patch_dict:
                buff.append(patch_dict[elem.name])
            else:
                buff.append(elem)
        # Overwrite with the buffer once we're done
        self.lexer_matchers = buff

    def insert_lexer_matchers(self, lexer_patch: list[LexerType], before: str) -> None:
        """Insert new records into an existing lexer struct.

        Used to edit the lexer of a sub-dialect. The patch is
        inserted *before* whichever element is named in `before`.
        """
        buff = []
        found = False
        if not self.lexer_matchers:  # pragma: no cover
            raise ValueError("Lexer struct must be defined before it can be patched!")

        for elem in self.lexer_matchers:
            if elem.name == before:
                found = True
                for patch in lexer_patch:
                    buff.append(patch)
                buff.append(elem)
            else:
                buff.append(elem)

        if not found:  # pragma: no cover
            raise ValueError(
                f"Lexer struct insert before '{before}' failed because tag never found."
            )
        # Overwrite with the buffer once we're done
        self.lexer_matchers = buff

    def get_root_segment(self) -> Union[type[BaseSegment], Matchable]:
        """Get the root segment of the dialect."""
        return self.ref(self.root_segment_name)
