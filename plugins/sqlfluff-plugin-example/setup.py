"""Setup file for example plugin."""
from setuptools import find_packages, setup

# Change this name in your plugin, e.g. company name or plugin purpose.
PLUGIN_NAME = "example"

setup(
    name="sqlfluff-plugin-{plugin_name}".format(plugin_name=PLUGIN_NAME),
    include_package_data=True,
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires="sqlfluff>=0.4.0",
    entry_points={"sqlfluff": ["{plugin_name} = {plugin_name}.rules".format(
        plugin_name=PLUGIN_NAME)]},
)
