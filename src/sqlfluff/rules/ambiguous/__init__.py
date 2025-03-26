"""The ambiguous plugin bundle.

NOTE: Yes the title of this bundle is ...ambiguous. 😁
"""

from sqlfluff.core.plugin import hookimpl
from sqlfluff.core.rules import BaseRule, ConfigInfo


@hookimpl
def get_configs_info() -> dict[str, ConfigInfo]:
    """Get additional rule config validations and descriptions."""
    return {
        "fully_qualify_join_types": {
            "validation": ["inner", "outer", "both"],
            "definition": ("Which types of JOIN clauses should be fully qualified?"),
        },
        "group_by_and_order_by_style": {
            "validation": ["consistent", "implicit", "explicit"],
            "definition": (
                "The expectation for using explicit column name references "
                "or implicit positional references."
            ),
        },
    }


@hookimpl
def get_rules() -> list[type[BaseRule]]:
    """Get plugin rules.

    NOTE: Rules are imported only on fetch to manage import times
    when rules aren't used.
    """
    from sqlfluff.rules.ambiguous.AM01 import Rule_AM01
    from sqlfluff.rules.ambiguous.AM02 import Rule_AM02
    from sqlfluff.rules.ambiguous.AM03 import Rule_AM03
    from sqlfluff.rules.ambiguous.AM04 import Rule_AM04
    from sqlfluff.rules.ambiguous.AM05 import Rule_AM05
    from sqlfluff.rules.ambiguous.AM06 import Rule_AM06
    from sqlfluff.rules.ambiguous.AM07 import Rule_AM07
    from sqlfluff.rules.ambiguous.AM08 import Rule_AM08

    return [
        Rule_AM01,
        Rule_AM02,
        Rule_AM03,
        Rule_AM04,
        Rule_AM05,
        Rule_AM06,
        Rule_AM07,
        Rule_AM08,
    ]
