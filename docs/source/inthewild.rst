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
  fantastic way to help us maintain our growing repositary of
  `over a thousand queries <https://github.com/HTTPArchive/almanac.httparchive.org/tree/main/sql>`_.
