"""Setup file for example plugin."""
from setuptools import find_packages, setup
from os.path import dirname, join
import configparser


def read(*names, **kwargs):
    """Read a file and return the contents as a string."""
    return open(
        join(dirname(__file__), *names), encoding=kwargs.get("encoding", "utf8")
    ).read()


setup(
    name="sqlfluff-templater-dbt",
    version="0.7.0a4",
    include_package_data=False,
    license="MIT License",
    description="Lint your dbt project SQL.",
    long_description=read("README.md"),
    # Make sure pypi is expecting markdown!
    long_description_content_type="text/markdown",
    package_dir={"": join(dirname(__file__), "src")},
    packages=find_packages(where="src"),
    # Make sure sqlfluff is at least as updated at this plugin.
    # We might break this in the future, but for now while
    # the two are bundled, this makes sense given the release
    # cycles are coupled.
    install_requires=[f"sqlfluff>=0.7.0a2", "dbt>=0.17"],
    entry_points={"sqlfluff": ["sqlfluff_templater_dbt = sqlfluff_templater_dbt"]},
)
