# Developing Plugins

*SQLFluff* is extensible through "plugins". We use the [pluggy library](https://pluggy.readthedocs.io/en/latest/) to make linting Rules pluggable, which enable users to implement rules that are just too "organization specific" to be shared, or too platform specific to be included in the core library.

::: tip NOTE
We recommend that the module in a plugin which defines all of the hook implementations (anything using the `@hookimpl` decorator) must be able to fully import before any rule implementations are imported. More specifically, SQLFluff must be able to both *import* **and** *run* any implementations of `get_configs_info()` before any plugin rules (i.e. any derivatives of `sqlfluff.core.rules.base.BaseRule`) are *imported*. Because of this, we recommend that rules are defined in a separate module to the root of the plugin and then only imported within the `get_rules()` method.

Importing in the main body of the module was previously our recommendation and so may be the case for versions of some plugins. If one of your plugins does use imports in this way, a warning will be presented, recommending that you update your plugin.

```python{7,8}
# The root module will need to import `hookimpl`, but
# should not yet import the rule definitions for the plugin.
from sqlfluff.core.plugin import hookimpl

@hookimpl
def get_rules():
    # Rules should be imported within the `get_rules` method instead
    from my_plugin.rules import MyRule
    return [MyRule]
```
:::


## Creating a plugin

We have an example plugin in
[sqlfluff/plugins/sqlfluff-plugin-example](https://github.com/sqlfluff/sqlfluff/tree/main/plugins/sqlfluff-plugin-example) which you can use as a template
for rules, or the [sqlfluff/plugins/sqlfluff-templater-dbt](https://github.com/sqlfluff/sqlfluff/tree/main/plugins/sqlfluff-templater-dbt) which you can
use as a template for templater plugins.

## Few things to note about plugins:

Currently, only Rules and Templaters can be added through plugins. Over time we expect more elements of SQLFluff will be extensible with plugins. Each plugin can implement multiple Rules or Templaters.

We recommend that the name of a plugin should start with *`sqlfluff-`* to be clear on the purpose of your plugin.

A plugin may need to include a default configuration if its rules are configurable: use plugin default configurations **only for that reason**! We advise against overwriting core configurations by using a default plugin configuration, as there is no mechanism in place to enforce precedence between the core library configs and plugin configs, and multiple plugins could clash.

A plugin Rule class name should have the structure: `Rule_PluginName_L000`. The 'L' can be any letter and is meant to categorize rules; you could use the letter 'S' to denote rules that enforce security checks for example.

An important thing to note when running custom implemented rules:
Run `pip install -e .`, inside the plugin folder so custom rules in linting are included.

A plugin Rule code includes the PluginName, so a rule `Rule_L000` in core will have code `L000`, while `Rule_PluginName_L000` will have code `PluginName_L000`. Codes are used to display errors, they are also used as configuration keys.

We make it easy for plugin developers to test their rules by exposing a testing library in *sqlfluff.utils.testing*.

## Giving feedback

Would you like to have other parts of *SQLFluff* be "pluggable"?
Tell us about it in a [GitHub issue](https://github.com/sqlfluff/sqlfluff/issues/new?assignees=&labels=enhancement&template=enhancement.md) 😄.
