use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_lexer::{LexInput, Lexer};
use sqlfluffrs_parser::parser::Parser;
use std::str::FromStr;

// TODO: Enable this test when the Exasol adapter script is ready
// #[test]
fn test_exasol_adapter_script() {
    env_logger::Builder::from_env(env_logger::Env::default().default_filter_or("info"))
        .is_test(true)
        .try_init()
        .ok();

    // Test if the regex itself matches (WITH the \A anchor that regex_lexer adds)
    let test_regex = regex::Regex::new(r"(?s)\A(?:\n/\n|\n/$)").unwrap();
    let test_input = "\n/\n";
    println!(
        "Testing ANCHORED regex pattern r\"(?s)\\A(?:\\n/\\n|\\n/$)\" against input {:?}",
        test_input
    );
    if let Some(m) = test_regex.find(test_input) {
        println!(
            "  Match found: {:?} at position {}-{}",
            m.as_str(),
            m.start(),
            m.end()
        );
        println!("  Match starts at position 0? {}", m.start() == 0);
    } else {
        println!("  No match!");
    }

    // Now test what happens with is_match() vs find()
    println!("\nTesting is_match vs find:");
    println!("  is_match(): {}", test_regex.is_match(test_input));
    println!(
        "  find() starts at 0: {}",
        test_regex
            .find(test_input)
            .map(|m| m.start() == 0)
            .unwrap_or(false)
    );

    // Test just the terminator part
    let sql = "\n/\n";

    println!("SQL: {}", sql);

    // Lex
    let dialect = Dialect::from_str("exasol").expect("Invalid dialect");
    let input = LexInput::String(sql.to_string());
    let lexer = Lexer::new(None, dialect.get_lexers().to_vec());
    let (tokens, errors) = lexer.lex(input, false);

    assert!(errors.is_empty(), "Lexer errors: {:?}", errors);

    println!("Matchers used:");
    for matcher in dialect.get_lexers() {
        println!("  - {:?}", matcher.name);
    }

    println!("\n=== TOKENS ===");
    for (idx, token) in tokens.iter().enumerate() {
        println!("  {}: Token {{ token_type: {:?}, raw: {:?}, instance_types: {:?}, class_types: {:?} }}",
                 idx, token.token_type, token.raw, token.instance_types, token.class_types);
    }

    // Parse
    let mut parser = Parser::new(&tokens, dialect);
    let result = parser.call_rule_as_root();

    match result {
        Ok(node) => {
            println!("\n=== PARSE RESULT ===");
            println!("Node type: {:?}", std::mem::discriminant(&node));

            // Convert to YAML-like structure (code_only=true, show_raw=true, include_meta=false)
            let record = node.as_record(true, true, false);
            println!("\n=== AS RECORD (YAML structure) ===");
            println!("{:#?}", record);
        }
        Err(e) => {
            println!("\n=== PARSE ERROR ===");
            println!("{:?}", e);
            panic!("Parse failed");
        }
    }
}
