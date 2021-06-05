"""Performance testing on parsing and lexing."""

import timeit

from sqlfluff.core import Lexer, Parser, Linter

# Set up and output the query
sql = "SeLEct  *, 1, blah as  fOO  from myTable"
print("Query: ", repr(sql))


def time_function(func, name, iterations=20):
    """A basic timing function."""
    # Do the timing
    time = timeit.timeit(func, number=iterations) / iterations
    # Output the result
    print(
        "{:<35} {:.6}s [{} iterations]".format(
            f"Time to {name}:",
            time,
            iterations,
        )
    )


# Set up some classes to process the data
lexer = Lexer()
parser = Parser()
linter = Linter()

# Pre-process the lexing step for the parsing step
tokens, _ = lexer.lex(sql)
# Pre-process the parsing step for the linting and parsing step
parsed = parser.parse(tokens)

# Time the steps
time_function(lambda: lexer.lex(sql), name="lex")
time_function(lambda: parser.parse(tokens, recurse=0), name="parse (one level only)")
time_function(lambda: parser.parse(tokens), name="parse (recursive)")
time_function(lambda: linter.lint(parsed), name="lint")
time_function(lambda: linter.fix(parsed), name="fix")
