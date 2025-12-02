.. _inthewildref:

SQLFluff in the Wild
====================

Want to find other people who are using SQLFluff in production
use cases? Want to brag about how you're using it? Just want to
show solidarity with the project and provide a testimonial for it?

Just add a section below by raising a PR on GitHub by
`editing this file ✏️ <https://github.com/sqlfluff/sqlfluff/edit/main/docs/source/inthewild.rst>`_.

- SQLFluff in production `dbt <http://www.getdbt.com/>`_ projects at
  `tails.com <https://tails.com>`_. We use the SQLFluff cli as part
  of our CI pipeline in `codeship <https://codeship.com>`_ to enforce
  certain styles in our SQL codebase (with over 650 models) and keep
  code quality high. Contact `@alanmcruickshank <https://github.com/alanmcruickshank>`_.
- `Netlify <https://www.netlify.com>`_'s data team uses SQLFluff with
  `dbt <http://www.getdbt.com/>`_ to keep code quality in more than 350
  models (and growing). Previously, we had our SQL Guidelines defined in
  a site hosted with Netlify, and now we're enforcing these rules in our
  CI workflow thanks to SQLFluff.
- `Drizly's <https://www.drizly.com>`_ analytics team uses SQLFluff with
  `dbt <http://www.getdbt.com/>`_ for over 700 models as part of our CI
  checks in GitHub. Before SQLFluff, we had SQL best practices outlined
  in a google doc and had to manually enforce through PR comments. We're
  now able to enforce much of our style guide automatically through SQLFluff.
- `Petal's <https://www.petalcard.com>`_ data-eng team runs SQLFluff on our 100+ model
  `dbt <http://www.getdbt.com/>`_ project. As a pre-commit hook and as a CI
  check, SQLFluff helps keep our SQL readable and consistent.
- `Surfline <https://www.surfline.com/>`_'s Analytics Engineering team
  implemented SQLFluff as part of our continuous integration (CI) suite across
  our entire `dbt <http://www.getdbt.com/>`_ project (700+ models). We implement
  the CI suite using `GitHub Actions and Workflows <https://docs.github.com/en/actions>`_.
  The benefits of using SQLFluff at Surfline are:

  - The SQL in our dbt models is consistent and easily readable.
  - Our style guide is maintained as :code:`code`, not a README that is rarely
    updated.
  - Reduced burden on Analytics Engineers to remember every single style rule.
  - New Analytics Engineers can quickly see and learn what "good SQL" looks
    like at Surfline and start writing it from day 1.
- The `HTTP Archive <https://httparchive.org>`_ uses SQLFluff to automatically
  check for quality and consistency of code submitted by the many contributors
  to this project. In particular our annual `Web Almanac <https://almanac.httparchive.org>`_
  attracts hundreds of volunteers to help analyse our BigQuery dataset and
  being able automatically lint Pull Requests through GitHub Actions is a
  fantastic way to help us maintain our growing repository of
  `over a thousand queries <https://github.com/HTTPArchive/almanac.httparchive.org/tree/main/sql>`_.
- `Brooklyn Data Co <https://www.brooklyndata.co>`_ has a `dbt_artifacts <https://github.com/brooklyn-data/dbt_artifacts>`_
  dbt package from which runs SQLFluff in CI to lint pull requests
  automatically. It uses the
  `GitHub Actions workflow <https://github.com/sqlfluff/sqlfluff-github-actions/tree/main/menu_of_workflows/surfline>`_
  contributed by Greg Clunies, with annotations on pull requests to make it
  easy for contributors to see where their SQL has failed any rules. See an
  `example pull request with SQLFluff annotations <https://github.com/brooklyn-data/dbt_artifacts/pull/74/files>`_.
- `Markerr <https://www.markerr.com>`_ has tightly integrated SQLFluff into our
  CI/CD process for data model changes and process improvements. Since adopting
  SQLFluff across the organization, the clarity of our SQL code has risen
  dramatically, freeing up review time to focus on deeper data and
  process-specific questions.
- `Symend <https://www.symend.com>`_ has a microservices platform supporting
  our SaaS product. We use SQLFLuff in the CI/CD process of several of our
  data-oriented microservices. Among other things, it validates our database
  migration scripts, deployed using
  `schemachange <https://github.com/Snowflake-Labs/schemachange>`_ and we have
  near-term plans to implement it for our `dbt`_ projects.
- At `CarePay <https://www.carepay.com>`_ we use SQLFLuff to lint and fix all
  our dbt models as well as several other SQL heavy projects. Locally we use
  SQLFluff with pre-commit and have also integrated it into our CI/CD
  pipelines.
- Core Analytics Team from `Typeform <https://www.typeform.com/>`_ and
  `videoask <https://www.videoask.com/>`_ uses SQLFluff in the production
  `dbt <http://www.getdbt.com/>`_ project for building our datawarehouse
  layer for both products:

  - We use it locally in our day to day work, helping us to write cleaner code.
  - We added SQLFluff to our CI processes, so during a PR we can check that any
    new or modified sql file has a consistent and easy-to-read format.
