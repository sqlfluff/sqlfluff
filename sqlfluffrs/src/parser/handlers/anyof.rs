use std::sync::Arc;

use crate::parser::iterative::{NextStep, ParseFrameStack};
use crate::parser::utils::apply_parse_mode_to_result;
use crate::parser::{FrameContext, FrameState, Node, ParseError, ParseFrame};
use hashbrown::HashSet;
use sqlfluffrs_types::{Grammar, ParseMode};

impl crate::parser::Parser<'_> {
    /// Handle AnySetOf grammar Initial state in iterative parser
    pub fn handle_anysetof_initial(
        &mut self,
        grammar: Arc<Grammar>,
        frame: &mut ParseFrame,
        parent_terminators: &[Arc<Grammar>],
        stack: &mut ParseFrameStack,
    ) -> Result<NextStep, ParseError> {
        log::debug!(
            "START AnySetOf: frame_id={}, pos={}, grammar={:?}",
            frame.frame_id,
            frame.pos,
            grammar
        );
        let pos = frame.pos;
        log::debug!("[ITERATIVE] AnySetOf Initial state at pos {}", pos);

        // Destructure the AnySetOf grammar
        let (
            elements,
            min_times,
            max_times,
            exclude,
            optional,
            local_terminators,
            reset_terminators,
            allow_gaps,
            parse_mode,
        ) = match grammar.as_ref() {
            Grammar::AnySetOf {
                elements,
                min_times,
                max_times,
                exclude,
                optional,
                terminators,
                reset_terminators,
                allow_gaps,
                parse_mode,
                ..
            } => (
                elements,
                *min_times,
                max_times.clone(),
                exclude,
                *optional,
                terminators,
                *reset_terminators,
                *allow_gaps,
                *parse_mode,
            ),
            _ => {
                return Err(ParseError {
                    message: "handle_anysetof_initial called with non-AnySetOf grammar".to_string(),
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

        // Check exclude grammar first
        if let Some(exclude_grammar) = exclude {
            let test_result =
                self.try_match_grammar((**exclude_grammar).clone(), pos, parent_terminators);
            if test_result.is_some() {
                log::debug!(
                    "AnySetOf: exclude grammar matched at pos {}, returning empty",
                    pos
                );
                return Ok(NextStep::Continue);
            }
            log::debug!("exclude grammar missed!")
        }

        let all_terminators: Vec<Arc<Grammar>> = if reset_terminators {
            local_terminators.to_vec()
        } else {
            local_terminators
                .iter()
                .cloned()
                .chain(parent_terminators.iter().cloned())
                .collect()
        };

        self.pos = pos;

        let mut max_idx = if parse_mode == ParseMode::Greedy {
            self.trim_to_terminator(pos, &all_terminators)
        } else {
            self.tokens.len()
        };
        if max_idx > 0 {
            max_idx = self.skip_stop_index_backward_to_code(max_idx, pos);
        }
        if let Some(parent_limit) = frame.parent_max_idx {
            max_idx = max_idx.min(parent_limit);
        }

        log::debug!(
            "[ITERATIVE] AnySetOf max_idx: {} (tokens.len: {})",
            max_idx,
            self.tokens.len()
        );

        frame.state = crate::parser::FrameState::WaitingForChild {
            child_index: 0,
            total_children: max_times.unwrap_or(usize::MAX).min(pruned_options.len()),
        };
        frame.context = FrameContext::AnySetOf {
            grammar: grammar.clone(),
            count: 0,
            matched_idx: pos,
            working_idx: pos,
            matched_elements: HashSet::new(),
            max_idx,
            last_child_frame_id: None,
        };
        frame.terminators = all_terminators.clone();

        stack.push(frame);

        let child_grammar = Arc::new(Grammar::OneOf {
            elements: pruned_options.to_vec(),
            exclude: None,
            optional: false,
            terminators: vec![],
            reset_terminators: false,
            allow_gaps,
            parse_mode,
            simple_hint: None,
        });

        let mut child_frame = crate::parser::ParseFrame {
            frame_id: stack.frame_id_counter,
            grammar: Arc::clone(&child_grammar),
            pos,
            terminators: all_terminators,
            state: crate::parser::FrameState::Initial,
            accumulated: vec![],
            context: FrameContext::None,
            parent_max_idx: Some(max_idx),
        };

        let next_child_id = stack.frame_id_counter;
        if let Some(parent_frame) = stack.last_mut() {
            if let FrameContext::AnySetOf {
                last_child_frame_id,
                ..
            } = &mut parent_frame.context
            {
                last_child_frame_id.replace(next_child_id);
            }
        }

        stack.increment_frame_id_counter();
        stack.push(&mut child_frame);
        Ok(NextStep::Continue)
    }

    pub(crate) fn handle_anysetof_waiting_for_child(
        &mut self,
        frame: &mut ParseFrame,
        child_node: &Node,
        child_end_pos: &usize,
        child_element_key: &Option<u64>,
        stack: &mut ParseFrameStack,
        frame_terminators: Vec<Arc<Grammar>>,
    ) -> Result<(), ParseError> {
        let FrameContext::AnySetOf {
            grammar,
            count,
            matched_idx,
            working_idx,
            matched_elements,
            max_idx,
            ..
        } = &mut frame.context
        else {
            panic!("Expected FrameContext::AnySetOf");
        };
        let Grammar::AnySetOf {
            elements,
            min_times,
            max_times,
            allow_gaps,
            optional,
            parse_mode,
            ..
        } = grammar.as_ref()
        else {
            panic!("Expected Grammar::AnySetOf in FrameContext::AnySetOf");
        };
        // Handle child result
        if child_node.is_empty() {
            // Child match failed
            log::debug!(
                "[ITERATIVE] AnySetOf child failed at position {}",
                frame.pos
            );

            // Check if we've met min_times requirement
            if *count < *min_times {
                if *optional {
                    self.pos = frame.pos;
                    log::debug!("[ITERATIVE] AnySetOf optional, returning Empty");
                    stack
                        .results
                        .insert(frame.frame_id, (Node::Empty, frame.pos, None));
                    return Ok(());
                } else {
                    return Err(ParseError::new(format!(
                        "Expected at least {} occurrences in AnySetOf, found {}",
                        min_times, count
                    )));
                }
            } else {
                // Met min_times, complete with what we have
                log::debug!(
                    "[ITERATIVE] AnySetOf met min_times, completing with {} items",
                    frame.accumulated.len()
                );
                self.pos = *matched_idx;
                let result_node = Node::DelimitedList {
                    children: frame.accumulated.clone(),
                };
                stack
                    .results
                    .insert(frame.frame_id, (result_node, *matched_idx, None));
                return Ok(());
            }
        } else {
            // Child matched successfully!
            log::debug!(
                "[ITERATIVE] AnySetOf child matched: pos {} -> {}",
                frame.pos,
                child_end_pos
            );

            // Collect transparent tokens between matched_idx and working_idx if allow_gaps
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

            // Add matched node
            frame.accumulated.push(child_node.clone());
            *matched_idx = *child_end_pos;
            *working_idx = *matched_idx;
            *count += 1;

            // Extract element_key from OneOf result and add to matched_elements
            let element_key = child_element_key.unwrap_or(0);
            matched_elements.insert(element_key);

            log::debug!(
                                            "[ITERATIVE] AnySetOf matched item #{}, element_key={}, matched_idx now: {}, matched_elements: {:?}",
                                            count, element_key, matched_idx, matched_elements
                                        );

            // Python behavior: Check for complete match (consumed all to max_idx)
            let reached_max = *matched_idx >= *max_idx;

            if reached_max {
                log::debug!(
                    "[ITERATIVE] AnySetOf: Complete match (reached max_idx={}), stopping iteration",
                    max_idx
                );
            }

            // Check termination conditions
            let should_terminate = reached_max
                || (*count >= *min_times
                    && ((max_times.is_some() && *count >= max_times.unwrap())
                        || matched_elements.len() >= elements.len())); // All unique elements matched

            if should_terminate {
                log::debug!(
                                                "[ITERATIVE] AnySetOf terminating: count={}, min_times={}, matched_idx={}, max_idx={}",
                                                count, min_times, matched_idx, max_idx
                                            );
                self.pos = *matched_idx;
                let result_node = Node::DelimitedList {
                    children: frame.accumulated.clone(),
                };
                stack
                    .results
                    .insert(frame.frame_id, (result_node, *matched_idx, None));
                return Ok(());
            } else {
                // Continue - create next child to try remaining elements
                *working_idx = if *allow_gaps {
                    self.skip_start_index_forward_to_code(*working_idx, *max_idx)
                } else {
                    *working_idx
                };

                // Filter out already matched elements by element_key
                let unmatched_elements: Vec<Arc<Grammar>> = elements
                    .iter()
                    .filter(|elem| !matched_elements.contains(&elem.cache_key()))
                    .cloned()
                    .collect();

                log::debug!(
                    "[ITERATIVE] AnySetOf continuing: {} unmatched elements of {} total",
                    unmatched_elements.len(),
                    elements.len()
                );

                if unmatched_elements.is_empty() {
                    // All elements matched - complete
                    log::debug!("[ITERATIVE] AnySetOf: all elements matched, completing");
                    self.pos = *matched_idx;
                    let result_node = Node::DelimitedList {
                        children: frame.accumulated.clone(),
                    };
                    stack
                        .results
                        .insert(frame.frame_id, (result_node, *matched_idx, None));
                    return Ok(());
                } else {
                    // Create OneOf with only unmatched elements
                    let child_grammar = Grammar::OneOf {
                        elements: unmatched_elements,
                        exclude: None,
                        optional: false,
                        terminators: vec![],
                        reset_terminators: false,
                        allow_gaps: *allow_gaps,
                        parse_mode: *parse_mode,
                        simple_hint: None,
                    };

                    // Get parent_max_idx to propagate
                    let parent_limit = frame.parent_max_idx;

                    let child_frame = ParseFrame::new_child(
                        stack.frame_id_counter,
                        child_grammar.into(),
                        *working_idx,
                        frame_terminators.clone(),
                        parent_limit, // Propagate parent's limit!
                    );

                    ParseFrame::push_child_and_update_parent(stack, frame, child_frame, "AnySetOf");
                    // Continue to process the child we just pushed
                    return Ok(());
                }
            }
        }
    }

    /// Handle AnyNumberOf grammar Initial state in iterative parser
    pub fn handle_anynumberof_initial(
        &mut self,
        grammar: Arc<Grammar>,
        frame: &mut ParseFrame,
        parent_terminators: &[Arc<Grammar>],
        stack: &mut ParseFrameStack,
        iteration_count: usize,
    ) -> Result<NextStep, ParseError> {
        log::debug!(
            "START AnyNumberOf: frame_id={}, pos={}, grammar={:?}",
            frame.frame_id,
            frame.pos,
            grammar
        );
        let (
            elements,
            min_times,
            max_times,
            max_times_per_element,
            exclude,
            optional,
            any_terminators,
            reset_terminators,
            allow_gaps,
            parse_mode,
        ) = match grammar.as_ref() {
            Grammar::AnyNumberOf {
                elements,
                min_times,
                max_times,
                max_times_per_element,
                exclude,
                optional,
                terminators: any_terminators,
                reset_terminators,
                allow_gaps,
                parse_mode,
                ..
            } => (
                elements,
                *min_times,
                max_times.clone(),
                max_times_per_element.clone(),
                exclude,
                *optional,
                any_terminators,
                *reset_terminators,
                *allow_gaps,
                *parse_mode,
            ),
            _ => {
                return Err(ParseError {
                    message: "handle_anynumberof_initial called with non-AnyNumberOf grammar"
                        .to_string(),
                });
            }
        };
        let start_idx = frame.pos;
        log::debug!(
            "AnyNumberOf starting at {}, min_times={}, max_times={:?}, allow_gaps={}, parse_mode={:?}",
            start_idx,
            min_times,
            max_times,
            allow_gaps,
            parse_mode
        );

        // Prune options BEFORE any other logic, like Python
        let pruned_options = self.prune_options(elements);
        // If no options remain after pruning, treat as no match
        if pruned_options.is_empty() {
            stack
                .results
                .insert(frame.frame_id, (Node::Empty, start_idx, None));
            return Ok(NextStep::Fallthrough);
        }

        if let Some(exclude_grammar) = exclude {
            let test_result =
                self.try_match_grammar(*exclude_grammar.clone(), start_idx, parent_terminators);
            if test_result.is_some() {
                log::debug!(
                    "AnyNumberOf: exclude grammar matched at pos {}, returning empty",
                    start_idx
                );
                return Ok(NextStep::Continue);
            }
            log::debug!("exclude grammar missed!")
        }

        let all_terminators: Vec<Arc<Grammar>> = if reset_terminators {
            any_terminators.to_vec()
        } else {
            any_terminators
                .iter()
                .cloned()
                .chain(parent_terminators.iter().cloned())
                .collect()
        };

        self.pos = start_idx;

        let mut max_idx = if parse_mode == ParseMode::Greedy {
            self.trim_to_terminator(start_idx, &all_terminators)
        } else {
            self.tokens.len()
        };
        if max_idx > 0 {
            max_idx = self.skip_stop_index_backward_to_code(max_idx, start_idx);
        }
        if let Some(parent_limit) = frame.parent_max_idx {
            max_idx = max_idx.min(parent_limit);
        }

        log::debug!("DEBUG [iter {}]: AnyNumberOf Initial at pos={}, parent_max_idx={:?}, elements.len()={}",
            iteration_count, frame.pos, frame.parent_max_idx, pruned_options.len());

        log::debug!(
            "AnyNumberOf max_idx: {} (tokens.len: {})",
            max_idx,
            self.tokens.len()
        );

        let elements = match self.get_available_grammar_options(&pruned_options, max_idx) {
            Ok(value) => value.into_iter().collect::<Vec<_>>(),
            Err(value) => {
                if let Node::Empty = value {
                    log::debug!("AnyNumberOf: No available options at start, returning Empty");
                    return self.handle_empty_initial(frame, &mut stack.results);
                } else {
                    unreachable!()
                }
            }
        };

        frame.state = crate::parser::FrameState::WaitingForChild {
            child_index: 0,
            total_children: elements.len(),
        };
        frame.context = FrameContext::AnyNumberOf {
            grammar,
            count: 0,
            matched_idx: start_idx,
            working_idx: start_idx,
            option_counter: hashbrown::HashMap::new(),
            max_idx,
            last_child_frame_id: None,
        };
        frame.terminators = all_terminators.clone();

        stack.push(frame);

        if !elements.is_empty() {
            let child_grammar = Arc::new(Grammar::OneOf {
                elements: elements.to_vec(),
                exclude: None,
                optional: true,
                terminators: all_terminators.clone(),
                reset_terminators: false,
                allow_gaps,
                parse_mode,
                simple_hint: None,
            });

            let mut child_frame = crate::parser::ParseFrame {
                frame_id: stack.frame_id_counter,
                grammar: Arc::clone(&child_grammar),
                pos: start_idx,
                terminators: all_terminators,
                state: crate::parser::FrameState::Initial,
                accumulated: vec![],
                context: FrameContext::None,
                parent_max_idx: Some(max_idx),
            };

            let next_child_id = stack.frame_id_counter;
            if let Some(parent_frame) = stack.last_mut() {
                if let FrameContext::AnyNumberOf {
                    last_child_frame_id,
                    ..
                } = &mut parent_frame.context
                {
                    last_child_frame_id.replace(next_child_id);
                }
            }

            stack.increment_frame_id_counter();
            log::debug!("DEBUG [iter {}]: AnyNumberOf Initial pushing child frame_id={}, stack size before push={}",
                iteration_count, child_frame.frame_id, stack.len());
            stack.push(&mut child_frame);
            log::debug!(
                "DEBUG [iter {}]: AnyNumberOf Initial ABOUT TO CONTINUE after pushing child",
                iteration_count
            );
        }
        Ok(NextStep::Continue)
    }

    /// Handle AnyNumberOf grammar WaitingForChild state in iterative parser
    pub(crate) fn handle_anynumberof_waiting_for_child(
        &mut self,
        frame: &mut crate::parser::ParseFrame,
        child_node: &crate::parser::Node,
        child_end_pos: &usize,
        child_element_key: &Option<u64>,
        stack: &mut crate::parser::iterative::ParseFrameStack,
        iteration_count: usize,
        frame_terminators: Vec<std::sync::Arc<crate::parser::Grammar>>,
    ) {
        // Extract the context from the frame
        let FrameContext::AnyNumberOf {
            grammar,
            count,
            matched_idx,
            working_idx,
            option_counter,
            max_idx,
            last_child_frame_id: _last_child_frame_id,
        } = &mut frame.context
        else {
            unreachable!("Expected AnyNumberOf context");
        };

        log::debug!(
            "AnyNumberOf WaitingForChild: count={}, child_node empty={}, matched_idx={}, working_idx={}",
            count, child_node.is_empty(), matched_idx, working_idx
        );
        let Grammar::AnyNumberOf {
            elements,
            min_times,
            max_times,
            max_times_per_element: _,
            exclude: _,
            optional: _,
            terminators: _,
            reset_terminators: _,
            allow_gaps,
            parse_mode,
            ..
        } = grammar.as_ref()
        else {
            unreachable!("Expected AnyNumberOf grammar");
        };

        if !child_node.is_empty() {
            if *allow_gaps && *matched_idx < *working_idx {
                while *matched_idx < *working_idx {
                    if let Some(tok) = self.tokens.get(*matched_idx) {
                        let tok_type = tok.get_type();
                        if tok_type == "whitespace" {
                            frame.accumulated.push(Node::Whitespace {
                                raw: tok.raw().to_string(),
                                token_idx: *matched_idx,
                            });
                        } else if tok_type == "newline" {
                            frame.accumulated.push(Node::Newline {
                                raw: tok.raw().to_string(),
                                token_idx: *matched_idx,
                            });
                        }
                    }
                    *matched_idx += 1;
                }
            }
            frame.accumulated.push(child_node.clone());
            *matched_idx = *child_end_pos;
            *working_idx = *matched_idx;
            *count += 1;
            let element_key = child_element_key.unwrap_or(0);
            *option_counter.entry(element_key).or_insert(0) += 1;
            log::debug!(
                "AnyNumberOf: matched element #{}, element_key={}, matched_idx now: {}",
                count,
                element_key,
                matched_idx
            );
            let reached_max = *matched_idx >= *max_idx;
            if reached_max {
                log::debug!(
                    "AnyNumberOf: Complete match (reached max_idx={}), stopping iteration",
                    max_idx
                );
            }
            let should_continue = !reached_max
                && (*count < *min_times || (max_times.is_none() || *count < max_times.unwrap()));
            if should_continue {
                if *allow_gaps {
                    *working_idx = self.skip_start_index_forward_to_code(*working_idx, *max_idx);
                }
                if !elements.is_empty() {
                    let child_grammar = if elements.len() == 1 {
                        Arc::clone(&elements[0])
                    } else {
                        Arc::new(Grammar::OneOf {
                            elements: elements.clone(),
                            exclude: None,
                            optional: true,
                            terminators: frame_terminators.clone(),
                            reset_terminators: false,
                            allow_gaps: *allow_gaps,
                            parse_mode: *parse_mode,
                            simple_hint: None,
                        })
                    };
                    let child_frame = ParseFrame::new_child(
                        stack.frame_id_counter,
                        child_grammar,
                        *working_idx,
                        frame_terminators.clone(),
                        Some(*max_idx),
                    );
                    ParseFrame::push_child_and_update_parent(
                        stack,
                        frame,
                        child_frame,
                        "AnyNumberOf",
                    );
                    log::debug!(
                        "DEBUG [iter {}]: AnyNumberOf pushed parent and child, stack.len()={}",
                        iteration_count,
                        stack.len()
                    );
                    return;
                }
            } else {
                self.pos = *matched_idx;
                let result_node = Node::DelimitedList {
                    children: frame.accumulated.clone(),
                };
                log::debug!(
                    "AnyNumberOf COMPLETE: {} matches, storing result at frame_id={}",
                    count,
                    frame.frame_id
                );
                stack
                    .results
                    .insert(frame.frame_id, (result_node, *matched_idx, None));
                return;
            }
        } else {
            log::debug!(
                "AnyNumberOf: child failed to match at position {}",
                working_idx
            );
            if *count < *min_times {
                self.pos = frame.pos;
                log::debug!(
                    "AnyNumberOf returning Empty (didn't meet min_times {} < {})",
                    count,
                    min_times
                );
                stack
                    .results
                    .insert(frame.frame_id, (Node::Empty, frame.pos, None));
                return;
            } else {
                self.pos = *matched_idx;
                let result_node = Node::DelimitedList {
                    children: frame.accumulated.clone(),
                };
                log::debug!(
                    "AnyNumberOf COMPLETE (child failed): {} matches, storing result at frame_id={}",
                    count, frame.frame_id
                );
                stack
                    .results
                    .insert(frame.frame_id, (result_node, *matched_idx, None));
                return;
            }
        }
    }

    /// Handle OneOf grammar Initial state in iterative parser
    pub fn handle_oneof_initial(
        &mut self,
        grammar: Arc<Grammar>,
        frame: &mut ParseFrame,
        parent_terminators: &[Arc<Grammar>],
        stack: &mut ParseFrameStack,
    ) -> Result<NextStep, ParseError> {
        log::debug!(
            "START OneOf: frame_id={}, pos={}, grammar={:?}",
            frame.frame_id,
            frame.pos,
            grammar
        );
        // Destructure Grammar::OneOf fields
        let (
            elements,
            exclude,
            optional,
            local_terminators,
            reset_terminators,
            allow_gaps,
            parse_mode,
        ) = match grammar.as_ref() {
            Grammar::OneOf {
                elements,
                exclude,
                optional,
                terminators: local_terminators,
                reset_terminators,
                allow_gaps,
                parse_mode,
                ..
            } => (
                elements,
                exclude,
                *optional,
                local_terminators,
                *reset_terminators,
                *allow_gaps,
                *parse_mode,
            ),
            _ => panic!("handle_oneof_initial called with non-OneOf grammar"),
        };
        let pos = frame.pos;

        // Prune options BEFORE any other logic, like Python
        let pruned_options = self.prune_options(elements);
        // If no options remain after pruning, treat as no match
        if pruned_options.is_empty() {
            stack
                .results
                .insert(frame.frame_id, (Node::Empty, pos, None));
            return Ok(NextStep::Fallthrough);
        }

        if let Some(exclude_grammar) = exclude {
            let test_result =
                self.try_match_grammar(*exclude_grammar.clone(), pos, parent_terminators);
            if test_result.is_some() {
                stack
                    .results
                    .insert(frame.frame_id, (Node::Empty, pos, None));
                return Ok(NextStep::Fallthrough);
            }
            log::debug!("exclude grammar missed!")
        }

        let leading_ws = if allow_gaps {
            self.collect_transparent(true)
        } else {
            Vec::new()
        };
        let mut post_skip_pos = self.pos;

        let all_terminators: Vec<Arc<Grammar>> = if reset_terminators {
            local_terminators.to_vec()
        } else {
            local_terminators
                .iter()
                .chain(parent_terminators.iter())
                .cloned()
                .collect()
        };

        let mut max_idx = if parse_mode == ParseMode::Greedy {
            self.trim_to_terminator(post_skip_pos, &all_terminators)
        } else {
            self.tokens.len()
        };
        if max_idx > 0 {
            max_idx = self.skip_stop_index_backward_to_code(max_idx, post_skip_pos);
        }
        if let Some(parent_limit) = frame.parent_max_idx {
            max_idx = max_idx.min(parent_limit);
        }

        if self.is_terminated(&all_terminators) {
            self.pos = pos;

            let result = if optional {
                Node::Empty
            } else {
                crate::parser::utils::apply_parse_mode_to_result(
                    self.tokens,
                    Node::Empty,
                    pos,
                    max_idx,
                    parse_mode,
                )
            };

            let final_pos = if matches!(result, Node::Empty) {
                pos
            } else {
                max_idx
            };
            self.pos = final_pos;
            stack
                .results
                .insert(frame.frame_id, (result, final_pos, None));
            return Ok(NextStep::Fallthrough);
        }

        let available_options: Vec<Arc<Grammar>> =
            self.prune_options(&elements).into_iter().collect();

        if available_options.is_empty() {
            // log::debug!("OneOf: No viable options after pruning");
            self.pos = pos;

            let result = if optional {
                Node::Empty
            } else {
                crate::parser::utils::apply_parse_mode_to_result(
                    self.tokens,
                    Node::Empty,
                    pos,
                    max_idx,
                    parse_mode,
                )
            };

            let final_pos = if matches!(result, Node::Empty) {
                pos
            } else {
                max_idx
            };
            self.pos = final_pos;
            stack
                .results
                .insert(frame.frame_id, (result, final_pos, None));
            return Ok(NextStep::Fallthrough);
        }

        frame.context = FrameContext::OneOf {
            grammar,
            leading_ws: leading_ws.clone(),
            post_skip_pos,
            longest_match: None,
            tried_elements: 0,
            max_idx,
            last_child_frame_id: Some(stack.frame_id_counter),
        };

        let first_element = available_options[0].clone();
        let element_key = first_element.cache_key();

        if matches!(*first_element, Grammar::Nothing() | Grammar::Empty) {
            // log::debug!(
            //     "OneOf: First element is Nothing, handling inline (element_key={})",
            //     element_key
            // );
            frame.context = if let FrameContext::OneOf {
                grammar,
                leading_ws,
                post_skip_pos,
                longest_match: _,
                tried_elements,
                max_idx,
                last_child_frame_id: _,
            } = &frame.context
            {
                FrameContext::OneOf {
                    grammar: grammar.clone(),
                    leading_ws: leading_ws.clone(),
                    post_skip_pos: *post_skip_pos,
                    longest_match: Some((Node::Empty, 0, element_key)),
                    tried_elements: *tried_elements + 1,
                    max_idx: *max_idx,
                    last_child_frame_id: None,
                }
            } else {
                unreachable!()
            };
            frame.state = crate::parser::FrameState::WaitingForChild {
                child_index: 0,
                total_children: 1,
            };
            stack.push(frame);
            return Ok(NextStep::Continue);
        }
        log::debug!("OneOf: Trying first element (cache_key: {})", element_key);

        let mut child_frame = crate::parser::ParseFrame {
            frame_id: stack.frame_id_counter,
            grammar: Arc::clone(&first_element),
            pos: post_skip_pos,
            terminators: all_terminators.clone(),
            state: crate::parser::FrameState::Initial,
            accumulated: Vec::new(),
            context: FrameContext::None,
            parent_max_idx: Some(max_idx),
        };

        frame.state = crate::parser::FrameState::WaitingForChild {
            child_index: 0,
            total_children: 1,
        };

        stack.increment_frame_id_counter();
        stack.push(frame);
        stack.push(&mut child_frame);
        Ok(NextStep::Continue)
    }

    pub(crate) fn handle_oneof_waiting_for_child(
        &mut self,
        frame: &mut ParseFrame,
        child_node: &Node,
        child_end_pos: &usize,
        child_element_key: &Option<u64>,
        stack: &mut ParseFrameStack,
        frame_terminators: Vec<Arc<Grammar>>,
    ) {
        let FrameContext::OneOf {
            grammar,
            leading_ws,
            post_skip_pos,
            longest_match,
            tried_elements,
            max_idx,
            last_child_frame_id: _,
        } = &mut frame.context
        else {
            unreachable!("Expected OneOf context");
        };

        let Grammar::OneOf {
            elements,
            optional,
            parse_mode,
            ..
        } = grammar.as_ref()
        else {
            panic!("Expected Grammar::OneOf in FrameContext::OneOf");
        };

        let consumed = *child_end_pos - *post_skip_pos;
        let element_key = if *tried_elements < elements.len() {
            elements[*tried_elements].cache_key()
        } else {
            0
        };

        if !child_node.is_empty() {
            let is_better = longest_match.is_none() || consumed > longest_match.as_ref().unwrap().1;
            if is_better {
                *longest_match = Some((child_node.clone(), consumed, element_key));
            }
            if *child_end_pos >= *max_idx {
                *tried_elements = elements.len();
            }
        }
        *tried_elements += 1;

        if *tried_elements < elements.len() {
            self.pos = *post_skip_pos;
            let next_element = elements[*tried_elements].clone();
            let child_frame = ParseFrame::new_child(
                stack.frame_id_counter,
                next_element,
                *post_skip_pos,
                frame.terminators.clone(),
                Some(*max_idx),
            );
            frame.state = FrameState::WaitingForChild {
                child_index: 0,
                total_children: 1,
            };
            ParseFrame::push_child_and_update_parent(stack, frame, child_frame, "OneOf");
            return;
        } else {
            if let Some((best_node, best_consumed, best_element_key)) = longest_match {
                self.pos = *post_skip_pos + *best_consumed;
                let result = if !leading_ws.is_empty() {
                    let mut children = leading_ws.clone();
                    children.push(best_node.clone());
                    Node::Sequence { children }
                } else {
                    best_node.clone()
                };
                stack
                    .results
                    .insert(frame.frame_id, (result, self.pos, Some(*best_element_key)));
                return;
            } else {
                let result_node = apply_parse_mode_to_result(
                    self.tokens,
                    Node::Empty,
                    frame.pos,
                    *max_idx,
                    *parse_mode,
                );
                let final_pos = if matches!(result_node, Node::Empty) {
                    frame.pos
                } else {
                    *max_idx
                };
                self.pos = final_pos;
                stack
                    .results
                    .insert(frame.frame_id, (result_node, final_pos, None));
                return;
            }
        }
    }

    // Helper methods
    /// Try to match a grammar at a specific position without consuming tokens
    /// Returns Some(end_pos) if the grammar matches, None otherwise
    ///
    /// This uses the same parsing logic as the main parser but in a non-destructive way,
    /// similar to how terminators are checked.
    pub(crate) fn try_match_grammar(
        &mut self,
        grammar: Arc<Grammar>,
        pos: usize,
        terminators: &[Arc<Grammar>],
    ) -> Option<usize> {
        // Save current state
        let saved_pos = self.pos;

        // Try to parse the grammar using parse_with_grammar_cached
        // This will temporarily move the parser position but we'll restore it
        self.pos = pos;

        let result = self.parse_with_grammar_cached(grammar, terminators);

        // Get the end position before restoring
        let end_pos = self.pos;

        // Restore position regardless of match success
        self.pos = saved_pos;

        // If the grammar matched, return the end position
        match result {
            Ok(node) => {
                // Only consider it a match if we actually consumed something meaningful (not just whitespace)
                if end_pos > pos && !matches!(node, Node::Empty) {
                    Some(end_pos)
                } else {
                    None
                }
            }
            Err(_) => None,
        }
    }
}
