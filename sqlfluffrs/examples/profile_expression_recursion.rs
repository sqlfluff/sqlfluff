use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_lexer::{LexInput, Lexer};
/// Profile parsing of expression_recursion.sql
///
/// Run with: cargo flamegraph --example profile_expression_recursion --release
use sqlfluffrs_parser::parser::Parser;

fn main() {
    // Read the test SQL file (path relative to workspace root)
    let sql = std::fs::read_to_string("../test/fixtures/dialects/ansi/expression_recursion.sql")
        .expect("Failed to read SQL file");

    // Lex the SQL
    let dialect = Dialect::Ansi;
    let input = LexInput::String(sql);
    let lexer = Lexer::new(None, dialect.get_lexers().to_vec());
    let (tokens, _) = lexer.lex(input, false);

    // Parse multiple times to get good profiling data
    let iterations = 100;
    println!("Profiling {} iterations...", iterations);
    for i in 0..iterations {
        let mut parser = Parser::new(&tokens, dialect, hashbrown::HashMap::new());
        parser.set_cache_enabled(true);
        let _result = parser
            .call_rule_as_root_match_result()
            .expect("Parsing failed");

        if i % 10 == 0 {
            print!(".");
            std::io::Write::flush(&mut std::io::stdout()).unwrap();
        }
    }
    println!("\nProfiling complete!");
}
