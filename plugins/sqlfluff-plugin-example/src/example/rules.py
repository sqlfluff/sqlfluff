"""An example of a custom rule implemented through the plugin system."""

from sqlfluff.core.plugin import hookimpl
from sqlfluff.core.rules.base import (
    BaseRule,
    LintResult,
    RuleContext,
)
from sqlfluff.core.rules.doc_decorators import (
    document_fix_compatible,
    document_configuration,
)
from typing import List
import os.path
from sqlfluff.core.config import ConfigLoader


@hookimpl
def get_rules() -> List[BaseRule]:
    """Get plugin rules."""
    return [Rule_Example_L001]


@hookimpl
def load_default_config() -> dict:
    """Loads the default configuration for the plugin."""
    return ConfigLoader.get_global().load_default_config_file(
        file_dir=os.path.dirname(__file__),
        file_name="plugin_default_config.cfg",
    )


@hookimpl
def get_configs_info() -> dict:
    """Get rule config validations and descriptions."""
    return {
        "forbidden_columns": {"definition": "A list of column to forbid"},
    }


# These two decorators allow plugins
# to be displayed in the sqlfluff docs
@document_fix_compatible
@document_configuration
class Rule_Example_L001(BaseRule):
    """ORDER BY on these columns is forbidden!

    | **Anti-pattern**
    | Using ORDER BY one some forbidden columns.

    .. code-block:: sql

        SELECT *
        FROM foo
        ORDER BY
            bar,
            baz

    | **Best practice**
    | Do not order by these columns.

    .. code-block:: sql

        SELECT *
        FROM foo
        ORDER BY bar
    """

    config_keywords = ["forbidden_columns"]

    def __init__(self, *args, **kwargs):
        """Overwrite __init__ to set config."""
        super().__init__(*args, **kwargs)
        self.forbidden_columns = [
            col.strip() for col in self.forbidden_columns.split(",")
        ]

    def _eval(self, context: RuleContext):
        """We should not use ORDER BY."""
        if context.segment.is_type("orderby_clause"):
            for seg in context.segment.segments:
                col_name = seg.raw.lower()
                if (
                    seg.is_type("column_reference")
                    and col_name in self.forbidden_columns
                ):
                    return LintResult(
                        anchor=seg,
                        description=f"Column `{col_name}` not allowed in ORDER BY.",
                    )
