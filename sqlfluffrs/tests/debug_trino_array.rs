use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_lexer::{LexInput, Lexer};
use sqlfluffrs_parser::parser::Parser;
use std::str::FromStr;

// TODO: Enable once Trino dialect is fully supported
// #[test]
fn test_trino_array_angle_brackets() {
    // Initialize the logger to capture debug output
    let _ = env_logger::builder()
        .is_test(true)
        .filter_level(log::LevelFilter::Debug)
        .try_init();

    println!("\n========================================");
    println!("DEBUGGING: Array datatype parsing with CREATE TABLE");
    println!("========================================");
    test_sql("CREATE TABLE t (x array(integer));");
}

fn test_sql(sql: &str) {
    let dialect = Dialect::from_str("trino").expect("Invalid dialect");
    let input = LexInput::String(sql.to_string());
    let lexer = Lexer::new(None, dialect.get_lexers().to_vec());
    let (tokens, errors) = lexer.lex(input, false);

    assert!(errors.is_empty(), "Lexer errors: {:?}", errors);

    println!("\n=== ALL TOKENS ===");
    for (idx, token) in tokens.iter().enumerate() {
        println!(
            "  {}: type={:15} raw={:10?} is_code={}",
            idx,
            token.token_type,
            token.raw(),
            token.is_code()
        );
    }

    // Parse
    let mut parser = Parser::new(&tokens, dialect, hashbrown::HashMap::new());
    let result = parser.call_rule_as_root();

    match result {
        Ok(node) => {
            println!("\n=== PARSE RESULT ===");
            println!("Parse result: {:?}", std::mem::discriminant(&node));
            println!("Parser final position: {} / {}", parser.pos, tokens.len());

            // Check if parser consumed all tokens
            if parser.pos < tokens.len() - 1 {
                // -1 for EOF
                println!("\nWARNING: Parser did not consume all tokens!");
                println!(
                    "Stopped at token {}: type={} raw={:?}",
                    parser.pos,
                    tokens[parser.pos].token_type,
                    tokens[parser.pos].raw()
                );
                println!("Remaining tokens:");
                for i in parser.pos..tokens.len().min(parser.pos + 10) {
                    println!(
                        "  {}: type={} raw={:?}",
                        i,
                        tokens[i].token_type,
                        tokens[i].raw()
                    );
                }
            }

            // Check the AST structure by converting to YAML
            let record = node.as_record(true, true, false);
            let yaml_str = format!("{:#?}", record);

            // Count key structures in the YAML output
            let has_bracketed = yaml_str.contains("\"bracketed\"");
            let has_column_def = yaml_str.contains("\"column_definition\"");

            println!("AST has bracketed section: {}", has_bracketed);
            println!("AST has column definition: {}", has_column_def);

            if parser.pos >= tokens.len() - 1 {
                println!("✓ SUCCESS: Parsed all tokens");
            } else {
                println!(
                    "✗ INCOMPLETE: Only parsed {} of {} tokens",
                    parser.pos,
                    tokens.len()
                );
            }
        }
        Err(e) => {
            println!("\n=== PARSE ERROR ===");
            println!("{:?}", e);
            panic!("Parse failed: {:?}", e);
        }
    }
}
