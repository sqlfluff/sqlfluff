---
layout: home
title: SQLFluff
titleTemplate: The SQL Linter for Humans

hero:
  name: SQLFluff
  text: The SQL Linter for Humans
  tagline: Dialect-flexible and configurable SQL linter
  image:
    src: /sqlfluff-lrg.png
    alt: SQLFluff Logo
  actions:
    - theme: brand
      text: Get Started
      link: /guide/
    - theme: alt
      text: View on GitHub
      link: https://github.com/sqlfluff/sqlfluff

features:
  - icon: 🔧
    title: Dialect Flexible
    details: Supports 25+ SQL dialects including T-SQL, PostgreSQL, BigQuery, Snowflake, and more
  - icon: ⚡
    title: Auto-Fix
    details: Automatically fix many linting violations with a single command
  - icon: 📏
    title: 70+ Rules
    details: Comprehensive linting rules covering style, structure, and best practices
  - icon: 🎨
    title: Configurable
    details: Extensive configuration options to match your team's coding standards
---

## Quick Example

```sql
-- Before linting
SELECT a,b  FROM my_table

-- After sqlfluff fix
SELECT
    a,
    b
FROM my_table
```

## Getting Started

Install SQLFluff with pip:

```bash
pip install sqlfluff
```

Lint your SQL files:

```bash
sqlfluff lint my_query.sql
```

Auto-fix issues:

```bash
sqlfluff fix my_query.sql
```
