use crate::parser::{
    table_driven::frame::{TableFrameResult, TableParseFrame, TableParseFrameStack},
    FrameContext, FrameState, MatchResult, ParseError, Parser,
};
use crate::vdebug;
use smallvec::SmallVec;
use sqlfluffrs_types::GrammarId;
use std::sync::Arc;

impl Parser<'_> {
    // ========================================================================
    // Table-driven OneOf Handlers (migrated from core.rs)
    // ========================================================================

    /// Handle OneOf Initial state using table-driven approach
    pub(crate) fn handle_oneof_table_driven_initial(
        &mut self,
        mut frame: TableParseFrame,
        parent_terminators: &[GrammarId],
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
            if let Ok(exclude_result) = self.parse_table_iterative(exclude_id, parent_terminators) {
                if !exclude_result.is_empty() {
                    vdebug!(
                        "OneOf[table]: exclude grammar matched at pos {}, returning Empty",
                        start_pos
                    );
                    stack.results.insert(
                        frame.frame_id,
                        (Arc::new(MatchResult::empty_at(start_pos)), start_pos, None),
                    );
                    return Ok(TableFrameResult::Done);
                }
            }
            vdebug!("OneOf[table]: exclude grammar did not match, continuing");
        }

        // Collect leading transparent tokens if allow_gaps
        let leading_ws = if allow_gaps {
            self.collect_transparent(true)
        } else {
            Vec::new()
        };
        let post_skip_pos = self.pos;

        // Combine terminators
        let local_terminators: Vec<GrammarId> = self.grammar_ctx.terminators(grammar_id).collect();
        let all_terminators = crate::parser::core::Parser::combine_terminators_table_driven(
            &local_terminators,
            parent_terminators,
            reset_terminators,
        );

        // Calculate max_idx with terminators
        let max_idx = self.calculate_max_idx_with_elements_table_driven(
            post_skip_pos,
            &all_terminators,
            &[],
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
        if parse_mode == sqlfluffrs_types::ParseMode::Greedy
            && self.is_terminated_table_driven(&all_terminators)
        {
            vdebug!("OneOf[table]: Early termination - at terminator position");
            if optional {
                stack.results.insert(
                    frame.frame_id,
                    (
                        Arc::new(MatchResult::empty_at(post_skip_pos)),
                        post_skip_pos,
                        None,
                    ),
                );
                return Ok(TableFrameResult::Done);
            }
        }

        // Get element children (excluding exclude grammar if present)
        let all_children: Vec<GrammarId> = self.grammar_ctx.element_children(grammar_id).collect();

        // Prune options based on simple hints (conservative - keeps all for now)
        let pruned_children = self.prune_options_table_driven(&all_children);

        // Debug: list kept children names
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

        if pruned_children.is_empty() {
            vdebug!("OneOf[table]: No children after pruning, returning Empty");
            stack.results.insert(
                frame.frame_id,
                (
                    Arc::new(MatchResult::empty_at(post_skip_pos)),
                    post_skip_pos,
                    None,
                ),
            );
            return Ok(TableFrameResult::Done);
        }

        // Track match attempts (like Python's longest_match - each option is an attempt)
        self.match_attempts
            .set(self.match_attempts.get() + pruned_children.len());

        // Try first child
        let first_child = pruned_children[0];

        vdebug!(
            "OneOf[table]: Trying first of {} pruned children, grammar_id={}",
            pruned_children.len(),
            first_child.0
        );

        // Save initial collected positions count for O(1) rollback via truncate
        // This ensures each child gets a fresh view of which whitespace to collect
        let initial_collected_count = self.collected_transparent_positions.len();

        // Store context for WaitingForChild state
        frame.context = FrameContext::OneOfTableDriven {
            grammar_id,
            pruned_children: pruned_children.clone(),
            leading_ws,
            post_skip_pos,
            longest_match: None,
            tried_elements: 0,
            max_idx,
            last_child_frame_id: Some(stack.frame_id_counter),
            current_child_id: Some(first_child),
            initial_collected_count,
        };

        frame.state = FrameState::WaitingForChild {
            child_index: 0,
            total_children: 1,
        };

        // CRITICAL: Store terminators in frame for use when trying subsequent children
        frame.table_terminators = SmallVec::from_vec(all_terminators.clone());

        // Create table-driven child frame with filtered terminators
        let mut child_frame = TableParseFrame::new_child(
            stack.frame_id_counter,
            first_child,
            post_skip_pos,
            all_terminators.clone(),
            Some(max_idx),
        );

        vdebug!(
            "OneOf[table]: Pushing child frame: parent_frame_id={}, child_frame_id={}, child_gid={}",
            frame.frame_id,
            child_frame.frame_id,
            first_child.0
        );

        stack.increment_frame_id_counter();
        stack.push(&mut frame);
        stack.push(&mut child_frame);
        Ok(TableFrameResult::Done)
    }

    /// Handle OneOf WaitingForChild state using table-driven approach
    pub(crate) fn handle_oneof_table_driven_waiting_for_child(
        &mut self,
        mut frame: TableParseFrame,
        child_match: &MatchResult,
        child_end_pos: &usize,
        stack: &mut TableParseFrameStack,
    ) -> Result<TableFrameResult, ParseError> {
        let FrameContext::OneOfTableDriven {
            pruned_children,
            post_skip_pos,
            longest_match,
            tried_elements,
            max_idx,
            current_child_id,
            initial_collected_count,
            ..
        } = &mut frame.context
        else {
            unreachable!("Expected OneOfTableDriven context");
        };

        let consumed = *child_end_pos - *post_skip_pos;
        let current_child = current_child_id.expect("current_child_id should be set");

        // Store the child result for reuse
        let child_match_rc = Arc::new(child_match.clone());

        // Values needed for logic (always computed)
        let child_end_pos_val = *child_end_pos;
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
                        candidate_tokens.push(tok.raw().to_string());
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
            self.complete_match_early_exits
                .set(self.complete_match_early_exits.get() + 1);
            *longest_match = Some((child_match_rc, consumed, current_child));
            // Skip directly to Combining state
            frame.state = FrameState::Combining;
            stack.push(&mut frame);
            return Ok(TableFrameResult::Done);
        }

        // Update longest match if this is better
        let mut should_early_terminate = false;
        if !child_match.is_empty() {
            let is_better = if let Some((ref current_best, current_consumed, _)) = longest_match {
                // Use MatchResult's contains_unparsable instead of is_node_clean
                let current_is_clean = !current_best.contains_unparsable();

                if child_is_clean && !current_is_clean {
                    true
                } else if !child_is_clean && current_is_clean {
                    false
                } else {
                    consumed > *current_consumed
                }
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

                // Python parity: Check for early termination with terminators
                // If we have a match and there's a terminator at the next position,
                // we can stop trying other options (significant performance improvement)
                let next_pos_after_match = child_end_pos_val;

                // Skip to next code position to check for terminators
                let next_code_pos =
                    self.skip_start_index_forward_to_code(next_pos_after_match, *max_idx);

                // If we've reached the end, consider it terminated
                if next_code_pos >= self.tokens.len() {
                    vdebug!("OneOf[table]: Early termination - reached end of tokens");
                    should_early_terminate = true;
                } else if !frame.table_terminators.is_empty() {
                    // Check if any terminator matches at this position
                    for terminator_id in &frame.table_terminators {
                        // Skip NONCODE sentinel value - it's handled separately in is_terminated
                        if *terminator_id == sqlfluffrs_types::GrammarId::NONCODE {
                            // Check if there's a non-code token at the current position
                            if next_code_pos < self.tokens.len() {
                                let tok = &self.tokens[next_code_pos];
                                if !tok.is_code() {
                                    vdebug!(
                                        "OneOf[table]: Early termination - NONCODE terminator matched non-code token at pos {}",
                                        next_code_pos
                                    );
                                    should_early_terminate = true;
                                    break;
                                }
                            }
                            continue;
                        }

                        self.pos = next_code_pos;
                        if let Ok(term_result) = self.parse_table_iterative(*terminator_id, &[]) {
                            if !term_result.is_empty() {
                                vdebug!(
                                    "OneOf[table]: Early termination - terminator {} matched at pos {}",
                                    terminator_id.0,
                                    next_code_pos
                                );
                                should_early_terminate = true;
                                break;
                            }
                        }
                    }
                }
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
            stack.push(&mut frame);
            return Ok(TableFrameResult::Done);
        }

        // Try next child
        if *tried_elements < pruned_children.len() {
            // CRITICAL: Restore collected positions before trying next child
            // This ensures each child gets a fresh view of which whitespace to collect.
            // Without this, the first child collects whitespace, marks it collected,
            // and subsequent children skip that whitespace - leading to missing whitespace
            // in the final AST if a later child wins.
            // OPTIMIZATION: Use truncate instead of clone for O(1) rollback
            self.collected_transparent_positions
                .truncate(*initial_collected_count);
            vdebug!(
                "OneOf[table]: Truncated collected_transparent_positions to {} (was {})",
                initial_collected_count,
                self.collected_transparent_positions.len()
            );

            // Try next child
            self.pos = *post_skip_pos;
            let next_child = pruned_children[*tried_elements];
            *current_child_id = Some(next_child);

            vdebug!(
                "OneOf[table]: Trying next child grammar_id={}",
                next_child.0
            );

            frame.state = FrameState::WaitingForChild {
                child_index: 0,
                total_children: 1,
            };

            // Build child frame using same table_terminators as parent
            let child_frame = TableParseFrame::new_child(
                stack.frame_id_counter,
                next_child,
                *post_skip_pos,
                frame.table_terminators.to_vec(),
                Some(*max_idx),
            );

            TableParseFrame::push_child_and_update_parent(stack, &mut frame, child_frame, "OneOf");
            Ok(TableFrameResult::Done)
        } else {
            // Should never reach here due to early termination logic above
            unreachable!("OneOf should have terminated in early termination check")
        }
    }

    /// Handle OneOf Combining state using table-driven approach
    pub(crate) fn handle_oneof_table_driven_combining(
        &mut self,
        mut frame: TableParseFrame,
        _stack: &mut TableParseFrameStack,
    ) -> Result<TableFrameResult, ParseError> {
        // Extract values from context by moving them out
        let (leading_ws, post_skip_pos, longest_match) = match &mut frame.context {
            FrameContext::OneOfTableDriven {
                leading_ws,
                post_skip_pos,
                longest_match,
                ..
            } => {
                // Take ownership to avoid clones
                (
                    std::mem::take(leading_ws),
                    *post_skip_pos,
                    longest_match.take(),
                )
            }
            _ => {
                return Err(ParseError::new(
                    "Expected OneOfTableDriven context in combining".to_string(),
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
        } else {
            vdebug!(
                "OneOf[table] Combining DEBUG: no match found, frame.accumulated={}",
                frame.accumulated.len()
            );
        }

        // Build final result
        let (result_match, final_pos, _child_id) =
            if let Some((best_match, best_consumed, best_child_id)) = longest_match {
                // Track successful match (like Python's longest_match returning a match)
                self.match_successes.set(self.match_successes.get() + 1);

                let final_pos = post_skip_pos + best_consumed;
                self.pos = final_pos;

                let result = if !leading_ws.is_empty() {
                    // Prepend leading whitespace as MatchResults
                    let mut children = leading_ws;
                    children.push(Arc::clone(&best_match));
                    MatchResult::sequence(frame.pos, final_pos, children)
                } else {
                    (*best_match).clone()
                };

                (result, final_pos, Some(best_child_id))
            } else {
                // No match found
                let final_pos = frame.pos;
                self.pos = final_pos;

                (MatchResult::empty_at(frame.pos), final_pos, None)
            };

        // Transition to Complete
        frame.end_pos = Some(final_pos);
        frame.state = FrameState::Complete(Arc::new(result_match));

        Ok(TableFrameResult::Push(frame))
    }
}
