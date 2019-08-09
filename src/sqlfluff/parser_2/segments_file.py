""" Code for parsing files """


from .segments_base import BaseSegment
from .segments_core import (StatementSegment, KeywordSegment)
from .lexer import Lexer
from .grammar import Delimited


class FileSegment(BaseSegment):
    """ This is a bit of a special segment in that it does the initial splitting
    and probably defines structure a little further down than it should. """
    type = 'file'
    grammar = Delimited(
        StatementSegment,
        delimiter=KeywordSegment.make(';', name="semicolon"),
        code_only=False,
        allow_trailing=True
    )

    @classmethod
    def from_raw(cls, raw):
        """ Take Raw Text and Make a FileSegment using the Lexer """
        lexer = Lexer()
        segments = lexer.lex(raw)
        # I think the logic for expanding out into statements should
        # live in the parse function.
        return cls(segments=segments)
