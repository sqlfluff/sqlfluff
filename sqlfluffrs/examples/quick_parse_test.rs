use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_lexer::{LexInput, Lexer};
use sqlfluffrs_parser::parser::Parser;
use std::fs;
use std::str::FromStr;

fn main() {
    env_logger::init();

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

    println!("Lexed {} tokens", tokens.len());

    // Parse
    let mut parser = Parser::new(&tokens, dialect, hashbrown::HashMap::new());
    match parser.call_rule_as_root() {
        Ok(ast) => {
            println!("\n=== PARSE SUCCESS ===");

            // Count statements by traversing the AST
            fn count_statements(node: &sqlfluffrs_parser::parser::Node) -> usize {
                match node {
                    sqlfluffrs_parser::parser::Node::Ref { name, child, .. }
                        if name == "StatementSegment" =>
                    {
                        1
                    }
                    sqlfluffrs_parser::parser::Node::Ref { child, .. } => count_statements(child),
                    sqlfluffrs_parser::parser::Node::Sequence { children } => {
                        children.iter().map(count_statements).sum()
                    }
                    sqlfluffrs_parser::parser::Node::DelimitedList { children } => {
                        children.iter().map(count_statements).sum()
                    }
                    sqlfluffrs_parser::parser::Node::Bracketed { children, .. } => {
                        children.iter().map(count_statements).sum()
                    }
                    _ => 0,
                }
            }

            let statement_count = count_statements(&ast);
            println!("Parsed {} statements successfully!", statement_count);
        }
        Err(e) => {
            eprintln!("\n=== PARSE ERROR ===");
            eprintln!("{:?}", e);
        }
    }
}
