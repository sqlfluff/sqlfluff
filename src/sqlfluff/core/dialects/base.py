"""Defines the base dialect class."""

from typing import Set, Union, Type

from sqlfluff.core.parser import (
    KeywordSegment,
    SegmentGenerator,
    BaseSegment,
    StringParser,
)
from sqlfluff.core.parser.grammar.base import BaseGrammar
from sqlfluff.core.parser.matchable import Matchable

DialectElementType = Union[Type[BaseSegment], Matchable, SegmentGenerator]
# NOTE: Post expansion, no generators remain
ExpandedDialectElementType = Union[Type[BaseSegment], Matchable]


class Dialect:
    """Serves as the basis for runtime resolution of Grammar.

    Args:
        name (:obj:`str`): The name of the dialect, used for lookup.
        lexer_matchers (iterable of :obj:`StringLexer`): A structure defining
            the lexing config for this dialect.

    """

    def __init__(
        self,
        name,
        lexer_matchers=None,
        library=None,
        sets=None,
        inherits_from=None,
        root_segment_name=None,
    ):
        self._library = library or {}
        self.name = name
        self.lexer_matchers = lexer_matchers
        self.expanded = False
        self._sets = sets or {}
        self.inherits_from = inherits_from
        self.root_segment_name = root_segment_name

    def __repr__(self):  # pragma: no cover
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
            if isinstance(expanded_copy._library[key], SegmentGenerator):
                # If the element is callable, call it passing the current
                # dialect and store the result in its place.
                # Use the .replace() method for its error handling.
                expanded_copy.replace(
                    **{key: expanded_copy._library[key].expand(expanded_copy)}
                )
        # Expand any keyword sets.
        for keyword_set in [
            "unreserved_keywords",
            "reserved_keywords",
        ]:  # e.g. reserved_keywords, (JOIN, ...)
            # Make sure the values are available as KeywordSegments
            for kw in expanded_copy.sets(keyword_set):
                n = kw.capitalize() + "KeywordSegment"
                if n not in expanded_copy._library:
                    expanded_copy._library[n] = StringParser(kw.lower(), KeywordSegment)
        expanded_copy.expanded = True
        return expanded_copy

    def sets(self, label) -> Set:
        """Allows access to sets belonging to this dialect.

        These sets belong to the dialect and are copied for sub
        dialects. These are used in combination with late-bound
        dialect objects to create some of the bulk-produced rules.

        """
        if label not in self._sets:
            self._sets[label] = set()
        return self._sets[label]

    def copy_as(self, name):
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

        return self.__class__(
            name=name,
            library=self._library.copy(),
            lexer_matchers=self.lexer_matchers.copy(),
            sets=new_sets,
            inherits_from=self.name,
            root_segment_name=self.root_segment_name,
        )

    def add(self, **kwargs: DialectElementType):
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

    def replace(self, **kwargs: DialectElementType):
        """Override a segment on the dialect directly.

        Usage is very similar to add, but elements specified must already exist.
        """
        for n in kwargs:
            if n not in self._library:  # pragma: no cover
                raise ValueError(f"{n!r} is not already registered in {self!r}")
            cls = kwargs[n]
            if self._library[n] is cls:
                continue
            elif self._library[n] == cls:
                # Check for replacement with a new but identical class.
                # This would be a sign of redundant definitions in the dialect.
                raise ValueError(
                    f"Attempted unnecessary identical redefinition of {n!r} in {self!r}"
                )  # pragma: no cover

            # To replace a segment, the replacement must either be a
            # subclass of the original, *or* it must have the same
            # public methods and/or fields as it.
            base_dir = set(dir(self._library[n]))
            subclass = False
            if isinstance(self._library[n], type) and isinstance(cls, type):
                subclass = issubclass(cls, self._library[n])
                if not subclass:
                    if self._library[n].type != cls.type:
                        raise ValueError(  # pragma: no cover
                            f"Cannot replace {n!r} because 'type' property does not "
                            f"match: {cls.type} != {self._library[n].type}"
                        )

                    cls_dir = set(dir(cls))
                    missing = set(
                        n for n in base_dir.difference(cls_dir) if not n.startswith("_")
                    )
                    if missing:
                        raise ValueError(  # pragma: no cover
                            f"Cannot replace {n!r} because it's not a subclass and "
                            f"is missing these from base: {', '.join(missing)}"
                        )

            if subclass:
                # If the segment class we're replacing defines these fields, the
                # replacement must override either:
                # - NONE of them or
                # - ALL of them
                # Overriding a subset of them is not necessarily wrong, but it's
                # error-prone, hence this policy.
                grammars = {"match_grammar", "parse_grammar"}
                # TRICKY: The explicit use of __dict__ on the classes is
                # deliberate. We are concerned with whether a class itself does
                # or does not define a thing, IGNORING INHERITED VALUES.
                if grammars.intersection(set(self._library[n].__dict__)) == grammars:
                    overrides = grammars.intersection(set(cls.__dict__))
                    if overrides and overrides != grammars:
                        for grammar in grammars:
                            if (
                                grammar in self._library[n].__dict__
                                and grammar not in cls.__dict__
                            ):
                                raise ValueError(
                                    f"Cannot replace {n!r} because it needs "
                                    f"to define '{grammar}'"
                                )
            self._library[n] = cls

    def add_update_segments(self, module_dct):
        """Scans module dictionary, adding or replacing segment definitions."""
        for k, v in module_dct.items():
            if isinstance(v, type) and issubclass(v, BaseSegment):
                if k not in self._library:
                    self.add(**{k: v})
                else:
                    self.replace(**{k: v})

    def get_grammar(self, name: str) -> BaseGrammar:
        """Allow access to grammars pre-expansion.

        This is typically for dialect inheritance. This method
        also validates that the result is a grammar.
        """
        if name not in self._library:  # pragma: no cover
            raise ValueError(f"Element {name} not found in dialect.")
        if not isinstance(self._library[name], BaseGrammar):  # pragma: no cover
            raise TypeError(
                f"Attempted to fetch non grammar [{name}] with get_grammar."
            )
        return self._library[name]

    def get_segment(self, name: str) -> Type["BaseSegment"]:
        """Allow access to segments pre-expansion.

        This is typically for dialect inheritance. This method
        also validates that the result is a segment.
        """
        if name not in self._library:  # pragma: no cover
            raise ValueError(f"Element {name} not found in dialect.")
        if not issubclass(self._library[name], BaseSegment):  # pragma: no cover
            raise TypeError(
                f"Attempted to fetch non segment [{name}] with get_segment."
            )
        return self._library[name]

    def ref(self, name: str) -> ExpandedDialectElementType:
        """Return an object which acts as a late binding reference to the element named.

        NB: This requires the dialect to be expanded, and only returns Matchables
        as a result.

        """
        if not self.expanded:  # pragma: no cover
            raise RuntimeError("Dialect must be expanded before use.")

        if name in self._library:
            res = self._library[name]
            if res:
                return res
            else:  # pragma: no cover
                raise ValueError(
                    "Unexpected Null response while fetching {!r} from {}".format(
                        name, self.name
                    )
                )
        else:  # pragma: no cover
            if name.endswith("KeywordSegment"):
                keyword_tip = (
                    " Perhaps specify the keyword? "
                    "https://github.com/sqlfluff/sqlfluff/wiki/Contributing-Dialect-Changes#keywords"  # noqa E501
                )
            else:
                keyword_tip = ""
            raise RuntimeError(
                (
                    "Grammar refers to "
                    "{!r} which was not found in the {} dialect.{}".format(
                        name, self.name, keyword_tip
                    )
                )
            )

    def set_lexer_matchers(self, lexer_matchers):
        """Set the lexer struct for the dialect.

        This is what is used for base dialects. For derived dialects
        (which don't exist yet) the assumption is that we'll introduce
        some kind of *patch* function which could be used to mutate
        an existing `lexer_matchers`.
        """
        self.lexer_matchers = lexer_matchers

    def get_lexer_matchers(self):
        """Fetch the lexer struct for this dialect."""
        if self.lexer_matchers:
            return self.lexer_matchers
        else:  # pragma: no cover
            raise ValueError(f"Lexing struct has not been set for dialect {self}")

    def patch_lexer_matchers(self, lexer_patch):
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

    def insert_lexer_matchers(self, lexer_patch, before):
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

    def get_root_segment(self):
        """Get the root segment of the dialect."""
        return self.ref(self.root_segment_name)
