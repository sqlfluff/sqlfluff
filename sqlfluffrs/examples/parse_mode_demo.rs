/// Demonstration of ParseMode enum and parse_mode() method
///
/// This example shows how to:
/// 1. Access the parse_mode of different grammar types
/// 2. Use the parse_mode() method to get the ParseMode for any grammar
///
/// Run with: cargo run --example parse_mode_demo --features python
use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_types::ParseMode;

fn main() {
    let dialect = Dialect::Ansi;

    // Get a grammar that has a parse_mode
    if let Some(grammar) = dialect.get_segment_grammar("SelectStatementSegment") {
        match &grammar {
            sqlfluffrs_types::RootGrammar::TableDriven { grammar_id, tables } => {
                println!(
                    "SelectStatementSegment is TableDriven with parse_mode: {:?}",
                    tables.get_inst(*grammar_id).parse_mode
                );
            }
            sqlfluffrs_types::RootGrammar::Arc(grammar) => {
                println!(
                    "SelectStatementSegment is Arc with parse_mode: {:?}",
                    grammar.parse_mode()
                );
            }
        }
    }

    // Get another grammar
    if let Some(grammar) = dialect.get_segment_grammar("BracketedColumnReferenceListGrammar") {
        match &grammar {
            sqlfluffrs_types::RootGrammar::TableDriven { grammar_id, tables } => {
                println!(
                    "BracketedColumnReferenceListGrammar is TableDriven with parse_mode: {:?}",
                    tables.get_inst(*grammar_id).parse_mode
                );
            }
            sqlfluffrs_types::RootGrammar::Arc(grammar) => {
                println!(
                    "BracketedColumnReferenceListGrammar is Arc with parse_mode: {:?}",
                    grammar.parse_mode()
                );
            }
        }
    }

    println!("\nParseMode variants:");
    println!("- Strict: {:?}", ParseMode::Strict);
    println!("- Greedy: {:?}", ParseMode::Greedy);
    println!("- GreedyOnceStarted: {:?}", ParseMode::GreedyOnceStarted);

    println!("\nDefault ParseMode: {:?}", ParseMode::default());
}
