"""An example of a custom rule implemented through the plugin system."""

from sqlfluff.core.plugin import hookimpl
from sqlfluff.core.rules.base import (
    BaseCrawler,
    LintResult,
    LintFix
)
from sqlfluff.core.rules.doc_decorators import (
    document_fix_compatible,
    document_configuration,
)
from typing import Tuple, List
import os.path
from sqlfluff.core.config import ConfigLoader

@hookimpl
def get_rules() -> List[BaseCrawler]:
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
        "forbidden_columns": {
            "definition": "A list of column to forbid"
        },
    }


@document_fix_compatible
@document_configuration
class Rule_Example_L001(BaseCrawler):
    """ORDER BY on these columns is forbidden!

    | **Anti-pattern**
    | Using ORDER BY one some forbidden columns.

    .. code-block::

        SELECT *
        FROM foo
        ORDER BY
            bar,
            baz

    | **Best practice**
    | Do not order by these columns.

    .. code-block::

        SELECT *
        FROM foo
        ORDER BY bar
    """

    # Binary operators behave like keywords too.
    _target_elems: List[Tuple[str, str]] = [("type", "orderby_clause")]
    config_keywords = ["forbidden_columns"]

    def _eval(self, segment, raw_stack, **kwargs):
        """We should not use ORDER BY."""
        if segment.is_type("orderby_clause"):
            for seg in segment.segments:
                col_name = seg.raw.lower()
                if seg.is_type("column_reference") and col_name in self.forbidden_columns:
                    return LintResult(anchor=seg, description=f"Column `{col_name}` not allowed in ORDER BY.")
