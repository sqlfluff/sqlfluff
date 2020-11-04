"""Performance testing on parsing and lexing."""

import timeit

from sqlfluff.core import Lexer, Parser

with open("test2.sql") as f:
    sql = f.read()

# #### Lexing
lexer = Lexer()


def lex_string():
    """Lex to tokens."""
    tokens, _ = lexer.lex(sql)
    return tokens


print("Time to lex: ", timeit.timeit(lex_string, number=100) / 100)
# As at 2020-11-02: 0.038s

# Actually lex
tokens = lex_string()

# #### Parsing
parser = Parser()


def parse_tokens():
    """Level 1 parse."""
    # (NB: this won't parse the StatementSegments, only FileSegment)
    return parser.parse(tokens, recurse=0)


print("Time to parse (level 1): ", timeit.timeit(parse_tokens, number=100) / 100)
# As at 2020-11-02: 0.119s


def parse_tokens_full():
    """Full parse."""
    return parser.parse(tokens)


print("Time to parse (Full): ", timeit.timeit(parse_tokens_full, number=20) / 20)
# As at 2020-11-02: 1.221s
