.. _diff-quality:

For projects with large amounts of (potentially imperfect) SQL code, the full
SQLFluff output could be very large, which can be distracting -- perhaps the CI
build for a one-line SQL change shouldn't encourage the developer to fix lots of
unrelated quality issues.

To support this use case, SQLFluff integrates with a quality checking tool
called `diff-quality`. By running SQLFluff using `diff-quality` (rather than
running it directly), you can limit the the output to the new or modified SQL
in the branch (aka pull request or PR) containing the proposed changes.

Currently, ``diff-quality`` requires that you are using ``git`` for version
control.

Installation
------------

To install the latest release of the `diff-quality` tool:

.. code:: bash

    pip install diff_cover

NOTE: In order to use the SQLFluff integration, you must install `diff_cover`
version 2.5.0 or higher.

Getting Started
---------------

1. Set the current working directory to a ``git`` repository.

2. In your CI build script, run `diff-quality`, specifying SQLFluff as the
underlying tool:

Example output:

```
$ diff-quality --violations sqlfluff
-------------
Diff Quality
Quality Report: sqlfluff
Diff: origin/master...HEAD, staged and unstaged changes
-------------
sql/audience_size_queries/constraints/_postcondition_check_gdpr_compliance.sql (0.0%):
sql/audience_size_queries/constraints/_postcondition_check_gdpr_compliance.sql:5: Inconsistent capitalisation of unquoted identifiers.
-------------
Total:   1 line
Violations: 1 line
% Quality: 0%
-------------
```

For more information on `diff-quality`, see the
[documentation](https://diff-cover.readthedocs.io/en/latest/). It covers topics
such as:

* Generating HTML reports
* Controlling which branch to compare against (i.e. to determine new/changed lines). The default is `origin/master`.
* Configuring `diff-quality` to return an error code if the quality is too low
* Troubleshooting
