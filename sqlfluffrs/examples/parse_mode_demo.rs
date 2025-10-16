/// Demonstration of ParseMode enum and parse_mode() method
///
/// This example shows how to:
/// 1. Access the parse_mode of different grammar types
/// 2. Use the parse_mode() method to get the ParseMode for any grammar
///
/// Run with: cargo run --example parse_mode_demo --features python

use sqlfluffrs::{Dialect, ParseMode};

fn main() {
    let dialect = Dialect::Ansi;

    // Get a grammar that has a parse_mode
    if let Some(grammar) = dialect.get_segment_grammar("SelectStatementSegment") {
        println!("SelectStatementSegment parse_mode: {:?}", grammar.parse_mode());
    }

    // Get another grammar
    if let Some(grammar) = dialect.get_segment_grammar("BracketedColumnReferenceListGrammar") {
        println!("BracketedColumnReferenceListGrammar parse_mode: {:?}", grammar.parse_mode());
    }

    println!("\nParseMode variants:");
    println!("- Strict: {:?}", ParseMode::Strict);
    println!("- Greedy: {:?}", ParseMode::Greedy);
    println!("- GreedyOnceStarted: {:?}", ParseMode::GreedyOnceStarted);

    println!("\nDefault ParseMode: {:?}", ParseMode::default());
}
