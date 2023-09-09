"""Base grammar, Ref, Anything and Nothing."""

import copy
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Iterable,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    TypeVar,
    Union,
)
from uuid import UUID, uuid4

from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.helpers import trim_non_code_segments
from sqlfluff.core.parser.match_logging import parse_match_logging
from sqlfluff.core.parser.match_result import MatchResult
from sqlfluff.core.parser.match_wrapper import match_wrapper
from sqlfluff.core.parser.matchable import Matchable
from sqlfluff.core.parser.segments import BaseSegment, allow_ephemeral
from sqlfluff.core.parser.types import MatchableType, SimpleHintType
from sqlfluff.core.string_helpers import curtail_string

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

    @staticmethod
    def _resolve_ref(elem: Union[str, MatchableType]) -> MatchableType:
        """Resolve potential string references to things we can match against."""
        if isinstance(elem, str):
            return Ref.keyword(elem)
        elif isinstance(elem, Matchable):
            return elem
        elif issubclass(elem, BaseSegment):
            return elem

        raise TypeError(
            "Grammar element [{!r}] was found of unexpected type [{}] was "
            "found.".format(elem, type(elem))  # pragma: no cover
        )

    def __init__(
        self,
        *args: Union[MatchableType, str],
        allow_gaps: bool = True,
        optional: bool = False,
        ephemeral_name: Optional[str] = None,
        terminators: Sequence[Union[MatchableType, str]] = (),
        reset_terminators: bool = False,
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
            ephemeral_name (:obj:`str`, optional): If specified this allows
                the grammar to match anything, and create an EphemeralSegment
                with the given name in its place. The content of this grammar
                is passed to the segment, and will become the parse grammar
                for it. If used widely this is an excellent way of breaking
                up the parse process and also signposting the name of a given
                chunk of code that might be parsed separately.
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
        """
        # We provide a common interface for any grammar that allows positional elements.
        # If *any* for the elements are a string and not a grammar, then this is a
        # shortcut to the Ref.keyword grammar by default.
        self._elements: List[MatchableType] = [self._resolve_ref(e) for e in args]

        # Now we deal with the standard kwargs
        self.allow_gaps = allow_gaps
        self.optional: bool = optional

        # The intent here is that if we match something, and then the _next_
        # item is one of these, we can safely conclude it's a "total" match.
        # In those cases, we return early without considering more options.
        self.terminators: Sequence[MatchableType] = [
            self._resolve_ref(t) for t in terminators
        ]
        self.reset_terminators = reset_terminators

        # ephemeral_name is a flag to indicate whether we need to make an
        # EphemeralSegment class. This is effectively syntactic sugar
        # to allow us to avoid specifying a EphemeralSegment directly in a dialect.
        # If this is the case, the actual segment construction happens in the
        # match_wrapper.
        self.ephemeral_name = ephemeral_name
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

    @match_wrapper()
    @allow_ephemeral
    def match(
        self, segments: Tuple[BaseSegment, ...], parse_context: ParseContext
    ) -> MatchResult:
        """Match a list of segments against this segment.

        Matching can be done from either the raw or the segments.
        This raw function can be overridden, or a grammar defined
        on the underlying class.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} has no match function implemented"
        )  # pragma: no cover

    @cached_method_for_parse_context
    def simple(
        self, parse_context: ParseContext, crumbs: Optional[Tuple[str]] = None
    ) -> SimpleHintType:
        """Does this matcher support a lowercase hash matching route?"""
        return None

    @staticmethod
    def _first_non_whitespace(
        segments: Iterable["BaseSegment"],
    ) -> Optional[Tuple[str, Set[str]]]:
        """Return the upper first non-whitespace segment in the iterable."""
        for segment in segments:
            if segment.first_non_whitespace_segment_raw_upper:
                return (
                    segment.first_non_whitespace_segment_raw_upper,
                    segment.class_types,
                )
        return None

    @classmethod
    def _prune_options(
        cls,
        options: List[MatchableType],
        segments: Tuple[BaseSegment, ...],
        parse_context: ParseContext,
    ) -> List[MatchableType]:
        """Use the simple matchers to prune which options to match on.

        Works in the context of a grammar making choices between options
        such as AnyOf or the content of Delimited.
        """
        available_options = []
        prune_buff = []

        # Find the first code element to match against.
        first_segment = cls._first_non_whitespace(segments)
        # If we don't have an appropriate option to match against,
        # then we should just return immediately. Nothing will match.
        if not first_segment:
            return options
        first_raw, first_types = first_segment

        for opt in options:
            simple = opt.simple(parse_context=parse_context)
            if simple is None:
                # This element is not simple, we have to do a
                # full match with it...
                available_options.append(opt)
                continue

            # Otherwise we have a simple option, so let's use
            # it for pruning.
            simple_raws, simple_types = simple
            matched = False

            # We want to know if the first meaningful element of the str_buff
            # matches the option, based on either simple _raw_ matching or
            # simple _type_ matching.

            # Match Raws
            if simple_raws and first_raw in simple_raws:
                # If we get here, it's matched the FIRST element of the string buffer.
                available_options.append(opt)
                matched = True

            # Match Types
            if simple_types and not matched and first_types.intersection(simple_types):
                # If we get here, it's matched the FIRST element of the string buffer.
                available_options.append(opt)
                matched = True

            if not matched:
                # Ditch this option, the simple match has failed
                prune_buff.append(opt)
                continue

        return available_options

    @classmethod
    def _longest_trimmed_match(
        cls,
        segments: Tuple[BaseSegment, ...],
        matchers: List[MatchableType],
        parse_context: ParseContext,
        trim_noncode: bool = True,
    ) -> Tuple[MatchResult, Optional[MatchableType]]:
        """Return longest match from a selection of matchers.

        Prioritise the first match, and if multiple match at the same point the longest.
        If two matches of the same length match at the same time, then it's the first in
        the iterable of matchers.

        Returns:
            `tuple` of (match_object, matcher).

        NOTE: This matching method is the workhorse of the parser. It drives the
        functionality of the AnyOf & AnyNumberOf grammars, and therefore by extension
        the degree of branching within the parser. It's performance can be monitored
        using the `parse_stats` object on the context.

        The things which determine the performance of this method are:
        1. Pruning. This method uses `_prune_options()` to filter down which matchable
           options proceed to the full matching step. Ideally only very few do and this
           can handle the majority of the filtering.
        2. Caching. This method uses the parse cache (`check_parse_cache` and
           `put_parse_cache`) on the ParseContext to speed up repetitive matching
           operations. As we make progress through a file there will often not be a
           cached value already available, and so this cache has the greatest impact
           within poorly optimised (or highly nested) expressions.
        3. Terminators. By default, _all_ the options are evaluated, and then the
           longest (the `best`) is returned. The exception to this is when the match
           is `complete` (i.e. it matches _all_ the remaining segments), or when a
           match is followed by a valid terminator (i.e. a segment which indicates
           that the match is _effectively_ complete). In these latter scenarios, the
           _first_ complete or terminated match is returned. In the ideal case, the
           only matcher which is evaluated should be the "correct" one, and then no
           others should be attempted.
        """
        # Have we been passed an empty list?
        if len(segments) == 0:  # pragma: no cover
            return MatchResult.from_empty(), None
        # If presented with no options, return no match
        elif not matchers:
            return MatchResult.from_unmatched(segments), None

        # Prune available options, based on their simple representation for efficiency.
        available_options = cls._prune_options(
            matchers, segments, parse_context=parse_context
        )

        # If we've pruned all the options, return no match
        if not available_options:
            return MatchResult.from_unmatched(segments), None

        terminated = False

        parse_context.increment("ltm_calls")
        # NOTE: The use of terminators is only available via the context.
        # They are set in that way to allow appropriate inheritance rather
        # than only being used in a per-grammar basis.
        if parse_context.terminators:
            parse_context.increment("ltm_calls_w_ctx_terms")
            terminators = parse_context.terminators
        else:
            terminators = ()

        # If gaps are allowed, trim the ends.
        if trim_noncode:
            pre_nc, segments, post_nc = trim_non_code_segments(segments)

        # At parse time we should be able to count on there being a location.
        assert segments[0].pos_marker

        # Characterise this location.
        # Initial segment raw, loc, type and length of segment series.
        loc_key = (
            segments[0].raw,
            segments[0].pos_marker.working_loc,
            segments[0].get_type(),
            len(segments),
        )

        best_match_length = 0
        best_match: Optional[Tuple[MatchResult, MatchableType]] = None
        # iterate at this position across all the matchers
        for idx, matcher in enumerate(available_options):
            # Check parse cache.
            matcher_key = matcher.cache_key()
            res_match: Optional[MatchResult] = parse_context.check_parse_cache(
                loc_key, matcher_key
            )
            if res_match:
                parse_match_logging(
                    cls.__name__,
                    "_look_ahead_match",
                    "HIT",
                    parse_context=parse_context,
                    cache_hit=matcher.__class__.__name__,
                    cache_key=matcher_key,
                )
            else:
                # Match fresh if no cache hit
                res_match = matcher.match(segments, parse_context)
                # Cache it for later to for performance.
                parse_context.put_parse_cache(loc_key, matcher_key, res_match)

            if res_match.is_complete():
                # Just return it! (WITH THE RIGHT OTHER STUFF)
                parse_context.increment("complete_match")
                if trim_noncode:
                    return (
                        MatchResult.from_matched(
                            pre_nc + res_match.matched_segments + post_nc
                        ),
                        matcher,
                    )
                else:
                    return res_match, matcher
            elif res_match:
                # We've got an incomplete match, if it's the best so far keep it.
                if res_match.trimmed_matched_length > best_match_length:
                    best_match = res_match, matcher
                    best_match_length = res_match.trimmed_matched_length

                    # If we've got a terminator next, it's an opportunity to
                    # end earlier, and claim an effectively "complete" match.
                    # NOTE: This means that by specifying terminators, we can
                    # significantly increase performance.
                    if idx == len(available_options) - 1:
                        # If it's the last option - no need to check terminators.
                        # We're going to end anyway, so we can skip that step.
                        terminated = True
                        break
                    elif terminators:
                        _, segs, _ = trim_non_code_segments(
                            best_match[0].unmatched_segments
                        )
                        for terminator in terminators:
                            terminator_match: MatchResult = terminator.match(
                                segs, parse_context
                            )

                            if terminator_match.matched_segments:
                                terminated = True
                                break

            if terminated:
                break

            # We could stash segments here, but given we might have some successful
            # matches here, we shouldn't, because they'll be mutated in the wrong way.
            # Eventually there might be a performance gain from doing that sensibly
            # here.

        if terminated:
            parse_context.increment("terminated_match")
        else:
            parse_context.increment("unterminated_match")

        # If we get here, then there wasn't a complete match. If we
        # has a best_match, return that.
        if best_match_length > 0:
            assert best_match
            # If not terminated, keep track of what the next token would
            # have been if we had been able to terminate using it.
            if not terminated:
                if best_match[0].unmatched_segments:
                    for seg in best_match[0].unmatched_segments:
                        if seg.is_code:
                            break
                    next_seg = seg.raw_segments[0].raw_upper
                else:  # pragma: no cover
                    # NOTE: I don't think this clause should ever
                    # occur, but it's included so that if it does happen
                    # we don't get an exception and can better debug.
                    next_seg = "<NONE>"
                parse_context.parse_stats["next_counts"][next_seg] += 1

            if trim_noncode:
                return (
                    MatchResult(
                        pre_nc + best_match[0].matched_segments,
                        best_match[0].unmatched_segments + post_nc,
                    ),
                    best_match[1],
                )
            else:
                return best_match
        # If no match at all, return nothing
        return MatchResult.from_unmatched(segments), None

    def __str__(self) -> str:  # pragma: no cover TODO?
        return repr(self)

    def __repr__(self) -> str:
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
        insert: Optional[List[MatchableType]] = None,
        at: Optional[int] = None,
        before: Optional[Any] = None,
        remove: Optional[List[MatchableType]] = None,
        terminators: List[Union[str, MatchableType]] = [],
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
        exclude: Optional[MatchableType] = None,
        terminators: Sequence[Union[MatchableType, str]] = (),
        reset_terminators: bool = False,
        allow_gaps: bool = True,
        optional: bool = False,
        ephemeral_name: Optional[str] = None,
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
            ephemeral_name=ephemeral_name,
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

    def _get_elem(self, dialect: "Dialect") -> MatchableType:
        """Get the actual object we're referencing."""
        if dialect:
            # Use the dialect to retrieve the grammar it refers to.
            return dialect.ref(self._ref)
        else:  # pragma: no cover
            raise ReferenceError("No Dialect has been provided to Ref grammar!")

    def __repr__(self) -> str:
        return "<Ref: {}{}>".format(
            repr(self._ref), " [opt]" if self.is_optional() else ""
        )

    @match_wrapper(v_level=4)  # Log less for Ref
    @allow_ephemeral
    def match(
        self, segments: Tuple[BaseSegment, ...], parse_context: ParseContext
    ) -> "MatchResult":
        """Match a list of segments against this segment.

        Matching can be done from either the raw or the segments.
        This raw function can be overridden, or a grammar defined
        on the underlying class.
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
                if self.exclude.match(segments, ctx):
                    return MatchResult.from_unmatched(segments)

        # Match against that. NB We're not incrementing the match_depth here.
        # References shouldn't really count as a depth of match.
        with parse_context.deeper_match(
            name=self._ref,
            clear_terminators=self.reset_terminators,
            push_terminators=self.terminators,
        ) as ctx:
            resp = elem.match(segments, ctx)

        return resp

    @classmethod
    def keyword(cls, keyword: str, optional: bool = False) -> BaseGrammar:
        """Generate a reference to a keyword by name.

        This function is entirely syntactic sugar, and designed
        for more readable dialects.

        Ref.keyword('select') == Ref('SelectKeywordSegment')

        """
        name = keyword.capitalize() + "KeywordSegment"
        return cls(name, optional=optional)


class Anything(BaseGrammar):
    """Matches anything."""

    def match(
        self, segments: Tuple[BaseSegment, ...], parse_context: ParseContext
    ) -> "MatchResult":
        """Matches... Anything.

        Most useful in match grammars, where a later parse grammar
        will work out what's inside.
        """
        return MatchResult.from_matched(segments)


class Nothing(BaseGrammar):
    """Matches nothing.

    Useful for placeholders which might be overwritten by other
    dialects.
    """

    def match(
        self, segments: Tuple[BaseSegment, ...], parse_context: ParseContext
    ) -> "MatchResult":
        """Matches... nothing.

        Useful for placeholders which might be overwritten by other
        dialects.
        """
        return MatchResult.from_unmatched(segments)
