"""Base grammar, Ref, Anything and Nothing."""

import copy
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    TypeVar,
    Union,
)
from uuid import UUID, uuid4

from sqlfluff.core.helpers.string import curtail_string
from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.match_algorithms import greedy_match
from sqlfluff.core.parser.match_result import MatchResult
from sqlfluff.core.parser.matchable import Matchable
from sqlfluff.core.parser.segments import BaseSegment
from sqlfluff.core.parser.types import ParseMode, SimpleHintType

if TYPE_CHECKING:  # pragma: no cover
    from sqlfluff.core.dialects.base import Dialect


def cached_method_for_parse_context(
    func: Callable[[Any, ParseContext, Optional[Tuple[str]]], SimpleHintType]
) -> Callable[..., SimpleHintType]:
    """A decorator to cache the output of this method for a given parse context.

    This cache automatically invalidates if the uuid
    of the parse context changes. The value is store
    in the __dict__ attribute of the class against a
    key unique to that function.
    """
    cache_key = "__cache_" + func.__name__

    def wrapped_method(
        self: Any, parse_context: ParseContext, crumbs: Optional[Tuple[str]] = None
    ) -> SimpleHintType:
        """Cache the output of the method against a given parse context.

        Note: kwargs are not taken into account in the caching, but
        for the current use case of dependency loop debugging that's
        ok.
        """
        try:
            cache_tuple: Tuple[UUID, SimpleHintType] = self.__dict__[cache_key]
            # Is the value for the current context?
            if cache_tuple[0] == parse_context.uuid:
                # If so return it.
                return cache_tuple[1]
        except KeyError:
            # Failed to find an item in the cache.
            pass

        # If we're here, we either didn't find a match in the cache or it
        # wasn't valid. Generate a new value, cache it and return
        result = func(self, parse_context, crumbs)
        self.__dict__[cache_key] = (parse_context.uuid, result)
        return result

    return wrapped_method


T = TypeVar("T", bound="BaseGrammar")


class BaseGrammar(Matchable):
    """Grammars are a way of composing match statements.

    Any grammar must implement the `match` function. Segments can also be
    passed to most grammars. Segments implement `match` as a classmethod. Grammars
    implement it as an instance method.

    """

    is_meta = False
    equality_kwargs: Tuple[str, ...] = ("_elements", "optional", "allow_gaps")
    # All grammars are assumed to support STRICT mode by default.
    # If they wish to support other modes, they should declare
    # it by overriding this attribute.
    supported_parse_modes: Set[ParseMode] = {ParseMode.STRICT}

    @staticmethod
    def _resolve_ref(elem: Union[str, Matchable]) -> Matchable:
        """Resolve potential string references to things we can match against."""
        if isinstance(elem, str):
            return Ref.keyword(elem)
        elif isinstance(elem, Matchable):
            # NOTE: BaseSegment types are an instance of Matchable.
            return elem

        raise TypeError(
            "Grammar element [{!r}] was found of unexpected type [{}] was "
            "found.".format(elem, type(elem))  # pragma: no cover
        )

    def __init__(
        self,
        *args: Union[Matchable, str],
        allow_gaps: bool = True,
        optional: bool = False,
        terminators: Sequence[Union[Matchable, str]] = (),
        reset_terminators: bool = False,
        parse_mode: ParseMode = ParseMode.STRICT,
    ) -> None:
        """Deal with kwargs common to all grammars.

        Args:
            *args: Any number of elements which because the subjects
                of this grammar. Optionally these elements may also be
                string references to elements rather than the Matchable
                elements themselves.
            allow_gaps (:obj:`bool`, optional): Does this instance of the
                grammar allow gaps between the elements it matches? This
                may be exhibited slightly differently in each grammar. See
                that grammar for details. Defaults `True`.
            optional (:obj:`bool`, optional): In the context of a sequence,
                is this grammar *optional*, i.e. can it be skipped if no
                match is found. Outside of a Sequence, this option does nothing.
                Defaults `False`.
            terminators (Sequence of :obj:`str` or Matchable): Matchable objects
                which can terminate the grammar early. These are also used in some
                parse modes to dictate how many segments to claim when handling
                unparsable sections. Items passed as :obj:`str` are assumed to
                refer to keywords and so will be passed to `Ref.keyword()` to
                be resolved. Terminators are also added to the parse context
                during deeper matching of child elements.
            reset_terminators (:obj:`bool`, default `False`): Controls whether
                any inherited terminators from outer grammars should be cleared
                before matching child elements. Situations where this might be
                appropriate are within bracketed expressions, where outer
                terminators should be temporarily ignored.
            parse_mode (:obj:`ParseMode`): Defines how eager the grammar should
                be in claiming unmatched segments. By default, grammars usually
                only claim what they can match, but by setting this to something
                more eager, grammars can control how unparsable sections are
                treated to give the user more granular feedback on what can (and
                what *cannot*) be parsed.
        """
        # We provide a common interface for any grammar that allows positional elements.
        # If *any* for the elements are a string and not a grammar, then this is a
        # shortcut to the Ref.keyword grammar by default.
        self._elements: List[Matchable] = [self._resolve_ref(e) for e in args]

        # Now we deal with the standard kwargs
        self.allow_gaps = allow_gaps
        self.optional: bool = optional

        # The intent here is that if we match something, and then the _next_
        # item is one of these, we can safely conclude it's a "total" match.
        # In those cases, we return early without considering more options.
        self.terminators: Sequence[Matchable] = [
            self._resolve_ref(t) for t in terminators
        ]
        self.reset_terminators = reset_terminators

        assert parse_mode in self.supported_parse_modes, (
            f"{self.__class__.__name__} does not support {parse_mode} "
            f"(only {self.supported_parse_modes})"
        )
        self.parse_mode = parse_mode
        # Generate a cache key
        self._cache_key = uuid4().hex

    def cache_key(self) -> str:
        """Get the cache key for this grammar.

        For grammars these are unique per-instance.
        """
        return self._cache_key

    def is_optional(self) -> bool:
        """Return whether this segment is optional.

        The optional attribute is set in the __init__ method.
        """
        return self.optional

    @cached_method_for_parse_context
    def simple(
        self, parse_context: ParseContext, crumbs: Optional[Tuple[str]] = None
    ) -> SimpleHintType:
        """Does this matcher support a lowercase hash matching route?"""
        return None

    def __str__(self) -> str:  # pragma: no cover TODO?
        """Return a string representation of the object."""
        return repr(self)

    def __repr__(self) -> str:
        """Return a string representation suitable for debugging."""
        return "<{}: [{}]>".format(
            self.__class__.__name__,
            curtail_string(
                ", ".join(curtail_string(repr(elem), 40) for elem in self._elements),
                100,
            ),
        )

    def __eq__(self, other: Any) -> bool:
        """Two grammars are equal if their elements and types are equal.

        NOTE: We use the equality_kwargs tuple on the class to define
        other kwargs which should also be checked so that things like
        "optional" is also taken into account in considering equality.
        """
        return type(self) is type(other) and all(
            getattr(self, k, None) == getattr(other, k, None)
            for k in self.equality_kwargs
        )

    def copy(
        self: T,
        insert: Optional[List[Matchable]] = None,
        at: Optional[int] = None,
        before: Optional[Any] = None,
        remove: Optional[List[Matchable]] = None,
        terminators: List[Union[str, Matchable]] = [],
        replace_terminators: bool = False,
        # NOTE: Optionally allow other kwargs to be provided to this
        # method for type compatibility. Any provided won't be used.
        **kwargs: Any,
    ) -> T:
        """Create a copy of this grammar, optionally with differences.

        This is mainly used in dialect inheritance.


        Args:
            insert (:obj:`list`, optional): Matchable elements to
                insert. This is inserted pre-expansion so can include
                unexpanded elements as normal.
            at (:obj:`int`, optional): The position in the elements
                to insert the item. Defaults to `None` which means
                insert at the end of the elements.
            before (optional): An alternative to _at_ to determine the
                position of an insertion. Using this inserts the elements
                immediately before the position of this element.
                Note that this is not an _index_ but an element to look
                for (i.e. a Segment or Grammar which will be compared
                with other elements for equality).
            remove (:obj:`list`, optional): A list of individual
                elements to remove from a grammar. Removal is done
                *after* insertion so that order is preserved.
                Elements are searched for individually.
            terminators (:obj:`list` of :obj:`str` or Matchable): New
                terminators to add to the existing ones. Whether they
                replace or append is controlled by `append_terminators`.
                :obj:`str` objects will be interpreted as keywords and
                passed to `Ref.keyword()`.
            replace_terminators (:obj:`bool`, default False): When `True`
                we replace the existing terminators from the copied grammar,
                otherwise we just append.
            **kwargs: Optional additional values may be passed to this
                method for inherited classes, but if unused they will raise
                an `AssertionError`.
        """
        assert not kwargs, f"Unexpected kwargs to .copy(): {kwargs}"
        # Copy only the *grammar* elements. The rest comes through
        # as is because they should just be classes rather than
        # instances.
        new_elems = [
            elem.copy() if isinstance(elem, BaseGrammar) else elem
            for elem in self._elements
        ]
        if insert:
            if at is not None and before is not None:  # pragma: no cover
                raise ValueError(
                    "Cannot specify `at` and `before` in BaseGrammar.copy()."
                )
            if before is not None:
                try:
                    idx = new_elems.index(before)
                except ValueError:  # pragma: no cover
                    raise ValueError(
                        "Could not insert {} in copy of {}. {} not Found.".format(
                            insert, self, before
                        )
                    )
                new_elems = new_elems[:idx] + insert + new_elems[idx:]
            elif at is None:
                new_elems = new_elems + insert
            else:
                new_elems = new_elems[:at] + insert + new_elems[at:]
        if remove:
            for elem in remove:
                try:
                    new_elems.remove(elem)
                except ValueError:  # pragma: no cover
                    raise ValueError(
                        "Could not remove {} from copy of {}. Not Found.".format(
                            elem, self
                        )
                    )
        new_grammar = copy.copy(self)
        new_grammar._elements = new_elems

        if replace_terminators:  # pragma: no cover
            # Override (NOTE: Not currently used).
            new_grammar.terminators = [self._resolve_ref(t) for t in terminators]
        else:
            # NOTE: This is also safe in the case that neither `terminators` or
            # `replace_terminators` are set. In that case, nothing will change.
            new_grammar.terminators = [
                *new_grammar.terminators,
                *(self._resolve_ref(t) for t in terminators),
            ]

        return new_grammar


class Ref(BaseGrammar):
    """A kind of meta-grammar that references other grammars by name at runtime."""

    equality_kwargs: Tuple[str, ...] = ("_ref", "optional", "allow_gaps")

    def __init__(
        self,
        *args: str,
        exclude: Optional[Matchable] = None,
        terminators: Sequence[Union[Matchable, str]] = (),
        reset_terminators: bool = False,
        allow_gaps: bool = True,
        optional: bool = False,
    ) -> None:
        # For Ref, there should only be one arg.
        assert len(args) == 1, (
            "Ref grammar can only deal with precisely one element for now. Instead "
            f"found {args!r}"
        )
        assert isinstance(args[0], str), f"Ref must be string. Found {args}."
        self._ref = args[0]
        # Any patterns to _prevent_ a match.
        self.exclude = exclude
        super().__init__(
            # NOTE: Don't pass on any args (we've already handled it with self._ref)
            allow_gaps=allow_gaps,
            optional=optional,
            # Terminators don't take effect directly within this grammar, but
            # the Ref grammar is an effective place to manage the terminators
            # inherited via the context.
            terminators=terminators,
            reset_terminators=reset_terminators,
        )

    @cached_method_for_parse_context
    def simple(
        self, parse_context: ParseContext, crumbs: Optional[Tuple[str]] = None
    ) -> SimpleHintType:
        """Does this matcher support a uppercase hash matching route?

        A ref is simple, if the thing it references is simple.
        """
        if crumbs and self._ref in crumbs:  # pragma: no cover
            loop = " -> ".join(crumbs)
            raise RecursionError(f"Self referential grammar detected: {loop}")
        return self._get_elem(dialect=parse_context.dialect).simple(
            parse_context=parse_context,
            crumbs=(crumbs or ()) + (self._ref,),
        )

    def _get_elem(self, dialect: "Dialect") -> Matchable:
        """Get the actual object we're referencing."""
        if dialect:
            # Use the dialect to retrieve the grammar it refers to.
            return dialect.ref(self._ref)
        else:  # pragma: no cover
            raise ReferenceError("No Dialect has been provided to Ref grammar!")

    def __repr__(self) -> str:
        """Return a string representation of the 'Ref' object."""
        return "<Ref: {}{}>".format(
            repr(self._ref), " [opt]" if self.is_optional() else ""
        )

    def match(
        self,
        segments: Sequence["BaseSegment"],
        idx: int,
        parse_context: "ParseContext",
    ) -> MatchResult:
        """Match a list of segments against this segment.

        Matching can be done from either the raw or the segments.
        This raw function can be overridden, or a grammar defined
        on the underlying class.

        Args:
            segments (Tuple[BaseSegment, ...]): The sequence of segments
                to match against.
            idx (int): Index of the element in the sequence.
            parse_context (ParseContext): The parse context.

        Returns:
            MatchResult: The result of the matching process.
        """
        elem = self._get_elem(dialect=parse_context.dialect)

        # First if we have an *exclude* option, we should check that
        # which would prevent the rest of this grammar from matching.
        if self.exclude:
            with parse_context.deeper_match(
                name=self._ref + "-Exclude",
                clear_terminators=self.reset_terminators,
                push_terminators=self.terminators,
            ) as ctx:
                if self.exclude.match(segments, idx, ctx):
                    return MatchResult.empty_at(idx)

        # Match against that. NB We're not incrementing the match_depth here.
        # References shouldn't really count as a depth of match.
        with parse_context.deeper_match(
            name=self._ref,
            clear_terminators=self.reset_terminators,
            push_terminators=self.terminators,
        ) as ctx:
            return elem.match(segments, idx, parse_context)

    @classmethod
    def keyword(cls, keyword: str, optional: bool = False) -> BaseGrammar:
        """Generate a reference to a keyword by name.

        This function is entirely syntactic sugar, and designed
        for more readable dialects.

        Ref.keyword('select') == Ref('SelectKeywordSegment')

        Args:
            keyword (str): The name of the keyword.
            optional (bool, optional): Whether the keyword is optional or
                not. Defaults to False.

        Returns:
            BaseGrammar: An instance of the BaseGrammar class.
        """
        name = keyword.capitalize() + "KeywordSegment"
        return cls(name, optional=optional)


class Anything(BaseGrammar):
    """Matches anything."""

    def match(
        self,
        segments: Sequence["BaseSegment"],
        idx: int,
        parse_context: "ParseContext",
    ) -> MatchResult:
        """Matches... Anything.

        Most useful in match grammars, where a later parse grammar
        will work out what's inside.

        NOTE: This grammar does still only match as far as any inherited
        terminators if they exist.
        """
        terminators = [*self.terminators]
        if not self.reset_terminators:
            # Only add context terminators if we're not resetting.
            terminators.extend(parse_context.terminators)
        if not terminators:
            return MatchResult(slice(idx, len(segments)))

        return greedy_match(
            segments,
            idx,
            parse_context,
            terminators,
            # Using the nested match option means that we can match
            # any bracketed sections we find to persist the structure
            # even if this grammar is permissive on the meaning.
            # This preserves backward compatibility with older
            # parsing behaviour.
            nested_match=True,
        )


class Nothing(BaseGrammar):
    """Matches nothing.

    Useful for placeholders which might be overwritten by other
    dialects.
    """

    def match(
        self,
        segments: Sequence["BaseSegment"],
        idx: int,
        parse_context: "ParseContext",
    ) -> MatchResult:
        """Always return a failed (empty) match."""
        return MatchResult.empty_at(idx)
