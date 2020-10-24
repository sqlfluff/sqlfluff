"""This is an example of how to use the simple sqlfluff api."""

import sqlfluff

#  -------- LINTING ----------

my_bad_query = "SeLEct  *, 1, blah as  fOO  from myTable"

# Lint the given string and get a list of violations found.
result = sqlfluff.lint(my_bad_query, dialect="bigquery")

# result =
# [
#     {"code": "L010", "line_no": 1, "line_pos": 1, "description": "Inconsistent capitalisation of keywords."}
#     ...
# ]

#  -------- FIXING ----------

# Fix the given string and get a string back which has been fixed.
result = sqlfluff.fix(my_bad_query, dialect="bigquery")
# result = 'SELECT  *, 1, blah AS  foo  FROM mytable\n'

# We can also fix just specific rules.
result = sqlfluff.fix(my_bad_query, rules="L010")
# result = 'SELECT  *, 1, blah AS  fOO  FROM myTable'

# Or a subset of rules...
result = sqlfluff.fix(my_bad_query, rules=["L010", "L014"])
# result = 'SELECT  *, 1, blah AS  fOO  FROM mytable'

#  -------- PARSING ----------

parsed = sqlfluff.parse(my_bad_query)

# Get the structure of the query
structure = parsed.to_tuple(show_raw=True, code_only=True)
# structure = ('file', (('statement', (('select_statement', (('select_clause', (('keyword', 'SeLEct'), ...

# Extract certain elements
keywords = [keyword.raw for keyword in parsed.recursive_crawl("keyword")]
# keywords = ['SeLEct', 'as', 'from']
