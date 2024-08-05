"""Configuration file for the Sphinx documentation builder.

This file only contains a selection of the most common options. For a full
list see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html
"""

import os
import sys

# tomllib is only in the stdlib from 3.11+
if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover
    import toml as tomllib

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

sys.path.append(os.path.abspath("./_ext"))

# Get the global config info as currently stated
# (we use the config file to avoid actually loading any python here)
with open("../../pyproject.toml", "rb") as config_file:
    config = tomllib.load(config_file)
stable_version = config.get("tool.sqlfluff_docs", "stable_version")

# -- Project information -----------------------------------------------------

project = "SQLFluff"
copyright = "2024, Alan Cruickshank"
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
exclude_patterns = [
    # Exclude the partials folder, which is made up of files intended
    # to be included in others.
    "_partials",
]

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
    # GitHub Fork button (points at a broken link, so disabling it)
    "github_banner": False,
    # GitHub star button
    "github_type": "star",
    # Use `"true"` instead of `True` for counting GitHub star, see https://ghbtns.com
    "github_count": "true",
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


def setup(app):
    """Configures the documentation app."""
    app.add_config_value("ultimate_replacements", {}, True)
    app.connect("source-read", ultimate_replace)
