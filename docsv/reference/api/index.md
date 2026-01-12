# Python API Reference

SQLFluff provides a Python API for programmatic access to linting, fixing, and parsing functionality.

## Modules

| Module | Description |
|--------|-------------|
| [`simple`](./simple) | High-level API for linting, fixing, and parsing SQL |
| [`info`](./info) | Information about available rules and dialects |

## Quick Start

```python
from sqlfluff.api import lint, fix, parse

# Lint SQL
violations = lint("SELECT * FROM tbl", dialect="postgres")

# Fix SQL
fixed_sql = fix("SELECT * FROM tbl", dialect="postgres")

# Parse SQL
tree = parse("SELECT * FROM tbl", dialect="postgres")
```
