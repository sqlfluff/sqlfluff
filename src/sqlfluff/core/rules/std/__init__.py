# No docstring here as it would appear in the rules docs.
# Rule definitions for the standard ruleset, dynamically imported from the directory.
# noqa

import os
from importlib import import_module
from glob import glob

# All rule files are expected in the format of L*.py
rules_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "L*.py")

for module in sorted(glob(rules_path)):
    # Manipulate the module path to extract the filename without the .py
    rule_id = os.path.splitext(os.path.basename(module))[0]
    # All rule classes are expected in the format of Rule_L*
    rule_class_name = f"Rule_{rule_id}"
    try:
        rule_class = getattr(
            import_module(f"sqlfluff.core.rules.std.{rule_id}"), rule_class_name
        )
    except ImportError:
        raise (ImportError("Rule classes must be named in the format of L*."))
    # Add the rule_classes to the module namespace with globals() to be imported in
    # sqlfluff/core/rules/__init__.py
    # Sphinx automodule documentation looks at this module (see rules.rst) so
    # this also ensures that all the Rule_* classes are available.
    globals()[rule_class_name] = rule_class
