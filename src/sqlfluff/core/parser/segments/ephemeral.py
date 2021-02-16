"""Ephemeral segment definitions."""

from sqlfluff.core.parser.segments.base import BaseSegment


class EphemeralSegment(BaseSegment):
    """A segment which acts like a normal segment, but is ephemeral.

    This segment allows grammars to behave like segments. It behaves like
    a normal segment except that during the `parse` step, it returns its
    contents rather than itself. This means in the final parsed structure
    it no longer exists.
    """

    def parse(self, parse_context):
        """Use the parse grammar to find subsegments within this segment.

        Return the content of the result, rather than itself.
        """
        # Call the usual parse function
        new_self = super().parse(parse_context)
        # Return the content of that result rather than self
        return new_self.segments

    @classmethod
    def make(cls, match_grammar, parse_grammar, name):
        """Make a subclass of the segment using a method.

        Note: This requires a custom make method, because it's a bit different.
        """
        # Now lets make the classname (it indicates the mother class for clarity)
        classname = "EphemeralSegment_{name}".format(name=name)
        # This is the magic, we generate a new class! SORCERY
        newclass = type(
            classname,
            (cls,),
            dict(match_grammar=match_grammar, parse_grammar=parse_grammar),
        )
        # Now we return that class in the abstract. NOT INSTANTIATED
        return newclass
