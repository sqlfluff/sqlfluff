"""The parser context.

This mirrors some of the same design of the flask
context manager. https://flask.palletsprojects.com/en/1.1.x/

The context acts as a way of keeping track of state, references
to common configuration and dialects, logging and also the parse
and match depth of the current operation.
"""

from collections import defaultdict
from contextlib import contextmanager
import logging
import uuid
from typing import Iterator, Optional, TYPE_CHECKING, Dict, Any, Tuple, Sequence

if TYPE_CHECKING:  # pragma: no cover
    from sqlfluff.core.parser.match_result import MatchResult
    from sqlfluff.core.dialects.base import Dialect, ExpandedDialectElementType
    from sqlfluff.core.config import FluffConfig

# Get the parser logger
parser_logger = logging.getLogger("sqlfluff.parser")


class ParseContext:
    """Object to handle the context at hand during parsing.

    Holds two tiers of references.
    1. Persistent config, like references to the dialect or
       the current verbosity and logger.
    2. Stack config, like the parse and match depth.

    The manipulation of the stack config is done using a context
    manager and layered config objects inside the context.

    NOTE: We use context managers here to avoid _copying_
    the context, just to mutate it safely. This is significantly
    more performant than the copy operation, but does require some
    care to use properly.

    When fetching elements from the context, we first look
    at the top level stack config object and the persistent
    config values (stored as attributes of the ParseContext
    itself).
    """

    def __init__(
        self,
        dialect: "Dialect",
        indentation_config: Optional[Dict[str, Any]] = None,
        recurse: bool = True,
    ) -> None:
        self.dialect = dialect
        self.recurse = recurse
        # Indentation config is used by Indent and Dedent and used to control
        # the intended indentation of certain features. Specifically it is
        # used in the Conditional grammar.
        self.indentation_config = indentation_config or {}
        # This is the logger that child objects will latch onto.
        self.logger = parser_logger
        # A uuid for this parse context to enable cache invalidation
        self.uuid = uuid.uuid4()
        # A dict for parse caching. This is reset for each file,
        # but persists for the duration of an individual file parse.
        self._parse_cache: Dict[Tuple[Any, ...], "MatchResult"] = {}
        # A dictionary for keeping track of some statistics on parsing
        # for performance optimisation.
        # Focused around BaseGrammar._longest_trimmed_match().
        # Initialise only with "next_counts", the rest will be int
        # and are dealt with in .increment().
        self.parse_stats: Dict[str, Any] = {"next_counts": defaultdict(int)}
        # The following attributes are only accessible via a copy
        # and not in the init method.
        self.match_segment: Optional[str] = None
        self.match_depth = 0
        self.parse_depth = 0
        # self.terminators is a tuple to afford some level of isolation
        # and protection from edits to outside the context. This introduces
        # a little more overhead than a list, but we manage this by only
        # copying it when necessary.
        # NOTE: Includes inherited parent terminators.
        self.terminators: Tuple["ExpandedDialectElementType", ...] = ()

    @classmethod
    def from_config(
        cls, config: "FluffConfig", **overrides: Dict[str, bool]
    ) -> "ParseContext":
        """Construct a `ParseContext` from a `FluffConfig`."""
        indentation_config = config.get_section("indentation") or {}
        try:
            indentation_config = {k: bool(v) for k, v in indentation_config.items()}
        except TypeError:  # pragma: no cover
            raise TypeError(
                "One of the configuration keys in the `indentation` section is not "
                "True or False: {!r}".format(indentation_config)
            )
        ctx = cls(
            dialect=config.get("dialect_obj"),
            recurse=config.get("recurse"),
            indentation_config=indentation_config,
        )
        # Set any overrides in the creation
        for key in overrides:
            if overrides[key] is not None:
                setattr(ctx, key, overrides[key])
        return ctx

    def _set_terminators(
        self,
        clear_terminators: bool = False,
        push_terminators: Optional[Sequence["ExpandedDialectElementType"]] = None,
    ) -> Tuple[int, Tuple["ExpandedDialectElementType", ...]]:
        _appended = 0
        # Retain a reference to the original terminators.
        _terminators = self.terminators
        # Note: only need to reset if clear _and not already clear_.
        if clear_terminators and self.terminators:
            # NOTE: It's really important that we .copy() on the way in, because
            # we don't know what else has a reference to the input list, and
            # we rely a lot in this code on having full control over the
            # list of terminators.
            self.terminators = tuple(push_terminators) if push_terminators else ()
        elif push_terminators:
            # Yes, inefficient for now.
            for terminator in push_terminators:
                if terminator not in self.terminators:
                    self.terminators += (terminator,)
                    _appended += 1
        return _appended, _terminators

    def _reset_terminators(
        self,
        appended: int,
        terminators: Tuple["ExpandedDialectElementType", ...],
        clear_terminators: bool = False,
    ) -> None:
        # If we totally reset them, just reinstate the old object.
        if clear_terminators:
            self.terminators = terminators
        # If we didn't, then trim any added ones.
        # NOTE: Because we dedupe, just because we had push_terminators
        # doesn't mean any of them actually got added here - we only trim
        # the number that actually got appended.
        elif appended:
            # Trim back to original length.
            self.terminators = self.terminators[:-appended]

    @contextmanager
    def deeper_match(
        self,
        clear_terminators: bool = False,
        push_terminators: Optional[Sequence["ExpandedDialectElementType"]] = None,
    ) -> Iterator["ParseContext"]:
        """Increment match depth."""
        self.match_depth += 1
        _append, _terms = self._set_terminators(clear_terminators, push_terminators)
        try:
            yield self
        finally:
            self._reset_terminators(
                _append, _terms, clear_terminators=clear_terminators
            )
            self.match_depth -= 1

    @contextmanager
    def deeper_parse(self) -> Iterator["ParseContext"]:
        """Increment parse depth."""
        _match_depth = self.match_depth
        self.parse_depth += 1
        self.match_depth = 0
        _append, _terms = self._set_terminators(clear_terminators=True)
        if not isinstance(self.recurse, bool):  # pragma: no cover TODO?
            self.recurse -= 1
        try:
            yield self
        finally:
            self.parse_depth -= 1
            self.match_depth = _match_depth
            if not isinstance(self.recurse, bool):  # pragma: no cover TODO?
                self.recurse += 1
            self._reset_terminators(_append, _terms, clear_terminators=True)

    def may_recurse(self) -> bool:
        """Return True if allowed to recurse."""
        return self.recurse > 1 or self.recurse is True

    @contextmanager
    def matching_segment(
        self,
        name: str,
        clear_terminators: bool = False,
        push_terminators: Optional[Sequence["ExpandedDialectElementType"]] = None,
    ) -> Iterator["ParseContext"]:
        """Set the name of the current matching segment.

        NB: We don't reset the match depth here.
        """
        old_name = self.match_segment
        self.match_segment = name
        _append, _terms = self._set_terminators(clear_terminators, push_terminators)
        try:
            yield self
        finally:
            self._reset_terminators(_append, _terms, clear_terminators)
            # Reset back to old name
            self.match_segment = old_name

    def check_parse_cache(
        self, loc_key: Tuple[Any, ...], matcher_key: str
    ) -> Optional["MatchResult"]:
        """Check against the parse cache for a pre-existing match.

        If no match is found in the cache, this returns None.
        """
        return self._parse_cache.get((loc_key, matcher_key))

    def put_parse_cache(
        self, loc_key: Tuple[Any, ...], matcher_key: str, match: "MatchResult"
    ) -> None:
        """Store a match in the cache for later retrieval."""
        self._parse_cache[(loc_key, matcher_key)] = match

    def increment(self, key: str, default: int = 0) -> None:
        """Increment one of the parse stats by name."""
        self.parse_stats[key] = self.parse_stats.get(key, 0) + 1
