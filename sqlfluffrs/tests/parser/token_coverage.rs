//! Token coverage tests
//!
//! Tests that verify all tokens from the input are present in the AST

use crate::parser::common::parse_and_verify_tokens;
use sqlfluffrs::parser_old::ParseError;
use sqlfluffrs::Dialect;

macro_rules! with_larger_stack {
    ($test_fn:expr) => {{
        std::thread::Builder::new()
            .stack_size(16 * 1024 * 1024) // 16MB stack
            .spawn($test_fn)
            .expect("Failed to spawn thread")
            .join()
            .expect("Thread panicked")
    }};
}

#[test]
fn test_all_tokens_present_simple_select() -> Result<(), ParseError> {
    with_larger_stack!(|| {
        env_logger::try_init().ok();
        parse_and_verify_tokens("SELECT * FROM table_name", "SelectStatementSegment", Dialect::Ansi)
    })
}

#[test]
fn test_all_tokens_present_with_whitespace() -> Result<(), ParseError> {
    with_larger_stack!(|| {
        env_logger::try_init().ok();
        // Multiple spaces, tabs, newlines
        parse_and_verify_tokens("SELECT  \t*\n  FROM\n\ttable_name  ", "SelectStatementSegment", Dialect::Ansi)
    })
}

#[test]
fn test_all_tokens_present_complex_query() -> Result<(), ParseError> {
    with_larger_stack!(|| {
        env_logger::try_init().ok();

        let raw = r#"SELECT
    t1.id,
    t1.name AS user_name,
    COUNT(*) as count
FROM users t1
LEFT JOIN orders t2 ON t1.id = t2.user_id
WHERE t1.status = 'active'
GROUP BY t1.id, t1.name
HAVING COUNT(*) > 5
ORDER BY count DESC
LIMIT 10"#;

        parse_and_verify_tokens(raw, "SelectStatementSegment", Dialect::Ansi)
    })
}

#[test]
fn test_all_tokens_present_with_subquery() -> Result<(), ParseError> {
    with_larger_stack!(|| {
        env_logger::try_init().ok();

        let raw = r#"SELECT * FROM (
    SELECT id, name
    FROM users
    WHERE active = true
) AS subquery
WHERE subquery.id > 100"#;

        parse_and_verify_tokens(raw, "FileSegment", Dialect::Ansi)
    })
}

#[test]
fn test_all_tokens_present_case_expression() -> Result<(), ParseError> {
    with_larger_stack!(|| {
        env_logger::try_init().ok();

        let raw = r#"SELECT
    CASE
        WHEN status = 'active' THEN 1
        WHEN status = 'pending' THEN 0
        ELSE -1
    END AS status_code
FROM users"#;

        parse_and_verify_tokens(raw, "SelectStatementSegment", Dialect::Ansi)
    })
}

#[test]
fn test_all_tokens_present_wildcards() -> Result<(), ParseError> {
    with_larger_stack!(|| {
        env_logger::try_init().ok();
        // Test various wildcard patterns
        parse_and_verify_tokens(
            "SELECT *, table1.*, schema.table2.* FROM table1, schema.table2",
            "SelectStatementSegment", Dialect::Ansi,
        )
    })
}

#[test]
fn test_all_tokens_present_with_backtracking() -> Result<(), ParseError> {
    with_larger_stack!(|| {
        env_logger::try_init().ok();
        // This tests backtracking in OneOf - could match as function call or column ref
        parse_and_verify_tokens("SELECT COUNT(*) FROM table_name", "SelectStatementSegment", Dialect::Ansi)
    })
}

#[test]
fn test_all_tokens_present_anysetof() -> Result<(), ParseError> {
    with_larger_stack!(|| {
        env_logger::try_init().ok();
        // Test AnySetOf with multiple elements in different orders
        parse_and_verify_tokens(
            "FOREIGN KEY (col) REFERENCES other(col) ON UPDATE CASCADE ON DELETE SET NULL",
            "TableConstraintSegment", Dialect::Ansi,
        )
    })
}

#[test]
fn test_all_tokens_present_delimited() -> Result<(), ParseError> {
    with_larger_stack!(|| {
        env_logger::try_init().ok();
        // Test Delimited with many elements and trailing commas
        parse_and_verify_tokens(
            "SELECT col1, col2, col3, col4, col5 FROM table_name",
            "SelectStatementSegment", Dialect::Ansi,
        )
    })
}

#[test]
fn test_all_tokens_present_bracketed() -> Result<(), ParseError> {
    with_larger_stack!(|| {
        env_logger::try_init().ok();
        // Test Bracketed expressions with nested content
        parse_and_verify_tokens(
            "SELECT (a + b) * (c - d) FROM table_name",
            "SelectStatementSegment", Dialect::Ansi,
        )
    })
}

#[test]
fn test_all_tokens_present_sequence_allow_gaps_false() -> Result<(), ParseError> {
    with_larger_stack!(|| {
        env_logger::try_init().ok();
        // Specifically test sequences with allow_gaps=false (like WildcardIdentifierSegment)
        // This is the case that triggered our retroactive collection fix
        parse_and_verify_tokens(
            "SELECT schema . table . * FROM table_name",
            "SelectStatementSegment", Dialect::Ansi,
        )
    })
}

#[test]
fn test_all_tokens_present_mixed_whitespace() -> Result<(), ParseError> {
    with_larger_stack!(|| {
        env_logger::try_init().ok();
        // Mix of spaces, tabs, and multiple newlines
        parse_and_verify_tokens("SELECT\n\n  *  \t\n FROM  \t table_name\n\n", "SelectStatementSegment", Dialect::Ansi)
    })
}

#[test]
fn test_all_tokens_present_insert_statement() -> Result<(), ParseError> {
    with_larger_stack!(|| {
        env_logger::try_init().ok();
        parse_and_verify_tokens(
            "INSERT INTO users (id, name, email) VALUES (1, 'John', 'john@example.com')",
            "InsertStatementSegment", Dialect::Ansi,
        )
    })
}

#[test]
fn test_all_tokens_present_update_statement() -> Result<(), ParseError> {
    with_larger_stack!(|| {
        env_logger::try_init().ok();
        parse_and_verify_tokens(
            "UPDATE users SET name = 'Jane', status = 'active' WHERE id = 1",
            "UpdateStatementSegment", Dialect::Ansi,
        )
    })
}

#[test]
fn test_all_tokens_present_create_table() -> Result<(), ParseError> {
    with_larger_stack!(|| {
        env_logger::try_init().ok();

        let raw = r#"CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255)
)"#;

        parse_and_verify_tokens(raw, "CreateTableStatementSegment", Dialect::Ansi)
    })
}
