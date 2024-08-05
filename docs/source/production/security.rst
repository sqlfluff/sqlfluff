.. _security:

Security Considerations
-----------------------

A full list of `Security Advisories is available on GitHub <https://github.com/sqlfluff/sqlfluff/security/advisories>`_.

Given the context of how SQLFluff is designed to be used, there are three
different tiers of access which users may have access to manipulate how the
tool functions in a secure environment.

#. *Users may have edit access to the SQL code which is being linted*. While
   SQLFluff does not execute the SQL itself, in the process of the
   :ref:`templating step <templater>` (in particular via jinja or dbt),
   certain macros may have the ability to execute arbitrary SQL code (e.g.
   the `dbt run_query macro`_). For the Jinja templater, SQLFluff uses the
   `Jinja2 SandboxedEnvironment`_ to limit the execution on unsafe code. When
   looking to further secure this situation, see below for ways to limit the
   ability of users to import other libraries.

#. *Users may have edit access to the SQLFluff :ref:`config-files`*. In some
   (perhaps, many) environments, the users who can edit SQL files may also
   be able to access and edit the :ref:`config-files`. It's important to note
   that because of :ref:`in_file_config`, that users who can edit SQL files
   which are designed to be linted, will also have access to the vast majority
   of any configuration options available in :ref:`config-files`. This means
   that there is minimal additional protection from restricting access to
   :ref:`config-files` for users who already have access to edit the linting
   target files (as described above).

#. *Users may have access to change how SQLFluff is invoked*. SQLFluff can
   be invoked either as a command line too or via the python API. Typically
   the method is fixed for a given application. When thinking about how to
   restrict the ability of users to call insecure code, SQLFluff aims to
   provide options at the point of invocation. In particular, as described
   above, the primary risk vector for SQLFluff is the macro environment
   as described in :ref:`templateconfig`. To restrict users being able to
   bring arbitrary python methods into sqlfluff via the ``library_path``
   configuration value (see :ref:`jinja_library_templating`), we recommend
   that for secure environments you override this config value either by
   providing an ``override`` option to the :class:`FluffConfig` object if
   using the Python API or via the ``--library-path`` CLI option:

   To disable this option entirely via the CLI:

   .. code-block:: bash

      $ sqlfluff lint my_path --library-path none

   To disable this option entirely via the python API:

   .. literalinclude:: ../../../examples/04_config_overrides.py
      :language: python

.. _`Jinja2 SandboxedEnvironment`: https://jinja.palletsprojects.com/en/3.0.x/sandbox/#jinja2.sandbox.SandboxedEnvironment
.. _`dbt run_query macro`: https://docs.getdbt.com/reference/dbt-jinja-functions/run_query
