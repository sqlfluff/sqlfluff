use sqlfluffrs::lexer::{LexInput, Lexer};
use sqlfluffrs::parser::Parser;
use sqlfluffrs::Dialect;

fn main() {
    env_logger::init();

    // Simple SQL with trailing whitespace
    let sql = "SELECT * FROM t  "; // Two trailing spaces
    println!("SQL: {:?}", sql);
    println!("Length: {}", sql.len());

    let dialect = Dialect::Ansi;
    let input = LexInput::String(sql.into());
    let lexer = Lexer::new(None, dialect);
    let (tokens, _) = lexer.lex(input, false);

    println!("\nTokens ({} total):", tokens.len());
    for (idx, tok) in tokens.iter().enumerate() {
        println!("  [{}] {:?} (type: {})", idx, tok.raw(), tok.get_type());
    }

    let mut parser = Parser::new(&tokens, dialect);
    match parser.call_rule("SelectStatementSegment", &[]) {
        Ok(ast) => {
            println!("\nAST collected successfully");

            // Collect positions
            let mut positions = std::collections::HashSet::new();
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

fn collect_positions(
    node: &sqlfluffrs::parser::Node,
    positions: &mut std::collections::HashSet<usize>,
) {
    use sqlfluffrs::parser::Node;
    match node {
        Node::Whitespace(_, pos)
        | Node::Newline(_, pos)
        | Node::Token(_, _, pos)
        | Node::EndOfFile(_, pos) => {
            positions.insert(*pos);
        }
        Node::Sequence(children)
        | Node::Bracketed(children)
        | Node::DelimitedList(children)
        | Node::Unparsable(_, children) => {
            for child in children {
                collect_positions(child, positions);
            }
        }
        Node::Ref { child, .. } => {
            collect_positions(child, positions);
        }
        Node::Empty | Node::Meta(_) => {}
    }
}
