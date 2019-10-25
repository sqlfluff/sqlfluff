""" Code for parsing files """


from .segments_base import BaseSegment
# TODO: Remove this too
from .segments_common import KeywordSegment
from .lexer import Lexer
from .grammar import Delimited, Ref


class FileSegment(BaseSegment):
    """ This is a bit of a special segment in that it does the initial splitting
    and probably defines structure a little further down than it should. """
    type = 'file'
    grammar = Delimited(
        Ref('StatementSegment'),
        delimiter=KeywordSegment.make(';', name="semicolon"),
        code_only=False,
        allow_trailing=True
    )

    @classmethod
    def from_raw(cls, raw):
        """ Take Raw Text and Make a FileSegment using the Lexer """
        lexer = Lexer()
        segments = lexer.lex(raw)
        return cls(segments=segments)
