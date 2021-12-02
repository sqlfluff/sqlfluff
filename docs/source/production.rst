Production Usage
================

SQLFluff is designed to be used both as a utility for developers but also to
be part of `CI/CD`_ pipelines.

Using SQLFluff on a whole sql codebase
--------------------------------------

The `exit code`_ provided by SQLFluff when run as a command line utility is
designed to assist usefulness in deployment pipelines. If no violations
are found then the `exit code`_ will be 0. If violations are found then
a non-zero code will be returned which can be interrogated to find out
more.

- At the moment all error states related to linting return *65*.
- An error as a result of a SQLFluff internal error will return *1*.

.. _`CI/CD`: https://en.wikipedia.org/wiki/Continuous_integration
.. _`exit code`: https://shapeshed.com/unix-exit-codes/

.. _diff-quality:

Using SQLFluff on changes using `diff-quality`
----------------------------------------------

For projects with large amounts of (potentially imperfect) SQL code, the full
SQLFluff output could be very large, which can be distracting -- perhaps the CI
build for a one-line SQL change shouldn't encourage the developer to fix lots
of unrelated quality issues.

To support this use case, SQLFluff integrates with a quality checking tool
called `diff-quality`. By running SQLFluff using `diff-quality` (rather than
running it directly), you can limit the the output to the new or modified SQL
in the branch (aka pull request or PR) containing the proposed changes.

Currently, ``diff-quality`` requires that you are using ``git`` for version
control.

NOTE: Installing SQLFluff automatically installs the `diff_cover` package that
provides the `diff-quality` tool.

Adding `diff-quality` to your builds
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In your CI build script:

1. Set the current working directory to the ``git`` repository containing the
SQL code to be checked.

2. Run `diff-quality`, specifying SQLFluff as the underlying tool:

.. code-block:: bash

    diff-quality --violations sqlfluff

The output will look something like:

.. code-block:: bash

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
although the format is a little different. Note that `diff-quality` only lists
the line _numbers_, not the character position. If you need the character
position, you will need to run SQLFluff directly.

For more information on `diff-quality`, see the
`documentation <https://diff-cover.readthedocs.io/en/latest/>`_. It covers topics
such as:

* Generating HTML reports
* Controlling which branch to compare against (i.e. to determine new/changed
  lines). The default is `origin/master`.
* Configuring `diff-quality` to return an error code if the quality is too low
* Troubleshooting

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
        # args: [--rules, "L003,L014"]
        # additional_dependencies: ['<dbt-adapter>', 'sqlfluff-templater-dbt']

When trying to use the `dbt templater`_, uncomment the
``additional_dependencies`` to install the extras.
This is equivalent to running ``pip install <dbt-adapter> sqlfluff-templater-dbt``.

Note that you can pass the same arguments available
through the CLI using ``args:``.

Using `GitHub Actions`_ to Annotate PRs
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
When `sqlfluff lint` is run with the `--format github-annotation` option, it
produces output compatible with this `action <https://github.com/yuzutech/annotations-action>`_.
You can use this to annotate the SQL in `GitHub pull requests`.

For more information and examples on using SQLFluff in GitHub Actions, see the
`sqlfluff-github-actions repository <https://github.com/sqlfluff/sqlfluff-github-actions>`_.

.. _`pre-commit`: https://pre-commit.com/
.. _`git hook`: https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks
.. _`dbt templater`: `dbt-project-configuration`
.. _`GitHub Actions`: https://github.com/features/actions
.. _`GitHub pull requests`: https://docs.github.com/en/github/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests
