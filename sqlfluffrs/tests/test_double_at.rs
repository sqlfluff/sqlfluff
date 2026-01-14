use sqlfluffrs_dialects::dialect::bigquery::matcher::BIGQUERY_LEXERS;
use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_lexer::{LexInput, Lexer};

#[test]
fn test_double_at_sign() {
    env_logger::try_init().ok();

    let sql = "@@error.message";

    let input = LexInput::String(sql.to_string());
    let lexer = Lexer::new(None, BIGQUERY_LEXERS.to_vec());
    let (tokens, lex_errors) = lexer.lex(input, false);

    println!("\n=== SQL: {} ===", sql);
    println!("\n=== Lex errors: {} ===", lex_errors.len());
    for err in &lex_errors {
        println!("Error: {:?}", err);
    }

    println!("\n=== Total tokens: {} ===", tokens.len());
    for (i, tok) in tokens.iter().enumerate() {
        println!(
            "{:3}: token_type={:20} instance_types={:?} raw={:?}",
            i,
            tok.token_type,
            tok.instance_types,
            tok.raw()
        );
    }

    assert!(
        lex_errors.is_empty(),
        "Lexer should not produce errors for @@error.message"
    );
    assert_eq!(tokens.len(), 2, "Should produce 1 token + EOF");
    assert!(
        tokens[0]
            .instance_types
            .contains(&"double_at_sign_literal".to_string()),
        "Token should have instance type double_at_sign_literal, got: {:?}",
        tokens[0].instance_types
    );
    assert_eq!(tokens[0].raw(), "@@error.message");

    // Verify EOF token
    assert_eq!(tokens[1].token_type, "end_of_file");
}
