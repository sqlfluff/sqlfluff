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

.. note::
   When using ``diff-quality`` with ``.sqlfluff`` :ref:`config-files`, and
   especially together with the :ref:`dbt_templater`, it can be really easy
   to run into issues with file discovery. There are a few steps you can
   take to make it much less likely that this will happen:

   1. ``diff-quality`` needs to be run from the root of your ``git``
      repository (so that it can find the ``git`` metadata).

   2. SQLFluff works best if the bulk of the configuration is done from a
      single ``.sqlfluff`` file, which should be in the root of your
      ``git`` repository.

   3. If using :ref:`dbt_templater`, then either place your ``dbt_project.yml``
      file in the same root folder, or if you put it in a subfolder, then
      only invoke ``diff-quality`` and ``sqlfluff`` from the root and define
      the subfolder that the ``dbt`` project lives in using the ``.sqlfluff``
      config file.

   By aligning the paths of all three, you should be able to achieve a
   robust setup. If each is rooted in different paths if can be very
   difficult to achieve the same result, and the resulting behaviour
   can be difficult to debug.
   
   To debug any issues relating to this setup, we recommend occasionally
   running ``sqlfluff`` directly using the main cli (i.e. calling
   :code:`sqlfluff lint my/project/path`) and check whether that route
   gives you the results you expect. ``diff-quality`` should behave as
   though it's calling the SQLFluff CLI *from the same path that you*
   *invoke* ``diff-quality``.

For more information on ``diff-quality`` and the ``diff_cover`` package, see the
`documentation <https://github.com/Bachmann1234/diff_cover>`_ on their github
repository. It covers topics such as:

* Generating HTML reports
* Controlling which branch to compare against (i.e. to determine new/changed
  lines). The default is ``origin/main``.
* Configuring ``diff-quality`` to return an error code if the quality is
  too low.
* Troubleshooting
