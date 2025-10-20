//! Helper methods for the Parser
//!
//! This module contains utility methods used by both iterative and recursive parsers
//! including token navigation, whitespace handling, and terminator checking.

use crate::token::Token;
use super::{Grammar, Node, ParseError};
use super::core::Parser;

impl<'a> Parser<'a> {
    /// Prune options based on simple matchers before attempting full parse.
    ///
    /// This is the Rust equivalent of Python's `prune_options()` function.
    /// It filters the list of grammar options to only those that could possibly
    /// match the current token, based on quick checks of raw strings and types.
    pub(crate) fn prune_options<'g>(&self, options: &'g [Grammar]) -> Vec<&'g Grammar> {
        // Find first code (non-whitespace) token from current position
        let first_code_token = self.tokens.iter().skip(self.pos).find(|t| t.is_code());

        // If no code token found, can't prune - return all options
        let Some(first_token) = first_code_token else {
            return options.iter().collect();
        };

        // Get token properties for matching
        let first_raw = first_token.raw().to_uppercase();
        let first_type = first_token.get_type();

        log::debug!(
            "Pruning {} options at pos {} (token: '{}', type: {})",
            options.len(),
            self.pos,
            first_raw,
            first_type
        );

        let mut pruned = Vec::new();

        for opt in options {
            // Try to get simple representation
            match opt.simple() {
                None => {
                    // Complex grammar - must try full match
                    log::debug!("  Keeping complex grammar: {}", opt);
                    pruned.push(opt);
                }
                Some(simple) => {
                    // Check if simple matches current token
                    if simple.could_match(first_token) {
                        log::debug!("  Keeping matched grammar: {}", opt);
                        pruned.push(opt);
                    } else {
                        log::debug!("  PRUNED grammar: {}", opt);
                    }
                }
            }
        }

        log::debug!(
            "Pruned from {} to {} options ({:.1}% reduction)",
            options.len(),
            pruned.len(),
            100.0 * (1.0 - pruned.len() as f64 / options.len() as f64)
        );

        pruned
    }

    /// Print cache statistics
    pub fn print_cache_stats(&self) {
        let (hits, misses, hit_rate) = self.parse_cache.stats();
        eprintln!("Parse Cache Statistics:");
        eprintln!("  Hits: {}", hits);
        eprintln!("  Misses: {}", misses);
        eprintln!("  Hit Rate: {:.2}%", hit_rate * 100.0);
    }

    /// Peek at the current token without consuming it
    pub fn peek(&self) -> Option<&Token> {
        self.tokens.get(self.pos)
    }

    /// Consume the current token and advance position
    pub fn bump(&mut self) {
        self.pos += 1;
    }

    /// Check if we've reached the end of the token stream
    pub fn is_at_end(&self) -> bool {
        self.pos >= self.tokens.len()
    }

    /// Collect all transparent tokens (whitespace, newlines) as nodes
    pub fn collect_transparent(&mut self, allow_gaps: bool) -> Vec<Node> {
        let mut transparent_nodes = Vec::new();

        if !allow_gaps {
            return transparent_nodes;
        }

        while let Some(tok) = self.peek() {
            if tok.is_code() {
                break;
            }

            let token_pos = self.pos;

            // Skip if already collected
            if self.collected_transparent_positions.contains(&token_pos) {
                self.bump();
                continue;
            }

            let tok_type = tok.get_type();
            let node = if tok_type == "whitespace" {
                Node::Whitespace(tok.raw(), token_pos)
            } else if tok_type == "newline" {
                Node::Newline(tok.raw(), token_pos)
            } else if tok_type == "end_of_file" {
                Node::EndOfFile(tok.raw(), token_pos)
            } else {
                Node::Code(tok.raw(), token_pos) // Fallback for other non-code tokens
            };

            log::debug!(
                "TRANSPARENT collecting token at pos {}: {:?}",
                token_pos,
                tok
            );
            transparent_nodes.push(node);
            self.collected_transparent_positions.insert(token_pos);
            self.bump();
        }

        transparent_nodes
    }

    /// Skip all transparent tokens (whitespace, newlines) without collecting them
    pub fn skip_transparent(&mut self, allow_gaps: bool) {
        if !allow_gaps {
            return;
        }
        while let Some(tok) = self.peek() {
            match tok {
                tok if !tok.is_code() => {
                    log::debug!("NOCODE skipping token: {:?}", tok);
                    self.bump()
                }
                _ => break,
            }
        }
    }

    /// Move an index forward through tokens until tokens[index] is code.
    /// Returns the index of the first code token, or max_idx if none found.
    pub(crate) fn skip_start_index_forward_to_code(&self, start_idx: usize, max_idx: usize) -> usize {
        for _idx in start_idx..max_idx {
            if self.tokens[_idx].is_code() {
                return _idx;
            }
        }
        max_idx
    }

    /// Move an index backward through tokens until tokens[index - 1] is code.
    /// Returns the index after the last code token, or min_idx if none found.
    pub(crate) fn skip_stop_index_backward_to_code(&self, stop_idx: usize, min_idx: usize) -> usize {
        for _idx in (min_idx + 1..=stop_idx).rev() {
            if self.tokens[_idx - 1].is_code() {
                return _idx;
            }
        }
        min_idx
    }

    /// Trim forward segments based on terminators.
    ///
    /// Given a forward set of segments, find the first terminator and return
    /// the index to use as max_idx (trimmed to last code segment before terminator).
    ///
    /// If no terminators are found, returns the original tokens.len().
    pub(crate) fn trim_to_terminator(&mut self, start_idx: usize, terminators: &[Grammar]) -> usize {
        if start_idx >= self.tokens.len() {
            return self.tokens.len();
        }

        let saved_pos = self.pos;
        self.pos = start_idx;

        // Check if already at a terminator immediately
        if self.is_terminated(terminators) {
            self.pos = saved_pos;
            return start_idx;
        }

        // Find first terminator position
        let mut term_pos = self.tokens.len();
        for idx in start_idx..self.tokens.len() {
            self.pos = idx;
            if self.is_terminated(terminators) {
                term_pos = idx;
                break;
            }
        }

        self.pos = saved_pos;

        // Skip backward from terminator to last code
        self.skip_stop_index_backward_to_code(term_pos, start_idx)
    }

    /// Check if the current position is at a terminator
    ///
    /// This uses fast simple matching where possible, falling back to full parsing
    /// only when necessary for complex terminators.
    pub fn is_terminated(&mut self, terminators: &[Grammar]) -> bool {
        let init_pos = self.pos;
        self.skip_transparent(true);
        let saved_pos = self.pos;

        // Check if we've reached end of file
        if self.is_at_end() {
            log::debug!("  TERMED Reached end of file");
            self.pos = init_pos; // restore to position before skipping transparent
            return true;
        }

        // Check if current token is end_of_file type
        if let Some(tok) = self.peek() {
            if tok.get_type() == "end_of_file" {
                log::debug!("  TERMED Found end_of_file token");
                self.pos = init_pos; // restore to position before skipping transparent
                return true;
            }
        }

        log::debug!(
            "  TERM Checking terminators: {:?} at pos {:?}",
            terminators,
            self.pos
        );

        // Get current token for simple matching
        let current_token = self.peek();
        if current_token.is_none() {
            log::debug!("  NOTERM No current token");
            self.pos = init_pos;
            return false;
        }
        let current_token = current_token.unwrap();

        // First pass: check all simple terminators (fast path)
        for term in terminators.iter() {
            let simple_opt = term.simple();
            if let Some(simple) = simple_opt {
                // Use fast simple matching
                if simple.could_match(current_token) {
                    log::debug!("  TERMED Simple terminator matched: {}", term);
                    self.pos = init_pos; // restore original position
                    return true;
                }
                log::debug!("  Simple terminator did not match: {}", term);
            }
        }

        // Second pass: check complex terminators that need full parsing (slow path)
        // Create a fresh parser for checking terminators independently
        for term in terminators.iter() {
            // Skip simple terminators (already checked)
            if term.simple().is_some() {
                continue;
            }

            // Complex terminator - need full parse
            // Use a fresh parser instance to avoid any shared state or recursion issues
            let mut terminator_parser = Parser::new(self.tokens, self.dialect);
            terminator_parser.pos = saved_pos;
            // Fresh parser uses iterative mode, but with its own frame stack - no conflicts

            if let Ok(node) = terminator_parser.parse_with_grammar_cached(term, &[]) {
                // Check if the node is "empty" in various ways
                let is_empty = node.is_empty();

                if !is_empty {
                    log::debug!("  TERMED Complex terminator matched: {}", term);
                    self.pos = init_pos; // restore original position
                    return true;
                }
            }
            log::debug!("  Complex terminator did not match: {}", term);
        }

        log::debug!("  NOTERM No terminators matched");
        self.pos = init_pos; // restore original position
        false
    }
}
