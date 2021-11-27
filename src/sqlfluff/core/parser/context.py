"""The parser context.

This mirrors some of the same design of the flask
context manager. https://flask.palletsprojects.com/en/1.1.x/

The context acts as a way of keeping track of state, references
to common configuration and dialects, logging and also the parse
and match depth of the current operation.
"""

import logging
import uuid

# Get the parser logger
from typing import Dict

parser_logger = logging.getLogger("sqlfluff.parser")


class RootParseContext:
    """Object to handle the context at hand during parsing.

    The root context holds the persistent config which stays
    consistent through a parsing operation. It also produces
    the individual contexts that are used at different layers.

    Each ParseContext maintains a reference to the RootParseContext
    which created it so that it can refer to config within it.
    """

    def __init__(self, dialect, indentation_config=None, recurse=True):
        """Store persistent config objects."""
        self.dialect = dialect
        self.recurse = recurse
        # Indentation config is used by Indent and Dedent and used to control
        # the intended indentation of certain features. Specifically it is
        # used in the Conditional grammar.
        self.indentation_config = indentation_config or {}
        # Initialise the denylist
        self.denylist = ParseDenylist()
        # This is the logger that child objects will latch onto.
        self.logger = parser_logger
        # A uuid for this parse context to enable cache invalidation
        self.uuid = uuid.uuid4()

    @classmethod
    def from_config(cls, config, **overrides: Dict[str, bool]) -> "RootParseContext":
        """Construct a `RootParseContext` from a `FluffConfig`."""
        indentation_config = config.get_section("indentation") or {}
        try:
            indentation_config = {k: bool(v) for k, v in indentation_config.items()}
        except TypeError:  # pragma: no cover
            raise TypeError(
                "One of the configuration keys in the `indentation` section is not True or False: {!r}".format(
                    indentation_config
                )
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

    def __enter__(self):
        """Enter into the context.

        Here we return a basic ParseContext with initial values,
        initialising just the recurse value.

        Note: The RootParseContext is usually entered at the beginning
        of the parse operation as follows::

            with RootParseContext.from_config(...) as ctx:
                parsed = file_segment.parse(parse_context=ctx)
        """
        return ParseContext(root_ctx=self, recurse=self.recurse)

    def __exit__(self, type, value, traceback):
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

    When fetching elements from the context, we first look
    at the top level stack config object and the persistent
    config values (stored as attributes of the ParseContext
    itself).
    """

    # We create a destroy many ParseContexts so we limit the slots
    # to improve performance.
    __slots__ = ["match_depth", "parse_depth", "match_segment", "recurse", "_root_ctx"]

    def __init__(self, root_ctx, recurse=True):
        self._root_ctx = root_ctx
        self.recurse = recurse
        # The following attributes are only accessible via a copy
        # and not in the init method.
        self.match_segment = None
        self.match_depth = 0
        self.parse_depth = 0

    def __getattr__(self, name):
        """If the attribute doesn't exist on this, revert to the root."""
        try:
            return getattr(self._root_ctx, name)
        except AttributeError:  # pragma: no cover
            raise AttributeError(
                "Attribute {!r} not found in {!r} or {!r}".format(
                    name, type(self).__name__, type(self._root_ctx).__name__
                )
            )

    def _copy(self):
        """Mimic the copy.copy() method but restrict only to local vars."""
        ctx = self.__class__(root_ctx=self._root_ctx)
        for key in self.__slots__:
            setattr(ctx, key, getattr(self, key))
        return ctx

    def __enter__(self):
        """Enter into the context.

        For the ParseContext, this just returns itself, because
        we already have the right kind of object.
        """
        return self

    def __exit__(self, type, value, traceback):
        """Clear up the context."""
        pass

    def deeper_match(self):
        """Return a copy with an incremented match depth."""
        ctx = self._copy()
        ctx.match_depth += 1
        return ctx

    def deeper_parse(self):
        """Return a copy with an incremented parse depth."""
        ctx = self._copy()
        if not isinstance(ctx.recurse, bool):  # pragma: no cover TODO?
            ctx.recurse -= 1
        ctx.parse_depth += 1
        ctx.match_depth = 0
        return ctx

    def may_recurse(self):
        """Return True if allowed to recurse."""
        return self.recurse > 1 or self.recurse is True

    def matching_segment(self, name):
        """Set the name of the current matching segment.

        NB: We don't reset the match depth here.
        """
        ctx = self._copy()
        ctx.match_segment = name
        return ctx


class ParseDenylist:
    """Acts as a cache to stop unnecessary matching."""

    def __init__(self):
        self._denylist_struct = {}

    def _hashed_version(self):  # pragma: no cover TODO?
        return {
            k: {hash(e) for e in self._denylist_struct[k]}
            for k in self._denylist_struct
        }

    def check(self, seg_name, seg_tuple):
        """Check this seg_tuple against this seg_name.

        Has this seg_tuple already been matched
        unsuccessfully against this segment name.
        """
        if seg_name in self._denylist_struct:  # pragma: no cover TODO?
            if seg_tuple in self._denylist_struct[seg_name]:
                return True
        return False

    def mark(self, seg_name, seg_tuple):
        """Mark this seg_tuple as not a match with this seg_name."""
        if seg_name in self._denylist_struct:
            self._denylist_struct[seg_name].add(seg_tuple)
        else:
            self._denylist_struct[seg_name] = {seg_tuple}

    def clear(self):
        """Clear the denylist struct."""
        self._denylist_struct = {}
