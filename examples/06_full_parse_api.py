"""Showing how to use the python API to filter SQL files.

This example shows how to use the Linter class to parse,
and then process, SQL scripts. The methods shown can be
very powerful for searching and filtering SQL scripts.
"""

from sqlfluff.core import Linter

# Let's make a SQL script with a few statements in it
sql = """
SELECT 1;
CREATE TABLE tbl (a int, b varchar);
SELECT 100;
INSERT INTO tbl VALUES (1, 'abc');
SELECT 10000;
"""
print("SQL Script: ", repr(sql))

# Call .parse_string() directly on the Linter object.
# The result is a ParsedString object.
linter = Linter(dialect="ansi")
parsed = linter.parse_string(sql)

# Get access to the parsed syntax tree.
tree = parsed.tree

# The root element of the parse tree should be a file segment
assert tree.is_type("file")

# The children of that segment are a mixture of statements
# and separators. Each of those are also segments with the same
# available methods. We can make a list of their raw representations.
sections = [(segment.get_type(), segment.raw) for segment in tree.segments]
assert sections == [
    ("newline", "\n"),
    ("statement", "SELECT 1"),
    ("statement_terminator", ";"),
    ("newline", "\n"),
    ("statement", "CREATE TABLE tbl (a int, b varchar)"),
    ("statement_terminator", ";"),
    ("newline", "\n"),
    ("statement", "SELECT 100"),
    ("statement_terminator", ";"),
    ("newline", "\n"),
    ("statement", "INSERT INTO tbl VALUES (1, 'abc')"),
    ("statement_terminator", ";"),
    ("newline", "\n"),
    ("statement", "SELECT 10000"),
    ("statement_terminator", ";"),
    ("newline", "\n"),
    ("end_of_file", ""),  # There's a final "end of file segment"
]

# There are a few search methods available for filtering, in particular when
# looking for segments of a specific type, when they might not be direct
# siblings of the parent, you can use .recursive_crawl().
# NOTE: In a performance sensitive application, we recommend you limit the
# search depth by setting the `no_recursive_seg_type` option.
select_statements = tree.recursive_crawl("select_statement")
selects = [(segment.get_type(), segment.raw) for segment in select_statements]
assert selects == [
    ("select_statement", "SELECT 1"),
    ("select_statement", "SELECT 100"),
    ("select_statement", "SELECT 10000"),
]

# We could make a file, which only includes these statements by adding back in
# the statement terminators:
filtered_script = ";\n".join(select[1] for select in selects)
assert filtered_script == "SELECT 1;\nSELECT 100;\nSELECT 10000"
print("Filtered SQL Script: ", repr(filtered_script))
