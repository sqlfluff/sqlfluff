
from collections import namedtuple

TokenMemory = namedtuple('TokenMemory', ['pos', 'token'], verbose=True)
Token = namedtuple('Token', ['start', 'end', 'terminator'], verbose=True)



class SQLParseError(ValueError):
    pass

print("Hello World!")

# Multi stage parser

## First strip comments, potentially extracting special comments (which start with sqlfluff:)
##   - this also makes comment sections, config sections (a subset of comments) and code sections


class BaseSegment(object):
    type = 'base'

    def __init__(self, raw, segments=None):
        self.raw = raw
        self.segments = segments
    
    def parse(self):
        raise NotImplementedError("parse not implemented on type {0}".format(self.__class__))
    
    def __repr__(self):
        if self.segments:
            return "<{0}: {1!s}>".format(self.__class__.__name__, segments)
        else:
            return "<{0}: {1!r}>".format(self.__class__.__name__, self.raw)


class FileSegment(BaseSegment):
    type = 'file'

    def parse(self):
        # Parsing files involves seperating comment segments and code segments and statements segments

        # Comments override everything unless we're in a string literal
        string_tokens = [
            Token('\'', '\'', None),
            Token('"', '"', None),
            Token('`', '`', None)
        ]

        comment_tokens = [
            Token('/*', '*/', None),
            Token('-- ', None, '\n'),
            Token('#', None, '\n')
        ]

        last_pos = 0
        segment_stack = []
        comment_entry = None
        string_entry = None
        skip = 0
        for pos in range(len(self.raw)):
            if skip > 0:
                skip -= 1
                continue
            forward = raw[pos:]
            if not comment_entry and not string_entry:
                for s in string_tokens:
                    if forward.startswith(s.start):
                        print("Found string start at pos {0}!".format(pos))
                        string_entry = TokenMemory(pos, s)
                        # Don't store the segment, because we're only looking for
                        # strings at this stage so we can ignore "false" comments
                        break
                for c in comment_tokens:
                    if forward.startswith(c.start):
                        print("Found comment start at pos {0}!".format(pos))
                        comment_entry = TokenMemory(pos, c)
                        # check that we have a segment to add
                        if pos - 1 > last_pos:
                            segment_stack.append(CodeSegment(raw[last_pos:pos]))
                            last_pos = pos
                        break
                # print(raw[pos:])
            elif string_entry:
                # We're in a string, just look for the end, of THIS KIND of string
                if string_entry.token.end and forward.startswith(string_entry.token.end):
                    # End of segment
                    # Don't save, remember, we're only looking for comments!
                    string_entry = None
                elif string_entry.token.terminator and forward.startswith(string_entry.token.terminator):
                    # End of segment
                    # Don't save, remember, we're only looking for comments!
                    string_entry = None
            elif comment_entry:
                # We're in a string, just look for the end, of THIS KIND of string
                if comment_entry.token.end and forward.startswith(comment_entry.token.end):
                    # End of segment
                    if pos - 1 > last_pos:
                        etl = len(comment_entry.token.end)
                        segment_stack.append(CommentSegment(raw[last_pos:pos + etl]))
                        last_pos = pos + etl
                        skip = etl
                    comment_entry = None
                elif comment_entry.token.terminator and forward.startswith(comment_entry.token.terminator):
                    # End of segment
                    if pos - 1 > last_pos:
                        segment_stack.append(CommentSegment(raw[last_pos:pos]))
                        last_pos = pos
                    comment_entry = None
            else:
                raise NotImplementedError("Aaargh!")
        # ok we got to the end, what did we finish in?
        if not comment_entry and not string_entry:
            # We ended on a code block. OK
            if len(raw) > last_pos:
                segment_stack.append(CodeSegment(raw[last_pos:len(raw)]))
        elif comment_entry:
            # We ended on a comment block
            # Should it have an ending?
            if comment_entry.token.end:
                raise SQLParseError("Final comment not terminated (Expected {0!r})".format(comment_entry.token.end))
            else:
                segment_stack.append(CommentSegment(raw[last_pos:len(raw)]))
        elif string_entry:
            if string_entry.token.end:
                raise SQLParseError("Final string not terminated (Expected {0!r})".format(string_entry.token.end))
            else:
                raise ValueError("Huh? safiihew")
        else:
            raise ValueError("Huh? eaiuyawren")
        
        self.segments = segment_stack
        return self

class CodeSegment(BaseSegment):
    type = 'code'

    def parse(self):
        return self

class CommentSegment(BaseSegment):
    type = 'comment'

    def parse(self):
        return self






raw = """\
# COMMENT
-- Another Comment
Select A from Sys.dual where a  
-- inline comment
in  ('RED',  /* Inline */  'GREEN','BLUE');
select * from tbl_b; # as another comment
insert into sch.tbl_b
    (col1)
values (123)
"""



tabsize = 4
SEMICOLON = ';'




if __name__ == "__main__":
    print("##### parsing:")
    print(raw)
    fs = FileSegment(raw)
    parsed = fs.parse()
    print(parsed.segments)
