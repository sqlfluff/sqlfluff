"""The structure plugin bundle."""

from sqlfluff.core.plugin import hookimpl
from sqlfluff.core.rules import BaseRule, ConfigInfo


@hookimpl
def get_configs_info() -> dict[str, ConfigInfo]:
    """Get additional rule config validations and descriptions."""
    return {
        "forbid_subquery_in": {
            "validation": ["join", "from", "both"],
            "definition": "Which clauses should be linted for subqueries?",
        },
        "preferred_first_table_in_join_clause": {
            "validation": ["earlier", "later"],
            "definition": (
                "Which table to list first when joining two tables. "
                "Defaults to ``earlier``."
            ),
        },
    }


@hookimpl
def get_rules() -> list[type[BaseRule]]:
    """Get plugin rules.

    NOTE: Rules are imported only on fetch to manage import times
    when rules aren't used.
    """
    from sqlfluff.rules.structure.ST01 import Rule_ST01
    from sqlfluff.rules.structure.ST02 import Rule_ST02
    from sqlfluff.rules.structure.ST03 import Rule_ST03
    from sqlfluff.rules.structure.ST04 import Rule_ST04
    from sqlfluff.rules.structure.ST05 import Rule_ST05
    from sqlfluff.rules.structure.ST06 import Rule_ST06
    from sqlfluff.rules.structure.ST07 import Rule_ST07
    from sqlfluff.rules.structure.ST08 import Rule_ST08
    from sqlfluff.rules.structure.ST09 import Rule_ST09
    from sqlfluff.rules.structure.ST10 import Rule_ST10
    from sqlfluff.rules.structure.ST11 import Rule_ST11

    return [
        Rule_ST01,
        Rule_ST02,
        Rule_ST03,
        Rule_ST04,
        Rule_ST05,
        Rule_ST06,
        Rule_ST07,
        Rule_ST08,
        Rule_ST09,
        Rule_ST10,
        Rule_ST11,
    ]
