"""The BigQuery-specific rules plugin bundle."""

from sqlfluff.core.plugin import hookimpl
from sqlfluff.core.rules import BaseRule, ConfigInfo


@hookimpl
def get_configs_info() -> dict[str, ConfigInfo]:
    """Get BigQuery rule config validations and descriptions."""
    return {
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
    """Load BigQuery rules only when rules are fetched."""
    from sqlfluff.rules.bigquery.BQ01 import Rule_BQ01

    return [Rule_BQ01]
