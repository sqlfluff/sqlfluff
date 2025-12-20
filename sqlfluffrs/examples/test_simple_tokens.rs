use hashbrown::HashSet;
use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_lexer::{LexInput, Lexer};
use sqlfluffrs_parser::parser::Parser;

fn main() {
    env_logger::init();

    // Simple SQL with trailing whitespace
    let sql = "SELECT * FROM t  "; // Two trailing spaces
    println!("SQL: {:?}", sql);
    println!("Length: {}", sql.len());

    let dialect = Dialect::Ansi;
    let input = LexInput::String(sql.into());
    use sqlfluffrs_dialects::dialect::ansi::matcher::ANSI_LEXERS;
    let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
    let (tokens, _) = lexer.lex(input, false);

    println!("\nTokens ({} total):", tokens.len());
    for (idx, tok) in tokens.iter().enumerate() {
        println!("  [{}] {:?} (type: {})", idx, tok.raw(), tok.get_type());
    }

    let mut parser = Parser::new(&tokens, dialect, hashbrown::HashMap::new());
    match parser.call_rule("SelectStatementSegment", &[]) {
        Ok(ast) => {
            println!("\nAST collected successfully");

            // Collect positions
            let mut positions = HashSet::new();
            collect_positions(&ast, &mut positions);

            println!("\nPositions in AST: {:?}", {
                let mut v: Vec<_> = positions.iter().cloned().collect();
                v.sort();
                v
            });

            // Check missing
            let mut missing = Vec::new();
            for idx in 0..tokens.len() {
                if !positions.contains(&idx) {
                    missing.push(idx);
                }
            }

            if !missing.is_empty() {
                println!("\nMISSING positions: {:?}", missing);
                for idx in missing {
                    println!(
                        "  [{}] {:?} (type: {})",
                        idx,
                        tokens[idx].raw(),
                        tokens[idx].get_type()
                    );
                }
            } else {
                println!("\nAll tokens present in AST! ✓");
            }
        }
        Err(e) => {
            log::debug!("Parse error: {:?}", e);
        }
    }
}

fn collect_positions(node: &sqlfluffrs_parser::parser::Node, positions: &mut HashSet<usize>) {
    use sqlfluffrs_parser::parser::Node;
    match node {
        Node::Whitespace { token_idx: pos, .. }
        | Node::Newline { token_idx: pos, .. }
        | Node::Token { token_idx: pos, .. }
        | Node::Comment { token_idx: pos, .. }
        | Node::EndOfFile { token_idx: pos, .. } => {
            positions.insert(*pos);
        }
        Node::Sequence { children }
        | Node::Bracketed { children, .. }
        | Node::DelimitedList { children }
        | Node::Unparsable {
            expected_message: _,
            children,
        } => {
            for child in children {
                collect_positions(child, positions);
            }
        }
        Node::Ref { child, .. } => {
            collect_positions(child, positions);
        }
        Node::Empty | Node::Meta { .. } => {}
    }
}
