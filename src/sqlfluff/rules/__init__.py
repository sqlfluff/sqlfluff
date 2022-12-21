"""Standard Rules packaged with sqlfluff."""


from sqlfluff.core.plugin.host import get_plugin_manager

# Sphinx effectively runs an import * from this module in rules.rst, so initialise
# __all__ with an empty list before we populate it with the rule names.
__all__ = []

# Iterate through the rules list and register each rule as a global for documentation
for plugin_rules in get_plugin_manager().hook.get_rules():
    for rule in plugin_rules:
        # Add the Rule classes to the module namespace with globals() so that they can
        # be found by Sphinx automodule documentation in rules.rst
        # The result is the same as declaring the classes in this file.
        # Rules coming from the "Example" plugin are excluded from the
        # documentation.
        globals()[rule.__name__] = rule
        # Add the rule class names to __all__ for Sphinx automodule discovery
        __all__.append(rule.__name__)
