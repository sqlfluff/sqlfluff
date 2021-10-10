"""Setup file for example plugin."""
from setuptools import find_packages, setup
import configparser


# Get the global config info as currently stated
# (we use the config file to avoid actually loading any python here)
config = configparser.ConfigParser()
config.read(["src/sqlfluff/config.ini"])
version = config.get("sqlfluff", "version")


long_description = """
# dbt plugin for SQLFluff

This plugin works with [SQLFluff](https://pypi.org/project/sqlfluff/), the
SQL linter for humans, to correctly parse and compile SQL projects using
[dbt](https://pypi.org/project/dbt/).
"""


setup(
    name="sqlfluff-templater-dbt",
    version=version,
    include_package_data=True,
    license="MIT License",
    description="Lint your dbt project SQL.",
    long_description=long_description,
    # Make sure pypi is expecting markdown!
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    # Make sure sqlfluff is at least as updated at this plugin.
    # We might break this in the future, but for now while
    # the two are bundled, this makes sense given the release
    # cycles are coupled.
    install_requires=[f"sqlfluff>={version}", "dbt>=0.17"],
    entry_points={"sqlfluff": ["sqlfluff_templater_dbt = sqlfluff_templater_dbt"]},
)
