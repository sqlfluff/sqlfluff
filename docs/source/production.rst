.. _production-use:

Production Usage & Security
===========================

SQLFluff is designed to be used both as a utility for developers but also to
be part of `CI/CD`_ pipelines.

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

   .. literalinclude:: ../../examples/04_config_overrides.py
      :language: python

.. _`Jinja2 SandboxedEnvironment`: https://jinja.palletsprojects.com/en/3.0.x/sandbox/#jinja2.sandbox.SandboxedEnvironment
.. _`dbt run_query macro`: https://docs.getdbt.com/reference/dbt-jinja-functions/run_query

Using SQLFluff on a whole sql codebase
--------------------------------------

The `exit code`_ provided by SQLFluff when run as a command line utility is
designed to assist usefulness in deployment pipelines. If no violations
are found then the `exit code`_ will be 0. If violations are found then
a non-zero code will be returned which can be interrogated to find out
more.

- An error code of ``0`` means *operation success*, *no issues found*.
- An error code of ``1`` means *operation success*, *issues found*. For
  example this might mean that a linting issue was found, or that one file
  could not be parsed.
- An error code of ``2`` means an error occurred and the operation could
  not be completed. For example a configuration issue or an internal error
  within SQLFluff.

.. _`CI/CD`: https://en.wikipedia.org/wiki/Continuous_integration
.. _`exit code`: https://shapeshed.com/unix-exit-codes/

.. _diff-quality:

Using SQLFluff on changes using ``diff-quality``
------------------------------------------------

For projects with large amounts of (potentially imperfect) SQL code, the full
SQLFluff output could be very large, which can be distracting -- perhaps the CI
build for a one-line SQL change shouldn't encourage the developer to fix lots
of unrelated quality issues.

To support this use case, SQLFluff integrates with a quality checking tool
called ``diff-quality``. By running SQLFluff using ``diff-quality`` (rather
than running it directly), you can limit the the output to the new or modified
SQL in the branch (aka pull request or PR) containing the proposed changes.

Currently, ``diff-quality`` requires that you are using ``git`` for version
control.

NOTE: Installing SQLFluff automatically installs the ``diff_cover`` package
that provides the ``diff-quality`` tool.

Adding ``diff-quality`` to your builds
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In your CI build script:

1. Set the current working directory to the ``git`` repository containing the
SQL code to be checked.

2. Run ``diff-quality``, specifying SQLFluff as the underlying tool:

.. code-block:: text

    $ diff-quality --violations sqlfluff

The output will look something like:

.. code-block:: text

    -------------
    Diff Quality
    Quality Report: sqlfluff
    Diff: origin/master...HEAD, staged and unstaged changes
    -------------
    sql/audience_size_queries/constraints/_postcondition_check_gdpr_compliance.sql (0.0%):
    sql/audience_size_queries/constraints/_postcondition_check_gdpr_compliance.sql:5: Unquoted Identifiers must be consistently upper case.
    -------------
    Total:   1 line
    Violations: 1 line
    % Quality: 0%
    -------------

These messages are basically the same as those provided directly by SQLFluff,
although the format is a little different. Note that ``diff-quality`` only lists
the line _numbers_, not the character position. If you need the character
position, you will need to run SQLFluff directly.

For more information on ``diff-quality``, see the
`documentation <https://diff-cover.readthedocs.io/en/latest/>`_. It covers topics
such as:

* Generating HTML reports
* Controlling which branch to compare against (i.e. to determine new/changed
  lines). The default is `origin/master`.
* Configuring ``diff-quality`` to return an error code if the quality is
  too low.
* Troubleshooting

.. _using-pre-commit:

Using `pre-commit`_
^^^^^^^^^^^^^^^^^^^

`pre-commit`_ is a framework to manage git "hooks"
triggered right before a commit is made.

A `git hook`_ is a git feature to "fire off custom scripts"
when specific actions occur.

Using `pre-commit`_ with SQLFluff is a good way
to provide automated linting to SQL developers.

With `pre-commit`_, you also get the benefit of
only linting/fixing the files that changed.

SQLFluff comes with two `pre-commit`_ hooks:

* sqlfluff-lint: returns linting errors.
* sqlfluff-fix: attempts to fix rule violations.

.. warning::
   For safety reasons, ``sqlfluff-fix`` by default will not make any fixes in
   files that had templating or parse errors, even if those errors were ignored
   using ``noqa`` or `--ignore``.

   Although it is not advised, you *can* tell SQLFluff to try and fix
   these files by overriding the ``fix_even_unparsable`` setting
   in ``.sqlfluff`` config file or using the ``sqlfluff fix --FIX-EVEN-UNPARSABLE``
   command line option.

   *Overriding this behavior may break your SQL. If you use this override,
   always be sure to review any fixes applied to files with templating or parse
   errors to verify they are okay.*

You should create a file named `.pre-commit-config.yaml`
at the root of your git project, which should look
like this:

.. code-block:: yaml

  repos:
  - repo: https://github.com/sqlfluff/sqlfluff
    rev: |release|
    hooks:
      - id: sqlfluff-lint
        # For dbt projects, this installs the dbt "extras".
        # You will need to select the relevant dbt adapter for your dialect
        # (https://docs.getdbt.com/docs/available-adapters):
        # additional_dependencies: ['<dbt-adapter>', 'sqlfluff-templater-dbt']
      - id: sqlfluff-fix
        # Arbitrary arguments to show an example
        # args: [--rules, "LT02,CP02"]
        # additional_dependencies: ['<dbt-adapter>', 'sqlfluff-templater-dbt']

When trying to use the `dbt templater`_, uncomment the
``additional_dependencies`` to install the extras.
This is equivalent to running ``pip install <dbt-adapter> sqlfluff-templater-dbt``.

You can specify the version of ``dbt-adapter`` used in `pre-commit`_,
for example:

.. code-block:: yaml

   additional_dependencies : ['dbt-bigquery==1.0.0', 'sqlfluff-templater-dbt']

See the list of available `dbt-adapters`_.

Note that you can pass the same arguments available
through the CLI using ``args:``.

Using `GitHub Actions`_ to Annotate PRs
---------------------------------------

There are two way to utilize SQLFluff to annotate Github PRs.

1. When :code:`sqlfluff lint` is run with the :code:`--format github-annotation-native`
   option, it produces output formatted as `Github workflow commands`_ which
   are converted into pull request annotations by Github.

2. When :code:`sqlfluff lint` is run with the :code:`--format github-annotation`
   option, it produces output compatible with this `action from yuzutech`_.
   Which uses Github API to annotate the SQL in `GitHub pull requests`.

.. warning::
   At present (December 2023), limitations put in place by Github mean that only the
   first 10 annotations will be displayed if the first option (using
   :code:`github-annotation-native`) is used. This is a not something that SQLFluff
   can control itself and so we currently recommend using the the second option
   above and the `action from yuzutech`_.

   There is an `open feature request <https://github.com/orgs/community/discussions/68471>`_
   for GitHub Actions which you can track to follow this issue.

For more information and examples on using SQLFluff in GitHub Actions, see the
`sqlfluff-github-actions repository <https://github.com/sqlfluff/sqlfluff-github-actions>`_.

.. _`pre-commit`: https://pre-commit.com/
.. _`git hook`: https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks
.. _`dbt templater`: `dbt-project-configuration`
.. _`GitHub Actions`: https://github.com/features/actions
.. _`GitHub pull requests`: https://docs.github.com/en/github/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests
.. _`Github workflow commands`: https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions#setting-a-notice-message
.. _`dbt-adapters`: https://docs.getdbt.com/docs/available-adapters
.. _`action from yuzutech`: https://github.com/yuzutech/annotations-action
