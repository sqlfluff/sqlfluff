"""Indent and Dedent classes."""

from sqlfluff.core.parser.match_wrapper import match_wrapper
from sqlfluff.core.parser.markers import FilePositionMarker

from sqlfluff.core.parser.segments.raw import RawSegment


class MetaSegment(RawSegment):
    """A segment which is empty but indicates where something should be."""

    type = "meta"
    _is_code = False
    _template = "<unset>"
    indent_val = 0
    is_meta = True
    _config_rules = None

    @classmethod
    def when(cls, **kwargs):
        """Configure whether this meta segment is available given certain rules.

        All we do is override the _config_rules parameter
        for the class.

        _config_rules should be an iterable of tuples (config, True|False)
        which determine whether this class is enabled or not. Later elements
        override earlier ones.
        """
        if len(kwargs) > 1:
            raise ValueError(
                "More than one condition specified for {0!r}. [{1!r}]".format(
                    cls, kwargs
                )
            )
        # Sorcery (but less to than on _ProtoKeywordSegment)
        return type(cls.__name__, (cls,), dict(_config_rules=kwargs))

    @classmethod
    def is_enabled(cls, indent_config):
        """Given a certain parse context, determine if this segment is enabled.

        All rules are assumed to be False if not present in the indent_config,
        and later rules in the config override previous ones.
        """
        # If no config rules are set then it's always enabled.
        if cls._config_rules is not None:
            config = indent_config or {}
            # This looks like an iteration, but there should only be one.
            for rule, val in cls._config_rules.items():
                # Assume False if not set.
                conf_val = config.get(rule, False)
                # Coerce to boolean.
                if val == bool(conf_val):
                    return True
                else:
                    return False
        return True

    @staticmethod
    def _suffix():
        """Return any extra output required at the end when logging.

        Meta classes have not much to say here so just stay blank.
        """
        return ""

    @classmethod
    @match_wrapper()
    def match(cls, segments, parse_context):
        """This will never be called. If it is then we're using it wrong."""
        raise NotImplementedError(
            "{0} has no match method, it should only be used in a Sequence!".format(
                cls.__name__
            )
        )

    def __init__(self, pos_marker=None):
        """For the meta segment we override the init method.

        For something without content, the content doesn't make
        sense. The pos_marker, will be matched with the following
        segment, but meta segments are ignored during fixes so it's
        ok in this sense. We need the pos marker later for dealing
        with repairs.
        """
        self._raw = ""
        self._raw_upper = ""
        # We strip the position marker, so that when fixing it's
        # skipped and not considered. If no position marker is given
        # then give it a fresh one - it will need to be realigned
        # before it's useful.
        if pos_marker:
            self.pos_marker = pos_marker.strip()
        else:
            self.pos_marker = FilePositionMarker()


class Indent(MetaSegment):
    """A segment which is empty but indicates where an indent should be.

    This segment is always empty, i.e. its raw format is '', but it indicates
    the position of a theoretical indent which will be used in linting
    and reconstruction. Even if there is an *actual indent* that occurs
    in the same place this intentionally *won't* capture it, they will just
    be compared later.
    """

    type = "indent"
    indent_val = 1


class Dedent(Indent):
    """A segment which is empty but indicates where an dedent should be.

    This segment is always empty, i.e. its raw format is '', but it indicates
    the position of a theoretical dedent which will be used in linting
    and reconstruction. Even if there is an *actual dedent* that occurs
    in the same place this intentionally *won't* capture it, they will just
    be compared later.

    """

    type = "dedent"
    indent_val = -1


class TemplateSegment(MetaSegment):
    """A segment which is empty but indicates something should be.

    This segment is always empty, i.e. its raw format is '', but it indicates
    the position of an element on a line which has been removed. This is used
    to record the position of template blocks, so that their indents are not
    removed during linting.

    This is used to hold a reference point for code from the source file
    which is removed in the templated version such as loop blocks or comments.
    On initialisation we optionally accept the source string as a kwarg in
    case rules want to lint this down the line.
    """

    type = "placeholder"

    def __init__(self, pos_marker=None, source_str="", block_type=""):
        """Initialise a placeholder with the source code embedded."""
        if not source_str:
            raise ValueError("Cannot instantiate TemplateSegment without a source_str.")
        self.source_str = source_str
        self.block_type = block_type
        # Call the super of the pos_marker.
        super().__init__(pos_marker=pos_marker)

    def _suffix(self):
        """Also output what it's a placeholder for."""
        return "[Type: {0!r}, Raw: {1!r}]".format(self.block_type, self.source_str)
