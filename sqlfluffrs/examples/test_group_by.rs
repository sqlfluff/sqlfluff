use sqlfluffrs_lexer::{LexInput, Lexer};
use sqlfluffrs_dialects::Dialect;
use sqlfluffrs::parser::Parser;

fn main() {
    env_logger::init();

    // Test 1: Simple SELECT with GROUP BY
    let sql1 = "SELECT department, COUNT(*) FROM users GROUP BY department, status";
    println!("=== Test 1: GROUP BY ===");
    println!("SQL: {}", sql1);
    test_sql(sql1);

    println!("\n");

    // Test 2: Simple SELECT without GROUP BY (should work)
    let sql2 = "SELECT a, b FROM users";
    println!("=== Test 2: Simple SELECT ===");
    println!("SQL: {}", sql2);
    test_sql(sql2);
}

fn test_sql(raw: &str) {
    let dialect = Dialect::Ansi;

    let input = LexInput::String(raw.into());
    use sqlfluffrs_dialects::dialect::ansi::matcher::ANSI_LEXERS;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _) = lexer.lex(input, false);

    println!("\nTokens:");
    for (i, tok) in tokens.iter().enumerate() {
        println!("  [{:2}] {:20} | {:?}", i, tok.get_type(), tok.raw());
    }

    let mut parser = Parser::new(&tokens, dialect);

    println!("\nParsing...");
    match parser.call_rule("SelectStatementSegment", &[]) {
        Ok(ast) => {
            println!("✓ Parse succeeded!");
            println!("\nAST:");
            println!("{:#?}", ast);
        }
        Err(e) => {
            println!("✗ Parse failed: {:?}", e);
        }
    }
}
