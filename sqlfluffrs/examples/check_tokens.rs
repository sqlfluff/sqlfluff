use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_lexer::{LexInput, Lexer};
use std::fs;
use std::str::FromStr;

fn main() {
    let sql = fs::read_to_string("../test/fixtures/dialects/duckdb/create_table.sql")
        .expect("Failed to read SQL file");

    let dialect = Dialect::from_str("duckdb").expect("Invalid dialect");

    // Lex
    let lexer = Lexer::new(None, dialect.get_lexers().to_vec());
    let (tokens, errors) = lexer.lex(LexInput::String(sql.clone()), false);

    if !errors.is_empty() {
        eprintln!("Lex errors: {:?}", errors);
        return;
    }

    println!("Total tokens: {}", tokens.len());

    // Find statement terminators
    let semicolon_positions: Vec<usize> = tokens
        .iter()
        .enumerate()
        .filter(|(_, t)| t.get_type() == "statement_terminator")
        .map(|(i, _)| i)
        .collect();

    println!(
        "Found {} semicolons at positions: {:?}",
        semicolon_positions.len(),
        semicolon_positions
    );

    // Show context around token 631
    if tokens.len() > 631 {
        println!("\nContext around token 631:");
        for i in 625..640.min(tokens.len()) {
            println!(
                "  [{}] {:?} (type: {})",
                i,
                tokens[i].raw(),
                tokens[i].get_type()
            );
        }
    }

    // Show context around token 638 (where generated column statements start)
    if tokens.len() > 638 {
        println!("\nContext around token 638 (expected start of generated column statements):");
        for i in 635..650.min(tokens.len()) {
            println!(
                "  [{}] {:?} (type: {})",
                i,
                tokens[i].raw(),
                tokens[i].get_type()
            );
        }
    }
}
