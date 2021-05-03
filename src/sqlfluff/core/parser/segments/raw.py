"""Raw segment definitions.

This is designed to be the root segment, without
any children, and the output of the lexer.
"""

from sqlfluff.core.parser.segments.base import BaseSegment


class RawSegment(BaseSegment):
    """This is a segment without any subsegments."""

    type = "raw"
    _is_code = False
    _is_comment = False
    _template = "<unset>"
    _classname = "RawSegment"

    def __init__(self, raw, pos_marker, **kwargs):
        self._raw = raw
        self._raw_upper = raw.upper()
        # pos marker is required here
        self.pos_marker = pos_marker
        self._kwargs = kwargs
        for k, v in kwargs.items():
            if not k.startswith("_"):
                k = "_{k}"
            setattr(self, k, v)

    def __repr__(self):
        return "<{0}: ({1}) {2!r}>".format(self._classname, self.pos_marker, self.raw)

    # ################ PUBLIC PROPERTIES

    @property
    def matched_length(self):
        """Return the length of the segment in characters."""
        return len(self._raw)

    @property
    def is_expandable(self):
        """Return true if it is meaningful to call `expand` on this segment."""
        return False

    @property
    def is_code(self):
        """Return True if this segment is code."""
        return self._is_code

    @property
    def is_comment(self):
        """Return True if this segment is a comment."""
        return self._is_comment

    @property
    def raw_upper(self):
        """Make an uppercase string from the segments of this segment."""
        return self._raw_upper

    @property
    def segments(self):
        """Return an empty list of child segments.

        This is in case something tries to iterate on this segment.
        """
        return []

    # ################ CLASS METHODS

    @classmethod
    def make(cls, template, case_sensitive=False, name=None, **kwargs):
        """Make a subclass of the segment using a method."""
        # Let's deal with the template first
        if case_sensitive:
            _template = template
        else:
            _template = template.upper()
        # Use the name if provided otherwise default to the template
        name = name or _template
        # Now lets make the classname (it indicates the mother class for clarity)
        classname = "{0}_{1}".format(name, cls.__name__)
        return RawSegmentFactory(cls, classname, _template, name, **kwargs)

    # ################ INSTANCE METHODS

    def iter_raw_seg(self):
        """Iterate raw segments, mostly for searching."""
        yield self

    def raw_trimmed(self):
        """Return a trimmed version of the raw content."""
        raw_buff = self.raw
        if self.trim_start:
            for seq in self.trim_start:
                if raw_buff.startswith(seq):
                    raw_buff = raw_buff[len(seq) :]
        if self.trim_chars:
            raw_buff = self.raw
            # for each thing to trim
            for seq in self.trim_chars:
                # trim start
                while raw_buff.startswith(seq):
                    raw_buff = raw_buff[len(seq) :]
                # trim end
                while raw_buff.endswith(seq):
                    raw_buff = raw_buff[: -len(seq)]
            return raw_buff
        return raw_buff

    def raw_list(self):
        """Return a list of the raw content of this segment."""
        return [self.raw]

    def _reconstruct(self):
        """Return a string of the raw content of this segment."""
        return self._raw

    def stringify(self, ident=0, tabsize=4, code_only=False):
        """Use indentation to render this segment and its children as a string."""
        preface = self._preface(ident=ident, tabsize=tabsize)
        return preface + "\n"

    def _suffix(self):
        """Return any extra output required at the end when logging.

        NB Override this for specific subclasses if we want extra output.
        """
        return "{0!r}".format(self.raw)

    def edit(self, raw):
        """Create a new segment, with exactly the same position but different content.

        Returns:
            A copy of this object with new contents.

        Used mostly by fixes.

        """
        # return self.__class__(raw=raw, pos_marker=self.pos_marker)
        return RawSegment(
            _classname=self._classname,
            _template=self._template,
            _name=self._name,
            **self._kwargs
        )

    def get_end_pos_marker(self):
        """Return the pos marker at the end of this segment."""
        return self.pos_marker.advance_by(self.raw)

    def get_start_pos_marker(self):
        """Return the pos marker at the start of this segment."""
        return self.pos_marker


class RawSegmentFactory:
    optional = False
    _anti_template = None

    def __init__(self, cls, classname, _template, _name, **kwargs):
        # if classname.startswith("semicolon"):
        #     import pdb; pdb.set_trace()
        self.cls = cls
        self.__name__ = classname
        self._template = _template
        self._name = _name
        self._kwargs = kwargs

    def __repr__(self):
        return f"<{self.cls.__name__}: {self.__name__} {self._template} {self._name} {self._kwargs}"

    def __call__(self, raw, pos_marker):
        result = self.cls(
            raw,
            pos_marker,
            _classname=self.__name__,
            _template=self._template,
            _name=self._name,
            _cls=self,
            **self._kwargs
        )
        return result

    def match(self, segments, parse_context):
        parse_context._factory = self
        result = self.cls.match(segments, parse_context)
        parse_context._factory = None
        return result

    def simple(self, parse_context):
        parse_context._factory = self
        result = self.cls.simple(parse_context)
        parse_context._factory = None
        return result

    def is_optional(self):
        return self.optional

    @property
    def is_meta(self):
        return self.cls.is_meta
