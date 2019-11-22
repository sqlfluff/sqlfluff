"""Code for parsing files."""


from .segments_base import BaseSegment
from .lexer import Lexer
from .grammar import Delimited, Ref


class FileSegment(BaseSegment):
    """A segment representing a whole file or script.

    This is a bit of a special segment in that it does the initial splitting
    and probably defines structure a little further down than it should. It
    is also the point at which the lexer is called.
    """
    type = 'file'
    grammar = Delimited(
        Ref('StatementSegment'),
        delimiter=Ref('SemicolonSegment'),
        code_only=False,
        allow_trailing=True
    )

    @classmethod
    def from_raw(cls, raw):
        """Take Raw Text and Make a FileSegment using the Lexer."""
        lexer = Lexer()
        segments = lexer.lex(raw)
        return cls(segments=segments)
