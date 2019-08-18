
import logging
import re

from .segments_base import (BaseSegment, RawSegment)
from .grammar import (Sequence, GreedyUntil, StartsWith, ContainsOnly,
                      OneOf, Delimited)

# NOTE: There is a concept here, of parallel grammars.
# We use one (slightly more permissive) grammar to MATCH
# and then a more detailed one to PARSE. One is called first,
# then the other - which allows sections of the file to be
# parsed even when others won't.

# Multi stage parser

# First strip comments, potentially extracting special comments (which start with sqlfluff:)
#   - this also makes comment sections, config sections (a subset of comments) and code sections

# Note on SQL Grammar
# https://www.cockroachlabs.com/docs/stable/sql-grammar.html#select_stmt


class KeywordSegment(RawSegment):
    """ The Keyword Segment is a bit special, because while it
    can be instantiated directly, we mostly generate them on the
    fly for convenience. The `make` method is defined on RawSegment
    instead of here, but can be used here too. """

    type = 'keyword'
    _is_code = True
    _template = '<unset>'
    _case_sensitive = False

    @classmethod
    def match(cls, segments, match_depth=0, parse_depth=0):
        """ Keyword implements it's own matching function """
        # If we've been passed the singular, make it a list
        if isinstance(segments, BaseSegment):
            segments = [segments]
        # We only match if it's of length 1, otherwise not
        if len(segments) == 1:
            raw = segments[0].raw
            pos = segments[0].pos_marker
            if cls._case_sensitive:
                raw_comp = raw
            else:
                raw_comp = raw.upper()
            logging.debug("[PD:{0} MD:{1}] (KW) {2}.match considering {3!r} against {4!r}".format(
                parse_depth, match_depth, cls.__name__, raw_comp, cls._template))
            if cls._template == raw_comp:
                return cls(raw=raw, pos_marker=pos),  # Return as a tuple
        else:
            logging.debug("{1} will not match sequence of length {0}".format(len(segments), cls.__name__))
        return None

    @classmethod
    def expected_string(cls):
        return cls._template


class ReSegment(KeywordSegment):
    """ A more flexible matching segment for use of regexes
    USE WISELY """
    @classmethod
    def match(cls, segments, match_depth=0, parse_depth=0):
        """ ReSegment implements it's own matching function,
        we assume that ._template is a r"" string, and is formatted
        for use directly as a regex. """
        # If we've been passed the singular, make it a list
        if isinstance(segments, BaseSegment):
            segments = [segments]
        # Regardless of what we're passed, make a string
        s = ''.join([seg.raw for seg in segments])
        # Deal with case sentitivity
        if not cls._case_sensitive:
            sc = s.upper()
        else:
            sc = s
        if len(s) == 0:
            raise ValueError("Zero length string passed to ReSegment!?")
        logging.debug("[PD:{0} MD:{1}] (RE) {2}.match considering {3!r} against {4!r}".format(
            parse_depth, match_depth, cls.__name__, sc, cls._template))
        # Try the regex
        result = re.match(cls._template, sc)
        if result:
            r = result.group(0)
            # Check that we've fully matched
            if r == sc:
                return cls(raw=s, pos_marker=segments[0].pos_marker)
        return None

    @classmethod
    def expected_string(cls):
        return cls.type


CommaSegment = KeywordSegment.make(',', name='Comma')
DotSegment = KeywordSegment.make('.', name='Dot', type='dot')

NakedIdentifierSegment = ReSegment.make(r"[A-Z0-9_]*", name='Identifier', type='naked_identifier')
# QuotedIdentifierSegment = ReSegment.make(r"(\"|\'|\`)[A-Z0-9_]*(\"|\'|\`)", name='Identifier', type='naked_identifier')

# class QuotedIdentifierSegment(BaseSegment):
#    type = 'quoted_identifier'
#    grammar = Sequence(UnquotedIdentifierSegment, QuotedIdentifierSegment, code_only=False)

# class UnquotedIdentifierSegment(BaseSegment):
#    type = 'unquoted_identifier'
#    grammar = KeywordSegment.make('dummy')


class IdentifierSegment(BaseSegment):
    type = 'identifier'
    grammar = Delimited(OneOf(NakedIdentifierSegment), delimiter=DotSegment, code_only=False)


class ColumnExpressionSegment(BaseSegment):
    type = 'column_expression'
    comment_seperate = True
    grammar = OneOf(IdentifierSegment, code_only=False)  # QuotedIdentifierSegment


class TableExpressionSegment(BaseSegment):
    type = 'table_expression'
    comment_seperate = True
    # match grammar (don't allow whitespace)
    grammar = Delimited(IdentifierSegment, delimiter=DotSegment, code_only=False)


class StatementSeperatorSegment(KeywordSegment):
    type = 'statement_seperator'
    _template = ';'


class SelectTargetGroupStatementSegment(BaseSegment):
    type = 'select_target_group'
    # From here down, comments are printed seperately.
    comment_seperate = True
    match_grammar = GreedyUntil(KeywordSegment.make('from'))
    # We should edit the parse grammar to deal with DISTINCT, ALL or similar
    # parse_grammar = Sequence(GreedyUntil(KeywordSegment.make('from')))


class FromClauseSegment(BaseSegment):
    type = 'from_clause'
    # From here down, comments are printed seperately.
    comment_seperate = True
    # match grammar
    match_grammar = Sequence(KeywordSegment.make('from'), Delimited(TableExpressionSegment, delimiter=CommaSegment))


class SelectStatementSegment(BaseSegment):
    type = 'select_statement'
    # From here down, comments are printed seperately.
    comment_seperate = True
    # match grammar. This one makes sense in the context of knowing that it's
    # definitely a statement, we just don't know what type yet.
    match_grammar = StartsWith(KeywordSegment.make('select'))
    # TODO: Prase grammar needs work
    parse_grammar = Sequence(
        KeywordSegment.make('select'),
        SelectTargetGroupStatementSegment,
        FromClauseSegment.as_optional(),
        # GreedyUntil(KeywordSegment.make('limit'), strict=False, optional=True)
    )


class WithCompoundStatementSegment(BaseSegment):
    type = 'with_compound_statement'
    # From here down, comments are printed seperately.
    comment_seperate = True
    # match grammar
    grammar = StartsWith(KeywordSegment.make('with'))
    # TODO: Re-enable this to parse the segment properly
    # parse_grammar = Sequence(KeywordSegment.make('select'), SelectTargetGroupStatementSegment, GreedyUntil(KeywordSegment.make('limit')))


class InsertStatementSegment(BaseSegment):
    type = 'insert_statement'
    # From here down, comments are printed seperately.
    comment_seperate = True
    grammar = StartsWith(KeywordSegment.make('insert'))


class EmptyStatementSegment(BaseSegment):
    type = 'empty_statement'
    # From here down, comments are printed seperately.
    comment_seperate = True
    grammar = ContainsOnly('comment', 'newline')
    # TODO: At some point - we should lint that these are only
    # allowed at the END - otherwise it's probably a parsing error


class StatementSegment(BaseSegment):
    type = 'statement'
    # From here down, comments are printed seperately.
    comment_seperate = True
    # Let's define a grammar from here on in
    parse_grammar = OneOf(SelectStatementSegment, InsertStatementSegment, EmptyStatementSegment, WithCompoundStatementSegment)
    match_grammar = GreedyUntil(KeywordSegment.make(';', name='semicolon'), strict=False)


class RawCodeSegment(RawSegment):
    type = 'rawcode'

    def parse(self):
        # Split into whitespace, newline and StrippedCode
        whitespace_chars = [' ', '\t']
        newline_chars = ['\n']
        this_pos = self.pos_marker
        segment_stack = []
        started = tuple()  # empty tuple to satisfy the linter (was None)
        last_char = None
        # TODO: Move this code into the FILE parsing routine.
        # TODO: Also make that code better
        for idx, c in enumerate(self.raw):  # enumerate through characters in the raw
            # Keep track of where we've got up to in the string, and keep a ref
            # to the last character.
            if last_char:
                this_pos = this_pos.advance_by(last_char)
            # Save the last char
            last_char = c
            # Check what kind of character we've found
            if c in newline_chars:
                # Are we part way through a segment?
                if started:
                    # Close the segment that we were in if we need to.
                    if started[0] == 'whitespace':
                        segment_stack.append(
                            WhitespaceSegment(
                                self.raw[started[2]:idx],
                                pos_marker=started[1])
                        )
                        started = None
                    elif started[0] == 'code':
                        segment_stack.append(
                            StrippedRawCodeSegment(
                                self.raw[started[2]:idx],
                                pos_marker=started[1])
                        )
                        started = None
                    else:
                        raise ValueError("Unexpected `started` value?!")
                # Regardless whether we needed to CLOSE the previous segment,
                # we should just push this one straight onto the stack, because
                # newlines are always a single char.
                segment_stack.append(
                    NewlineSegment(c, pos_marker=this_pos)
                )
            # Is it whitespace
            elif c in whitespace_chars:
                # Close the segment if we need to, if it's changed
                if started:
                    if started[0] == 'whitespace':
                        # We don't want to reset the whitespace counter!
                        # This is because we're already in a whitespace segment.
                        continue
                    elif started[0] == 'code':
                        segment_stack.append(
                            StrippedRawCodeSegment(
                                self.raw[started[2]:idx],
                                pos_marker=started[1])
                        )
                    else:
                        raise ValueError("Unexpected `started` value?!")
                # Start a new segment on the current character
                started = ('whitespace', this_pos, idx)
            else:
                # This isn't whitespace or a newline
                if started:
                    if started[0] == 'code':
                        # We don't want to reset the code counter!
                        # This is because we're already in a code segment.
                        continue
                    elif started[0] == 'whitespace':
                        segment_stack.append(
                            WhitespaceSegment(
                                self.raw[started[2]:idx],
                                pos_marker=started[1])
                        )
                    else:
                        raise ValueError("Unexpected `started` value?!")
                started = ('code', this_pos, idx)
        # We've got to the end, Have we started without finishing
        if started:
            if started[0] == 'code':
                segment_stack.append(
                    StrippedRawCodeSegment(
                        self.raw[started[2]:],
                        pos_marker=started[1])
                )
            elif started[0] == 'whitespace':
                segment_stack.append(
                    WhitespaceSegment(
                        self.raw[started[2]:],
                        pos_marker=started[1])
                )
            else:
                raise ValueError("Unexpected `started` value?! (on close)")
        # Return the full segment stack
        return segment_stack


class QuotedSegment(RawSegment):
    type = 'quoted'


class StrippedRawCodeSegment(RawSegment):
    type = 'strippedcode'
    _is_code = True


class WhitespaceSegment(RawSegment):
    type = 'whitespace'
    is_whitespace = True


class NewlineSegment(WhitespaceSegment):
    type = 'newline'


class CommentSegment(RawSegment):
    type = 'comment'

    def parse(self):
        # Split into several types of comment? Or just parse as is?
        # Probably parse as is.
        return self
