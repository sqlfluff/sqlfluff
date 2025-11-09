use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_lexer::{LexInput, Lexer};
use sqlfluffrs_parser::parser::Parser;
use std::fs;
use std::str::FromStr;

fn main() {
    env_logger::Builder::from_env(env_logger::Env::default().default_filter_or("debug")).init();

    let sql = "ALTER PUBLICATION abc ADD TABLE def, TABLE ghi;";

    let dialect = Dialect::from_str("postgres").expect("Invalid dialect");

    // Lex
    let lexer = Lexer::new(None, dialect.get_lexers().to_vec());
    let (tokens, errors) = lexer.lex(LexInput::String(sql.to_string()), false);

    if !errors.is_empty() {
        eprintln!("Lex errors: {:?}", errors);
        return;
    }

    println!("Lexed {} tokens:", tokens.len());
    for (i, token) in tokens.iter().enumerate() {
        println!("  [{}] '{}' (type: {})", i, token.raw(), token.get_type());
    }

    println!("\n=== Parsing ===\n");

    // Parse
    let mut parser = Parser::new(&tokens, dialect);
    parser.set_cache_enabled(true);
    match parser.call_rule_as_root() {
        Ok(ast) => {
            println!("\n=== PARSE SUCCESS ===");
            println!(
                "AST (first 500 chars): {:?}",
                format!("{:?}", ast).chars().take(500).collect::<String>()
            );
        }
        Err(e) => {
            eprintln!("\n=== PARSE ERROR ===");
            eprintln!("{:?}", e);
        }
    }

    parser.print_cache_stats();
}
