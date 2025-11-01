use sqlfluffrs_dialects::dialect::ansi::matcher::ANSI_LEXERS;
use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_lexer::{LexInput, Lexer};
use sqlfluffrs_parser::parser::Parser;

#[test]
fn test_table_expression_debug() {
    env_logger::try_init().ok();

    // Test with WITH OFFSET
    let sql = r#"SELECT id
FROM UNNEST([1, 2, 3]) id WITH OFFSET pos1
WHERE id = 1;"#;

    let input = LexInput::String(sql.to_string());
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, lex_errors) = lexer.lex(input, false);

    println!("\n=== TOKENS ===");
    for (i, tok) in tokens.iter().enumerate() {
        println!("{:3}: {:20} {:?}", i, tok.token_type, tok.raw);
    }

    assert!(lex_errors.is_empty(), "Lexer errors: {:?}", lex_errors);

    let mut parser = Parser::new(&tokens, Dialect::Ansi);
    let ast = parser.call_rule_as_root();

    match &ast {
        Ok(node) => {
            println!("\n=== AST ===");
            println!("{:#?}", node);

            println!("\n=== YAML ===");
            let as_record = node.as_record(true, true, false);
            let yaml_str = serde_yaml_ng::to_string(&as_record).unwrap();
            println!("{}", yaml_str);

            println!("\n=== Parser position: {} / {} ===", parser.pos, tokens.len());
        }
        Err(e) => {
            println!("\n=== PARSE ERROR ===");
            println!("{:?}", e);
        }
    }

    assert!(ast.is_ok(), "Parse error: {:?}", ast.err());
}
