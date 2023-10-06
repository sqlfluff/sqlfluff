"""Defines the base dialect class."""

import sys
from typing import Any, Dict, List, Optional, Set, Type, Union, cast

from sqlfluff.core.parser import (
    BaseSegment,
    KeywordSegment,
    SegmentGenerator,
    StringParser,
)
from sqlfluff.core.parser.grammar.base import BaseGrammar, Nothing
from sqlfluff.core.parser.lexer import LexerType
from sqlfluff.core.parser.matchable import Matchable
from sqlfluff.core.parser.types import BracketPairTuple, DialectElementType


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
        lexer_matchers: Optional[List[LexerType]] = None,
        library: Optional[Dict[str, DialectElementType]] = None,
        sets: Optional[Dict[str, Set[Union[str, BracketPairTuple]]]] = None,
        inherits_from: Optional[str] = None,
    ) -> None:
        self._library = library or {}
        self.name = name
        self.lexer_matchers = lexer_matchers
        self.expanded = False
        self._sets = sets or {}
        self.inherits_from = inherits_from
        self.root_segment_name = root_segment_name

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
        ]:  # e.g. reserved_keywords, (JOIN, ...)
            # Make sure the values are available as KeywordSegments
            keyword_sets = expanded_copy.sets(keyword_set)
            for kw in keyword_sets:
                n = kw.capitalize() + "KeywordSegment"
                if n not in expanded_copy._library:
                    expanded_copy._library[n] = StringParser(kw.lower(), KeywordSegment)
        expanded_copy.expanded = True
        return expanded_copy

    def sets(self, label: str) -> Set[str]:
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
        return cast(Set[str], self._sets[label])

    def bracket_sets(self, label: str) -> Set[BracketPairTuple]:
        """Allows access to bracket sets belonging to this dialect."""
        assert label in (
            "bracket_pairs",
            "angle_bracket_pairs",
        ), "Invalid bracket set. Consider using `sets` instead."

        if label not in self._sets:
            self._sets[label] = set()
        return cast(Set[BracketPairTuple], self._sets[label])

    def update_keywords_set_from_multiline_string(
        self, set_label: str, values: str
    ) -> None:
        """Special function to update a keywords set from a multi-line string."""
        self.sets(set_label).update(
            [n.strip().upper() for n in values.strip().split("\n")]
        )

    def copy_as(self, name: str) -> "Dialect":
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
            sets=new_sets,
            inherits_from=self.name,
            root_segment_name=self.root_segment_name,
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
                assert isinstance(
                    replacement, type
                ), f"Cannot replace {n!r} with {replacement}"
                old_seg = cast(Type["BaseSegment"], self._library[n])
                new_seg = cast(Type["BaseSegment"], replacement)
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
                    missing = set(
                        n for n in base_dir.difference(cls_dir) if not n.startswith("_")
                    )
                    if missing:
                        raise ValueError(  # pragma: no cover
                            f"Cannot replace {n!r} because it's not a subclass and "
                            f"is missing these from base: {', '.join(missing)}"
                        )

            self._library[n] = replacement

    def add_update_segments(self, module_dct: Dict[str, Any]) -> None:
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

    def get_segment(self, name: str) -> Type["BaseSegment"]:
        """Allow access to segments pre-expansion.

        This is typically for dialect inheritance. This method
        also validates that the result is a segment.
        """
        if name not in self._library:  # pragma: no cover
            raise ValueError(f"Element {name} not found in dialect.")
        segment = cast(Type["BaseSegment"], self._library[name])

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
                "https://github.com/sqlfluff/sqlfluff/wiki/Contributing-Dialect-Changes#keywords"  # noqa E501
            )
            # Keyword errors are common so avoid printing the whole, scary,
            # traceback as not that useful and confusing to people.
            sys.tracebacklimit = 0
            raise RuntimeError(
                (
                    "Grammar refers to the "
                    "{!r} keyword which was not found in the {} dialect.{}".format(
                        keyword, self.name, keyword_tip
                    )
                )
            )
        else:  # pragma: no cover
            raise RuntimeError(
                (
                    "Grammar refers to "
                    "{!r} which was not found in the {} dialect.".format(
                        name, self.name
                    )
                )
            )

    def set_lexer_matchers(self, lexer_matchers: List[LexerType]) -> None:
        """Set the lexer struct for the dialect.

        This is what is used for base dialects. For derived dialects
        (which don't exist yet) the assumption is that we'll introduce
        some kind of *patch* function which could be used to mutate
        an existing `lexer_matchers`.
        """
        self.lexer_matchers = lexer_matchers

    def get_lexer_matchers(self) -> List[LexerType]:
        """Fetch the lexer struct for this dialect."""
        if self.lexer_matchers:
            return self.lexer_matchers
        else:  # pragma: no cover
            raise ValueError(f"Lexing struct has not been set for dialect {self}")

    def patch_lexer_matchers(self, lexer_patch: List[LexerType]) -> None:
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

    def insert_lexer_matchers(self, lexer_patch: List[LexerType], before: str) -> None:
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

    def get_root_segment(self) -> Union[Type[BaseSegment], Matchable]:
        """Get the root segment of the dialect."""
        return self.ref(self.root_segment_name)
