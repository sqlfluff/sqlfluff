"""Setup file for example plugin."""
from setuptools import find_packages, setup

setup(
    name="sqlfluff-plugin-example",
    include_package_data=True,
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires="sqlfluff>=0.4.0",
    entry_points={"sqlfluff": ["example = example.rules"]},
)
