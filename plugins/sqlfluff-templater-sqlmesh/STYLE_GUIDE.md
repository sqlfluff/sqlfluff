# SQLMesh Linter Style Guide

This document defines the style conventions enforced by our SQLMesh linting setup in SQLFluff.

## Scope

The SQLMesh plugin itself is a templater (it renders SQLMesh models so SQLFluff can lint them). Style enforcement comes from SQLFluff rules configured for the lint run.

Current enforced/recommended rules (as exercised in plugin tests):

- `LT01`: No trailing whitespace
- `LT02`: Consistent indentation
- `CP01`: Consistent keyword capitalisation
- `ST06`: Avoid wildcard selects (`SELECT *`)

## Rule Summary

### `LT01` - Trailing whitespace

Enforces no trailing spaces at the end of lines.

Bad:

```sql
SELECT
  id,
  name
FROM customers;
```

Good:

```sql
SELECT
  id,
  name
FROM customers;
```

### `LT02` - Indentation

Enforces consistent indentation and alignment in multi-line SQL.

Bad:

```sql
SELECT
id,
    name,
  email
FROM customers;
```

Good:

```sql
SELECT
  id,
  name,
  email
FROM customers;
```

### `CP01` - Capitalisation policy

Enforces a consistent keyword capitalisation policy (typically upper-case SQL keywords).

Bad:

```sql
select id, name from customers;
```

Good:

```sql
SELECT id, name FROM customers;
```

### `ST06` - Disallow wildcard select

Enforces explicit column selection instead of `SELECT *`.

Bad:

```sql
SELECT *
FROM customers;
```

Good:

```sql
SELECT
  customer_id,
  customer_name,
  created_at
FROM customers;
```

## Recommended `.sqlfluff` Configuration

Use this in your SQLMesh project root:

```ini
[sqlfluff]
templater = sqlmesh
dialect = duckdb
rules = LT01,LT02,CP01,ST06

[sqlfluff:templater:sqlmesh]
project_dir = .
```

## Generate Style Output (Lint Report)

Run this command to produce a shareable report of style violations:

```bash
sqlfluff lint models --format yaml > sqlmesh_lint_report.yaml
```

If you want to limit to this style guide rule set explicitly:

```bash
sqlfluff lint models --rules LT01,LT02,CP01,ST06 --format yaml > sqlmesh_style_guide_report.yaml
```

## Auto-fix

Auto-fix applies to fixable issues (for example `LT01` and many `LT02` cases):

```bash
sqlfluff fix models --rules LT01,LT02,CP01,ST06
```

Review fixes before committing.
