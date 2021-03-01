# No docstring here as it would appear in the rules docs.
# Rule definitions for the standard ruleset, dynamically imported from the directory.
# noqa

import os
from importlib import import_module
from glob import glob


def get_rules_from_path(
    # All rule files are expected in the format of L*.py
    rules_path=os.path.join(os.path.abspath(os.path.dirname(__file__)), "L*.py"),
    base_module="sqlfluff.core.rules.std",
):
    """Reads all of the Rule classes from a path into a list."""
    # Create a rules dictionary for importing in sqlfluff/src/sqlfluff/core/rules/__init__.py
    rules = []

    for module in sorted(glob(rules_path)):
        # Manipulate the module path to extract the filename without the .py
        rule_id = os.path.splitext(os.path.basename(module))[0]
        # All rule classes are expected in the format of Rule_L*
        rule_class_name = f"Rule_{rule_id}"
        try:
            rule_class = getattr(
                import_module(f"{base_module}.{rule_id}"), rule_class_name
            )
        except AttributeError as e:
            raise AttributeError(
                "Rule classes must be named in the format of L*."
            ) from e
        # Add the rules to the rules dictionary for sqlfluff/src/sqlfluff/core/rules/__init__.py
        rules.append(rule_class)

    return rules
