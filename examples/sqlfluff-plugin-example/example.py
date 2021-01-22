"""An example of a custom rule implemented through the plugin system."""

from sqlfluff.core.plugin import hookimpl
from sqlfluff.core.rules.base import (
    BaseCrawler,
    LintResult,
)
from sqlfluff.core.rules.doc_decorators import (
    document_fix_compatible,
    document_configuration,
)
from typing import Tuple, List
import os.path
from sqlfluff.core.config import ConfigLoader


@document_fix_compatible
@document_configuration
class Rule_Example_L001(BaseCrawler):
    # TODO: Find a good example!
    """Example rule.

    I fail all the time.
    """

    # Binary operators behave like keywords too.
    _target_elems: List[Tuple[str, str]] = [("type", "keyword")]
    config_keywords = ["capitalisation_policy"]

    def _eval(self, segment, memory, **kwargs):
        """Example rule.

        I fail all the time.
        """
        return LintResult(anchor=segment, description="I just fail.")


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
