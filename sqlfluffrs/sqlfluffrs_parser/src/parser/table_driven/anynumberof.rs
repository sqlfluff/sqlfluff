use crate::parser::{
    iterative::{FrameResult, ParseFrameStack},
    table_driven::frame::{TableFrameResult, TableParseFrame, TableParseFrameStack},
    FrameContext, FrameState, Node, ParseError, ParseFrame, Parser,
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
        let grammar_name = match ctx.variant(grammar_id) {
            sqlfluffrs_types::GrammarVariant::Ref => ctx.ref_name(grammar_id).to_string(),
            sqlfluffrs_types::GrammarVariant::StringParser
            | sqlfluffrs_types::GrammarVariant::TypedParser
            | sqlfluffrs_types::GrammarVariant::RegexParser => ctx.template(grammar_id).to_string(),
            other => format!("{:?}", other),
        };

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
        // Debug element names for easier tracing
        let element_names: Vec<String> = element_ids
            .iter()
            .map(|gid| match ctx.variant(*gid) {
                sqlfluffrs_types::GrammarVariant::Ref => ctx.ref_name(*gid).to_string(),
                sqlfluffrs_types::GrammarVariant::StringParser
                | sqlfluffrs_types::GrammarVariant::TypedParser
                | sqlfluffrs_types::GrammarVariant::RegexParser => ctx.template(*gid).to_string(),
                other => format!("{:?}", other),
            })
            .collect();
        log::debug!(
            "AnyNumberOf[table] element_ids_count={} names={:?}",
            element_ids.len(),
            element_names
        );
        // (will log terminators after they are combined below)
        if element_ids.is_empty() {
            log::debug!("AnyNumberOf[table]: No elements to match after filtering");
            stack
                .results
                .insert(frame.frame_id, (Node::Empty, start_pos, None));
            return Ok(TableFrameResult::Done);
        }

        // Initialize option counter for max_times_per_element tracking
        let option_counter: hashbrown::HashMap<u64, usize> =
            element_ids.iter().map(|id| (id.0 as u64, 0)).collect();

        // Combine terminators
        let local_terminators: Vec<GrammarId> = ctx.terminators(grammar_id).collect();
        let all_terminators = crate::parser::core::Parser::combine_terminators_table_driven(
            &local_terminators,
            parent_terminators,
            inst.flags.reset_terminators(),
        );
        let grammar_parse_mode = inst.parse_mode;

        // Debug: log pruned_children ids and the combined terminators
        let pruned_ids: Vec<u64> = element_ids.iter().map(|g| g.0 as u64).collect();
        let term_names: Vec<String> = all_terminators
            .iter()
            .map(|gid| match ctx.variant(*gid) {
                sqlfluffrs_types::GrammarVariant::Ref => ctx.ref_name(*gid).to_string(),
                _ => ctx.template(*gid).to_string(),
            })
            .collect();
        log::debug!(
            "AnyNumberOf[table] pruned_children_ids={:?} all_terminators_count={} names={:?}",
            pruned_ids,
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

        // Store context with max_times config and pruned element list
        frame.context = crate::parser::FrameContext::AnyNumberOfTableDriven {
            grammar_id,
            pruned_children: element_ids.clone(),
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

        frame.state = crate::parser::FrameState::WaitingForChild {
            child_index: 0,
            total_children: element_ids.len(),
        };

        // Create initial child frame for the first element candidate and
        // let the WaitingForChild handler iterate remaining candidates.
        let first_element = element_ids[0];
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
            element_ids.len()
        );
        // Debug pushed element name
        let first_name = match ctx.variant(first_element) {
            sqlfluffrs_types::GrammarVariant::Ref => ctx.ref_name(first_element).to_string(),
            _ => ctx.template(first_element).to_string(),
        };
        log::debug!(
            "AnyNumberOf[table]: pushing first_element name='{}' gid={}",
            first_name,
            first_element.0
        );

        // Push parent then child (parent.last_child_frame_id was set in context)
        stack.increment_frame_id_counter();
        stack.push(&mut frame);
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
            ..
        } = &mut frame.context
        else {
            unreachable!("Expected AnyNumberOfTableDriven context");
        };

        let inst = ctx.inst(*grammar_id);
        // Use pruned_children from the frame context (set in Initial)
        // rather than recomputing element list each time.
        let element_ids: Vec<GrammarId> = pruned_children.clone();

        // Determine which element candidate index we last attempted (stored in
        // the parent's FrameState::WaitingForChild). If not present, default
        // to 0 so we try the first element.
        let (mut current_element_idx, total_candidates) = match frame.state {
            crate::parser::FrameState::WaitingForChild {
                child_index,
                total_children,
            } => (child_index, total_children),
            _ => (0usize, element_ids.len()),
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
        let pruned_dbg: Vec<u64> = element_ids.iter().map(|g| g.0 as u64).collect();
        let table_term_names: Vec<String> = frame
            .table_terminators
            .iter()
            .map(|gid| match ctx.variant(*gid) {
                sqlfluffrs_types::GrammarVariant::Ref => ctx.ref_name(*gid).to_string(),
                _ => ctx.template(*gid).to_string(),
            })
            .collect();
        log::debug!(
            "AnyNumberOf[table] WaitingForChild DEBUG: pruned_children_ids={:?} table_terminators_count={} names={:?}",
            pruned_dbg,
            frame.table_terminators.len(),
            table_term_names
        );

        if !child_node.is_empty() {
            // Check for zero-width match to prevent infinite loops
            if *child_end_pos == *working_idx {
                log::warn!(
                    "AnyNumberOf[table]: zero-width match at {}, stopping to prevent infinite loop",
                    working_idx
                );
                frame.end_pos = Some(*matched_idx);
                frame.state = FrameState::Combining;
                stack.push(&mut frame);
                return Ok(TableFrameResult::Done);
            }

            // Match succeeded - accumulate and increment count
            frame.accumulated.push(child_node.clone());
            *matched_idx = *child_end_pos;
            *working_idx = *matched_idx;
            *count += 1;

            // Update option counter for max_times_per_element using the actual
            // element grammar id that matched (current_element_idx)
            let matched_element = element_ids
                .get(current_element_idx)
                .copied()
                .unwrap_or(element_ids[0]);
            let element_key = matched_element.0 as u64;
            *option_counter.entry(element_key).or_insert(0) += 1;

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

            // Get max_times config from aux_data
            let (_min_times, max_times, max_times_per_element, _has_exclude) =
                ctx.anynumberof_config(*grammar_id);

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

            // Check max_times_per_element constraint
            if let Some(max_per) = max_times_per_element {
                let element_count = option_counter.get(&element_key).copied().unwrap_or(0);
                if element_count >= max_per {
                    log::debug!(
                        "AnyNumberOf[table]: Element {} reached max_times_per_element={}, count={}",
                        element_key,
                        max_per,
                        element_count
                    );
                    // This element can't be matched again, but continue with other elements
                    // For now, since we only try first element, this ends the loop
                    // TODO: When OneOf with ALL elements is implemented, filter this element out
                }
            }

            // Continue matching - prepare to match the next repetition. For the
            // next repetition we should start again trying all element
            // candidates from index 0.
            self.pos = *working_idx;
            let next_element = element_ids[0];
            let mut next_child_frame = TableParseFrame::new_child(
                stack.frame_id_counter,
                next_element,
                *working_idx,
                frame.table_terminators.clone(),
                Some(*max_idx),
            );

            // Reset child_index to 0 and total_children to number of candidates
            frame.state = FrameState::WaitingForChild {
                child_index: 0,
                total_children: element_ids.len(),
            };

            stack.increment_frame_id_counter();
            stack.push(&mut frame);
            stack.push(&mut next_child_frame);
            return Ok(TableFrameResult::Done);
        } else {
            // Child failed - check if we met min_times
            log::debug!(
                "AnyNumberOf[table]: Child failed at candidate_idx={}, count={}, min_times={}",
                current_element_idx,
                count,
                inst.min_times
            );

            // If there are remaining element candidates for this repetition,
            // try the next one instead of finalizing immediately.
            if current_element_idx + 1 < element_ids.len() {
                current_element_idx += 1;
                let next_candidate = element_ids[current_element_idx];

                log::debug!(
                    "AnyNumberOf[table]: Trying next element candidate idx={} gid={}",
                    current_element_idx,
                    next_candidate.0
                );

                // Update frame to indicate which candidate we're trying next
                frame.state = FrameState::WaitingForChild {
                    child_index: current_element_idx,
                    total_children: element_ids.len(),
                };

                // Push parent and next candidate child
                let mut next_child_frame = TableParseFrame::new_child(
                    stack.frame_id_counter,
                    next_candidate,
                    frame.pos,
                    frame.table_terminators.clone(),
                    Some(*max_idx),
                );

                stack.increment_frame_id_counter();
                stack.push(&mut frame);
                stack.push(&mut next_child_frame);
                return Ok(TableFrameResult::Done);
            }

            // No more candidates for this repetition - finalize based on min_times
            if *count >= inst.min_times as usize {
                // Success - we have enough matches
                frame.end_pos = Some(*matched_idx);
                frame.state = FrameState::Combining;
                stack.push(&mut frame);
                return Ok(TableFrameResult::Done);
            } else {
                // Failure - didn't meet min_times
                frame.end_pos = Some(frame.pos);
                frame.state = FrameState::Combining;
                stack.push(&mut frame);
                return Ok(TableFrameResult::Done);
            }
        }
    }

    /// Handle AnyNumberOf Combining state using table-driven approach
    pub(crate) fn handle_anynumberof_table_driven_combining(
        &mut self,
        mut frame: TableParseFrame,
        stack: &mut TableParseFrameStack,
    ) -> Result<TableFrameResult, ParseError> {
        let ctx = self.grammar_ctx.expect("GrammarContext required");
        let _stack = stack; // Suppress unused

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

        // Build final result
        let (result_node, final_pos) = if *count >= inst.min_times as usize {
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
        } else {
            // Failure - didn't meet min_times
            if inst.flags.optional() {
                (Node::Empty, frame.pos)
            } else {
                (Node::Empty, frame.pos)
            }
        };

        self.pos = final_pos;
        frame.end_pos = Some(final_pos);
        frame.state = crate::parser::FrameState::Complete(result_node);

        Ok(TableFrameResult::Push(frame))
    }
}
