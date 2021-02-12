"""Setup file for example plugin."""
from setuptools import setup

setup(
    name="sqlfluff-plugin-example",
    # TODO: Change me to the first release
    # that includes the pluggy work.
    install_requires="sqlfluff>=0.4.0a3",
    entry_points={"sqlfluff": ["example = example"]},
    py_modules=["example"],
)
