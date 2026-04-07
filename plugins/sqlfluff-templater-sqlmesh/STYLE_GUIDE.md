# SQLFluff + SQLMesh Strict Profile (Project Side)

This profile belongs in the SQLMesh project repository (the repository being
linted), not in the SQLFluff source repository.

## What Failed During Plugin Verification

The plugin itself loaded correctly during manual validation:

- `sqlfluff lint --help` exposed `sqlmesh` as a valid templater.
- A SQL file was linted using `--templater sqlmesh --dialect snowflake`.
- SQLFluff delegated rendering to the SQLMesh templater as expected.

The run then failed during templating, not during plugin discovery or
registration.

Observed failure summary:

- SQLFluff reported that SQLMesh rendering failed for the model.
- SQLMesh indicated local environment or state was ahead of remote state.
- SQLMesh requested `sqlmesh migrate` before rendering could proceed.

This means the blocker is SQLMesh project state consistency, not whether the
plugin is importable or wired into SQLFluff.

## Where To Put It

Create a `.sqlfluff` file at the root of the SQLMesh project.

## Why A Stricter Project-Local Profile Is Needed

- Removes dependency on ad hoc CLI flags, so repeated runs are consistent.
- Guarantees the same templater and dialect locally and in CI.
- Reduces false negatives from linting with the wrong templater.
- Gives the plugin a realistic integration target with repo-specific paths.
- Narrows troubleshooting once configuration is standardized.

The profile does not replace `sqlmesh migrate`. It makes validation reproducible
after project state is brought into sync.

## Recommended Strict Profile

```ini
[sqlfluff]
dialect = snowflake
templater = sqlmesh
max_line_length = 120
exclude_rules =

[sqlfluff:templater:sqlmesh]
project_dir = .

[sqlfluff:rules]
tab_space_size = 4
indent_unit = space

[sqlfluff:rules:layout.long_lines]
ignore_comment_lines = True
ignore_comment_clauses = True

[sqlfluff:rules:references.qualification]
force_enable = True

[sqlfluff:rules:references.consistent]
force_enable = True
```

## Typical SQLMesh-Friendly Excludes

If your SQLMesh repository has generated or non-source SQL paths, add an
`.sqlfluffignore` file at repository root, for example:

```gitignore
.venv/
.dist/
.target/
__pycache__/
*/__pycache__/

# SQLMesh artifacts (adjust to your project)
.cache/
state/
logs/
```

## Validation Steps

1. Ensure SQLMesh project metadata is up to date:
   `sqlmesh migrate`
2. Run lint with project config:
   `sqlfluff lint path/to/model.sql -vv`
3. Lint all SQL files if needed:
   `sqlfluff lint . --ext .sql`

## Development Workflow Example

### 1. Developer Starts Work

No special setup beyond the project-local `.sqlfluff` and optional
`.sqlfluffignore`.

### 2. Check SQL Formatting Accuracy

Run lint manually before commit:

```bash
sqlfluff lint path/to/model.sql -vv
```

The project-local `.sqlfluff` is picked up automatically, so explicit
`--templater` and `--dialect` flags are usually unnecessary.

### 3. Re-Format Automatically

Manual auto-fix:

```bash
sqlfluff fix path/to/model.sql
```

Or run on the project:

```bash
sqlfluff fix . --ext .sql
```

What SQLFluff usually fixes well: spacing, indentation, capitalization,
trailing whitespace, and similar layout issues.

What often requires manual edits: semantic or structural issues where no safe
automated fix exists.

### 4. Exception Handling And Allowed Violations

Use exceptions at the narrowest scope possible.

Line-level:

```sql
SELECT very_long_expression -- noqa: LT05
```

File-level path exclusions via `.sqlfluffignore`:

```gitignore
generated/
```

Project-level rule exclusion in `.sqlfluff`:

```ini
[sqlfluff]
exclude_rules = LT05,ST06
```

Prefer rule tuning and path scoping over broad global disablements.

### 5. PR Checks When Steps 2/3/4 Were Skipped

In GitHub Actions for the SQLMesh project, run a CI lint job that:

1. Detects changed SQL files.
2. Installs SQLFluff + SQLMesh templater plugin.
3. Runs `sqlmesh migrate`.
4. Runs `sqlfluff lint` on changed models.
5. Publishes results as PR annotations (warning or failure).

Advisory mode pattern:

```bash
sqlfluff lint <files> --format github-annotation-native --nofail
```

Enforced mode pattern:

- remove `--nofail`
- configure the CI step to fail on lint violations

## Suggested Additional Testing In A Consumer SQLMesh Project

### Configuration And Registration

- Confirm `sqlmesh` appears in `sqlfluff lint --help` after plugin installation.
- Confirm project-root `.sqlfluff` is picked up without CLI templater or dialect flags.
- Confirm `.sqlfluffignore` excludes non-source directories.

### Rendering Success Paths

- Lint a simple model with no macros.
- Lint a model using SQLMesh macros or environment-aware rendering.
- Lint multiple Snowflake models in one run.

### Failure-Path Behavior

- Reproduce the pre-migration failure and capture SQLFluff error output.
- Re-run after `sqlmesh migrate` and verify failure disappears.
- Test wrong or missing SQLMesh project path in config.
- Test missing SQLMesh dependencies or invalid project state.

### Rule And Fix Behavior

- Validate standard SQLFluff violations are reported on SQLMesh-rendered SQL.
- Run `sqlfluff fix` on safe samples under `sqlmesh` templater.
- Compare lint output: CLI flags versus project-local `.sqlfluff` config.

### CI-Oriented Checks

- Add a smoke command: `sqlmesh migrate` then `sqlfluff lint`.
- Verify same command in a clean environment, not only warmed developer machines.
- Record tested versions: SQLFluff, SQLMesh templater plugin, and SQLMesh.

## Why This Lives In The Project Repository

The templater depends on project-specific SQLMesh state and paths. Keeping
`.sqlfluff` in the SQLMesh repository ensures local and CI linting use the same
environment-aware configuration.
