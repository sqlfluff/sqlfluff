use crate::{
    parser::{FrameContext, FrameState, Grammar, Node, ParseFrame, Parser},
    ParseMode,
};

impl<'a> Parser<'_> {
    /// Handle Sequence grammar Initial state in iterative parser
    /// Returns true if caller should continue main loop
    pub(crate) fn handle_sequence_initial(
        &mut self,
        elements: &[Grammar],
        optional: bool,
        seq_terminators: &[Grammar],
        reset_terminators: bool,
        allow_gaps: bool,
        parse_mode: ParseMode,
        frame: ParseFrame,
        parent_terminators: &[Grammar],
        stack: &mut Vec<ParseFrame>,
        frame_id_counter: &mut usize,
        results: &mut std::collections::HashMap<usize, (Node, usize, Option<u64>)>,
    ) -> bool {
        let pos = frame.pos;
        log::debug!("DEBUG: Sequence Initial at pos={}, parent_max_idx={:?}, allow_gaps={}, elements.len()={}",
                  pos, frame.parent_max_idx, allow_gaps, elements.len());
        let start_idx = pos; // Where did we start

        // Combine parent and local terminators
        let all_terminators: Vec<Grammar> = if reset_terminators {
            seq_terminators.to_vec()
        } else {
            seq_terminators
                .iter()
                .cloned()
                .chain(parent_terminators.iter().cloned())
                .collect()
        };

        // Calculate max_idx for GREEDY mode
        // What is the limit
        self.pos = start_idx;
        let max_idx = if parse_mode == ParseMode::Greedy {
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
        let mut frame = frame;
        frame.state = FrameState::WaitingForChild {
            child_index: 0,
            total_children: elements.len(),
        };
        frame.context = FrameContext::Sequence {
            elements: elements.to_vec(),
            allow_gaps,
            optional,
            parse_mode,
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
        let first_child_pos = if allow_gaps {
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

                if parse_mode == ParseMode::Strict {
                    // In strict mode, return Empty
                    results.insert(current_frame_id, (Node::Empty, start_idx, None));
                    return false; // Don't continue, we stored a result
                }
                // In greedy modes, check if first element is optional
                if elements[0].is_optional() {
                    // First element is optional, can skip
                    results.insert(current_frame_id, (Node::Empty, start_idx, None));
                    return false;
                } else {
                    // Required element, no segments - this is unparsable in greedy mode
                    results.insert(current_frame_id, (Node::Empty, start_idx, None));
                    return false;
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
                                    Node::Whitespace(_, _) | Node::Newline(_, _) => {
                                        insert_pos -= 1;
                                    }
                                    _ => break,
                                }
                            }
                            parent_frame
                                .accumulated
                                .insert(insert_pos, Node::Meta(meta_type));
                        } else {
                            parent_frame.accumulated.push(Node::Meta(meta_type));
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
                    let current_max_idx = if let Some(parent_frame) = stack.last() {
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
                                    Node::Sequence(std::mem::take(&mut parent_frame.accumulated));
                                results.insert(current_frame_id, (seq_node, first_child_pos, None));
                            }
                            return false;
                        }
                    }

                    let child_frame = ParseFrame {
                        frame_id: *frame_id_counter,
                        grammar: elements[child_idx].clone(),
                        pos: first_child_pos, // Use position after skipping to code!
                        terminators: stack
                            .last()
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
                        frame_id_counter,
                        child_idx,
                    );
                    return true; // Continue to process the child we just pushed
                }
            }
        }

        false // No child pushed, don't continue
    }
}
