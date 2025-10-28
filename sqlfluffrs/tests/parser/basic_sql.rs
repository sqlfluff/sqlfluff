//! Basic SQL parsing tests
//!
//! Tests for fundamental SQL statements like SELECT, CREATE TABLE, etc.

use crate::parser::common::parse_sql;
use sqlfluffrs::parser::{ParseError, Parser};
use sqlfluffrs_lexer::{LexInput, Lexer};
use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_dialects::dialect::ansi::matcher::ANSI_LEXERS;

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
fn parse_select_statement() -> Result<(), ParseError> {
    env_logger::try_init().ok();

    let raw = "SELECT a, b FROM my_table";
    let ast = parse_sql(raw, "SelectStatementSegment", Dialect::Ansi)?;

    // Verify AST was created
    println!("AST: {:#?}", ast);

    Ok(())
}

#[test]
fn parse_select_single_item() -> Result<(), ParseError> {
    env_logger::try_init().ok();

    let raw = "SELECT a";
    let input = LexInput::String(raw.into());
    let dialect = Dialect::Ansi;
    // TODO: Select the correct lexers for the dialect dynamically
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _errors) = lexer.lex(input, false);
    let mut parser = Parser::new(&tokens, dialect);

    let ast = parser.call_rule("SelectClauseSegment", &[])?;
    println!("AST: {:#?}", ast);

    let last_non_code_pos = parser
        .tokens
        .iter()
        .enumerate()
        .rev()
        .find(|(_, t)| !t.is_code())
        .map(|(i, _)| i)
        .unwrap_or(parser.tokens.len());

    assert!(parser.pos >= last_non_code_pos);

    Ok(())
}

#[test]
fn parse_bracket() -> Result<(), ParseError> {
    env_logger::try_init().ok();

    let raw = "( this, that )";
    let input = LexInput::String(raw.into());
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _errors) = lexer.lex(input, false);
    let mut parser = Parser::new(&tokens, dialect);

    let ast = parser.call_rule("BracketedColumnReferenceListGrammar", &[])?;
    println!("AST: {:#?}", ast);

    // The parser should have consumed up to (and including) the closing bracket
    assert_eq!(parser.pos, 8);
    assert_eq!(parser.tokens[7].raw(), ")");

    Ok(())
}

#[test]
fn parse_naked_identifier() -> Result<(), ParseError> {
    env_logger::try_init().ok();

    let raw = "a";
    let ast = parse_sql(raw, "BaseExpressionElementGrammar", Dialect::Ansi)?;

    println!("AST: {:#?}", ast);

    Ok(())
}

#[test]
fn parse_select_terminator() -> Result<(), ParseError> {
    env_logger::try_init().ok();

    let raw = "FROM";
    let input = LexInput::String(raw.into());
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _errors) = lexer.lex(input, false);
    let mut parser = Parser::new(&tokens, dialect);

    let ast = parser.call_rule("SelectClauseTerminatorGrammar", &[])?;
    println!("AST: {:#?}", ast);

    parser.skip_transparent(true);
    assert_eq!(parser.tokens[parser.pos - 1].get_type(), "end_of_file");
    assert_eq!(parser.pos, parser.tokens.len());

    Ok(())
}

#[test]
fn parse_statements() -> Result<(), ParseError> {
    env_logger::try_init().ok();

    let raw = "SELECT 1 FROM tabx as b";
    let input = LexInput::String(raw.into());
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _errors) = lexer.lex(input, false);
    let mut parser = Parser::new(&tokens, dialect);

    let ast = parser.call_rule_as_root()?;
    println!("AST: {:#?}", ast);

    assert_eq!(parser.pos, tokens.len());
    assert_eq!(tokens[parser.pos - 1].get_type(), "end_of_file");

    Ok(())
}

#[test]
fn parse_create_table_from_statements() -> Result<(), ParseError> {
    with_larger_stack!(|| {
        env_logger::try_init().ok();

        let raw = "CREATE TABLE foo AS SELECT * FROM bar";
        let ast = parse_sql(raw, "FileSegment", Dialect::Ansi)?;

        println!("AST: {:#?}", ast);

        Ok(())
    })
}

#[test]
fn parse_column_def_with_not_null_segment() -> Result<(), ParseError> {
    env_logger::try_init().ok();

    let raw = "a INT NOT NULL";
    let ast = parse_sql(raw, "ColumnDefinitionSegment", Dialect::Ansi)?;

    println!("AST: {:#?}", ast);

    Ok(())
}

#[test]
fn parse_datatype_segment() -> Result<(), ParseError> {
    env_logger::try_init().ok();

    let raw = "INT";
    let ast = parse_sql(raw, "DatatypeSegment", Dialect::Ansi)?;

    println!("AST: {:#?}", ast);

    Ok(())
}

#[test]
fn parse_many_join() -> Result<(), ParseError> {
    env_logger::try_init().ok();

    let raw = "SELECT a FROM t1 JOIN t2 ON t1.id = t2.id";
    let ast = parse_sql(raw, "SelectStatementSegment", Dialect::Ansi)?;

    println!("AST: {:#?}", ast);

    Ok(())
}

#[test]
fn parse_col_def_segment() -> Result<(), ParseError> {
    env_logger::try_init().ok();

    let raw = "id INT PRIMARY KEY";
    let ast = parse_sql(raw, "ColumnDefinitionSegment", Dialect::Ansi)?;

    println!("AST: {:#?}", ast);

    Ok(())
}

#[test]
fn parse_from_expression_segment() -> Result<(), ParseError> {
    env_logger::try_init().ok();

    let raw = "table_name";
    let ast = parse_sql(raw, "FromExpressionSegment", Dialect::Ansi)?;

    println!("AST: {:#?}", ast);

    Ok(())
}
