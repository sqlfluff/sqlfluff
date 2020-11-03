"""Performance testing on parsing and lexing."""

import timeit

from sqlfluff.core import Lexer, Parser

sql = "SeLEct  *, 1, blah as  fOO  from myTable"

# Set up some classes to process the data
lexer = Lexer()
parser = Parser()

# Pre-process the lexing step for the parsing step
tokens, _ = lexer.lex(sql)

# Time the steps
print("Time to lex: ", timeit.timeit(lambda: lexer.lex(sql), number=100) / 100)
print(
    "Time to parse (one level only): ",
    timeit.timeit(lambda: parser.parse(tokens, recurse=0), number=100) / 100,
)
print(
    "Time to parse (recursive): ",
    timeit.timeit(lambda: parser.parse(tokens), number=20) / 20,
)
