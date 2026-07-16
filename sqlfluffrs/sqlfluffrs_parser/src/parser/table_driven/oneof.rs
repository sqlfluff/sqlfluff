use crate::parser::{
    table_driven::frame::{TableFrameResult, TableParseFrame, TableParseFrameStack},
    table_driven::parity,
    FrameContext, FrameState, MatchResult, OneOfState, ParseError, Parser,
};
#[cfg(feature = "verbose-debug")]
use crate::vdebug;
use sqlfluffrs_types::{GrammarId, GrammarVariant};
use std::sync::Arc;

impl Parser<'_> {
    // ========================================================================
    // Table-driven OneOf Handlers (migrated from core.rs)
    // ========================================================================

    /// Handle OneOf Initial state using table-driven approach
    pub(crate) fn handle_oneof_initial(
        &mut self,
        mut frame: TableParseFrame,
        stack: &mut TableParseFrameStack,
    ) -> Result<TableFrameResult, ParseError> {
        // CRITICAL: Restore parser position from frame
        self.pos = frame.pos;

        let grammar_id = frame.grammar_id;
        #[cfg(feature = "verbose-debug")]
        let child_count = self.grammar_ctx.inst(grammar_id).child_count;
        let allow_gaps = self.grammar_ctx.inst(grammar_id).flags.allow_gaps();
        let reset_terminators = self.grammar_ctx.inst(grammar_id).flags.reset_terminators();
        let parse_mode = self.grammar_ctx.inst(grammar_id).parse_mode;
        let optional = self.grammar_ctx.inst(grammar_id).flags.optional();
        let start_pos = frame.pos;

        vdebug!(
            "OneOf[table] Initial: frame_id={}, pos={}, grammar_id={}, children={}",
            frame.frame_id,
            start_pos,
            grammar_id.0,
            child_count
        );

        // Check exclude grammar first (before any other logic)
        if let Some(exclude_id) = self.grammar_ctx.exclude(grammar_id) {
            // Try matching exclude grammar
            if let Ok(exclude_result) =
                self.parse_table_iterative_match_result(exclude_id, &frame.table_terminators)
            {
                if !exclude_result.is_empty() {
                    vdebug!(
                        "OneOf[table]: exclude grammar matched at pos {}, returning Empty",
                        start_pos
                    );
                    return Ok(stack.complete_frame_empty(&frame));
                }
            }
            vdebug!("OneOf[table]: exclude grammar did not match, continuing");
        }

        // Collect leading transparent tokens if allow_gaps
        let post_skip_pos = self.skip_to_code_if_gaps(start_pos, self.tokens.len(), allow_gaps);

        // Combine terminators (read parent terminators from frame directly)
        let local_terminators: Vec<GrammarId> = self.grammar_ctx.terminators(grammar_id).collect();
        let all_terminators = Parser::combine_terminators(
            &local_terminators,
            &frame.table_terminators,
            reset_terminators,
        );

        // Calculate max_idx with terminators
        let max_idx = self.calculate_max_idx(
            post_skip_pos,
            &all_terminators,
            parse_mode,
            frame.parent_max_idx,
        )?;

        // Store calculated max_idx in frame for cache consistency
        frame.calculated_max_idx = Some(max_idx);

        vdebug!(
            "OneOf[table]: post_skip_pos={}, max_idx={}, terminators={}",
            post_skip_pos,
            max_idx,
            all_terminators.len()
        );

        // Early termination check for GREEDY mode
        if parse_mode == sqlfluffrs_types::ParseMode::Greedy && self.is_terminated(&all_terminators)
        {
            vdebug!("OneOf[table]: Early termination - at terminator position");
            if optional {
                return Ok(stack.complete_frame_empty(&frame));
            }
        }

        // Get element children (excluding exclude grammar if present)
        let all_children: Vec<GrammarId> = self.grammar_ctx.element_children(grammar_id).collect();

        // Prune options based on simple hints
        let pruned_children = self.prune_options(&all_children);

        // Debug: list kept children names
        #[cfg(feature = "verbose-debug")]
        {
            let mut kept_names: Vec<String> = Vec::new();
            for gid in &pruned_children {
                let var = self.grammar_ctx.variant(*gid);
                let name = match var {
                    sqlfluffrs_types::GrammarVariant::Ref => {
                        self.grammar_ctx.ref_name(*gid).to_string()
                    }
                    sqlfluffrs_types::GrammarVariant::StringParser
                    | sqlfluffrs_types::GrammarVariant::TypedParser
                    | sqlfluffrs_types::GrammarVariant::RegexParser => {
                        self.grammar_ctx.template(*gid).to_string()
                    }
                    other => format!("{:?}", other),
                };
                kept_names.push(name);
            }
            vdebug!(
                "OneOf[table]: kept_children_count={} names={:?}",
                pruned_children.len(),
                kept_names
            );
        }

        if pruned_children.is_empty() {
            vdebug!("OneOf[table]: No children after pruning, returning Empty");
            return Ok(stack.complete_frame_empty(&frame));
        }

        // Track match attempts (like Python's longest_match - each option is an attempt)
        self.metrics
            .match_attempts
            .set(self.metrics.match_attempts.get() + pruned_children.len());

        // Save first child before moving pruned_children into context
        let first_child = pruned_children[0];

        vdebug!(
            "OneOf[table]: Trying first of {} pruned children, grammar_id={}",
            pruned_children.len(),
            first_child.0
        );

        // Store context for WaitingForChild state (move pruned_children, no clone)
        frame.context = FrameContext::OneOf(OneOfState {
            grammar_id,
            pruned_children,
            post_skip_pos,
            longest_match: None,
            tried_elements: 0,
            max_idx,
            last_child_frame_id: Some(stack.frame_id_counter),
            current_child_id: Some(first_child),
        });

        // Move terminators into frame (no clone)
        frame.table_terminators = all_terminators;

        // Inline fast path: terminal candidates need no frame machinery.
        // Feed the result straight into the shared candidate-handling logic.
        self.pos = post_skip_pos;
        if let Some(mr) = self.try_terminal_inline(first_child, Some(max_idx))? {
            let end_pos = self.pos;
            let arc = Arc::new(mr);
            return self.handle_oneof_waiting_for_child(frame, &arc, &end_pos, stack);
        }

        // Create table-driven child frame (copy terminators from frame)
        let child_frame = TableParseFrame::new_child(
            stack.frame_id_counter,
            first_child,
            post_skip_pos,
            &frame.table_terminators,
            Some(max_idx),
        );

        vdebug!(
            "OneOf[table]: Pushing child frame: parent_frame_id={}, child_frame_id={}, child_gid={}",
            frame.frame_id,
            child_frame.frame_id,
            first_child.0
        );

        // Transition: push child and wait
        Ok(stack.push_child_and_wait(frame, child_frame, 0))
    }

    /// Try to match a terminal (frame-less) grammar candidate inline.
    ///
    /// OneOf candidates are dominated by synchronous terminal parsers
    /// (keywords and typed/token matchers) which succeed or fail on a single
    /// token comparison. Routing each of them through the frame machine cost
    /// a frame allocation, two stack transitions and an empty-result Arc per
    /// failed candidate. This evaluates them directly instead.
    ///
    /// Returns `Ok(None)` when the candidate is not a synchronous terminal
    /// variant (the caller falls back to the frame path). On `Ok(Some(..))`
    /// the parser position has been advanced past the match on success, or
    /// left at the candidate position on a failed match, exactly as the
    /// frame-based handlers do. The StringParser/TypedParser/MultiStringParser/
    /// RegexParser/Token variants are never frame-cached (see
    /// `parity::is_frame_cacheable`), so no cache semantics are lost for
    /// them. `Ref` IS listed as frame-cacheable there, and a `Ref` resolving
    /// to a terminal target loses that memoization by going through this
    /// path instead of the frame path's cache check - accepted here because
    /// the underlying match is a single-token comparison, cheap enough that
    /// a cache lookup is unlikely to be a net win anyway.
    pub(crate) fn try_terminal_inline(
        &mut self,
        grammar_id: GrammarId,
        parent_max_idx: Option<usize>,
    ) -> Result<Option<MatchResult>, ParseError> {
        use sqlfluffrs_types::GrammarVariant;
        let variant = self.grammar_ctx.variant(grammar_id);
        // Refs resolving to a terminal target (e.g. keyword segments) are
        // evaluated frame-free too, including the Ref wrapping.
        let result = if matches!(variant, GrammarVariant::Ref) {
            self.try_ref_terminal_inline(grammar_id, parent_max_idx)
        } else if !Self::is_terminal_variant(variant) {
            Ok(None)
        } else {
            self.dispatch_terminal_match(variant, grammar_id).map(Some)
        };
        match result {
            Ok(Some(_)) => self
                .metrics
                .terminal_fast_path_hits
                .set(self.metrics.terminal_fast_path_hits.get() + 1),
            Ok(None) => self
                .metrics
                .terminal_fast_path_misses
                .set(self.metrics.terminal_fast_path_misses.get() + 1),
            Err(_) => {}
        }
        result
    }

    /// The set of `GrammarVariant`s that can be evaluated frame-free by
    /// [`Self::dispatch_terminal_match`]: single-token parsers with no
    /// sub-grammar of their own. Shared by `try_terminal_inline` and
    /// `try_ref_terminal_inline`'s own terminal-target check so the two
    /// "is this variant terminal" answers cannot drift.
    #[inline]
    pub(crate) fn is_terminal_variant(variant: sqlfluffrs_types::GrammarVariant) -> bool {
        use sqlfluffrs_types::GrammarVariant;
        matches!(
            variant,
            GrammarVariant::StringParser
                | GrammarVariant::TypedParser
                | GrammarVariant::MultiStringParser
                | GrammarVariant::RegexParser
                | GrammarVariant::Token
        )
    }

    /// Dispatch a single-token terminal match for `grammar_id`, given its
    /// already-known `variant` (one of [`Self::is_terminal_variant`]'s set).
    /// Shared by `try_terminal_inline` and `try_ref_terminal_inline` so the
    /// two "which handler for which variant" mappings cannot drift.
    #[inline]
    pub(crate) fn dispatch_terminal_match(
        &mut self,
        variant: sqlfluffrs_types::GrammarVariant,
        grammar_id: GrammarId,
    ) -> Result<MatchResult, ParseError> {
        use sqlfluffrs_types::GrammarVariant;
        match variant {
            GrammarVariant::StringParser => self.handle_string_parser(grammar_id),
            GrammarVariant::TypedParser => self.typed_parser_match(grammar_id),
            GrammarVariant::MultiStringParser => self.handle_multi_string_parser(grammar_id),
            GrammarVariant::RegexParser => self.handle_regex_parser(grammar_id),
            GrammarVariant::Token => self.handle_token(grammar_id),
            other => {
                unreachable!("dispatch_terminal_match called with non-terminal variant {other:?}")
            }
        }
    }

    /// Handle OneOf WaitingForChild state using table-driven approach
    pub(crate) fn handle_oneof_waiting_for_child(
        &mut self,
        mut frame: TableParseFrame,
        child_match: &Arc<MatchResult>,
        child_end_pos: &usize,
        stack: &mut TableParseFrameStack,
    ) -> Result<TableFrameResult, ParseError> {
        // Owned so the inline-terminal-candidate loop below can rebind them
        // in place across candidates instead of recursing once per
        // candidate - native recursion depth would otherwise be bounded
        // only by this OneOf's candidate count.
        let mut child_match = Arc::clone(child_match);
        let mut child_end_pos = *child_end_pos;

        loop {
            let FrameContext::OneOf(OneOfState {
                pruned_children,
                post_skip_pos,
                longest_match,
                tried_elements,
                max_idx,
                current_child_id,
                ..
            }) = &mut frame.context
            else {
                unreachable!("Expected OneOf context");
            };

            let consumed = child_end_pos - *post_skip_pos;
            let current_child = current_child_id.expect("current_child_id should be set");

            // Store the child result for reuse
            let child_match_rc = Arc::clone(&child_match);

            // Values needed for logic (always computed)
            let child_end_pos_val = child_end_pos;
            let child_is_clean = if child_match.is_empty() {
                false
            } else {
                !child_match.contains_unparsable()
            };

            // Expensive debug-only variable collection (gated by verbose-debug feature)
            #[cfg(feature = "verbose-debug")]
            {
                let child_consumed = consumed;
                let child_name = match self.grammar_ctx.variant(current_child) {
                    sqlfluffrs_types::GrammarVariant::Ref => {
                        self.grammar_ctx.ref_name(current_child).to_string()
                    }
                    sqlfluffrs_types::GrammarVariant::StringParser
                    | sqlfluffrs_types::GrammarVariant::TypedParser
                    | sqlfluffrs_types::GrammarVariant::RegexParser => {
                        self.grammar_ctx.template(current_child).to_string()
                    }
                    other => format!("{:?}", other),
                };

                // Collect the raw tokens consumed by this candidate for debugging (bounded)
                let mut candidate_tokens: Vec<String> = Vec::new();
                if child_end_pos_val > *post_skip_pos {
                    let start_idx = (*post_skip_pos).min(self.tokens.len());
                    let end_idx = child_end_pos_val.min(self.tokens.len());
                    if start_idx < end_idx {
                        for tok in &self.tokens[start_idx..end_idx] {
                            candidate_tokens.push(tok.raw().to_owned());
                        }
                    }
                }

                vdebug!(
                "OneOf[table] WaitingForChild: frame_id={}, child_empty={}, consumed={}, tried={}/{}, candidate_id={}, candidate_name={}, candidate_end_pos={}, candidate_consumed={}, candidate_clean={}, candidate_tokens={:?}",
                frame.frame_id,
                child_match.is_empty(),
                consumed,
                tried_elements,
                pruned_children.len(),
                current_child.0,
                child_name,
                child_end_pos_val,
                child_consumed,
                child_is_clean,
                candidate_tokens
            );
            }

            // PYTHON PARITY: Check for COMPLETE match first (matched all available segments)
            // If we matched up to max_idx, we can return immediately without trying other options
            // This is a major optimization for expressions with many alternatives
            // See Python's longest_match() lines 245-246
            if !child_match.is_empty() && child_end_pos_val >= *max_idx {
                vdebug!(
                "OneOf[table]: COMPLETE MATCH - child {} matched all segments up to max_idx={}, returning immediately",
                current_child.0,
                max_idx
            );
                // Track early exit for stats
                self.metrics
                    .complete_match_early_exits
                    .set(self.metrics.complete_match_early_exits.get() + 1);
                *longest_match = Some((child_match_rc, consumed, current_child));
                // Skip directly to Combining state
                frame.state = FrameState::Combining;
                stack.push(frame);
                return Ok(TableFrameResult::Done);
            }

            // Update longest match if this is better
            let mut should_early_terminate = false;
            if !child_match.is_empty() {
                let is_better = if let Some((ref current_best, current_consumed, _)) = longest_match
                {
                    // Use MatchResult's contains_unparsable instead of is_node_clean
                    let current_is_clean = !current_best.contains_unparsable();
                    parity::is_better_candidate(
                        parity::MatchQualityPolicy::LongestClean,
                        consumed,
                        child_is_clean,
                        *current_consumed,
                        current_is_clean,
                    )
                } else {
                    true
                };

                if is_better {
                    *longest_match = Some((child_match_rc, consumed, current_child));
                    vdebug!(
                        "OneOf[table]: longest_match set: child_id={}, consumed={}",
                        current_child.0,
                        consumed
                    );

                    let next_code_pos =
                        self.skip_start_index_forward_to_code(child_end_pos_val, *max_idx);
                    self.pos = next_code_pos;
                    should_early_terminate = self.is_terminated(&frame.table_terminators);
                }
            }

            *tried_elements += 1;

            // Early termination: If last option OR terminated by terminators, go straight to Combining
            let is_last_option = *tried_elements >= pruned_children.len();
            if should_early_terminate || is_last_option {
                vdebug!(
                    "OneOf[table]: {} - transitioning to Combining (tried {}/{})",
                    if should_early_terminate {
                        "Early termination"
                    } else {
                        "Last option"
                    },
                    tried_elements,
                    pruned_children.len()
                );
                frame.state = FrameState::Combining;
                stack.push(frame);
                return Ok(TableFrameResult::Done);
            }

            // Try next child
            if *tried_elements < pruned_children.len() {
                self.pos = *post_skip_pos;
                let next_child = pruned_children[*tried_elements];
                *current_child_id = Some(next_child);

                vdebug!(
                    "OneOf[table]: Trying next child grammar_id={}",
                    next_child.0
                );

                // Inline fast path for terminal candidates (see
                // try_terminal_inline): loop back to the top with the new
                // candidate's result instead of recursing, so a run of
                // consecutive terminal candidates costs no extra native stack.
                if let Some(mr) = self.try_terminal_inline(next_child, Some(*max_idx))? {
                    child_end_pos = self.pos;
                    child_match = Arc::new(mr);
                    continue;
                }

                frame.state = FrameState::WaitingForChild { child_index: 0 };

                // Build child frame using same table_terminators as parent
                let child_frame = TableParseFrame::new_child(
                    stack.frame_id_counter,
                    next_child,
                    *post_skip_pos,
                    &frame.table_terminators,
                    Some(*max_idx),
                );

                stack.push_child_and_update_parent(frame, child_frame, GrammarVariant::OneOf);
                return Ok(TableFrameResult::Done);
            } else {
                // Should never reach here due to early termination logic above
                unreachable!("OneOf should have terminated in early termination check")
            }
        }
    }

    /// Handle OneOf Combining state using table-driven approach
    pub(crate) fn handle_oneof_combining(
        &mut self,
        mut frame: TableParseFrame,
        stack: &mut TableParseFrameStack,
    ) -> Result<TableFrameResult, ParseError> {
        // Extract values from context by moving them out
        let (post_skip_pos, longest_match) = match &mut frame.context {
            FrameContext::OneOf(state) => {
                // Take ownership to avoid clones
                (state.post_skip_pos, state.longest_match.take())
            }
            _ => {
                return Err(ParseError::new(
                    "Expected OneOf context in combining".to_string(),
                ));
            }
        };

        vdebug!(
            "OneOf[table] Combining: frame_id={}, has_match={}",
            frame.frame_id,
            longest_match.is_some()
        );

        #[cfg(feature = "verbose-debug")]
        if let Some((ref best_node, best_consumed, best_child_id)) = longest_match {
            vdebug!(
                "OneOf[table] Combining DEBUG: best_child_id={}, best_consumed={}, best_node={:?}",
                best_child_id.0,
                best_consumed,
                best_node
            );
        }

        // Build final result
        let result_match = if let Some((best_match, best_consumed, _best_child_id)) = longest_match
        {
            // Track successful match (like Python's longest_match returning a match)
            self.metrics
                .match_successes
                .set(self.metrics.match_successes.get() + 1);
            self.pos = post_skip_pos + best_consumed;

            best_match
        } else {
            // No match found
            self.pos = frame.pos;

            Arc::new(MatchResult::empty_at(frame.pos))
        };

        // Transition to Complete
        stack.complete_frame(frame, result_match);
        Ok(TableFrameResult::Done)
    }
}
