Using GitLab CI Code Quality reports
====================================

When :code:`sqlfluff lint` is run with the :code:`--format gitlab` option, it
produces a `GitLab Code Quality report`_ (the Code Climate issue format).
GitLab can ingest that file and show findings in merge requests.

A typical job writes the report with :code:`--write-output` and publishes it
as a :code:`codequality` artifact:

.. code-block:: yaml

   lint-sql:
     image: sqlfluff/sqlfluff
     script:
       - sqlfluff lint --format gitlab --write-output gl-code-quality-report.json
     artifacts:
       reports:
         codequality: gl-code-quality-report.json

.. _`GitLab Code Quality report`: https://docs.gitlab.com/ci/testing/code_quality/#code-quality-report-format
