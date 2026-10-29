"""Defines the base dialect class."""

import sys
from collections.abc import Sequence
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

# The sets that hold a dialect's keyword statuses. declare_keyword_sets()
# explains them, and test/dialects/keyword_reference_test.py checks them.
KEYWORD_STATUS_SETS = (
    "reserved_keywords",
    "unreserved_keywords",
    "unimplemented_keywords",
    "future_reserved_keywords",
)


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
        keyword_reference_error_docs: Optional[str] = None,
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
        # A message from this dialect's maintainers to a contributor who is
        # probably working on another dialect, usually a parent, and has hit a
        # keyword reference error here: how to look up a keyword in this
        # dialect. Printed as is in those errors. Not inherited.
        self.keyword_reference_error_docs = keyword_reference_error_docs

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

        # copy_as() makes a child dialect; the expanded copy is this dialect,
        # so it keeps this dialect's own identity, parent included.
        expanded_copy = self.copy_as(
            name=self.name,
            formatted_name=self.formatted_name,
            docstring=self.docstring,
            keyword_reference_error_docs=self.keyword_reference_error_docs,
        )
        expanded_copy.inherits_from = self.inherits_from
        # Expand any callable elements of the dialect.
        for key in expanded_copy._library:
            seg_gen = expanded_copy._library[key]
            if isinstance(seg_gen, SegmentGenerator):
                # If the element is callable, call it passing the current
                # dialect and store the result in its place.
                # Use the .replace() method for its error handling.
                expanded_copy.replace(**{key: seg_gen.expand(expanded_copy)})
        # Expand any keyword sets.
        unimplemented = expanded_copy.sets("unimplemented_keywords")
        for keyword_set in KEYWORD_STATUS_SETS:  # e.g. reserved_keywords, (JOIN, ...)
            if keyword_set == "unimplemented_keywords":
                # Handled below: these resolve to Nothing().
                continue
            # Make sure the values are available as KeywordSegments
            keyword_sets = expanded_copy.sets(keyword_set)
            for kw in keyword_sets:
                # A future reserved word can also be unimplemented (not a
                # keyword yet on this server); unimplemented decides the grammar.
                if kw in unimplemented:
                    continue
                n = kw.capitalize() + "KeywordSegment"
                if n not in expanded_copy._library:
                    expanded_copy._library[n] = StringParser(kw.lower(), KeywordSegment)
        # An unimplemented keyword resolves, so that inherited grammar which
        # uses it doesn't crash, but to something that never matches.
        for kw in unimplemented:
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

    @staticmethod
    def _keyword_words(words: Sequence[str], function: str, argument: str) -> set[str]:
        """The upper-cased keywords in a list of words."""
        if isinstance(words, str):
            # Refuse strings because they would be treated as a sequence of letters.
            raise TypeError(
                f"{function}() takes {argument} as a list of words, not a string. "
                'Pass one word as a list, e.g. ["LIBRARY"]; split a keyword file\'s '
                "multi-line string with .split() in that file."
            )
        return {word.upper() for word in words}

    @staticmethod
    def _refuse_overlapping_keyword_lists(listed: dict[str, set[str]]) -> None:
        """Refuse a call that lists a word under two lists that exclude each other.

        Only the call's own lists are checked. Inherited sets are resolved, not
        refused, because a child can't fix its parent's lists.
        """
        # Pairs of lists that can't share a word. A keyword is reserved or
        # unreserved, not both; an unimplemented word is one the server
        # doesn't have, so it is neither; a word the vendor will reserve isn't
        # reserved yet. Future reserved may go with unreserved or unimplemented.
        exclusive_lists = (
            ("reserved", "unreserved"),
            ("reserved", "unimplemented"),
            ("unreserved", "unimplemented"),
            ("reserved", "future_reserved"),
        )
        clashes = []
        for first, second in exclusive_lists:
            for word in sorted(listed[first] & listed[second]):
                clashes.append(f"{word} ({first} and {second})")
        if clashes:
            raise ValueError(
                "declare_keyword_sets() was given words in two lists that exclude "
                "each other: " + ", ".join(clashes) + ". A keyword is reserved or "
                "unreserved, not both. Unimplemented means the server doesn't have "
                "the word, so it can't also be a keyword. A future reserved word "
                "isn't reserved yet. Keep each word in one of its two lists. If the "
                "server has a word but not a parent's syntax that uses it, keep the "
                "word a keyword and override that syntax in the dialect."
            )

    def declare_keyword_sets(
        self,
        *,
        reserved: Sequence[str],
        reserved_mode: str,
        unreserved: Sequence[str],
        unimplemented: Sequence[str],
        future_reserved: Sequence[str],
        future_reserved_mode: str,
    ) -> None:
        """Safely assign and inherit keywords by changing, not dropping, present status.

        The dialect starts with every keyword's status from its parent. Each
        word may be in no more than one of reserved, unreserved and
        unimplemented, and always gets the present status it's listed under,
        losing any contradictory inherited present status.

        Args:
            reserved: Words that are keywords everywhere and never names.
            reserved_mode: What happens to inherited reserved words that aren't
                explicitly given another status by the caller.
                "add": they are kept reserved
                "replace": they become unreserved
            unreserved: Words that are keywords in some places and names in
                others.
            unimplemented: Words the dialect's server (not sqlfluff) doesn't
                implement. In inherited grammar, evaluates to Nothing()
                and stop matching. You can see which ones block grammar with
                keyword_reference_test.py <dialect> --level notice
            future_reserved: Words the vendor says will become reserved. A tag
                that may go with unreserved, unimplemented, or unlisted words.
            future_reserved_mode:
                "add": parent future_reserved are kept, unless reserved above.
                "replace": parent future_reserved are dropped.

        A word may not lose all present status, as inherited grammar may use it
        either now or after future parent edits. This allows effortless feature
        inheritance, stops crashes from the parent adding a feature, and
        protects a parent from the maintenance burden of a poorly maintained
        child.

        A future_reserved word may be nothing, unreserved, or unimplemented, but
        not reserved.

        Exclusively using this function in child dialects to assign present
        keyword status is strongly recommended. This does not and should not
        address other sets, as they don't tend to cause bad refs on inheritance
        as grammar does not look for a single member and fail as they would
        with one of the above addressed keyword sets.
        """
        for argument, mode in (
            ("reserved_mode", reserved_mode),
            ("future_reserved_mode", future_reserved_mode),
        ):
            if mode not in ("add", "replace"):
                raise ValueError(
                    f'declare_keyword_sets() takes {argument}="add" or '
                    f'"replace", not {mode!r}.'
                )
        listed_reserved = self._keyword_words(
            reserved, "declare_keyword_sets", "reserved"
        )
        listed_unreserved = self._keyword_words(
            unreserved, "declare_keyword_sets", "unreserved"
        )
        listed_unimplemented = self._keyword_words(
            unimplemented, "declare_keyword_sets", "unimplemented"
        )
        listed_future = self._keyword_words(
            future_reserved, "declare_keyword_sets", "future_reserved"
        )
        self._refuse_overlapping_keyword_lists(
            {
                "reserved": listed_reserved,
                "unreserved": listed_unreserved,
                "unimplemented": listed_unimplemented,
                "future_reserved": listed_future,
            }
        )

        inherited_reserved = set(self.sets("reserved_keywords"))
        inherited_unreserved = set(self.sets("unreserved_keywords"))
        inherited_unimplemented = set(self.sets("unimplemented_keywords"))
        inherited_future = set(self.sets("future_reserved_keywords"))

        if reserved_mode == "replace":
            new_reserved = listed_reserved
            # Unlisted inherited reserved words become unreserved. A word the
            # call lists anywhere gets exactly what it says instead.
            demoted = (
                inherited_reserved
                - listed_reserved
                - listed_unreserved
                - listed_unimplemented
            )
        else:
            new_reserved = (
                inherited_reserved
                - listed_unreserved
                - listed_future
                - listed_unimplemented
            ) | listed_reserved
            # A future reserved word isn't reserved yet, so an inherited
            # reserved word listed as future becomes unreserved (or stays
            # unimplemented, if it's listed that way too: see below).
            demoted = inherited_reserved & listed_future
        new_unreserved = (
            inherited_unreserved | listed_unreserved | demoted
        ) - new_reserved
        # Listing a word as a keyword here switches inherited grammar that
        # needs it back on.
        new_unimplemented = (
            inherited_unimplemented - listed_reserved - listed_unreserved
        ) | listed_unimplemented
        # Unimplemented wins over an inherited keyword status, as it does in
        # expand(), so the sets never overlap.
        new_reserved -= new_unimplemented
        new_unreserved -= new_unimplemented
        if future_reserved_mode == "replace":
            new_future = listed_future - new_reserved
        else:
            new_future = (inherited_future | listed_future) - new_reserved

        new_sets = {
            "reserved_keywords": new_reserved,
            "unreserved_keywords": new_unreserved,
            "unimplemented_keywords": new_unimplemented,
            "future_reserved_keywords": new_future,
        }
        for label in KEYWORD_STATUS_SETS:
            keyword_set = self.sets(label)
            keyword_set.clear()
            keyword_set.update(new_sets[label])

    def copy_as(
        self,
        name: str,
        formatted_name: Optional[str] = None,
        docstring: Optional[str] = None,
        keyword_reference_error_docs: Optional[str] = None,
    ) -> "Dialect":
        """Copy this dialect and create a new one with a different name.

        This is the primary method for inheritance, after which, the
        `replace` method can be used to override particular rules.

        keyword_reference_error_docs is a message from the new dialect's
        maintainers to a contributor who is probably working on another
        dialect, usually a parent, and has hit a keyword reference error in
        this one: how to look up a keyword here. It is printed as is in those
        errors. Write whatever helps for this dialect: a link to the vendor's
        keyword list, or which source file and grammar rule to read. It is
        optional and not inherited.
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
            keyword_reference_error_docs=keyword_reference_error_docs,
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

    @staticmethod
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
                f"{self._reference_audit_tip(self.name)}"
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
                    name, self.name, self._reference_audit_tip(self.name)
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
