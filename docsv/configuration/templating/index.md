# Templating Configuration

This section explains how to configure templating for SQL files.

When writing SQL files, users might utilise some kind of templating.
The SQL file itself is written with placeholders which get rendered to proper
SQL at run time.
This can range from very simple placeholder templating to complex Jinja
templating.

SQLFluff supports templated sections in SQL, see [Stage 1, Templater](../../development/architecture#stage-1-the-templater).
This is achieved by the following set of operations:

1. SQLFluff pre-renders the templated SQL
2. SQLFluff applies the lint and fix operations to the rendered file
3. SQLFluff backports the rule violations to the templated section of the SQL.

SQLFluff does not automatically have access to the same environment used in
production template setup. This means it is necessary to either provide that
environment or provide dummy values to effectively render the template and
generate valid SQL. Refer to the templater sections below for details.

SQLFluff natively supports the following templating engines

- [Jinja templater](jinja)
- [Placeholder templater](placeholder)
- [Python templater](python)

Also, SQLFluff has an integration to use `dbt` as a templater.

- [dbt templater](dbt) (via plugin which is covered in a different section).

::: tip NOTE
Templaters may not be able to generate a rendered SQL that cover
the entire raw file.

For example, if the raw SQL uses a `{% if condition %}` block,
the rendered version of the template will only include either the
`{% then %}` or the `{% else %}` block (depending on the
provided configuration for the templater), but not both.

In this case, because SQLFluff linting can only operate on the output
of the templater, some areas of the raw SQL will never be seen by the
linter and will not be covered by lint rules.

This is functionality we hope to support in future.
:::
