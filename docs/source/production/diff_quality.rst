.. _diff-quality:

Using SQLFluff on changes using ``diff-quality``
================================================

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
--------------------------------------

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
