# dbt plugin for SQLFluff

This plugin works with [SQLFluff](https://pypi.org/project/sqlfluff/), the
SQL linter for humans, to correctly parse and compile SQL projects using
[legacy Python dbt Core 1.x](https://pypi.org/project/dbt-core/).

Use `templater = dbt` with this package. For the Rust dbt v2 runtime, use
[`sqlfluff-templater-dbt2`](../sqlfluff-templater-dbt2/README.md) and
`templater = dbt2` instead. That experimental plugin currently requires a build
containing the render-trace API proposed in
[dbt-labs/dbt#16870](https://github.com/dbt-labs/dbt/pull/16870); stock dbt v2
releases do not yet provide that API.

This package requires `dbt-core>=1.4.1,<2`. If a dbt v2 distribution is present
despite that constraint, the templater reports this guidance before trying to
import legacy compiler internals.

For more details on how to use this plugin,
[see the documentation](https://docs.sqlfluff.com/en/stable/perma/dbt.html).
