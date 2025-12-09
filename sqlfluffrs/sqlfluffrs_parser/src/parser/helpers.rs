//! Helper methods for the Parser
//!
//! This module contains utility methods used by both iterative and recursive parsers
//! including token navigation, whitespace handling, and terminator checking.

use hashbrown::HashSet;

use super::core::Parser;
use super::Node;
use sqlfluffrs_types::{GrammarId, ParseMode, Token};

impl<'a> Parser<'a> {
    /// Combine parent and local terminators based on reset_terminators flag.
    ///
    /// This is a common pattern used by all handlers (AnySetOf, AnyNumberOf, OneOf, Sequence, etc.)
    /// to determine which terminators to use for child parsing.
    ///
    /// If reset_terminators is true, only local_terminators are used.
    /// If reset_terminators is false, both local and parent terminators are combined.
    pub(crate) fn combine_table_terminators(
        &self,
        local_terminators: &[GrammarId],
        parent_terminators: &[GrammarId],
        reset_terminators: bool,
    ) -> Vec<GrammarId> {
        if reset_terminators {
            local_terminators.to_vec()
        } else {
            local_terminators
                .iter()
                .cloned()
                .chain(parent_terminators.iter().cloned())
                .collect()
        }
    }

    /// Print cache statistics
    pub fn print_cache_stats(&self) {
        // Print table cache stats
        let (table_hits, table_misses, table_hit_rate) = self.table_cache.stats();
        println!("Table Parse Cache Statistics:");
        println!("  Hits: {}", table_hits);
        println!("  Misses: {}", table_misses);
        println!("  Entries: {}", self.table_cache.len());
        println!("  Hit Rate: {:.2}%", table_hit_rate * 100.0);
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
                Node::new_token(tok.token_type.clone(), tok.raw(), token_pos) // Fallback for other non-code tokens
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
        // Note: Angle brackets (<>) are handled as comparison operators by the lexer
        // (less_than/greater_than), so they won't reach this function.
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

    // ============================================================================
    // TABLE-DRIVEN UTILITY FUNCTIONS
    // ============================================================================
    //
    // These are table-driven equivalents of the Arc<Grammar> utility functions above.
    // They work with GrammarId and use GrammarContext for
    // table access.

    /// Combine parent and local terminators for table-driven parsing.
    ///
    /// If reset_terminators is true, only local_terminators are used.
    /// Otherwise, both local and parent terminators are combined.
    pub(crate) fn combine_terminators_table_driven(
        local_terminators: &[GrammarId],
        parent_terminators: &[GrammarId],
        reset_terminators: bool,
    ) -> Vec<GrammarId> {
        if reset_terminators {
            local_terminators.to_vec()
        } else {
            local_terminators
                .iter()
                .copied()
                .chain(parent_terminators.iter().copied())
                .collect()
        }
    }

    /// Calculate max_idx for table-driven parsing, considering terminators and parent constraints.
    ///
    /// This is the table-driven equivalent of calculate_max_idx().
    pub(crate) fn calculate_max_idx_table_driven(
        &mut self,
        start_idx: usize,
        terminators: &[GrammarId],
        parse_mode: ParseMode,
        parent_max_idx: Option<usize>,
    ) -> usize {
        // Calculate initial max_idx based on parse_mode
        let mut max_idx = if parse_mode == ParseMode::Greedy {
            self.trim_to_terminator_table_driven(start_idx, terminators)
        } else {
            self.tokens.len()
        };

        // Trim backward to last code token
        if max_idx > 0 {
            max_idx = self.skip_stop_index_backward_to_code(max_idx, start_idx);
        }

        // Apply parent's constraint
        if let Some(parent_limit) = parent_max_idx {
            max_idx = max_idx.min(parent_limit);
        }

        log::debug!(
            "calculate_max_idx_table_driven: start_idx={}, terminators.len()={}, parse_mode={:?}, parent_max_idx={:?}, final_max_idx={}",
            start_idx, terminators.len(), parse_mode, parent_max_idx, max_idx
        );

        max_idx
    }

    /// Calculate max_idx for table-driven parsing with element awareness (for AnyNumberOf).
    ///
    /// This is the table-driven equivalent of calculate_max_idx_with_elements().
    pub(crate) fn calculate_max_idx_with_elements_table_driven(
        &mut self,
        start_idx: usize,
        terminators: &[GrammarId],
        elements: &[GrammarId],
        parse_mode: ParseMode,
        parent_max_idx: Option<usize>,
    ) -> usize {
        // Calculate initial max_idx based on parse_mode
        let mut max_idx = if parse_mode == ParseMode::Greedy {
            self.trim_to_terminator_with_elements_table_driven(start_idx, terminators, elements)
        } else {
            self.tokens.len()
        };

        // Trim backward to last code token
        if max_idx > 0 {
            max_idx = self.skip_stop_index_backward_to_code(max_idx, start_idx);
        }

        // Apply parent's constraint
        if let Some(parent_limit) = parent_max_idx {
            max_idx = max_idx.min(parent_limit);
        }

        max_idx
    }

    /// Prune options for table-driven parsing based on simple hints.
    ///
    /// This is the table-driven equivalent of prune_options().
    pub(crate) fn prune_options_table_driven(&mut self, options: &[GrammarId]) -> Vec<GrammarId> {
        // Track stats
        self.pruning_calls.set(self.pruning_calls.get() + 1);
        self.pruning_total
            .set(self.pruning_total.get() + options.len());

        // Find first code token
        let first_code_token = self.tokens.iter().skip(self.pos).find(|t| t.is_code());

        // If no code token found, can't prune - return all options
        let Some(first_token) = first_code_token else {
            self.pruning_kept
                .set(self.pruning_kept.get() + options.len());
            return options.to_vec();
        };

        // Get token properties for matching
        let first_raw = first_token.raw_upper();
        let first_types: HashSet<String> = first_token.get_all_types();

        log::debug!(
            "Pruning {} options at pos {} (token: '{}', types: {:?})",
            options.len(),
            self.pos,
            first_raw,
            first_types
        );

        let mut available_options = Vec::new();

        // Get grammar tables if available
        let tables = Some(self.grammar_ctx.tables());

        for &opt_id in options {
            // Try to get simple hint for this grammar from tables
            if let Some(tables) = tables {
                if let Some(hint) = tables.get_simple_hint_for_grammar(opt_id) {
                    // We have a hint - track it
                    self.pruning_hinted.set(self.pruning_hinted.get() + 1);
                    // Use hint to filter
                    if tables.hint_can_match(hint, &first_raw, &first_types) {
                        available_options.push(opt_id);
                    } else {
                        // Hint says no match possible - skip this option
                        continue;
                    }
                } else {
                    // No hint = complex grammar, must try it
                    self.pruning_complex.set(self.pruning_complex.get() + 1);
                    available_options.push(opt_id);
                }
            } else {
                // No tables available - keep all options (conservative)
                self.pruning_complex.set(self.pruning_complex.get() + 1);
                available_options.push(opt_id);
            }
        }

        // Compute human-readable names for kept and dropped options for debugging
        {
            let ctx = &self.grammar_ctx;
            let mut kept_names: Vec<String> = Vec::new();
            let mut dropped_names: Vec<String> = Vec::new();
            for &opt_id in options {
                let var = ctx.variant(opt_id);
                let name = match var {
                    sqlfluffrs_types::GrammarVariant::Ref => ctx.ref_name(opt_id).to_string(),
                    sqlfluffrs_types::GrammarVariant::StringParser
                    | sqlfluffrs_types::GrammarVariant::TypedParser
                    | sqlfluffrs_types::GrammarVariant::RegexParser => {
                        ctx.template(opt_id).to_string()
                    }
                    sqlfluffrs_types::GrammarVariant::Meta => {
                        let aux = ctx.tables().aux_data_offsets[opt_id.get() as usize];
                        ctx.tables().get_string(aux).to_string()
                    }
                    other => format!("{:?}", other),
                };
                if available_options.contains(&opt_id) {
                    kept_names.push(name);
                } else {
                    dropped_names.push(name);
                }
            }
            log::debug!(
                "Prune result: kept={} dropped={} kept_names={:?} dropped_names={:?}",
                available_options.len(),
                options.len() - available_options.len(),
                kept_names,
                dropped_names
            );
        }

        self.pruning_kept
            .set(self.pruning_kept.get() + available_options.len());

        available_options
    }

    /// Check if we're at a terminator for table-driven parsing, considering elements.
    ///
    /// This is the table-driven equivalent of is_terminated_with_elements().
    pub(crate) fn is_terminated_table_driven(&mut self, terminators: &[GrammarId]) -> bool {
        let init_pos = self.pos;

        // CRITICAL: Check for GrammarId::NONCODE BEFORE skipping transparent tokens!
        // NONCODE should match non-code tokens at the CURRENT position,
        // not after skipping them. This is essential for allow_gaps=false behavior.
        let has_noncode_terminator = terminators.contains(&GrammarId::NONCODE);
        log::debug!(
            "  is_terminated_table_driven at pos {}: has_noncode_terminator={}",
            init_pos,
            has_noncode_terminator
        );
        if has_noncode_terminator {
            if let Some(tok) = self.peek() {
                let is_code = tok.is_code();
                log::debug!(
                    "  is_terminated_table_driven: current token is_code={}, type={}",
                    is_code,
                    tok.get_type()
                );
                if !is_code {
                    log::debug!("  TERMED NONCODE found non-code token at current position");
                    return true;
                }
            }
        }

        // Filter out NONCODE from terminators for the rest of the check
        // We've already checked it at the current position above
        let terminators_without_noncode: Vec<GrammarId> = if has_noncode_terminator {
            terminators
                .iter()
                .filter(|&t| *t != GrammarId::NONCODE)
                .copied()
                .collect()
        } else {
            terminators.to_vec()
        };

        self.skip_transparent(true);
        let saved_pos = self.pos;

        // Check if we've reached end of file
        if self.is_at_end() {
            log::debug!("  TERMED Reached end of file");
            self.pos = init_pos;
            return true;
        }

        // Check if current token is end_of_file type
        if let Some(tok) = self.peek() {
            if tok.get_type() == "end_of_file" {
                log::debug!("  TERMED Found end_of_file token");
                self.pos = init_pos;
                return true;
            }
        }

        // Prune terminators before checking
        log::debug!(
            "  TERM Before prune: {} terminators at pos {}: {:?}",
            terminators_without_noncode.len(),
            self.pos,
            terminators_without_noncode
        );
        let pruned_terminators = self.prune_terminators_table_driven(&terminators_without_noncode);
        log::debug!(
            "  TERM Checking {} pruned terminators at pos {}",
            pruned_terminators.len(),
            self.pos
        );

        // Get current token for simple matching
        let current_token = self.peek();
        if current_token.is_none() {
            log::debug!("  NOTERM No current token");
            self.pos = init_pos;
            return false;
        }
        // Note: In future, we can use simple_hint matching here like the Arc version

        // Check all terminators - use full parse for multi-token terminators
        for term_id in pruned_terminators.iter() {
            // Skip NONCODE - already handled above
            if *term_id == GrammarId::NONCODE {
                continue;
            }

            // TODO: Implement simple_hint check from table
            // TODO: Implement needs_full_parse check (Sequence with multiple elements)

            // For now, do full parse for all terminators (conservative approach)
            let check_pos = self.pos;
            self.pos = saved_pos;

            if let Ok(node) = self.parse_table_iterative(*term_id, &[]) {
                let is_empty = node.is_empty();
                self.pos = check_pos;

                if !is_empty {
                    log::debug!("  TERMED Terminator matched (table-driven): {:?}", term_id);
                    self.pos = init_pos;
                    return true;
                }
            } else {
                self.pos = check_pos;
            }
            log::debug!("  Terminator did not match (table-driven): {:?}", term_id);
        }

        log::debug!("  NOTERM No terminators matched");
        self.pos = init_pos;
        false
    }

    /// Prune terminators for table-driven parsing based on simple matchers.
    ///
    /// This is the table-driven equivalent of prune_terminators().
    fn prune_terminators_table_driven(&mut self, terminators: &[GrammarId]) -> Vec<GrammarId> {
        // Reuse the same pruning logic as prune_options_table_driven
        self.prune_options_table_driven(terminators)
    }

    pub(crate) fn trim_to_terminator_table_driven(
        &mut self,
        start_idx: usize,
        terminators: &[GrammarId],
    ) -> usize {
        let segments = self.tokens;

        if start_idx >= segments.len() {
            log::debug!(
                "[TRIM_TO_TERM_TABLE] start_idx {} >= segments.len() {}, returning {}",
                start_idx,
                segments.len(),
                segments.len()
            );
            return segments.len();
        }

        let pruned_terms = self.prune_options_table_driven(terminators);
        log::debug!(
            "[TRIM_TO_TERM_TABLE] Scanning for terminators from idx={}, pruned_terms={:?}",
            start_idx,
            pruned_terms
        );
        for term in pruned_terms.iter() {
            let grammar_name = self.grammar_ctx.grammar_id_name(*term);
            log::debug!(
                "[TRIM_TO_TERM_TABLE] Trying terminator {:?} (name: {}) at idx={}",
                term,
                grammar_name,
                start_idx
            );
            if let Ok(m) = self.try_match_grammar_table_driven(*term, start_idx, &[]) {
                log::debug!(
                    "[TRIM_TO_TERM_TABLE] Terminator {:?} (name: {}) matched at idx={}, returning {}",
                    term,
                    grammar_name,
                    start_idx,
                    m
                );
                return m;
            } else {
                log::debug!(
                    "[TRIM_TO_TERM_TABLE] Terminator {:?} (name: {}) did NOT match at idx={}",
                    term,
                    grammar_name,
                    start_idx
                );
            }
        }

        let term_match = self.greedy_match_table_driven(start_idx, terminators, self.tokens.len());
        log::debug!(
            "[TRIM_TO_TERM_TABLE] greedy_match_table_driven returned {:?}",
            term_match
        );
        // term_match.1 is already the last code index before the terminator (computed by greedy_match_table_driven)
        let final_idx = term_match.1;
        log::debug!(
            "[TRIM_TO_TERM_TABLE] Using term_match.1 as final_idx: {}",
            final_idx
        );
        final_idx
    }

    /// Trim to first terminator position for table-driven parsing with element awareness.
    ///
    /// This is the table-driven equivalent of trim_to_terminator_with_elements().
    pub(crate) fn trim_to_terminator_with_elements_table_driven(
        &mut self,
        start_idx: usize,
        terminators: &[GrammarId],
        _elements: &[GrammarId],
    ) -> usize {
        // Python version: trim at the first position where a terminator matches.
        // For keyword terminators (all alphabetical), require whitespace before them.
        if terminators.is_empty() {
            return self.tokens.len();
        }

        let mut idx = start_idx;
        'outer: while idx < self.tokens.len() {
            // IMPORTANT: Check for opening brackets FIRST and skip over them.
            // This prevents nested brackets from being incorrectly matched as terminators.
            // For example, in `EXTRACT(MICROSECOND FROM col1)`, the `FROM` inside the brackets
            // should not be matched as a terminator - we skip the entire `(...)` section.
            if let Some(tok) = self.tokens.get(idx) {
                let tok_type = tok.get_type();
                let tok_raw = tok.raw();

                // Check both by type AND by raw value, since some lexers use "raw" type for brackets
                // instead of "start_bracket"/"start_square_bracket"/"start_angle_bracket"
                // Note: We don't check for "<" here because angle brackets are tokenized as
                // "less_than"/"greater_than" and the parser handles them differently than brackets.
                // Treating "<" as a bracket would break comparisons like `WHERE a < b AND c > d`.
                let is_open_bracket = tok_type == "start_bracket"
                    || tok_type == "start_square_bracket"
                    || tok_type == "start_angle_bracket"
                    || (tok_type == "raw" && (tok_raw == "(" || tok_raw == "[" || tok_raw == "{"));

                if is_open_bracket {
                    if let Some(end_idx) = self.find_matching_bracket(idx) {
                        idx = end_idx + 1;
                        continue;
                    }
                }
            }

            let saved_pos = self.pos;
            self.pos = idx;

            // Skip transparent tokens before matching
            self.skip_transparent(true);
            let match_pos = self.pos; // Position after skipping transparent tokens

            for term_id in terminators {
                if let Ok(node) = self.parse_table_iterative(*term_id, &[]) {
                    if !node.is_empty() {
                        let match_end_pos = self.pos; // Position after match

                        // Check if this terminator is a keyword (all alphabetical).
                        // If so, require whitespace before it (Python behavior from greedy_match).
                        // Instead of checking the grammar structure, check the token that matched.
                        // If the token at match_pos is all alphabetical, it's a keyword.
                        let requires_whitespace = if let Some(tok) = self.tokens.get(match_pos) {
                            let raw = tok.raw();
                            !raw.is_empty() && raw.chars().all(|c| c.is_alphabetic())
                        } else {
                            false
                        };

                        if requires_whitespace {
                            // Edge case: if matching at start_idx, allow it (Python behavior)
                            if match_pos == start_idx {
                                self.pos = saved_pos;
                                return idx;
                            }

                            // Check for whitespace before this position
                            // Look backward from match_pos for whitespace (skip meta/transparent)
                            let mut has_whitespace = false;
                            let mut check_idx = match_pos;
                            while check_idx > 0 {
                                check_idx -= 1;
                                if let Some(prev_tok) = self.tokens.get(check_idx) {
                                    let prev_type = prev_tok.get_type();
                                    // Skip meta/transparent tokens (indent, dedent, comment, etc.)
                                    if prev_tok.is_meta {
                                        continue;
                                    }
                                    // Found whitespace - keyword is preceded by whitespace
                                    if prev_type == "whitespace" || prev_type == "newline" {
                                        has_whitespace = true;
                                        break;
                                    }
                                    // Found something other than meta/whitespace - stop looking
                                    break;
                                }
                            }

                            if !has_whitespace {
                                // Keyword terminator without preceding whitespace.
                                // Skip past this match and continue looking for next terminator.
                                // (Python: working_idx = _stop_idx; continue)
                                self.pos = saved_pos;
                                idx = match_end_pos;
                                continue 'outer;
                            }
                        }

                        // Terminator is valid - return the position
                        self.pos = saved_pos;
                        return idx;
                    }
                }
            }

            self.pos = saved_pos;
            idx += 1;
        }

        self.tokens.len()
    }
}
