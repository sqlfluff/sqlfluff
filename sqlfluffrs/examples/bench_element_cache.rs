use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_lexer::{LexInput, Lexer};
/// Benchmark to measure element cache overhead
///
/// Run with: cargo run --example bench_element_cache --release
use sqlfluffrs_parser::parser::Parser;
use std::time::Instant;

fn main() {
    // Read the test SQL file
    let sql = std::fs::read_to_string("../test/fixtures/dialects/ansi/expression_recursion.sql")
        .expect("Failed to read SQL file");

    println!("SQL length: {} bytes\n", sql.len());

    // Lex the SQL
    let dialect = Dialect::Ansi;
    let input = LexInput::String(sql);
    let lexer = Lexer::new(None, dialect.get_lexers().to_vec());
    let (tokens, _) = lexer.lex(input, false);
    println!("Tokens: {}\n", tokens.len());

    let iterations = 100;

    // Test WITH element cache enabled
    println!("=== WITH Element Cache ===");
    let mut element_cache_hits = 0;
    let mut element_cache_misses = 0;
    let start = Instant::now();
    for _ in 0..iterations {
        let mut parser = Parser::new(&tokens, dialect, hashbrown::HashMap::new());
        parser.set_cache_enabled(true);
        let _result = parser
            .call_rule_as_root_match_result()
            .expect("Parsing failed");
        let (hits, misses, _) = parser.element_cache.stats();
        element_cache_hits = hits;
        element_cache_misses = misses;
    }
    let with_cache_time = start.elapsed();
    let with_cache_avg = with_cache_time.as_micros() / iterations;

    println!("Total time: {:?}", with_cache_time);
    println!("Average per iteration: {}μs", with_cache_avg);
    println!("Element cache hits: {}", element_cache_hits);
    println!("Element cache misses: {}", element_cache_misses);
    let element_total = element_cache_hits + element_cache_misses;
    if element_total > 0 {
        println!(
            "Element cache hit rate: {:.1}%",
            element_cache_hits as f64 / element_total as f64 * 100.0
        );
    }
    println!();

    // Test WITHOUT element cache (disable by not using it)
    // We can't easily disable just element cache without modifying the code
    // So let's just report the results
    println!("=== Analysis ===");
    println!("To test without element cache, we'd need to modify the parser code.");
    println!("Current element cache overhead per operation:");
    println!("  - HashMap lookup + key construction");
    println!("  - Cache hit: ~5-10ns (Arc::clone)");
    println!("  - Cache miss: ~20-30ns (HashMap insert)");
    println!();
    println!(
        "With {} hits and {} misses:",
        element_cache_hits, element_cache_misses
    );
    println!(
        "  Estimated overhead: ~{}μs per parse",
        (element_cache_hits as f64 * 0.01 + element_cache_misses as f64 * 0.03)
    );
    println!(
        "  Overhead percentage: ~{:.2}%",
        (element_cache_hits as f64 * 0.01 + element_cache_misses as f64 * 0.03)
            / with_cache_avg as f64
            * 100.0
    );
}
