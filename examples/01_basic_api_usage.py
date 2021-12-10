"""This is an example of how to use the simple sqlfluff api."""

import sqlfluff

#  -------- LINTING ----------

my_bad_query = "SeLEct  *, 1, blah as  fOO  from myTable"

# Lint the given string and return an array of violations in JSON representation.
lint_result = sqlfluff.lint(my_bad_query, dialect="bigquery")
# lint_result =
# [
#     {"code": "L010", "line_no": 1, "line_pos": 1, "description": "Keywords must be consistently upper case."}
#     ...
# ]

#  -------- FIXING ----------

# Fix the given string and get a string back which has been fixed.
fix_result_1 = sqlfluff.fix(my_bad_query, dialect="bigquery")
# fix_result_1 = 'SELECT  *, 1, blah AS  foo  FROM mytable\n'

# We can also fix just specific rules.
fix_result_2 = sqlfluff.fix(my_bad_query, rules=["L010"])
# fix_result_2 = 'SELECT  *, 1, blah AS  fOO  FROM myTable'

# Or a subset of rules...
fix_result_3 = sqlfluff.fix(my_bad_query, rules=["L010", "L014"])
# fix_result_3 = 'SELECT  *, 1, blah AS  fOO  FROM mytable'

#  -------- PARSING ----------

# Parse the given string and return a JSON representation of the parsed tree.
parse_result = sqlfluff.parse(my_bad_query)
# parse_result = {'file': {'statement': {...}, 'newline': '\n'}}
