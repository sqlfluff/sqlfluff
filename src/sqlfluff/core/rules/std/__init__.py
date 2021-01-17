# No docstring here as it would appear in the rules docs.
# Rule definitions for the standard ruleset, dynamically imported from the directory.
# noqa

import os
from importlib import import_module
from glob import glob

rules_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "L*.py")

for module in sorted(glob(rules_path)):
    # Manipulate the module path to extract the filename without the .py
    rule_id = module.split("/")[-1][:-3]
    rule_class_name = f"Rule_{rule_id}"
    rule_class = getattr(
        import_module(f"sqlfluff.core.rules.std.{rule_id}"), rule_class_name
    )
    # Add the rule_classes to the module namespace to be imported in
    # sqlfluff/core/rules/__init__.py
    globals()[rule_class_name] = rule_class
