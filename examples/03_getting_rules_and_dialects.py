"""This is an example of how get basic options from sqlfluff."""

import sqlfluff

#  -------- DIALECTS ----------

dialects = sqlfluff.list_dialects()
# dialects = [DialectTuple(label='ansi', name='ansi', inherits_from='nothing'), ...]
dialect_names = [dialect.label for dialect in dialects]
# dialect_names = ["ansi", "snowflake", ...]


#  -------- RULES ----------

rules = sqlfluff.list_rules()
# rules = [
#     RuleTuple(
#         code='Example_LT01',
#         description='ORDER BY on these columns is forbidden!'
#     ),
#     ...
# ]
rule_codes = [rule.code for rule in rules]
# rule_codes = ["LT01", "LT02", ...]
