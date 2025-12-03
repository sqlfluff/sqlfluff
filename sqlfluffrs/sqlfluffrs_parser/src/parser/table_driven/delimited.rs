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

        // Get children: elements + delimiter
        let all_children: Vec<GrammarId> = ctx.children(grammar_id).collect();
        // Debug: map children to readable names for diagnostics
        let child_names: Vec<String> = all_children
            .iter()
            .map(|gid| ctx.grammar_id_name(*gid))
            .collect();
        log::debug!(
            "Delimited[table] children ids={:?} names={:?}",
            all_children.iter().map(|g| g.0).collect::<Vec<u32>>(),
            child_names
        );
        if all_children.len() < 2 {
            log::debug!("Delimited[table]: Not enough children (need elements + delimiter)");
            stack
                .results
                .insert(frame.frame_id, (Node::Empty, start_pos, None));
            return Ok(TableFrameResult::Done);
        }

        // Get configuration from aux_data
        let (delimiter_child_idx, min_delimiters) = ctx.delimited_config(grammar_id);

        // Use delimiter_child_idx to select delimiter
        let delimiter_id = all_children[delimiter_child_idx];
        // All other children except the delimiter are elements
        let element_ids: Vec<GrammarId> = all_children
            .iter()
            .enumerate()
            .filter_map(|(i, &gid)| {
                if i != delimiter_child_idx {
                    Some(gid)
                } else {
                    None
                }
            })
            .collect();

        // CRITICAL: Filter delimiter from terminators to prevent infinite loops!
        // This matches Python's behavior: `*(t for t in terminators if t not in delimiter_matchers)`
        // The delimiter should NOT be able to terminate the delimited list itself.
        log::debug!(
            "Delimited[table]: Filtering delimiter from {} parent terminators",
            parent_terminators.len()
        );
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
        // If allow_gaps is false, add a special terminator for noncode tokens.
        let mut all_terminators: Vec<GrammarId> = filtered_local
            .into_iter()
            .chain(filtered_terminators)
            .collect();

        if !inst.flags.allow_gaps() {
            // GrammarId::NONCODE is a sentinel for noncode termination.
            all_terminators.push(GrammarId::NONCODE);
        }

        log::debug!(
            "Delimited[table]: After filtering: {} terminators (min_delimiters={})",
            all_terminators.len(),
            min_delimiters
        );

        // Calculate max_idx with terminators
        // Convert GrammarInst ParseMode to Grammar ParseMode
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

        // Prune element options based on current token
        let pruned_elements = self.prune_options_table_driven(&element_ids);
        log::debug!(
            "Delimited[table]: Pruned elements from {} to {} options",
            element_ids.len(),
            pruned_elements.len()
        );

        // If all elements were pruned, we can't match anything
        if pruned_elements.is_empty() {
            log::debug!("Delimited[table]: All elements pruned, returning empty");
            frame.end_pos = Some(start_pos);
            frame.state = FrameState::Combining;
            frame.context = FrameContext::DelimitedTableDriven {
                grammar_id,
                delimiter_count: 0,
                matched_idx: start_pos,
                working_idx: start_pos,
                max_idx,
                state: DelimitedState::MatchingElement,
                last_child_frame_id: None,
                delimiter_match: None,
                pos_before_delimiter: None,
                element_children: vec![],
            };
            stack.push(&mut frame);
            return Ok(TableFrameResult::Done);
        }

        // Store context
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
            element_children: pruned_elements.clone(),
        };

        frame.state = FrameState::WaitingForChild {
            child_index: 0,
            total_children: pruned_elements.len(),
        };

        // Create OneOf child with all element options
        // TODO: Create proper OneOf with all elements (not just first)
        let first_element = pruned_elements[0];
        let child_frame = TableParseFrame::new_child(
            stack.frame_id_counter,
            first_element,
            start_pos,
            all_terminators.clone(), // Use filtered terminators!
            Some(max_idx),
        );

        log::debug!(
            "Delimited[table]: Trying first element grammar_id={} with {} terminators",
            first_element.0,
            all_terminators.len()
        );

        stack.increment_frame_id_counter();
        stack.push(&mut frame);
        stack.push(&mut child_frame.clone());

        Ok(TableFrameResult::Done)
    }

    /// Handle Delimited WaitingForChild state using table-driven approach
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
            element_children,
            ..
        } = &mut frame.context
        else {
            unreachable!("Expected DelimitedTableDriven context");
        };

        // Get children: elements + delimiter
        let all_children: Vec<GrammarId> = ctx.children(*grammar_id).collect();
        if all_children.len() < 2 {
            log::debug!("Delimited[table]: Not enough children (need elements + delimiter)");
            panic!();
        }

        // Get configuration from aux_data
        let (delimiter_child_idx, _) = ctx.delimited_config(*grammar_id);
        let delimiter_id = all_children[delimiter_child_idx];

        log::debug!(
            "Delimited[table] WaitingForChild: frame_id={}, child_empty={}, state={:?}, delim_count={}",
            frame.frame_id,
            child_node.is_empty(),
            delim_state,
            delimiter_count
        );

        match delim_state {
            DelimitedState::MatchingElement => {
                if !child_node.is_empty() {
                    // Element matched
                    frame.accumulated.push(child_node.clone());
                    *matched_idx = *child_end_pos;
                    *working_idx = *child_end_pos;

                    // If child consumed past current max_idx, update max_idx to allow
                    // transparent token collection and subsequent children to continue
                    // from the correct position. This handles cases where a child
                    // (like Bracketed) legitimately consumed past the terminator-based
                    // max_idx constraint.
                    if *matched_idx > *max_idx {
                        log::debug!(
                            "Delimited[table]: Child consumed past max_idx ({}->{}), updating max_idx to matched_idx",
                            *max_idx, *matched_idx
                        );
                        *max_idx = *matched_idx;
                    }

                    // Try to match delimiter next
                    *delim_state = DelimitedState::MatchingDelimiter;
                    self.pos = *working_idx;

                    // Get the grammar instruction to check allow_gaps
                    let inst = ctx.inst(*grammar_id);

                    // If allow_gaps is set, skip whitespace BEFORE trying to match delimiter
                    // This matches Python's behavior where skip_start_index_forward_to_code
                    // is called at the START of each loop iteration, before matching
                    // either content OR delimiter.
                    if inst.flags.allow_gaps() {
                        let next_code_pos =
                            self.skip_start_index_forward_to_code(*working_idx, *max_idx);
                        // Collect whitespace/newlines between element and delimiter
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

                    // Store the current max_idx value before the borrow ends
                    let current_max_idx = *max_idx;

                    let delimiter_frame = TableParseFrame::new_child(
                        stack.frame_id_counter,
                        delimiter_id,
                        *working_idx,
                        frame.table_terminators.clone(),
                        Some(current_max_idx),
                    );

                    frame.state = FrameState::WaitingForChild {
                        child_index: 0,
                        total_children: 1,
                    };

                    // Push parent and delimiter child while updating parent's last_child_frame_id
                    TableParseFrame::push_child_and_update_parent(
                        stack,
                        &mut frame,
                        delimiter_frame,
                        "Delimited",
                    );
                    return Ok(TableFrameResult::Done);
                } else {
                    // Element failed - try other element candidates if available
                    let (child_index, total_children) = match frame.state {
                        FrameState::WaitingForChild {
                            child_index,
                            total_children,
                        } => (child_index, total_children),
                        _ => unreachable!("Expected WaitingForChild state in DelimitedTableDriven"),
                    };

                    if child_index + 1 < total_children {
                        let next_idx = child_index + 1;
                        let next_gid = element_children[next_idx];

                        log::debug!(
                            "Delimited[table]: Element candidate {} failed, trying next candidate idx={} gid={}",
                            child_index,
                            next_idx,
                            next_gid.0
                        );

                        let next_child = TableParseFrame::new_child(
                            stack.frame_id_counter,
                            next_gid,
                            *working_idx,
                            frame.table_terminators.clone(),
                            Some(*max_idx),
                        );

                        frame.state = FrameState::WaitingForChild {
                            child_index: next_idx,
                            total_children,
                        };

                        TableParseFrame::push_child_and_update_parent(
                            stack,
                            &mut frame,
                            next_child,
                            "Delimited",
                        );

                        return Ok(TableFrameResult::Done);
                    }

                    // No more candidates: finalize
                    log::debug!("Delimited[table]: Element failed, finalizing");
                    frame.end_pos = Some(*matched_idx);
                    frame.state = FrameState::Combining;
                    stack.push(&mut frame);
                    return Ok(TableFrameResult::Done);
                }
            }
            DelimitedState::MatchingDelimiter => {
                if !child_node.is_empty() {
                    // Delimiter matched
                    frame.accumulated.push(child_node.clone());
                    *delimiter_count += 1;
                    *matched_idx = *child_end_pos;
                    *working_idx = *child_end_pos;

                    // If child consumed past current max_idx, update max_idx
                    if *matched_idx > *max_idx {
                        log::debug!(
                            "Delimited[table]: Delimiter consumed past max_idx ({}->{}), updating max_idx to matched_idx",
                            *max_idx, *matched_idx
                        );
                        *max_idx = *matched_idx;
                    }

                    // Try to match next element
                    *delim_state = DelimitedState::MatchingElement;
                    self.pos = *working_idx;

                    // Get the grammar instruction to check allow_gaps
                    let inst = ctx.inst(*grammar_id);

                    // If allow_gaps is set, skip whitespace and collect transparent tokens
                    // between the delimiter and the next element (Python parity)
                    if inst.flags.allow_gaps() {
                        let next_code_pos =
                            self.skip_start_index_forward_to_code(*working_idx, *max_idx);
                        // Collect whitespace/newlines between delimiter and next element
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

                    // Get configuration to rebuild element_ids
                    let (delimiter_child_idx, _) = ctx.delimited_config(*grammar_id);

                    // Rebuild element_ids from all_children (excluding delimiter)
                    let original_element_ids: Vec<GrammarId> = all_children
                        .iter()
                        .enumerate()
                        .filter_map(|(i, &gid)| {
                            if i != delimiter_child_idx {
                                Some(gid)
                            } else {
                                None
                            }
                        })
                        .collect();

                    // Re-prune at the new position
                    let repruned_elements = self.prune_options_table_driven(&original_element_ids);
                    log::debug!(
                        "Delimited[table]: After delimiter, re-pruned elements from {} to {}",
                        original_element_ids.len(),
                        repruned_elements.len()
                    );

                    // If all elements pruned, finalize (successful if we have delimiters)
                    if repruned_elements.is_empty() {
                        log::debug!(
                            "Delimited[table]: All elements pruned after delimiter, finalizing"
                        );
                        frame.end_pos = Some(*matched_idx);
                        frame.state = FrameState::Combining;
                        stack.push(&mut frame);
                        return Ok(TableFrameResult::Done);
                    }

                    // Update element_children in context
                    *element_children = repruned_elements.clone();

                    // Store current max_idx value for child frame creation
                    let current_max_idx = *max_idx;

                    // After a delimiter matched, try the first element candidate again
                    let first_element = repruned_elements[0];
                    let element_frame = TableParseFrame::new_child(
                        stack.frame_id_counter,
                        first_element,
                        *working_idx,
                        frame.table_terminators.clone(),
                        Some(current_max_idx),
                    );

                    frame.state = FrameState::WaitingForChild {
                        child_index: 0,
                        total_children: repruned_elements.len(),
                    };

                    // Push parent and element child while updating parent's last_child_frame_id
                    TableParseFrame::push_child_and_update_parent(
                        stack,
                        &mut frame,
                        element_frame,
                        "Delimited",
                    );
                    return Ok(TableFrameResult::Done);
                } else {
                    // Delimiter failed - finalize (successful if we have min_delimiters)
                    log::debug!("Delimited[table]: Delimiter failed, finalizing");
                    frame.end_pos = Some(*matched_idx);
                    frame.state = FrameState::Combining;
                    stack.push(&mut frame);
                    return Ok(TableFrameResult::Done);
                }
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
