use crate::parser::iterative::{NextStep, ParseFrameStack};
use crate::parser::{Grammar, Node, ParseError, ParseFrame, ParseMode};
use hashbrown::HashSet;

impl crate::parser::Parser<'_> {
    /// Handle AnySetOf grammar Initial state in iterative parser
    pub fn handle_anysetof_initial(
        &mut self,
        elements: &[Grammar],
        min_times: usize,
        max_times: Option<usize>,
        exclude: &Option<Box<Grammar>>,
        optional: bool,
        local_terminators: &[Grammar],
        reset_terminators: bool,
        allow_gaps: bool,
        parse_mode: ParseMode,
        frame: &mut ParseFrame,
        parent_terminators: &[Grammar],
        stack: &mut ParseFrameStack,
    ) -> Result<NextStep, ParseError> {
        let pos = frame.pos;
        log::debug!("[ITERATIVE] AnySetOf Initial state at pos {}", pos);

        // Check exclude grammar first
        if let Some(exclude_grammar) = exclude {
            let test_result = self.try_match_grammar(exclude_grammar, pos, parent_terminators);
            if test_result.is_some() {
                log::debug!(
                    "AnySetOf: exclude grammar matched at pos {}, returning empty",
                    pos
                );
                return Ok(NextStep::Continue);
            }
        }

        let all_terminators: Vec<Grammar> = if reset_terminators {
            local_terminators.to_vec()
        } else {
            local_terminators
                .iter()
                .cloned()
                .chain(parent_terminators.iter().cloned())
                .collect()
        };

        self.pos = pos;
        let max_idx = if parse_mode == ParseMode::Greedy {
            self.trim_to_terminator(pos, &all_terminators)
        } else {
            self.tokens.len()
        };

        let max_idx = if let Some(parent_limit) = frame.parent_max_idx {
            max_idx.min(parent_limit)
        } else {
            max_idx
        };

        log::debug!(
            "[ITERATIVE] AnySetOf max_idx: {} (tokens.len: {})",
            max_idx,
            self.tokens.len()
        );

        frame.state = crate::parser::FrameState::WaitingForChild {
            child_index: 0,
            total_children: max_times.unwrap_or(usize::MAX).min(elements.len()),
        };
        frame.context = crate::parser::FrameContext::AnySetOf {
            min_times,
            max_times,
            allow_gaps,
            optional,
            count: 0,
            matched_idx: pos,
            working_idx: pos,
            matched_elements: HashSet::new(),
            max_idx,
            last_child_frame_id: None,
            elements: elements.to_vec(),
            parse_mode,
        };
        frame.terminators = all_terminators.clone();

        stack.push(frame);

        let child_grammar = Grammar::OneOf {
            elements: elements.to_vec(),
            exclude: None,
            optional: false,
            terminators: vec![],
            reset_terminators: false,
            allow_gaps,
            parse_mode,
        };

        let mut child_frame = crate::parser::ParseFrame {
            frame_id: stack.frame_id_counter,
            grammar: child_grammar,
            pos,
            terminators: all_terminators,
            state: crate::parser::FrameState::Initial,
            accumulated: vec![],
            context: crate::parser::FrameContext::None,
            parent_max_idx: Some(max_idx),
        };

        let next_child_id = stack.frame_id_counter;
        if let Some(parent_frame) = stack.last_mut() {
            if let crate::parser::FrameContext::AnySetOf {
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

    /// Handle AnyNumberOf grammar Initial state in iterative parser
    pub fn handle_anynumberof_initial(
        &mut self,
        elements: &[Grammar],
        min_times: usize,
        max_times: Option<usize>,
        max_times_per_element: Option<usize>,
        exclude: &Option<Box<Grammar>>,
        optional: bool,
        any_terminators: &[Grammar],
        reset_terminators: bool,
        allow_gaps: bool,
        parse_mode: ParseMode,
        frame: &mut ParseFrame,
        parent_terminators: &[Grammar],
        stack: &mut ParseFrameStack,
        iteration_count: usize,
    ) -> Result<NextStep, ParseError> {
        let start_idx = frame.pos;
        log::debug!(
            "AnyNumberOf starting at {}, min_times={}, max_times={:?}, allow_gaps={}, parse_mode={:?}",
            start_idx,
            min_times,
            max_times,
            allow_gaps,
            parse_mode
        );

        if let Some(exclude_grammar) = exclude {
            let test_result =
                self.try_match_grammar(exclude_grammar, start_idx, parent_terminators);
            if test_result.is_some() {
                log::debug!(
                    "AnyNumberOf: exclude grammar matched at pos {}, returning empty",
                    start_idx
                );
                return Ok(NextStep::Continue);
            }
        }

        let all_terminators: Vec<Grammar> = if reset_terminators {
            any_terminators.to_vec()
        } else {
            any_terminators
                .iter()
                .cloned()
                .chain(parent_terminators.iter().cloned())
                .collect()
        };

        self.pos = start_idx;
        let max_idx = if parse_mode == ParseMode::Greedy {
            self.trim_to_terminator(start_idx, &all_terminators)
        } else {
            self.tokens.len()
        };

        let max_idx = if let Some(parent_limit) = frame.parent_max_idx {
            max_idx.min(parent_limit)
        } else {
            max_idx
        };

        log::debug!("DEBUG [iter {}]: AnyNumberOf Initial at pos={}, parent_max_idx={:?}, elements.len()={}",
            iteration_count, frame.pos, frame.parent_max_idx, elements.len());

        log::debug!(
            "AnyNumberOf max_idx: {} (tokens.len: {})",
            max_idx,
            self.tokens.len()
        );

        frame.state = crate::parser::FrameState::WaitingForChild {
            child_index: 0,
            total_children: elements.len(),
        };
        frame.context = crate::parser::FrameContext::AnyNumberOf {
            elements: elements.to_vec(),
            min_times,
            max_times,
            max_times_per_element,
            allow_gaps,
            optional,
            parse_mode,
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
            let child_grammar = Grammar::OneOf {
                elements: elements.to_vec(),
                exclude: None,
                optional: true,
                terminators: all_terminators.clone(),
                reset_terminators: false,
                allow_gaps,
                parse_mode,
            };

            let mut child_frame = crate::parser::ParseFrame {
                frame_id: stack.frame_id_counter,
                grammar: child_grammar,
                pos: start_idx,
                terminators: all_terminators,
                state: crate::parser::FrameState::Initial,
                accumulated: vec![],
                context: crate::parser::FrameContext::None,
                parent_max_idx: Some(max_idx),
            };

            let next_child_id = stack.frame_id_counter;
            if let Some(parent_frame) = stack.last_mut() {
                if let crate::parser::FrameContext::AnyNumberOf {
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

    /// Handle OneOf grammar Initial state in iterative parser
    pub fn handle_oneof_initial(
        &mut self,
        elements: &[Grammar],
        exclude: &Option<Box<Grammar>>,
        optional: bool,
        local_terminators: &[Grammar],
        reset_terminators: bool,
        allow_gaps: bool,
        parse_mode: ParseMode,
        frame: &mut ParseFrame,
        parent_terminators: &[Grammar],
        stack: &mut ParseFrameStack,
    ) -> Result<NextStep, ParseError> {
        let pos = frame.pos;
        log::debug!(
            "OneOf Initial state at pos {}, {} elements, parse_mode={:?}",
            pos,
            elements.len(),
            parse_mode
        );

        if let Some(exclude_grammar) = exclude {
            let test_result = self.try_match_grammar(exclude_grammar, pos, parent_terminators);
            if test_result.is_some() {
                log::debug!(
                    "OneOf: exclude grammar matched at pos {}, returning empty",
                    pos
                );
                stack
                    .results
                    .insert(frame.frame_id, (Node::Empty, pos, None));
                return Ok(NextStep::Fallthrough);
            }
        }

        let leading_ws = if allow_gaps {
            self.collect_transparent(true)
        } else {
            Vec::new()
        };
        let post_skip_pos = self.pos;

        let all_terminators: Vec<Grammar> = if reset_terminators {
            local_terminators.to_vec()
        } else {
            local_terminators
                .iter()
                .chain(parent_terminators.iter())
                .cloned()
                .collect()
        };

        let max_idx = if parse_mode == ParseMode::Greedy {
            self.trim_to_terminator(post_skip_pos, &all_terminators)
        } else {
            self.tokens.len()
        };

        let max_idx = if let Some(parent_limit) = frame.parent_max_idx {
            max_idx.min(parent_limit)
        } else {
            max_idx
        };

        if self.is_terminated(&all_terminators) {
            log::debug!("OneOf: Already at terminator");
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

        let available_options: Vec<Grammar> =
            self.prune_options(elements).into_iter().cloned().collect();

        if available_options.is_empty() {
            log::debug!("OneOf: No viable options after pruning");
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

        frame.context = crate::parser::FrameContext::OneOf {
            elements: available_options.clone(),
            allow_gaps,
            optional,
            leading_ws: leading_ws.clone(),
            post_skip_pos,
            longest_match: None,
            tried_elements: 0,
            max_idx,
            parse_mode,
            last_child_frame_id: Some(stack.frame_id_counter),
        };

        let first_element = available_options[0].clone();
        let element_key = first_element.cache_key();

        if matches!(first_element, Grammar::Nothing() | Grammar::Empty) {
            log::debug!(
                "OneOf: First element is Nothing, handling inline (element_key={})",
                element_key
            );
            frame.context = if let crate::parser::FrameContext::OneOf {
                elements,
                allow_gaps,
                optional,
                leading_ws,
                post_skip_pos,
                longest_match: _,
                tried_elements,
                max_idx,
                parse_mode,
                last_child_frame_id: _,
            } = &frame.context
            {
                crate::parser::FrameContext::OneOf {
                    elements: elements.clone(),
                    allow_gaps: *allow_gaps,
                    optional: *optional,
                    leading_ws: leading_ws.clone(),
                    post_skip_pos: *post_skip_pos,
                    longest_match: Some((Node::Empty, 0, element_key)),
                    tried_elements: *tried_elements + 1,
                    max_idx: *max_idx,
                    parse_mode: *parse_mode,
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
            grammar: first_element,
            pos: post_skip_pos,
            terminators: all_terminators.clone(),
            state: crate::parser::FrameState::Initial,
            accumulated: Vec::new(),
            context: crate::parser::FrameContext::None,
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

    // Helper methods
    /// Try to match a grammar at a specific position without consuming tokens
    /// Returns Some(end_pos) if the grammar matches, None otherwise
    ///
    /// This uses the same parsing logic as the main parser but in a non-destructive way,
    /// similar to how terminators are checked.
    fn try_match_grammar(
        &mut self,
        grammar: &Grammar,
        pos: usize,
        terminators: &[Grammar],
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
                // Only consider it a match if we actually consumed something
                // or if it's an empty match at the exact position
                if end_pos > pos {
                    Some(end_pos)
                } else if matches!(node, Node::Empty) {
                    // Empty nodes might still be valid matches (like optional elements)
                    None
                } else {
                    Some(end_pos)
                }
            }
            Err(_) => None,
        }
    }
}
