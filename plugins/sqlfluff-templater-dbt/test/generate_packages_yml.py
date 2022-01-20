"""Script used for dbt templater tests."""
import os
import sys
from typing import Optional, Tuple

from jinja2.sandbox import SandboxedEnvironment

DBT_VERSION_TUPLE: Optional[Tuple[int, int]] = None
try:
    from sqlfluff_templater_dbt.templater import DBT_VERSION_TUPLE
except ImportError:
    pass


def main(project_dir):
    """Load Jinja template file expand it write to packages.yml."""
    env = SandboxedEnvironment()
    with open(os.path.join(project_dir, "packages.yml.jinja2")) as f:
        template_str = f.read()
    template = env.from_string(
        template_str, globals=dict(DBT_VERSION_TUPLE=DBT_VERSION_TUPLE)
    )
    expanded = template.render()
    with open(os.path.join(project_dir, "packages.yml"), "w") as f:
        f.write(expanded)


if __name__ == "__main__":
    if DBT_VERSION_TUPLE is not None:
        main(sys.argv[1])
