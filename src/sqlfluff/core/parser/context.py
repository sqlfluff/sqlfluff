"""The parser context.

This mirrors some of the same design of the flask
context manager. https://flask.palletsprojects.com/en/1.1.x/

The context acts as a way of keeping track of state, references
to common configuration and dialects, logging and also the parse
and match depth of the current operation.
"""

import logging
import uuid
from collections import defaultdict
from contextlib import contextmanager
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterator,
    List,
    NoReturn,
    Optional,
    Sequence,
    Tuple,
)

from tqdm import tqdm

from sqlfluff.core.config import progress_bar_configuration

if TYPE_CHECKING:  # pragma: no cover
    from sqlfluff.core.config import FluffConfig
    from sqlfluff.core.dialects.base import Dialect
    from sqlfluff.core.parser.match_result import MatchResult
    from sqlfluff.core.parser.matchable import Matchable

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
    ) -> None:
        """Initialize a new instance of the class.

        Args:
            dialect (Dialect): The dialect used for parsing.
            indentation_config (Optional[Dict[str, Any]], optional): The indentation
                configuration used by Indent and Dedent to control the intended
                indentation of certain features. Defaults to None.
        """
        self.dialect = dialect
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
        # NOTE: We default to the name `File` which is not
        # particularly informative, does indicate the root segment.
        self.match_segment: str = "File"
        self._match_stack: List[str] = []
        self._parse_stack: List[str] = []
        self.match_depth = 0
        self.parse_depth = 0
        # self.terminators is a tuple to afford some level of isolation
        # and protection from edits to outside the context. This introduces
        # a little more overhead than a list, but we manage this by only
        # copying it when necessary.
        # NOTE: Includes inherited parent terminators.
        self.terminators: Tuple["Matchable", ...] = ()
        # Value for holding a reference to the progress bar.
        self._tqdm: Optional[tqdm[NoReturn]] = None
        # Variable to store whether we're tracking progress. When looking
        # ahead to terminators or suchlike, we set this to False so as not
        # to confuse the progress bar.
        self.track_progress = True
        # The current character, to store where the progress bar is at.
        self._current_char = 0

    @classmethod
    def from_config(cls, config: "FluffConfig") -> "ParseContext":
        """Construct a `ParseContext` from a `FluffConfig`.

        Args:
            config (FluffConfig): The configuration object.

        Returns:
            ParseContext: The constructed ParseContext object.
        """
        indentation_config = config.get_section("indentation") or {}
        try:
            indentation_config = {k: bool(v) for k, v in indentation_config.items()}
        except TypeError:  # pragma: no cover
            raise TypeError(
                "One of the configuration keys in the `indentation` section is not "
                "True or False: {!r}".format(indentation_config)
            )
        return cls(
            dialect=config.get("dialect_obj"),
            indentation_config=indentation_config,
        )

    def _set_terminators(
        self,
        clear_terminators: bool = False,
        push_terminators: Optional[Sequence["Matchable"]] = None,
    ) -> Tuple[int, Tuple["Matchable", ...]]:
        """Set the terminators used in the class.

        This private method sets the terminators used in the class. If
        `clear_terminators` is True and the existing terminators are not
        already cleared, the method clears the terminators. If `push_terminators` is
        provided, the method appends them to the existing terminators if they are not
        already present.

        Args:
            clear_terminators (bool, optional): A flag indicating whether to clear the
                existing terminators. Defaults to False.
            push_terminators (Optional[Sequence["Matchable"]], optional): A sequence of
                `Matchable` objects to be added as terminators.
            Defaults to None.

        Returns:
            Tuple[int, Tuple["Matchable", ...]]: A tuple containing the
            number of terminators appended and the original terminators.
        """
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
        terminators: Tuple["Matchable", ...],
        clear_terminators: bool = False,
    ) -> None:
        """Reset the terminators attribute of the class.

        This method is used to reset the terminators attribute of the
        class. If the clear_terminators parameter is True, the terminators attribute
        is set to the provided terminators. If the clear_terminators parameter is
        False and the appended parameter is non-zero, the terminators attribute is
        trimmed to its original length minus the value of the appended parameter.

        Args:
            appended (int): The number of terminators that were appended.
            terminators (Tuple["Matchable", ...]): The original terminators.
            clear_terminators (bool, optional): If True, clear the terminators attribute
                completely. Defaults to False.
        """
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
        name: str,
        clear_terminators: bool = False,
        push_terminators: Optional[Sequence["Matchable"]] = None,
        track_progress: Optional[bool] = None,
    ) -> Iterator["ParseContext"]:
        """Increment match depth.

        Args:
            name (:obj:`str`): Name of segment we are starting to parse.
                NOTE: This value is entirely used for tracking and logging
                purposes.
            clear_terminators (:obj:`bool`, optional): Whether to force
                clear any inherited terminators. This is useful in structures
                like brackets, where outer terminators shouldn't apply while
                within. Terminators are stashed until we return back out of
                this context.
            push_terminators (:obj:`Sequence` of :obj:`Matchable`): Additional
                terminators to add to the environment while in this context.
            track_progress (:obj:`bool`, optional): Whether to pause progress
                tracking for deeper matches. This avoids having the linting
                progress bar jump forward when performing greedy matches on
                terminators.
        """
        self._match_stack.append(self.match_segment)
        self.match_segment = name
        self.match_depth += 1
        _append, _terms = self._set_terminators(clear_terminators, push_terminators)
        _track_progress = self.track_progress
        if track_progress is False:
            self.track_progress = False
        elif track_progress is True:  # pragma: no cover
            # We can't go from False to True. Raise an issue if not.
            assert self.track_progress is True, "Cannot set tracking from False to True"
        try:
            yield self
        finally:
            self._reset_terminators(
                _append, _terms, clear_terminators=clear_terminators
            )
            self.match_depth -= 1
            # Reset back to old name
            self.match_segment = self._match_stack.pop()
            # Reset back to old progress tracking.
            self.track_progress = _track_progress

    @contextmanager
    def progress_bar(self, last_char: int) -> Iterator["ParseContext"]:
        """Set up the progress bar (if it's not already set up).

        Args:
            last_char (:obj:`int`): The templated character position of the
                final segment in the sequence. This is usually populated
                from the end of `templated_slice` on the final segment.
                We require this on initialising the progress bar so that
                we know how far there is to go as we track progress through
                the file.
        """
        assert not self._tqdm, "Attempted to re-initialise progressbar."
        self._tqdm = tqdm(
            # Progress is character by character in the *templated* file.
            total=last_char,
            desc="parsing",
            miniters=1,
            mininterval=0.2,
            disable=progress_bar_configuration.disable_progress_bar,
            leave=False,
        )

        try:
            yield self
        finally:
            self._tqdm.close()

    def update_progress(self, char_idx: int) -> None:
        """Update the progress bar if configured.

        If progress isn't configured, we do nothing.
        If `track_progress` is false we do nothing.
        """
        if not self._tqdm or not self.track_progress:
            return None
        if char_idx <= self._current_char:
            return None
        self._tqdm.update(char_idx - self._current_char)
        self._current_char = char_idx
        return None

    def stack(self) -> Tuple[Tuple[str, ...], Tuple[str, ...]]:  # pragma: no cover
        """Return stacks as a tuples so that it can't be edited."""
        return tuple(self._parse_stack), tuple(self._match_stack)

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
