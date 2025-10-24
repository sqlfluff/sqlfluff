use crate::{
    parser::{
        iterative::{NextStep, ParseFrameStack}, BracketedState, FrameContext, FrameState, Grammar, Node, ParseError, ParseFrame, Parser
    },
    ParseMode,
};

impl<'a> Parser<'_> {
    /// Handle Sequence grammar Initial state in iterative parser
    /// Returns true if caller should continue main loop
    pub(crate) fn handle_sequence_initial(
        &mut self,
        grammar: &Grammar,
        frame: &mut ParseFrame,
        parent_terminators: &[Grammar],
        stack: &mut ParseFrameStack,
    ) -> Result<NextStep, ParseError> {
        // Destructure Grammar::Sequence fields
        let (elements, optional, seq_terminators, reset_terminators, allow_gaps, parse_mode) = match grammar {
            Grammar::Sequence {
                elements,
                optional,
                terminators: seq_terminators,
                reset_terminators,
                allow_gaps,
                parse_mode,
                ..
            } => (elements, optional, seq_terminators, reset_terminators, allow_gaps, parse_mode),
            _ => panic!("handle_sequence_initial called with non-Sequence grammar"),
        };
        let pos = frame.pos;
        log::debug!("DEBUG: Sequence Initial at pos={}, parent_max_idx={:?}, allow_gaps={}, elements.len()={}",
                  pos, frame.parent_max_idx, allow_gaps, elements.len());
        let start_idx = pos; // Where did we start

        // Combine parent and local terminators
        let all_terminators: Vec<Grammar> = if *reset_terminators {
            seq_terminators.to_vec()
        } else {
            seq_terminators
                .iter()
                .cloned()
                .chain(parent_terminators.iter().cloned())
                .collect()
        };

        // Calculate max_idx for GREEDY mode
        self.pos = start_idx;
        let max_idx = if *parse_mode == ParseMode::Greedy {
            self.trim_to_terminator(start_idx, &all_terminators)
        } else {
            self.tokens.len()
        };

        // Apply parent's max_idx limit (simulates Python's segments[:max_idx])
        let max_idx = if let Some(parent_limit) = frame.parent_max_idx {
            max_idx.min(parent_limit)
        } else {
            max_idx
        };

        // Update frame with Sequence context
        frame.state = FrameState::WaitingForChild {
            child_index: 0,
            total_children: elements.len(),
        };
        frame.context = FrameContext::Sequence {
            elements: elements.to_vec(),
            allow_gaps: *allow_gaps,
            optional: *optional,
            parse_mode: *parse_mode,
            matched_idx: start_idx,
            tentatively_collected: vec![],
            max_idx,
            original_max_idx: max_idx, // Store original before any GREEDY_ONCE_STARTED trimming
            last_child_frame_id: None,
            current_element_idx: 0, // Start at first element
            first_match: true,      // For GREEDY_ONCE_STARTED trimming
        };
        frame.terminators = all_terminators;
        let current_frame_id = frame.frame_id; // Save before moving frame
        stack.push(frame);

        // Skip to code if allow_gaps (matching Python's behavior at sequence.py line 196)
        let first_child_pos = if *allow_gaps {
            self.skip_start_index_forward_to_code(start_idx, max_idx)
        } else {
            start_idx
        };

        // Push first child to parse
        if !elements.is_empty() {
            // Check if we've run out of segments before first element
            if first_child_pos >= max_idx {
                // Haven't matched anything yet and already at limit
                // Pop the frame we just pushed since we're returning early
                stack.pop();

                if *parse_mode == ParseMode::Strict {
                    // In strict mode, return Empty
                    stack
                        .results
                        .insert(current_frame_id, (Node::Empty, start_idx, None));
                    return Ok(NextStep::Fallthrough); // Don't continue, we stored a result
                }
                // In greedy modes, check if first element is optional
                if elements[0].is_optional() {
                    // First element is optional, can skip
                    stack
                        .results
                        .insert(current_frame_id, (Node::Empty, start_idx, None));
                    return Ok(NextStep::Fallthrough);
                } else {
                    // Required element, no segments - this is unparsable in greedy mode
                    stack
                        .results
                        .insert(current_frame_id, (Node::Empty, start_idx, None));
                    return Ok(NextStep::Fallthrough);
                }
            }

            // Handle Meta elements specially
            let mut child_idx = 0;
            while child_idx < elements.len() {
                if let Grammar::Meta(meta_type) = &elements[child_idx] {
                    // Meta doesn't need parsing - just add to accumulated
                    if let Some(ref mut parent_frame) = stack.last_mut() {
                        if *meta_type == "indent" {
                            // Indent goes before whitespace
                            let mut insert_pos = parent_frame.accumulated.len();
                            while insert_pos > 0 {
                                match &parent_frame.accumulated[insert_pos - 1] {
                                    Node::Whitespace { raw: _, token_idx: _ } | Node::Newline { raw: _, token_idx: _ } => {
                                        insert_pos -= 1;
                                    }
                                    _ => break,
                                }
                            }
                            parent_frame
                                .accumulated
                                .insert(insert_pos, Node::Meta { token_type: meta_type, token_idx: None });
                        } else {
                            parent_frame.accumulated.push(Node::Meta { token_type: meta_type, token_idx: None });
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
                        if let FrameContext::Sequence { max_idx, .. } = &parent_frame.context {
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

                    // Optimization: Handle Nothing grammar inline without creating a frame
                    if matches!(elements[child_idx], Grammar::Nothing() | Grammar::Empty) {
                        log::debug!(
                            "Sequence: Element {} is Nothing, handling inline",
                            child_idx
                        );

                        // Nothing always returns Empty - just mark it as complete and move to next element
                        if let Some(ref mut parent_frame) = stack.last_mut() {
                            if let FrameContext::Sequence {
                                current_element_idx,
                                ..
                            } = &mut parent_frame.context
                            {
                                *current_element_idx += 1;
                            }
                        }

                        // Check if we need to process more elements
                        child_idx += 1;
                        if child_idx < elements.len() {
                            // More elements to process - continue with next element
                            continue;
                        } else {
                            // No more elements - sequence is complete
                            // Pop the parent frame to finalize
                            if let Some(mut parent_frame) = stack.pop() {
                                let seq_node =
                                    Node::Sequence { children: std::mem::take(&mut parent_frame.accumulated) };
                                stack
                                    .results
                                    .insert(current_frame_id, (seq_node, first_child_pos, None));
                            }
                            return Ok(NextStep::Fallthrough);
                        }
                    }

                    let child_frame = ParseFrame {
                        frame_id: stack.frame_id_counter,
                        grammar: elements[child_idx].clone(),
                        pos: first_child_pos, // Use position after skipping to code!
                        terminators: stack
                            .last_mut()
                            .map(|f| f.terminators.clone())
                            .unwrap_or_default(),
                        state: FrameState::Initial,
                        accumulated: vec![],
                        context: FrameContext::None,
                        parent_max_idx: current_max_idx, // Pass Sequence's max_idx to child!
                    };

                    // Update parent (already on stack) and push child
                    ParseFrame::update_sequence_parent_and_push_child(
                        stack,
                        child_frame,
                        child_idx,
                    );
                    return Ok(NextStep::Continue); // Continue to process the child we just pushed
                }
            }
        }

        Ok(NextStep::Fallthrough) // No child pushed, don't continue
    }

    /// Handle Bracketed grammar Initial state in iterative parser
    pub(crate) fn handle_bracketed_initial(
        &mut self,
        grammar: &Grammar,
        frame: &mut ParseFrame,
        parent_terminators: &[Grammar],
        stack: &mut ParseFrameStack,
    ) -> Result<NextStep, ParseError> {
        let (bracket_pairs, elements, optional, bracket_terminators, reset_terminators, allow_gaps, parse_mode) = match grammar {
            Grammar::Bracketed {
                bracket_pairs,
                elements,
                optional,
                terminators: bracket_terminators,
                reset_terminators,
                allow_gaps,
                parse_mode,
                ..
            } => (bracket_pairs, elements, optional, bracket_terminators, reset_terminators, allow_gaps, parse_mode),
            _ => {
                return Err(ParseError {
                    message: "handle_bracketed_initial called with non-Bracketed grammar".to_string(),
                });
            }
        };
        let start_idx = frame.pos;
        log::debug!(
            "Bracketed starting at {}, allow_gaps={}, parse_mode={:?}",
            start_idx,
            allow_gaps,
            parse_mode
        );

        // Combine parent and local terminators
        let all_terminators: Vec<Grammar> = if *reset_terminators {
            bracket_terminators.to_vec()
        } else {
            bracket_terminators
                .iter()
                .cloned()
                .chain(parent_terminators.iter().cloned())
                .collect()
        };

        // Update frame with Bracketed context
        frame.state = FrameState::WaitingForChild {
            child_index: 0,
            total_children: 3, // open, content, close
        };
        frame.context = FrameContext::Bracketed {
            bracket_pairs: bracket_pairs.clone(),
            elements: elements.to_vec(),
            allow_gaps: *allow_gaps,
            optional: *optional,
            parse_mode: *parse_mode,
            state: BracketedState::MatchingOpen,
            last_child_frame_id: None,
        };
        frame.terminators = all_terminators.clone();
        stack.push(frame);

        // Start by trying to match the opening bracket
        let mut child_frame = ParseFrame {
            frame_id: stack.frame_id_counter,
            grammar: (*bracket_pairs.0).clone(),
            pos: start_idx,
            terminators: all_terminators,
            state: FrameState::Initial,
            accumulated: vec![],
            context: FrameContext::None,
            parent_max_idx: stack.last_mut().unwrap().parent_max_idx, // Propagate parent's limit!
        };

        // Update parent's last_child_frame_id
        {
            let next_child_id = stack.frame_id_counter;
            if let Some(parent_frame) = stack.last_mut() {
                if let FrameContext::Bracketed {
                    last_child_frame_id,
                    ..
                } = &mut parent_frame.context
                {
                    *last_child_frame_id = Some(next_child_id);
                }
            }
        }

        stack.increment_frame_id_counter();
        stack.push(&mut child_frame);
        Ok(NextStep::Continue)
    }
}
