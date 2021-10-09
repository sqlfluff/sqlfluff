"""Setup file for example plugin."""
from setuptools import find_packages, setup

long_description = """
# dbt plugin for SQLFluff

This plugin works with [SQLFluff](https://pypi.org/project/sqlfluff/), the
SQL linter for humans, to correctly parse and compile SQL projects using
[dbt](https://pypi.org/project/dbt/).
"""


setup(
    name="sqlfluff-templater-dbt",
    version="0.0.1a1",
    include_package_data=True,
    license="MIT License",
    description="Lint your dbt project SQL.",
    long_description=long_description,
    # Make sure pypi is expecting markdown!
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=["sqlfluff>=0.7.0a1", "dbt>=0.17"],
    entry_points={"sqlfluff": ["sqlfluff_templater_dbt = sqlfluff_templater_dbt"]},
)
