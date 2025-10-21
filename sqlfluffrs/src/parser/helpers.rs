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
        println!("Parse Cache Statistics:");
        println!("  Hits: {}", hits);
        println!("  Misses: {}", misses);
        println!("  Hit Rate: {:.2}%", hit_rate * 100.0);
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
                Node::Token(tok.raw(), tok.token_type.clone(), token_pos) // Fallback for other non-code tokens
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
                    self.bump() // bump() handles bracket depth tracking
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

    /// Find the matching closing bracket for an opening bracket.
    /// Returns the index of the closing bracket, or None if not found.
    fn find_matching_bracket(&self, open_idx: usize) -> Option<usize> {
        if open_idx >= self.tokens.len() {
            return None;
        }

        let open_tok = self.tokens.get(open_idx)?;
        let open_raw = open_tok.raw();

        // Determine which closing bracket we're looking for based on the opening bracket
        let (is_matching_open, is_matching_close): (fn(&str) -> bool, fn(&str) -> bool) = match open_raw.as_str() {
            "(" => (|s| s == "(", |s| s == ")"),
            "[" => (|s| s == "[", |s| s == "]"),
            "{" => (|s| s == "{", |s| s == "}"),
            _ => return None, // Not an opening bracket
        };

        let mut depth = 1; // We've already seen the opening bracket
        for idx in (open_idx + 1)..self.tokens.len() {
            if let Some(tok) = self.tokens.get(idx) {
                let tok_raw = tok.raw();

                // Check for matching bracket type
                if is_matching_open(&tok_raw) {
                    depth += 1;
                } else if is_matching_close(&tok_raw) {
                    depth -= 1;
                    if depth == 0 {
                        return Some(idx);
                    }
                }
            }
        }

        None // No matching closing bracket found
    }

    /// Trim forward segments based on terminators, excluding bracketed content.
    ///
    /// This implements Python's `next_ex_bracket_match` behavior:
    /// When searching for terminators, if we encounter an opening bracket,
    /// we skip the entire bracketed section (by finding its matching closing
    /// bracket) and continue searching after it.
    ///
    /// This prevents matching terminators that are inside nested brackets,
    /// e.g., finding the wrong ")" when parsing DATEADD(DAY, ABS(5), '2024-01-01').
    ///
    /// Returns the index to use as max_idx (trimmed to last code segment before terminator).
    pub(crate) fn trim_to_terminator(&mut self, start_idx: usize, terminators: &[Grammar]) -> usize {
        if start_idx >= self.tokens.len() {
            return self.tokens.len();
        }

        let saved_pos = self.pos;

        // Check if already at a terminator immediately
        if self.is_terminated(terminators) {
            self.pos = saved_pos;
            return start_idx;
        }

        log::debug!("[TRIM_TO_TERM] Starting scan from idx={}, checking {} terminators",
                    start_idx, terminators.len());

        // Scan forward looking for terminators, but skip over bracketed sections
        let mut idx = start_idx;
        let mut term_pos = self.tokens.len();

        while idx < self.tokens.len() {
            self.pos = idx;

            // Check if current position is a terminator
            if self.is_terminated(terminators) {
                log::debug!("[TRIM_TO_TERM] Found terminator at idx={}", idx);
                term_pos = idx;
                break;
            }

            // Check if current token is an opening bracket
            if let Some(tok) = self.tokens.get(idx) {
                let tok_raw = tok.raw();
                if tok_raw == "(" || tok_raw == "[" || tok_raw == "{" {
                    // Found opening bracket - skip the entire bracketed section
                    log::debug!("[TRIM_TO_TERM] idx={} found opening bracket '{}', finding matching close", idx, tok_raw);

                    if let Some(close_idx) = self.find_matching_bracket(idx) {
                        // Skip past the closing bracket
                        log::debug!("[TRIM_TO_TERM] Found matching close at idx={}, continuing from idx={}", close_idx, close_idx + 1);
                        idx = close_idx + 1;
                        continue;
                    } else {
                        // No matching bracket found - this is malformed SQL
                        // Just continue scanning (will likely fail parsing later)
                        log::debug!("[TRIM_TO_TERM] No matching close bracket found for idx={}", idx);
                        idx += 1;
                        continue;
                    }
                }
            }

            // Not a terminator, not an opening bracket - move to next token
            idx += 1;
        }

        log::debug!("[TRIM_TO_TERM] Scan complete, term_pos={}", term_pos);

        // Restore parser state
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
        for term in terminators.iter() {
            // Skip simple terminators (already checked)
            if term.simple().is_some() {
                continue;
            }

            // Complex terminator - need full parse
            // Use the same parser to share the cache, but save/restore position
            let check_pos = self.pos;
            self.pos = saved_pos;

            if let Ok(node) = self.parse_with_grammar_cached(term, &[]) {
                // Check if the node is "empty" in various ways
                let is_empty = node.is_empty();

                // Restore position before returning
                self.pos = check_pos;

                if !is_empty {
                    log::debug!("  TERMED Complex terminator matched: {}", term);
                    self.pos = init_pos; // restore original position
                    return true;
                }
            } else {
                // Restore position after failed parse
                self.pos = check_pos;
            }
            log::debug!("  Complex terminator did not match: {}", term);
        }

        log::debug!("  NOTERM No terminators matched");
        self.pos = init_pos; // restore original position
        false
    }
}
