Using `GitHub Actions`_ to Annotate PRs
=======================================

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

.. _`GitHub Actions`: https://github.com/features/actions
.. _`GitHub pull requests`: https://docs.github.com/en/github/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests
.. _`Github workflow commands`: https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions#setting-a-notice-message
.. _`action from yuzutech`: https://github.com/yuzutech/annotations-action
