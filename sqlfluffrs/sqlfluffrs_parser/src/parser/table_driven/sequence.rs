use sqlfluffrs_types::{GrammarId, GrammarInstExt, ParseMode};

use crate::parser::{
    table_driven::frame::{TableFrameResult, TableParseFrame, TableParseFrameStack},
    FrameContext, FrameState, Node, ParseError, Parser,
};

impl<'a> Parser<'_> {
    // ========================================================================
    // Table-Driven Sequence Handlers
    // ========================================================================

    /// Handle Sequence Initial state using table-driven approach
    pub(crate) fn handle_sequence_table_driven_initial(
        &mut self,
        mut frame: TableParseFrame,
        parent_terminators: &[GrammarId],
        stack: &mut TableParseFrameStack,
    ) -> Result<TableFrameResult, ParseError> {
        self.pos = frame.pos;
        let start_idx = self.pos;
        let ctx = self.grammar_ctx.expect("Grammar Context");
        let grammar_id = frame.grammar_id;
        let grammar_inst = ctx.inst(grammar_id);
        let local_terminators = ctx.terminators(grammar_id).collect::<Vec<_>>();
        let reset_terminators = grammar_inst.flags.reset_terminators();
        let parse_mode = grammar_inst.parse_mode;
        let elements = ctx.children(grammar_id).collect::<Vec<_>>();

        // combine parent and local terminators
        let all_terminators = self.combine_table_terminators(
            &local_terminators,
            parent_terminators,
            reset_terminators,
        );

        // calculate max_idx with terminator and parent constraints
        let max_idx = self.calculate_max_idx_table_driven(
            start_idx,
            &all_terminators,
            parse_mode,
            frame.parent_max_idx,
        );

        // Push a collection checkpoint for this sequence
        // This allows us to rollback transparent token collections if we backtrack
        // TODO: Do we still need this?
        self.push_collection_checkpoint(frame.frame_id);

        // Update frame with Sequence context
        frame.state = FrameState::WaitingForChild {
            child_index: 0,
            total_children: elements.len(),
        };
        frame.context = FrameContext::SequenceTableDriven {
            grammar_id,
            matched_idx: start_idx,
            tentatively_collected: vec![],
            max_idx,
            original_max_idx: max_idx, // Store original before any GREEDY_ONCE_STARTED trimming
            last_child_frame_id: None,
            current_element_idx: 0,                  // Start at first element
            first_match: true,                       // For GREEDY_ONCE_STARTED trimming
            optional: grammar_inst.flags.optional(), // Store Sequence-level optional flag
        };
        frame.table_terminators = all_terminators;
        let current_frame_id = frame.frame_id; // Save before moving frame
        stack.push(&mut frame);

        // Don't skip whitespace here! Python's Sequence.match skips whitespace IN THE LOOP
        let first_child_pos = start_idx; // Start at the original position

        // Handle empty elements case - sequence with no elements should succeed immediately
        if elements.is_empty() {
            // Pop the frame we just pushed
            stack.pop();
            // Transition to Combining to finalize empty Sequence result
            frame.end_pos = Some(start_idx);
            frame.state = FrameState::Combining;
            stack.push(&mut frame);
            return Ok(TableFrameResult::Done);
        }

        if first_child_pos >= max_idx {
            stack.pop();
            self.rollback_collection_checkpoint(current_frame_id);

            if parse_mode == ParseMode::Strict {
                stack
                    .results
                    .insert(current_frame_id, (Node::Empty, start_idx, None));
                return Ok(TableFrameResult::Done);
            }

            // In greedy modes, check if first element is optional
            if ctx.is_optional(elements[0]) {
                stack
                    .results
                    .insert(current_frame_id, (Node::Empty, start_idx, None));
                return Ok(TableFrameResult::Done);
            } else {
                // Wrap remaining content as an Unparsable node (table-driven variant)
                let element_desc = format!("GrammarId({})", elements[0]);
                let unparsable_children: Vec<Node> = (start_idx..max_idx)
                    .filter_map(|pos| {
                        if pos < self.tokens.len() {
                            let tok = &self.tokens[pos];
                            Some(Node::Token {
                                token_type: tok.get_type(),
                                raw: tok.raw().to_string(),
                                token_idx: pos,
                            })
                        } else {
                            None
                        }
                    })
                    .collect();

                let unparsable_node = Node::Unparsable {
                    children: unparsable_children,
                    expected_message: element_desc,
                };

                stack
                    .results
                    .insert(current_frame_id, (unparsable_node, max_idx, None));
                return Ok(TableFrameResult::Done);
            }
        }

        let mut child_idx = 0;
        while child_idx < elements.len() {
            if ctx.variant(elements[child_idx]) == sqlfluffrs_types::GrammarVariant::Meta {
                // Meta doesn't need parsing - just add to accumulated
                if let Some(ref mut parent_frame) = stack.last_mut() {
                    if ctx.segment_type(elements[child_idx]).expect("meta type") == "indent" {
                        // Indent goes before whitespace
                        let mut insert_pos = parent_frame.accumulated.len();
                        while insert_pos > 0 {
                            match &parent_frame.accumulated[insert_pos - 1] {
                                Node::Whitespace { .. } | Node::Newline { .. } => {
                                    insert_pos -= 1;
                                }
                                _ => break,
                            }
                        }
                        parent_frame.accumulated.insert(
                            insert_pos,
                            Node::Meta {
                                token_type: "indent".to_string(),
                                token_idx: None,
                            },
                        );
                    } else {
                        parent_frame.accumulated.push(Node::Meta {
                            token_type: ctx
                                .segment_type(elements[child_idx])
                                .expect("meta type")
                                .to_string(),
                            token_idx: None,
                        });
                    }

                    // Update state to next child
                    if let FrameState::WaitingForChild {
                        child_index,
                        total_children: _,
                    } = &mut parent_frame.state
                    {
                        *child_index = child_idx + 1;
                    }
                }
                child_idx += 1;
            } else {
                // Get max_idx from parent Sequence to pass to child
                let current_max_idx = if let Some(parent_frame) = stack.last_mut() {
                    if let FrameContext::SequenceTableDriven { max_idx, .. } = &parent_frame.context
                    {
                        Some(*max_idx)
                    } else {
                        None
                    }
                } else {
                    None
                };

                // Non-meta element - needs actual parsing
                log::debug!(
                    "DEBUG: Creating FIRST child at pos={}, max_idx={}",
                    first_child_pos,
                    max_idx
                );

                let child_frame = TableParseFrame {
                    frame_id: stack.frame_id_counter,
                    grammar_id: elements[child_idx],
                    pos: first_child_pos, // Use position after skipping to code!
                    table_terminators: stack
                        .last_mut()
                        .map(|f| f.table_terminators.clone())
                        .unwrap_or_default(),
                    state: FrameState::Initial,
                    accumulated: vec![],
                    context: FrameContext::None,
                    parent_max_idx: current_max_idx, // Pass Sequence's max_idx to child!
                    end_pos: None,
                    transparent_positions: None,
                    element_key: None,
                };

                // Update parent (already on stack) and push child
                TableParseFrame::update_sequence_parent_and_push_child(
                    stack,
                    child_frame,
                    child_idx,
                );
                return Ok(TableFrameResult::Done);
            }
        }

        Ok(TableFrameResult::Done)
    }

    /// Handle Sequence grammar Waiting for child state
    /// child_node,
    /// child_end_pos,
    /// child_element_key,
    /// stack,
    pub(crate) fn handle_sequence_table_driven_waiting_for_child(
        &mut self,
        mut frame: TableParseFrame,
        child_node: &Node,
        child_end_pos: &usize,
        child_element_key: &Option<u64>,
        stack: &mut TableParseFrameStack,
    ) -> Result<TableFrameResult, ParseError> {
        let ctx = self.grammar_ctx.expect("Grammar Context");

        // Extract grammar id and instance for table-driven logic
        let grammar_id = match &frame.context {
            FrameContext::SequenceTableDriven { grammar_id, .. } => *grammar_id,
            _ => unreachable!("Expected SequenceTableDriven context"),
        };

        let inst = ctx.inst(grammar_id);
        let all_children: Vec<GrammarId> = ctx.children(grammar_id).collect();

        // Read current index and first_match for logging (immutable borrow)
        let (current_element_idx_val, first_match_val) = match &frame.context {
            FrameContext::SequenceTableDriven {
                current_element_idx,
                first_match,
                ..
            } => (*current_element_idx, *first_match),
            _ => unreachable!("Expected SequenceTableDriven context"),
        };

        log::debug!(
            "Sequence[table] WaitingForChild: frame_id={}, child_empty={}, child_end_pos={}, current_idx={}/{}, first_match={}",
            frame.frame_id,
            child_node.is_empty(),
            child_end_pos,
            current_element_idx_val,
            all_children.len(),
            first_match_val
        );

        // Child matched
        if !child_node.is_empty() {
            frame.accumulated.push(child_node.clone());

            if let FrameContext::SequenceTableDriven {
                matched_idx,
                max_idx,
                current_element_idx,
                first_match,
                original_max_idx,
                ..
            } = &mut frame.context
            {
                *matched_idx = *child_end_pos;
                *current_element_idx += 1;
                if *first_match && inst.parse_mode == ParseMode::GreedyOnceStarted {
                    *first_match = false;
                    // Use element-aware trimming so we don't treat terminators that are
                    // actually the start of upcoming elements (e.g., FROM) as terminators.
                    let remaining_children: Vec<GrammarId> = all_children
                        .iter()
                        .skip(*current_element_idx)
                        .cloned()
                        .collect();

                    let new_max_idx = self.trim_to_terminator_with_elements_table_driven(
                        *matched_idx,
                        &frame.table_terminators,
                        &remaining_children,
                    );
                    // Respect original parent max constraint
                    *max_idx = new_max_idx.min(*original_max_idx);
                    log::debug!("Sequence[table]: Trimmed max_idx to {}", *max_idx);
                }
            }

            let (matched_idx_val, max_idx_val, current_element_idx_val) = match &frame.context {
                FrameContext::SequenceTableDriven {
                    matched_idx,
                    max_idx,
                    current_element_idx,
                    ..
                } => (*matched_idx, *max_idx, *current_element_idx),
                _ => unreachable!("Expected SequenceTableDriven context"),
            };

            if current_element_idx_val < all_children.len() {
                // Move parser position to where the child ended
                self.pos = matched_idx_val;

                // When gaps are allowed, skip forward to the next code token before
                // attempting to parse the next element (Python parity).
                // Also collect any transparent tokens between the child end and
                // the next code token into the accumulated list (tentatively).
                let next_start_pos = if inst.flags.allow_gaps() {
                    let ns = self.skip_start_index_forward_to_code(matched_idx_val, max_idx_val);
                    // collect transparent tokens between matched_idx and ns into accumulated
                    if ns > matched_idx_val {
                        if let FrameContext::SequenceTableDriven {
                            tentatively_collected,
                            ..
                        } = &mut frame.context
                        {
                            self.table_collect_transparent_between_into_accum(
                                &mut frame.accumulated,
                                tentatively_collected,
                                frame.frame_id,
                                matched_idx_val,
                                ns,
                            );
                        }
                    }
                    ns
                } else {
                    matched_idx_val
                };

                let next_child = all_children[current_element_idx_val];

                // Pass the current (possibly trimmed) max_idx to child frames.
                // For GREEDY_ONCE_STARTED, max_idx is trimmed after the first match,
                // and subsequent children MUST respect this trimmed boundary to prevent
                // parsing past terminators (e.g., FROM being parsed as an alias).
                let child_parent_max = Some(max_idx_val);

                // Debug: log token at matched_idx and at next_start_pos to diagnose why
                // parsing doesn't advance beyond this point in table-driven mode.
                if next_start_pos < self.tokens.len() {
                    let tok = &self.tokens[next_start_pos];
                    log::debug!(
                        "Sequence[table] about to push child {} at pos {} (token='{}', type='{}')",
                        next_child,
                        next_start_pos,
                        tok.raw(),
                        tok.get_type()
                    );
                } else {
                    log::debug!(
                        "Sequence[table] about to push child {} at pos {} (EOF)",
                        next_child,
                        next_start_pos
                    );
                }

                let child_frame = TableParseFrame::new_child(
                    stack.frame_id_counter,
                    next_child,
                    next_start_pos,
                    frame.table_terminators.clone(),
                    child_parent_max,
                );

                frame.state = FrameState::WaitingForChild {
                    child_index: current_element_idx_val,
                    total_children: all_children.len(),
                };

                TableParseFrame::push_sequence_child_and_update_parent(
                    stack,
                    &mut frame,
                    child_frame,
                    current_element_idx_val,
                );
                return Ok(TableFrameResult::Done);
            } else {
                self.pos = matched_idx_val;
                frame.end_pos = Some(matched_idx_val);
                frame.state = FrameState::Combining;
                stack.push(&mut frame);
                return Ok(TableFrameResult::Done);
            }
        }

        // Child failed (Empty)
        let failed_idx = current_element_idx_val;
        let failed_child = all_children[failed_idx];
        let failed_inst = ctx.inst(failed_child);

        // Determine element_start (where this element began) from frame context
        let element_start = match &frame.context {
            FrameContext::SequenceTableDriven { matched_idx, .. } => *matched_idx,
            _ => frame.pos,
        };

        // If child returned Empty but advanced the parser (child_end_pos != element_start),
        // correct the live parser position to respect the Empty contract.
        let corrected_child_end_pos = if *child_end_pos != element_start {
            log::debug!(
                "[SEQUENCE TABLE FIX] Child returned Empty but child_end_pos={} > element_start={}. Correcting and resetting self.pos.",
                child_end_pos,
                element_start
            );
            element_start
        } else {
            *child_end_pos
        };

        if self.pos != corrected_child_end_pos {
            log::debug!(
                "[SEQUENCE TABLE FIX] frame_id={} resetting self.pos {} -> {}",
                frame.frame_id,
                self.pos,
                corrected_child_end_pos
            );
            self.pos = corrected_child_end_pos;
        }

        if failed_inst.flags.optional() {
            let next_index = failed_idx + 1;
            if next_index < all_children.len() {
                // Determine a sensible start position for the next child.
                // Use the sequence's matched_idx (last successful match) as the base
                // so we don't accidentally start at an earlier frame.pos that doesn't
                // reflect the position after previous successful children.
                let (base_matched_idx, base_max_idx) = match &frame.context {
                    FrameContext::SequenceTableDriven {
                        matched_idx,
                        max_idx,
                        ..
                    } => (*matched_idx, *max_idx),
                    _ => (frame.pos, frame.pos),
                };

                // Respect allow_gaps: if allowed, advance to next code token and
                // collect transparent tokens between base_matched_idx and that pos.
                let next_start_pos = if inst.flags.allow_gaps() {
                    let ns = self.skip_start_index_forward_to_code(base_matched_idx, base_max_idx);
                    if ns > base_matched_idx {
                        if let FrameContext::SequenceTableDriven {
                            tentatively_collected,
                            ..
                        } = &mut frame.context
                        {
                            self.table_collect_transparent_between_into_accum(
                                &mut frame.accumulated,
                                tentatively_collected,
                                frame.frame_id,
                                base_matched_idx,
                                ns,
                            );
                        }
                    }
                    ns
                } else {
                    base_matched_idx
                };

                let next_child = all_children[next_index];
                let child_frame = TableParseFrame::new_child(
                    stack.frame_id_counter,
                    next_child,
                    next_start_pos,
                    frame.table_terminators.clone(),
                    match &frame.context {
                        FrameContext::SequenceTableDriven { max_idx, .. } => Some(*max_idx),
                        _ => None,
                    },
                );

                frame.state = FrameState::WaitingForChild {
                    child_index: next_index,
                    total_children: all_children.len(),
                };

                TableParseFrame::push_sequence_child_and_update_parent(
                    stack,
                    &mut frame,
                    child_frame,
                    next_index,
                );

                return Ok(TableFrameResult::Done);
            } else {
                // Child failure at end of sequence: ensure parser position is restored
                // to the sequence's starting position before completing with Empty.
                self.pos = frame.pos;
                self.rollback_collection_checkpoint(frame.frame_id);
                frame.end_pos = Some(frame.pos);
                frame.state = FrameState::Combining;
                stack.push(&mut frame);
                return Ok(TableFrameResult::Done);
            }
        } else {
            // Required child failed: restore parser position to sequence start
            self.pos = frame.pos;
            self.rollback_collection_checkpoint(frame.frame_id);

            // CRITICAL FIX: When a required element fails, the Sequence must fail completely.
            // This is true regardless of whether the Sequence itself is optional.
            // - If Sequence is optional, the parent handles the Empty appropriately.
            // - If Sequence is not optional, this is a parse error that propagates up.
            // In both cases, we should NOT go to Combining state with partial results,
            // as that would incorrectly return a partial Sequence node.
            log::debug!(
                "Sequence[table]: Required element {} returned Empty - Sequence fails completely",
                failed_idx
            );
            stack
                .results
                .insert(frame.frame_id, (Node::Empty, frame.pos, None));
            return Ok(TableFrameResult::Done);
        }
    }

    /// Handle Sequence Combining state using table-driven approach
    pub(crate) fn handle_sequence_table_driven_combining(
        &mut self,
        mut frame: TableParseFrame,
        stack: &mut TableParseFrameStack,
    ) -> Result<TableFrameResult, ParseError> {
        let FrameContext::SequenceTableDriven {
            tentatively_collected,
            matched_idx,
            ..
        } = &frame.context
        else {
            return Err(ParseError::new(
                "Expected SequenceTableDriven context in combining".to_string(),
            ));
        };

        log::debug!(
            "Sequence[table] Combining: frame_id={}, accumulated={}, matched_idx={}",
            frame.frame_id,
            frame.accumulated.len(),
            matched_idx
        );

        let (result_node, final_pos) = if frame.accumulated.is_empty() {
            self.rollback_collection_checkpoint(frame.frame_id);
            (Node::Empty, frame.pos)
        } else {
            self.commit_collection_checkpoint(frame.frame_id);
            (
                Node::Sequence {
                    children: frame.accumulated.clone(),
                },
                *matched_idx,
            )
        };

        stack
            .transparent_positions
            .insert(frame.frame_id, tentatively_collected.clone());

        self.pos = final_pos;
        frame.end_pos = Some(final_pos);
        frame.state = FrameState::Complete(result_node);

        Ok(TableFrameResult::Push(frame))
    }

    /// Helper: Collect transparent tokens between two positions (from .. to), used when allow_gaps==true.
    fn table_collect_transparent_between_into_accum(
        &mut self,
        accumulated: &mut Vec<Node>,
        tentatively_collected: &mut Vec<usize>,
        frame_id: usize,
        from: usize,
        to: usize,
    ) {
        for collect_pos in from..to {
            if collect_pos < self.tokens.len() && !self.tokens[collect_pos].is_code() {
                let tok = &self.tokens[collect_pos];
                let tok_type = tok.get_type();
                // Only check if already in THIS frame's accumulated to avoid duplicating within the same frame
                let already_in_frame = accumulated.iter().any(|node| match node {
                    Node::Whitespace { token_idx: pos, .. }
                    | Node::Newline { token_idx: pos, .. }
                    | Node::EndOfFile { token_idx: pos, .. } => *pos == collect_pos,
                    _ => false,
                });
                if !already_in_frame {
                    match &*tok_type {
                        "whitespace" => {
                            log::debug!(
                                "COLLECTING whitespace at {}: {:?}",
                                collect_pos,
                                tok.raw()
                            );
                            accumulated.push(Node::Whitespace {
                                raw: tok.raw().to_string(),
                                token_idx: collect_pos,
                            });
                            tentatively_collected.push(collect_pos);
                        }
                        "newline" => {
                            log::debug!("COLLECTING newline at {}: {:?}", collect_pos, tok.raw());
                            accumulated.push(Node::Newline {
                                raw: tok.raw().to_string(),
                                token_idx: collect_pos,
                            });
                            tentatively_collected.push(collect_pos);
                        }
                        "end_of_file" => {
                            log::debug!("COLLECTING EOF at {}: {:?}", collect_pos, tok.raw());
                            accumulated.push(Node::EndOfFile {
                                raw: tok.raw().to_string(),
                                token_idx: collect_pos,
                            });
                            tentatively_collected.push(collect_pos);
                        }
                        _ => {}
                    }
                }
            }
        }
    }
}
