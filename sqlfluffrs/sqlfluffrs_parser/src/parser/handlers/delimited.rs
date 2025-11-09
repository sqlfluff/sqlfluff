use std::sync::Arc;

use crate::parser::iterative::{FrameResult, ParseFrameStack};
use crate::parser::utils::skip_start_index_forward_to_code;
use crate::parser::DelimitedState;
use crate::parser::{FrameContext, FrameState};
use crate::parser::{Node, ParseError, ParseFrame};
use sqlfluffrs_types::{Grammar, ParseMode};

impl crate::parser::Parser<'_> {
    /// Handle Delimited grammar Initial state in iterative parser.
    ///
    /// ## State Machine:
    /// ```text
    /// Initial
    ///   ↓ (prune options, combine terminators, calculate max_idx)
    ///   ↓ (push OneOf(elements) as child with optional=true)
    /// MatchingElement
    ///   ↓ (element matched)
    ///   ├─→ Collect transparent tokens if allow_gaps
    ///   ├─→ Check terminators: if terminated, Terminal (success)
    ///   ├─→ Check for trailing whitespace if !allow_gaps: Terminal if found
    ///   ├─→ Push delimiter as child
    ///   └─→ MatchingDelimiter
    ///   ↓ (element failed)
    ///   ├─→ Terminal: success if delimiter_count >= min_delimiters
    ///   └─→ Terminal: fail with Empty if delimiter_count < min_delimiters
    /// MatchingDelimiter
    ///   ↓ (delimiter matched)
    ///   ├─→ Store delimiter_match (for potential trailing delimiter)
    ///   ├─→ Check terminators: if terminated + !allow_trailing, backtrack or error
    ///   ├─→ Check terminators: if terminated + allow_trailing, append delimiter, Terminal
    ///   ├─→ Skip to code if allow_gaps
    ///   ├─→ Push OneOf(elements) as child
    ///   └─→ MatchingElement
    ///   ↓ (delimiter failed)
    ///   ├─→ Terminal: success if delimiter_count >= min_delimiters
    ///   └─→ Terminal: fail with Empty if delimiter_count < min_delimiters
    /// ```
    ///
    /// ## Key Behavior:
    /// - Alternates between matching elements and delimiters
    /// - Tracks delimiter_count to enforce min_delimiters requirement
    /// - Handles trailing delimiters based on allow_trailing flag
    /// - If !allow_gaps and whitespace detected, stops matching
    /// - Filters delimiter from parent terminators (delimiter shouldn't terminate itself)
    /// - Trims child max_idx to next delimiter to prevent element from consuming delimiter
    /// Returns true if caller should continue main loop
    pub fn handle_delimited_initial(
        &mut self,
        grammar: Arc<Grammar>,
        mut frame: ParseFrame,
        parent_terminators: &[Arc<Grammar>],
        stack: &mut ParseFrameStack,
    ) -> Result<FrameResult, ParseError> {
        let mut working_pos = frame.pos;
        log::debug!("[ITERATIVE] Delimited Initial state at pos {}", working_pos);

        // Destructure the Delimited grammar
        let (
            elements,
            delimiter,
            allow_trailing,
            optional,
            optional_delimiter,
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
                optional_delimiter,
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
                *optional_delimiter,
                terminators,
                *reset_terminators,
                *allow_gaps,
                *min_delimiters,
                *parse_mode,
            ),
            _ => {
                return Err(ParseError::with_context(
                    "handle_delimited_initial called with non-Delimited grammar".to_string(),
                    Some(self.pos),
                    Some(grammar),
                ));
            }
        };

        // // Prune options BEFORE any other logic, like Python
        // let pruned_options = self.prune_options(elements);
        // // If no options remain after pruning, treat as no match
        // if pruned_options.is_empty() {
        //     stack
        //         .results
        //         .insert(frame.frame_id, (Node::Empty, pos, None));
        //     return Ok(FrameResult::Done);
        // }

        // Remove fast NonCodeMatcher: now handled as a real grammar in terminators

        // Combine terminators, filtering out delimiter from BOTH local and parent terminators
        // This is critical - delimiter shouldn't terminate the delimited list itself
        // Python's line 124: `*(t for t in parse_context.terminators if t not in delimiter_matchers)`
        // filters delimiter from the COMBINED terminator list
        log::debug!(
            "[DELIMITED] Delimiter filtering at pos {}: parent_count={}, local_count={}",
            self.pos,
            parent_terminators.len(),
            local_terminators.len()
        );
        let filtered_parent: Vec<Arc<Grammar>> = parent_terminators
            .iter()
            .filter(|t| *t != delimiter.as_ref())
            .cloned()
            .collect();

        let filtered_local: Vec<Arc<Grammar>> = local_terminators
            .iter()
            .filter(|t| *t != delimiter.as_ref())
            .cloned()
            .collect();

        log::debug!(
            "[DELIMITED] After filtering: filtered_parent={}, filtered_local={}",
            filtered_parent.len(),
            filtered_local.len()
        );

        // NOTE: Delimited does NOT respect reset_terminators flag
        // It always combines local + filtered parent terminators
        // This differs from other handlers but matches Python's behavior
        let mut all_terminators: Vec<Arc<Grammar>> =
            filtered_local.into_iter().chain(filtered_parent).collect();

        // If allow_gaps is false, add NonCodeMatcher as a real terminator
        if !allow_gaps {
            all_terminators.push(Arc::new(Grammar::NonCodeMatcher));
        }

        // Calculate max_idx based on parse_mode and terminators
        // let max_idx = if parse_mode == ParseMode::Greedy {
        //     // In GREEDY mode, actively look for terminators
        //     self.trim_to_terminator(pos, &all_terminators)
        // } else {
        //     // In STRICT mode, still need to respect terminators if they exist
        //     // Check if there's a terminator anywhere ahead
        //     if all_terminators.is_empty() {
        //         self.tokens.len()
        //     } else {
        //         self.trim_to_terminator(pos, &all_terminators)
        //     }
        // };

        // Apply parent's max_idx limit (simulates Python's segments[:max_idx])
        let max_idx = if let Some(parent_limit) = frame.parent_max_idx {
            self.tokens.len().min(parent_limit)
        } else {
            self.tokens.len()
        };

        if allow_gaps && working_pos > self.pos {
            working_pos = skip_start_index_forward_to_code(self.tokens, working_pos, max_idx)
        }

        if working_pos >= max_idx {
            // End of input or max_idx reached before matching any elements.
            // This is equivalent to breaking out of the while loop in Python.
            // Now, handle the "post-while" logic: if optional, succeed with empty list; else, fail.
            if optional {
                stack.results.insert(
                    frame.frame_id,
                    (Node::DelimitedList { children: vec![] }, working_pos, None),
                );
                return Ok(FrameResult::Done);
            } else {
                return Err(ParseError::with_context(
                    "Delimited: expected at least one element, but none found".to_string(),
                    Some(self.pos),
                    Some(grammar),
                ));
            }
        }

        // Create Delimited context
        frame.state = FrameState::WaitingForChild {
            child_index: 0,
            total_children: usize::MAX, // Unknown number of children
        };
        frame.context = FrameContext::Delimited {
            grammar: grammar.clone(),
            delimiter_count: 0,
            matched_idx: working_pos,
            working_idx: working_pos,
            max_idx,
            state: DelimitedState::MatchingElement,
            last_child_frame_id: None,
            delimiter_match: None,
            pos_before_delimiter: None,
        };
        frame.terminators = all_terminators.clone();

        // Extract max_idx before moving frame - this is the limit for children!
        // Children should be constrained by the Delimited's calculated max_idx
        // NOTE: We do NOT trim to the next delimiter position for element children.
        // This is because the element itself might be a Delimited grammar that uses
        // the same delimiter internally. Instead, we rely on the element's grammar
        // to naturally stop at the correct position, and then check for a delimiter
        // after the element completes.
        // let delimiter_max_idx = self.trim_to_terminator(working_pos, &[(**delimiter).clone()]);
        // let child_max_idx = max_idx.min(delimiter_max_idx);
        let child_max_idx = max_idx;
        log::debug!(
            "[DELIMITED] Initial: working_pos={}, max_idx={}, child_max_idx={}",
            working_pos,
            max_idx,
            child_max_idx
        );
        stack.push(&mut frame);

        // Create first child to match element (try all elements via OneOf)
        let child_grammar = Grammar::OneOf {
            elements: elements.to_vec(),
            exclude: None,
            optional: true, // Elements in Delimited are implicitly optional
            terminators: vec![],
            reset_terminators: false,
            allow_gaps,
            parse_mode,
            simple_hint: None,
        };

        // Python parity: When matching elements (not seeking delimiter),
        // the delimiter should be added as a terminator so child grammars
        // (especially Anything) stop at the delimiter.
        // See Python's delimited.py line 146-148:
        //   _push_terminators = delimiter_matchers if not seeking_delimiter else []
        let mut element_terminators = all_terminators.clone();
        element_terminators.push((**delimiter).clone());

        log::debug!(
            "[ITERATIVE] Delimited: pushing child element at working_pos={}, child_max_idx={:?}, element_terminators count={}",
            working_pos,
            Some(child_max_idx),
            element_terminators.len()
        );
        let mut child_frame = ParseFrame::new_child(
            stack.frame_id_counter,
            child_grammar.into(),
            working_pos,
            element_terminators, // Include delimiter as terminator for elements!
            Some(child_max_idx), // Use Delimited's max_idx trimmed to next delimiter!
        );

        // Update parent's last_child_frame_id and push child
        ParseFrame::update_parent_last_child_id(stack, "Delimited", stack.frame_id_counter);
        stack.increment_frame_id_counter();
        stack.push(&mut child_frame);
        Ok(FrameResult::Done) // Continue to process the child frame we just pushed
    }

    pub(crate) fn handle_delimited_waiting_for_child(
        &mut self,
        mut frame: ParseFrame,
        child_node: &Node,
        child_end_pos: &usize,
        child_element_key: &Option<u64>,
        stack: &mut ParseFrameStack,
        frame_terminators: Vec<Arc<Grammar>>,
    ) -> Result<FrameResult, ParseError> {
        let FrameContext::Delimited {
            grammar,
            delimiter_count,
            matched_idx,
            working_idx,
            max_idx,
            state,
            last_child_frame_id: _,
            delimiter_match,
            pos_before_delimiter,
        } = &mut frame.context
        else {
            unreachable!("Expected Delimited context");
        };
        let Grammar::Delimited {
            elements,
            delimiter,
            min_delimiters,
            allow_trailing,
            allow_gaps,
            optional,
            optional_delimiter,
            parse_mode,
            ..
        } = grammar.as_ref()
        else {
            panic!("Expected Grammar::Delimited in FrameContext::Delimited");
        };
        log::debug!("[ITERATIVE] Delimited WaitingForChild: state={:?}, delimiter_count={}, child_node is_empty={}, working_idx={}, self.pos={}", state, delimiter_count, child_node.is_empty(), working_idx, self.pos);
        match state {
            DelimitedState::MatchingElement => {
                // If allow_gaps, skip non-code tokens before matching
                if *allow_gaps {
                    *working_idx = self.skip_start_index_forward_to_code(*working_idx, *max_idx);
                    self.pos = *working_idx;
                    log::debug!(
                        "[ITERATIVE] Delimited: after skipping gaps, working_idx={}, self.pos={}",
                        working_idx,
                        self.pos
                    );
                } else {
                    // CRITICAL: Set self.pos to working_idx even when allow_gaps=false!
                    // This ensures terminator checks happen at the correct position.
                    self.pos = *working_idx;
                    log::debug!(
                        "[ITERATIVE] Delimited: allow_gaps=false, working_idx={}, self.pos={}",
                        working_idx,
                        self.pos
                    );
                }

                // Python parity: Check for terminators BEFORE trying to match element/delimiter
                // This is critical - terminators are checked at the START of each iteration,
                // not after matching an element. This ensures that a delimiter can be matched
                // even if it's also a terminator in an outer scope.
                //
                // CRITICAL FIX: If we have a pending delimiter, check terminators from BEFORE
                // the delimiter, not after it. This is needed for terminators like
                // Sequence(CommaSegment, "TABLE") which need to match the delimiter itself.
                let check_pos = if delimiter_match.is_some() && pos_before_delimiter.is_some() {
                    pos_before_delimiter.unwrap()
                } else {
                    self.pos
                };
                let saved_pos = self.pos;
                self.pos = check_pos;
                let is_terminated = self.is_terminated(&frame_terminators);
                self.pos = saved_pos;

                if self.is_at_end() || is_terminated {
                    log::debug!(
                        "[ITERATIVE] Delimited: terminator found at position {}, matched_idx={}, delimiter_match present={}",
                        self.pos,
                        matched_idx,
                        delimiter_match.is_some()
                    );
                    log::debug!(
                        "[ITERATIVE] Delimited completing with {} items",
                        frame.accumulated.len()
                    );

                    // CRITICAL FIX: If we have a pending delimiter match that hasn't been added yet,
                    // we need to return the position BEFORE that delimiter, not after it.
                    // This matches Python's behavior where terminators are checked AFTER delimiters
                    // are matched but BEFORE the next element, and if terminated, the delimiter
                    // is NOT included in the result.
                    let final_pos = if delimiter_match.is_some() && pos_before_delimiter.is_some() {
                        // We have a pending delimiter - return position before it
                        let before_delim = pos_before_delimiter.unwrap();
                        log::debug!(
                            "[ITERATIVE] Delimited: terminator after delimiter, returning pos_before_delimiter={}",
                            before_delim
                        );
                        before_delim
                    } else {
                        // No pending delimiter - return matched_idx
                        *matched_idx
                    };

                    self.pos = final_pos;
                    // Handle trailing delimiter if allowed and present
                    if *allow_trailing && delimiter_match.is_some() {
                        frame.accumulated.push(delimiter_match.take().unwrap());
                        *delimiter_count += 1;
                    }
                    // Check min_delimiters at completion
                    if *delimiter_count < *min_delimiters {
                        // Transition to Combining to finalize Empty result
                        frame.end_pos = Some(frame.pos);
                        frame.state = FrameState::Combining;
                        stack.push(&mut frame);
                        return Ok(FrameResult::Done);
                    }
                    // Transition to Combining to finalize DelimitedList result
                    frame.end_pos = Some(final_pos);
                    frame.state = FrameState::Combining;
                    stack.push(&mut frame);
                    return Ok(FrameResult::Done);
                }

                if child_node.is_empty() {
                    log::debug!(
                        "[ITERATIVE] Delimited: no element matched at position {}",
                        frame.pos
                    );
                    log::debug!(
                        "[ITERATIVE] Delimited completing with {} items",
                        frame.accumulated.len()
                    );

                    // CRITICAL FIX: If we have a pending delimiter match that hasn't been added yet,
                    // we need to return the position BEFORE that delimiter, not after it.
                    // Python's Delimited: when element fails after delimiter, the delimiter is NOT
                    // included in working_match, so the return position should be before the delimiter.
                    let final_pos = if delimiter_match.is_some() && pos_before_delimiter.is_some() {
                        // We have a pending delimiter - return position before it
                        let before_delim = pos_before_delimiter.unwrap();
                        log::debug!(
                            "[ITERATIVE] Delimited: element failed after delimiter, returning pos_before_delimiter={}",
                            before_delim
                        );
                        before_delim
                    } else {
                        // No pending delimiter - return matched_idx
                        *matched_idx
                    };

                    self.pos = final_pos;
                    // Handle trailing delimiter if allowed and present
                    if *allow_trailing && delimiter_match.is_some() {
                        frame.accumulated.push(delimiter_match.take().unwrap());
                        *delimiter_count += 1;
                    }
                    // Check min_delimiters at completion
                    if *delimiter_count < *min_delimiters {
                        // Transition to Combining to finalize Empty result
                        frame.end_pos = Some(frame.pos);
                        frame.state = FrameState::Combining;
                        stack.push(&mut frame);
                        return Ok(FrameResult::Done);
                    }
                    // Transition to Combining to finalize DelimitedList result
                    frame.end_pos = Some(final_pos);
                    frame.state = FrameState::Combining;
                    stack.push(&mut frame);
                    return Ok(FrameResult::Done);
                } else {
                    log::debug!(
                        "[ITERATIVE] Delimited element matched: pos {} -> {}",
                        frame.pos,
                        child_end_pos
                    );
                    // Python parity: collect all whitespace/newline nodes between matched_idx and working_idx
                    // In Python, these are implicitly included via the slice range in MatchResult.apply()
                    // Python includes ALL whitespace, not just "non-trivial" whitespace
                    if *allow_gaps {
                        for check_pos in *matched_idx..*working_idx {
                            if check_pos < self.tokens.len() && !self.tokens[check_pos].is_code() {
                                let tok = &self.tokens[check_pos];
                                let tok_type = tok.get_type();
                                let tok_raw = tok.raw();
                                // Only check if already in frame's accumulated (duplicates across grammars will be handled by deduplication)
                                let already_in_frame =
                                    frame.accumulated.iter().any(|node| match node {
                                        Node::Whitespace { token_idx: idx, .. }
                                        | Node::Newline { token_idx: idx, .. } => *idx == check_pos,
                                        _ => false,
                                    });
                                if !already_in_frame {
                                    if tok_type == "whitespace" {
                                        frame.accumulated.push(Node::Whitespace {
                                            raw: tok_raw.to_string(),
                                            token_idx: check_pos,
                                        });
                                    } else if tok_type == "newline" {
                                        frame.accumulated.push(Node::Newline {
                                            raw: tok_raw.to_string(),
                                            token_idx: check_pos,
                                        });
                                    }
                                }
                            }
                        }
                    }
                    // If there was a delimiter match, append it and increment count
                    if delimiter_match.is_some() {
                        frame.accumulated.push(delimiter_match.take().unwrap());
                        *delimiter_count += 1;
                    }
                    frame.accumulated.push(child_node.clone());
                    *matched_idx = *child_end_pos;
                    *working_idx = *matched_idx;
                    if *allow_gaps {
                        *working_idx =
                            self.skip_start_index_forward_to_code(*working_idx, *max_idx);
                    }
                    self.pos = *working_idx;
                    // Python parity: DO NOT check terminators here!
                    // Terminators are checked at the START of the next iteration,
                    // which allows the delimiter to be matched even if it's a terminator.
                    *state = DelimitedState::MatchingDelimiter;
                    // If allow_gaps=false and next position has ANY whitespace, stop matching
                    // Python's NonCodeMatcher would terminate here
                    if !*allow_gaps && *working_idx < self.tokens.len() {
                        let tok = &self.tokens[*working_idx];
                        if !tok.is_code() {
                            log::debug!(
                                "[ITERATIVE] Delimited: allow_gaps=false and next position {} has whitespace, completing",
                                *working_idx
                            );
                            // Check min_delimiters at completion
                            if *delimiter_count < *min_delimiters {
                                // Transition to Combining to finalize Empty result
                                frame.end_pos = Some(frame.pos);
                                frame.state = FrameState::Combining;
                                stack.push(&mut frame);
                                return Ok(FrameResult::Done);
                            }
                            self.pos = *matched_idx;
                            // Transition to Combining to finalize DelimitedList result
                            frame.end_pos = Some(*matched_idx);
                            frame.state = FrameState::Combining;
                            stack.push(&mut frame);
                            return Ok(FrameResult::Done);
                        }
                    }
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
                        &mut frame,
                        child_frame,
                        "Delimited",
                    );
                    return Ok(FrameResult::Done);
                }
            }
            DelimitedState::MatchingDelimiter => {
                if child_node.is_empty() {
                    // Failed to match a delimiter
                    if *optional_delimiter {
                        // Python lines 157-162: If delimiter is optional and failed to match,
                        // loop again to try matching another element without requiring delimiter
                        log::debug!(
                            "[ITERATIVE] Delimited: no delimiter found, but optional_delimiter=true, continuing to match elements at position {}",
                            matched_idx
                        );
                        *state = DelimitedState::MatchingElement;
                        // Don't change working_idx or matched_idx - continue from where we are
                        // Push child to try matching another element
                        if *allow_gaps {
                            *working_idx =
                                self.skip_start_index_forward_to_code(*working_idx, *max_idx);
                        }
                        self.pos = *working_idx;
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
                            &mut frame,
                            child_frame,
                            "Delimited",
                        );
                        return Ok(FrameResult::Done);
                    }

                    // Not optional_delimiter, so complete the delimited list
                    log::debug!(
                        "[ITERATIVE] Delimited: no delimiter found, completing at position {}",
                        matched_idx
                    );
                    // If no delimiter matched, check min_delimiters
                    if *delimiter_count < *min_delimiters {
                        // If not enough delimiters, return empty match
                        self.pos = frame.pos;
                        // Transition to Combining to finalize Empty result
                        frame.end_pos = Some(frame.pos);
                        frame.state = FrameState::Combining;
                        stack.push(&mut frame);
                    } else {
                        // Handle trailing delimiter if allowed and present
                        if *allow_trailing && delimiter_match.is_some() {
                            frame.accumulated.push(delimiter_match.take().unwrap());
                            *delimiter_count += 1;
                        }
                        self.pos = *matched_idx;
                        // Transition to Combining to finalize DelimitedList result
                        frame.end_pos = Some(*matched_idx);
                        frame.state = FrameState::Combining;
                        stack.push(&mut frame);
                    }
                    return Ok(FrameResult::Done);
                } else {
                    log::debug!(
                        "[ITERATIVE] Delimited delimiter matched: pos {} -> {}",
                        working_idx,
                        child_end_pos
                    );
                    // Track accumulated length before adding whitespace for potential backtrack
                    let accumulated_len_before_gaps = frame.accumulated.len();
                    // Python parity: collect all whitespace/newline nodes between matched_idx and working_idx
                    // In Python, these are implicitly included via the slice range in MatchResult.apply()
                    // Python includes ALL whitespace, not just "non-trivial" whitespace
                    if *allow_gaps {
                        for check_pos in *matched_idx..*working_idx {
                            if check_pos < self.tokens.len() && !self.tokens[check_pos].is_code() {
                                let tok = &self.tokens[check_pos];
                                let tok_type = tok.get_type();
                                let tok_raw = tok.raw();
                                // Only check if already in frame's accumulated
                                let already_in_frame =
                                    frame.accumulated.iter().any(|node| match node {
                                        Node::Whitespace { token_idx: idx, .. }
                                        | Node::Newline { token_idx: idx, .. } => *idx == check_pos,
                                        _ => false,
                                    });
                                if !already_in_frame {
                                    if tok_type == "whitespace" {
                                        frame.accumulated.push(Node::Whitespace {
                                            raw: tok_raw.to_string(),
                                            token_idx: check_pos,
                                        });
                                    } else if tok_type == "newline" {
                                        frame.accumulated.push(Node::Newline {
                                            raw: tok_raw.to_string(),
                                            token_idx: check_pos,
                                        });
                                    }
                                }
                            }
                        }
                    }
                    // Store the delimiter match for the next element
                    *delimiter_match = Some(child_node.clone());
                    // Save position before delimiter for potential backtrack
                    *pos_before_delimiter = Some(*matched_idx);
                    *matched_idx = *child_end_pos;
                    *working_idx = *matched_idx;
                    self.pos = *matched_idx;
                    log::debug!("[ITERATIVE] Delimited: after delimiter match, self.pos={}, matched_idx={}, checking terminators...", self.pos, matched_idx);
                    let is_term = self.is_terminated(&frame_terminators);
                    log::debug!("[ITERATIVE] Delimited: is_terminated returned: {}", is_term);
                    if is_term {
                        log::debug!("[ITERATIVE] Delimited: terminated after delimiter");
                        if !*allow_trailing {
                            // When allow_trailing=false and we hit a terminator after a delimiter:
                            // - If we haven't matched any delimiters yet (delimiter_count==0), backtrack
                            // - If we've already matched delimiters (delimiter_count>0), return error
                            if *delimiter_count == 0 {
                                // Backtrack: don't consume the delimiter
                                log::debug!("[ITERATIVE] Delimited: backtracking - not consuming trailing delimiter");
                                // Restore position to before the delimiter and discard delimiter_match
                                *delimiter_match = None;
                                let backtrack_pos = pos_before_delimiter.unwrap();
                                self.pos = backtrack_pos;
                                // Also remove any whitespace nodes we added before the delimiter
                                frame.accumulated.truncate(accumulated_len_before_gaps);
                                // Check min_delimiters at completion
                                if *delimiter_count < *min_delimiters {
                                    // Transition to Combining to finalize Empty result
                                    frame.end_pos = Some(frame.pos);
                                    frame.state = FrameState::Combining;
                                    stack.push(&mut frame);
                                    return Ok(FrameResult::Done);
                                }
                                // Transition to Combining to finalize DelimitedList result
                                frame.end_pos = Some(backtrack_pos);
                                frame.state = FrameState::Combining;
                                stack.push(&mut frame);
                                return Ok(FrameResult::Done);
                            } else {
                                // We've already matched delimiters, so return error
                                log::debug!("[ITERATIVE] Delimited: trailing delimiter not allowed after matching delimiters");
                                return Err(ParseError::new(
                                    "Trailing delimiter not allowed".to_string(),
                                ));
                            }
                        }
                        // Handle trailing delimiter if allowed and present
                        if *allow_trailing && delimiter_match.is_some() {
                            frame.accumulated.push(delimiter_match.take().unwrap());
                            *delimiter_count += 1;
                        }
                        // Check min_delimiters at completion
                        if *delimiter_count < *min_delimiters {
                            // Transition to Combining to finalize Empty result
                            frame.end_pos = Some(frame.pos);
                            frame.state = FrameState::Combining;
                            stack.push(&mut frame);
                            return Ok(FrameResult::Done);
                        }
                        // Transition to Combining to finalize DelimitedList result
                        frame.end_pos = Some(*matched_idx);
                        frame.state = FrameState::Combining;
                        stack.push(&mut frame);
                        Ok(FrameResult::Done)
                    } else {
                        *state = DelimitedState::MatchingElement;
                        if *allow_gaps {
                            *working_idx =
                                self.skip_start_index_forward_to_code(*working_idx, *max_idx);
                        }
                        self.pos = *working_idx;
                        log::debug!("[ITERATIVE] Delimited: changed to MatchingElement, self.pos={}, working_idx={}, checking terminators again...", self.pos, working_idx);
                        let is_term2 = self.is_at_end() || self.is_terminated(&frame_terminators);
                        log::debug!(
                            "[ITERATIVE] Delimited: second terminator check returned: {}",
                            is_term2
                        );
                        if is_term2 {
                            // Handle trailing delimiter if allowed and present
                            if *allow_trailing && delimiter_match.is_some() {
                                frame.accumulated.push(delimiter_match.take().unwrap());
                                *delimiter_count += 1;
                            }
                            // Check min_delimiters at completion
                            if *delimiter_count < *min_delimiters {
                                // Transition to Combining to finalize Empty result
                                frame.end_pos = Some(frame.pos);
                                frame.state = FrameState::Combining;
                                stack.push(&mut frame);
                                return Ok(FrameResult::Done);
                            }
                            self.pos = *matched_idx;
                            // Transition to Combining to finalize DelimitedList result
                            frame.end_pos = Some(*matched_idx);
                            frame.state = FrameState::Combining;
                            stack.push(&mut frame);
                            return Ok(FrameResult::Done);
                        }
                        log::debug!(
                            "[ITERATIVE] Delimited: about to push child element at working_pos={}",
                            working_idx
                        );
                        // Create child for next element
                        // NOTE: We do NOT trim to the next delimiter position for element children.
                        // This is because the element itself might be a Delimited grammar that uses
                        // the same delimiter internally. Instead, we rely on the element's grammar
                        // to naturally stop at the correct position, and then check for a delimiter
                        // after the element completes.
                        log::debug!(
                            "[DELIM-DEBUG] Before creating element child: working_idx={}, matched_idx={}, max_idx={}",
                            *working_idx, *matched_idx, *max_idx
                        );
                        // let delimiter_max_idx = self.trim_to_terminator(*working_idx, &[(**delimiter).clone()]);
                        // log::debug!(
                        //     "[DELIM-DEBUG] After trim_to_terminator: delimiter_max_idx={}",
                        //     delimiter_max_idx
                        // );
                        // let child_max_idx = (*max_idx).min(delimiter_max_idx);
                        let child_max_idx = *max_idx;
                        log::debug!(
                            "[DELIM-DEBUG] Creating element child at pos={}, with max_idx={}",
                            *working_idx,
                            child_max_idx
                        );
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
                        // Python parity: Add delimiter as terminator for elements
                        // (same as in handle_delimited_initial)
                        let mut element_terminators = frame_terminators.clone();
                        element_terminators.push((**delimiter).clone());
                        let child_frame = ParseFrame::new_child(
                            stack.frame_id_counter,
                            child_grammar.into(),
                            *working_idx,
                            element_terminators, // Include delimiter as terminator!
                            Some(child_max_idx),
                        );
                        log::debug!("[ITERATIVE] Delimited: pushing child #2 at working_idx={}, frame_id={}", working_idx, stack.frame_id_counter);
                        ParseFrame::push_child_and_update_parent(
                            stack,
                            &mut frame,
                            child_frame,
                            "Delimited",
                        );
                        Ok(FrameResult::Done)
                    }
                }
            }
        }
    }

    /// Handle Delimited grammar Combining state - build final node from accumulated children.
    ///
    /// Called after all children have been collected in waiting_for_child state.
    /// Builds the final DelimitedList node and transitions to Complete state.
    pub(crate) fn handle_delimited_combining(
        &mut self,
        mut frame: ParseFrame,
    ) -> Result<crate::parser::iterative::FrameResult, ParseError> {
        let combine_end = frame.end_pos.unwrap_or(self.pos);
        log::debug!(
            "🔨 Delimited combining at pos {}-{} - frame_id={}, accumulated={}",
            frame.pos,
            combine_end.saturating_sub(1),
            frame.frame_id,
            frame.accumulated.len()
        );

        // Extract delimiter_count from context to determine if we should return Empty or DelimitedList
        let delimiter_count = if let FrameContext::Delimited {
            delimiter_count, ..
        } = &frame.context
        {
            *delimiter_count
        } else {
            0
        };

        // Extract min_delimiters from grammar
        let min_delimiters = if let FrameContext::Delimited { grammar, .. } = &frame.context {
            if let Grammar::Delimited { min_delimiters, .. } = grammar.as_ref() {
                *min_delimiters
            } else {
                0
            }
        } else {
            0
        };

        // The result is determined by delimiter_count vs min_delimiters:
        // - If delimiter_count < min_delimiters, return Empty (failed to meet requirement)
        // - Otherwise, return DelimitedList with accumulated children

        let result_node = if delimiter_count < min_delimiters {
            log::debug!(
                "Delimited combining with delimiter_count={} < min_delimiters={} → returning Node::Empty (not enough delimiters), frame_id={}",
                delimiter_count,
                min_delimiters,
                frame.frame_id
            );
            // Return empty list to indicate failure
            Node::DelimitedList { children: vec![] }
        } else {
            log::debug!(
                "Delimited combining with {} children, delimiter_count={} >= min_delimiters={} → building Node::DelimitedList, frame_id={}",
                frame.accumulated.len(),
                delimiter_count,
                min_delimiters,
                frame.frame_id
            );
            Node::DelimitedList {
                children: frame.accumulated.clone(),
            }
        };

        // Transition to Complete state with the final result
        let end_pos = frame.end_pos.unwrap_or(frame.pos);
        frame.state = FrameState::Complete(result_node);
        frame.end_pos = Some(end_pos);

        Ok(crate::parser::iterative::FrameResult::Push(frame))
    }
}
