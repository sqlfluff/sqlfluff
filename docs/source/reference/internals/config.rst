.. _fluffconfig:

:code:`sqlfluff.core.config`: Configuration & ``FluffConfig``
-------------------------------------------------------------

When using the Python API, there are additional options for configuration
beyond those specified in the :ref:`setting_config` section of the main
docs. Internally, SQLFluff uses a consistent
:py:class:`~sqlfluff.core.config.fluffconfig.FluffConfig` class which is
then made accessible to different parts of the tool during linting and fixing.

As described in the :ref:`nesting` section of the configuration docs, multiple
nested documentation files can be used in a project and the result is a
combined config object which contains the resulting union of those files.
Under the hood, this is stored in a dict object, and it's possible get and
set individual values, using
:py:meth:`~sqlfluff.core.config.fluffconfig.FluffConfig.get`
& :py:meth:`~sqlfluff.core.config.fluffconfig.FluffConfig.set_value`, but
also get entire portions of that config dict using
:py:meth:`~sqlfluff.core.config.fluffconfig.FluffConfig.get_section`.

Methods for creating config mappings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When instantiating a :py:class:`~sqlfluff.core.config.fluffconfig.FluffConfig`
object, there are a few options to set specific config values (such as
``dialect`` or ``rules``), but to access the full available set of features
it's best to pass in a :obj:`dict` of the values you want to set.

This config :obj:`dict` is a nested object, where the colon (`:`) characters
from the ``.sqlfluff`` config files, delimit the keys. For example, take the
following config file:

.. code-block:: cfg

    [sqlfluff:rules:capitalisation.keywords]
    capitalisation_policy = lower

This would be represented in the config dict as below. See that the nested
structure has been created by splitting the keys on the colon (`:`) characters:

.. code-block:: python

    configs = {
        "rules":{
            "capitalisation.keywords": {
                "capitalisation_policy": "lower"
            }
        }
    }

The following methods are provided to allow conversion of a selection of file
formats into a consistent mapping object for instantiating a
:py:class:`~sqlfluff.core.config.fluffconfig.FluffConfig` object.

.. autofunction:: sqlfluff.core.config.loader.load_config_string

.. autofunction:: sqlfluff.core.config.loader.load_config_file

.. autofunction:: sqlfluff.core.config.loader.load_config_resource

.. autofunction:: sqlfluff.core.config.loader.load_config_at_path

.. autofunction:: sqlfluff.core.config.loader.load_config_up_to_path

The ``FluffConfig`` object
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: sqlfluff.core.config.fluffconfig.FluffConfig
   :members:
