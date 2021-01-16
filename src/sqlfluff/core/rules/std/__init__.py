# No docstring here as it would appear in the rules docs.
# Rule definitions for the standard ruleset, dynamically imported from the directory.
# noqa

import os
from glob import glob

rules_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "L*.py")

for module in sorted(glob(rules_path)):
    # Manipulate the module path to extract the filename without the .py
    rule = module.split("/")[-1][:-3]
    cmd = f"from sqlfluff.core.rules.std.{rule} import Rule_{rule}"
    exec(cmd)
