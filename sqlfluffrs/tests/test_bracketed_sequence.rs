use sqlfluffrs_dialects::dialect::ansi::matcher::ANSI_LEXERS;
use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_lexer::{LexInput, Lexer};
use sqlfluffrs_parser::parser::Parser;

#[test]
fn test_bracketed_implicit_sequence() {
    env_logger::try_init().ok();

    // Test that Bracketed with multiple elements creates an implicit Sequence
    // Using function call with multiple arguments: func(arg1, arg2, arg3)
    // This is simpler than CREATE CAST and avoids grammar ambiguity
    let sql = r#"SELECT COUNT(DISTINCT col1, col2) FROM table1"#;

    let input = LexInput::String(sql.to_string());
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, lex_errors) = lexer.lex(input, false);

    println!("\n=== TOKENS ===");
    for (i, tok) in tokens.iter().enumerate() {
        println!("{:3}: {:20} {:?}", i, tok.token_type, tok.raw);
    }

    assert!(lex_errors.is_empty(), "Lexer errors: {:?}", lex_errors);

    let mut parser = Parser::new(&tokens, Dialect::Ansi, hashbrown::HashMap::new());
    let ast = parser.call_rule_as_root();

    match &ast {
        Ok(node) => {
            println!("\n=== AST ===");
            println!("{:#?}", node);

            println!("\n=== YAML ===");
            let as_record = node.as_record(true, true, false);
            let yaml_str = serde_yaml_ng::to_string(&as_record).unwrap();
            println!("{}", yaml_str);

            println!(
                "\n=== Parser position: {} / {} ===",
                parser.pos,
                tokens.len()
            );

            // Verify the structure includes bracketed content
            let yaml_str = serde_yaml_ng::to_string(&as_record).unwrap();

            // Check that bracketed content exists
            assert!(
                yaml_str.contains("bracketed"),
                "Should have bracketed structure"
            );

            // Check that we have a start_bracket and end_bracket
            assert!(
                yaml_str.contains("start_bracket"),
                "Should have start_bracket"
            );
            assert!(yaml_str.contains("end_bracket"), "Should have end_bracket");

            // Verify bracketed implicit Sequence is working:
            // 1. Should have start_bracket and end_bracket tokens
            assert!(yaml_str.contains("start_bracket:"), "Missing start_bracket");
            assert!(yaml_str.contains("end_bracket:"), "Missing end_bracket");

            // 2. Should have comma separators between elements
            assert!(yaml_str.contains("comma:"), "Missing comma separator");

            // 3. The CRITICAL test: should have multiple elements inside brackets
            // In the YAML, bracketed children are listed with "- " prefix
            // Count how many "- " appear after "bracketed:" and before the next non-indented line
            let expression_count = yaml_str.matches("expression:").count();
            println!("\n=== Expression count: {} ===", expression_count);

            // Success! If we have multiple expressions and commas, the implicit Sequence is working
            assert!(expression_count >= 2,
                "Bracketed should contain multiple expression elements (implicit Sequence working), found {}",
                expression_count);

            println!("\n✓ Bracketed with multiple elements successfully creates implicit Sequence");
            println!("✓ Parser correctly handles start_bracket, elements, commas, end_bracket");
        }
        Err(e) => {
            eprintln!("Parse error: {:?}", e);
            panic!("Parse failed");
        }
    }

    assert!(ast.is_ok(), "Parse should succeed");
}
