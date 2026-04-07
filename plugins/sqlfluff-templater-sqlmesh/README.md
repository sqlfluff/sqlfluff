# SQLMesh plugin for SQLFluff

This plugin works with [SQLFluff](https://pypi.org/project/sqlfluff/), the
SQL linter for humans, to correctly parse and compile SQL projects using
[SQLMesh](https://pypi.org/project/sqlmesh/).

For more details on how to use this plugin,
see the [SQLFluff documentation](https://docs.sqlfluff.com/).

## Project-Side Profile And Workflow

The SQLMesh templater plugin belongs in the SQLFluff ecosystem, but the lint
profile belongs in the SQLMesh project repository being linted.

Use [STYLE_GUIDE.md](STYLE_GUIDE.md) for:

- a strict project-local `.sqlfluff` profile for SQLMesh + SQLFluff
- `.sqlfluffignore` patterns for SQLMesh projects
- a practical developer workflow (check, auto-fix, exceptions, CI/PR checks)
- failure-path guidance for SQLMesh state issues (for example when
	`sqlmesh migrate` is required before rendering)
