# Example rules plugin

This example plugin showcases the ability to setup installable rule plugins.

This interface is supported from version `0.4.0` of SQLFluff onwards.

For a step by step guide on using custom rule plugins, see the
[guide in the docs](https://docs.sqlfluff.com/en/stable/perma/plugin_guide.html),
or the more technical docs on [developing plugins](https://docs.sqlfluff.com/en/stable/perma/plugin_dev.html).

## Discovery

SQLFluff plugins use [pluggy](https://pluggy.readthedocs.io/en/latest/) to
enable plugin discovery. This relies on the python packaging metadata, and
therefore your plugin *must be installed as a python package* to be found
by SQLFluff. This doesn't mean that you need to make your plugin *public*
because you can install from a local path or private git repo (or any
other location that you can `pip install` from). See the docs links
above for more details.

## Plugin structure

This plugin follows the structure we recommend for any custom plugin:

* `pyproject.toml` defines all the package metadata, including importantly
  the `entry_point` configuration which allows SQLFluff to find your
  plugin once installed. See the [python docs](https://setuptools.pypa.io/en/stable/userguide/entry_point.html)
  for more detail and examples for `setup.cfg` or `setup.py` if you prefer
  that format instead.

* `MANIFEST.in` defines any *non-python* files to include when the package
  is installed. This specifies that we should also include the bundled
  config file for the rule. If you don't specify any new config keys for
  your rule you don't need this.

* `/src/sqlfluff_plugin_example` contains the main source code for the
  plugin. You should change the name to an appropriate one for your plugin
  and ensure that it matches the configuration in `pyproject.toml`. Within
  that folder you should find most of the methods are individually
  documented so you can understand what does what.

* `/test` contains a test suite for this rule. We recommend that you *do*
  create tests for your rule, and so we include an example `pytest` suite
  for our example rule here. This folder is not *necessary* for the rule
  to function, and so the level of test coverage you implement is up to
  you. The test suite can be invoked by running [pytest](https://docs.pytest.org/en/stable/)
  on this folder. Great tests for your rules not only ensure consistent
  functionality over time, but can also be a great tool during initial
  development and serve as examples of how the rule operates to share with
  colleagues when rolling out your rule.
