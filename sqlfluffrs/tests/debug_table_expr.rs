use sqlfluffrs_dialects::dialect::ansi::matcher::ANSI_LEXERS;
use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_lexer::{LexInput, Lexer};
use sqlfluffrs_parser::parser::Parser;

#[test]
fn test_table_expression_debug() {
    env_logger::try_init().ok();

    // Test with WITH OFFSET - second query from fixture
    let sql = r#"SELECT id, name
FROM
    UNNEST([1, 2, 3]) id WITH OFFSET pos1,
    UNNEST(['a', 'b', 'c']) name WITH OFFSET pos2
WHERE pos1 = pos2;"#;

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

            if parser.pos < tokens.len() - 1 {
                println!("\n!!! WARNING: Parser did not consume all tokens !!!");
                println!("Remaining tokens:");
                for i in parser.pos..tokens.len() {
                    println!("{:3}: {:20} {:?}", i, tokens[i].token_type, tokens[i].raw);
                }
            }
        }
        Err(e) => {
            println!("\n=== PARSE ERROR ===");
            println!("{:?}", e);
        }
    }

    assert!(ast.is_ok(), "Parse error: {:?}", ast.err());
    // Parser position should be at or past the last token index
    // tokens.len() is the count, so last index is len() - 1
    // Parser position can be len() if it consumed everything including end_of_file
    assert!(
        parser.pos >= tokens.len() - 1,
        "Parser did not consume all tokens. Stopped at {} / {} tokens (last index: {})",
        parser.pos,
        tokens.len(),
        tokens.len() - 1
    );
}
