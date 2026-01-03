use crate::vdebug;
use sqlfluffrs_types::{GrammarId, ParseMode};

use crate::parser::{
    table_driven::frame::{TableFrameResult, TableParseFrame, TableParseFrameStack},
    DelimitedState, FrameContext, FrameState, MatchResult, ParseError, Parser,
};

impl<'a> Parser<'_> {
    // ========================================================================
    // Table-Driven Delimited Handlers
    // ========================================================================

    /// Handle Delimited Initial state using table-driven approach
    ///
    /// Structure after code generator change:
    /// - Child 0: OneOf(elements) if multiple elements, or single element directly
    /// - Child 1: delimiter
    pub(crate) fn handle_delimited_table_driven_initial(
        &mut self,
        mut frame: TableParseFrame,
        parent_terminators: &[GrammarId],
        stack: &mut TableParseFrameStack,
    ) -> Result<TableFrameResult, ParseError> {
        self.pos = frame.pos;
        let grammar_id = frame.grammar_id;
        let inst = self.grammar_ctx.inst(grammar_id);
        let start_pos = frame.pos;

        vdebug!(
            "Delimited[table] Initial: frame_id={}, pos={}, grammar_id={}, children={}",
            frame.frame_id,
            start_pos,
            grammar_id.0,
            inst.child_count
        );

        // Get children: [elements_or_oneof, delimiter]
        let all_children: Vec<GrammarId> = self.grammar_ctx.children(grammar_id).collect();
        if all_children.len() != 2 {
            vdebug!(
                "Delimited[table]: Expected exactly 2 children (elements + delimiter), got {}",
                all_children.len()
            );
            stack.results.insert(
                frame.frame_id,
                (MatchResult::empty_at(start_pos), start_pos, None),
            );
            return Ok(TableFrameResult::Done);
        }

        // Child 0 is elements (either single element or OneOf wrapping multiple)
        // Child 1 is delimiter
        let elements_id = all_children[0];
        let delimiter_id = all_children[1];

        // Get min_delimiters from aux_data
        let (_delimiter_child_idx, _min_delimiters) = self.grammar_ctx.delimited_config(grammar_id);

        vdebug!(
            "Delimited[table] elements_id={}, delimiter_id={}, min_delimiters={}",
            elements_id.0,
            delimiter_id.0,
            _min_delimiters
        );

        // CRITICAL: Filter delimiter from terminators to prevent infinite loops!
        // We must filter by grammar NAME, not just GrammarId, because the same logical
        // grammar (e.g., "CommaSegment") can have multiple GrammarIds if it's referenced
        // in different contexts. Without this, a parent's "CommaSegment" terminator
        // could prematurely terminate a child Delimited that uses "CommaSegment" as its
        // delimiter, even though we filtered out the child's specific delimiter GrammarId.
        let delimiter_name = self.grammar_ctx.grammar_id_name(delimiter_id);

        let filtered_parent_terminators: Vec<GrammarId> = parent_terminators
            .iter()
            .filter(|&term_id| {
                // Filter out ANY grammar with the same name as the delimiter
                self.grammar_ctx.grammar_id_name(*term_id) != delimiter_name
            })
            .copied()
            .collect();

        // Get local terminators (e.g., ObjectReferenceTerminatorGrammar)
        let local_terminators: Vec<GrammarId> = self.grammar_ctx.terminators(grammar_id).collect();
        let filtered_local: Vec<GrammarId> = local_terminators
            .iter()
            .filter(|&term_id| self.grammar_ctx.grammar_id_name(*term_id) != delimiter_name)
            .copied()
            .collect();

        // PYTHON PARITY: Two sets of terminators!
        // 1. all_terminators: Used for terminator checks at Delimited level (includes local)
        // 2. child_terminators: Passed to child element matcher (EXCLUDES local, only delimiter + parent)
        //
        // In Python's Delimited.match():
        // - terminator_matchers includes self.terminators (local) + parse_context.terminators
        // - But when calling longest_match, only delimiter is pushed as terminator
        // - The local terminators (ObjectReferenceTerminatorGrammar) are NOT passed to longest_match
        // - This allows longest_match to try ALL element options without early termination

        // Terminators for Delimited-level checks (includes local)
        let mut all_terminators: Vec<GrammarId> = filtered_local
            .clone()
            .into_iter()
            .chain(filtered_parent_terminators.clone())
            .collect();

        // Terminators for child element matching (EXCLUDES local, only delimiter + parent)
        // This matches Python's deeper_match(push_terminators=delimiter_matchers)
        let mut child_terminators: Vec<GrammarId> = vec![delimiter_id];
        child_terminators.extend(filtered_parent_terminators);

        // If allow_gaps is false, add a special terminator for noncode tokens.
        if !inst.flags.allow_gaps() {
            all_terminators.push(GrammarId::NONCODE);
            child_terminators.push(GrammarId::NONCODE);
        }

        vdebug!(
            "Delimited[table]: {} all_terminators, {} child_terminators (min_delimiters={})",
            all_terminators.len(),
            child_terminators.len(),
            _min_delimiters
        );

        // Store local terminators for terminator checks at Delimited level
        frame.table_terminators = all_terminators.clone();

        // Calculate max_idx with terminators
        let grammar_parse_mode = match inst.parse_mode {
            ParseMode::Strict => sqlfluffrs_types::ParseMode::Strict,
            ParseMode::Greedy => sqlfluffrs_types::ParseMode::Greedy,
            ParseMode::GreedyOnceStarted => sqlfluffrs_types::ParseMode::GreedyOnceStarted,
        };
        let max_idx = self.calculate_max_idx_table_driven(
            start_pos,
            &all_terminators,
            grammar_parse_mode,
            frame.parent_max_idx,
        )?;

        // Store context - element_children now just contains the single elements_id
        // (which may be a OneOf internally)
        frame.context = FrameContext::DelimitedTableDriven {
            grammar_id,
            delimiter_count: 0,
            matched_idx: start_pos,
            working_idx: start_pos,
            max_idx,
            state: DelimitedState::MatchingElement,
            last_child_frame_id: Some(stack.frame_id_counter),
            delimiter_match: None,
            pos_before_delimiter: None,
            element_children: vec![elements_id], // Single entry: the OneOf or single element
            child_terminators: child_terminators.clone(), // Python parity: terminators for element matching
        };

        frame.state = FrameState::WaitingForChild {
            child_index: 0,
            total_children: 1, // Always 1 now - it's either OneOf or single element
        };

        // Push child to match element(s)
        // The OneOf handler will handle trying multiple options if needed
        // PYTHON PARITY: Pass child_terminators (excludes local), NOT all_terminators
        let child_frame = TableParseFrame::new_child(
            stack.frame_id_counter,
            elements_id,
            start_pos,
            child_terminators.clone(),
            Some(max_idx),
        );

        vdebug!(
            "Delimited[table]: Trying elements grammar_id={} with {} child_terminators",
            elements_id.0,
            child_terminators.len()
        );

        stack.increment_frame_id_counter();
        stack.push(&mut frame);
        stack.push(&mut child_frame.clone());

        Ok(TableFrameResult::Done)
    }

    /// Handle Delimited WaitingForChild state using table-driven approach
    ///
    /// This matches the Python handler logic:
    /// - MatchingElement: handles termination/end/empty uniformly, then processes match
    /// - MatchingDelimiter: stores delimiter_match (doesn't push immediately), checks termination
    pub(crate) fn handle_delimited_table_driven_waiting_for_child(
        &mut self,
        mut frame: TableParseFrame,
        child_match: &MatchResult,
        child_end_pos: &usize,
        stack: &mut TableParseFrameStack,
    ) -> Result<TableFrameResult, ParseError> {
        let FrameContext::DelimitedTableDriven {
            grammar_id,
            delimiter_count,
            matched_idx,
            working_idx,
            max_idx,
            state: delim_state,
            element_children: _, // No longer used - OneOf handles element selection
            delimiter_match,
            pos_before_delimiter,
            child_terminators,
            ..
        } = &mut frame.context
        else {
            unreachable!("Expected DelimitedTableDriven context");
        };

        // Clone child_terminators before mutable borrow to use later
        let child_terminators_clone = child_terminators.clone();

        let frame_terminators = frame.table_terminators.clone();

        // Get children: [elements_or_oneof, delimiter]
        let all_children: Vec<GrammarId> = self.grammar_ctx.children(*grammar_id).collect();
        if all_children.len() != 2 {
            vdebug!("Delimited[table]: Expected 2 children (elements + delimiter)");
            panic!();
        }

        // Get configuration from aux_data
        let (_delimiter_child_idx, min_delimiters) = self.grammar_ctx.delimited_config(*grammar_id);
        // Child 0 is elements (single or OneOf), Child 1 is delimiter
        let elements_id = all_children[0];
        let delimiter_id = all_children[1];

        // Get the grammar instruction for flags
        let inst = self.grammar_ctx.inst(*grammar_id);
        let allow_gaps = inst.flags.allow_gaps();
        let allow_trailing = inst.flags.allow_trailing();
        let optional_delimiter = inst.flags.optional_delimiter();

        vdebug!(
            "Delimited[table] WaitingForChild: frame_id={}, child_empty={}, state={:?}, delim_count={}, allow_trailing={}, optional_delimiter={}",
            frame.frame_id,
            child_match.is_empty(),
            delim_state,
            delimiter_count,
            allow_trailing,
            optional_delimiter
        );

        match delim_state {
            DelimitedState::MatchingElement => {
                // If allow_gaps, skip non-code tokens before processing
                if allow_gaps {
                    *working_idx = self.skip_start_index_forward_to_code(*working_idx, *max_idx);
                }
                self.pos = *working_idx;

                // Python parity: Check for terminators BEFORE trying to match element/delimiter
                // The terminator check should be at the current position (working_idx),
                // which is AFTER the delimiter if one was matched.
                // This matches Python where working_idx is updated to match.matched_slice.stop
                // after each match, so terminator check happens from past the delimiter.
                let is_terminated = self.is_terminated_table_driven(&frame_terminators);

                // Handle termination or end of input
                if self.is_at_end() || is_terminated {
                    vdebug!(
                        "Delimited[table]: terminator/end at pos {}, matched_idx={}, delimiter_match={}",
                        self.pos,
                        matched_idx,
                        delimiter_match.is_some()
                    );

                    // Determine final position - if we have pending delimiter, use pos before it
                    let final_pos = if allow_trailing && delimiter_match.is_some() {
                        // Include trailing delimiter
                        frame.accumulated.push(delimiter_match.take().unwrap());
                        *delimiter_count += 1;
                        *matched_idx
                    } else if delimiter_match.is_some() && pos_before_delimiter.is_some() {
                        // Don't include trailing delimiter - backtrack
                        pos_before_delimiter.unwrap()
                    } else {
                        *matched_idx
                    };

                    self.pos = final_pos;
                    // CRITICAL: Update matched_idx so Combining uses the correct position
                    *matched_idx = final_pos;

                    // Check min_delimiters requirement
                    if *delimiter_count < min_delimiters {
                        frame.end_pos = Some(frame.pos);
                        frame.state = FrameState::Combining;
                        stack.push(&mut frame);
                        return Ok(TableFrameResult::Done);
                    }

                    frame.end_pos = Some(final_pos);
                    frame.state = FrameState::Combining;
                    stack.push(&mut frame);
                    return Ok(TableFrameResult::Done);
                }

                // Handle element match failure
                // With the new structure, OneOf handles trying multiple element candidates,
                // so if child_match is empty, all element options have failed
                if child_match.is_empty() {
                    vdebug!(
                        "Delimited[table]: element match failed (all candidates exhausted by OneOf), finalizing at pos {}",
                        matched_idx
                    );

                    // Determine final position
                    let final_pos = if allow_trailing && delimiter_match.is_some() {
                        frame.accumulated.push(delimiter_match.take().unwrap());
                        *delimiter_count += 1;
                        *matched_idx
                    } else if delimiter_match.is_some() && pos_before_delimiter.is_some() {
                        pos_before_delimiter.unwrap()
                    } else {
                        *matched_idx
                    };

                    self.pos = final_pos;
                    // CRITICAL: Update matched_idx so Combining uses the correct position
                    *matched_idx = final_pos;

                    if *delimiter_count < min_delimiters {
                        frame.end_pos = Some(frame.pos);
                        frame.state = FrameState::Combining;
                        stack.push(&mut frame);
                        return Ok(TableFrameResult::Done);
                    }

                    frame.end_pos = Some(final_pos);
                    frame.state = FrameState::Combining;
                    stack.push(&mut frame);
                    return Ok(TableFrameResult::Done);
                }

                // Element matched - process it
                vdebug!(
                    "Delimited[table]: element matched pos {} -> {}",
                    frame.pos,
                    child_end_pos
                );

                // PYTHON PARITY: Push the pending delimiter FIRST (if any), then the element.
                // This matches Python's behavior where delimiter is only added when the
                // NEXT element successfully matches.
                if let Some(dm) = delimiter_match.take() {
                    frame.accumulated.push(dm);
                    *delimiter_count += 1;
                }

                // Add the matched element
                frame.accumulated.push(child_match.clone());
                *matched_idx = *child_end_pos;
                *working_idx = *matched_idx;

                // If child consumed past max_idx, update it
                if *matched_idx > *max_idx {
                    vdebug!(
                        "Delimited[table]: Child consumed past max_idx ({}->{}), updating",
                        *max_idx,
                        *matched_idx
                    );
                    *max_idx = *matched_idx;
                }

                // Skip to next code position if allow_gaps
                if allow_gaps {
                    *working_idx = self.skip_start_index_forward_to_code(*working_idx, *max_idx);
                }
                self.pos = *working_idx;

                // Transition to MatchingDelimiter
                *delim_state = DelimitedState::MatchingDelimiter;

                // IMPORTANT: Don't pass max_idx to delimiter frame!
                // The delimiter should be matchable at the current position even if
                // max_idx was computed based on terminators. The delimiter itself
                // is filtered from terminators, so it should always be matchable.
                let delimiter_frame = TableParseFrame::new_child(
                    stack.frame_id_counter,
                    delimiter_id,
                    *working_idx,
                    frame.table_terminators.clone(),
                    None, // Don't constrain delimiter by max_idx
                );

                frame.state = FrameState::WaitingForChild {
                    child_index: 0,
                    total_children: 1,
                };

                TableParseFrame::push_child_and_update_parent(
                    stack,
                    &mut frame,
                    delimiter_frame,
                    "Delimited",
                );
                Ok(TableFrameResult::Done)
            }

            DelimitedState::MatchingDelimiter => {
                if child_match.is_empty() {
                    // Delimiter failed to match
                    if optional_delimiter {
                        // Python lines 157-162: If delimiter is optional and failed,
                        // loop again to try matching another element without requiring delimiter
                        vdebug!(
                            "Delimited[table]: optional delimiter failed, trying another element"
                        );
                        *delim_state = DelimitedState::MatchingElement;

                        // With new structure, elements_id (child 0) is the element grammar
                        // Just push it to try matching elements again
                        let current_max_idx = *max_idx;

                        // PYTHON PARITY: Use child_terminators (excludes local terminators)
                        let element_frame = TableParseFrame::new_child(
                            stack.frame_id_counter,
                            elements_id,
                            *working_idx,
                            child_terminators_clone.clone(),
                            Some(current_max_idx),
                        );

                        frame.state = FrameState::WaitingForChild {
                            child_index: 0,
                            total_children: 1,
                        };

                        TableParseFrame::push_child_and_update_parent(
                            stack,
                            &mut frame,
                            element_frame,
                            "Delimited",
                        );
                        return Ok(TableFrameResult::Done);
                    }

                    // Not optional - finalize
                    vdebug!("Delimited[table]: delimiter failed, finalizing");

                    if *delimiter_count < min_delimiters {
                        self.pos = frame.pos;
                        frame.end_pos = Some(frame.pos);
                        frame.state = FrameState::Combining;
                        stack.push(&mut frame);
                    } else {
                        // Handle trailing delimiter if allowed and present
                        if allow_trailing {
                            if let Some(dm) = delimiter_match.take() {
                                frame.accumulated.push(dm);
                                *delimiter_count += 1;
                            }
                        }
                        self.pos = *matched_idx;
                        frame.end_pos = Some(*matched_idx);
                        frame.state = FrameState::Combining;
                        stack.push(&mut frame);
                    }
                    return Ok(TableFrameResult::Done);
                }

                // Delimiter matched - store it (don't push to accumulated yet!)
                vdebug!(
                    "Delimited[table]: delimiter matched pos {} -> {}",
                    working_idx,
                    child_end_pos
                );

                // NOTE: We do NOT collect whitespace here between matched_idx and working_idx.
                // That whitespace (if any) will be collected when the NEXT element matches,
                // ensuring correct ordering: element → delimiter → whitespace → next_element.
                // Previously, collecting whitespace here caused misordering where whitespace
                // appeared before the delimiter in the output.

                // Store delimiter match for later (will be added when next element matches)
                *delimiter_match = Some(child_match.clone());
                *pos_before_delimiter = Some(*matched_idx);
                *matched_idx = *child_end_pos;
                *working_idx = *matched_idx;
                self.pos = *matched_idx;

                // If child consumed past max_idx, update it
                if *matched_idx > *max_idx {
                    vdebug!(
                        "Delimited[table]: Delimiter consumed past max_idx ({}->{}), updating",
                        *max_idx,
                        *matched_idx
                    );
                    *max_idx = *matched_idx;
                }

                // CRITICAL FIX: Check for termination from BEFORE the delimiter position.
                // This is essential for terminators like `Sequence(CommaSegment, TABLE)`
                // which start with the delimiter itself. If we check from AFTER the delimiter,
                // such terminators won't match and we'll incorrectly include the delimiter
                // in the output before discovering the termination.
                //
                // Save and restore self.pos to check from pos_before_delimiter
                let saved_pos = self.pos;
                self.pos = pos_before_delimiter.unwrap();
                let is_terminated = self.is_terminated_table_driven(&frame_terminators);
                self.pos = saved_pos;

                if is_terminated {
                    vdebug!("Delimited[table]: terminated after delimiter");

                    if allow_trailing {
                        // Include the trailing delimiter
                        if let Some(dm) = delimiter_match.take() {
                            frame.accumulated.push(dm);
                            *delimiter_count += 1;
                        }
                    } else {
                        // Backtrack to before delimiter
                        *matched_idx = pos_before_delimiter.unwrap();
                        *delimiter_match = None;
                    }

                    if *delimiter_count < min_delimiters {
                        frame.end_pos = Some(frame.pos);
                        frame.state = FrameState::Combining;
                        stack.push(&mut frame);
                        return Ok(TableFrameResult::Done);
                    }

                    frame.end_pos = Some(*matched_idx);
                    frame.state = FrameState::Combining;
                    stack.push(&mut frame);
                    return Ok(TableFrameResult::Done);
                }

                // Transition to MatchingElement
                *delim_state = DelimitedState::MatchingElement;

                // DON'T push the delimiter yet - we need to check for termination first.
                // The delimiter will be pushed only if we're NOT terminated.

                // Collect and skip transparent tokens (whitespace, newlines, comments) after delimiter if allow_gaps
                // NOTE: Don't constrain by max_idx - transparent tokens should be collected unconditionally
                if allow_gaps {
                    let start_pos = *working_idx;
                    // Skip to next code token (skips through comments) so we can collect all transparent tokens
                    let next_code_pos =
                        self.skip_start_index_forward_to_code(start_pos, self.tokens.len());

                    // Collect transparent tokens (whitespace, newlines, comments) in the skipped range
                    vdebug!(
                        "Delimited[table]: collecting transparent after delimiter from {} to {}",
                        start_pos,
                        next_code_pos
                    );
                    for idx in start_pos..next_code_pos {
                        if idx < self.tokens.len() {
                            let tok = &self.tokens[idx];
                            // Skip if already collected IN THIS BRANCH
                            // Note: We use mark_position_collected() which integrates with the checkpoint system
                            if self.collected_transparent_positions.contains(&idx) {
                                vdebug!("Delimited[table]: SKIPPING already collected idx={}", idx);
                                continue;
                            }
                            let tok_type = tok.get_type();
                            vdebug!("Delimited[table]: CHECKING transparent at idx={}, tok_type='{}', raw='{}'", idx, tok_type, tok.raw());
                            // PYTHON PARITY: Only collect end_of_file explicitly
                            // Whitespace, newlines, comments captured implicitly by apply()
                            if tok_type == "end_of_file" {
                                vdebug!("Delimited[table]: COLLECTING EOF at idx={}", idx);
                                frame.accumulated.push(MatchResult {
                                    matched_slice: idx..idx + 1,
                                    matched_class: None, // Inferred from token type
                                    ..Default::default()
                                });
                                self.mark_position_collected(idx);
                            } else if tok_type == "whitespace"
                                || tok_type == "newline"
                                || tok_type == "comment"
                            {
                                vdebug!(
                                    "Delimited[table]: Skipping explicit collection of {} at {} - will be captured as trailing",
                                    tok_type,
                                    idx
                                );
                            }
                        }
                    }

                    *working_idx = next_code_pos;
                }
                self.pos = *working_idx;

                // Check termination again after skipping whitespace
                // CRITICAL: Check from pos_before_delimiter, not self.pos!
                // The terminator may include the delimiter itself (e.g., ", TABLE")
                let term_check_pos = pos_before_delimiter.unwrap_or(*working_idx);
                let saved_pos = self.pos;
                self.pos = term_check_pos;
                let is_term2 =
                    self.is_at_end() || self.is_terminated_table_driven(&frame_terminators);
                self.pos = saved_pos;

                if is_term2 {
                    vdebug!("Delimited[table]: terminated after delimiter+whitespace");

                    if allow_trailing {
                        // Include the trailing delimiter
                        if let Some(dm) = delimiter_match.take() {
                            frame.accumulated.push(dm);
                            *delimiter_count += 1;
                        }
                    } else {
                        // Don't include the delimiter - backtrack
                        *matched_idx = pos_before_delimiter.unwrap();
                        *delimiter_match = None;
                    }

                    if *delimiter_count < min_delimiters {
                        frame.end_pos = Some(frame.pos);
                        frame.state = FrameState::Combining;
                        stack.push(&mut frame);
                        return Ok(TableFrameResult::Done);
                    }

                    frame.end_pos = Some(*matched_idx);
                    frame.state = FrameState::Combining;
                    stack.push(&mut frame);
                    return Ok(TableFrameResult::Done);
                }

                // NOT terminated - keep the delimiter in delimiter_match for now.
                // It will be pushed to accumulated ONLY if the next element successfully matches.
                // This ensures we don't include trailing delimiters when allow_trailing=false.
                // (The delimiter is stored in delimiter_match and will be pushed in
                // MatchingElement branch when child_match is NOT empty)

                // Re-try elements at new position
                // With the new structure, just use elements_id directly (OneOf or single element)

                // CRITICAL: After matching a delimiter, we must recalculate max_idx from the
                // new working position. The original max_idx was computed from the start position
                // and may point to THIS delimiter, which is now behind us.
                //
                // For Strict parse mode (which Delimited uses), we allow parsing to the end
                // of the token stream, BUT we must handle the case where parent_max_idx
                // was pointing TO the delimiter we just consumed.
                //
                // PYTHON PARITY FIX: If parent_max_idx points to a position we've already
                // passed (i.e., before or at the delimiter we just consumed), then the
                // parent's constraint is based on the delimiter being a terminator, which
                // is no longer relevant since we've consumed it. In this case, we should
                // ignore the parent_max_idx and recompute from the new position.
                let new_max_idx = if let Some(parent_limit) = frame.parent_max_idx {
                    // If parent_limit <= working_idx, it means the parent's constraint was
                    // likely based on the delimiter we just consumed. Ignore it and use tokens.len()
                    if parent_limit <= *working_idx {
                        self.tokens.len()
                    } else {
                        parent_limit
                    }
                } else {
                    self.tokens.len()
                };

                vdebug!(
                    "Delimited[table]: Recalculated max_idx from {} to {} at working_idx={}",
                    *max_idx,
                    new_max_idx,
                    *working_idx
                );
                *max_idx = new_max_idx;

                vdebug!(
                    "Delimited[table]: After delimiter, trying elements_id={} at pos {}, max_idx={}, working_idx={}",
                    elements_id.0,
                    *working_idx,
                    *max_idx,
                    *working_idx
                );

                // PYTHON PARITY: Use child_terminators (excludes local terminators)
                let element_frame = TableParseFrame::new_child(
                    stack.frame_id_counter,
                    elements_id,
                    *working_idx,
                    child_terminators_clone.clone(),
                    Some(*max_idx), // Use recalculated max_idx
                );

                frame.state = FrameState::WaitingForChild {
                    child_index: 0,
                    total_children: 1,
                };

                TableParseFrame::push_child_and_update_parent(
                    stack,
                    &mut frame,
                    element_frame,
                    "Delimited",
                );
                Ok(TableFrameResult::Done)
            }
        }
    }

    /// Handle Delimited Combining state using table-driven approach
    pub(crate) fn handle_delimited_table_driven_combining(
        &mut self,
        mut frame: TableParseFrame,
    ) -> Result<TableFrameResult, ParseError> {
        let FrameContext::DelimitedTableDriven {
            grammar_id,
            delimiter_count,
            matched_idx,
            ..
        } = &frame.context
        else {
            return Err(ParseError::new(
                "Expected DelimitedTableDriven context in combining".to_string(),
            ));
        };

        vdebug!(
            "Delimited[table] Combining: frame_id={}, accumulated={}, delim_count={}",
            frame.frame_id,
            frame.accumulated.len(),
            delimiter_count
        );

        // Get min_delimiters from aux_data
        let (_delimiter_child_idx, min_delimiters) = self.grammar_ctx.delimited_config(*grammar_id);

        // Build final result
        let (result_match, final_pos) = if frame.accumulated.is_empty() {
            // No matches
            (MatchResult::empty_at(frame.pos), frame.pos)
        } else if *delimiter_count < min_delimiters {
            // Not enough delimiters - fail
            vdebug!(
                "Delimited[table]: Failed - only {} delimiters, need {}",
                delimiter_count,
                min_delimiters
            );
            (MatchResult::empty_at(frame.pos), frame.pos)
        } else {
            // Success - use lazy evaluation - store child_matches
            let accumulated = std::mem::take(&mut frame.accumulated);
            (
                MatchResult::delimited(frame.pos, *matched_idx, accumulated),
                *matched_idx,
            )
        };

        self.pos = final_pos;
        frame.end_pos = Some(final_pos);
        frame.state = FrameState::Complete(result_match);

        Ok(TableFrameResult::Push(frame))
    }
}
