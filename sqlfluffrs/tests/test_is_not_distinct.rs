use std::str::FromStr;

use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_lexer::{LexInput, Lexer};
use sqlfluffrs_parser::parser::Parser;

#[test]
fn test_is_not_distinct_simple() {
    env_logger::try_init().ok();

    // Simplest case from the fixture
    let sql = "SELECT a_column FROM t_table WHERE a_column IS NOT DISTINCT FROM b_column;";

    println!("\n=== SQL ===\n{}\n", sql);

    let dialect = Dialect::from_str("bigquery").expect("Invalid dialect");
    let lexer = Lexer::new(None, Dialect::get_lexers(&dialect).to_vec());
    let (tokens, lex_errors) = lexer.lex(LexInput::String(sql.to_string()), false);

    assert!(lex_errors.is_empty(), "Lexer errors: {:?}", lex_errors);

    println!("=== Total tokens: {} ===", tokens.len());
    for (i, tok) in tokens.iter().enumerate() {
        println!("{:3}: {:20} {:?}", i, tok.token_type, tok.raw());
    }

    let mut parser = Parser::new(&tokens, dialect);
    let ast = parser.call_rule_as_root().expect("Parse error");

    println!("\n=== Parse successful ===");
    println!("AST type: {:?}", std::any::type_name_of_val(&ast));
}

#[test]
fn test_is_not_distinct_with_brackets() {
    env_logger::try_init().ok();

    // First statement from fixture with brackets
    let sql = "SELECT (a_column IS DISTINCT FROM b_column) FROM t_table;";

    println!("\n=== SQL ===\n{}\n", sql);

    let dialect = Dialect::from_str("bigquery").expect("Invalid dialect");
    let lexer = Lexer::new(None, Dialect::get_lexers(&dialect).to_vec());
    let (tokens, lex_errors) = lexer.lex(LexInput::String(sql.to_string()), false);

    assert!(lex_errors.is_empty(), "Lexer errors: {:?}", lex_errors);

    println!("=== Total tokens: {} ===", tokens.len());

    let mut parser = Parser::new(&tokens, dialect);
    let ast = parser.call_rule_as_root().expect("Parse error");

    println!("\n=== Parse successful ===");
}
