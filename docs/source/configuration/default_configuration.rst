.. _defaultconfig:

Default Configuration
---------------------

The default configuration is as follows, note the :ref:`builtin_jinja_blocks`
in section *[sqlfluff:templater:jinja:macros]* as referred to above.

.. note::

    This shows the *entire* default config. **We do not recommend that users**
    **copy this whole config as the starter config file for their project**.

    This is for two reasons:

    #. The config file should act as a form of *documentation* for your team.
       A record of what decisions you've made which govern how your format your
       sql. By having a more concise config file, and only defining config settings
       where they differ from the defaults - you are more clearly stating to your
       team what choices you've made.

    #. As the project evolves, the structure of the config file may change
       and we will attempt to make changes as backward compatible as possible.
       If you have not overridden a config setting in your project, we can
       easily update the default config to match your expected behaviour over time.
       We may also find issues with the default config which we can also fix
       in the background. *However*, the longer your local config file, the
       more work it will be to update and migrate your config file between
       major versions.

    If you are starting a fresh project and are looking for a good *starter config*,
    check out the :ref:`starter_config` section above.


.. literalinclude:: ../../../src/sqlfluff/core/default_config.cfg
   :language: cfg
