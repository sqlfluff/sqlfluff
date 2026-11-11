# SQLMesh templater

The `sqlmesh` templater lets SQLFluff lint SQL model files in a
[SQLMesh](https://sqlmesh.readthedocs.io/en/stable/) project. It handles the
`MODEL (...)` header separately from the SQL query and uses your SQLMesh project
to resolve macros when needed.

The templater is available as the separate `sqlfluff-templater-sqlmesh` plugin.

## Installation & Configuration

Install the plugin in the same Python environment as SQLFluff and your SQLMesh
project dependencies:

```bash
pip install sqlfluff-templater-sqlmesh
```

This also installs SQLMesh (if you haven't already) and a compatible
version of SQLFluff. You'll still need to install any SQLMesh extras
required by your project's database connection separately if those
aren't already installed (e.g. `sqlmesh[duckdb]` for DuckDB.

In a `.sqlfluff` file in your project root, select the templater and the SQLFluff
dialect matching your model SQL. For example, for a DuckDB project:

```ini
[sqlfluff]
templater = sqlmesh
dialect = duckdb

[sqlfluff:templater:sqlmesh]
project_dir = .
```

Run SQLFluff from that directory, targeting your SQL models:

```bash
sqlfluff lint models/
sqlfluff fix models/
```

Set `templater = sqlmesh` in the configuration loaded from the directory where
you run SQLFluff. The templater cannot be changed in configuration files in
subdirectories. See [Setting Configuration](/configuration/) for details.

### Project settings

The following settings are optional and belong in `[sqlfluff:templater:sqlmesh]`:

| Setting | Description | Default |
| --- | --- | --- |
| `project_dir` | Path to the SQLMesh project directory containing `config.py`, `config.yaml` or `config.yml`. Relative paths are resolved from the current working directory. | `SQLMESH_PROJECT_DIR`, if set, otherwise the current working directory. |
| `config` | Name of the configuration object in SQLMesh's `config.py`, for projects defining multiple configurations. | The `config` object in `config.py`, or the project's YAML configuration. |
| `gateway` | Name of the SQLMesh gateway to use when loading the project. | SQLMesh's default gateway selection. |

For example, to select a configuration object named `local` and a gateway named
`dev` in a project under `./analytics`:

```ini
[sqlfluff:templater:sqlmesh]
project_dir = ./analytics
config = local
gateway = dev
```

An explicit `project_dir` takes precedence over `SQLMESH_PROJECT_DIR`. Setting
`project_dir` does not change which files SQLFluff lints; pass the model paths
to `sqlfluff lint` or `sqlfluff fix` separately.

Configure project variables and macros in SQLMesh itself. The plugin uses the
selected SQLMesh project configuration rather than a
`[sqlfluff:templater:sqlmesh:context]` section. See the
[SQLMesh configuration reference](https://sqlmesh.readthedocs.io/en/stable/reference/configuration/).

## Linting and fixing model SQL

For a model such as:

```sql
MODEL (
    name example.simple_model,
    kind FULL
);

SELECT 1 AS id;
```

SQLFluff lints the `SELECT` statement and reports violations at their positions
in the source file. The `MODEL (...)` header is excluded from linting and fixing.

How much of a query SQLFluff can lint and fix depends on its templating:

- **SQL without macros or Jinja** is linted directly, preserving the original
  formatting and source positions. This does not require loading the SQLMesh
  project context.
- **Macros that resolve to a single inline expression**, such as `@start_ds`,
  are substituted while preserving the surrounding SQL. SQLFluff can lint and
  fix the surrounding SQL without rewriting the macro calls. Project-defined
  Python macros can also use this approach when they resolve inline.
- **More complex macros and Jinja queries** use SQLMesh to render the whole
  query. This includes structural macros such as `@EACH` that expand into
  multiple expressions, and `JINJA_QUERY_BEGIN` blocks. The rendered query is
  treated as a single templated region because it cannot currently be mapped precisely
  to the source.

With the default `ignore_templated_areas = True`, most lint violations in a
whole-query rendering are suppressed. A successful lint run can therefore
report no violations for such a model even though its source has formatting
issues. Setting `ignore_templated_areas = False` can expose violations in the
rendered SQL, but does not restore precise source positions or make those
regions safely fixable.

## Known limitations

- This integration targets SQL model queries. It does not lint Python model
  code or provide dedicated rendering for standalone macro, audit or SQLMesh
  test files. Target `models/` rather than the entire project, or use
  [`.sqlfluffignore`](/configuration/ignoring#sqlfluffignore) to exclude those
  files.
- When the plugin loads a model to resolve templating, it uses SQLMesh's parsed
  statements to separate the query from pre- and post-statements. Those
  statements are excluded where this separation is available.
- Temporal macros such as `@start_ds` and `@end_ds` use representative values
  for linting. These are not a backfill interval, and linting does not exercise
  every possible macro or Jinja branch.
- Models requiring macro or Jinja rendering need a loadable SQLMesh project
  and its dependencies. Project loading or rendering errors are reported as
  templating errors. If your project configuration or macros access a database
  during loading or rendering, the linting environment also needs that access.
