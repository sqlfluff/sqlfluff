//! Helper methods for the Parser
//!
//! This module contains utility methods used by both iterative and recursive parsers
//! including token navigation, whitespace handling, and terminator checking.

use std::sync::Arc;

use hashbrown::HashSet;

use super::core::Parser;
use super::Node;
use crate::parser::utils::skip_start_index_forward_to_code;
use sqlfluffrs_types::{Token, Grammar};

impl<'a> Parser<'a> {
    /// Prune terminators based on simple matchers before attempting full termination check.
    ///
    /// Only prunes if the next token is code and allow_gaps is false. Otherwise, returns all terminators.
    /// This matches Python's conservative pruning logic.
    pub(crate) fn prune_terminators(&mut self, terminators: &[Arc<Grammar>]) -> Vec<Arc<Grammar>> {
        // If allow_gaps is true, do NOT prune: gaps may skip to a code token later.
        // (We don't have allow_gaps here, so this must be handled by the caller. If needed, add as param.)
        // For now, only prune if the next token is code; otherwise, return all terminators.

        let first_token = self.tokens.get(self.pos);
        if let Some(tok) = first_token {
            if !tok.is_code() {
                // Next token is not code (could be gap/whitespace), so don't prune
                return terminators.iter().cloned().collect();
            }
        } else {
            // No token at all (EOF), can't prune
            return terminators.iter().cloned().collect();
        }

        let first_token = first_token.unwrap();
        let first_raw = first_token.raw_upper();
        let first_types: HashSet<String> = first_token.get_all_types();

        let mut available_terminators = Vec::new();
        for term in terminators {
            match term.simple_hint(&mut self.simple_hint_cache) {
                None => {
                    // Complex terminator - must try full match
                    available_terminators.push(term.clone());
                }
                Some(hint) => {
                    if hint.can_match_token(&first_raw, &first_types) {
                        available_terminators.push(term.clone());
                    }
                }
            }
        }
        available_terminators
    }
    /// Prune options based on simple matchers before attempting full parse.
    ///
    /// This is the Rust equivalent of Python's `prune_options()` function.
    /// It filters the list of grammar options to only those that could possibly
    /// match the current token, based on quick checks of raw strings and types.
    pub(crate) fn prune_options(&mut self, options: &[Arc<Grammar>]) -> Vec<Arc<Grammar>> {
        // Track stats
        self.pruning_calls.set(self.pruning_calls.get() + 1);
        self.pruning_total
            .set(self.pruning_total.get() + options.len());

        // Find first code (non-whitespace) token from current position
        let first_code_token = self.tokens.iter().skip(self.pos).find(|t| t.is_code());

        // If no code token found, can't prune - return all options
        let Some(first_token) = first_code_token else {
            self.pruning_kept
                .set(self.pruning_kept.get() + options.len());
            return options.iter().cloned().collect();
        };

        // Get token properties for matching
        // Use ALL types (instance_types + class_types) to match Python's behavior
        let first_raw = first_token.raw_upper();
        let first_types: HashSet<String> = first_token.get_all_types();

        // log::debug!(
        //     "Pruning {} options at pos {} (token: '{}', types: {:?})",
        //     options.len(),
        //     self.pos,
        //     first_raw,
        //     first_types
        // );

        let mut available_options = Vec::new();

        for opt in options {
            // Try to get simple hint for this grammar (with dialect for Ref resolution)
            match opt.simple_hint(&mut self.simple_hint_cache) {
                None => {
                    // Complex grammar - must try full match
                    self.pruning_complex.set(self.pruning_complex.get() + 1);
                    // log::debug!("  Keeping complex grammar: {}", opt);
                    available_options.push(opt.clone());
                }
                Some(hint) => {
                    // Track that this had a hint
                    self.pruning_hinted.set(self.pruning_hinted.get() + 1);
                    // Check if hint matches current token (using ALL types for intersection)
                    if hint.can_match_token(&first_raw, &first_types) {
                        // log::debug!("  Keeping matched grammar: {}", opt);
                        available_options.push(opt.clone());
                    } else {
                        // log::debug!("  PRUNED grammar: {}", opt);
                        // pruned_count += 1;
                    }
                }
            }
        }

        // if pruned_count > 0 {
        // log::debug!(
        //     "Pruned from {} to {} options ({} pruned, {:.1}% reduction)",
        //     options.len(),
        //     available_options.len(),
        //     pruned_count,
        //     100.0 * (pruned_count as f64 / options.len() as f64)
        // );
        // }

        self.pruning_kept
            .set(self.pruning_kept.get() + available_options.len());
        available_options
    }

    /// Find the longest matching grammar option from a list.
    /// This is more reflective of the python implementation of longest_match.
    pub(crate) fn longest_match(
        &mut self,
        options: &[Arc<Grammar>],
        max_idx: usize,
        terminators: &[Arc<Grammar>],
    ) -> Node {
        let available_options = match self.get_available_grammar_options(options, max_idx) {
            Ok(value) => value,
            Err(value) => return value,
        };

        let mut terminated = false;
        let mut best_option = Node::Empty;
        let mut best_grammar: Option<Arc<Grammar>> = None;
        let mut best_length = 0;

        for (match_idx, opt) in available_options.iter().enumerate() {
            let saved_pos = self.pos;
            match self.parse_with_grammar_cached(&opt, terminators) {
                Ok(node) => {
                    let length = self.pos - saved_pos;
                    log::debug!("Option {} matched with length {}: {:#?}", opt, length, node);
                    if self.pos == max_idx {
                        log::debug!("Reached max_idx {}, stopping search", max_idx);
                        return node;
                    }

                    if length >= best_length {
                        best_length = length;
                        best_option = node;
                        best_grammar = Some(opt.clone());

                        if match_idx == available_options.len() - 1 {
                            log::debug!(
                                "Last option matched with length {}, returning best match",
                                length
                            );
                            terminated = true;
                            break;
                        } else if !terminators.is_empty() {
                            let next_code_idx =
                                skip_start_index_forward_to_code(self.tokens, self.pos, max_idx);
                            if next_code_idx == max_idx {
                                log::debug!(
                                    "Next code index reached max_idx {}, stopping search",
                                    max_idx
                                );
                                terminated = true;
                                break;
                            }
                        }
                        if self.is_terminated(terminators) {
                            terminated = true;
                            log::debug!("Terminator reached after option {}, stopping search", opt);
                            break;
                        }
                    }
                }
                Err(err) => {
                    log::debug!("Option {} failed to parse: {:?}", opt, err);
                }
            }
            if terminated {
                break;
            }
            self.pos = saved_pos; // Restore position for next option
        }

        best_option
    }

    pub(crate) fn get_available_grammar_options<'g>(
        &mut self,
        options: &[Arc<Grammar>],
        max_idx: usize,
    ) -> Result<Vec<Arc<Grammar>>, Node> {
        if options.is_empty() || self.pos == max_idx {
            return Err(Node::Empty);
        }
        let available_options = self.prune_options(options);
        if available_options.is_empty() {
            log::debug!("No options left after pruning, returning Empty");
            return Err(Node::Empty);
        }
        Ok(available_options)
    }

    /// Print cache statistics
    pub fn print_cache_stats(&self) {
        let (hits, misses, hit_rate) = self.parse_cache.stats();
        println!("Parse Cache Statistics:");
        println!("  Hits: {}", hits);
        println!("  Misses: {}", misses);
        println!("  Hit Rate: {:.2}%", hit_rate * 100.0);
        println!();

        // Print pruning stats
        let calls = self.pruning_calls.get();
        let total = self.pruning_total.get();
        let kept = self.pruning_kept.get();
        let pruned = total.saturating_sub(kept);
        let hinted = self.pruning_hinted.get();
        let complex = self.pruning_complex.get();

        if calls > 0 {
            println!("SimpleHint Pruning Statistics:");
            println!("  Pruning calls: {}", calls);
            println!("  Total options: {}", total);
            println!(
                "  Options with hints: {} ({:.1}%)",
                hinted,
                100.0 * hinted as f64 / total as f64
            );
            println!(
                "  Complex options (no hint): {} ({:.1}%)",
                complex,
                100.0 * complex as f64 / total as f64
            );
            println!(
                "  Options kept: {} ({:.1}%)",
                kept,
                100.0 * kept as f64 / total as f64
            );
            println!(
                "  Options pruned: {} ({:.1}%)",
                pruned,
                100.0 * pruned as f64 / total as f64
            );
            println!(
                "  Pruning effectiveness: {:.1}% of hinted options pruned",
                if hinted > 0 {
                    100.0 * pruned as f64 / hinted as f64
                } else {
                    0.0
                }
            );
            println!("  Avg options per call: {:.1}", total as f64 / calls as f64);
        }
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
                Node::Whitespace {
                    raw: tok.raw(),
                    token_idx: token_pos,
                }
            } else if tok_type == "newline" {
                Node::Newline {
                    raw: tok.raw(),
                    token_idx: token_pos,
                }
            } else if tok_type == "end_of_file" {
                Node::EndOfFile {
                    raw: tok.raw(),
                    token_idx: token_pos,
                }
            } else {
                Node::Token {
                    token_type: tok.token_type.clone(),
                    raw: tok.raw(),
                    token_idx: token_pos,
                } // Fallback for other non-code tokens
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
    pub(crate) fn skip_start_index_forward_to_code(
        &self,
        start_idx: usize,
        max_idx: usize,
    ) -> usize {
        for _idx in start_idx..max_idx {
            if self.tokens[_idx].is_code() {
                return _idx;
            }
        }
        max_idx
    }

    /// Move an index backward through tokens until tokens[index - 1] is code.
    /// Returns the index after the last code token, or min_idx if none found.
    pub(crate) fn skip_stop_index_backward_to_code(
        &self,
        stop_idx: usize,
        min_idx: usize,
    ) -> usize {
        for _idx in (min_idx + 1..=stop_idx).rev() {
            if self.tokens[_idx - 1].is_code() {
                return _idx;
            }
        }
        min_idx
    }

    /// Find the matching closing bracket for an opening bracket.
    /// Returns the index of the closing bracket, or None if not found.
    ///
    /// OPTIMIZATION: Uses pre-computed bracket pairs from lexer for O(1) lookup.
    /// Falls back to O(n) scanning if pre-computation failed or wasn't run.
    fn find_matching_bracket(&self, open_idx: usize) -> Option<usize> {
        if open_idx >= self.tokens.len() {
            return None;
        }

        let open_tok = self.tokens.get(open_idx)?;

        // FAST PATH: Use pre-computed bracket pair if available (O(1))
        if let Some(matching_idx) = open_tok.matching_bracket_idx {
            log::debug!(
                "find_matching_bracket: Using pre-computed match {} -> {}",
                open_idx,
                matching_idx
            );
            return Some(matching_idx);
        }

        // SLOW PATH: Fallback to scanning (for tokens created without lexer)
        log::debug!(
            "find_matching_bracket: Pre-computed match not available for index {}, falling back to scan",
            open_idx
        );

        let open_raw = open_tok.raw();

        // Determine which closing bracket we're looking for based on the opening bracket
        let (is_matching_open, is_matching_close): (fn(&str) -> bool, fn(&str) -> bool) =
            match open_raw.as_str() {
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

    /// Get the pre-computed matching bracket index for a token.
    /// This is a public wrapper for accessing pre-computed bracket pairs.
    /// Returns None if not a bracket or if matching bracket wasn't found during lexing.
    pub(crate) fn get_matching_bracket_idx(&self, token_idx: usize) -> Option<usize> {
        self.tokens.get(token_idx)?.matching_bracket_idx
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
    pub(crate) fn trim_to_terminator(
        &mut self,
        start_idx: usize,
        terminators: &[Arc<Grammar>],
    ) -> usize {
        if start_idx >= self.tokens.len() {
            return self.tokens.len();
        }

        let saved_pos = self.pos;

        // Check if already at a terminator immediately
        if self.is_terminated(terminators) {
            self.pos = saved_pos;
            return start_idx;
        }

        log::debug!(
            "[TRIM_TO_TERM] Starting scan from idx={}, checking {} terminators",
            start_idx,
            terminators.len()
        );

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
                    log::debug!(
                        "[TRIM_TO_TERM] idx={} found opening bracket '{}', finding matching close",
                        idx,
                        tok_raw
                    );

                    if let Some(close_idx) = self.find_matching_bracket(idx) {
                        // Skip past the closing bracket
                        log::debug!(
                            "[TRIM_TO_TERM] Found matching close at idx={}, continuing from idx={}",
                            close_idx,
                            close_idx + 1
                        );
                        idx = close_idx + 1;
                        continue;
                    } else {
                        // No matching bracket found - this is malformed SQL
                        // Just continue scanning (will likely fail parsing later)
                        log::debug!(
                            "[TRIM_TO_TERM] No matching close bracket found for idx={}",
                            idx
                        );
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
    pub fn is_terminated(&mut self, terminators: &[Arc<Grammar>]) -> bool {
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

        // Prune terminators before checking, to reduce unnecessary checks
        let pruned_terminators = self.prune_terminators(terminators);
        log::debug!(
            "  TERM Checking pruned terminators: {:?} at pos {:?}",
            pruned_terminators,
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
        let current_token_raw_upper = current_token.raw_upper();
        let current_token_types = current_token.get_all_types();

        // First pass: check all simple terminators (fast path)
        for term in pruned_terminators.iter() {
            let simple_opt = term.simple_hint(&mut self.simple_hint_cache);
            if let Some(simple) = simple_opt {
                // Use fast simple matching
                if simple.can_match_token(&current_token_raw_upper, &current_token_types) {
                    log::debug!("  TERMED Simple terminator matched: {}", term);
                    self.pos = init_pos; // restore original position
                    return true;
                }
                log::debug!("  Simple terminator did not match: {}", term);
            }
        }

        // Second pass: check complex terminators that need full parsing (slow path)
        for term in pruned_terminators.iter() {
            // Skip simple terminators (already checked)
            if term.simple_hint(&mut self.simple_hint_cache).is_some() {
                continue;
            }

            // Complex terminator - need full parse
            // Use the same parser to share the cache, but save/restore position
            let check_pos = self.pos;
            self.pos = saved_pos;

            if let Ok(node) = self.parse_with_grammar_cached(&term, &[]) {
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
