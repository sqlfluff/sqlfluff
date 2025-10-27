use std::sync::Arc;

use crate::{
    parser::{
        iterative::{NextStep, ParseFrameStack},
        BracketedState, FrameContext, FrameState, Grammar, Node, ParseError, ParseFrame, Parser,
    },
    ParseMode,
};

impl<'a> Parser<'_> {
    /// Handle Sequence grammar Initial state in iterative parser
    /// Returns true if caller should continue main loop
    pub(crate) fn handle_sequence_initial(
        &mut self,
        grammar: Arc<Grammar>,
        frame: &mut ParseFrame,
        parent_terminators: &[Arc<Grammar>],
        stack: &mut ParseFrameStack,
    ) -> Result<NextStep, ParseError> {
        // Destructure Grammar::Sequence fields
        let (elements, optional, seq_terminators, reset_terminators, allow_gaps, parse_mode) =
            match grammar.as_ref() {
                Grammar::Sequence {
                    elements,
                    optional,
                    terminators: seq_terminators,
                    reset_terminators,
                    allow_gaps,
                    parse_mode,
                    ..
                } => (
                    elements,
                    optional,
                    seq_terminators,
                    reset_terminators,
                    allow_gaps,
                    parse_mode,
                ),
                _ => panic!("handle_sequence_initial called with non-Sequence grammar"),
            };
        let pos = frame.pos;
        log::debug!("DEBUG: Sequence Initial at pos={}, parent_max_idx={:?}, allow_gaps={}, elements.len()={}",
                  pos, frame.parent_max_idx, allow_gaps, elements.len());
        let start_idx = pos; // Where did we start

        // Combine parent and local terminators
        let all_terminators: Vec<Arc<Grammar>> = if *reset_terminators {
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
            grammar: grammar.clone(),
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
                if let Grammar::Meta(meta_type) = &*elements[child_idx] {
                    // Meta doesn't need parsing - just add to accumulated
                    if let Some(ref mut parent_frame) = stack.last_mut() {
                        if *meta_type == "indent" {
                            // Indent goes before whitespace
                            let mut insert_pos = parent_frame.accumulated.len();
                            while insert_pos > 0 {
                                match &parent_frame.accumulated[insert_pos - 1] {
                                    Node::Whitespace {
                                        raw: _,
                                        token_idx: _,
                                    }
                                    | Node::Newline {
                                        raw: _,
                                        token_idx: _,
                                    } => {
                                        insert_pos -= 1;
                                    }
                                    _ => break,
                                }
                            }
                            parent_frame.accumulated.insert(
                                insert_pos,
                                Node::Meta {
                                    token_type: meta_type,
                                    token_idx: None,
                                },
                            );
                        } else {
                            parent_frame.accumulated.push(Node::Meta {
                                token_type: meta_type,
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
                    if matches!(
                        elements[child_idx].as_ref(),
                        Grammar::Nothing() | Grammar::Empty
                    ) {
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
                                let seq_node = Node::Sequence {
                                    children: std::mem::take(&mut parent_frame.accumulated),
                                };
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

    /// Handle Sequence grammar WaitingForChild state in iterative parser
    pub(crate) fn handle_sequence_waiting_for_child(
        &mut self,
        frame: &mut ParseFrame,
        child_node: &Node,
        child_end_pos: &usize,
        stack: &mut ParseFrameStack,
        iteration_count: usize,
        frame_terminators: Vec<Arc<Grammar>>,
    ) {
        let FrameContext::Sequence {
            grammar,
            matched_idx,
            tentatively_collected,
            max_idx,
            original_max_idx,
            last_child_frame_id: _last_child_frame_id,
            current_element_idx,
            first_match,
        } = &mut frame.context
        else {
            panic!("Expected FrameContext::Sequence in handle_sequence_waiting_for_child");
        };
        let Grammar::Sequence {
            elements,
            allow_gaps,
            parse_mode,
            simple_hint: _,
            ..
        } = grammar.as_ref()
        else {
            panic!("Expected Grammar::Sequence in FrameContext::Sequence");
        };
        let element_start = *matched_idx;

        if child_node.is_empty() {
            let current_element = &elements[*current_element_idx];
            if current_element.is_optional() {
                log::debug!("Sequence: child returned Empty and is optional, continuing");
            } else {
                let element_desc = match current_element.as_ref() {
                    Grammar::Ref { name, .. } => format!("Ref({})", name),
                    Grammar::StringParser { template, .. } => {
                        format!("StringParser('{}')", template)
                    }
                    _ => format!("{:?}", current_element),
                };
                let found_token = if element_start < self.tokens.len() {
                    let tok = &self.tokens[element_start];
                    format!("'{}' (type: {})", tok.raw(), tok.get_type())
                } else {
                    "EOF".to_string()
                };
                log::debug!("WARNING: Sequence failing - required element returned Empty!");
                log::debug!(
                    "  frame_id={}, element_idx={}/{}",
                    frame.frame_id,
                    *current_element_idx,
                    elements.len()
                );
                log::debug!("  Expected: {}", element_desc);
                log::debug!("  At position: {} (found: {})", element_start, found_token);
                log::debug!("Sequence: required element returned Empty, returning Empty");
                self.pos = frame.pos;
                for pos in tentatively_collected.iter() {
                    self.collected_transparent_positions.remove(pos);
                }
                stack
                    .results
                    .insert(frame.frame_id, (Node::Empty, frame.pos, None));
                return;
            }
        } else {
            *matched_idx = *child_end_pos;
            frame.accumulated.push(child_node.clone());
            if !*allow_gaps {
                let mut last_code_consumed = element_start;
                for check_pos in element_start..*matched_idx {
                    if check_pos < self.tokens.len() && self.tokens[check_pos].is_code() {
                        last_code_consumed = check_pos;
                    }
                }
                let mut collect_end = *matched_idx;
                while collect_end < self.tokens.len() && !self.tokens[collect_end].is_code() {
                    collect_end += 1;
                }
                log::debug!("Retroactive collection for frame_id={}: element_start={}, last_code_consumed={}, matched_idx={}, collect_end={}", frame.frame_id, element_start, last_code_consumed, *matched_idx, collect_end);
                for check_pos in (last_code_consumed + 1)..collect_end {
                    if check_pos < self.tokens.len() && !self.tokens[check_pos].is_code() {
                        let already_in_accumulated = tentatively_collected.contains(&check_pos);
                        let globally_collected =
                            self.collected_transparent_positions.contains(&check_pos);
                        if !already_in_accumulated && !globally_collected {
                            let tok = &self.tokens[check_pos];
                            let tok_type = tok.get_type();
                            if tok_type == "whitespace" {
                                log::debug!(
                                    "RETROACTIVELY collecting whitespace at {}: {:?}",
                                    check_pos,
                                    tok.raw()
                                );
                                frame.accumulated.push(Node::Whitespace {
                                    raw: tok.raw().to_string(),
                                    token_idx: check_pos,
                                });
                                tentatively_collected.push(check_pos);
                            } else if tok_type == "newline" {
                                log::debug!(
                                    "RETROACTIVELY collecting newline at {}: {:?}",
                                    check_pos,
                                    tok.raw()
                                );
                                frame.accumulated.push(Node::Newline {
                                    raw: tok.raw().to_string(),
                                    token_idx: check_pos,
                                });
                                tentatively_collected.push(check_pos);
                            }
                        }
                    }
                }
            }
            if *first_match && *parse_mode == crate::parser::ParseMode::GreedyOnceStarted {
                log::debug!(
                    "GREEDY_ONCE_STARTED: Trimming max_idx after first match from {} to terminator",
                    *max_idx
                );
                *max_idx = self.trim_to_terminator(*matched_idx, &frame_terminators);
                *first_match = false;
                log::debug!("  New max_idx: {}", *max_idx);
            }
        }
        let current_matched_idx = *matched_idx;
        let current_allow_gaps = *allow_gaps;
        let current_parse_mode = *parse_mode;
        let current_max_idx = *max_idx;
        let current_original_max_idx = *original_max_idx;
        let current_elem_idx = *current_element_idx;
        *current_element_idx += 1;
        let elements_clone = elements.clone();
        let all_elements_processed = current_elem_idx + 1 >= elements_clone.len();
        if all_elements_processed {
            log::debug!(
                "Sequence completing: current_elem_idx={}, elements_clone.len={}",
                current_elem_idx,
                elements_clone.len()
            );
            let result_node = if frame.accumulated.is_empty() {
                log::debug!("WARNING: Sequence completing with EMPTY accumulated! frame_id={}, current_elem_idx={}, elements.len={}", frame.frame_id, current_elem_idx, elements_clone.len());
                Node::Empty
            } else {
                Node::Sequence {
                    children: frame.accumulated.clone(),
                }
            };
            log::debug!(
                "Sequence COMPLETE: Storing result at frame_id={}",
                frame.frame_id
            );
            stack
                .results
                .insert(frame.frame_id, (result_node, current_matched_idx, None));
            return;
        } else {
            let mut next_pos = current_matched_idx;
            if current_allow_gaps
                && child_node.is_empty() == false
                && child_end_pos > &current_matched_idx
                && current_elem_idx < elements_clone.len()
            {
                let _idx =
                    self.skip_start_index_forward_to_code(current_matched_idx, current_max_idx);
                let has_uncollected = (current_matched_idx.._idx).any(|pos| {
                    pos < self.tokens.len()
                        && !self.tokens[pos].is_code()
                        && !self.collected_transparent_positions.contains(&pos)
                });
                if has_uncollected {
                    log::debug!(
                        "Collecting transparent tokens from {} to {}",
                        current_matched_idx,
                        _idx
                    );
                    for collect_pos in current_matched_idx.._idx {
                        if collect_pos < self.tokens.len() && !self.tokens[collect_pos].is_code() {
                            let tok = &self.tokens[collect_pos];
                            let tok_type = tok.get_type();
                            let already_collected =
                                frame.accumulated.iter().any(|node| match node {
                                    Node::Whitespace { token_idx: pos, .. }
                                    | Node::Newline { token_idx: pos, .. } => *pos == collect_pos,
                                    _ => false,
                                });
                            if !already_collected {
                                if tok_type == "whitespace" {
                                    log::debug!(
                                        "COLLECTING whitespace at {}: {:?}",
                                        collect_pos,
                                        tok.raw()
                                    );
                                    frame.accumulated.push(Node::Whitespace {
                                        raw: tok.raw().to_string(),
                                        token_idx: collect_pos,
                                    });
                                    tentatively_collected.push(collect_pos);
                                } else if tok_type == "newline" {
                                    log::debug!(
                                        "COLLECTING newline at {}: {:?}",
                                        collect_pos,
                                        tok.raw()
                                    );
                                    frame.accumulated.push(Node::Newline {
                                        raw: tok.raw().to_string(),
                                        token_idx: collect_pos,
                                    });
                                    tentatively_collected.push(collect_pos);
                                }
                            }
                        }
                    }
                }
                next_pos = _idx;
            }
            let next_elem_idx = current_elem_idx + 1;
            if next_pos >= current_max_idx && next_elem_idx < elements_clone.len() {
                let mut check_idx = next_elem_idx;
                let mut next_element_optional = true;
                while check_idx < elements_clone.len() {
                    if let Grammar::Meta(_) = &elements_clone[check_idx].as_ref() {
                        check_idx += 1;
                    } else {
                        next_element_optional = elements_clone[check_idx].is_optional();
                        break;
                    }
                }
                if next_element_optional {
                    for pos in tentatively_collected.iter() {
                        self.collected_transparent_positions.insert(*pos);
                    }
                    self.pos = current_matched_idx;
                    let result_node = if frame.accumulated.is_empty() {
                        Node::Empty
                    } else {
                        Node::Sequence {
                            children: frame.accumulated.clone(),
                        }
                    };
                    stack
                        .results
                        .insert(frame.frame_id, (result_node, current_matched_idx, None));
                    return;
                } else {
                    if current_parse_mode == crate::parser::ParseMode::Strict
                        || frame.accumulated.is_empty()
                    {
                        stack
                            .results
                            .insert(frame.frame_id, (Node::Empty, element_start, None));
                        return;
                    } else {
                        for pos in tentatively_collected.iter() {
                            self.collected_transparent_positions.insert(*pos);
                        }
                        self.pos = current_matched_idx;
                        let result_node = Node::Sequence {
                            children: frame.accumulated.clone(),
                        };
                        stack
                            .results
                            .insert(frame.frame_id, (result_node, current_matched_idx, None));
                        return;
                    }
                }
            }
            frame.state = FrameState::WaitingForChild {
                child_index: match frame.state {
                    FrameState::WaitingForChild { child_index, .. } => child_index + 1,
                    _ => unreachable!(),
                },
                total_children: match frame.state {
                    FrameState::WaitingForChild { total_children, .. } => total_children,
                    _ => unreachable!(),
                },
            };
            let mut next_elem_idx = current_elem_idx + 1;
            let mut created_child = false;
            let frame_id_for_debug = frame.frame_id;
            let mut final_accumulated = frame.accumulated.clone();
            while next_elem_idx < elements_clone.len() {
                if let Grammar::Meta(meta_type) = elements_clone[next_elem_idx].as_ref() {
                    if *meta_type == "indent" {
                        let mut insert_pos = final_accumulated.len();
                        while insert_pos > 0 {
                            match &final_accumulated[insert_pos - 1] {
                                Node::Whitespace { .. } | Node::Newline { .. } => {
                                    insert_pos -= 1;
                                }
                                _ => break,
                            }
                        }
                        final_accumulated.insert(
                            insert_pos,
                            Node::Meta {
                                token_type: meta_type,
                                token_idx: None,
                            },
                        );
                        frame.accumulated.insert(
                            insert_pos,
                            Node::Meta {
                                token_type: meta_type,
                                token_idx: None,
                            },
                        );
                    } else {
                        final_accumulated.push(Node::Meta {
                            token_type: meta_type,
                            token_idx: None,
                        });
                        frame.accumulated.push(Node::Meta {
                            token_type: meta_type,
                            token_idx: None,
                        });
                    }
                    next_elem_idx += 1;
                } else {
                    let child_frame = ParseFrame::new_child(
                        stack.frame_id_counter,
                        elements_clone[next_elem_idx].clone(),
                        next_pos,
                        frame_terminators.clone(),
                        Some(current_original_max_idx),
                    );
                    ParseFrame::push_sequence_child_and_update_parent(
                        stack,
                        frame,
                        child_frame,
                        next_elem_idx,
                    );
                    created_child = true;
                    break;
                }
            }
            if created_child {
                return;
            }
            self.pos = current_matched_idx;
            let result_node = if final_accumulated.is_empty() {
                Node::Empty
            } else {
                Node::Sequence {
                    children: final_accumulated,
                }
            };
            stack
                .results
                .insert(frame_id_for_debug, (result_node, current_matched_idx, None));
        }
    }

    /// Handle Bracketed grammar Initial state in iterative parser
    pub(crate) fn handle_bracketed_initial(
        &mut self,
        grammar: Arc<Grammar>,
        frame: &mut ParseFrame,
        parent_terminators: &[Arc<Grammar>],
        stack: &mut ParseFrameStack,
    ) -> Result<NextStep, ParseError> {
        let (
            bracket_pairs,
            elements,
            optional,
            bracket_terminators,
            reset_terminators,
            allow_gaps,
            parse_mode,
        ) = match grammar.as_ref() {
            Grammar::Bracketed {
                bracket_pairs,
                elements,
                optional,
                terminators: bracket_terminators,
                reset_terminators,
                allow_gaps,
                parse_mode,
                ..
            } => (
                bracket_pairs,
                elements,
                optional,
                bracket_terminators,
                reset_terminators,
                allow_gaps,
                parse_mode,
            ),
            _ => {
                return Err(ParseError {
                    message: "handle_bracketed_initial called with non-Bracketed grammar"
                        .to_string(),
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
        let all_terminators: Vec<Arc<Grammar>> = if *reset_terminators {
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
            grammar: grammar.clone(),
            state: BracketedState::MatchingOpen,
            last_child_frame_id: None,
            bracket_max_idx: None,
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

    /// Handle Bracketed grammar WaitingForChild state in iterative parser
    pub(crate) fn handle_bracketed_waiting_for_child(
        &mut self,
        frame: &mut crate::parser::ParseFrame,
        child_node: &crate::parser::Node,
        child_end_pos: &usize,
        stack: &mut crate::parser::iterative::ParseFrameStack,
    ) {
        // Extract the context from the frame
        let FrameContext::Bracketed {
            grammar,
            state,
            last_child_frame_id,
            bracket_max_idx,
        } = &mut frame.context else {
            unreachable!("Expected Bracketed context");
        };
        let local_bracket_max_idx = *bracket_max_idx;
        log::debug!(
            "Bracketed WaitingForChild: state={:?}, child_node empty={}",
            state,
            child_node.is_empty()
        );
        let Grammar::Bracketed {
            elements,
            bracket_pairs,
            allow_gaps,
            parse_mode,
            optional,
            ..
        } = grammar.as_ref() else {
            panic!("Expected Grammar::Bracketed in FrameContext::Bracketed");
        };
        match state {
            BracketedState::MatchingOpen => {
                if child_node.is_empty() {
                    self.pos = frame.pos;
                    log::debug!("Bracketed returning Empty (no opening bracket, optional={})", optional);
                    stack.results.insert(
                        frame.frame_id,
                        (Node::Empty, frame.pos, None),
                    );
                    return;
                } else {
                    frame.accumulated.push(child_node.clone());
                    let content_start_idx = *child_end_pos;
                    let bracket_max_idx = child_node.get_token_idx().and_then(|open_idx| {
                        let idx = self.get_matching_bracket_idx(open_idx);
                        if let Some(close_idx) = idx {
                            let close_tok = self.tokens.get(close_idx);
                            let before_tok = if close_idx > 0 { self.tokens.get(close_idx - 1) } else { None };
                            let after_tok = self.tokens.get(close_idx + 1);
                            log::debug!(
                                "[BRACKET-DEBUG] open_idx={}, close_idx={}, close_tok={:?}, before_tok={:?}, after_tok={:?}",
                                open_idx, close_idx,
                                close_tok.map(|t| t.raw()),
                                before_tok.map(|t| t.raw()),
                                after_tok.map(|t| t.raw()),
                            );
                        } else {
                            log::debug!("[BRACKET-DEBUG] open_idx={}, no matching close_idx", open_idx);
                        }
                        idx
                    });
                    if let Some(close_idx) = bracket_max_idx {
                        log::debug!(
                            "Bracketed: Using pre-computed closing bracket at idx={} as max_idx",
                            close_idx
                        );
                    }
                    if *allow_gaps {
                        let code_idx = self.skip_start_index_forward_to_code(
                            content_start_idx,
                            self.tokens.len(),
                        );
                        for pos in content_start_idx..code_idx {
                            if let Some(tok) = self.tokens.get(pos) {
                                let tok_type = tok.get_type();
                                if tok_type == "whitespace" {
                                    frame.accumulated.push(Node::Whitespace {
                                        raw: tok.raw().to_string(),
                                        token_idx: pos,
                                    });
                                } else if tok_type == "newline" {
                                    frame.accumulated.push(Node::Newline {
                                        raw: tok.raw().to_string(),
                                        token_idx: pos,
                                    });
                                }
                            }
                        }
                        self.pos = code_idx;
                    } else {
                        self.pos = content_start_idx;
                    }
                    *state = BracketedState::MatchingContent;
                    let content_grammar = Grammar::Sequence {
                        elements: elements.clone(),
                        optional: false,
                        terminators: vec![(*bracket_pairs.1).clone()],
                        reset_terminators: true,
                        allow_gaps: *allow_gaps,
                        parse_mode: *parse_mode,
                        simple_hint: None,
                    };
                    let mut child_frame = ParseFrame {
                        frame_id: stack.frame_id_counter,
                        grammar: content_grammar.into(),
                        pos: self.pos,
                        terminators: vec![(*bracket_pairs.1).clone()],
                        state: FrameState::Initial,
                        accumulated: vec![],
                        context: FrameContext::Bracketed {
                            grammar: grammar.clone(),
                            state: BracketedState::MatchingContent,
                            last_child_frame_id: *last_child_frame_id,
                            bracket_max_idx,
                        },
                        parent_max_idx: bracket_max_idx,
                    };
                    *last_child_frame_id = Some(stack.frame_id_counter);
                    stack.frame_id_counter += 1;
                    stack.push(frame);
                    stack.push(&mut child_frame);
                    return;
                }
            }
            BracketedState::MatchingContent => {
                log::debug!("Bracketed MatchingContent - frame_id={}, child_end_pos={}, is_empty={}", frame.frame_id, child_end_pos, child_node.is_empty());
                let mut check_pos = *child_end_pos;
                while let Some(tok) = self.tokens.get(check_pos) {
                    let is_not_code = !tok.is_code();
                    if is_not_code {
                        log::debug!("[BRACKET-DEBUG] Skipping non-code token at pos {}: type='{}', raw='{}'", check_pos, tok.get_type(), tok.raw());
                        check_pos += 1;
                    } else {
                        break;
                    }
                }
                if let Some(expected_close_pos) = local_bracket_max_idx {
                    log::debug!("[BRACKET-DEBUG] After skipping ws/nl: check_pos={}, expected_close_pos={}", check_pos, expected_close_pos);
                    if check_pos != expected_close_pos {
                        log::debug!("[BRACKET-DEBUG] Bracketed content did not end at closing bracket (check_pos != expected_close_pos), returning Node::Empty for retry. frame_id={}, frame.pos={}", frame.frame_id, frame.pos);
                        self.pos = frame.pos;
                        stack.results.insert(
                            frame.frame_id,
                            (Node::Empty, frame.pos, None),
                        );
                        return;
                    } else {
                        log::debug!("[BRACKET-DEBUG] Bracketed content ends at expected closing bracket (check_pos == expected_close_pos)");
                    }
                }
                if !child_node.is_empty() {
                    let mut to_process = vec![child_node.clone()];
                    while let Some(node) = to_process.pop() {
                        match node {
                            Node::Sequence { children } | Node::DelimitedList { children } => {
                                to_process.extend(children.into_iter().rev());
                            }
                            _ => {
                                frame.accumulated.push(node);
                            }
                        }
                    }
                }
                let gap_start = *child_end_pos;
                self.pos = gap_start;
                log::debug!("DEBUG: After content, gap_start={}, current_pos={}", gap_start, self.pos);
                if *allow_gaps {
                    let code_idx = self.skip_start_index_forward_to_code(
                        gap_start,
                        self.tokens.len(),
                    );
                    log::debug!(
                        "[BRACKET-DEBUG] After content, gap_start={}, code_idx={}, token at gap_start={:?}, token at code_idx={:?}",
                        gap_start, code_idx,
                        self.tokens.get(gap_start).map(|t| t.raw()),
                        self.tokens.get(code_idx).map(|t| t.raw()),
                    );
                    for pos in gap_start..code_idx {
                        if let Some(tok) = self.tokens.get(pos) {
                            let tok_type = tok.get_type();
                            if tok_type == "whitespace" {
                                frame.accumulated.push(Node::Whitespace {
                                    raw: tok.raw().to_string(),
                                    token_idx: pos,
                                });
                            } else if tok_type == "newline" {
                                frame.accumulated.push(Node::Newline {
                                    raw: tok.raw().to_string(),
                                    token_idx: pos,
                                });
                            }
                        }
                    }
                    self.pos = code_idx;
                }
                log::debug!("DEBUG: Checking for closing bracket - self.pos={}, tokens.len={}", self.pos, self.tokens.len());
                if self.pos >= self.tokens.len()
                    || self.peek().is_some_and(|t| t.get_type() == "end_of_file")
                {
                    log::debug!("DEBUG: No closing bracket found!");
                    if *parse_mode == ParseMode::Strict {
                        self.pos = frame.pos;
                        stack.results.insert(
                            frame.frame_id,
                            (Node::Empty, frame.pos, None),
                        );
                        return;
                    } else {
                        panic!("Couldn't find closing bracket for opening bracket");
                    }
                } else {
                    log::debug!("DEBUG: Transitioning to MatchingClose!");
                    *state = BracketedState::MatchingClose;
                    let parent_limit = frame.parent_max_idx;
                    log::debug!("DEBUG: Creating closing bracket child at pos={}, parent_limit={:?}", self.pos, parent_limit);
                    let mut child_frame = ParseFrame {
                        frame_id: stack.frame_id_counter,
                        grammar: (*bracket_pairs.1).clone(),
                        pos: self.pos,
                        terminators: vec![(*bracket_pairs.1).clone()],
                        state: FrameState::Initial,
                        accumulated: vec![],
                        context: FrameContext::None,
                        parent_max_idx: parent_limit,
                    };
                    *last_child_frame_id = Some(stack.frame_id_counter);
                    stack.frame_id_counter += 1;
                    stack.push(frame);
                    stack.push(&mut child_frame);
                    return;
                }
            }
            BracketedState::MatchingClose => {
                log::debug!("DEBUG: Bracketed MatchingClose - child_node.is_empty={}, child_end_pos={}", child_node.is_empty(), child_end_pos);
                let window = 5;
                let start = if self.pos >= window { self.pos - window } else { 0 };
                let end = (self.pos + window + 1).min(self.tokens.len());
                for idx in start..end {
                    let t = &self.tokens[idx];
                    log::debug!(
                        "[BRACKET-DEBUG] Token[{}]: type='{}', raw='{}'{}",
                        idx,
                        t.get_type(),
                        t.raw(),
                        if idx == self.pos { " <-- parser pos" } else { "" }
                    );
                }
                if let Some(tok) = self.tokens.get(self.pos) {
                    log::debug!("[BRACKET-DEBUG] At parser pos {}: type='{}', raw='{}'", self.pos, tok.get_type(), tok.raw());
                } else {
                    log::debug!("[BRACKET-DEBUG] At parser pos {}: <out of bounds>", self.pos);
                }
                if child_node.is_empty() {
                    if *parse_mode == ParseMode::Strict {
                        self.pos = frame.pos;
                        stack.results.insert(
                            frame.frame_id,
                            (Node::Empty, frame.pos, None),
                        );
                        return;
                    } else {
                        panic!("Couldn't find closing bracket for opening bracket");
                    }
                } else {
                    frame.accumulated.push(child_node.clone());
                    self.pos = *child_end_pos;
                    let result_node = Node::Bracketed {
                        children: frame.accumulated.clone(),
                    };
                    log::debug!(
                        "Bracketed COMPLETE: {} children, storing result at frame_id={}",
                        frame.accumulated.len(),
                        frame.frame_id
                    );
                    stack.results.insert(
                        frame.frame_id,
                        (result_node, *child_end_pos, None),
                    );
                    return;
                }
            }
        }
    }
}
