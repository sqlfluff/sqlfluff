"""An example of a custom rule implemented through the plugin system.

This uses the rules API supported from 2.0.0 onwards. If you require
compatibility with versions prior to that, consider using the v1
interface as shown in `sqlfluff-rules-plugin-v1-example`.
"""

from sqlfluff.core.plugin import hookimpl
from sqlfluff.core.rules import (
    BaseRule,
    LintResult,
    RuleContext,
    RuleManifest,
)
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.core.rules.doc_decorators import (
    document_configuration,
    document_fix_compatible,
    document_groups,
)
from typing import List, Type
import os.path
from sqlfluff.core.config import ConfigLoader


@hookimpl
def get_rules() -> List[Type[BaseRule]]:
    """Get plugin rules."""
    return [Rule_Plugin_v2_Example]


@hookimpl
def load_default_config() -> dict:
    """Loads the default configuration for the plugin."""
    return ConfigLoader.get_global().load_config_file(
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
@document_groups
@document_fix_compatible
@document_configuration
class Rule_Plugin_v2_Example(BaseRule):
    """ORDER BY on these columns is forbidden!

    **Anti-pattern**

    Using ``ORDER BY`` one some forbidden columns.

    .. code-block:: sql

        SELECT *
        FROM foo
        ORDER BY
            bar,
            baz

    **Best practice**

    Do not order by these columns.

    .. code-block:: sql

        SELECT *
        FROM foo
        ORDER BY bar
    """

    config_keywords = ["forbidden_columns"]
    crawl_behaviour = SegmentSeekerCrawler({"orderby_clause"})
    declared_rules = (
        RuleManifest("EX02", "forbidden_columns", "plugin", groups=("all",)),
    )

    def __init__(self, *args, **kwargs):
        """Overwrite __init__ to set config."""
        super().__init__(*args, **kwargs)
        self.forbidden_columns = [
            col.strip() for col in self.forbidden_columns.split(",")
        ]

    def _eval(self, context: RuleContext):
        """We should not ORDER BY forbidden_columns.

        NOTE: _eval() must return a dict if more than one rule
        is declared. Here we just return directly for convenience.
        """
        for seg in context.segment.segments:
            col_name = seg.raw.lower()
            if col_name in self.forbidden_columns:
                return LintResult(
                    anchor=seg,
                    description=f"Column `{col_name}` not allowed in ORDER BY.",
                )
