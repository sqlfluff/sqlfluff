use crate::parser::{
    table_driven::frame::{TableFrameResult, TableParseFrame, TableParseFrameStack},
    FrameContext, FrameState, MatchResult, ParseError, Parser,
};
use crate::vdebug;
use sqlfluffrs_types::GrammarId;

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
                        stack.results.insert(
                            frame.frame_id,
                            (MatchResult::empty_at(start_pos), start_pos, None),
                        );
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
            stack.results.insert(
                frame.frame_id,
                (MatchResult::empty_at(start_pos), start_pos, None),
            );
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
        let FrameContext::AnyNumberOfTableDriven {
            grammar_id,
            pruned_children,
            count,
            matched_idx,
            working_idx,
            option_counter,
            max_idx,
            last_child_frame_id,
            longest_match,
            tried_elements,
        } = &mut frame.context
        else {
            unreachable!("Expected AnyNumberOfTableDriven context");
        };

        let inst = self.grammar_ctx.inst(*grammar_id);
        #[cfg(feature = "verbose-debug")]
        let parse_mode = inst.parse_mode;

        // Determine which element candidate index we last attempted (stored in
        // the parent's FrameState::WaitingForChild). If not present, default
        // to 0 so we try the first element.
        let (current_element_idx, _total_candidates) = match frame.state {
            FrameState::WaitingForChild {
                child_index,
                total_children,
            } => (child_index, total_children),
            _ => (0usize, pruned_children.len()),
        };

        vdebug!(
            "AnyNumberOf[table] WaitingForChild: frame_id={}, child_empty={}, count={}, matched_idx={}, trying_idx={}/{}, tried_elements={}",
            frame.frame_id,
            child_match.is_empty(),
            count,
            matched_idx,
            current_element_idx,
            _total_candidates,
            tried_elements
        );

        // Extra debug: show pruned_children and parent table_terminators for this frame
        #[cfg(feature = "verbose-debug")]
        let pruned_dbg: Vec<u64> = pruned_children.iter().map(|g| g.0 as u64).collect();
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

        // Get the current candidate's grammar_id for longest_match tracking
        let current_candidate = pruned_children
            .get(current_element_idx)
            .copied()
            .unwrap_or(pruned_children[0]);

        // Update longest_match if this child is better (like OneOf does)
        if !child_match.is_empty() && *child_end_pos <= *max_idx {
            let is_better = if let Some((_, current_end_pos, _)) = longest_match {
                *child_end_pos > *current_end_pos
            } else {
                true
            };

            if is_better {
                *longest_match = Some((child_match.clone(), *child_end_pos, current_candidate));
                vdebug!(
                    "AnyNumberOf[table]: Updated longest_match: child_id={}, end_pos={}",
                    current_candidate.0,
                    child_end_pos
                );
            }
        }

        *tried_elements += 1;

        // Try next element candidate if there are more
        if current_element_idx + 1 < pruned_children.len() {
            let next_element_idx = current_element_idx + 1;
            let next_candidate = pruned_children[next_element_idx];

            vdebug!(
                "AnyNumberOf[table]: Trying next element candidate idx={} gid={} (for longest_match)",
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

        // All element candidates tried for this repetition - use longest_match if any
        vdebug!(
            "AnyNumberOf[table]: All candidates tried at pos={}, longest_match={:?}, count={}, min_times={}, max_idx={}",
            working_idx,
            longest_match.as_ref().map(|(_, end, gid)| (end, gid.0)),
            count,
            inst.min_times,
            max_idx
        );

        if let Some((best_match, best_end_pos, best_gid)) = longest_match.take() {
            // Check for zero-width match to prevent infinite loops
            if best_end_pos == *working_idx {
                log::warn!(
                    "AnyNumberOf[table]: zero-width match at {}, stopping to prevent infinite loop",
                    working_idx
                );
                frame.state = FrameState::Combining;
                stack.push(&mut frame);
                return Ok(TableFrameResult::Done);
            }

            // Collect transparent tokens (whitespace, newlines, comments) before the match if allow_gaps is true
            let allow_gaps = inst.flags.allow_gaps();
            if allow_gaps && *matched_idx < *working_idx {
                for offset in 0..(*working_idx - *matched_idx) {
                    let token_idx = *matched_idx + offset;
                    let tok = &self.tokens[token_idx];
                    // Skip if already collected IN THIS BRANCH
                    if self.collected_transparent_positions.contains(&token_idx) {
                        continue;
                    }
                    // PYTHON PARITY: Only collect end_of_file explicitly
                    // Whitespace, newlines, comments captured implicitly by apply()
                    match tok.get_type().as_str() {
                        "end_of_file" => {
                            frame.accumulated.push(MatchResult {
                                matched_slice: token_idx..token_idx + 1,
                                matched_class: None, // Inferred from token type
                                ..Default::default()
                            });
                            self.mark_position_collected(token_idx);
                        }
                        "whitespace" | "newline" | "comment" => {
                            vdebug!(
                                "AnyNumberOf[table]: Skipping explicit collection of {} at {} - will be captured as trailing",
                                tok.get_type(),
                                token_idx
                            );
                        }
                        _ => {}
                    }
                }
                *matched_idx = *working_idx;
            }

            // Get max_times config from aux_data
            let (_min_times, max_times, max_times_per_element, _has_exclude) =
                self.grammar_ctx.anynumberof_config(*grammar_id);

            // Check max_times constraint (total matches across all elements)
            if let Some(max) = max_times {
                if *count >= max {
                    vdebug!("AnyNumberOf[table]: Reached max_times={}, finalizing", max);
                    frame.end_pos = Some(*matched_idx);
                    frame.state = FrameState::Combining;
                    stack.push(&mut frame);
                    return Ok(TableFrameResult::Done);
                }
            }

            // Update option counter for max_times_per_element
            let element_key = best_gid.0 as u64;
            let count_for_element = option_counter.entry(element_key).or_insert(0);
            *count_for_element += 1;

            if let Some(max_per) = max_times_per_element {
                if *count_for_element > max_per {
                    vdebug!(
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
            frame.accumulated.push(best_match);
            *matched_idx = best_end_pos;
            *working_idx = *matched_idx;
            *count += 1;

            // If child consumed past current max_idx, update max_idx to allow
            // transparent token collection and subsequent children to continue
            // from the correct position. This handles cases where a child
            // (like Bracketed) legitimately consumed past the terminator-based
            // max_idx constraint.
            if *matched_idx > *max_idx {
                vdebug!(
                    "AnyNumberOf[table]: Child consumed past max_idx ({}->{}), updating max_idx to matched_idx",
                    *max_idx, *matched_idx
                );
                *max_idx = *matched_idx;
            }

            // Skip transparent tokens (including comments) for next iteration if allow_gaps is true (Python behavior)
            // This matches Python's AnyNumberOf.match which calls
            // skip_start_index_forward_to_code after each successful match.
            if allow_gaps {
                *working_idx = self.skip_start_index_forward_to_code(*matched_idx, *max_idx);
            }

            vdebug!(
                "AnyNumberOf[table]: Match #{} (longest), element_key={}, matched_idx={}, working_idx={}",
                count,
                element_key,
                matched_idx,
                working_idx
            );

            // Check if we've reached max_idx
            if *matched_idx >= *max_idx {
                vdebug!(
                    "AnyNumberOf[table]: Reached max_idx={}, matched_idx={}, parent_max_idx={:?}, parse_mode={:?}, finalizing",
                    max_idx,
                    matched_idx,
                    frame.parent_max_idx,
                    parse_mode
                );
                frame.end_pos = Some(*matched_idx);
                frame.state = FrameState::Combining;
                stack.push(&mut frame);
                return Ok(TableFrameResult::Done);
            }

            // Continue matching - prepare to match the next repetition
            // Reset for next repetition: try all element candidates from index 0
            self.pos = *working_idx;

            // Re-prune at the new position for better efficiency
            let element_ids: Vec<GrammarId> =
                self.grammar_ctx.element_children(*grammar_id).collect();
            let repruned_children = self.prune_options_table_driven(&element_ids);
            vdebug!(
                "AnyNumberOf[table]: After match, re-pruned elements from {} to {}",
                element_ids.len(),
                repruned_children.len()
            );

            // If all elements pruned, finalize
            if repruned_children.is_empty() {
                vdebug!("AnyNumberOf[table]: All elements pruned after match, finalizing");
                frame.end_pos = Some(*matched_idx);
                frame.state = FrameState::Combining;
                stack.push(&mut frame);
                return Ok(TableFrameResult::Done);
            }

            // Update pruned_children in context
            *pruned_children = repruned_children.clone();

            // Reset longest_match and tried_elements for next repetition
            *longest_match = None;
            *tried_elements = 0;

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
            return Ok(TableFrameResult::Done);
        }

        // No match found - finalize based on min_times
        vdebug!(
            "AnyNumberOf[table]: No match found, finalizing with count={}, min_times={}",
            count,
            inst.min_times
        );
        frame.state = FrameState::Combining;
        stack.push(&mut frame);
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
            frame.state = FrameState::Complete(MatchResult::empty_at(frame.pos));
            return Ok(TableFrameResult::Push(frame));
        }

        // Build final result
        let (result_match, final_pos) = {
            // Success - use lazy evaluation - store child_matches
            if frame.accumulated.is_empty() {
                (MatchResult::empty_at(frame.pos), frame.pos)
            } else {
                let accumulated = std::mem::take(&mut frame.accumulated);
                (
                    MatchResult::sequence(frame.pos, *matched_idx, accumulated),
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
