use sqlfluffrs_dialects::dialect::Dialect;
use sqlfluffrs_lexer::lexer::Lexer;
use sqlfluffrs_parser::parser::core::Parser;
use std::time::Instant;

fn main() {
    // Read the test SQL
    let sql = std::fs::read_to_string("../test/fixtures/dialects/ansi/expression_recursion.sql")
        .expect("Failed to read SQL file");

    println!("SQL: {} bytes", sql.len());

    // Create dialect and lexer
    let dialect = Dialect::Ansi;
    let lexer = Lexer::new(&dialect);
    let lex_result = lexer.lex(sqlfluffrs_lexer::lexer::LexInput::String(&sql));
    let tokens = lex_result.elements();
    println!("Tokens: {}", tokens.len());

    // Create parser
    let mut parser = Parser::new(&dialect);

    // Warmup
    for _ in 0..5 {
        let _ = parser.call_rule_as_root_match_result("FileSegment", &tokens);
    }

    // Profile parse with detailed timing
    const ITERATIONS: usize = 50;
    let mut total_time = 0u128;

    println!("\nProfiling {} iterations...", ITERATIONS);

    for i in 0..ITERATIONS {
        let start = Instant::now();
        let result = parser.call_rule_as_root_match_result("FileSegment", &tokens);
        let elapsed = start.elapsed().as_micros();
        total_time += elapsed;

        if i < 5 || i >= ITERATIONS - 5 {
            println!("  Iteration {}: {}μs", i + 1, elapsed);
        } else if i == 5 {
            println!("  ...");
        }

        assert!(result.is_match(), "Parse failed at iteration {}", i + 1);
    }

    let avg_micros = total_time / ITERATIONS as u128;
    println!("\nAverage: {}μs ({}ms)", avg_micros, avg_micros / 1000);
    println!("Total: {}ms", total_time / 1000);
    println!("Iterations/sec: {:.2}", 1_000_000.0 / avg_micros as f64);

    // Cache statistics
    println!("\nCache statistics:");
    let stats = parser.cache_statistics();
    println!("  Table cache hits: {}", stats.table_hits);
    println!("  Table cache misses: {}", stats.table_misses);
    let table_total = stats.table_hits + stats.table_misses;
    if table_total > 0 {
        println!(
            "  Table hit rate: {:.1}%",
            100.0 * stats.table_hits as f64 / table_total as f64
        );
    }

    println!("  Element cache hits: {}", stats.element_hits);
    println!("  Element cache misses: {}", stats.element_misses);
    let element_total = stats.element_hits + stats.element_misses;
    if element_total > 0 {
        println!(
            "  Element hit rate: {:.1}%",
            100.0 * stats.element_hits as f64 / element_total as f64
        );
    }
}
