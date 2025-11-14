# T-SQL Dialect - AI Assistant Instructions

This file provides T-SQL (Microsoft SQL Server) specific development guidance.

## T-SQL Syntax Documentation

When implementing T-SQL features, refer to:
- **Primary**: [T-SQL Reference](https://learn.microsoft.com/en-us/sql/t-sql/)
- **Syntax Conventions**: [Transact-SQL Syntax Conventions](https://learn.microsoft.com/en-us/sql/t-sql/language-elements/transact-sql-syntax-conventions-transact-sql)

## Microsoft Docs → SQLFluff Translation

### T-SQL (Microsoft Docs) Translation

Microsoft's syntax notation → SQLFluff grammar:

| Microsoft Notation | Meaning | SQLFluff Translation |
|-------------------|---------|---------------------|
| `UPPERCASE` | Keyword | Literal string `"UPPERCASE"` |
| *italic* | User parameter | `Ref("SegmentName")` |
| `\|` (pipe) | Choice | `OneOf(...)` |
| `[ ]` (brackets) | Optional | `optional=True` or `Ref(..., optional=True)` |
| `{ }` (braces) | Required choice | `OneOf(...)` without optional |
| `[, ...n]` | Comma-separated repetition | `Delimited(...)` |
| `[...n]` | Space-separated repetition | `AnyNumberOf(...)` |
| `;` | Statement terminator | `Ref("SemicolonSegment")` |
| `<label> ::=` | Named syntax block | Define as separate segment class |

**Example:**
```
Microsoft Docs:
CREATE TABLE <table_name>
(
    <column_definition> [, ...n]
)
[ WITH ( <table_option> [, ...n] ) ]

SQLFluff:
class CreateTableStatementSegment(BaseSegment):
    type = "create_table_statement"
    match_grammar = Sequence(
        "CREATE", "TABLE",
        Ref("TableReferenceSegment"),
        Bracketed(
            Delimited(Ref("ColumnDefinitionSegment"))
        ),
        Sequence(
            "WITH",
            Bracketed(Delimited(Ref("TableOptionSegment"))),
            optional=True,
        ),
    )
```

## Known Edge Cases

### Quoted Identifiers

T-SQL supports:
- Square brackets: `[column name]`, `[table].[column]`
- Double quotes: `"column name"` (when `QUOTED_IDENTIFIER` is ON)

Square brackets are the standard T-SQL approach.

### String Literals

- Single quotes: `'string value'`
- Escaped quotes: `'It''s a string'` (double single quote)
- Unicode prefix: `N'Unicode string'`

### Multi-part Identifiers

T-SQL supports up to 4-part names:
- `[server].[database].[schema].[object]`
- `[database].[schema].[table]`
- `[schema].[table]`
- `[table]`

### SET Statements

T-SQL uses many SET statements for session configuration:
```sql
SET NOCOUNT ON
SET ANSI_NULLS ON
SET QUOTED_IDENTIFIER ON
SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED
```

## Testing T-SQL Features

### Test File Locations

```
test/fixtures/dialects/tsql/
├── select_top.sql
├── merge_statement.sql
├── pivot_unpivot.sql
├── table_hints.sql
├── output_clause.sql
├── cte_multiple.sql
└── create_index_clustered.sql
```

### Running T-SQL Tests

```bash
# Generate all T-SQL fixtures
python test/generate_parse_fixture_yml.py -d tsql

# Run T-SQL dialect tests
tox -e py312 -- test/dialects/tsql_test.py

# Parse single file
sqlfluff parse test/fixtures/dialects/tsql/select_top.sql --dialect tsql
```

## Common Implementation Tasks

### Adding New T-SQL Function

1. Check if function exists in Microsoft docs
2. Add to T-SQL function list in dialect file
3. Create test case in appropriate test file
4. Verify parsing

### Adding New Statement Type

1. Study Microsoft docs syntax
2. Create segment class with `match_grammar`
3. Add to `StatementSegment` via `.replace()`
4. Create comprehensive test cases
5. Regenerate fixtures

### Fixing Parsing Issue

1. Identify failing SQL in test fixtures
2. Run `sqlfluff parse <file> --dialect tsql` to see error
3. Examine parse tree output
4. Adjust grammar in dialect file
5. Regenerate and verify

## Resources

- [T-SQL Language Reference](https://learn.microsoft.com/en-us/sql/t-sql/language-reference-database-engine)
- [T-SQL Statements](https://learn.microsoft.com/en-us/sql/t-sql/statements/statements)
- [T-SQL Functions](https://learn.microsoft.com/en-us/sql/t-sql/functions/functions)
- [T-SQL Data Types](https://learn.microsoft.com/en-us/sql/t-sql/data-types/data-types-transact-sql)

---

**See also:**
- `src/sqlfluff/dialects/AGENTS.md` for general dialect development
- Root `AGENTS.md` for project overview
