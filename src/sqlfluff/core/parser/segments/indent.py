"""Indent and Dedent classes."""

from ..match_wrapper import match_wrapper

from .raw import RawSegment


class Indent(RawSegment):
    """A segment which is empty but indicates where an indent should be.

    This segment is always empty, i.e. it's raw format is '', but it indicates
    the position of a theoretical indent which will be used in linting
    and reconstruction. Even if there is an *actual indent* that occurs
    in the same place this intentionally *won't* capture it, they will just
    be compared later.
    """

    type = "indent"
    _is_code = False
    _template = "<unset>"
    indent_val = 1
    is_meta = True
    _config_rules = None

    @classmethod
    def when(cls, **kwargs):
        """Configure whether this indent/dedent is available given certain rules.

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
    def is_enabled(cls, parse_context):
        """Given a certain parse context, determine if this segment is enabled.

        All rules are assumed to be False if not present in the parse_context,
        and later rules in the config override previous ones.
        """
        # All rules are assumed to be False if not present
        if cls._config_rules is not None:
            config = parse_context.indentation_config or {}
            # This looks like an iteration, but there should only be one.
            for rule, val in cls._config_rules.items():
                conf_val = config.get(rule, False)
                if val == conf_val:
                    return True
                else:
                    return False
        return True

    @staticmethod
    def _suffix():
        """Return any extra output required at the end when logging.

        Meta classess have not much to say here so just stay blank.
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

    def __init__(self, pos_marker):
        """For the indent we override the init method.

        For something without content, the content doesn't make
        sense. The pos_marker, will be matched with the following
        segment, but meta segments are ignored during fixes so it's
        ok in this sense. We need the pos marker later for dealing
        with repairs.
        """
        self._raw = ""
        # We strip the position marker, so that when fixing it's
        # skipped and not considered.
        self.pos_marker = pos_marker.strip()


class Dedent(Indent):
    """A segment which is empty but indicates where an dedent should be.

    This segment is always empty, i.e. it's raw format is '', but it indicates
    the position of a theoretical dedent which will be used in linting
    and reconstruction. Even if there is an *actual dedent* that occurs
    in the same place this intentionally *won't* capture it, they will just
    be compared later.

    """

    indent_val = -1


class NonCodePlaceholder(Indent):
    """A segment which is empty but indicates something should be.

    This segment is always empty, i.e. it's raw format is '', but it indicates
    the position of an element on a line which has been removed. This is used
    to record the position of template blocks, so that their indents are not
    removed during linting.
    """

    type = "placeholder"
    indent_val = 0
