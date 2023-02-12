# Example V1 rules plugin

This example plugin showcases the ability to setup
installable rule plugins using the v1 specification
of that interface.

This requires rules to have codes _only_ and requires
one rule to be implemented at a time. For a more flexible
rules API, consider using the v2 interface as shown
in [plugins/sqlfluff-rules-plugin-v2-example](plugins/sqlfluff-rules-plugin-v2-example).
This interface is supported from version `0.4.0` of
SQLFluff onwards.

Use this specification as a guide for maintaining rules
for versions of sqlfluff up to 2.0.0. If developing new
plugins, we strongly recommend basing your plugin on the
new v2 example.
