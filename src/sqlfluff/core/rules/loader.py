"""Methods to load rules."""

import os
from glob import glob
from importlib import import_module
from typing import TYPE_CHECKING, List, Type

if TYPE_CHECKING:  # pragma: no cover
    from sqlfluff.core.rules.base import BaseRule


def get_rules_from_path(
    # All rule files are expected in the format of L*.py
    rules_path: str = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../rules", "L*.py")
    ),
    base_module: str = "sqlfluff.rules",
) -> List[Type["BaseRule"]]:
    """Reads all of the Rule classes from a path into a list."""
    # Create a rules dictionary for importing in
    # sqlfluff/src/sqlfluff/core/rules/__init__.py
    rules = []

    for module in sorted(glob(rules_path)):
        # Manipulate the module path to extract the filename without the .py
        rule_id = os.path.splitext(os.path.basename(module))[0]
        # All rule classes are expected in the format of Rule_L*
        rule_class_name = f"Rule_{rule_id}"
        # NOTE: We import the module outside of the try clause to
        # properly catch any import errors.
        rule_module = import_module(f"{base_module}.{rule_id}")
        try:
            rule_class = getattr(rule_module, rule_class_name)
        except AttributeError as e:
            raise AttributeError(
                "Rule classes must be named in the format of Rule_*. "
                f"[{rule_class_name}]"
            ) from e
        # Add the rules to the rules dictionary for
        # sqlfluff/src/sqlfluff/core/rules/__init__.py
        rules.append(rule_class)

    return rules
