use sqlfluffrs_dialects::dialect::bigquery::matcher::BIGQUERY_LEXERS;
use sqlfluffrs_lexer::{LexInput, Lexer};

#[test]
fn test_handle_exception_sql() {
    env_logger::try_init().ok();

    // Exact SQL from the fixture file lines 23-27
    let sql = r#"BEGIN
  SELECT 100/0;
EXCEPTION WHEN ERROR THEN
  RAISE USING MESSAGE = FORMAT("Something went wrong: %s", @@error.message);
END;"#;

    println!("\n=== SQL ===\n{}\n", sql);

    let lexer = Lexer::new(None, BIGQUERY_LEXERS.to_vec());
    let (tokens, lex_errors) = lexer.lex(LexInput::String(sql.to_string()), false);

    println!("=== Lex errors: {} ===", lex_errors.len());
    for err in &lex_errors {
        println!("  {:?}", err);
    }

    println!("\n=== Total tokens: {} ===", tokens.len());
    for (i, tok) in tokens.iter().enumerate() {
        println!("{:3}: {:20} {:?}", i, tok.token_type, tok.raw());
    }

    assert!(lex_errors.is_empty(), "Should lex without errors");
}
