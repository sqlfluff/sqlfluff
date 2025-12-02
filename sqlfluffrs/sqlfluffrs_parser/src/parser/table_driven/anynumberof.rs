use crate::parser::{
    table_driven::frame::{TableFrameResult, TableParseFrame, TableParseFrameStack},
    FrameContext, FrameState, Node, ParseError, Parser,
};
use sqlfluffrs_types::GrammarId;

impl<'a> Parser<'_> {
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
        let ctx = self.grammar_ctx.expect("GrammarContext required");
        let grammar_id = frame.grammar_id;

        let inst = ctx.inst(grammar_id);
        let start_pos = frame.pos;

        log::debug!(
            "AnyNumberOf[table] Initial: frame_id={}, pos={}, grammar_id={}, children={}",
            frame.frame_id,
            start_pos,
            grammar_id.0,
            inst.child_count
        );

        // Extra debug: build a readable grammar name (works for Ref/String/Regex variants)
        let grammar_name = ctx.grammar_id_name(grammar_id);

        if start_pos < self.tokens.len() {
            let tok = &self.tokens[start_pos];
            log::debug!(
                "AnyNumberOf[table] Initial: grammar='{}' start_token='{}' token_type='{}' start_pos={}",
                grammar_name,
                tok.raw,
                tok.get_type(),
                start_pos
            );
        } else {
            log::debug!(
                "AnyNumberOf[table] Initial: grammar='{}' start_token=<EOF>",
                grammar_name
            );
        }

        // Get config from aux_data
        let (min_times, max_times, max_times_per_element, has_exclude) =
            ctx.anynumberof_config(grammar_id);

        log::debug!(
            "AnyNumberOf[table]: min_times={}, max_times={:?}, max_times_per_element={:?}, has_exclude={}",
            min_times,
            max_times,
            max_times_per_element,
            has_exclude
        );

        // Check exclude grammar if present
        if has_exclude {
            if let Some(exclude_id) = ctx.exclude(grammar_id) {
                self.pos = start_pos;
                if let Ok(exclude_result) =
                    self.parse_table_iterative(exclude_id, parent_terminators)
                {
                    if !exclude_result.is_empty() {
                        log::debug!("AnyNumberOf[table]: Exclude grammar matched, returning Empty");
                        stack
                            .results
                            .insert(frame.frame_id, (Node::Empty, start_pos, None));
                        return Ok(TableFrameResult::Done);
                    }
                }
                self.pos = start_pos; // Reset position
            }
        }

        // Get all element children (excludes exclude grammar via element_children)
        let element_ids: Vec<GrammarId> = ctx.element_children(grammar_id).collect();
        let pruned_children = self.prune_options_table_driven(&element_ids);
        // Debug element names for easier tracing
        let element_names: Vec<String> = pruned_children
            .iter()
            .map(|gid| ctx.grammar_id_name(*gid))
            .collect();
        log::debug!(
            "AnyNumberOf[table] element_ids_count={} names={:?}",
            pruned_children.len(),
            element_names
        );
        // (will log terminators after they are combined below)
        if pruned_children.is_empty() {
            log::debug!("AnyNumberOf[table]: No elements to match after filtering");
            stack
                .results
                .insert(frame.frame_id, (Node::Empty, start_pos, None));
            return Ok(TableFrameResult::Done);
        }

        // Initialize option counter for max_times_per_element tracking
        // TODO: actually prune element_ids
        let pruned_children_count = pruned_children.len();
        let first_element = pruned_children[0];
        let option_counter: hashbrown::HashMap<u64, usize> =
            pruned_children.iter().map(|id| (id.0 as u64, 0)).collect();

        // Combine terminators
        let local_terminators: Vec<GrammarId> = ctx.terminators(grammar_id).collect();
        let all_terminators = crate::parser::core::Parser::combine_terminators_table_driven(
            &local_terminators,
            parent_terminators,
            inst.flags.reset_terminators(),
        );
        let grammar_parse_mode = inst.parse_mode;

        // Debug: log pruned_children ids and the combined terminators
        let term_names: Vec<String> = all_terminators
            .iter()
            .map(|gid| ctx.grammar_id_name(*gid))
            .collect();
        log::debug!(
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
        };

        // Persist the combined terminators on the parent frame so subsequent
        // child frames (created during waiting/continuation) reuse the same
        // terminator set. Not setting this caused later child frames to be
        // created without terminators which can change matching behavior.
        frame.table_terminators = all_terminators.clone();
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

        log::debug!(
            "AnyNumberOf[table]: Pushing initial child for element 0 gid={} (total candidates={})",
            first_element.0,
            pruned_children_count
        );
        // Debug pushed element name
        let first_name = ctx.grammar_id_name(first_element);
        log::debug!(
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
        child_node: &Node,
        child_end_pos: &usize,
        stack: &mut TableParseFrameStack,
    ) -> Result<TableFrameResult, ParseError> {
        let ctx = self.grammar_ctx.expect("GrammarContext required");

        let FrameContext::AnyNumberOfTableDriven {
            grammar_id,
            pruned_children,
            count,
            matched_idx,
            working_idx,
            option_counter,
            max_idx,
            last_child_frame_id,
        } = &mut frame.context
        else {
            unreachable!("Expected AnyNumberOfTableDriven context");
        };

        let inst = ctx.inst(*grammar_id);

        // Determine which element candidate index we last attempted (stored in
        // the parent's FrameState::WaitingForChild). If not present, default
        // to 0 so we try the first element.
        let (current_element_idx, total_candidates) = match frame.state {
            FrameState::WaitingForChild {
                child_index,
                total_children,
            } => (child_index, total_children),
            _ => (0usize, pruned_children.len()),
        };

        log::debug!(
            "AnyNumberOf[table] WaitingForChild: frame_id={}, child_empty={}, count={}, matched_idx={}, trying_idx={}/{}",
            frame.frame_id,
            child_node.is_empty(),
            count,
            matched_idx,
            current_element_idx,
            total_candidates
        );

        // Extra debug: show pruned_children and parent table_terminators for this frame
        let pruned_dbg: Vec<u64> = pruned_children.iter().map(|g| g.0 as u64).collect();
        let table_term_names: Vec<String> = frame
            .table_terminators
            .iter()
            .map(|gid| ctx.grammar_id_name(*gid))
            .collect();
        log::debug!(
            "AnyNumberOf[table] WaitingForChild DEBUG: pruned_children_ids={:?} table_terminators_count={} names={:?}",
            pruned_dbg,
            frame.table_terminators.len(),
            table_term_names
        );

        if child_node.is_empty() {
            // Child failed - check if there are more element candidates to try
            log::debug!(
                "AnyNumberOf[table]: Child failed at candidate_idx={}, count={}, min_times={}",
                current_element_idx,
                count,
                inst.min_times
            );

            // If there are remaining element candidates for this repetition,
            // try the next one instead of finalizing immediately.
            if current_element_idx + 1 < pruned_children.len() {
                let next_element_idx = current_element_idx + 1;
                let next_candidate = pruned_children[next_element_idx];

                log::debug!(
                    "AnyNumberOf[table]: Trying next element candidate idx={} gid={}",
                    next_element_idx,
                    next_candidate.0
                );

                // Update frame to indicate which candidate we're trying next
                frame.state = FrameState::WaitingForChild {
                    child_index: next_element_idx,
                    total_children: pruned_children.len(),
                };

                // Push parent and next candidate child
                let new_child_frame_id = stack.frame_id_counter;
                let mut next_child_frame = TableParseFrame::new_child(
                    new_child_frame_id,
                    next_candidate,
                    *working_idx,
                    frame.table_terminators.clone(),
                    Some(*max_idx),
                );

                // Update last_child_frame_id so the parent knows which result to look up
                *last_child_frame_id = Some(new_child_frame_id);

                stack.increment_frame_id_counter();
                stack.push(&mut frame);
                stack.push(&mut next_child_frame);
                return Ok(TableFrameResult::Done);
            }

            // No more candidates for this repetition - finalize based on min_times
            log::debug!(
                "AnyNumberOf[table]: No more element candidates, finalizing with count={}, min_times={}",
                count,
                inst.min_times
            );
            frame.state = FrameState::Combining;
            stack.push(&mut frame);
            return Ok(TableFrameResult::Done);
        }
        // Child succeeded

        // Check for zero-width match to prevent infinite loops
        if *child_end_pos == *working_idx {
            log::warn!(
                "AnyNumberOf[table]: zero-width match at {}, stopping to prevent infinite loop",
                working_idx
            );
            // frame.end_pos = Some(*matched_idx);
            frame.state = FrameState::Combining;
            stack.push(&mut frame);
            return Ok(TableFrameResult::Done);
        }

        if *child_end_pos > *max_idx {
            log::debug!(
                "AnyNumberOf[table]: child_end_pos={} exceeds max_idx={}, stopping without accumulating this match",
                child_end_pos,
                max_idx
            );
            frame.end_pos = Some(*matched_idx);
            frame.state = FrameState::Combining;
            stack.push(&mut frame);
            return Ok(TableFrameResult::Done);
        }

        let allow_gaps = inst.flags.allow_gaps();
        if allow_gaps && *matched_idx < *working_idx {
            self.tokens[*matched_idx..*working_idx]
                .iter()
                .enumerate()
                .for_each(|(offset, tok)| match tok.get_type().as_str() {
                    "whitespace" => frame.accumulated.push(Node::Whitespace {
                        raw: tok.raw().to_string(),
                        token_idx: *matched_idx + offset,
                    }),
                    "newline" => frame.accumulated.push(Node::Newline {
                        raw: tok.raw().to_string(),
                        token_idx: *matched_idx + offset,
                    }),
                    _ => {}
                });
            *matched_idx = *working_idx;
        }

        // Get max_times config from aux_data
        let (_min_times, max_times, max_times_per_element, _has_exclude) =
            ctx.anynumberof_config(*grammar_id);

        if *child_end_pos > *max_idx {
            log::debug!(
                "AnyNumberOf[table]: child_end_pos={} exceeds max_idx={}, returning early",
                child_end_pos,
                max_idx
            );
            frame.end_pos = Some(*matched_idx);
            frame.state = FrameState::Combining;
            stack.push(&mut frame);
            return Ok(TableFrameResult::Done);
        }

        // Check max_times constraint (total matches across all elements)
        if let Some(max) = max_times {
            if *count >= max {
                log::debug!("AnyNumberOf[table]: Reached max_times={}, finalizing", max);
                frame.end_pos = Some(*matched_idx);
                frame.state = FrameState::Combining;
                stack.push(&mut frame);
                return Ok(TableFrameResult::Done);
            }
        }

        let matched_element = pruned_children
            .get(current_element_idx)
            .copied()
            .unwrap_or(pruned_children[0]);
        let element_key = matched_element.0 as u64;
        let count_for_element = option_counter.entry(element_key).or_insert(0);
        *count_for_element += 1;

        if let Some(max_per) = max_times_per_element {
            if *count_for_element > max_per {
                log::debug!(
                    "AnyNumberOf[table]: Element {} exceeded max_times_per_element={}, count={}",
                    element_key,
                    max_per,
                    count_for_element
                );
                // Return early, do not add match
                frame.end_pos = Some(*matched_idx);
                frame.state = FrameState::Combining;
                stack.push(&mut frame);
                return Ok(TableFrameResult::Done);
            }
        }

        // Match succeeded - accumulate and increment count
        frame.accumulated.push(child_node.clone());
        *matched_idx = *child_end_pos;
        *working_idx = *matched_idx;
        *count += 1;

        log::debug!(
            "AnyNumberOf[table]: Match #{}, element_key={}, matched_idx={}",
            count,
            element_key,
            matched_idx
        );

        // Check if we've reached max_idx
        if *matched_idx >= *max_idx {
            log::debug!(
                "AnyNumberOf[table]: Reached max_idx={}, finalizing",
                max_idx
            );
            frame.end_pos = Some(*matched_idx);
            frame.state = FrameState::Combining;
            stack.push(&mut frame);
            return Ok(TableFrameResult::Done);
        }

        // Continue matching - prepare to match the next repetition. For the
        // next repetition we should start again trying all element
        // candidates from index 0.
        self.pos = *working_idx;

        // Re-prune at the new position for better efficiency
        let element_ids: Vec<GrammarId> = ctx.element_children(*grammar_id).collect();
        let repruned_children = self.prune_options_table_driven(&element_ids);
        log::debug!(
            "AnyNumberOf[table]: After match, re-pruned elements from {} to {}",
            element_ids.len(),
            repruned_children.len()
        );

        // If all elements pruned, finalize
        if repruned_children.is_empty() {
            log::debug!("AnyNumberOf[table]: All elements pruned after match, finalizing");
            frame.end_pos = Some(*matched_idx);
            frame.state = FrameState::Combining;
            stack.push(&mut frame);
            return Ok(TableFrameResult::Done);
        }

        // Update pruned_children in context
        *pruned_children = repruned_children.clone();

        let next_element = repruned_children[0];
        let new_child_frame_id = stack.frame_id_counter;
        let mut next_child_frame = TableParseFrame::new_child(
            new_child_frame_id,
            next_element,
            *working_idx,
            frame.table_terminators.clone(),
            Some(*max_idx),
        );

        // Update last_child_frame_id so the parent knows which result to look up
        *last_child_frame_id = Some(new_child_frame_id);

        // Reset child_index to 0 and total_children to number of candidates
        frame.state = FrameState::WaitingForChild {
            child_index: 0,
            total_children: repruned_children.len(),
        };

        stack.increment_frame_id_counter();
        stack.push(&mut frame);
        stack.push(&mut next_child_frame);
        Ok(TableFrameResult::Done)
    }

    /// Handle AnyNumberOf Combining state using table-driven approach
    pub(crate) fn handle_anynumberof_table_driven_combining(
        &mut self,
        mut frame: TableParseFrame,
        stack: &mut TableParseFrameStack,
    ) -> Result<TableFrameResult, ParseError> {
        let ctx = self.grammar_ctx.expect("GrammarContext required");

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

        let inst = ctx.inst(*grammar_id);

        log::debug!(
            "AnyNumberOf[table] Combining: frame_id={}, accumulated={}, count={}",
            frame.frame_id,
            frame.accumulated.len(),
            count
        );

        if *count < inst.min_times as usize {
            // Didn't meet min_times
            self.pos = frame.pos;
            frame.end_pos = Some(frame.pos);
            frame.state = FrameState::Complete(Node::Empty);
            return Ok(TableFrameResult::Push(frame));
        }

        // Build final result
        let (result_node, final_pos) = {
            // Success - return sequence of matches
            if frame.accumulated.is_empty() {
                (Node::Empty, frame.pos)
            } else {
                (
                    Node::Sequence {
                        children: frame.accumulated.clone(),
                    },
                    *matched_idx,
                )
            }
        };

        self.pos = final_pos;
        frame.end_pos = Some(final_pos);
        frame.state = FrameState::Complete(result_node);

        Ok(TableFrameResult::Push(frame))
    }
}
