//! Parser integration tests
//!
//! Tests are organized by category:
//! - `basic_sql` - Basic SQL parsing (SELECT, CREATE TABLE, etc.)
//! - `grammar` - Grammar features (AnySetOf, Delimited, Bracketed, etc.)
//! - `iterative` - Iterative parser specific tests
//! - `token_coverage` - Tests verifying all tokens appear in AST
//! - `common` - Common test helpers and utilities

mod common;
mod basic_sql;
mod grammar;
mod iterative;
mod token_coverage;
