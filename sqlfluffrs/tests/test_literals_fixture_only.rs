use std::fs;
use std::path::PathBuf;
use std::str::FromStr;

use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_lexer::{LexInput, Lexer};
use sqlfluffrs_parser::parser::Parser;

#[test]
fn test_literals_fixture_only() {
    env_logger::try_init().ok();

    let fixture_path = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .join("test/fixtures/dialects/bigquery/literals_with_data_type_and_quoted.sql");

    let sql = fs::read_to_string(&fixture_path).expect("Failed to read fixture");

    println!("\n=== SQL ({} chars) ===", sql.len());

    let dialect = Dialect::from_str("bigquery").expect("Invalid dialect");
    let lexer = Lexer::new(None, Dialect::get_lexers(&dialect).to_vec());
    let (tokens, lex_errors) = lexer.lex(LexInput::String(sql.clone()), false);

    assert!(lex_errors.is_empty(), "Lexer errors: {:?}", lex_errors);

    println!("=== Total tokens: {} ===", tokens.len());

    let mut parser = Parser::new(&tokens, dialect);
    let _ast = parser.call_rule_as_root().expect("Parse error");

    println!("\n=== Parse successful ===");
}
