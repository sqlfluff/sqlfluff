# Dialect Development - AI Assistant Instructions

This file provides guidance for developing and extending SQL dialect support in SQLFluff.

## Overview

SQLFluff supports 25+ SQL dialects through an inheritance-based system. Each dialect extends the ANSI base dialect and overrides specific grammar segments to match the target SQL variant's syntax.

## Dialect Architecture

### Inheritance Hierarchy

```
ANSI (base) ← All dialects inherit from here
├── T-SQL (Microsoft SQL Server)
├── PostgreSQL
│   └── Redshift (extends PostgreSQL)
├── MySQL
│   └── MariaDB (extends MySQL)
├── BigQuery
├── Snowflake
└── ... (20+ more dialects)
```

### File Organization

```
src/sqlfluff/dialects/
├── dialect_ansi.py              # Base ANSI SQL dialect
├── dialect_tsql.py              # T-SQL (SQL Server)
├── dialect_postgres.py          # PostgreSQL
├── dialect_bigquery.py          # Google BigQuery
├── dialect_snowflake.py         # Snowflake
├── ...
├── dialect_ansi_keywords.py     # ANSI reserved/unreserved keywords
├── dialect_tsql_keywords.py     # T-SQL keywords
└── dialect_instructions/    # Per-dialect agent instructions (optional)
    ├── tsql.md
    ├── postgres.md
    └── ...
```

## Creating/Extending a Dialect

### Basic Dialect Structure

```python
"""The T-SQL (Microsoft SQL Server) dialect."""

from sqlfluff.core.dialects import load_raw_dialect
from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.parser.grammar import (
    Sequence, OneOf, Ref, Bracketed, Delimited, AnyNumberOf, Optional
)

# Load parent dialect
ansi_dialect = load_raw_dialect("ansi")

# Create new dialect as copy
tsql_dialect = ansi_dialect.copy_as("tsql")

# Set keywords from separate file
tsql_dialect.sets("reserved_keywords").update([
    "CLUSTERED", "NONCLUSTERED", "ROWGUIDCOL", "TOP"
])

# Define new segments specific to T-SQL
class TopClauseSegment(BaseSegment):
    """TOP clause for T-SQL SELECT statements."""

    type = "top_clause"
    match_grammar = Sequence(
        "TOP",
        OneOf(
            Ref("NumericLiteralSegment"),
            Bracketed(Ref("ExpressionSegment")),
        ),
        Sequence("PERCENT", optional=True),
        Sequence("WITH", "TIES", optional=True),
    )

# Override existing ANSI segments
tsql_dialect.replace(
    SelectStatementSegment=Sequence(
        "SELECT",
        Ref("TopClauseSegment", optional=True),  # T-SQL addition
        Ref("SelectClauseSegment"),
        Ref("FromClauseSegment", optional=True),
        Ref("WhereClauseSegment", optional=True),
    ),
)
```

### Grammar Composition Primitives

Located in `src/sqlfluff/core/parser/grammar/`:

| Primitive | Purpose | Example |
|-----------|---------|---------|
| `Sequence()` | Ordered sequence of elements | `Sequence("SELECT", Ref("SelectClauseSegment"))` |
| `OneOf()` | Choice between alternatives | `OneOf("ASC", "DESC")` |
| `Delimited()` | Comma-separated list | `Delimited(Ref("ColumnReferenceSegment"))` |
| `AnyNumberOf()` | Zero or more repetitions | `AnyNumberOf(Ref("WhereClauseSegment"))` |
| `Bracketed()` | Content in parentheses | `Bracketed(Ref("ExpressionSegment"))` |
| `Ref()` | Reference to another segment | `Ref("TableReferenceSegment")` |
| `Optional()` | Optional element (or use `optional=True`) | `Optional(Ref("WhereClause"))` |

### Grammar Organization Patterns

#### Internal Grammar (Private Attributes with `_` prefix)

Use for grammar components specific to one statement:

```python
class CreateDatabaseStatementSegment(BaseSegment):
    """A CREATE DATABASE statement."""

    # Internal grammar - only used in this segment
    _filestream_option = OneOf(
        Sequence("NON_TRANSACTED_ACCESS", Ref("EqualsSegment"), "OFF"),
        Sequence("DIRECTORY_NAME", Ref("EqualsSegment"), Ref("QuotedLiteralSegment")),
    )

    _create_database_option = OneOf(
        Sequence("FILESTREAM", Bracketed(Delimited(_filestream_option))),
        Sequence("DEFAULT_LANGUAGE", Ref("EqualsSegment"), Ref("LanguageNameSegment")),
        Sequence("DEFAULT_FULLTEXT_LANGUAGE", Ref("EqualsSegment"), Ref("LanguageNameSegment")),
    )

    type = "create_database_statement"
    match_grammar = Sequence(
        "CREATE", "DATABASE",
        Ref("DatabaseReferenceSegment"),
        Sequence("WITH", Delimited(_create_database_option), optional=True),
    )
```

#### Shared Segments (Named Classes)

Create separate segment classes for reusable components:

```python
class FileSpecSegment(BaseSegment):
    """File specification - reusable in CREATE/ALTER statements."""

    type = "file_spec"
    match_grammar = Bracketed(
        Sequence(
            Sequence("NAME", Ref("EqualsSegment"), Ref("QuotedLiteralSegment"), optional=True),
            Sequence("FILENAME", Ref("EqualsSegment"), Ref("QuotedLiteralSegment")),
            Sequence("SIZE", Ref("EqualsSegment"), Ref("FileSizeSegment"), optional=True),
        )
    )

# Now FileSpecSegment can be used in multiple statements
class CreateDatabaseStatementSegment(BaseSegment):
    match_grammar = Sequence(
        "CREATE", "DATABASE",
        Ref("DatabaseReferenceSegment"),
        Sequence("ON", Delimited(Ref("FileSpecSegment")), optional=True),
    )

class AlterDatabaseStatementSegment(BaseSegment):
    match_grammar = Sequence(
        "ALTER", "DATABASE",
        Ref("DatabaseReferenceSegment"),
        "ADD", "FILE", Ref("FileSpecSegment"),
    )
```

**Decision criteria:**
- **Use `_prefix` internal grammar** when:
  - Grammar is specific to one statement type
  - No other segments need to reference it
  - Breaking down complex `match_grammar` for readability

- **Use shared segment classes** when:
  - Multiple statements use the same construct
  - Construct represents a meaningful SQL element
  - Other rules or segments need to `Ref()` it by name
  - Semantic meaning beyond one statement

## Development Workflow

### Step 1: Create Test SQL Files

```bash
# Add SQL test cases to test/fixtures/dialects/<dialect>/
echo "SELECT TOP 10 * FROM users;" > test/fixtures/dialects/tsql/top_clause.sql
echo "CREATE CLUSTERED INDEX idx_id ON users(id);" > test/fixtures/dialects/tsql/create_index.sql
```

**Test file conventions:**
- Organize by segment type (e.g., `select_statement.sql`, `create_table.sql`, `merge_statement.sql`)
- Include multiple test cases per file covering edge cases
- Use descriptive filenames matching the segment being tested
- Test various keyword combinations, identifier formats, literal types, comments

**Example structure:**
```
test/fixtures/dialects/tsql/
├── select_top.sql           # TOP clause variations
├── create_index.sql         # CLUSTERED/NONCLUSTERED indexes
├── merge_statement.sql      # MERGE operations
├── pivot_unpivot.sql        # PIVOT/UNPIVOT queries
└── table_hints.sql          # WITH (NOLOCK) etc.
```

### Step 2: Generate Expected Parse Trees

```bash
# Activate virtual environment
source .venv/bin/activate

# Generate YAML fixtures for specific dialect
python test/generate_parse_fixture_yml.py -d tsql

# Or use tox
tox -e generate-fixture-yml -- -d tsql
```

This creates `.yml` files showing the current parse tree. Initially these may show parsing failures or incorrect structures.

### Step 3: Implement Grammar

Edit `src/sqlfluff/dialects/dialect_<name>.py`:

```python
# 1. Define new segments needed
class TopClauseSegment(BaseSegment):
    """TOP clause for T-SQL."""
    type = "top_clause"
    match_grammar = Sequence(
        "TOP",
        Ref("NumericLiteralSegment"),
        Sequence("PERCENT", optional=True),
    )

# 2. Override parent segments
tsql_dialect.replace(
    SelectStatementSegment=Sequence(
        "SELECT",
        Ref("TopClauseSegment", optional=True),
        Ref("SelectClauseSegment"),
        # ... rest of SELECT grammar
    ),
)
```

### Step 4: Regenerate and Verify

```bash
# Regenerate YAML to see updated parse tree
python test/generate_parse_fixture_yml.py -d tsql

# Check that parsing now works correctly
sqlfluff parse test/fixtures/dialects/tsql/top_clause.sql --dialect tsql
```

### Step 5: Run Full Test Suite

```bash
# Test just the dialect
tox -e generate-fixture-yml -- -d tsql

# Run full test suite to ensure no regressions
tox -e py312
```

## Keywords Management

### Keyword Files

Each dialect should have a keywords file: `dialect_<name>_keywords.py`

```python
"""T-SQL reserved and unreserved keywords."""

RESERVED_KEYWORDS = [
    "ADD", "ALL", "ALTER", "AND", "ANY", "AS", "ASC",
    "CLUSTERED", "NONCLUSTERED", "TOP", "PIVOT", "UNPIVOT",
    # ... full list
]

UNRESERVED_KEYWORDS = [
    "ABSOLUTE", "ACTION", "ADA", "ALIAS", "ALLOCATE",
    # ... full list
]
```

In dialect file:
```python
from sqlfluff.dialects.dialect_tsql_keywords import (
    RESERVED_KEYWORDS, UNRESERVED_KEYWORDS
)

tsql_dialect.sets("reserved_keywords").update(RESERVED_KEYWORDS)
tsql_dialect.sets("unreserved_keywords").update(UNRESERVED_KEYWORDS)
```

## Common Dialect Patterns

### Adding Vendor-Specific Functions

```python
class TSQLFunctionNameSegment(BaseSegment):
    """T-SQL specific function names."""

    type = "function_name"
    match_grammar = OneOf(
        "GETDATE", "NEWID", "SCOPE_IDENTITY",
        "IDENT_CURRENT", "ROWCOUNT_BIG",
        # Add more T-SQL functions
    )

tsql_dialect.replace(
    FunctionNameSegment=OneOf(
        Ref("AnsiSQLFunctionNameSegment"),  # Inherit ANSI functions
        Ref("TSQLFunctionNameSegment"),      # Add T-SQL specific
    ),
)
```

### Adding Statement Types

```python
class MergeStatementSegment(BaseSegment):
    """MERGE statement (T-SQL, Oracle, etc.)."""

    type = "merge_statement"
    match_grammar = Sequence(
        "MERGE",
        Sequence("TOP", Ref("ExpressionSegment"), optional=True),
        "INTO", Ref("TableReferenceSegment"),
        "USING", Ref("TableReferenceSegment"),
        "ON", Ref("ExpressionSegment"),
        AnyNumberOf(
            Sequence("WHEN", "MATCHED", "THEN", Ref("MergeActionSegment")),
            Sequence("WHEN", "NOT", "MATCHED", "THEN", Ref("MergeActionSegment")),
        ),
    )

# Add to statement grammar
tsql_dialect.replace(
    StatementSegment=OneOf(
        Ref("SelectStatementSegment"),
        Ref("InsertStatementSegment"),
        Ref("MergeStatementSegment"),  # New addition
        # ... other statements
    ),
)
```

### Adding Data Types

```python
tsql_dialect.replace(
    DatatypeSegment=OneOf(
        # Inherit ANSI types
        Sequence("VARCHAR", Bracketed(Ref("NumericLiteralSegment"), optional=True)),
        Sequence("INT"),

        # Add T-SQL specific types
        Sequence("NVARCHAR",
                 OneOf(Bracketed(Ref("NumericLiteralSegment")), "MAX", optional=True)),
        Sequence("UNIQUEIDENTIFIER"),
        Sequence("DATETIME2", Bracketed(Ref("NumericLiteralSegment"), optional=True)),
        Sequence("HIERARCHYID"),
    ),
)
```

## Testing Dialect Changes

### Dialect-Specific Tests

Located in `test/dialects/<dialect>_test.py`:

```python
"""Tests specific to T-SQL dialect."""
import pytest
from sqlfluff.core import Linter

@pytest.fixture
def tsql_linter():
    """Provide T-SQL linter for tests."""
    return Linter(dialect="tsql")

def test_top_clause_parsing(tsql_linter):
    """Test TOP clause in SELECT."""
    sql = "SELECT TOP 10 * FROM users;"
    parsed = tsql_linter.parse_string(sql)
    assert parsed.tree is not None
    # Find TOP clause in parse tree
    top_clause = parsed.tree.find("top_clause")
    assert top_clause is not None
```

### Regression Prevention

Always run the full fixture generation to ensure your changes don't break other dialects:

```bash
# Test all dialects
tox -e generate-fixture-yml

# Or specific ones that might be affected
tox -e generate-fixture-yml -- -d ansi -d postgres -d mysql
```

## Per-Dialect Agent Instructions

For complex dialects with vendor-specific quirks, SEE detailed instructions:

**T-SQL**: `src/sqlfluff/dialects/dialect_instructions/tsql.md`

---

**See also:**
- Root `AGENTS.md` for general project overview
- `src/sqlfluff/AGENTS.md` for Python coding standards
- `test/AGENTS.md` for testing conventions
- Individual `dialect_instructions/<dialect>.md` files for dialect-specific guidance
