"""Setup file for example plugin."""
from setuptools import find_packages, setup
from os.path import dirname, join
import configparser


# Get the global config info as currently stated
# (we use the config file to avoid actually loading any python here)
config = configparser.ConfigParser()
config.read([join(dirname(__file__), "../../src/sqlfluff/config.ini")])
version = config.get("sqlfluff", "version")


def read(*names, **kwargs):
    """Read a file and return the contents as a string."""
    return open(
        join(dirname(__file__), *names), encoding=kwargs.get("encoding", "utf8")
    ).read()


setup(
    name="sqlfluff-templater-dbt",
    version=version,
    include_package_data=True,
    license="MIT License",
    description="Lint your dbt project SQL.",
    long_description=read("README.md"),
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
