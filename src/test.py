from sqlfluff.core.rules.analysis.select import get_select_statement_info
from sqlfluff.api.simple import get_simple_config
from sqlfluff.core.linter import Linter
from sqlfluff.core.rules.base import RuleContext

config = get_simple_config(dialect="redshift")
given_linter = Linter(config=config)
sql_str = """SELECT c[0].col, o FROM customer_orders c, c.c_orders o;"""
parsed_str = given_linter.parse_string(in_str=sql_str, config=config)
rule_set = given_linter.get_ruleset(config=config)
filtered_rule_set = [rule for rule in rule_set if rule.code in ["L027"]]
for rule in filtered_rule_set:
    parent_stack = ()
    raw_stack = ()
    siblings_post = ()
    siblings_pre = ()
    memory = {}
    select_statement = parsed_str.tree.segments[0].segments[0]
    select_info = get_select_statement_info(select_statement, config.get("dialect_obj"))
    output = rule._lint_references_and_aliases(
        select_info.table_aliases,
        select_info.standalone_aliases,
        select_info.reference_buffer,
        select_info.col_aliases,
        select_info.using_cols,
        None,
        config.get("dialect_obj").name,
    )
    print(output)
