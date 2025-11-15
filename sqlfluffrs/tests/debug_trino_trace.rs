// Trace-level debug tests for Trino array datatype parsing issue
use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_lexer::{LexInput, Lexer};
use sqlfluffrs_parser::parser::Parser;
use std::str::FromStr;

// TODO: Enable once Trino dialect is fully supported
// #[test]
fn test_varchar_trace() {
    let _ = env_logger::builder()
        .is_test(true)
        .filter_level(log::LevelFilter::Trace)
        .try_init();

    let sql = "CREATE TABLE t (x varchar);";
    println!("\n========== VARCHAR (WORKING) ==========");
    test_sql(sql);
}

// TODO: Enable once Trino dialect is fully supported
// #[test]
fn test_array_trace() {
    let _ = env_logger::builder()
        .is_test(true)
        .filter_level(log::LevelFilter::Trace)
        .try_init();

    let sql = "CREATE TABLE t (x array(integer));";
    println!("\n========== ARRAY (FAILING) ==========");
    test_sql(sql);
}

fn test_sql(sql: &str) {
    let dialect = Dialect::from_str("trino").expect("Invalid dialect");
    let input = LexInput::String(sql.to_string());
    let lexer = Lexer::new(None, dialect.get_lexers().to_vec());
    let (tokens, errors) = lexer.lex(input, false);

    assert!(errors.is_empty(), "Lexer errors: {:?}", errors);

    println!("\nSQL: {}", sql);
    println!("\nTokens: {} total", tokens.len());

    // Parse
    let mut parser = Parser::new(&tokens, dialect);
    let result = parser.call_rule_as_root();

    match result {
        Ok(node) => {
            println!("\n=== RESULT ===");
            println!("Parsed {} / {} tokens", parser.pos, tokens.len());

            let record = node.as_record(true, true, false);
            let yaml_str = format!("{:#?}", record);
            let has_bracketed = yaml_str.contains("\"bracketed\"");

            println!("Has bracketed section: {}", has_bracketed);
        }
        Err(e) => {
            println!("\n=== ERROR ===");
            println!("{:?}", e);
            panic!("Parse failed");
        }
    }
}
