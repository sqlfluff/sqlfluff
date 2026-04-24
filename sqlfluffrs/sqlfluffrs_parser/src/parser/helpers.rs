//! Helper methods for the Parser
//!
//! This module contains utility methods used by both iterative and recursive parsers
//! including token navigation, whitespace handling, and terminator checking.

use hashbrown::HashSet;
use smallvec::SmallVec;

use super::core::Parser;
use sqlfluffrs_types::{GrammarId, ParseMode, Token};

#[cfg(feature = "verbose-debug")]
use crate::vdebug;

impl<'a> Parser<'a> {
    /// Combine parent and local terminators based on reset_terminators flag.
    ///
    /// This is a common pattern used by all handlers (AnySetOf, AnyNumberOf, OneOf, Sequence, etc.)
    /// to determine which terminators to use for child parsing.
    ///
    /// If reset_terminators is true, only local_terminators are used.
    /// If reset_terminators is false, both local and parent terminators are combined.
    #[inline]
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
    #[inline]
    pub fn peek(&self) -> Option<&Token> {
        self.tokens.get(self.pos)
    }

    /// Consume the current token and advance position
    #[inline]
    pub fn bump(&mut self) {
        self.pos += 1;
    }

    /// Check if we've reached the end of the token stream
    pub fn is_at_end(&self) -> bool {
        self.pos >= self.tokens.len()
    }

    /// Skip all transparent tokens (whitespace, newlines) without collecting them
    /// IMPORTANT: Comments are NOT transparent - they should be collected, not skipped!
    pub fn skip_transparent(&mut self, allow_gaps: bool) {
        if !allow_gaps {
            return;
        }
        while let Some(tok) = self.peek() {
            match tok {
                // Skip only whitespace/newlines, NOT comments
                tok if !tok.is_code() && !tok.is_comment() => {
                    vdebug!("NOCODE skipping token: {:?}", tok);
                    self.bump() // bump() handles bracket depth tracking
                }
                _ => break,
            }
        }
    }

    /// Skip forward through non-code tokens (whitespace, newlines, comments) to the next code token.
    /// This matches Python's skip_start_index_forward_to_code which only checks is_code.
    /// Comments have is_code=False, so they ARE skipped (to be collected elsewhere).
    /// Returns the index of the first code token, or max_idx if none found.
    pub(crate) fn skip_start_index_forward_to_code(
        &self,
        start_idx: usize,
        max_idx: usize,
    ) -> usize {
        for _idx in start_idx..max_idx {
            let tok = &self.tokens[_idx];
            if tok.is_code() {
                return _idx;
            }
        }
        max_idx
    }

    /// Move an index backward through tokens until tokens[index - 1] is code or comment.
    /// Returns the index after the last code/comment token, or min_idx if none found.
    /// IMPORTANT: Comments are NOT skipped - they should be collected like code tokens!
    pub(crate) fn skip_stop_index_backward_to_code(
        &self,
        stop_idx: usize,
        min_idx: usize,
    ) -> usize {
        for _idx in (min_idx..stop_idx).rev() {
            let tok = &self.tokens[_idx];
            if tok.is_code() || tok.is_comment() {
                return _idx + 1;
            }
        }
        min_idx
    }

    /// Get the pre-computed matching bracket index for a token.
    /// This is a public wrapper for accessing pre-computed bracket pairs.
    /// Returns None if not a bracket, if matching bracket wasn't found during lexing,
    /// or if the pre-computed index is invalid (can happen with trimmed token arrays).
    ///
    /// IMPORTANT: When tokens are trimmed (e.g., leading comments removed), the
    /// pre-computed indices from lexing may point to the wrong token. This function
    /// validates that the token at matching_idx is actually the expected closing bracket.
    pub(crate) fn get_matching_bracket_idx(&self, token_idx: usize) -> Option<usize> {
        let open_tok = self.tokens.get(token_idx)?;
        let matching_idx = open_tok.matching_bracket_idx?;

        // Validate the pre-computed index is within bounds
        if matching_idx >= self.tokens.len() {
            vdebug!(
                "get_matching_bracket_idx: Pre-computed match {} is out of bounds (len={})",
                matching_idx,
                self.tokens.len()
            );
            return None;
        }

        // Validate the token at matching_idx is actually the expected closing bracket
        let close_tok = self.tokens.get(matching_idx)?;
        let open_raw = open_tok.raw();
        let expected_close = match open_raw.as_str() {
            "(" => ")",
            "[" => "]",
            "{" => "}",
            _ => return None, // Not an opening bracket
        };

        if close_tok.raw() == expected_close {
            Some(matching_idx)
        } else {
            vdebug!(
                "get_matching_bracket_idx: Pre-computed match {} points to '{}' not '{}', returning None",
                matching_idx,
                close_tok.raw(),
                expected_close
            );
            None
        }
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
    #[inline]
    pub(crate) fn combine_terminators_table_driven(
        local_terminators: &[GrammarId],
        parent_terminators: &[GrammarId],
        reset_terminators: bool,
    ) -> SmallVec<[GrammarId; 4]> {
        if reset_terminators {
            SmallVec::from_slice(local_terminators)
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
    #[inline]
    pub(crate) fn calculate_max_idx_table_driven(
        &mut self,
        start_idx: usize,
        terminators: &[GrammarId],
        parse_mode: ParseMode,
        parent_max_idx: Option<usize>,
    ) -> Result<usize, crate::parser::ParseError> {
        // Calculate initial max_idx based on parse_mode
        let mut max_idx = if parse_mode == ParseMode::Greedy {
            self.trim_to_terminator_table_driven(start_idx, terminators)?
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

        vdebug!(
            "calculate_max_idx_table_driven: start_idx={}, terminators.len()={}, parse_mode={:?}, parent_max_idx={:?}, final_max_idx={}",
            start_idx, terminators.len(), parse_mode, parent_max_idx, max_idx
        );

        Ok(max_idx)
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

        vdebug!(
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
        // This is expensive (iterates all options, builds String vecs) so only
        // compile it in when verbose-debug is enabled.
        #[cfg(feature = "verbose-debug")]
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
            vdebug!(
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
        vdebug!(
            "  is_terminated_table_driven at pos {}: has_noncode_terminator={}",
            init_pos,
            has_noncode_terminator
        );
        if has_noncode_terminator {
            if let Some(tok) = self.peek() {
                let is_code = tok.is_code();
                vdebug!(
                    "  is_terminated_table_driven: current token is_code={}, type={}",
                    is_code,
                    tok.get_type()
                );
                if !is_code {
                    vdebug!("  TERMED NONCODE found non-code token at current position");
                    self.terminator_hits.set(self.terminator_hits.get() + 1);
                    return true;
                }
            }
        }

        // Filter out NONCODE from terminators for the rest of the check
        // We've already checked it at the current position above.
        // Avoid allocation when no filtering is needed (the common case).
        let filtered_storage: Vec<GrammarId>;
        let terminators_without_noncode: &[GrammarId] = if has_noncode_terminator {
            filtered_storage = terminators
                .iter()
                .filter(|&t| *t != GrammarId::NONCODE)
                .copied()
                .collect();
            &filtered_storage
        } else {
            terminators
        };

        self.skip_transparent(true);
        let saved_pos = self.pos;

        // Check if we've reached end of file
        if self.is_at_end() {
            vdebug!("  TERMED Reached end of file");
            self.pos = init_pos;
            self.terminator_hits.set(self.terminator_hits.get() + 1);
            return true;
        }

        // Check if current token is end_of_file type
        if let Some(tok) = self.peek() {
            if tok.get_type() == "end_of_file" {
                vdebug!("  TERMED Found end_of_file token");
                self.pos = init_pos;
                self.terminator_hits.set(self.terminator_hits.get() + 1);
                return true;
            }
        }

        // Prune terminators before checking
        vdebug!(
            "  TERM Before prune: {} terminators at pos {}: {:?}",
            terminators_without_noncode.len(),
            self.pos,
            terminators_without_noncode
        );
        let pruned_terminators = self.prune_terminators_table_driven(terminators_without_noncode);
        vdebug!(
            "  TERM Checking {} pruned terminators at pos {}",
            pruned_terminators.len(),
            self.pos
        );

        // Get current token for simple matching
        let current_token = self.peek();
        if current_token.is_none() {
            vdebug!("  NOTERM No current token");
            self.pos = init_pos;
            return false;
        }
        // PYTHON PARITY: In Python, AnyNumberOf checks terminators via term.match().
        // Python's StringParser type-gates: StringParser("FROM") only matches `keyword`
        // type segments, never `word` type. So a `word`-type `from` token (as in
        // `value:data:from::string`) never matches the FROM terminator.
        //
        // In Rust, StringParser does not type-gate today, so `from` (word type)
        // incorrectly matches. We compensate: if the token at the current position
        // is all-alphabetical code and is NOT preceded by whitespace, skip all
        // non-TypedParser terminators (TypedParser matches by type, not raw string).
        let current_tok_is_alpha_only = self.peek().is_some_and(|tok| {
            tok.is_code()
                && !tok.raw().is_empty()
                && tok.raw().chars().all(|c| c.is_ascii_alphabetic())
        });
        let alpha_tok_has_whitespace_before = if current_tok_is_alpha_only {
            self.is_preceded_by_whitespace(self.tokens, saved_pos, 0)
        } else {
            true // symbol terminators don't need this check
        };

        for term_id in pruned_terminators.iter() {
            // Skip NONCODE - already handled above
            if *term_id == GrammarId::NONCODE {
                continue;
            }

            // See block comment above: compensate for Rust StringParser not type-gating.
            // TypedParser terminators are exempt (they match by token type, not raw string).
            if current_tok_is_alpha_only && !alpha_tok_has_whitespace_before {
                let tables = self.grammar_ctx.tables();
                let variant = tables.get_inst(*term_id).variant;
                if variant != sqlfluffrs_types::GrammarVariant::TypedParser {
                    vdebug!(
                        "  NOTERM All-alpha non-whitespace-preceded: skipping non-TypedParser terminator {:?} at pos {}",
                        term_id, saved_pos
                    );
                    continue;
                }
            }

            // Check terminator match cache first - key is (position after skipping transparent, grammar_id)
            let cache_key = (saved_pos, term_id.0);
            if let Some(&cached_result) = self.terminator_match_cache.borrow().get(&cache_key) {
                vdebug!(
                    "  TERMCACHE HIT at pos {} for {:?}: {}",
                    saved_pos,
                    term_id,
                    cached_result
                );
                if cached_result {
                    vdebug!("  TERMED Terminator matched (cached): {:?}", term_id);
                    self.pos = init_pos;
                    self.terminator_hits.set(self.terminator_hits.get() + 1);
                    return true;
                }
                // Cached false - skip this terminator
                continue;
            }

            // Cache miss - do full parse
            let check_pos = self.pos;
            self.pos = saved_pos;

            if let Ok(mr) = self.parse_table_iterative_match_result(*term_id, &[]) {
                let is_empty = mr.is_empty();
                self.pos = check_pos;

                // Cache the result
                self.terminator_match_cache
                    .borrow_mut()
                    .insert(cache_key, !is_empty);

                if !is_empty {
                    vdebug!("  TERMED Terminator matched (table-driven): {:?}", term_id);
                    self.pos = init_pos;
                    self.terminator_hits.set(self.terminator_hits.get() + 1);
                    return true;
                }
            } else {
                self.pos = check_pos;
                // Cache the failure
                self.terminator_match_cache
                    .borrow_mut()
                    .insert(cache_key, false);
            }
            vdebug!("  Terminator did not match (table-driven): {:?}", term_id);
        }

        vdebug!("  NOTERM No terminators matched");
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
    ) -> Result<usize, crate::parser::ParseError> {
        let segments = self.tokens;

        if start_idx >= segments.len() {
            vdebug!(
                "[TRIM_TO_TERM_TABLE] start_idx {} >= segments.len() {}, returning {}",
                start_idx,
                segments.len(),
                segments.len()
            );
            return Ok(segments.len());
        }

        let pruned_terms = self.prune_options_table_driven(terminators);
        vdebug!(
            "[TRIM_TO_TERM_TABLE] Scanning for terminators from idx={}, pruned_terms={:?}",
            start_idx,
            pruned_terms
        );
        for term in pruned_terms.iter() {
            #[cfg(feature = "verbose-debug")]
            let grammar_name = self.grammar_ctx.grammar_id_name(*term);
            vdebug!(
                "[TRIM_TO_TERM_TABLE] Trying terminator {:?} (name: {}) at idx={}",
                term,
                grammar_name,
                start_idx
            );
            if let Ok(_m) = self.try_match_grammar_table_driven(*term, start_idx, &[]) {
                vdebug!(
                    "[TRIM_TO_TERM_TABLE] Terminator {:?} (name: {}) matched immediately at idx={}, returning start_idx={}",
                    term,
                    grammar_name,
                    start_idx,
                    start_idx
                );
                // Terminator matched immediately at (or right after) start_idx.
                // Return start_idx so that max_idx is trimmed to exclude the
                // terminator and any content it covers.
                return Ok(start_idx);
            } else {
                vdebug!(
                    "[TRIM_TO_TERM_TABLE] Terminator {:?} (name: {}) did NOT match at idx={}",
                    term,
                    grammar_name,
                    start_idx
                );
            }
        }

        let term_match =
            self.greedy_match_table_driven(start_idx, terminators, self.tokens.len())?;
        vdebug!(
            "[TRIM_TO_TERM_TABLE] greedy_match_table_driven returned {:?}",
            term_match
        );
        // term_match.1 is already the last code index before the terminator (computed by greedy_match_table_driven)
        let final_idx = term_match.1;
        vdebug!(
            "[TRIM_TO_TERM_TABLE] Using term_match.1 as final_idx: {}",
            final_idx
        );
        Ok(final_idx)
    }
}
