use std::sync::Arc;

use crate::parser::{
    iterative::{FrameResult, ParseFrameStack},
    BracketedState, FrameContext, FrameState, Node, ParseError, ParseFrame, Parser,
};
use sqlfluffrs_types::{Grammar, ParseMode};

impl<'a> Parser<'_> {
    /// Handle Sequence grammar Initial state in iterative parser.
    ///
    /// ## State Machine:
    /// ```text
    /// Initial
    ///   ↓ (calculate max_idx, push first element as child)
    /// WaitingForChild (for each element in sequence)
    ///   ↓ (child matched)
    ///   ├─→ GREEDY_ONCE_STARTED && first_match: trim max_idx to terminators
    ///   ├─→ More elements: push next element as child, stay in WaitingForChild
    ///   └─→ All elements matched: Terminal (success)
    ///   ↓ (child failed - returned Empty)
    ///   ├─→ Element is optional: skip to next element
    ///   ├─→ Element is required + STRICT mode: Terminal (fail with Empty)
    ///   └─→ Element is required + GREEDY mode: wrap remaining as Unparsable, Terminal
    /// ```
    ///
    /// ## Key Behavior:
    /// - Elements must match IN ORDER (not interchangeable like OneOf/AnySetOf)
    /// - Handles Meta elements inline without creating child frames
    /// - GREEDY_ONCE_STARTED: after first match, trims max_idx to terminators
    /// - STRICT mode: fails on first required element that doesn't match
    /// - GREEDY mode: wraps unparsable content and continues
    /// - Tracks transparent tokens tentatively, commits/rollbacks on success/failure
    /// Returns true if caller should continue main loop
    pub(crate) fn handle_sequence_initial(
        &mut self,
        grammar: Arc<Grammar>,
        mut frame: ParseFrame,
        parent_terminators: &[Arc<Grammar>],
        stack: &mut ParseFrameStack,
    ) -> Result<FrameResult, ParseError> {
        // CRITICAL: Restore parser position from frame before doing anything else
        // The global self.pos may have been advanced by other frames
        self.pos = frame.pos;

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
        log::debug!("DEBUG: Sequence Initial at pos={}, parent_max_idx={:?}, allow_gaps={}, elements.len()={}, parse_mode={:?}",
                  pos, frame.parent_max_idx, allow_gaps, elements.len(), parse_mode);
        let start_idx = pos; // Where did we start

        // Combine parent and local terminators
        let all_terminators =
            self.combine_terminators(seq_terminators, parent_terminators, *reset_terminators);

        // Calculate max_idx with terminator and parent constraints
        self.pos = start_idx;
        let max_idx = self.calculate_max_idx(
            start_idx,
            &all_terminators,
            *parse_mode,
            frame.parent_max_idx,
        );

        log::debug!(
            "DEBUG: Sequence Initial calculated max_idx={}, frame.parent_max_idx={:?}",
            max_idx,
            frame.parent_max_idx
        );

        // Push a collection checkpoint for this sequence
        // This allows us to rollback transparent token collections if we backtrack
        self.push_collection_checkpoint(frame.frame_id);

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
        stack.push(&mut frame);

        // DON'T skip whitespace here! Python's Sequence.match skips whitespace IN THE LOOP
        // before each element match attempt (see sequence.py lines 190-196).
        // If we skip here and the first element fails, we'll have consumed whitespace
        // but returned Empty, violating the Empty contract.
        //
        // Whitespace should be skipped BETWEEN successfully matched elements, not before
        // attempting to match the first element. This logic is in handle_sequence_waiting_for_child.
        let first_child_pos = start_idx; // Start at the original position

        // Handle empty elements case - sequence with no elements should succeed immediately
        if elements.is_empty() {
            // Pop the frame we just pushed
            stack.pop();
            // Transition to Combining to finalize empty Sequence result
            frame.end_pos = Some(start_idx);
            frame.state = FrameState::Combining;
            stack.push(&mut frame);
            return Ok(crate::parser::iterative::FrameResult::Done);
        }

        // Push first child to parse
        if !elements.is_empty() {
            // Check if we've run out of segments before first element
            if first_child_pos >= max_idx {
                // Haven't matched anything yet and already at limit
                // Pop the frame we just pushed since we're returning early
                stack.pop();

                // Rollback the checkpoint since we're failing
                self.rollback_collection_checkpoint(current_frame_id);

                if *parse_mode == ParseMode::Strict {
                    // In strict mode, return Empty
                    stack
                        .results
                        .insert(current_frame_id, (Node::Empty, start_idx, None));
                    return Ok(FrameResult::Done); // Don't continue, we stored a result
                }
                // In greedy modes, check if first element is optional
                if elements[0].is_optional() {
                    // First element is optional, can skip
                    stack
                        .results
                        .insert(current_frame_id, (Node::Empty, start_idx, None));
                    return Ok(FrameResult::Done);
                } else {
                    // Required element, no segments - this is unparsable in greedy mode
                    stack
                        .results
                        .insert(current_frame_id, (Node::Empty, start_idx, None));
                    return Ok(FrameResult::Done);
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
                            return Ok(FrameResult::Done);
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
                        end_pos: None,
                        transparent_positions: None,
                        element_key: None,
                    };

                    // Update parent (already on stack) and push child
                    ParseFrame::update_sequence_parent_and_push_child(
                        stack,
                        child_frame,
                        child_idx,
                    );
                    return Ok(FrameResult::Done); // Child pushed, continue main loop
                }
            }
        }

        Ok(FrameResult::Done) // No child pushed, don't continue
    }

    /// Handle Sequence grammar WaitingForChild state in iterative parser
    pub(crate) fn handle_sequence_waiting_for_child(
        &mut self,
        mut frame: ParseFrame,
        child_node: &Node,
        child_end_pos: &usize,
        stack: &mut ParseFrameStack,
        iteration_count: usize,
        frame_terminators: Vec<Arc<Grammar>>,
    ) -> Result<FrameResult, ParseError> {
        log::debug!(
            "[SEQUENCE CHILD] frame_id={}, child_end_pos={}, child_empty={}",
            frame.frame_id,
            child_end_pos,
            child_node.is_empty()
        );

        let FrameContext::Sequence {
            grammar,
            matched_idx,
            tentatively_collected,
            max_idx,
            original_max_idx,
            last_child_frame_id: _,
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
            terminators: sequence_terminators,
            simple_hint: _,
            ..
        } = grammar.as_ref()
        else {
            panic!("Expected Grammar::Sequence in FrameContext::Sequence");
        };
        let element_start = *matched_idx;
        let current_element = &elements[*current_element_idx];

        if child_node.is_empty() {
            // CRITICAL: When a child returns Empty, it MUST not have consumed any tokens.
            // In Python, an empty MatchResult has slice(idx, idx) - zero length.
            // If child_end_pos != element_start, the child consumed tokens before failing,
            // which violates the Empty contract.
            //
            // FIX: Override the buggy child_end_pos with element_start to maintain Python parity.
            // This handles cases where child grammars with allow_gaps=True call collect_transparent,
            // advancing self.pos, but then fail to properly restore it before returning Empty.
            let corrected_child_end_pos = if *child_end_pos != element_start {
                // Get child grammar description for debugging
                let child_desc = match current_element.as_ref() {
                    Grammar::Ref { name, .. } => format!("Ref({})", name),
                    Grammar::Sequence { .. } => "Sequence".to_string(),
                    Grammar::OneOf { .. } => "OneOf".to_string(),
                    Grammar::Delimited { .. } => "Delimited".to_string(),
                    Grammar::StringParser { template, .. } => {
                        format!("StringParser('{}')", template)
                    }
                    _ => format!("{:?}", current_element).chars().take(50).collect(),
                };

                log::debug!(
                    "[SEQUENCE FIX] Child {} returned Empty with child_end_pos={} > element_start={}. Correcting to element_start.",
                    child_desc, *child_end_pos, element_start
                );

                element_start
            } else {
                *child_end_pos
            };

            log::debug!("[SEQUENCE EMPTY] frame_id={}, current_elem_idx={}/{}, is_optional={}, element_start={}, child_end_pos={}, corrected={}",
                frame.frame_id, *current_element_idx, elements.len(), current_element.is_optional(), element_start, *child_end_pos, corrected_child_end_pos);

            // Use corrected_child_end_pos for all subsequent logic
            let child_end_pos = &corrected_child_end_pos;

            if current_element.is_optional() {
                log::debug!(
                    "[SEQUENCE EMPTY OPT] frame_id={}, moving to next element",
                    frame.frame_id
                );
                log::debug!(
                    "Sequence: child returned Empty and is optional, continuing to next element"
                );
                // Don't advance matched_idx or push anything - just move to next element
                *current_element_idx += 1;

                // Check if we've processed all elements
                if *current_element_idx >= elements.len() {
                    log::debug!("[SEQUENCE ALL DONE] frame_id={}, completing after processing all {} elements",
                        frame.frame_id, elements.len());
                    // All elements processed (some optional and skipped)
                    log::debug!(
                        "Sequence completing after optional elements: current_elem_idx={}, elements.len={}",
                        *current_element_idx,
                        elements.len()
                    );

                    let result_node = if frame.accumulated.is_empty() {
                        Node::Empty
                    } else {
                        Node::Sequence {
                            children: frame.accumulated.clone(),
                        }
                    };

                    // Store transparent positions and commit checkpoint
                    stack
                        .transparent_positions
                        .insert(frame.frame_id, tentatively_collected.clone());
                    self.commit_collection_checkpoint(frame.frame_id);

                    log::debug!(
                        "[SEQUENCE COMPLETE OPT] frame_id={}, matched_idx={}, parse_mode={:?}",
                        frame.frame_id,
                        *matched_idx,
                        *parse_mode
                    );
                    stack
                        .results
                        .insert(frame.frame_id, (result_node, *matched_idx, None));
                    return Ok(FrameResult::Done);
                }

                // Create next child frame for the next element
                let next_elem_idx = *current_element_idx;
                let next_pos = if *allow_gaps {
                    self.skip_start_index_forward_to_code(*matched_idx, *max_idx)
                } else {
                    *matched_idx
                };

                // Check if we've run out of segments
                if next_pos >= *max_idx {
                    log::debug!("[SEQUENCE AT BOUNDARY] frame_id={}, next_pos={}, max_idx={}, checking remaining elements",
                        frame.frame_id, next_pos, *max_idx);
                    // Check if remaining elements are all optional
                    let remaining_all_optional = elements[next_elem_idx..]
                        .iter()
                        .all(|e| e.is_optional() || matches!(e.as_ref(), Grammar::Meta(_)));

                    if remaining_all_optional {
                        log::debug!("[SEQUENCE BOUNDARY + ALL OPT] frame_id={}, all {} remaining elements are optional, completing",
                            frame.frame_id, elements.len() - next_elem_idx);
                        // All remaining are optional, we can finish successfully
                        let result_node = if frame.accumulated.is_empty() {
                            Node::Empty
                        } else {
                            Node::Sequence {
                                children: frame.accumulated.clone(),
                            }
                        };

                        stack
                            .transparent_positions
                            .insert(frame.frame_id, tentatively_collected.clone());
                        self.commit_collection_checkpoint(frame.frame_id);

                        stack
                            .results
                            .insert(frame.frame_id, (result_node, *matched_idx, None));
                        return Ok(FrameResult::Done);
                    } else if *parse_mode == ParseMode::Strict {
                        log::debug!("[SEQUENCE BOUNDARY + STRICT] frame_id={}, has required elements, failing", frame.frame_id);
                        // Strict mode and required elements remaining: fail
                        self.rollback_collection_checkpoint(frame.frame_id);
                        stack
                            .results
                            .insert(frame.frame_id, (Node::Empty, frame.pos, None));
                        return Ok(FrameResult::Done);
                    } else {
                        log::debug!("[SEQUENCE BOUNDARY + GREEDY] frame_id={}, has required elements but GREEDY mode, attempting to continue", frame.frame_id);
                        // GREEDY mode: try to continue even at boundary
                    }
                }

                // Push next child frame
                let child_frame = ParseFrame::new_child(
                    stack.frame_id_counter,
                    elements[next_elem_idx].clone(),
                    next_pos,
                    frame_terminators.clone(),
                    Some(*original_max_idx),
                );
                ParseFrame::push_sequence_child_and_update_parent(
                    stack,
                    &mut frame,
                    child_frame,
                    next_elem_idx,
                );
                return Ok(FrameResult::Done);
            } else {
                log::debug!(
                    "[SEQUENCE EMPTY REQ] frame_id={}, required element {} returned Empty!",
                    frame.frame_id,
                    *current_element_idx
                );
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

                // Python reference: sequence.py Sequence.match() lines ~240-280
                // When a required element fails to match, check parse_mode:
                // - STRICT: return Empty (no match)
                // - GREEDY_ONCE_STARTED: if nothing matched yet, return Empty; else wrap as unparsable
                // - GREEDY: wrap remaining content as unparsable
                if *parse_mode == ParseMode::Strict {
                    log::debug!(
                        "Sequence: STRICT mode - required element returned Empty, returning Empty"
                    );
                    self.pos = frame.pos;
                    // Rollback the checkpoint - undoes all collections made during this sequence
                    self.rollback_collection_checkpoint(frame.frame_id);
                    stack
                        .results
                        .insert(frame.frame_id, (Node::Empty, frame.pos, None));
                    return Ok(FrameResult::Done);
                }

                // GREEDY or GREEDY_ONCE_STARTED mode
                // Check if we've matched anything yet
                if element_start == frame.pos {
                    // Haven't matched anything yet
                    if *parse_mode == ParseMode::GreedyOnceStarted {
                        // GREEDY_ONCE_STARTED with no matches yet: return Empty
                        log::debug!(
                            "Sequence: GREEDY_ONCE_STARTED mode - no matches yet, returning Empty"
                        );
                        self.pos = frame.pos;
                        // Rollback the checkpoint - undoes all collections made during this sequence
                        self.rollback_collection_checkpoint(frame.frame_id);
                        stack
                            .results
                            .insert(frame.frame_id, (Node::Empty, frame.pos, None));
                        return Ok(FrameResult::Done);
                    }

                    // GREEDY mode with no matches: wrap all content as unparsable
                    log::debug!(
                        "Sequence: GREEDY mode - wrapping all content from {} to {} as unparsable",
                        element_start,
                        *max_idx
                    );
                    let unparsable_children: Vec<Node> = (element_start..*max_idx)
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
                        .insert(frame.frame_id, (unparsable_node, *max_idx, None));
                    return Ok(FrameResult::Done);
                }

                // We've already matched some elements - wrap remaining content as unparsable
                log::debug!("Sequence: GREEDY mode - partial match, wrapping remaining content from {} to {} as unparsable", element_start, *max_idx);

                // Collect any remaining whitespace/newlines if allow_gaps
                let unparsable_start = if *allow_gaps {
                    self.skip_start_index_forward_to_code(element_start, *max_idx)
                } else {
                    element_start
                };

                // Add whitespace between last match and unparsable content
                if *allow_gaps && unparsable_start > element_start {
                    for pos in element_start..unparsable_start {
                        if pos < self.tokens.len() {
                            let tok = &self.tokens[pos];
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
                }

                // Create unparsable node for remaining content
                let unparsable_children: Vec<Node> = (unparsable_start..*max_idx)
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

                frame.accumulated.push(unparsable_node);

                // Complete the sequence with what we have
                let result_node = Node::Sequence {
                    children: frame.accumulated.clone(),
                };

                stack
                    .results
                    .insert(frame.frame_id, (result_node, *max_idx, None));
                return Ok(FrameResult::Done);
            }
        } else {
            // Child returned a non-empty result
            // Don't collect inter-child tokens here - the between-elements collection (in handle_sequence_element_loop) handles gaps
            // Collecting here would duplicate tokens that are within the child's range

            *matched_idx = *child_end_pos;

            // If the child matched beyond the current max_idx, update max_idx to include it
            // This can happen in GREEDY_ONCE_STARTED mode where max_idx was trimmed to a
            // terminator, but subsequent elements (like FROM clause) legitimately parse beyond it
            if *child_end_pos > *max_idx {
                log::debug!(
                    "Sequence: child matched beyond max_idx ({}), extending max_idx to {}",
                    *max_idx,
                    *child_end_pos
                );
                *max_idx = *child_end_pos;
            }

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
                        // Also check frame's accumulated nodes to prevent duplicates
                        let already_in_frame = frame.accumulated.iter().any(|node| match node {
                            Node::Whitespace { token_idx: idx, .. }
                            | Node::Newline { token_idx: idx, .. } => *idx == check_pos,
                            _ => false,
                        });
                        if !already_in_accumulated && !already_in_frame {
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
            log::debug!(
                "[TRIM CHECK] frame_id={}, first_match={}, parse_mode={:?}, about to check trimming",
                frame.frame_id, *first_match, *parse_mode
            );
            if *first_match && *parse_mode == crate::parser::ParseMode::GreedyOnceStarted {
                log::debug!(
                    "GREEDY_ONCE_STARTED: Trimming max_idx after first match from {} to terminator",
                    *max_idx
                );
                log::debug!(
                    "GREEDY_ONCE_STARTED: Using {} combined terminators (sequence + parent): {:?}",
                    frame.terminators.len(),
                    frame.terminators
                );
                // Use the combined terminators (sequence + parent) to respect parent boundaries
                // For example, a StatementSegment's ';' terminator should stop the Sequence
                //
                // Also pass the remaining elements to be parsed - this prevents terminators
                // that are also the start of upcoming elements from incorrectly trimming
                // (e.g., FROM is a terminator for SELECT clause but also starts FROM clause)
                let remaining_elements: Vec<Arc<Grammar>> = elements
                    .iter()
                    .skip(*current_element_idx + 1)
                    .cloned()
                    .collect();
                log::debug!(
                    "GREEDY_ONCE_STARTED: Passing {} remaining elements to trim logic",
                    remaining_elements.len(),
                );
                let new_max_idx = self.trim_to_terminator_with_elements(
                    *matched_idx,
                    &frame.terminators,
                    &remaining_elements,
                );
                // Respect the original parent max_idx constraint
                *max_idx = new_max_idx.min(*original_max_idx);
                *first_match = false;
                log::debug!(
                    "  New max_idx: {} (trimmed to {}, constrained by original {})",
                    *max_idx,
                    new_max_idx,
                    *original_max_idx
                );
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

            // Python reference: sequence.py Sequence.match() lines ~344-360
            // After matching all elements, check if there's remaining content in GREEDY modes
            // If so, wrap it as unparsable
            log::debug!(
                "[SEQUENCE] Completion check: frame_id={}, parse_mode={:?}, matched_idx={}, max_idx={}, elements.len={}",
                frame.frame_id, current_parse_mode, current_matched_idx, current_max_idx, elements_clone.len()
            );
            if current_parse_mode != ParseMode::Strict {
                // Skip whitespace if allow_gaps
                let unparsable_start = if current_allow_gaps {
                    self.skip_start_index_forward_to_code(current_matched_idx, current_max_idx)
                } else {
                    current_matched_idx
                };

                // If there's content between where we finished and max_idx, it's unparsable
                if unparsable_start < current_max_idx {
                    log::debug!(
                        "Sequence GREEDY: wrapping remaining content from {} to {} as unparsable",
                        unparsable_start,
                        current_max_idx
                    );

                    // Collect whitespace before unparsable content if allow_gaps
                    if current_allow_gaps && unparsable_start > current_matched_idx {
                        for pos in current_matched_idx..unparsable_start {
                            if pos < self.tokens.len() {
                                let tok = &self.tokens[pos];
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
                    }

                    // Create unparsable node for remaining content
                    let unparsable_children: Vec<Node> = (unparsable_start..current_max_idx)
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

                    if !unparsable_children.is_empty() {
                        let unparsable_node = Node::Unparsable {
                            children: unparsable_children,
                            expected_message: "end of sequence".to_string(),
                        };
                        frame.accumulated.push(unparsable_node);
                    }
                }
            }

            let result_node = if frame.accumulated.is_empty() {
                log::debug!("WARNING: Sequence completing with EMPTY accumulated! frame_id={}, current_elem_idx={}, elements.len={}", frame.frame_id, current_elem_idx, elements_clone.len());
                Node::Empty
            } else {
                let grammar_desc = match grammar.as_ref() {
                    Grammar::Sequence { elements, .. } if !elements.is_empty() => {
                        match elements[0].as_ref() {
                            Grammar::Ref { name, .. } => format!("Seq[{}...]", name),
                            _ => "Seq[...]".to_string(),
                        }
                    }
                    _ => "Seq".to_string(),
                };
                log::debug!(
                    "Sequence result ({}): accumulated.len = {}, tentatively_collected = {:?}",
                    grammar_desc,
                    frame.accumulated.len(),
                    tentatively_collected
                );

                Node::Sequence {
                    children: frame.accumulated.clone(),
                }
            };

            // NOTE: We do NOT mark tentatively_collected as globally collected here
            // because this result might not be used (due to backtracking/caching).
            // Instead, store them in stack.transparent_positions so they can be marked
            // when the parent actually retrieves and uses this result.
            stack
                .transparent_positions
                .insert(frame.frame_id, tentatively_collected.clone());

            // Pop the collection checkpoint but DON'T commit it globally yet.
            // The positions are stored in transparent_positions, and will be marked globally
            // only when the parent actually uses this result.
            // We rollback to remove from collected_transparent_positions, but keep in transparent_positions.
            self.rollback_collection_checkpoint(frame.frame_id);

            log::debug!(
                "Sequence COMPLETE: Storing result at frame_id={}",
                frame.frame_id
            );
            // In STRICT mode, end at current_matched_idx (where we actually matched to)
            // In GREEDY modes, end at current_max_idx (we consumed extra content as unparsable)
            let end_pos = if current_parse_mode == ParseMode::Strict {
                current_matched_idx
            } else {
                current_max_idx
            };
            log::debug!("[SEQUENCE COMPLETE] frame_id={}, current_matched_idx={}, current_max_idx={}, parse_mode={:?}, end_pos={}",
                frame.frame_id, current_matched_idx, current_max_idx, current_parse_mode, end_pos);

            // Store end_pos in frame for Combining handler
            frame.end_pos = Some(end_pos);

            // Transition to Combining state
            log::debug!(
                "Sequence: All elements processed, transitioning to Combining state, frame_id={}",
                frame.frame_id
            );
            frame.state = FrameState::Combining;
            stack.push(&mut frame);
            return Ok(FrameResult::Done);
        } else {
            let mut next_pos = current_matched_idx;
            log::debug!(
                "Checking transparent collection: child_end_pos={}, current_matched_idx={}, current_elem_idx={}, allow_gaps={}, child_empty={}",
                child_end_pos, current_matched_idx, current_elem_idx, current_allow_gaps, child_node.is_empty()
            );
            // Collect transparent tokens between this child and the next element
            // We should do this whenever allow_gaps is true and there are more elements to process
            if current_allow_gaps
                && !child_node.is_empty()
                && current_elem_idx < elements_clone.len()
            {
                let _idx =
                    self.skip_start_index_forward_to_code(current_matched_idx, current_max_idx);
                log::debug!(
                    "Collecting transparent tokens from {} to {}",
                    current_matched_idx,
                    _idx
                );
                // Collect all non-code tokens between current position and next code token
                for collect_pos in current_matched_idx.._idx {
                    if collect_pos < self.tokens.len() && !self.tokens[collect_pos].is_code() {
                        let tok = &self.tokens[collect_pos];
                        let tok_type = tok.get_type();
                        // Only check if already in THIS frame's accumulated to avoid duplicating within the same frame
                        let already_in_frame = frame.accumulated.iter().any(|node| match node {
                            Node::Whitespace { token_idx: pos, .. }
                            | Node::Newline { token_idx: pos, .. } => *pos == collect_pos,
                            _ => false,
                        });
                        if !already_in_frame {
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
                next_pos = _idx;
            }
            let next_elem_idx = current_elem_idx + 1;

            // Log next element info for debugging
            if next_elem_idx < elements_clone.len() {
                let next_elem_desc = match elements_clone[next_elem_idx].as_ref() {
                    Grammar::Ref { name, .. } => format!("Ref({})", name),
                    Grammar::Meta(m) => format!("Meta({})", m),
                    g => format!("{:?}", g).chars().take(50).collect(),
                };
                log::debug!(
                    "SEQUENCE NEXT ELEMENT: idx={}, grammar={}, optional={}",
                    next_elem_idx,
                    next_elem_desc,
                    elements_clone[next_elem_idx].is_optional()
                );
            }

            // DEBUG: Log the state before the early return check
            log::debug!("SEQUENCE CONTINUATION CHECK: next_pos={}, current_max_idx={}, next_elem_idx={}, elements_clone.len()={}",
                next_pos, current_max_idx, next_elem_idx, elements_clone.len());

            // Check if we've reached the max_idx boundary
            // We use >= here because when next_pos == max_idx, we're at the boundary.
            // However, if we just extended max_idx because a child went beyond it, we should
            // NOT stop here - the extension means we can continue parsing.
            // The child extension logic (lines 583-594) already updated max_idx if a child
            // went beyond it, so if we're still at/beyond the boundary here AND we didn't
            // just extend it, we should check if remaining elements are optional.
            if next_pos >= current_max_idx && next_elem_idx < elements_clone.len() {
                // Determine if the next element (skipping Meta elements) is optional
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

                if !next_element_optional {
                    // Next element is required but we've hit max_idx
                    // Python parity: if required element at boundary, stop the sequence
                    if current_parse_mode == crate::parser::ParseMode::Strict
                        || frame.accumulated.is_empty()
                    {
                        // Rollback the checkpoint since we're failing
                        self.rollback_collection_checkpoint(frame.frame_id);
                        stack
                            .results
                            .insert(frame.frame_id, (Node::Empty, element_start, None));
                        return Ok(FrameResult::Done);
                    } else {
                        // Store transparent positions for when this result is used
                        stack
                            .transparent_positions
                            .insert(frame.frame_id, tentatively_collected.clone());
                        // Commit the collection checkpoint - this sequence succeeded
                        self.commit_collection_checkpoint(frame.frame_id);
                        self.pos = current_matched_idx;
                        let result_node = Node::Sequence {
                            children: frame.accumulated.clone(),
                        };
                        stack
                            .results
                            .insert(frame.frame_id, (result_node, current_matched_idx, None));
                        return Ok(FrameResult::Done);
                    }
                }
                // If next_element_optional is true, we DON'T return early.
                // Python parity: skip optional elements at boundary and continue to next element.
                // This matches Python's `continue` behavior at line 215 of sequence.py.
                // The code will naturally continue below to try the next element.
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
                    // Python parity: Pass the TRIMMED max_idx to child frames, not the original.
                    // In GREEDY_ONCE_STARTED mode, after the first match the Sequence trims max_idx
                    // to the next terminator (line 759). This trimmed max_idx should constrain all
                    // subsequent children. Using original_max_idx would allow children to match
                    // beyond terminators, causing issues like FROM being parsed as an identifier
                    // instead of recognized as a terminator for the SELECT clause.
                    let child_frame = ParseFrame::new_child(
                        stack.frame_id_counter,
                        elements_clone[next_elem_idx].clone(),
                        next_pos,
                        frame_terminators.clone(),
                        Some(current_max_idx), // Use trimmed max_idx, not original_max_idx
                    );
                    ParseFrame::push_sequence_child_and_update_parent(
                        stack,
                        &mut frame,
                        child_frame,
                        next_elem_idx,
                    );
                    created_child = true;
                    break;
                }
            }
            if created_child {
                return Ok(FrameResult::Done);
            }

            // Store transparent positions for when this result is used
            // instead of marking them as globally collected immediately.
            let FrameContext::Sequence {
                tentatively_collected: ref mut tc,
                ..
            } = &mut frame.context
            else {
                unreachable!();
            };
            stack
                .transparent_positions
                .insert(frame.frame_id, tc.clone());

            // Commit the collection checkpoint - this sequence succeeded
            self.commit_collection_checkpoint(frame.frame_id);

            // Debug: check if position 15 is in final_accumulated
            let has_pos_15 = final_accumulated.iter().any(|node| match node {
                Node::Whitespace { token_idx, .. } | Node::Newline { token_idx, .. } => {
                    *token_idx == 15
                }
                _ => false,
            });
            log::debug!("Sequence completing: has position 15 in final_accumulated = {}, final_accumulated.len() = {}", has_pos_15, final_accumulated.len());

            self.pos = current_matched_idx;
            // Store result for Combining handler
            frame.accumulated = final_accumulated;
            // Transition to Combining state
            frame.end_pos = Some(current_matched_idx);
            frame.state = FrameState::Combining;
            stack.push(&mut frame);
        }
        Ok(FrameResult::Done)
    }

    /// Handle Sequence grammar Combining state - build final node from accumulated children.
    ///
    /// Called after all children have been collected in waiting_for_child state.
    /// Builds the final Sequence node and transitions to Complete state.
    pub(crate) fn handle_sequence_combining(
        &mut self,
        mut frame: ParseFrame,
        stack: &mut ParseFrameStack,
    ) -> Result<crate::parser::iterative::FrameResult, ParseError> {
        let combine_end = frame.end_pos.unwrap_or(self.pos);
        log::debug!(
            "🔨 Sequence combining frame_id={}, range={}-{}",
            frame.frame_id,
            frame.pos,
            combine_end.saturating_sub(1)
        );

        // Extract context to get tentatively_collected for transparent_positions
        let FrameContext::Sequence {
            tentatively_collected,
            ..
        } = &frame.context
        else {
            return Err(ParseError::new(
                "Expected Sequence context in handle_sequence_combining".to_string(),
            ));
        };

        // Build the final result node from accumulated children
        let result_node = if frame.accumulated.is_empty() {
            log::debug!(
                "WARNING: Sequence completing with EMPTY accumulated! frame_id={}",
                frame.frame_id
            );
            Node::Empty
        } else {
            Node::Sequence {
                children: frame.accumulated.clone(),
            }
        };

        // Store transparent positions for parent to use
        stack
            .transparent_positions
            .insert(frame.frame_id, tentatively_collected.clone());

        // Rollback the collection checkpoint
        self.rollback_collection_checkpoint(frame.frame_id);

        // Get the end position that was stored in the frame
        let final_pos = frame.end_pos.unwrap_or(self.pos);

        // Store transparent positions in frame for Complete handler
        frame.transparent_positions = Some(tentatively_collected.clone());

        log::debug!(
            "Sequence COMPLETE: Storing result at frame_id={}, end_pos={}",
            frame.frame_id,
            final_pos
        );

        // Transition to Complete state
        frame.state = FrameState::Complete(result_node);
        frame.end_pos = Some(final_pos);

        Ok(crate::parser::iterative::FrameResult::Push(frame))
    }

    /// Handle Bracketed grammar Combining state - build final node from accumulated children.
    ///
    /// Called after all children have been collected in waiting_for_child state.
    /// Builds the final Bracketed node and transitions to Complete state.
    pub(crate) fn handle_bracketed_combining(
        &mut self,
        mut frame: ParseFrame,
    ) -> Result<crate::parser::iterative::FrameResult, ParseError> {
        let combine_end = frame.end_pos.unwrap_or(self.pos);
        log::debug!(
            "🔨 Bracketed combining at pos {}-{} - frame_id={}, accumulated={}",
            frame.pos,
            combine_end.saturating_sub(1),
            frame.frame_id,
            frame.accumulated.len()
        );

        // Extract the bracketed state and grammar from the frame context
        let (is_complete, bracket_persists) = if let FrameContext::Bracketed {
            state,
            grammar,
            ..
        } = &frame.context
        {
            let complete = matches!(state, BracketedState::Complete);

            // Determine bracket_persists from the grammar's bracket_pairs
            // Python parity: round brackets persist=True, square/curly persist=False
            let persists = if let Grammar::Bracketed { bracket_pairs, .. } = grammar.as_ref() {
                // bracket_pairs is (Box<Arc<Grammar>>, Box<Arc<Grammar>>)
                // So bracket_pairs.0 is Box<Arc<Grammar>>
                let start_bracket_grammar: &Grammar = &**bracket_pairs.0;

                // Check the bracket type - could be Ref or StringParser
                match start_bracket_grammar {
                    Grammar::Ref { name, .. } => {
                        let is_round = *name == "StartBracketSegment";
                        log::debug!(
                            "Bracketed: start bracket Ref name={}, bracket_persists={}",
                            name,
                            is_round
                        );
                        // Round brackets: "StartBracketSegment" -> persist=True
                        // Square brackets: "StartSquareBracketSegment" -> persist=False
                        // Curly brackets: "StartCurlyBracketSegment" -> persist=False
                        is_round
                    }
                    Grammar::StringParser { template, .. } => {
                        let is_round = *template == "(";
                        log::debug!(
                            "Bracketed: start bracket StringParser template={}, bracket_persists={}",
                            template,
                            is_round
                        );
                        // Round: "(" -> persist=True
                        // Square: "[" -> persist=False
                        // Curly: "{" -> persist=False
                        is_round
                    }
                    Grammar::MultiStringParser { templates, .. } => {
                        let bracket_char = templates.first().copied().unwrap_or("(");
                        let is_round = bracket_char == "(";
                        log::debug!(
                            "Bracketed: start bracket MultiStringParser template={}, bracket_persists={}",
                            bracket_char,
                            is_round
                        );
                        is_round
                    }
                    _ => {
                        log::debug!("Bracketed: start bracket is neither Ref nor StringParser, defaulting to persist=true");
                        // Default to true if we can't determine
                        true
                    }
                }
            } else {
                log::debug!("Bracketed: grammar is not Bracketed, defaulting to persist=true");
                true
            };

            (complete, persists)
        } else {
            (false, true)
        };

        // The result is determined by the bracketed state:
        // - If state is Complete, we successfully matched all parts (open + content + close)
        // - Otherwise, the match failed at some point and we return Empty

        let result_node = if is_complete {
            log::debug!(
                "Bracketed combining with COMPLETE state → building Node::Bracketed, frame_id={}, bracket_persists={}",
                frame.frame_id,
                bracket_persists
            );
            Node::Bracketed {
                children: frame.accumulated.clone(),
                bracket_persists,
            }
        } else {
            log::debug!(
                "Bracketed combining with INCOMPLETE state → returning Node::Empty, frame_id={}",
                frame.frame_id
            );
            Node::Empty
        };

        // Transition to Complete state with the final result
        let end_pos = frame.end_pos.unwrap_or(frame.pos);
        frame.state = FrameState::Complete(result_node);
        frame.end_pos = Some(end_pos);

        Ok(crate::parser::iterative::FrameResult::Push(frame))
    }

    /// Handle Bracketed grammar Initial state in iterative parser.
    ///
    /// ## State Machine:
    /// ```text
    /// Initial
    ///   ↓ (push opening bracket grammar as child)
    /// MatchingOpen
    ///   ↓ (opening bracket matched)
    ///   ├─→ Collect whitespace after opener if allow_gaps
    ///   ├─→ Push Sequence(elements) as child with closing bracket as terminator
    ///   └─→ MatchingContent
    ///   ↓ (opening bracket failed)
    ///   └─→ Terminal (fail with Empty)
    /// MatchingContent
    ///   ↓ (content matched)
    ///   ├─→ Flatten Sequence/DelimitedList children into accumulated
    ///   ├─→ Collect whitespace before closer if allow_gaps
    ///   ├─→ Push closing bracket grammar as child
    ///   └─→ MatchingClose
    ///   ↓ (content failed - STRICT mode)
    ///   └─→ Terminal (fail with Empty for retry)
    ///   ↓ (content failed - GREEDY mode)
    ///   └─→ Continue (may contain unparsable, which is allowed)
    /// MatchingClose
    ///   ↓ (closing bracket matched)
    ///   └─→ Terminal (success with Bracketed node)
    ///   ↓ (closing bracket failed)
    ///   └─→ Terminal (fail with Empty in STRICT, error in GREEDY)
    /// ```
    ///
    /// ## Key Behavior:
    /// - Three-phase matching: opening bracket → content → closing bracket
    /// - Pre-computes matching bracket position during lexing (optimization)
    /// - Content is parsed as Sequence with closing bracket as terminator
    /// - STRICT mode: fails if content doesn't end exactly at closing bracket
    /// - GREEDY mode: allows unparsable content within brackets
    /// - Flattens Sequence/DelimitedList children to avoid double-nesting
    pub(crate) fn handle_bracketed_initial(
        &mut self,
        grammar: Arc<Grammar>,
        mut frame: ParseFrame,
        parent_terminators: &[Arc<Grammar>],
        stack: &mut ParseFrameStack,
    ) -> Result<FrameResult, ParseError> {
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
                panic!("handle_bracketed_initial called with non-Bracketed grammar");
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
        let all_terminators =
            self.combine_terminators(bracket_terminators, parent_terminators, *reset_terminators);

        // Start by trying to match the opening bracket
        // TODO: check if we need to pass terminators here
        initialize_bracketed_frame(&grammar, frame, stack, all_terminators.clone());
        let mut child_frame =
            create_child_frame(stack, &bracket_pairs.0, start_idx, all_terminators.clone());
        update_parent_last_child_frame(stack);
        stack.increment_frame_id_counter();
        stack.push(&mut child_frame);
        Ok(FrameResult::Done) // Child pushed, continue main loop
    }

    /// Handle Bracketed grammar WaitingForChild state in iterative parser
    pub(crate) fn handle_bracketed_waiting_for_child(
        &mut self,
        mut frame: crate::parser::ParseFrame,
        child_node: &crate::parser::Node,
        child_end_pos: &usize,
        stack: &mut crate::parser::iterative::ParseFrameStack,
    ) -> Result<crate::parser::iterative::FrameResult, crate::parser::ParseError> {
        // Extract the context from the frame
        let FrameContext::Bracketed {
            grammar,
            state,
            last_child_frame_id,
            bracket_max_idx,
        } = &mut frame.context
        else {
            panic!("Expected Bracketed context");
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
        } = grammar.as_ref()
        else {
            panic!("Expected Grammar::Bracketed in FrameContext::Bracketed");
        };
        match state {
            BracketedState::MatchingOpen => {
                if child_node.is_empty() {
                    self.pos = frame.pos;
                    log::debug!(
                        "Bracketed returning Empty (no opening bracket, optional={})",
                        optional
                    );
                    // Transition to Combining to finalize Empty result
                    frame.end_pos = Some(frame.pos);
                    frame.state = FrameState::Combining;
                    stack.push(&mut frame);
                    return Ok(crate::parser::iterative::FrameResult::Done);
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

                    // If allow_gaps is false and there's whitespace after opening bracket, fail in STRICT mode
                    if !*allow_gaps && *parse_mode == ParseMode::Strict {
                        // Check if there's any whitespace/newline between opening bracket and next code token
                        let mut check_pos = content_start_idx;
                        while check_pos < self.tokens.len() {
                            if let Some(tok) = self.tokens.get(check_pos) {
                                if tok.is_code() {
                                    break;
                                } else {
                                    // Found whitespace/newline and allow_gaps is false - fail
                                    log::debug!(
                                        "Bracketed: allow_gaps=false, found whitespace/newline at {}, failing in STRICT mode",
                                        check_pos
                                    );
                                    self.pos = frame.pos;
                                    // Transition to Combining to finalize Empty result
                                    frame.end_pos = Some(frame.pos);
                                    frame.state = FrameState::Combining;
                                    stack.push(&mut frame);
                                    return Ok(crate::parser::iterative::FrameResult::Done);
                                }
                            }
                            check_pos += 1;
                        }
                    }

                    if *allow_gaps {
                        let code_idx = self
                            .skip_start_index_forward_to_code(content_start_idx, self.tokens.len());
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
                        end_pos: None,
                        transparent_positions: None,
                        element_key: None,
                    };
                    *last_child_frame_id = Some(stack.frame_id_counter);
                    stack.frame_id_counter += 1;
                    stack.push(&mut frame);
                    stack.push(&mut child_frame);
                    return Ok(FrameResult::Done);
                }
            }
            BracketedState::MatchingContent => {
                log::debug!(
                    "Bracketed MatchingContent - frame_id={}, child_end_pos={}, is_empty={}",
                    frame.frame_id,
                    child_end_pos,
                    child_node.is_empty()
                );
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
                // Python reference: sequence.py Bracketed.match() lines ~530-570
                // In Python, Bracketed doesn't pre-compute the closing bracket position.
                // Instead, it lets Sequence.match() handle the content (which may return
                // unparsable segments in GREEDY mode), then matches the closing bracket.
                // This Rust logic optimizes by pre-computing the bracket position, but
                // must still respect GREEDY mode semantics.
                if let Some(expected_close_pos) = local_bracket_max_idx {
                    log::debug!(
                        "[BRACKET-DEBUG] After skipping ws/nl: check_pos={}, expected_close_pos={}",
                        check_pos,
                        expected_close_pos
                    );
                    if check_pos != expected_close_pos {
                        // Content didn't end exactly at the closing bracket.
                        // In STRICT mode: retry (return Empty)
                        // In GREEDY mode: continue anyway - the content may contain unparsable
                        // segments, which is allowed in GREEDY mode
                        if *parse_mode == ParseMode::Strict {
                            log::debug!("[BRACKET-DEBUG] STRICT mode: Bracketed content did not end at closing bracket, returning Node::Empty for retry. frame_id={}, frame.pos={}", frame.frame_id, frame.pos);
                            self.pos = frame.pos;
                            // Transition to Combining to finalize Empty result
                            frame.end_pos = Some(frame.pos);
                            frame.state = FrameState::Combining;
                            stack.push(&mut frame);
                            return Ok(crate::parser::iterative::FrameResult::Done);
                        } else {
                            log::debug!("[BRACKET-DEBUG] GREEDY mode: Content didn't end at bracket, but continuing (may contain unparsable). check_pos={}, expected_close_pos={}", check_pos, expected_close_pos);
                        }
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
                log::debug!(
                    "DEBUG: After content, gap_start={}, current_pos={}",
                    gap_start,
                    self.pos
                );
                if *allow_gaps {
                    let code_idx =
                        self.skip_start_index_forward_to_code(gap_start, self.tokens.len());
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
                log::debug!(
                    "DEBUG: Checking for closing bracket - self.pos={}, tokens.len={}",
                    self.pos,
                    self.tokens.len()
                );
                if self.pos >= self.tokens.len()
                    || self.peek().is_some_and(|t| t.get_type() == "end_of_file")
                {
                    log::debug!("DEBUG: No closing bracket found!");
                    if *parse_mode == ParseMode::Strict {
                        self.pos = frame.pos;
                        // Transition to Combining to finalize Empty result
                        frame.end_pos = Some(frame.pos);
                        frame.state = FrameState::Combining;
                        stack.push(&mut frame);
                        return Ok(FrameResult::Done);
                    } else {
                        panic!("Couldn't find closing bracket for opening bracket");
                    }
                } else {
                    log::debug!("DEBUG: Transitioning to MatchingClose!");
                    *state = BracketedState::MatchingClose;
                    let parent_limit = frame.parent_max_idx;
                    log::debug!(
                        "DEBUG: Creating closing bracket child at pos={}, parent_limit={:?}",
                        self.pos,
                        parent_limit
                    );
                    let mut child_frame = ParseFrame {
                        frame_id: stack.frame_id_counter,
                        grammar: (*bracket_pairs.1).clone(),
                        pos: self.pos,
                        terminators: vec![(*bracket_pairs.1).clone()],
                        state: FrameState::Initial,
                        accumulated: vec![],
                        context: FrameContext::None,
                        parent_max_idx: parent_limit,
                        end_pos: None,
                        transparent_positions: None,
                        element_key: None,
                    };
                    *last_child_frame_id = Some(stack.frame_id_counter);
                    stack.frame_id_counter += 1;
                    stack.push(&mut frame);
                    stack.push(&mut child_frame);
                    return Ok(FrameResult::Done);
                }
            }
            BracketedState::MatchingClose => {
                log::debug!(
                    "DEBUG: Bracketed MatchingClose - child_node.is_empty={}, child_end_pos={}",
                    child_node.is_empty(),
                    child_end_pos
                );
                let window = 5;
                let start = if self.pos >= window {
                    self.pos - window
                } else {
                    0
                };
                let end = (self.pos + window + 1).min(self.tokens.len());
                for idx in start..end {
                    let t = &self.tokens[idx];
                    log::debug!(
                        "[BRACKET-DEBUG] Token[{}]: type='{}', raw='{}'{}",
                        idx,
                        t.get_type(),
                        t.raw(),
                        if idx == self.pos {
                            " <-- parser pos"
                        } else {
                            ""
                        }
                    );
                }
                if let Some(tok) = self.tokens.get(self.pos) {
                    log::debug!(
                        "[BRACKET-DEBUG] At parser pos {}: type='{}', raw='{}'",
                        self.pos,
                        tok.get_type(),
                        tok.raw()
                    );
                } else {
                    log::debug!(
                        "[BRACKET-DEBUG] At parser pos {}: <out of bounds>",
                        self.pos
                    );
                }
                if child_node.is_empty() {
                    if *parse_mode == ParseMode::Strict {
                        self.pos = frame.pos;
                        // Transition to Combining to finalize Empty result
                        frame.end_pos = Some(frame.pos);
                        frame.state = FrameState::Combining;
                        stack.push(&mut frame);
                        return Ok(FrameResult::Done);
                    } else {
                        // In GREEDY mode, not finding a closing bracket is an error
                        // But we still need to store SOME result so the parent doesn't wait forever
                        log::error!(
                            "Bracketed GREEDY mode: Couldn't find closing bracket for opening bracket at pos {}, frame_id={}",
                            frame.pos,
                            frame.frame_id
                        );
                        self.pos = frame.pos;
                        // Transition to Combining to finalize Empty result
                        frame.end_pos = Some(frame.pos);
                        frame.state = FrameState::Combining;
                        stack.push(&mut frame);
                        return Ok(FrameResult::Done);
                    }
                } else {
                    frame.accumulated.push(child_node.clone());
                    self.pos = *child_end_pos;
                    log::debug!(
                        "Bracketed SUCCESS: {} children, transitioning to Combining at frame_id={}",
                        frame.accumulated.len(),
                        frame.frame_id
                    );
                    // Mark as Complete so the combining handler knows this is a successful match
                    *state = BracketedState::Complete;
                    // Transition to Combining to build final Bracketed node
                    frame.end_pos = Some(*child_end_pos);
                    frame.state = FrameState::Combining;
                    stack.push(&mut frame);
                    return Ok(FrameResult::Done);
                }
            }
            BracketedState::Complete => {
                // This state should never be reached in WaitingForChild handler
                // because we only transition to Complete right before Combining.
                unreachable!(
                    "BracketedState::Complete should not occur in WaitingForChild handler"
                );
            }
        }
    }
}

fn initialize_bracketed_frame(
    grammar: &Arc<Grammar>,
    mut frame: ParseFrame,
    stack: &mut ParseFrameStack,
    all_terminators: Vec<Arc<Grammar>>,
) {
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
    frame.terminators = all_terminators;
    stack.push(&mut frame);
}

fn create_child_frame(
    stack: &mut ParseFrameStack,
    grammar: &Arc<Grammar>,
    start_idx: usize,
    terminators: Vec<Arc<Grammar>>,
) -> ParseFrame {
    ParseFrame {
        frame_id: stack.frame_id_counter,
        grammar: grammar.clone(),
        pos: start_idx,
        terminators,
        state: FrameState::Initial,
        accumulated: vec![],
        context: FrameContext::None,
        parent_max_idx: stack.last_mut().unwrap().parent_max_idx, // Propagate parent's limit!
        end_pos: None,
        transparent_positions: None,
        element_key: None,
    }
}
fn update_parent_last_child_frame(stack: &mut ParseFrameStack) {
    let next_child_id = stack.frame_id_counter;
    if let Some(parent_frame) = stack.last_mut() {
        match &mut parent_frame.context {
            FrameContext::Bracketed {
                last_child_frame_id,
                ..
            } => *last_child_frame_id = Some(next_child_id),
            _ => {
                todo!("implement update_parent_last_child_frame for this grammar type");
            }
        }
    }
}
