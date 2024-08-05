.. _using-pre-commit:

Using :code:`pre-commit`
^^^^^^^^^^^^^^^^^^^^^^^^

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

.. _`pre-commit`: https://pre-commit.com/
.. _`git hook`: https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks
.. _`dbt templater`: `dbt-project-configuration`
.. _`dbt-adapters`: https://docs.getdbt.com/docs/available-adapters
