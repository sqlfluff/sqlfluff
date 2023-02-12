"""Setup file for an example rules plugin."""
from setuptools import find_packages, setup

# Change these names in your plugin, e.g. company name or plugin purpose.
PLUGIN_LOGICAL_NAME = "v2_example"
PLUGIN_ROOT_MODULE = "example_v2"

setup(
    name=f"sqlfluff-plugin-{PLUGIN_LOGICAL_NAME}",
    version="1.0.0",
    include_package_data=True,
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires="sqlfluff>=2.0.0a4",
    entry_points={
        "sqlfluff": [
            f"{PLUGIN_LOGICAL_NAME} = {PLUGIN_ROOT_MODULE}.rules"
        ]
    },
)
