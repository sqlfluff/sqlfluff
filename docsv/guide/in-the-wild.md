# SQLFluff in the Wild

Want to find other people who are using SQLFluff in production? Want to brag
about how you're using it? Just want to show solidarity with the project and
provide a testimonial?

[Edit this page on GitHub](https://github.com/sqlfluff/sqlfluff/edit/main/docsv/guide/in-the-wild.md)
to add your entry by raising a PR.

---

- SQLFluff in production [dbt](http://www.getdbt.com/) projects at
  [tails.com](https://tails.com). We use the SQLFluff CLI as part of our CI
  pipeline in [Codeship](https://codeship.com) to enforce certain styles in our
  SQL codebase (with over 650 models) and keep code quality high.
  Contact [@alanmcruickshank](https://github.com/alanmcruickshank).

- [Netlify](https://www.netlify.com)'s data team uses SQLFluff with
  [dbt](http://www.getdbt.com/) to keep code quality in more than 350 models
  (and growing). Previously, we had our SQL Guidelines defined in a site hosted
  with Netlify, and now we're enforcing these rules in our CI workflow thanks to
  SQLFluff.

- [Drizly's](https://www.drizly.com) analytics team uses SQLFluff with
  [dbt](http://www.getdbt.com/) for over 700 models as part of our CI checks in
  GitHub. Before SQLFluff, we had SQL best practices outlined in a Google Doc and
  had to manually enforce them through PR comments. We're now able to enforce much
  of our style guide automatically through SQLFluff.

- [Petal's](https://www.petalcard.com) data-eng team runs SQLFluff on our 100+
  model [dbt](http://www.getdbt.com/) project. As a pre-commit hook and as a CI
  check, SQLFluff helps keep our SQL readable and consistent.

- [Surfline](https://www.surfline.com/)'s Analytics Engineering team implemented
  SQLFluff as part of our continuous integration (CI) suite across our entire
  [dbt](http://www.getdbt.com/) project (700+ models), using
  [GitHub Actions](https://docs.github.com/en/actions). The benefits of using
  SQLFluff at Surfline are:
  - The SQL in our dbt models is consistent and easily readable.
  - Our style guide is maintained as code, not a README that is rarely updated.
  - Reduced burden on Analytics Engineers to remember every single style rule.
  - New Analytics Engineers can quickly see and learn what "good SQL" looks like
    at Surfline and start writing it from day 1.

- The [HTTP Archive](https://httparchive.org) uses SQLFluff to automatically
  check for quality and consistency of code submitted by the many contributors to
  this project. In particular our annual [Web Almanac](https://almanac.httparchive.org)
  attracts hundreds of volunteers to help analyse our BigQuery dataset and being
  able to automatically lint Pull Requests through GitHub Actions is a fantastic
  way to help us maintain our growing repository of
  [over a thousand queries](https://github.com/HTTPArchive/almanac.httparchive.org/tree/main/sql).

- [Brooklyn Data Co](https://www.brooklyndata.co) has a
  [dbt_artifacts](https://github.com/brooklyn-data/dbt_artifacts) dbt package
  which runs SQLFluff in CI to lint pull requests automatically, with annotations
  on pull requests to make it easy for contributors to see where their SQL has
  failed any rules.

- [Markerr](https://www.markerr.com) has tightly integrated SQLFluff into our
  CI/CD process for data model changes. Since adopting SQLFluff across the
  organization, the clarity of our SQL code has risen dramatically, freeing up
  review time to focus on deeper data and process-specific questions.

- [Symend](https://www.symend.com) uses SQLFluff in the CI/CD process of several
  data-oriented microservices, validating database migration scripts deployed
  using [schemachange](https://github.com/Snowflake-Labs/schemachange).

- At [CarePay](https://www.carepay.com) we use SQLFluff to lint and fix all our
  dbt models as well as several other SQL-heavy projects. Locally we use SQLFluff
  with pre-commit and have also integrated it into our CI/CD pipelines.

- The Core Analytics Team from [Typeform](https://www.typeform.com/) and
  [VideoAsk](https://www.videoask.com/) uses SQLFluff in their production
  [dbt](http://www.getdbt.com/) project for building the data warehouse layer for
  both products, both locally in day-to-day work and in CI on PRs.
