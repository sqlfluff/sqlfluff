use sqlfluffrs_types::{GrammarId, ParseMode};

use crate::parser::{
    table_driven::frame::{TableFrameResult, TableParseFrame, TableParseFrameStack},
    DelimitedState, FrameContext, FrameState, Node, ParseError, Parser,
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
        let ctx = self.grammar_ctx.expect("GrammarContext required");
        let grammar_id = frame.grammar_id;
        let inst = ctx.inst(grammar_id);
        let start_pos = frame.pos;

        log::debug!(
            "Delimited[table] Initial: frame_id={}, pos={}, grammar_id={}, children={}",
            frame.frame_id,
            start_pos,
            grammar_id.0,
            inst.child_count
        );

        // Get children: [elements_or_oneof, delimiter]
        let all_children: Vec<GrammarId> = ctx.children(grammar_id).collect();
        if all_children.len() != 2 {
            log::debug!(
                "Delimited[table]: Expected exactly 2 children (elements + delimiter), got {}",
                all_children.len()
            );
            stack
                .results
                .insert(frame.frame_id, (Node::Empty, start_pos, None));
            return Ok(TableFrameResult::Done);
        }

        // Child 0 is elements (either single element or OneOf wrapping multiple)
        // Child 1 is delimiter
        let elements_id = all_children[0];
        let delimiter_id = all_children[1];

        // Get min_delimiters from aux_data
        let (_delimiter_child_idx, min_delimiters) = ctx.delimited_config(grammar_id);

        log::debug!(
            "Delimited[table] elements_id={}, delimiter_id={}, min_delimiters={}",
            elements_id.0,
            delimiter_id.0,
            min_delimiters
        );

        // CRITICAL: Filter delimiter from terminators to prevent infinite loops!
        let filtered_terminators: Vec<GrammarId> = parent_terminators
            .iter()
            .filter(|&term_id| *term_id != delimiter_id)
            .copied()
            .collect();

        // Get local terminators and filter them too
        let local_terminators: Vec<GrammarId> = ctx.terminators(grammar_id).collect();
        let filtered_local: Vec<GrammarId> = local_terminators
            .iter()
            .filter(|&term_id| *term_id != delimiter_id)
            .copied()
            .collect();

        // Delimited does NOT respect reset_terminators - always combines
        let mut all_terminators: Vec<GrammarId> = filtered_local
            .into_iter()
            .chain(filtered_terminators)
            .collect();

        // If allow_gaps is false, add a special terminator for noncode tokens.
        if !inst.flags.allow_gaps() {
            all_terminators.push(GrammarId::NONCODE);
        }

        log::debug!(
            "Delimited[table]: {} terminators (min_delimiters={})",
            all_terminators.len(),
            min_delimiters
        );

        // CRITICAL: Update frame's table_terminators to include local terminators!
        // Otherwise WaitingForChild will use the old parent terminators.
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
        );

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
        };

        frame.state = FrameState::WaitingForChild {
            child_index: 0,
            total_children: 1, // Always 1 now - it's either OneOf or single element
        };

        // Push child to match element(s)
        // The OneOf handler will handle trying multiple options if needed
        let child_frame = TableParseFrame::new_child(
            stack.frame_id_counter,
            elements_id,
            start_pos,
            all_terminators.clone(),
            Some(max_idx),
        );

        log::debug!(
            "Delimited[table]: Trying elements grammar_id={} with {} terminators",
            elements_id.0,
            all_terminators.len()
        );

        stack.increment_frame_id_counter();
        stack.push(&mut frame);
        stack.push(&mut child_frame.clone());

        Ok(TableFrameResult::Done)
    }

    /// Handle Delimited WaitingForChild state using table-driven approach
    ///
    /// This mirrors the Arc-based handler logic:
    /// - MatchingElement: handles termination/end/empty uniformly, then processes match
    /// - MatchingDelimiter: stores delimiter_match (doesn't push immediately), checks termination
    pub(crate) fn handle_delimited_table_driven_waiting_for_child(
        &mut self,
        mut frame: TableParseFrame,
        child_node: &Node,
        child_end_pos: &usize,
        stack: &mut TableParseFrameStack,
    ) -> Result<TableFrameResult, ParseError> {
        let ctx = self.grammar_ctx.expect("GrammarContext required");

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
            ..
        } = &mut frame.context
        else {
            unreachable!("Expected DelimitedTableDriven context");
        };

        let frame_terminators = frame.table_terminators.clone();

        // Get children: [elements_or_oneof, delimiter]
        let all_children: Vec<GrammarId> = ctx.children(*grammar_id).collect();
        if all_children.len() != 2 {
            log::debug!("Delimited[table]: Expected 2 children (elements + delimiter)");
            panic!();
        }

        // Get configuration from aux_data
        let (_delimiter_child_idx, min_delimiters) = ctx.delimited_config(*grammar_id);
        // Child 0 is elements (single or OneOf), Child 1 is delimiter
        let elements_id = all_children[0];
        let delimiter_id = all_children[1];

        // Get the grammar instruction for flags
        let inst = ctx.inst(*grammar_id);
        let allow_gaps = inst.flags.allow_gaps();
        let allow_trailing = inst.flags.allow_trailing();
        let optional_delimiter = inst.flags.optional_delimiter();

        log::debug!(
            "Delimited[table] WaitingForChild: frame_id={}, child_empty={}, state={:?}, delim_count={}, allow_trailing={}, optional_delimiter={}",
            frame.frame_id,
            child_node.is_empty(),
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
                // CRITICAL: If we have a pending delimiter, check terminators from BEFORE
                // the delimiter, not after it.
                let check_pos = if delimiter_match.is_some() && pos_before_delimiter.is_some() {
                    pos_before_delimiter.unwrap()
                } else {
                    self.pos
                };

                let saved_pos = self.pos;
                self.pos = check_pos;
                let is_terminated =
                    self.is_terminated_with_elements_table_driven(&frame_terminators, &[]);
                self.pos = saved_pos;

                // Handle termination or end of input
                if self.is_at_end() || is_terminated {
                    log::debug!(
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
                // so if child_node is empty, all element options have failed
                if child_node.is_empty() {
                    log::debug!(
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
                log::debug!(
                    "Delimited[table]: element matched pos {} -> {}",
                    frame.pos,
                    child_end_pos
                );

                // Collect whitespace between matched_idx and working_idx (Python parity)
                if allow_gaps {
                    for idx in *matched_idx..*working_idx {
                        if idx < self.tokens.len() {
                            let tok = &self.tokens[idx];
                            let tok_type = tok.get_type();
                            if tok_type == "whitespace" {
                                frame.accumulated.push(Node::Whitespace {
                                    raw: tok.raw().to_string(),
                                    token_idx: idx,
                                });
                            } else if tok_type == "newline" {
                                frame.accumulated.push(Node::Newline {
                                    raw: tok.raw().to_string(),
                                    token_idx: idx,
                                });
                            }
                        }
                    }
                }

                // If there was a pending delimiter match, append it now
                if let Some(dm) = delimiter_match.take() {
                    frame.accumulated.push(dm);
                    *delimiter_count += 1;
                }

                // Add the matched element
                frame.accumulated.push(child_node.clone());
                *matched_idx = *child_end_pos;
                *working_idx = *matched_idx;

                // If child consumed past max_idx, update it
                if *matched_idx > *max_idx {
                    log::debug!(
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
                if child_node.is_empty() {
                    // Delimiter failed to match
                    if optional_delimiter {
                        // Python lines 157-162: If delimiter is optional and failed,
                        // loop again to try matching another element without requiring delimiter
                        log::debug!(
                            "Delimited[table]: optional delimiter failed, trying another element"
                        );
                        *delim_state = DelimitedState::MatchingElement;

                        // With new structure, elements_id (child 0) is the element grammar
                        // Just push it to try matching elements again
                        let current_max_idx = *max_idx;

                        let element_frame = TableParseFrame::new_child(
                            stack.frame_id_counter,
                            elements_id,
                            *working_idx,
                            frame.table_terminators.clone(),
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
                    log::debug!("Delimited[table]: delimiter failed, finalizing");

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
                log::debug!(
                    "Delimited[table]: delimiter matched pos {} -> {}",
                    working_idx,
                    child_end_pos
                );

                // Collect whitespace between matched_idx and working_idx
                if allow_gaps {
                    for idx in *matched_idx..*working_idx {
                        if idx < self.tokens.len() {
                            let tok = &self.tokens[idx];
                            let tok_type = tok.get_type();
                            if tok_type == "whitespace" {
                                frame.accumulated.push(Node::Whitespace {
                                    raw: tok.raw().to_string(),
                                    token_idx: idx,
                                });
                            } else if tok_type == "newline" {
                                frame.accumulated.push(Node::Newline {
                                    raw: tok.raw().to_string(),
                                    token_idx: idx,
                                });
                            }
                        }
                    }
                }

                // Store delimiter match for later (will be added when next element matches)
                *delimiter_match = Some(child_node.clone());
                *pos_before_delimiter = Some(*matched_idx);
                *matched_idx = *child_end_pos;
                *working_idx = *matched_idx;
                self.pos = *matched_idx;

                // If child consumed past max_idx, update it
                if *matched_idx > *max_idx {
                    log::debug!(
                        "Delimited[table]: Delimiter consumed past max_idx ({}->{}), updating",
                        *max_idx,
                        *matched_idx
                    );
                    *max_idx = *matched_idx;
                }

                // Check for termination after delimiter
                let is_terminated =
                    self.is_terminated_with_elements_table_driven(&frame_terminators, &[]);

                if is_terminated {
                    log::debug!("Delimited[table]: terminated after delimiter");

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

                // Skip whitespace after delimiter if allow_gaps
                // NOTE: Don't constrain by max_idx - whitespace should be skippable unconditionally
                if allow_gaps {
                    let next_code_pos =
                        self.skip_start_index_forward_to_code(*working_idx, self.tokens.len());
                    // Collect whitespace between delimiter and next element
                    for idx in *working_idx..next_code_pos {
                        if idx < self.tokens.len() {
                            let tok = &self.tokens[idx];
                            let tok_type = tok.get_type();
                            if tok_type == "whitespace" {
                                frame.accumulated.push(Node::Whitespace {
                                    raw: tok.raw().to_string(),
                                    token_idx: idx,
                                });
                            } else if tok_type == "newline" {
                                frame.accumulated.push(Node::Newline {
                                    raw: tok.raw().to_string(),
                                    token_idx: idx,
                                });
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
                let is_term2 = self.is_at_end()
                    || self.is_terminated_with_elements_table_driven(&frame_terminators, &[]);
                self.pos = saved_pos;

                if is_term2 {
                    log::debug!("Delimited[table]: terminated after delimiter+whitespace");

                    if allow_trailing {
                        if let Some(dm) = delimiter_match.take() {
                            frame.accumulated.push(dm);
                            *delimiter_count += 1;
                        }
                    } else {
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

                // Re-try elements at new position
                // With the new structure, just use elements_id directly (OneOf or single element)

                // CRITICAL: After matching a delimiter, we must recalculate max_idx from the
                // new working position. The original max_idx was computed from the start position
                // and may point to THIS delimiter, which is now behind us.
                //
                // For Strict parse mode (which Delimited uses), we allow parsing to the end
                // of the token stream, BUT we must respect the parent_max_idx constraint.
                // This is important because:
                // 1. For cases like DATEPART(YEAR, col1), there's no parent constraint, so we
                //    allow parsing to tokens.len() after the comma.
                // 2. For cases like "SELECT a, b FROM ..." where the parent Sequence (with
                //    GreedyOnceStarted mode) set a max_idx based on FROM, we respect that.
                //
                // The parent_max_idx already accounts for terminators - the parent grammar
                // would have computed it via calculate_max_idx_table_driven which does
                // trim_to_terminator for Greedy mode.
                let new_max_idx = if let Some(parent_limit) = frame.parent_max_idx {
                    parent_limit
                } else {
                    self.tokens.len()
                };

                log::debug!(
                    "Delimited[table]: Recalculated max_idx from {} to {} at working_idx={}",
                    *max_idx,
                    new_max_idx,
                    *working_idx
                );
                *max_idx = new_max_idx;

                log::debug!(
                    "Delimited[table]: After delimiter, trying elements_id={} at pos {}, max_idx={}, working_idx={}",
                    elements_id.0,
                    *working_idx,
                    *max_idx,
                    *working_idx
                );

                let element_frame = TableParseFrame::new_child(
                    stack.frame_id_counter,
                    elements_id,
                    *working_idx,
                    frame.table_terminators.clone(),
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
        let ctx = self.grammar_ctx.expect("GrammarContext required");

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

        log::debug!(
            "Delimited[table] Combining: frame_id={}, accumulated={}, delim_count={}",
            frame.frame_id,
            frame.accumulated.len(),
            delimiter_count
        );

        // Get min_delimiters from aux_data
        let (_delimiter_child_idx, min_delimiters) = ctx.delimited_config(*grammar_id);

        // Build final result
        let (result_node, final_pos) = if frame.accumulated.is_empty() {
            // No matches
            (Node::Empty, frame.pos)
        } else if *delimiter_count < min_delimiters {
            // Not enough delimiters - fail
            log::debug!(
                "Delimited[table]: Failed - only {} delimiters, need {}",
                delimiter_count,
                min_delimiters
            );
            (Node::Empty, frame.pos)
        } else {
            // Success - enough matches and delimiters
            (
                Node::DelimitedList {
                    children: frame.accumulated.clone(),
                },
                *matched_idx,
            )
        };

        self.pos = final_pos;
        frame.end_pos = Some(final_pos);
        frame.state = FrameState::Complete(result_node);

        Ok(TableFrameResult::Push(frame))
    }
}
