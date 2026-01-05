use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_lexer::{LexInput, Lexer};
/// Detailed profiling with timing breakdown
///
/// Run with: cargo run --example profile_detailed --release
use sqlfluffrs_parser::parser::Parser;
use std::time::Instant;

fn main() {
    // Read the test SQL file
    let sql = std::fs::read_to_string("../test/fixtures/dialects/ansi/expression_recursion.sql")
        .expect("Failed to read SQL file");

    println!("SQL length: {} bytes", sql.len());
    println!();

    // Lex the SQL
    let dialect = Dialect::Ansi;
    let input = LexInput::String(sql);

    let lex_start = Instant::now();
    let lexer = Lexer::new(None, dialect.get_lexers().to_vec());
    let (tokens, _) = lexer.lex(input, false);
    let lex_time = lex_start.elapsed();

    println!("Lexing:");
    println!("  Time: {:?}", lex_time);
    println!("  Tokens: {}", tokens.len());
    println!();

    // Parse with timing
    let iterations = 100;
    println!("Parsing {} iterations...", iterations);

    let total_start = Instant::now();
    for i in 0..iterations {
        let parse_start = Instant::now();
        let mut parser = Parser::new(&tokens, dialect, hashbrown::HashMap::new());
        parser.set_cache_enabled(true);
        let _result = parser
            .call_rule_as_root_match_result()
            .expect("Parsing failed");
        let parse_time = parse_start.elapsed();

        if i == 0 {
            println!("  First iteration: {:?}", parse_time);
        }

        if i % 10 == 0 && i > 0 {
            print!(".");
            std::io::Write::flush(&mut std::io::stdout()).unwrap();
        }
    }
    let total_time = total_start.elapsed();

    println!();
    println!("Total parse time: {:?}", total_time);
    println!("Average per iteration: {:?}", total_time / iterations);
    println!(
        "Iterations per second: {:.2}",
        iterations as f64 / total_time.as_secs_f64()
    );
}
