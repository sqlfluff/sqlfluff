use std::str::FromStr;

use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_lexer::{LexInput, Lexer};
use sqlfluffrs_parser::parser::Parser;

#[test]
fn test_numeric_literal_simple() {
    env_logger::try_init().ok();

    let sql = "SELECT NUMERIC '0';";

    println!("\n=== SQL ===\n{}\n", sql);

    let dialect = Dialect::from_str("bigquery").expect("Invalid dialect");
    let lexer = Lexer::new(None, Dialect::get_lexers(&dialect).to_vec());
    let (tokens, lex_errors) = lexer.lex(LexInput::String(sql.to_string()), false);

    assert!(lex_errors.is_empty(), "Lexer errors: {:?}", lex_errors);

    println!("=== Total tokens: {} ===", tokens.len());
    for (i, tok) in tokens.iter().enumerate() {
        println!("{:3}: {:20} {:?}", i, tok.token_type, tok.raw());
    }

    let mut parser = Parser::new(&tokens, dialect, hashbrown::HashMap::new());
    let _ast = parser.call_rule_as_root().expect("Parse error");

    println!("\n=== Parse successful ===");
}

#[test]
fn test_numeric_literal_comparison() {
    env_logger::try_init().ok();

    let sql = "SELECT NUMERIC '0' = NUMERIC '0';";

    println!("\n=== SQL ===\n{}\n", sql);

    let dialect = Dialect::from_str("bigquery").expect("Invalid dialect");
    let lexer = Lexer::new(None, Dialect::get_lexers(&dialect).to_vec());
    let (tokens, lex_errors) = lexer.lex(LexInput::String(sql.to_string()), false);

    assert!(lex_errors.is_empty(), "Lexer errors: {:?}", lex_errors);

    println!("=== Total tokens: {} ===", tokens.len());

    let mut parser = Parser::new(&tokens, dialect, hashbrown::HashMap::new());
    let _ast = parser.call_rule_as_root().expect("Parse error");

    println!("\n=== Parse successful ===");
}
