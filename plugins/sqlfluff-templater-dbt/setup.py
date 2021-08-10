"""Setup file for example plugin."""
from setuptools import find_packages, setup

setup(
    name="sqlfluff-templater-dbt",
    version="0.0.1a1",
    include_package_data=True,
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "sqlfluff>=0.7.0a1",
        "dbt>=0.17"
    ],
    entry_points={
        "sqlfluff": ["sqlfluff_templater_dbt = dbt_templater"]
    },
)
