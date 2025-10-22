//! Common test helpers and utilities

use sqlfluffrs::parser::{Node, ParseError, Parser};
use sqlfluffrs::token::Token;
use sqlfluffrs::{
    lexer::{LexInput, Lexer},
    Dialect,
};

/// Macro to run a test with a larger stack size (16MB)
/// This prevents stack overflow on deeply nested or complex queries
#[macro_export]
macro_rules! with_larger_stack {
    ($test_fn:expr) => {{
        std::thread::Builder::new()
            .stack_size(16 * 1024 * 1024) // 16MB stack
            .spawn($test_fn)
            .expect("Failed to spawn thread")
            .join()
            .expect("Thread panicked")
    }};
}

/// Verify that all tokens from the lexer appear in the AST
pub fn verify_all_tokens_in_ast(raw: &str, ast: &Node, tokens: &[Token]) -> Result<(), String> {
    // Collect all token positions from the AST
    let mut ast_positions = std::collections::HashSet::new();
    collect_token_positions(ast, &mut ast_positions);

    log::debug!(
        "DEBUG: Total tokens: {}, Positions in AST: {:?}",
        tokens.len(),
        {
            let mut sorted: Vec<_> = ast_positions.iter().copied().collect();
            sorted.sort();
            sorted
        }
    );

    // Check which tokens are missing
    let mut missing = Vec::new();
    for (idx, token) in tokens.iter().enumerate() {
        if !ast_positions.contains(&idx) {
            missing.push((idx, token.clone()));
        }
    }

    if !missing.is_empty() {
        let mut msg = format!("\nMissing {} tokens from AST:\n", missing.len());
        msg.push_str(&format!("SQL: {}\n\n", raw));
        for (idx, token) in missing {
            msg.push_str(&format!(
                "  Position {}: {:?} (type: {})\n",
                idx,
                token.raw(),
                token.get_type()
            ));
        }
        return Err(msg);
    }

    Ok(())
}

/// Recursively collect all token positions from a Node
pub fn collect_token_positions(node: &Node, positions: &mut std::collections::HashSet<usize>) {
    match node {
        Node::Whitespace(_, pos) | Node::Newline(_, pos) | Node::Token(_, _, pos) => {
            positions.insert(*pos);
        }
        Node::EndOfFile(_, pos) => {
            log::debug!(
                "collect_token_positions: Found EndOfFile at position {}",
                pos
            );
            positions.insert(*pos);
        }
        Node::Sequence(children)
        | Node::DelimitedList(children)
        | Node::File(children)
        | Node::Unparsable(_, children)
        | Node::Bracketed(children) => {
            for child in children {
                collect_token_positions(child, positions);
            }
        }
        Node::Ref { child, .. } => {
            collect_token_positions(child, positions);
        }
        Node::Empty | Node::Meta(_) => {
            // No tokens
        }
    }
}

/// Parse SQL with a given dialect and segment type
pub fn parse_sql(raw: &str, segment: &str, dialect: Dialect) -> Result<Node, ParseError> {
    let input = LexInput::String(raw.into());
    let lexer = Lexer::new(None, dialect);
    let (tokens, _errors) = lexer.lex(input, false);
    let mut parser = Parser::new(&tokens, dialect);
    parser.call_rule(segment, &[])
}

/// Parse SQL and verify all tokens are present in the AST
pub fn parse_and_verify_tokens(
    raw: &str,
    segment: &str,
    dialect: Dialect,
) -> Result<(), ParseError> {
    let input = LexInput::String(raw.into());
    let lexer = Lexer::new(None, dialect);
    let (tokens, _) = lexer.lex(input, false);
    let mut parser = Parser::new(&tokens, dialect);
    let ast = parser.call_rule(segment, &[])?;

    verify_all_tokens_in_ast(raw, &ast, &tokens).map_err(ParseError::new)?;

    Ok(())
}
