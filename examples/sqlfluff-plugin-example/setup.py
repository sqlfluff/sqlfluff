"""Setup file for example plugin."""
from setuptools import setup

setup(
    name="sqlfluff-plugin-example",
    install_requires="sqlfluff",
    entry_points={"sqlfluff": ["example = example"]},
    py_modules=["example"],
)
