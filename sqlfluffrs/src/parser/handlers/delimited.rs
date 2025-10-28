use std::sync::Arc;

use crate::parser::{Node, ParseError, ParseFrame};
use crate::parser::iterative::{NextStep, ParseFrameStack};
use crate::parser::{FrameState, FrameContext};
use crate::parser::DelimitedState;
use sqlfluffrs_types::{Grammar, ParseMode};

impl crate::parser::Parser<'_> {
    /// Handle Delimited grammar Initial state in iterative parser
    /// Returns true if caller should continue main loop
    pub fn handle_delimited_initial(
        &mut self,
        grammar: Arc<Grammar>,
        frame: &mut ParseFrame,
        parent_terminators: &[Arc<Grammar>],
        stack: &mut ParseFrameStack,
    ) -> Result<NextStep, ParseError> {
        let pos = frame.pos;
        log::debug!("[ITERATIVE] Delimited Initial state at pos {}", pos);

        // Destructure the Delimited grammar
        let (
            elements,
            delimiter,
            allow_trailing,
            optional,
            local_terminators,
            reset_terminators,
            allow_gaps,
            min_delimiters,
            parse_mode,
        ) = match grammar.as_ref() {
            Grammar::Delimited {
                elements,
                delimiter,
                allow_trailing,
                optional,
                terminators,
                reset_terminators,
                allow_gaps,
                min_delimiters,
                parse_mode,
                ..
            } => (
                elements,
                delimiter,
                *allow_trailing,
                *optional,
                terminators,
                *reset_terminators,
                *allow_gaps,
                *min_delimiters,
                *parse_mode,
            ),
            _ => {
                return Err(ParseError {
                    message: "handle_delimited_initial called with non-Delimited grammar".to_string(),
                });
            }
        };

        // Prune options BEFORE any other logic, like Python
        let pruned_options = self.prune_options(elements);
        // If no options remain after pruning, treat as no match
        if pruned_options.is_empty() {
            stack
                .results
                .insert(frame.frame_id, (Node::Empty, pos, None));
            return Ok(NextStep::Fallthrough);
        }

        // Combine terminators, filtering out delimiter from parent terminators
        // This is critical - delimiter shouldn't terminate the delimited list itself
        let filtered_parent: Vec<Arc<Grammar>> = parent_terminators
            .iter()
            .filter(|t| *t != delimiter.as_ref())
            .cloned()
            .collect();

        let all_terminators: Vec<Arc<Grammar>> = if reset_terminators {
            local_terminators.to_vec()
        } else {
            local_terminators
                .iter()
                .cloned()
                .chain(filtered_parent)
                .collect()
        };

        // Calculate max_idx based on parse_mode and terminators
        self.pos = pos;
        let max_idx = if parse_mode == ParseMode::Greedy {
            // In GREEDY mode, actively look for terminators
            self.trim_to_terminator(pos, &all_terminators)
        } else {
            // In STRICT mode, still need to respect terminators if they exist
            // Check if there's a terminator anywhere ahead
            if all_terminators.is_empty() {
                self.tokens.len()
            } else {
                self.trim_to_terminator(pos, &all_terminators)
            }
        };

        // Apply parent's max_idx limit (simulates Python's segments[:max_idx])
        let max_idx = if let Some(parent_limit) = frame.parent_max_idx {
            max_idx.min(parent_limit)
        } else {
            max_idx
        };

        log::debug!(
            "[ITERATIVE] Delimited max_idx: {} (tokens.len: {}), parse_mode={:?}, terminators.len={}",
            max_idx,
            self.tokens.len(),
            parse_mode,
            all_terminators.len()
        );

        // Check if optional and already terminated
        if optional && (self.is_at_end() || self.is_terminated(&all_terminators)) {
            log::debug!("[ITERATIVE] Delimited: empty optional");
            stack
                .results
                .insert(frame.frame_id, (Node::DelimitedList { children: vec![] }, pos, None));
            return Ok(NextStep::Fallthrough); // Don't continue, we stored a result
        }

        // Create Delimited context
        frame.state = FrameState::WaitingForChild {
            child_index: 0,
            total_children: usize::MAX, // Unknown number of children
        };
        frame.context = FrameContext::Delimited {
            grammar: grammar.clone(),
            delimiter_count: 0,
            matched_idx: pos,
            working_idx: pos,
            max_idx,
            state: DelimitedState::MatchingElement,
            last_child_frame_id: None,
        };
        frame.terminators = all_terminators.clone();

        // Extract max_idx before moving frame - this is the limit for children!
        // Children should be constrained by the Delimited's calculated max_idx
        let child_max_idx = max_idx;
        stack.push(frame);

        // Create first child to match element (try all elements via OneOf)
        let child_grammar = Grammar::OneOf {
            elements: pruned_options.to_vec(),
            exclude: None,
            optional: true, // Elements in Delimited are implicitly optional
            terminators: vec![],
            reset_terminators: false,
            allow_gaps,
            parse_mode,
            simple_hint: None,
        };

        let mut child_frame = ParseFrame::new_child(
            stack.frame_id_counter,
            child_grammar.into(),
            pos,
            all_terminators,
            Some(child_max_idx), // Use Delimited's max_idx!
        );

        // Update parent's last_child_frame_id and push child
        ParseFrame::update_parent_last_child_id(stack, "Delimited", stack.frame_id_counter);
        stack.increment_frame_id_counter();
        stack.push(&mut child_frame);
        Ok(NextStep::Continue) // Continue to process the child frame we just pushed
    }

    pub(crate) fn handle_delimited_waiting_for_child(
        &mut self,
        frame: &mut ParseFrame,
        child_node: &Node,
        child_end_pos: &usize,
        child_element_key: &Option<u64>,
        stack: &mut ParseFrameStack,
        frame_terminators: Vec<Arc<Grammar>>,
    ) {
        let FrameContext::Delimited {
            grammar,
            delimiter_count,
            matched_idx,
            working_idx,
            max_idx,
            state,
            last_child_frame_id: _,
        } = &mut frame.context else {
            unreachable!("Expected Delimited context");
        };
        let Grammar::Delimited {
            elements,
            delimiter,
            min_delimiters,
            allow_trailing,
            allow_gaps,
            optional,
            parse_mode,
            ..
        } = grammar.as_ref() else {
            panic!("Expected Grammar::Delimited in FrameContext::Delimited");
        };
        log::debug!("[ITERATIVE] Delimited WaitingForChild: state={:?}, delimiter_count={}, child_node is_empty={}", state, delimiter_count, child_node.is_empty());
        match state {
            DelimitedState::MatchingElement => {
                if child_node.is_empty() {
                    log::debug!("[ITERATIVE] Delimited: no element matched at position {}", frame.pos);
                    log::debug!("[ITERATIVE] Delimited completing with {} items", frame.accumulated.len());
                    self.pos = *matched_idx;
                    stack.results.insert(
                        frame.frame_id,
                        (Node::DelimitedList { children: frame.accumulated.clone() }, *matched_idx, None),
                    );
                    return;
                } else {
                    log::debug!("[ITERATIVE] Delimited element matched: pos {} -> {}", frame.pos, child_end_pos);
                    if *allow_gaps {
                        for check_pos in *matched_idx..*working_idx {
                            if check_pos < self.tokens.len()
                                && !self.tokens[check_pos].is_code()
                                && !self.collected_transparent_positions.contains(&check_pos)
                            {
                                let tok = &self.tokens[check_pos];
                                let tok_type = tok.get_type();
                                if tok_type == "whitespace" {
                                    frame.accumulated.push(Node::Whitespace {
                                        raw: tok.raw().to_string(),
                                        token_idx: check_pos,
                                    });
                                    self.collected_transparent_positions.insert(check_pos);
                                } else if tok_type == "newline" {
                                    frame.accumulated.push(Node::Newline {
                                        raw: tok.raw().to_string(),
                                        token_idx: check_pos,
                                    });
                                    self.collected_transparent_positions.insert(check_pos);
                                }
                            }
                        }
                    }
                    frame.accumulated.push(child_node.clone());
                    *matched_idx = *child_end_pos;
                    *working_idx = *matched_idx;
                    if *allow_gaps {
                        *working_idx = self.skip_start_index_forward_to_code(*working_idx, *max_idx);
                    }
                    self.pos = *working_idx;
                    if self.is_at_end() || self.is_terminated(&frame_terminators) {
                        log::debug!("[ITERATIVE] Delimited: at EOF or terminator after element, completing at position {}", matched_idx);
                        self.pos = *matched_idx;
                        stack.results.insert(
                            frame.frame_id,
                            (Node::DelimitedList { children: frame.accumulated.clone() }, *matched_idx, None),
                        );
                        return;
                    } else {
                        *state = DelimitedState::MatchingDelimiter;
                        let child_max_idx = *max_idx;
                        let child_frame = ParseFrame::new_child(
                            stack.frame_id_counter,
                            (**delimiter).clone(),
                            *working_idx,
                            frame_terminators.clone(),
                            Some(child_max_idx),
                        );
                        ParseFrame::push_child_and_update_parent(
                            stack,
                            frame,
                            child_frame,
                            "Delimited",
                        );
                        return;
                    }
                }
            }
            DelimitedState::MatchingDelimiter => {
                if child_node.is_empty() {
                    log::debug!("[ITERATIVE] Delimited: no delimiter found, completing at position {}", matched_idx);
                    if *delimiter_count < *min_delimiters {
                        if *optional {
                            self.pos = frame.pos;
                            stack.results.insert(
                                frame.frame_id,
                                (Node::DelimitedList { children: frame.accumulated.clone() }, frame.pos, None),
                            );
                        } else {
                            panic!("Expected at least {} delimiters, found {}", min_delimiters, delimiter_count);
                        }
                    } else {
                        self.pos = *matched_idx;
                        stack.results.insert(
                            frame.frame_id,
                            (Node::DelimitedList { children: frame.accumulated.clone() }, *matched_idx, None),
                        );
                    }
                    return;
                } else {
                    log::debug!("[ITERATIVE] Delimited delimiter matched: pos {} -> {}", working_idx, child_end_pos);
                    if *allow_gaps {
                        for check_pos in *matched_idx..*working_idx {
                            if check_pos < self.tokens.len()
                                && !self.tokens[check_pos].is_code()
                                && !self.collected_transparent_positions.contains(&check_pos)
                            {
                                let tok = &self.tokens[check_pos];
                                let tok_type = tok.get_type();
                                if tok_type == "whitespace" {
                                    frame.accumulated.push(Node::Whitespace {
                                        raw: tok.raw().to_string(),
                                        token_idx: check_pos,
                                    });
                                    self.collected_transparent_positions.insert(check_pos);
                                } else if tok_type == "newline" {
                                    frame.accumulated.push(Node::Newline {
                                        raw: tok.raw().to_string(),
                                        token_idx: check_pos,
                                    });
                                    self.collected_transparent_positions.insert(check_pos);
                                }
                            }
                        }
                    }
                    frame.accumulated.push(child_node.clone());
                    *matched_idx = *child_end_pos;
                    *working_idx = *matched_idx;
                    *delimiter_count += 1;
                    self.pos = *matched_idx;
                    if self.is_terminated(&frame_terminators) {
                        log::debug!("[ITERATIVE] Delimited: terminated after delimiter");
                        if !*allow_trailing {
                            panic!("Trailing delimiter not allowed");
                        }
                        stack.results.insert(
                            frame.frame_id,
                            (Node::DelimitedList { children: frame.accumulated.clone() }, *matched_idx, None),
                        );
                        return;
                    } else {
                        *state = DelimitedState::MatchingElement;
                        if *allow_gaps {
                            *working_idx = self.skip_start_index_forward_to_code(*working_idx, *max_idx);
                        }
                        self.pos = *working_idx;
                        if self.is_at_end() || self.is_terminated(&frame_terminators) {
                            log::debug!("[ITERATIVE] Delimited: at terminator/EOF before next element, completing");
                            self.pos = *matched_idx;
                            stack.results.insert(
                                frame.frame_id,
                                (Node::DelimitedList { children: frame.accumulated.clone() }, *matched_idx, None),
                            );
                            return;
                        }
                        let child_max_idx = *max_idx;
                        let child_grammar = Grammar::OneOf {
                            elements: elements.clone(),
                            exclude: None,
                            optional: true,
                            terminators: vec![],
                            reset_terminators: false,
                            allow_gaps: *allow_gaps,
                            parse_mode: *parse_mode,
                            simple_hint: None,
                        };
                        let child_frame = ParseFrame::new_child(
                            stack.frame_id_counter,
                            child_grammar.into(),
                            *working_idx,
                            frame_terminators.clone(),
                            Some(child_max_idx),
                        );
                        ParseFrame::push_child_and_update_parent(
                            stack,
                            frame,
                            child_frame,
                            "Delimited",
                        );
                        return;
                    }
                }
            }
        }
    }
}
