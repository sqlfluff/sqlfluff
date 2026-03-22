use crate::parser::{
    table_driven::frame::{TableFrameResult, TableParseFrame, TableParseFrameStack},
    FrameContext, FrameState, MatchResult, ParseError, Parser,
};
#[cfg(feature = "verbose-debug")]
use crate::vdebug;
use smallvec::SmallVec;
use sqlfluffrs_types::GrammarId;
use std::sync::Arc;

impl Parser<'_> {
    // ========================================================================
    // Table-Driven AnyNumberOf Handlers (migrated from core.rs)
    // ========================================================================

    /// Handle AnyNumberOf Initial state using table-driven approach
    pub(crate) fn handle_anynumberof_table_driven_initial(
        &mut self,
        mut frame: TableParseFrame,
        stack: &mut TableParseFrameStack,
    ) -> Result<TableFrameResult, ParseError> {
        self.pos = frame.pos;
        let grammar_id = frame.grammar_id;
        let reset_terminators = self.grammar_ctx.inst(grammar_id).flags.reset_terminators();
        let parse_mode = self.grammar_ctx.inst(grammar_id).parse_mode;
        let start_pos = frame.pos;
        let (_min_times, _max_times, _max_times_per_element, has_exclude) =
            self.grammar_ctx.anynumberof_config(grammar_id);

        #[cfg(feature = "verbose-debug")]
        {
            let child_count = self.grammar_ctx.inst(grammar_id).child_count;

            vdebug!(
                "AnyNumberOf[table] Initial: frame_id={}, pos={}, grammar_id={}, children={}",
                frame.frame_id,
                start_pos,
                grammar_id.0,
                child_count
            );

            // Extra debug: build a readable grammar name (works for Ref/String/Regex variants)
            let grammar_name = self.grammar_ctx.grammar_id_name(grammar_id);

            if start_pos < self.tokens.len() {
                let tok = &self.tokens[start_pos];
                vdebug!(
                "AnyNumberOf[table] Initial: grammar='{}' start_token='{}' token_type='{}' start_pos={}",
                grammar_name,
                tok.raw,
                tok.get_type(),
                start_pos
            );
            } else {
                vdebug!(
                    "AnyNumberOf[table] Initial: grammar='{}' start_token=<EOF>",
                    grammar_name
                );
            }

            vdebug!(
                "AnyNumberOf[table]: min_times={}, max_times={:?}, max_times_per_element={:?}, has_exclude={}",
                _min_times,
                _max_times,
                _max_times_per_element,
                has_exclude
            );
        }

        // Check exclude grammar if present
        if has_exclude {
            if let Some(exclude_id) = self.grammar_ctx.exclude(grammar_id) {
                self.pos = start_pos;
                if let Ok(exclude_result) =
                    self.parse_table_iterative_match_result(exclude_id, &frame.table_terminators)
                {
                    if !exclude_result.is_empty() {
                        vdebug!("AnyNumberOf[table]: Exclude grammar matched, returning Empty");
                        return Ok(stack.complete_frame_empty(&frame));
                    }
                }
                self.pos = start_pos; // Reset position
            }
        }

        // Get all element children (excludes exclude grammar via element_children)
        let element_ids: Vec<GrammarId> = self.grammar_ctx.element_children(grammar_id).collect();
        let pruned_children = self.prune_options_table_driven(&element_ids);
        #[cfg(feature = "verbose-debug")]
        {
            // Debug element names for easier tracing
            let element_names: Vec<String> = pruned_children
                .iter()
                .map(|gid| self.grammar_ctx.grammar_id_name(*gid))
                .collect();
            vdebug!(
                "AnyNumberOf[table] element_ids_count={} names={:?}",
                pruned_children.len(),
                element_names
            );
        }

        if pruned_children.is_empty() {
            vdebug!("AnyNumberOf[table]: No elements to match after filtering");
            return Ok(stack.complete_frame_empty(&frame));
        }

        // Initialize option counter for max_times_per_element tracking
        #[cfg(feature = "verbose-debug")]
        let pruned_children_count = pruned_children.len();
        let first_element = pruned_children[0];
        let option_counter: hashbrown::HashMap<u64, usize> =
            pruned_children.iter().map(|id| (id.0 as u64, 0)).collect();

        // Combine terminators (read parent terminators from frame directly)
        let local_terminators: Vec<GrammarId> = self.grammar_ctx.terminators(grammar_id).collect();
        let all_terminators = Parser::combine_terminators_table_driven(
            &local_terminators,
            &frame.table_terminators,
            reset_terminators,
        );

        #[cfg(feature = "verbose-debug")]
        {
            // Debug: log pruned_children ids and the combined terminators
            let term_names: Vec<String> = all_terminators
                .iter()
                .map(|gid| self.grammar_ctx.grammar_id_name(*gid))
                .collect();
            vdebug!(
                "AnyNumberOf[table] pruned_children_ids={:?} all_terminators_count={} names={:?}",
                pruned_children,
                all_terminators.len(),
                term_names
            );
        }

        // Calculate max_idx using terminators only (match Python behavior)
        // Python's AnyNumberOf uses a simple trim-to-terminator rather than
        // calculating max based on element grammar lookahead. Using the
        // element-aware max_idx here caused the parse window to be too
        // restrictive in some cases (e.g. bracketed lists). Use the
        // terminator-only variant for parity.
        let max_idx = self.calculate_max_idx_table_driven(
            start_pos,
            &all_terminators,
            parse_mode,
            frame.parent_max_idx,
        )?;

        // Store calculated max_idx in frame for cache consistency
        frame.calculated_max_idx = Some(max_idx);

        vdebug!(
            "AnyNumberOf[table] Initial handler: grammar_id={}, start_pos={}, max_idx={}, parse_mode={:?}, parent_max_idx={:?}",
            grammar_id.0,
            start_pos,
            max_idx,
            parse_mode,
            frame.parent_max_idx
        );

        // If we're already at or past max_idx, return Empty
        if start_pos >= max_idx {
            vdebug!(
                "AnyNumberOf[table]: start_pos >= max_idx ({} >= {}), returning Empty",
                start_pos,
                max_idx
            );
            return Ok(stack.complete_frame_empty(&frame));
        }

        frame.state = FrameState::WaitingForChild { child_index: 0 };

        // Store context with max_times config and pruned element list
        frame.context = FrameContext::AnyNumberOfTableDriven {
            grammar_id,
            pruned_children,
            count: 0,
            matched_idx: start_pos,
            working_idx: start_pos,
            option_counter,
            max_idx,
            last_child_frame_id: Some(stack.frame_id_counter),
            matched: Arc::new(MatchResult::empty_at(start_pos)),
            longest_match: (Arc::new(MatchResult::empty_at(start_pos)), None),
            tried_elements: 0,
        };

        // Move terminators into frame (no clone)
        frame.table_terminators = SmallVec::from_vec(all_terminators);

        // Create initial child frame for the first element candidate and
        // let the WaitingForChild handler iterate remaining candidates.
        let child_frame = TableParseFrame::new_child(
            stack.frame_id_counter,
            first_element,
            start_pos,
            frame.table_terminators.to_vec(),
            Some(max_idx),
        );

        #[cfg(feature = "verbose-debug")]
        {
            vdebug!(
                "AnyNumberOf[table]: Pushing initial child for element 0 gid={} (total candidates={})",
                first_element.0,
                pruned_children_count
            );
            // Debug pushed element name
            let first_name = self.grammar_ctx.grammar_id_name(first_element);
            vdebug!(
                "AnyNumberOf[table]: pushing first_element name='{}' gid={}",
                first_name,
                first_element.0
            );
        }

        // Push parent then child (parent.last_child_frame_id was set in context)
        Ok(stack.push_child_and_wait(frame, child_frame, 0))
    }

    /// Handle AnyNumberOf WaitingForChild state using table-driven approach
    pub(crate) fn handle_anynumberof_table_driven_waiting_for_child(
        &mut self,
        mut frame: TableParseFrame,
        child_match: &Arc<MatchResult>,
        child_end_pos: &usize,
        stack: &mut TableParseFrameStack,
    ) -> Result<TableFrameResult, ParseError> {
        // Make frame mutable so we can obtain &mut references to context fields.
        let mut ctx = frame
            .context
            .as_anynumberof_mut()
            .expect("Expected AnyNumberOfTableDriven context");

        // Get current candidate for tracking
        let current_element_idx = ctx.next_candidate_idx();
        let current_candidate = ctx
            .pruned_children
            .get(current_element_idx)
            .copied()
            .unwrap_or(ctx.pruned_children[0]);

        #[cfg(feature = "verbose-debug")]
        {
            vdebug!(
                "AnyNumberOf[table] WaitingForChild: frame_id={}, child_empty={}, count={}, matched_idx={}, trying_idx={}/{}, tried_elements={}",
                frame.frame_id,
                child_match.is_empty(),
                ctx.count,
                ctx.matched_idx,
                current_element_idx,
                ctx.pruned_children.len(),
                ctx.tried_elements
            );

            // Extra debug: show pruned_children and parent table_terminators for this frame
            let pruned_dbg: Vec<u64> = ctx.pruned_children.iter().map(|g| g.0 as u64).collect();
            let table_term_names: Vec<String> = frame
                .table_terminators
                .iter()
                .map(|gid| self.grammar_ctx.grammar_id_name(*gid))
                .collect();
            vdebug!(
                "AnyNumberOf[table] WaitingForChild DEBUG: pruned_children_ids={:?} table_terminators_count={} names={:?}",
                pruned_dbg,
                frame.table_terminators.len(),
                table_term_names
            );
        }

        // Update longest_match if this child is better
        if !child_match.is_empty() && *child_end_pos <= *ctx.max_idx {
            ctx.update_longest_match(Arc::clone(child_match), *child_end_pos, current_candidate);
        }

        *ctx.tried_elements += 1;

        // Try next element candidate if there are more
        if ctx.has_more_candidates() {
            return self.try_next_anynumberof_candidate(frame, stack);
        }

        // All candidates tried - process longest match or finalize
        self.process_anynumberof_longest_match(frame, stack)
    }

    /// Try the next element candidate in AnyNumberOf
    #[inline]
    fn try_next_anynumberof_candidate(
        &mut self,
        mut frame: TableParseFrame,
        stack: &mut TableParseFrameStack,
    ) -> Result<TableFrameResult, ParseError> {
        let ctx = frame
            .context
            .as_anynumberof_mut()
            .expect("Expected AnyNumberOfTableDriven context");
        let next_element_idx = *ctx.tried_elements;
        let next_candidate = ctx.pruned_children[next_element_idx];

        vdebug!(
            "AnyNumberOf[table]: Trying next element candidate idx={} gid={}",
            next_element_idx,
            next_candidate.0
        );

        // Create and push child frame
        let child_frame = TableParseFrame::new_child(
            stack.frame_id_counter,
            next_candidate,
            *ctx.working_idx,
            frame.table_terminators.to_vec(),
            Some(*ctx.max_idx),
        );

        // Update last_child_frame_id
        *ctx.last_child_frame_id = Some(stack.frame_id_counter);

        Ok(stack.push_child_and_wait(frame, child_frame, next_element_idx))
    }

    /// Process the longest match after all candidates are tried
    #[inline]
    fn process_anynumberof_longest_match(
        &mut self,
        mut frame: TableParseFrame,
        stack: &mut TableParseFrameStack,
    ) -> Result<TableFrameResult, ParseError> {
        let mut ctx = frame
            .context
            .as_anynumberof_mut()
            .expect("Expected AnyNumberOfTableDriven context");

        let grammar_id = *ctx.grammar_id;
        let inst = self.grammar_ctx.inst(grammar_id);
        let allow_gaps = inst.flags.allow_gaps();
        let (_, max_times, max_times_per_element, _) =
            self.grammar_ctx.anynumberof_config(grammar_id);

        vdebug!(
            "AnyNumberOf[table]: All candidates tried at pos={}, longest_match={:?}, count={}, min_times={}",
            ctx.working_idx,
            (ctx.longest_match.0.end(), ctx.longest_match.1.map(|gid| gid.0)),
            ctx.count,
            inst.min_times
        );

        // Take longest_match to avoid borrow issues
        let (best_match, best_gid) = if let (ref m, Some(gid)) = ctx.longest_match {
            (Arc::clone(m), gid)
        } else {
            // No match found - finalize
            vdebug!(
                "AnyNumberOf[table]: No match found, finalizing with count={}",
                ctx.count
            );
            let matched_idx = *ctx.matched_idx;
            return Ok(stack.transition_to_combining(frame, Some(matched_idx)));
        };

        // Check for zero-width match
        if best_match.end() == *ctx.working_idx {
            log::warn!(
                "AnyNumberOf[table]: zero-width match at {}, stopping",
                ctx.working_idx
            );
            return Ok(stack.transition_to_combining(frame, None));
        }

        // Check max_times constraint
        if let Some(max) = max_times {
            if *ctx.count >= max {
                vdebug!("AnyNumberOf[table]: Reached max_times={}", max);
                let matched_idx = *ctx.matched_idx;
                return Ok(stack.transition_to_combining(frame, Some(matched_idx)));
            }
        }

        // Update option counter and check max_times_per_element
        let element_key = best_gid.0 as u64;
        let count_for_element = ctx.increment_element_count(element_key);

        if let Some(max_per) = max_times_per_element {
            if count_for_element > max_per {
                vdebug!(
                    "AnyNumberOf[table]: Element {} exceeded max_times_per_element={}",
                    element_key,
                    max_per
                );
                let matched_idx = *ctx.matched_idx;
                return Ok(stack.transition_to_combining(frame, Some(matched_idx)));
            }
        }

        // Match succeeded - accumulate and continue
        MatchResult::append_into(ctx.matched, best_match.clone());
        *ctx.matched_idx = best_match.end();
        *ctx.working_idx = *ctx.matched_idx;
        *ctx.count += 1;

        // Update max_idx if child consumed past it
        if *ctx.matched_idx > *ctx.max_idx {
            vdebug!(
                "AnyNumberOf[table]: Child consumed past max_idx ({}->{})",
                *ctx.max_idx,
                *ctx.matched_idx
            );
            *ctx.max_idx = *ctx.matched_idx;
        }

        // Skip transparent tokens for next iteration
        if allow_gaps {
            *ctx.working_idx =
                self.skip_start_index_forward_to_code(*ctx.matched_idx, *ctx.max_idx);
        }

        vdebug!(
            "AnyNumberOf[table]: Match #{}, element_key={}, matched_idx={}, working_idx={}",
            ctx.count,
            element_key,
            ctx.matched_idx,
            ctx.working_idx
        );

        // Check if we've reached max_idx
        if *ctx.matched_idx >= *ctx.max_idx {
            vdebug!(
                "AnyNumberOf[table]: Reached max_idx={}, finalizing",
                ctx.max_idx
            );
            let matched_idx = *ctx.matched_idx;
            return Ok(stack.transition_to_combining(frame, Some(matched_idx)));
        }

        // Continue matching - re-prune at new position
        self.continue_anynumberof_matching(frame, stack)
    }

    /// Continue matching after a successful repetition in AnyNumberOf
    #[inline]
    fn continue_anynumberof_matching(
        &mut self,
        mut frame: TableParseFrame,
        stack: &mut TableParseFrameStack,
    ) -> Result<TableFrameResult, ParseError> {
        let mut ctx = frame
            .context
            .as_anynumberof_mut()
            .expect("Expected AnyNumberOfTableDriven context");
        let grammar_id = *ctx.grammar_id;
        self.pos = *ctx.working_idx;

        // Re-prune at new position
        let element_ids: Vec<GrammarId> = self.grammar_ctx.element_children(grammar_id).collect();
        let repruned_children = self.prune_options_table_driven(&element_ids);

        vdebug!(
            "AnyNumberOf[table]: After match, re-pruned elements from {} to {}",
            element_ids.len(),
            repruned_children.len()
        );

        // If all elements pruned, finalize
        if repruned_children.is_empty() {
            vdebug!("AnyNumberOf[table]: All elements pruned after match");
            let matched_idx = *ctx.matched_idx;
            return Ok(stack.transition_to_combining(frame, Some(matched_idx)));
        }

        // Reset for next repetition
        ctx.reset_for_next_repetition(&repruned_children);

        let next_element = repruned_children[0];
        let child_frame = TableParseFrame::new_child(
            stack.frame_id_counter,
            next_element,
            *ctx.working_idx,
            frame.table_terminators.to_vec(),
            Some(*ctx.max_idx),
        );

        // Update context via mutable borrow
        *ctx.last_child_frame_id = Some(stack.frame_id_counter);

        // Update frame state
        Ok(stack.push_child_and_wait(frame, child_frame, 0))
    }

    /// Handle AnyNumberOf Combining state using table-driven approach
    pub(crate) fn handle_anynumberof_table_driven_combining(
        &mut self,
        mut frame: TableParseFrame,
        stack: &mut TableParseFrameStack,
    ) -> Result<TableFrameResult, ParseError> {
        let FrameContext::AnyNumberOfTableDriven {
            grammar_id,
            count,
            matched_idx,
            matched,
            ..
        } = &frame.context
        else {
            return Err(ParseError::new(
                "Expected AnyNumberOfTableDriven context in combining".to_string(),
            ));
        };

        let inst = self.grammar_ctx.inst(*grammar_id);

        vdebug!(
            "AnyNumberOf[table] Combining: frame_id={}, count={}",
            frame.frame_id,
            count
        );

        if *count < inst.min_times as usize {
            // Didn't meet min_times
            return Ok(stack.complete_frame_empty(&frame));
        }

        // Build final result
        let (result_match, final_pos) = {
            // Success - use lazy evaluation - store child_matches
            if matched.is_empty() {
                return Ok(stack.complete_frame_empty(&frame));
            } else {
                (matched.clone(), *matched_idx)
            }
        };

        self.pos = final_pos;
        frame.end_pos = Some(final_pos);
        frame.state = FrameState::Complete(result_match);

        Ok(TableFrameResult::Push(frame))
    }
}
