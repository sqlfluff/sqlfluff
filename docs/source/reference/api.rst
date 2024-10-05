.. _apiref:

Python API
==========

SQLFluff exposes a public api for other python applications to use.
A basic example of this usage is given here, with the documentation
for each of the methods below.


.. literalinclude:: ../../../examples/01_basic_api_usage.py
   :language: python


Simple API commands
-------------------


.. automodule:: sqlfluff
   :members: lint, fix, parse


Advanced API usage
------------------

The simple API presents only a fraction of the functionality present
within the core SQLFluff library. For more advanced use cases, users
can import the :code:`Linter()` and :code:`FluffConfig()` classes from
:code:`sqlfluff.core`. As of version 0.4.0 this is considered as
*experimental only* as the internals may change without warning in any
future release. If you come to rely on the internals of SQLFluff, please
post an issue on GitHub to share what you're up to. This will help shape
a more reliable, tidy and well documented public API for use.

Configuring SQLFluff
~~~~~~~~~~~~~~~~~~~~

You can use :code:`FluffConfig()` class to configure SQLFluff behaviour.


.. literalinclude:: ../../../examples/04_config_overrides.py
   :language: python


Instances of :code:`FluffConfig()` can be created manually, or parsed.


.. literalinclude:: ../../../examples/05_simple_api_config.py
   :language: python


Supported dialects and rules are available through :code:`list_dialects()`
and :code:`list_rules()`.


.. literalinclude:: ../../../examples/03_getting_rules_and_dialects.py
   :language: python


Advanced API reference
~~~~~~~~~~~~~~~~~~~~~~


.. automodule:: sqlfluff.core
   :members: Linter, Lexer, Parser, FluffConfig
