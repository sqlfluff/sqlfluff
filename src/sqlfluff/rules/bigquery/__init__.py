"""The BigQuery rules plugin bundle.

This plugin bundles linting rules which apply exclusively to BigQuery. At some
point in the future it might be useful to spin this off into a separate
installable python package, but so long as the number of rules remain low, it
makes sense to keep it bundled with SQLFluff core.
"""

from sqlfluff.core.plugin import hookimpl
from sqlfluff.core.rules import BaseRule
from sqlfluff.core.rules.config_info import ConfigInfo


@hookimpl
def get_configs_info() -> dict[str, ConfigInfo]:
    """Get additional rule config validations and descriptions."""
    return {
        "forbid_with_expressions": {
            "validation": [True, False],
            "definition": (
                "If ``True``, flag every BigQuery ``WITH`` expression. "
                "Defaults to ``False``."
            ),
        },
        "writing_style": {
            "validation": ["consistent", "one_liner", "aligned", "indented"],
            "definition": (
                "Layout of chained function calls. With consistent, infer the style "
                "from the first chain and enforce it throughout the file."
            ),
        },
    }


@hookimpl
def get_rules() -> list[type[BaseRule]]:
    """Get plugin rules.

    NOTE: Rules are imported only on fetch to manage import times
    when rules aren't used.
    """
    from sqlfluff.rules.bigquery.BQ01 import Rule_BQ01
    from sqlfluff.rules.bigquery.BQ02 import Rule_BQ02

    return [Rule_BQ01, Rule_BQ02]
