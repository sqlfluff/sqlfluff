//! Utility functions for parser operations
//!
//! This module contains pure utility functions that don't depend on Parser state

use super::types::{Grammar, Node, ParseMode};
use crate::token::Token;

/// Check if a grammar element is optional.
///
/// Returns true if the grammar can match zero tokens successfully.
pub fn is_grammar_optional(grammar: &Grammar) -> bool {
    let result = match grammar {
        Grammar::Sequence { optional, .. } => *optional,
        Grammar::AnyNumberOf {
            optional,
            min_times,
            ..
        } => {
            log::debug!(
                "is_grammar_optional: AnyNumberOf optional={}, min_times={}",
                optional,
                min_times
            );
            *optional || *min_times == 0
        }
        Grammar::OneOf { optional, .. } => *optional,
        Grammar::Delimited { optional, .. } => *optional,
        Grammar::Bracketed { optional, .. } => *optional,
        Grammar::Ref { optional, .. } => *optional,
        Grammar::StringParser { optional, .. } => *optional,
        Grammar::MultiStringParser { optional, .. } => *optional,
        Grammar::TypedParser { optional, .. } => *optional,
        Grammar::RegexParser { optional, .. } => *optional,
        _ => false,
    };
    log::debug!("is_grammar_optional for {}: {}", grammar, result);
    result
}

/// Skip forward from start_idx to the next code token.
///
/// Returns the index of the next code token, or max_idx if none found.
pub fn skip_start_index_forward_to_code(
    tokens: &[Token],
    start_idx: usize,
    max_idx: usize,
) -> usize {
    for i in start_idx..max_idx {
        if i < tokens.len() && tokens[i].is_code() {
            return i;
        }
    }
    max_idx
}

/// Skip backward from stop_idx to the previous code token.
///
/// Returns the index after the last code token, or min_idx if none found.
pub fn skip_stop_index_backward_to_code(
    tokens: &[Token],
    stop_idx: usize,
    min_idx: usize,
) -> usize {
    if stop_idx <= min_idx {
        return min_idx;
    }

    for i in (min_idx..stop_idx).rev() {
        if i < tokens.len() && tokens[i].is_code() {
            return i + 1;
        }
    }
    min_idx
}

/// Apply parse_mode logic to match result.
///
/// In GREEDY mode, this creates UnparsableSegments for any unmatched code tokens.
/// In STRICT mode, returns the node as-is.
pub fn apply_parse_mode_to_result(
    tokens: &[Token],
    current_node: Node,
    current_pos: usize,
    max_idx: usize,
    parse_mode: ParseMode,
) -> Node {
    // If we're being strict, just return as-is
    if parse_mode == ParseMode::Strict {
        return current_node;
    }

    // Nothing unmatched anyway?
    if current_pos >= max_idx {
        return current_node;
    }

    // Check if all remaining segments are non-code
    let all_non_code = (current_pos..max_idx).all(|i| i >= tokens.len() || !tokens[i].is_code());

    if all_non_code {
        return current_node;
    }

    // Skip forward to next code token
    let trim_idx = skip_start_index_forward_to_code(tokens, current_pos, max_idx);

    // Create unparsable segment for GREEDY mode
    log::debug!(
        "Creating UnparsableSegment for positions {}..{} in GREEDY mode",
        trim_idx,
        max_idx
    );

    // Collect all tokens in the unparsable range
    let mut unparsable_children = Vec::new();
    for i in trim_idx..max_idx {
        if i < tokens.len() {
            let tok = &tokens[i];
            let tok_type = tok.get_type();
            if tok_type == "whitespace" {
                unparsable_children.push(Node::Whitespace(tok.raw().to_string(), i));
            } else if tok_type == "newline" {
                unparsable_children.push(Node::Newline(tok.raw().to_string(), i));
            } else {
                unparsable_children.push(Node::Token(
                    tok.get_type().to_string(),
                    tok.raw().to_string(),
                    i,
                ));
            }
        }
    }

    // Build expected message
    let expected = if max_idx < tokens.len() {
        format!("Nothing else before {:?}", tokens[max_idx].raw())
    } else {
        "Nothing else".to_string()
    };

    let unparsable_node = Node::Unparsable(expected, unparsable_children);

    // Combine current match with unparsable segment
    match current_node {
        Node::Empty => unparsable_node,
        Node::Sequence(mut children) => {
            children.push(unparsable_node);
            Node::Sequence(children)
        }
        other => Node::Sequence(vec![other, unparsable_node]),
    }
}
