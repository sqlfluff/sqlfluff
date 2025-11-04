use std::sync::Arc;

use crate::parser::iterative::{NextStep, ParseFrameStack};
use crate::parser::utils::{apply_parse_mode_to_result, skip_start_index_forward_to_code};
use crate::parser::{FrameContext, FrameState, Node, ParseError, ParseFrame};
use sqlfluffrs_types::{Grammar, ParseMode};

type ResultType = (Node, usize, Option<u64>);

impl crate::parser::Parser<'_> {
    /// Handle AnyNumberOf grammar Initial state in iterative parser.
    ///
    /// ## State Machine:
    /// ```text
    /// Initial
    ///   ↓ (prune options, check exclude)
    ///   ↓ (push OneOf child with optional=true)
    /// WaitingForChild
    ///   ↓ (child matched)
    ///   ├─→ Terminal: count >= min_times AND (count >= max_times OR reached max_idx)
    ///   ├─→ Continue: create new OneOf with same elements, go back to WaitingForChild
    ///   ↓ (child failed)
    ///   ├─→ Terminal: count >= min_times (success with what we have)
    ///   └─→ Terminal: count < min_times (fail with Empty)
    /// ```
    ///
    /// ## Key Behavior:
    /// - Matches elements in any order, allowing unlimited duplicates (subject to max_times)
    /// - Unlike AnySetOf, does NOT filter out matched elements (can repeat indefinitely)
    /// - Tracks per-element counts via option_counter (for max_times_per_element)
    /// - Terminates when min/max requirements met OR child match fails
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
                max_times,
                max_times_per_element,
                exclude,
                *optional,
                any_terminators,
                *reset_terminators,
                *allow_gaps,
                *parse_mode,
            ),
            _ => {
                return Err(ParseError::with_context(
                    "handle_anynumberof_initial called with non-AnyNumberOf grammar".to_string(),
                    Some(self.pos),
                    Some(grammar),
                ));
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

        // Python parity: Check exclude grammar first, before any other logic
        if let Some(exclude_grammar) = exclude {
            let test_result =
                self.try_match_grammar(*exclude_grammar.clone(), start_idx, parent_terminators);
            if test_result.is_ok() {
                log::debug!(
                    "AnyNumberOf: exclude grammar matched at pos {}, returning Empty",
                    start_idx
                );
                stack
                    .results
                    .insert(frame.frame_id, (Node::Empty, start_idx, None));
                return Ok(NextStep::Continue);
            }
            log::debug!("AnyNumberOf: exclude grammar did not match, continuing");
        }

        let option_counter: hashbrown::HashMap<u64, usize> =
            elements.iter().map(|elem| (elem.cache_key(), 0)).collect();
        let matched: ResultType = (Node::Empty, start_idx, None);
        let max_idx = self.tokens.len();

        // Combine parent and local terminators
        let all_terminators =
            self.combine_terminators(any_terminators, parent_terminators, reset_terminators);


        // If we are in greedy mode, calculate max_idx with terminators (Python parity)
        // This must happen before we push the child frame, so we don't overrun terminators.
        let mut max_idx = max_idx;
        if parse_mode == ParseMode::Greedy {
            // In GREEDY mode, trim max_idx to the first terminator (if any)
            // Use all_terminators, which already combines local and parent terminators
            max_idx = self.trim_to_terminator(start_idx, &all_terminators);
        }

        // Here we have 0 matches, so if min_times is 0 and we're at max_idx,
        // or we've hit max times we want to return the results from
        if min_times == 0 && start_idx >= max_idx {
            log::debug!(
                "AnyNumberOf: start_idx ({}) >= max_idx ({}), min_times={}",
                start_idx,
                max_idx,
                min_times
            );
            if let Some(value) = self.parse_mode_match_result(
                frame, stack, parse_mode, start_idx, max_idx, matched,
            ) {
                return value;
            }
        }

        // if our pos is already at or past max_idx, return Empty match
        if start_idx >= max_idx {
            log::debug!(
            "AnyNumberOf: start_idx ({}) >= max_idx ({}), returning Empty",
            start_idx,
            max_idx
            );
            stack
            .results
            .insert(frame.frame_id, (Node::Empty, start_idx, None));
            return Ok(NextStep::Continue);
        }

        // Prune options BEFORE any other logic, like Python
        let pruned_options = self.prune_options(elements);
        // If no options remain after pruning, treat as no match
        if pruned_options.is_empty() {
            stack
                .results
                .insert(frame.frame_id, (Node::Empty, start_idx, None));
            return Ok(NextStep::Fallthrough);
        }

        // Calculate max_idx with terminator and parent constraints
        // AnyNumberOf uses trim_to_terminator_with_elements to avoid over-eager termination
        self.pos = start_idx;
        let max_idx = self.calculate_max_idx_with_elements(
            start_idx,
            &all_terminators,
            &pruned_options,
            parse_mode,
            frame.parent_max_idx,
        );

        log::debug!("DEBUG [iter {}]: AnyNumberOf Initial at pos={}, parent_max_idx={:?}, elements.len()={}",
            iteration_count, frame.pos, frame.parent_max_idx, pruned_options.len());

        log::debug!(
            "AnyNumberOf max_idx: {} (tokens.len: {})",
            max_idx,
            self.tokens.len()
        );

        // Check if any options are available (for error handling)
        let available_check = match self.get_available_grammar_options(&pruned_options, max_idx) {
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

        // IMPORTANT: Use ORIGINAL elements for all OneOf children, not filtered!
        // This ensures consistent element_keys across all iterations.
        // The pruning above is just for validation; actual matching is controlled
        // by max_times_per_element (for AnySetOf behavior via delegation).
        let elements_for_oneof = elements.clone();

        frame.state = crate::parser::FrameState::WaitingForChild {
            child_index: 0,
            total_children: available_check.len(),
        };
        frame.context = FrameContext::AnyNumberOf {
            grammar,
            count: 0,
            matched_idx: start_idx,
            working_idx: start_idx,
            option_counter,
            max_idx,
            last_child_frame_id: None,
        };
        frame.terminators = all_terminators.clone();

        stack.push(frame);

        if !elements_for_oneof.is_empty() {
            log::debug!(
                "AnyNumberOf creating initial OneOf with {} elements, option_counter is empty",
                elements_for_oneof.len()
            );
            let child_grammar = Arc::new(Grammar::OneOf {
                elements: elements_for_oneof.to_vec(),
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

    fn parse_mode_match_result(
        &mut self,
        frame: &mut ParseFrame,
        stack: &mut ParseFrameStack,
        parse_mode: ParseMode,
        start_idx: usize,
        max_idx: usize,
        current_match: ResultType,
    ) -> Option<Result<NextStep, ParseError>> {
        // Rust implementation of _parse_mode_match_result logic:
        log::debug!(
            "parse_mode_match_result: start_idx ({}) >= max_idx ({})",
            start_idx,
            max_idx,
        );
        // If we're being strict, just current match.
        if parse_mode == ParseMode::Strict {
            stack.results.insert(frame.frame_id, current_match);
            return Some(Ok(NextStep::Continue));
        }

        // If nothing unmatched anyway?
        // In Rust, tokens are self.tokens, and we want to check if all tokens from start_idx to max_idx are not code.
        let all_non_code = self.tokens[start_idx..max_idx]
            .iter()
            .all(|tok| !tok.is_code());

        if start_idx == max_idx || all_non_code {
            stack.results.insert(frame.frame_id, current_match);
            return Some(Ok(NextStep::Continue));
        }

        // Find the first code token after start_idx
        let mut trim_idx = self.skip_start_index_forward_to_code(start_idx, max_idx);
        while trim_idx < max_idx && !self.tokens[trim_idx].is_code() {
            trim_idx += 1;
        }

        // Create an unmatched segment (Unparsable)
        let mut expected = "Nothing else".to_string();
        if self.tokens.len() > max_idx {
            expected += &format!(" before {:?}", self.tokens[max_idx].raw());
        }

        let unmatched_node = Node::Unparsable {
            children: self.tokens[trim_idx..max_idx]
                .iter()
                .enumerate()
                .map(|(idx, tok)| Node::Token {
                    token_type: tok.token_type.clone(),
                    raw: tok.raw().to_string(),
                    token_idx: trim_idx + idx,
                })
                .collect(),
            expected_message: expected,
        };

        // Append the unmatched_node to the current_match, as in Python (_parse_mode_match_result)
        let (mut node, _, _) = current_match;
        let result_node = match node {
            Node::Sequence { ref mut children } => {
                children.push(unmatched_node);
                node
            }
            Node::Empty => Node::Sequence {
                children: vec![Node::Empty, unmatched_node],
            },
            _ => Node::Sequence {
                children: vec![node, unmatched_node],
            },
        };

        stack
            .results
            .insert(frame.frame_id, (result_node, max_idx, None));
        return Some(Ok(NextStep::Continue));
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
            max_times_per_element,
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

            // Save previous matched_idx before updating (needed for max_times_per_element rollback)
            let previous_matched_idx = *matched_idx;
            *matched_idx = *child_end_pos;
            *working_idx = *matched_idx;
            *count += 1;
            let element_key = child_element_key.unwrap_or(0);
            log::debug!(
                "AnyNumberOf received match: element_key={}, count before increment={}, child_element_key={:?}",
                element_key,
                option_counter.get(&element_key).copied().unwrap_or(0),
                child_element_key
            );
            *option_counter.entry(element_key).or_insert(0) += 1;

            // Check max_times_per_element constraint
            // Python: increments counter, checks > max, returns BEFORE appending
            // We: already appended, so must remove if exceeded
            if let Some(max_per_elem) = max_times_per_element {
                if let Some(elem_count) = option_counter.get(&element_key) {
                    if *elem_count > *max_per_elem {
                        // Exceeded max_times_per_element for this specific element
                        log::debug!(
                            "AnyNumberOf: element_key={} exceeded max_times_per_element={} (count={}), stopping",
                            element_key, max_per_elem, elem_count
                        );

                        // Remove the element that exceeded the limit (to match Python)
                        frame.accumulated.pop();
                        *count -= 1;
                        *matched_idx = previous_matched_idx;

                        // Check if we met min_times without the excess element
                        if *count >= *min_times {
                            self.pos = *matched_idx;
                            let result_node = Node::DelimitedList {
                                children: frame.accumulated.clone(),
                            };
                            log::debug!(
                                "AnyNumberOf COMPLETE (max_times_per_element): {} matches",
                                count
                            );
                            stack
                                .results
                                .insert(frame.frame_id, (result_node, *matched_idx, None));
                            return;
                        } else {
                            // Didn't meet min_times, return Empty
                            self.pos = frame.pos;
                            log::debug!(
                                "AnyNumberOf Empty (max_times_per_element exceeded, min_times not met)"
                            );
                            stack
                                .results
                                .insert(frame.frame_id, (Node::Empty, frame.pos, None));
                            return;
                        }
                    }
                }
            }

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
                    "AnyNumberOf COMPLETE: {} matches, storing result at frame_id={}, matched_idx={}",
                    count,
                    frame.frame_id,
                    matched_idx
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

    /// Handle OneOf grammar Initial state in iterative parser.
    ///
    /// ## State Machine:
    /// ```text
    /// Initial
    ///   ↓ (prune options, check exclude, check if already terminated)
    ///   ↓ (push first element as child)
    /// WaitingForChild
    ///   ↓ (child matched)
    ///   ├─→ Terminal: child consumed to max_idx (perfect match)
    ///   ├─→ Update longest_match, try next element
    ///   ↓ (child failed)
    ///   ├─→ Try next element
    ///   ↓ (all elements tried)
    ///   ├─→ Terminal: return longest_match (or Empty/Unparsable if none)
    /// ```
    ///
    /// ## Key Behavior:
    /// - Tries each element in sequence, keeping track of the longest match
    /// - Stops early if an element matches all the way to max_idx (perfect match)
    /// - Returns longest successful match, NOT first match (greedy longest)
    /// - Can return Empty (if optional) or Unparsable (if parse_mode allows)
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
            if test_result.is_ok() {
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
        let post_skip_pos = self.pos;

        // Combine parent and local terminators
        let all_terminators =
            self.combine_terminators(local_terminators, parent_terminators, reset_terminators);

        // Calculate max_idx with terminator and parent constraints
        let max_idx = self.calculate_max_idx(
            post_skip_pos,
            &all_terminators,
            parse_mode,
            frame.parent_max_idx,
        );

        // Check termination using ORIGINAL elements, not pruned
        // Pruning is for optimization only and shouldn't affect termination logic
        if self.is_terminated_with_elements(&all_terminators, elements) {
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

        // Use the already-pruned options (don't prune again)
        let available_options = pruned_options;

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

        let first_element = available_options[0].clone();
        let element_key = first_element.cache_key();

        frame.context = FrameContext::OneOf {
            grammar: grammar.clone(), // Clone instead of move since grammar is borrowed above
            leading_ws: leading_ws.clone(),
            post_skip_pos,
            longest_match: None,
            tried_elements: 0,
            max_idx,
            last_child_frame_id: Some(stack.frame_id_counter),
            current_element_key: Some(element_key), // Store the key of the element we're about to try
        };

        if matches!(*first_element, Grammar::Nothing() | Grammar::Empty) {
            log::debug!(
                "OneOf: First element is Nothing/Empty, handling inline (element_key={})",
                element_key
            );

            // Update context to record that we tried this element and it matched Empty
            frame.context = FrameContext::OneOf {
                grammar: grammar.clone(),
                leading_ws: leading_ws.clone(),
                post_skip_pos,
                longest_match: Some((Node::Empty, 0, element_key)),
                tried_elements: 1, // We tried one element
                max_idx,
                last_child_frame_id: None,
                current_element_key: None,
            };

            // Since Nothing/Empty is an instant match, simulate what would happen if a child returned Empty
            // We need to try the next element or finalize the result
            // Call the WaitingForChild handler with an Empty node
            frame.state = FrameState::WaitingForChild {
                child_index: 0,
                total_children: 1,
            };
            self.handle_oneof_waiting_for_child(
                frame,
                &Node::Empty,
                &post_skip_pos,
                &Some(element_key),
                stack,
                all_terminators,
            );
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
            current_element_key,
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
        // Use the current_element_key that was stored when we created the child frame
        // This is important when option pruning happens, as we need the key from the actual tried element
        let element_key = current_element_key.unwrap_or_else(|| {
            // Fallback: use child_element_key if available (for nested OneOf), or calculate from grammar
            child_element_key.unwrap_or_else(|| {
                if *tried_elements < elements.len() {
                    elements[*tried_elements].cache_key()
                } else {
                    0
                }
            })
        });

        eprintln!("[ONEOF CHILD] frame_id={}, child_empty={}, child_end_pos={}, consumed={}, tried_elements={}/{}, post_skip_pos={}",
            frame.frame_id, child_node.is_empty(), child_end_pos, consumed, tried_elements, elements.len(), post_skip_pos);
        if consumed >= 5 {
            eprintln!("[ONEOF CHILD LONG MATCH] This is a long match! Investigating...");
            eprintln!("  Grammar: {:?}", grammar);
        }

        log::debug!(
            "OneOf WaitingForChild: tried_elements={}, elements.len()={}, element_key={} (from current_element_key={:?}), child_empty={}, child_end_pos={}, max_idx={}, consumed={}",
            tried_elements, elements.len(), element_key, current_element_key, child_node.is_empty(), child_end_pos, max_idx, consumed
        );

        if !child_node.is_empty() {
            // Python parity: Prioritize matches by:
            // 1. Clean matches over unclean matches (those with Unparsable segments)
            // 2. Longer matches over shorter matches
            let child_is_clean = Self::is_node_clean(child_node);
            let is_better = if let Some((ref current_best, current_consumed, _)) = longest_match {
                let current_is_clean = Self::is_node_clean(current_best);

                // If child is clean and current is unclean, child is better
                if child_is_clean && !current_is_clean {
                    true
                }
                // If child is unclean and current is clean, child is NOT better
                else if !child_is_clean && current_is_clean {
                    false
                }
                // Both clean or both unclean: compare by length
                else {
                    consumed > *current_consumed
                }
            } else {
                // No previous match, this is better
                true
            };

            if is_better {
                eprintln!("[ONEOF BETTER] frame_id={}, consumed={}, clean={}, replacing previous best",
                    frame.frame_id, consumed, child_is_clean);
                log::debug!(
                    "OneOf: Found better match! element_key={}, consumed={}, child_end_pos={}, max_idx={}, clean={}",
                    element_key, consumed, child_end_pos, max_idx, child_is_clean
                );
                *longest_match = Some((child_node.clone(), consumed, element_key));

                // Python parity: Check for early termination conditions
                // 1. If we've reached max_idx, stop trying more elements
                if *child_end_pos >= *max_idx {
                    log::debug!("OneOf: reached max_idx={}, stopping early (perfect match)", max_idx);
                    *tried_elements = elements.len();
                }
                // 2. If this is the last element, we're done (no need to check terminators)
                else if *tried_elements + 1 >= elements.len() {
                    log::debug!("OneOf: last element matched, stopping early");
                    *tried_elements = elements.len();
                }
                // 3. Check if a terminator matches after this match
                else if !frame_terminators.is_empty() {
                    let next_code_idx = self.skip_start_index_forward_to_code(*child_end_pos, *max_idx);
                    eprintln!("[ONEOF DEBUG] Checking terminators: child_end_pos={}, next_code_idx={}, max_idx={}, frame_terminators.len()={}",
                        child_end_pos, next_code_idx, max_idx, frame_terminators.len());
                    if next_code_idx < self.tokens.len() {
                        let next_tok = &self.tokens[next_code_idx];
                        eprintln!("[ONEOF DEBUG] Next token at {}: {:?} (type: {})", next_code_idx, next_tok.raw(), next_tok.get_type());
                    }
                    log::debug!(
                        "OneOf: Checking terminators after match, child_end_pos={}, next_code_idx={}, max_idx={}",
                        child_end_pos, next_code_idx, max_idx
                    );
                    if next_code_idx >= *max_idx {
                        eprintln!("[ONEOF DEBUG] No more code after match, stopping");
                        log::debug!("OneOf: no more code segments after match, stopping early");
                        *tried_elements = elements.len();
                    } else {
                        // Check if any terminator matches
                        for (term_idx, terminator) in frame_terminators.iter().enumerate() {
                            eprintln!("[ONEOF DEBUG] Trying terminator #{}: {:?}", term_idx, terminator);
                            if self.try_match_grammar(terminator.clone(), next_code_idx, &[]).is_ok() {
                                eprintln!("[ONEOF DEBUG] Terminator #{} MATCHED! Stopping early.", term_idx);
                                log::debug!(
                                    "OneOf: terminator {:?} matched at pos={}, stopping early (terminated match)",
                                    terminator, next_code_idx
                                );
                                *tried_elements = elements.len();
                                break;
                            } else {
                                eprintln!("[ONEOF DEBUG] Terminator #{} did not match", term_idx);
                            }
                        }
                    }
                }
            }
        }
        *tried_elements += 1;

        if *tried_elements < elements.len() {
            self.pos = *post_skip_pos;
            let next_element = elements[*tried_elements].clone();
            let next_element_key = next_element.cache_key();
            *current_element_key = Some(next_element_key); // Store the key for next iteration
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
                eprintln!("[ONEOF RESULT] Returning match: frame_id={}, element_key={}, consumed={}, final_pos={}",
                    frame.frame_id, best_element_key, best_consumed, self.pos);
                log::debug!(
                    "OneOf returning match with element_key={}, consumed={}",
                    best_element_key,
                    best_consumed
                );
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

    /// Check if a node is "clean" (doesn't contain Unparsable segments).
    /// Python's longest_match prioritizes clean matches over unclean ones.
    fn is_node_clean(node: &Node) -> bool {
        match node {
            Node::Unparsable { .. } => false,
            Node::Sequence { children } => children.iter().all(Self::is_node_clean),
            Node::Ref { child, .. } => Self::is_node_clean(child),
            _ => true, // Token, Whitespace, Newline, Empty, etc. are all clean
        }
    }

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
    ) -> Result<usize, ParseError> {
        // Save current state
        let saved_pos = self.pos;

        // Try to parse the grammar using parse_with_grammar_cached
        // This will temporarily move the parser position but we'll restore it
        self.pos = pos;

        let result = self.parse_with_grammar_cached(&grammar, terminators);

        // Get the end position before restoring
        let end_pos = self.pos;

        // Restore position regardless of match success
        self.pos = saved_pos;

        // If the grammar matched, return the end position
        match result {
            Ok(node) => {
                // Only consider it a match if we actually consumed something meaningful (not just whitespace)
                if end_pos > pos && !matches!(node, Node::Empty) {
                    Ok(end_pos)
                } else {
                    Err(ParseError::with_context(
                        "trying but only an empty match found".to_string(),
                        Some(self.pos),
                        Some(grammar),
                    ))
                }
            }
            Err(s) => Err(s),
        }
    }
}
