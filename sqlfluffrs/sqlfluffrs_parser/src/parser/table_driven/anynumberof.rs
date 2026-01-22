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
        parent_terminators: &[GrammarId],
        stack: &mut TableParseFrameStack,
    ) -> Result<TableFrameResult, ParseError> {
        self.pos = frame.pos;
        let grammar_id = frame.grammar_id;

        #[cfg(feature = "verbose-debug")]
        let child_count = self.grammar_ctx.inst(grammar_id).child_count;
        let reset_terminators = self.grammar_ctx.inst(grammar_id).flags.reset_terminators();
        let parse_mode = self.grammar_ctx.inst(grammar_id).parse_mode;
        let start_pos = frame.pos;

        vdebug!(
            "AnyNumberOf[table] Initial: frame_id={}, pos={}, grammar_id={}, children={}",
            frame.frame_id,
            start_pos,
            grammar_id.0,
            child_count
        );

        // Extra debug: build a readable grammar name (works for Ref/String/Regex variants)
        #[cfg(feature = "verbose-debug")]
        let grammar_name = self.grammar_ctx.grammar_id_name(grammar_id);

        #[cfg(feature = "verbose-debug")]
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

        // Get config from aux_data
        let (_min_times, _max_times, _max_times_per_element, has_exclude) =
            self.grammar_ctx.anynumberof_config(grammar_id);

        vdebug!(
            "AnyNumberOf[table]: min_times={}, max_times={:?}, max_times_per_element={:?}, has_exclude={}",
            _min_times,
            _max_times,
            _max_times_per_element,
            has_exclude
        );

        // Check exclude grammar if present
        if has_exclude {
            if let Some(exclude_id) = self.grammar_ctx.exclude(grammar_id) {
                self.pos = start_pos;
                if let Ok(exclude_result) =
                    self.parse_table_iterative(exclude_id, parent_terminators)
                {
                    if !exclude_result.is_empty() {
                        vdebug!("AnyNumberOf[table]: Exclude grammar matched, returning Empty");
                        stack.insert_empty_result(frame.frame_id, start_pos);
                        return Ok(TableFrameResult::Done);
                    }
                }
                self.pos = start_pos; // Reset position
            }
        }

        // Get all element children (excludes exclude grammar via element_children)
        let element_ids: Vec<GrammarId> = self.grammar_ctx.element_children(grammar_id).collect();
        let pruned_children = self.prune_options_table_driven(&element_ids);
        // Debug element names for easier tracing
        #[cfg(feature = "verbose-debug")]
        let element_names: Vec<String> = pruned_children
            .iter()
            .map(|gid| self.grammar_ctx.grammar_id_name(*gid))
            .collect();
        vdebug!(
            "AnyNumberOf[table] element_ids_count={} names={:?}",
            pruned_children.len(),
            element_names
        );
        // (will log terminators after they are combined below)
        if pruned_children.is_empty() {
            vdebug!("AnyNumberOf[table]: No elements to match after filtering");
            stack.insert_empty_result(frame.frame_id, start_pos);
            return Ok(TableFrameResult::Done);
        }

        // Initialize option counter for max_times_per_element tracking
        // TODO: actually prune element_ids
        let pruned_children_count = pruned_children.len();
        let first_element = pruned_children[0];
        let option_counter: hashbrown::HashMap<u64, usize> =
            pruned_children.iter().map(|id| (id.0 as u64, 0)).collect();

        // Combine terminators
        let local_terminators: Vec<GrammarId> = self.grammar_ctx.terminators(grammar_id).collect();
        let all_terminators = crate::parser::core::Parser::combine_terminators_table_driven(
            &local_terminators,
            parent_terminators,
            reset_terminators,
        );
        let grammar_parse_mode = parse_mode;

        // Debug: log pruned_children ids and the combined terminators
        #[cfg(feature = "verbose-debug")]
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

        // Calculate max_idx using terminators only (match Python behavior)
        // Python's AnyNumberOf uses a simple trim-to-terminator rather than
        // calculating max based on element grammar lookahead. Using the
        // element-aware max_idx here caused the parse window to be too
        // restrictive in some cases (e.g. bracketed lists). Use the
        // terminator-only variant for parity.
        let max_idx = self.calculate_max_idx_table_driven(
            start_pos,
            &all_terminators,
            grammar_parse_mode,
            frame.parent_max_idx,
        )?;

        // Store calculated max_idx in frame for cache consistency
        frame.calculated_max_idx = Some(max_idx);

        vdebug!(
            "AnyNumberOf[table] Initial handler: grammar_id={}, start_pos={}, max_idx={}, parse_mode={:?}, parent_max_idx={:?}",
            grammar_id.0,
            start_pos,
            max_idx,
            grammar_parse_mode,
            frame.parent_max_idx
        );

        frame.state = FrameState::WaitingForChild {
            child_index: 0,
            total_children: pruned_children_count,
        };

        // Store context with max_times config and pruned element list
        frame.context = crate::parser::FrameContext::AnyNumberOfTableDriven {
            grammar_id,
            pruned_children,
            count: 0,
            matched_idx: start_pos,
            working_idx: start_pos,
            option_counter,
            max_idx,
            last_child_frame_id: Some(stack.frame_id_counter),
            longest_match: None,
            tried_elements: 0,
        };

        // Persist the combined terminators on the parent frame so subsequent
        // child frames (created during waiting/continuation) reuse the same
        // terminator set. Not setting this caused later child frames to be
        // created without terminators which can change matching behavior.
        frame.table_terminators = SmallVec::from_vec(all_terminators.clone());
        stack.push(&mut frame);

        // Create initial child frame for the first element candidate and
        // let the WaitingForChild handler iterate remaining candidates.
        let mut child_frame = TableParseFrame::new_child(
            stack.frame_id_counter,
            first_element,
            start_pos,
            all_terminators.clone(),
            Some(max_idx),
        );

        vdebug!(
            "AnyNumberOf[table]: Pushing initial child for element 0 gid={} (total candidates={})",
            first_element.0,
            pruned_children_count
        );
        // Debug pushed element name
        #[cfg(feature = "verbose-debug")]
        let first_name = self.grammar_ctx.grammar_id_name(first_element);
        vdebug!(
            "AnyNumberOf[table]: pushing first_element name='{}' gid={}",
            first_name,
            first_element.0
        );

        // Push parent then child (parent.last_child_frame_id was set in context)
        stack.increment_frame_id_counter();
        stack.push(&mut child_frame);

        Ok(TableFrameResult::Done)
    }

    /// Handle AnyNumberOf WaitingForChild state using table-driven approach
    pub(crate) fn handle_anynumberof_table_driven_waiting_for_child(
        &mut self,
        mut frame: TableParseFrame,
        child_match: &MatchResult,
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
        #[cfg(feature = "verbose-debug")]
        let pruned_dbg: Vec<u64> = ctx.pruned_children.iter().map(|g| g.0 as u64).collect();
        #[cfg(feature = "verbose-debug")]
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

        // Update longest_match if this child is better
        if !child_match.is_empty() && *child_end_pos <= *ctx.max_idx {
            ctx.update_longest_match(
                Arc::new(child_match.clone()),
                *child_end_pos,
                current_candidate,
            );
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

        // Update frame state
        frame.state = FrameState::WaitingForChild {
            child_index: next_element_idx,
            total_children: ctx.pruned_children.len(),
        };

        // Create and push child frame
        let mut child_frame = TableParseFrame::new_child(
            stack.frame_id_counter,
            next_candidate,
            *ctx.working_idx,
            frame.table_terminators.to_vec(),
            Some(*ctx.max_idx),
        );

        // Update last_child_frame_id
        *ctx.last_child_frame_id = Some(stack.frame_id_counter);

        stack.increment_frame_id_counter();
        stack.push(&mut frame);
        stack.push(&mut child_frame);

        Ok(TableFrameResult::Done)
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
            ctx.longest_match.as_ref().map(|(_, end, gid)| (end, gid.0)),
            ctx.count,
            inst.min_times
        );

        // Take longest_match to avoid borrow issues
        let (best_match, best_end_pos, best_gid) =
            if let Some((ref m, pos, gid)) = ctx.longest_match {
                (Arc::clone(m), *pos, gid)
            } else {
                // No match found - finalize
                vdebug!(
                    "AnyNumberOf[table]: No match found, finalizing with count={}",
                    ctx.count
                );
                let matched_idx = *ctx.matched_idx;
                return Ok(frame.transition_to_combining(Some(matched_idx), stack));
            };

        // Check for zero-width match
        if best_end_pos == *ctx.working_idx {
            log::warn!(
                "AnyNumberOf[table]: zero-width match at {}, stopping",
                ctx.working_idx
            );
            return Ok(frame.transition_to_combining(None, stack));
        }

        // We no longer "collect tokens", it's all lazy evaluation now.
        if allow_gaps && *ctx.matched_idx < *ctx.working_idx {
            *ctx.matched_idx = *ctx.working_idx;
        }

        // Check max_times constraint
        if let Some(max) = max_times {
            if *ctx.count >= max {
                vdebug!("AnyNumberOf[table]: Reached max_times={}", max);
                let matched_idx = *ctx.matched_idx;
                return Ok(frame.transition_to_combining(Some(matched_idx), stack));
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
                return Ok(frame.transition_to_combining(Some(matched_idx), stack));
            }
        }

        // Match succeeded - accumulate and continue
        frame.accumulated.push(Arc::clone(&best_match));
        *ctx.matched_idx = best_end_pos;
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
            return Ok(frame.transition_to_combining(Some(matched_idx), stack));
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
            return Ok(frame.transition_to_combining(Some(matched_idx), stack));
        }

        // Reset for next repetition
        ctx.reset_for_next_repetition(&repruned_children);

        let next_element = repruned_children[0];
        let mut child_frame = TableParseFrame::new_child(
            stack.frame_id_counter,
            next_element,
            *ctx.working_idx,
            frame.table_terminators.to_vec(),
            Some(*ctx.max_idx),
        );

        // Update context via mutable borrow
        *ctx.last_child_frame_id = Some(stack.frame_id_counter);

        // Update frame state
        frame.state = FrameState::WaitingForChild {
            child_index: 0,
            total_children: repruned_children.len(),
        };

        stack.increment_frame_id_counter();
        stack.push(&mut frame);
        stack.push(&mut child_frame);
        Ok(TableFrameResult::Done)
    }

    /// Handle AnyNumberOf Combining state using table-driven approach
    pub(crate) fn handle_anynumberof_table_driven_combining(
        &mut self,
        mut frame: TableParseFrame,
    ) -> Result<TableFrameResult, ParseError> {
        let FrameContext::AnyNumberOfTableDriven {
            grammar_id,
            count,
            matched_idx,
            ..
        } = &frame.context
        else {
            return Err(ParseError::new(
                "Expected AnyNumberOfTableDriven context in combining".to_string(),
            ));
        };

        let inst = self.grammar_ctx.inst(*grammar_id);

        vdebug!(
            "AnyNumberOf[table] Combining: frame_id={}, accumulated={}, count={}",
            frame.frame_id,
            frame.accumulated.len(),
            count
        );

        if *count < inst.min_times as usize {
            // Didn't meet min_times
            self.pos = frame.pos;
            frame.end_pos = Some(frame.pos);
            frame.state = FrameState::Complete(Arc::new(MatchResult::empty_at(frame.pos)));
            return Ok(TableFrameResult::Push(frame));
        }

        // Build final result
        let (result_match, final_pos) = {
            // Success - use lazy evaluation - store child_matches
            if frame.accumulated.is_empty() {
                (Arc::new(MatchResult::empty_at(frame.pos)), frame.pos)
            } else {
                let accumulated = std::mem::take(&mut frame.accumulated);
                (
                    Arc::new(MatchResult::sequence(
                        frame.pos,
                        *matched_idx,
                        accumulated.into_vec(),
                    )),
                    *matched_idx,
                )
            }
        };

        self.pos = final_pos;
        frame.end_pos = Some(final_pos);
        frame.state = FrameState::Complete(result_match);

        Ok(TableFrameResult::Push(frame))
    }
}
