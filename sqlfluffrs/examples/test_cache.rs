/// Test cache functionality in the parser
use sqlfluffrs::{
    lexer::{LexInput, Lexer},
    parser::Parser,
    Dialect,
};

fn main() {
    // Parse a simple SELECT statement twice
    let sql = "SELECT a FROM b";
    let input = LexInput::String(sql.to_string());
    let dialect = Dialect::Ansi;

    let lexer = Lexer::new(None, dialect);
    let (tokens, _errors) = lexer.lex(input, false);

    let mut parser = Parser::new(&tokens, dialect);

    // First parse - should populate cache
    println!("\n=== First Parse (should populate cache) ===");
    match parser.call_rule("SelectStatementSegment", &[]) {
        Ok(_ast) => {
            println!("✓ Parse successful");
            parser.print_cache_stats();
        }
        Err(e) => {
            eprintln!("✗ Parse failed: {:?}", e);
            parser.print_cache_stats();
        }
    }

    // Reset position
    parser.pos = 0;

    // Second parse - should hit cache heavily
    println!("\n=== Second Parse (should hit cache) ===");
    match parser.call_rule("SelectStatementSegment", &[]) {
        Ok(_ast) => {
            println!("✓ Parse successful");
            parser.print_cache_stats();
        }
        Err(e) => {
            eprintln!("✗ Parse failed: {:?}", e);
            parser.print_cache_stats();
        }
    }
}
