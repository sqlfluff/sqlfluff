use sqlfluffrs_dialects::dialect::ansi::matcher::ANSI_LEXERS;
use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_lexer::{LexInput, Lexer};
use sqlfluffrs_parser::parser::Parser;

#[test]
fn test_cast_with_whitespaces_debug() {
    env_logger::try_init().ok();

    let sql = r#"-- ansi_cast_with_whitespaces.sql
/* Several valid queries where there is whitespace surrounding the ANSI
cast operator (::) */

-- query from https://github.com/sqlfluff/sqlfluff/issues/2720
SELECT amount_of_honey :: FLOAT
FROM bear_inventory;


-- should be able to support an arbitrary amount of whitespace
SELECT amount_of_honey        ::        FLOAT
FROM bear_inventory;"#;

    let input = LexInput::String(sql.to_string());
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, lex_errors) = lexer.lex(input, false);

    println!("\n=== Total tokens: {} ===", tokens.len());
    for (i, tok) in tokens.iter().enumerate() {
        if tok.is_code() {
            println!("{:3}: {:20} {:?}", i, tok.token_type, tok.raw);
        }
    }

    let dialect = Dialect::Ansi;
    let mut parser = Parser::new(&tokens, dialect);
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

            if parser.pos < tokens.len() {
                println!("\n!!! WARNING: Parser did not consume all tokens !!!");
                println!("Remaining tokens:");
                for i in parser.pos..tokens.len().min(parser.pos + 10) {
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
    assert!(
        parser.pos >= tokens.len() - 1,
        "Parser did not consume all tokens. Stopped at {} / {} tokens (last index: {})",
        parser.pos,
        tokens.len(),
        tokens.len() - 1
    );
}

#[test]
fn test_select_from_debug() {
    env_logger::try_init().ok();

    let sql = r#"SELECT amount_of_honey FROM bear_inventory;"#;

    let input = LexInput::String(sql.to_string());
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, lex_errors) = lexer.lex(input, false);

    println!("\n=== Total tokens: {} ===", tokens.len());
    for (i, tok) in tokens.iter().enumerate() {
        if tok.is_code() {
            println!("{:3}: {:20} {:?}", i, tok.token_type, tok.raw);
        }
    }

    let dialect = Dialect::Ansi;
    let mut parser = Parser::new(&tokens, dialect);
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

            if parser.pos < tokens.len() {
                println!("\n!!! WARNING: Parser did not consume all tokens !!!");
                println!("Remaining tokens:");
                for i in parser.pos..tokens.len().min(parser.pos + 10) {
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
    assert!(
        parser.pos >= tokens.len() - 1,
        "Parser did not consume all tokens. Stopped at {} / {} tokens (last index: {})",
        parser.pos,
        tokens.len(),
        tokens.len() - 1
    );
}

fn run_sql_debug(sql: &str) {
    env_logger::try_init().ok();

    let input = LexInput::String(sql.to_string());
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _lex_errors) = lexer.lex(input, false);

    println!("\n=== Total tokens: {} ===", tokens.len());
    for (i, tok) in tokens.iter().enumerate() {
        println!("{:3}: {:20} {:?}", i, tok.token_type, tok.raw);
    }

    let dialect = Dialect::Ansi;
    let mut parser = Parser::new(&tokens, dialect);
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

            if parser.pos < tokens.len() {
                println!("\n!!! WARNING: Parser did not consume all tokens !!!");
                println!("Remaining tokens:");
                for i in parser.pos..tokens.len().min(parser.pos + 10) {
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
    assert!(
        parser.pos >= tokens.len() - 1,
        "Parser did not consume all tokens. Stopped at {} / {} tokens (last index: {})",
        parser.pos,
        tokens.len(),
        tokens.len() - 1
    );
}

#[test]
fn test_cast_with_select_b_context_debug() {
    let path = format!(
        "{}/../test/fixtures/dialects/ansi/select_b.sql",
        env!("CARGO_MANIFEST_DIR")
    );
    let sql = std::fs::read_to_string(&path).unwrap_or_else(|_| panic!("Failed to read {}", path));
    run_sql_debug(&sql);
}
