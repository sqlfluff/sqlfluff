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
from typing import Optional, TYPE_CHECKING, Dict, Any, Tuple, Type, List

if TYPE_CHECKING:  # pragma: no cover
    from types import TracebackType
    from sqlfluff.core.parser.match_result import MatchResult
    from sqlfluff.core.dialects.base import Dialect, ExpandedDialectElementType
    from sqlfluff.core.config import FluffConfig

# Get the parser logger
parser_logger = logging.getLogger("sqlfluff.parser")


class RootParseContext:
    """Object to handle the context at hand during parsing.

    The root context holds the persistent config which stays
    consistent through a parsing operation. It also produces
    the individual contexts that are used at different layers.

    Each ParseContext maintains a reference to the RootParseContext
    which created it so that it can refer to config within it.
    """

    def __init__(
        self,
        dialect: "Dialect",
        indentation_config: Optional[Dict[str, Any]] = None,
        recurse: bool = True,
    ) -> None:
        """Store persistent config objects."""
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

    @classmethod
    def from_config(
        cls, config: "FluffConfig", **overrides: Dict[str, bool]
    ) -> "RootParseContext":
        """Construct a `RootParseContext` from a `FluffConfig`."""
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

    def __enter__(self) -> "ParseContext":
        """Enter into the context.

        Here we return a basic ParseContext with initial values,
        initialising just the recurse value.

        Note: The RootParseContext is usually entered at the beginning
        of the parse operation as follows::

            with RootParseContext.from_config(...) as ctx:
                parsed = file_segment.parse(parse_context=ctx)
        """
        return ParseContext(root_ctx=self, recurse=self.recurse)

    def __exit__(
        self,
        type: Optional[Type[BaseException]],
        value: Optional[BaseException],
        traceback: Optional["TracebackType"],
    ) -> None:
        """Clear up the context."""
        pass


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

    # We create and destroy many ParseContexts, so we limit the slots
    # to improve performance.
    __slots__ = [
        "match_depth",
        "parse_depth",
        "match_segment",
        "recurse",
        "terminators",
        "_root_ctx",
    ]

    def __init__(self, root_ctx: RootParseContext, recurse: bool = True) -> None:
        self._root_ctx = root_ctx
        self.recurse = recurse
        # The following attributes are only accessible via a copy
        # and not in the init method.
        self.match_segment: Optional[str] = None
        self.match_depth = 0
        self.parse_depth = 0
        self.terminators: List[
            "ExpandedDialectElementType"
        ] = []  # NOTE: Includes inherited parent terminators.

    def __getattr__(self, name: str) -> Any:
        """If the attribute doesn't exist on this, revert to the root."""
        try:
            return getattr(self._root_ctx, name)
        except AttributeError:  # pragma: no cover
            raise AttributeError(
                "Attribute {!r} not found in {!r} or {!r}".format(
                    name, type(self).__name__, type(self._root_ctx).__name__
                )
            )

    def _set_terminators(
        self,
        clear_terminators: bool = False,
        push_terminators: Optional[List["ExpandedDialectElementType"]] = None,
    ):
        _appended = 0
        _terminators = self.terminators  # Retain a reference to the original list.
        if clear_terminators:
            # NOTE: It's really important that we .copy() on the way in, because
            # we don't know what else has a reference to the input list, and
            # we rely a lot in this code on having full control over the
            # list of terminators.
            self.terminators = push_terminators.copy() if push_terminators else []
        elif push_terminators:
            # Yes, inefficient for now.
            for terminator in push_terminators:
                if terminator not in self.terminators:
                    self.terminators.append(terminator)
                    _appended += 1
        return _appended, _terminators

    def _reset_terminators(
        self,
        appended,
        terminators,
        clear_terminators: bool = False,
    ):
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
        push_terminators: Optional[List["ExpandedDialectElementType"]] = None,
    ) -> "ParseContext":
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
    def deeper_parse(self) -> "ParseContext":
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
        push_terminators: Optional[List["ExpandedDialectElementType"]] = None,
    ) -> "ParseContext":
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
        return self._root_ctx._parse_cache.get((loc_key, matcher_key))

    def put_parse_cache(
        self, loc_key: Tuple[Any, ...], matcher_key: str, match: "MatchResult"
    ) -> None:
        """Store a match in the cache for later retrieval."""
        self._root_ctx._parse_cache[(loc_key, matcher_key)] = match

    def increment(self, key: str, default: int = 0) -> None:
        """Increment one of the parse stats by name."""
        self._root_ctx.parse_stats[key] = self._root_ctx.parse_stats.get(key, 0) + 1
