"""Configuration file for the Sphinx documentation builder.

This file only contains a selection of the most common options. For a full
list see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html
"""

import os
import sys
import configparser
from collections import defaultdict

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

sys.path.append(os.path.abspath("./_ext"))

# Get the global config info as currently stated
# (we use the config file to avoid actually loading any python here)
config = configparser.ConfigParser()
config.read(["../../setup.cfg"])
stable_version = config.get("sqlfluff_docs", "stable_version")

# -- Project information -----------------------------------------------------

project = "SQLFluff"
copyright = "2023, Alan Cruickshank"
author = "Alan Cruickshank"

# The full version, including alpha/beta/rc tags
release = stable_version


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    # Autodocumentation from docstrings
    "sphinx.ext.autodoc",
    # Allow Google style docstrings
    "sphinx.ext.napoleon",
    # Documenting click commands
    "sphinx_click.ext",
    # Redirects
    "sphinx_reredirects",
    # SQLFluff domain
    "sqlfluff_domain",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# Master doc
master_doc = "index"

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = False


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "alabaster"
html_favicon = "favicon-fluff.png"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# -- Options for Alabaster Theme ---------------------------------------------

html_theme_options = {
    # Set branch to main (used by Codecov button)
    "badge_branch": "main",
    "logo": "images/sqlfluff-lrg.png",
    # Icon for iOS shortcuts
    "touch_icon": "images/sqlfluff-sm2-sq.png",
    "github_user": "sqlfluff",
    "github_repo": "sqlfluff",
    # GitHub Fork button
    "github_banner": True,
    # GitHub star button
    "github_type": "star",
    # Use `"true"` instead of `True` for counting GitHub star, see https://ghbtns.com
    "github_count": "true",
    # Codecov button
    "codecov_button": True,
}

# -- Options for redirects ---------------------------------------------
# https://documatt.gitlab.io/sphinx-reredirects/usage.html

redirects = {
    # There's an old link to /indentation in config files.
    # That should point to the layout section now.
    "indentation": "layout.html#configuring-indent-locations",
    "architecture": "internals.html#architecture",
}


def ultimate_replace(app, docname, source):
    """Replaces variables in docs, including code blocks.

    From: https://github.com/sphinx-doc/sphinx/issues/4054#issuecomment-329097229
    """
    result = source[0]
    for key in app.config.ultimate_replacements:
        result = result.replace(key, app.config.ultimate_replacements[key])
    source[0] = result


ultimate_replacements = {"|release|": release}

##########################################
# Generate rule documentation dynamically.
##########################################

autogen_header = """..
    NOTE: This file is generated by the conf.py script.
    Don't edit this by hand


"""

table_header = """
+------------------------------------------+--------------------------------------------------+------------------------------+--------------------+
| Bundle                                   | Rule Name                                        | Code                         | Aliases            |
+==========================================+==================================================+==============================+====================+
"""

# Extract all the rules.
from sqlfluff.core.plugin.host import get_plugin_manager

rule_bundles = defaultdict(list)
for plugin_rules in get_plugin_manager().hook.get_rules():
    for rule in plugin_rules:
        _bundle_name = rule.name.split(".")[0]
        rule_bundles[_bundle_name].append(rule)

# Write them into the table. Bundle by bundle.
with open("rules/ruletable.rst", "w", encoding="utf8") as f:
    f.write(autogen_header)
    f.write(table_header)
    for bundle in sorted(rule_bundles.keys()):
        # Set the bundle name to the ref.
        _bundle_name = f":doc:`/rules/bundles/{bundle}`"
        for idx, rule in enumerate(rule_bundles[bundle]):
            aliases = ", ".join(rule.aliases[:3]) + (
                "," if len(rule.aliases) > 3 else ""
            )
            name_ref = f":sqlfluff:ref:`{rule.name}`"
            code_ref = f":sqlfluff:ref:`{rule.code}`"
            f.write(
                f"| {_bundle_name : <40} | {name_ref : <48} | {code_ref : <28} | {aliases : <18} |\n"
            )

            j = 3
            while True:
                if not rule.aliases[j:]:
                    break
                aliases = ", ".join(rule.aliases[j : j + 3]) + (
                    "," if len(rule.aliases[j:]) > 3 else ""
                )
                f.write(f"|{' ' * 42}|{' ' * 50}|{' ' * 30}| {aliases : <18} |\n")
                j += 3

            if idx + 1 < len(rule_bundles[bundle]):
                f.write(f"|{' ' * 42}+{'-' * 50}+{'-' * 30}+{'-' * 20}+\n")
            else:
                f.write(f"+{'-' * 42}+{'-' * 50}+{'-' * 30}+{'-' * 20}+\n")
            # Unset the bundle name so we don't repeat it.
            _bundle_name = ""
    f.write("\n\n")


# Write each of the summary files.
for bundle in sorted(rule_bundles.keys()):
    with open(f"rules/bundles/{bundle}.rst", "w", encoding="utf8") as f:
        f.write(autogen_header)
        if "sql" in bundle:
            # This accounts for things like "TSQL"
            header_name = bundle.upper()
        else:
            header_name = bundle.capitalize()
        f.write(
            f".. _bundle_{bundle}:\n\n"
            f"{header_name} bundle\n"
            f"{'=' * (len(bundle) + 7)}\n\n"
        )
        for rule in rule_bundles[bundle]:
            f.write(
                f".. sqlfluff:rule:: {rule.code}\n"
                f"                   {rule.name}\n\n"
            )
            # Separate off the heading so we can bold it.
            heading, _, doc_body = rule.__doc__.partition("\n")
            underline_char = '"'
            f.write(f"    {heading}\n")
            f.write(f"    {underline_char * len(heading)}\n\n")
            f.write("    " + doc_body)
            f.write("\n\n")


def setup(app):
    """Configures the documentation app."""
    app.add_config_value("ultimate_replacements", {}, True)
    app.connect("source-read", ultimate_replace)
