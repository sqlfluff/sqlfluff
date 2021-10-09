.. _developingpluginsref:

Developing Plugins
==================

*SQLFluff* is extensible through "plugins". We use the `pluggy library`_
to make linting Rules pluggable, which enable users to implement rules that
are just too "organization specific" to be shared, or too platform specific
to be included in the core library.

.. _`pluggy library`: https://pluggy.readthedocs.io/en/latest/

Creating a plugin
-----------------

We have an example plugin in
`sqlfluff/plugins/sqlfluff-plugin-example`_ which you can use as a template
for rules, or the `sqlfluff/plugins/sqlfluff-templater-dbt`_ which you can
use as a template for templater plugins.

Few things to note about plugins:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Currently, only Rules and Templaters can be added through plugins. Over time
we expect more elements of SQLFluff will be extensible with plugins. Each
plugin can implement multiple Rules or Templaters.

We recomment that the name of a plugin should start with *"sqlfluff-"* to be
clear on the purpose of your plugin.

A plugin may need to include a default configuration if its rules
are configurable: use plugin default configurations **only for that reason**!
We advise against overwriting core configurations by using a default
plugin configuration, as there is no mechanism in place to enforce precendence
between the core library configs and plugin configs,
and multiple plugins could clash.

A plugin Rule class name should have the structure:
"Rule_PluginName_L000". The 'L' can be any letter
and is meant to categorize rules; you could use the
letter 'S' to denote rules that enforce security checks
for example.

A plugin Rule code includes the PluginName,
so a rule "Rule_L000" in core will have code "L000",
while "Rule_PluginName_L000" will have code "PluginName_L000".
Codes are used to display errors, they are also used as configuration keys.

We make it easy for plugin developers to test their rules by
exposing a testing library in *sqlfluff.testing*.

.. _`sqlfluff/plugins/sqlfluff-plugin-example`: https://github.com/sqlfluff/sqlfluff/tree/main/plugins/sqlfluff-plugin-example
.. _`sqlfluff/plugins/sqlfluff-templater-dbt`: https://github.com/sqlfluff/sqlfluff/tree/main/plugins/sqlfluff-templater-dbt

Giving feedback
---------------

Would you like to have other parts of *SQLFluff* be "pluggable"?
Tell us about it in a `GitHub issue`_ 😄.

.. _`GitHub issue`: https://github.com/sqlfluff/sqlfluff/issues/new?assignees=&labels=enhancement&template=enhancement.md
