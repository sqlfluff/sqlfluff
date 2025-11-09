use hashbrown::HashSet;
use sqlfluffrs_dialects::dialect::ansi::matcher::ANSI_LEXERS;
use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_lexer::{LexInput, Lexer};
use sqlfluffrs_parser::parser::{Node, Parser};

fn collect_token_positions(node: &Node, positions: &mut HashSet<usize>) {
    match node {
        Node::Whitespace { token_idx: pos, .. }
        | Node::Newline { token_idx: pos, .. }
        | Node::Token { token_idx: pos, .. }
        | Node::EndOfFile { token_idx: pos, .. } => {
            positions.insert(*pos);
        }
        Node::Sequence { children }
        | Node::DelimitedList { children }
        | Node::Unparsable { children, .. }
        | Node::Bracketed { children, .. } => {
            for child in children {
                collect_token_positions(child, positions);
            }
        }
        Node::Ref { child, .. } => {
            collect_token_positions(child, positions);
        }
        Node::Empty | Node::Meta { .. } => {}
    }
}

#[test]
fn debug_delimited() {
    use std::io::Write;
    let _ = env_logger::builder()
        .format(|buf, record| writeln!(buf, "{}: {}", record.level(), record.args()))
        .filter_level(log::LevelFilter::Debug)
        .is_test(true)
        .try_init();

    let sql = "SELECT col1, col2, col3, col4, col5 FROM table_name";

    let input = LexInput::String(sql.into());
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _) = lexer.lex(input, false);

    println!("\n=== TOKENS ===");
    for (idx, token) in tokens.iter().enumerate() {
        println!(
            "Token {}: {:?} (type: {})",
            idx,
            token.raw(),
            token.get_type()
        );
    }

    let mut parser = Parser::new(&tokens, Dialect::Ansi);
    let ast = parser.call_rule("SelectStatementSegment", &[]).unwrap();

    let mut ast_positions = HashSet::new();
    collect_token_positions(&ast, &mut ast_positions);

    println!("\n=== AST POSITIONS ===");
    let mut sorted: Vec<_> = ast_positions.iter().copied().collect();
    sorted.sort();
    println!("{:?}", sorted);

    println!("\n=== MISSING POSITIONS ===");
    for (idx, token) in tokens.iter().enumerate() {
        if !ast_positions.contains(&idx) && token.get_type() != "end_of_file" {
            println!(
                "Missing {}: {:?} (type: {})",
                idx,
                token.raw(),
                token.get_type()
            );
        }
    }
}

#[test]
fn debug_bracketed() {
    let sql = "SELECT (a + b) * (c - d) FROM table_name";

    let input = LexInput::String(sql.into());
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _) = lexer.lex(input, false);

    println!("\n=== TOKENS ===");
    for (idx, token) in tokens.iter().enumerate() {
        println!(
            "Token {}: {:?} (type: {})",
            idx,
            token.raw(),
            token.get_type()
        );
    }

    let mut parser = Parser::new(&tokens, Dialect::Ansi);
    let ast = parser.call_rule("SelectStatementSegment", &[]).unwrap();

    let mut ast_positions = HashSet::new();
    collect_token_positions(&ast, &mut ast_positions);

    println!("\n=== AST POSITIONS ===");
    let mut sorted: Vec<_> = ast_positions.iter().copied().collect();
    sorted.sort();
    println!("{:?}", sorted);

    println!("\n=== MISSING POSITIONS ===");
    for (idx, token) in tokens.iter().enumerate() {
        if !ast_positions.contains(&idx) && token.get_type() != "end_of_file" {
            println!(
                "Missing {}: {:?} (type: {})",
                idx,
                token.raw(),
                token.get_type()
            );
        }
    }
}
