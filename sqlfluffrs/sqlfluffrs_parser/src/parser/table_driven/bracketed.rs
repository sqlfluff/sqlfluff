use crate::vdebug;
use smallvec::SmallVec;
use sqlfluffrs_types::{GrammarId, ParseMode};
use std::sync::Arc;

use crate::parser::{
    table_driven::frame::{TableFrameResult, TableParseFrame, TableParseFrameStack},
    BracketedState, FrameContext, FrameState, MatchResult, ParseError, Parser,
};

impl Parser<'_> {
    pub(crate) fn handle_bracketed_table_driven_initial(
        &mut self,
        grammar_id: GrammarId,
        frame: TableParseFrame,
        parent_terminators: &[GrammarId],
        stack: &mut TableParseFrameStack,
    ) -> Result<TableFrameResult, ParseError> {
        vdebug!(
            "Bracketed[table] Initial: grammar_id={}, frame_id={}, pos={}",
            grammar_id,
            frame.frame_id,
            frame.pos
        );
        let start_idx = frame.pos;
        let local_terminators = self
            .grammar_ctx
            .terminators(grammar_id)
            .collect::<Vec<GrammarId>>();
        let reset_terminators = self.grammar_ctx.inst(grammar_id).flags.reset_terminators();
        let all_terminators = self.combine_table_terminators(
            &local_terminators,
            parent_terminators,
            reset_terminators,
        );
        let all_children: Vec<GrammarId> = self.grammar_ctx.children(grammar_id).collect();
        vdebug!(
            "Bracketed[table] children count={}, children={:?}",
            all_children.len(),
            all_children
        );
        if all_children.len() < 2 {
            vdebug!("Bracketed[table]: Not enough children (need bracket_pairs + elements)");
            stack.results.insert(
                frame.frame_id,
                (Arc::new(MatchResult::empty_at(start_idx)), start_idx, None),
            );
            return Ok(TableFrameResult::Done);
        }
        let (start_bracket_idx, _end_bracket_idx) = self.grammar_ctx.bracketed_config(grammar_id);
        let open_bracket_id = all_children[start_bracket_idx];
        initialize_table_driven_bracketed_frame(grammar_id, frame, stack, &all_terminators);
        let parent_max_idx = stack.last_mut().unwrap().parent_max_idx;
        let mut child_frame = create_table_driven_child_frame(
            stack.frame_id_counter,
            open_bracket_id,
            start_idx,
            &all_terminators,
            FrameContext::None,
            parent_max_idx,
            None, // No override for opening bracket
        );
        vdebug!(
            "Bracketed[table] pushed open_bracket child grammar_id={} at pos={} frame_id={}",
            open_bracket_id,
            start_idx,
            child_frame.frame_id
        );
        TableParseFrame::update_parent_last_child_id(stack, "Bracketed", stack.frame_id_counter);
        // update_parent_last_child_frame(stack);
        stack.increment_frame_id_counter();
        stack.push(&mut child_frame);
        Ok(TableFrameResult::Done) // Child pushed, continue main loop
    }

    /// Handle Bracketed WaitingForChild state using table-driven approach
    pub(crate) fn handle_bracketed_table_driven_waiting_for_child(
        &mut self,
        mut frame: TableParseFrame,
        child_match: &MatchResult,
        child_end_pos: &usize,
        stack: &mut TableParseFrameStack,
    ) -> Result<TableFrameResult, ParseError> {
        // Work with MatchResult directly (Python parity)
        let child_is_empty = child_match.is_empty();

        // Extract needed fields from frame.context
        let FrameContext::BracketedTableDriven {
            grammar_id,
            state: bracket_state,
            bracket_max_idx,
            last_child_frame_id,
            content_ids,
            content_idx,
            parse_mode_override,
        } = &mut frame.context
        else {
            unreachable!("Expected BracketedTableDriven context");
        };

        let all_children: Vec<GrammarId> = self.grammar_ctx.children(*grammar_id).collect();
        let (start_bracket_idx, end_bracket_idx) = self.grammar_ctx.bracketed_config(*grammar_id);
        let close_bracket_id = all_children[end_bracket_idx];
        let content_ids_local = all_children
            .iter()
            .cloned()
            .enumerate()
            .filter(|(idx, _id)| *idx != start_bracket_idx && *idx != end_bracket_idx)
            .map(|(_, id)| id)
            .collect::<Vec<_>>();

        vdebug!(
            "Bracketed[table] WaitingForChild: frame_id={}, child_empty={}, state={:?}, bracket_max_idx={:?}, content_ids_local={:?}, content_ids_frame={:?}, content_idx={}, last_child_frame_id={:?}",
            frame.frame_id,
            child_is_empty,
            bracket_state,
            bracket_max_idx,
            content_ids_local,
            content_ids,
            content_idx,
            last_child_frame_id
        );

        match bracket_state {
            BracketedState::MatchingOpen => {
                if child_is_empty {
                    self.pos = frame.pos;
                    vdebug!("Bracketed[table] returning Empty (no opening bracket)",);
                    // Transition to Combining to finalize Empty result
                    frame.end_pos = Some(frame.pos);
                    frame.state = FrameState::Combining;
                    stack.push(&mut frame);
                    return Ok(TableFrameResult::Done);
                }

                let grammar_inst = self.grammar_ctx.inst(frame.grammar_id);
                let allow_gaps = grammar_inst.flags.allow_gaps();
                // Check for parse_mode_override first (though Bracketed itself shouldn't be overridden,
                // this is here for completeness)
                let parse_mode = frame.parse_mode_override.unwrap_or(grammar_inst.parse_mode);

                vdebug!(
                    "Bracketed[table] MatchingOpen: grammar_id={}, parse_mode={:?}",
                    frame.grammar_id,
                    parse_mode
                );

                frame.accumulated.push(Arc::new(child_match.clone()));
                let content_start_idx = *child_end_pos;
                // Compute bracket_max_idx from the opening bracket's token position
                let computed_bracket_max_idx = if !child_match.matched_slice.is_empty() {
                    let token_idx = child_match.matched_slice.start;
                    self.get_matching_bracket_idx(token_idx)
                } else {
                    None
                };
                #[cfg(feature = "verbose-debug")]
                if let Some(close_idx) = computed_bracket_max_idx {
                    vdebug!(
                        "Bracketed: Using pre-computed closing bracket at idx={} as max_idx",
                        close_idx
                    );
                }
                // CRITICAL: Update the frame context's bracket_max_idx field!
                *bracket_max_idx = computed_bracket_max_idx;

                // If allow_gaps is false and there's whitespace after opening bracket, fail in STRICT mode
                if !allow_gaps && parse_mode == ParseMode::Strict {
                    if let Some(_ws_pos) = (content_start_idx..self.tokens.len())
                        .find(|&pos| !self.tokens[pos].is_code())
                    {
                        vdebug!("Bracketed: allow_gaps=false, found whitespace/newline at {}, failing in STRICT mode", _ws_pos);
                        self.pos = frame.pos;

                        // Transition to Combining to finalize Empty result
                        frame.end_pos = Some(frame.pos);
                        frame.state = FrameState::Combining;
                        stack.push(&mut frame);
                        return Ok(TableFrameResult::Done);
                    }
                }

                // Collect whitespace/newlines after opening bracket if allow_gaps
                if allow_gaps {
                    let code_idx =
                        self.skip_start_index_forward_to_code(content_start_idx, self.tokens.len());
                    for pos in content_start_idx..code_idx {
                        if let Some(tok) = self.tokens.get(pos) {
                            // Check if already collected globally
                            if self.collected_transparent_positions.contains(&pos) {
                                continue;
                            }
                            // PYTHON PARITY: Only collect end_of_file explicitly
                            // Whitespace, newlines, comments captured implicitly by apply()
                            match &*tok.get_type() {
                                "end_of_file" => {
                                    frame.accumulated.push(Arc::new(MatchResult {
                                        matched_slice: pos..pos + 1,
                                        matched_class: None, // Inferred from token type
                                        ..Default::default()
                                    }));
                                    self.mark_position_collected(pos);
                                }
                                "whitespace" | "newline" | "comment" => {
                                    vdebug!(
                                        "Bracketed[table]: Skipping explicit collection of {} at {} - will be captured as trailing",
                                        tok.get_type(),
                                        pos
                                    );
                                }
                                _ => {}
                            }
                        }
                    }
                    self.pos = code_idx;
                } else {
                    self.pos = content_start_idx;
                }

                // Transition to MatchingContent state
                *bracket_state = BracketedState::MatchingContent;

                // CRITICAL: If Bracketed is GREEDY, set parse_mode_override so content inherits it.
                // This matches Python behavior where Bracketed(parse_mode=GREEDY) inherits from
                // Sequence and passes parse_mode to all content elements.
                // Without this, content would use its own parse_mode (often STRICT), causing
                // the entire bracketed expression to fail on unparsable content instead of
                // creating granular unparsable sections.
                if parse_mode == ParseMode::Greedy {
                    *parse_mode_override = Some(ParseMode::Greedy);
                    vdebug!(
                        "Bracketed[table]: Setting parse_mode_override=Greedy for content (Bracketed is GREEDY)"
                    );
                }

                // CRITICAL: Store all content IDs in the frame context.
                // Multiple content grammars (e.g., DatatypeSegment, "AS", DatatypeSegment)
                // will be parsed sequentially as an implicit Sequence.
                *content_ids = content_ids_local.clone();
                *content_idx = 0;

                let content_grammar_id = if content_ids_local.is_empty() {
                    // No elements - skip to closing bracket
                    // update the state in the frame context to MatchingClose
                    vdebug!("DEBUG: Transitioning to MatchingClose!");
                    *bracket_state = BracketedState::MatchingClose;
                    let parent_limit = frame.parent_max_idx;
                    vdebug!(
                        "DEBUG: Creating closing bracket child at pos={}, parent_limit={:?}",
                        self.pos,
                        parent_limit
                    );
                    let mut close_frame = create_table_driven_child_frame(
                        stack.frame_id_counter,
                        close_bracket_id,
                        self.pos,
                        &[close_bracket_id],
                        FrameContext::None,
                        parent_limit,
                        None, // No override for closing bracket
                    );

                    *last_child_frame_id = Some(stack.frame_id_counter);
                    stack.increment_frame_id_counter();
                    stack.push(&mut frame);
                    stack.push(&mut close_frame);
                    return Ok(TableFrameResult::Done);
                } else {
                    // Start with the first content element
                    vdebug!(
                        "Bracketed[table]: content_ids.len()={}, starting with element 0",
                        content_ids_local.len()
                    );
                    content_ids_local[0]
                };

                // Push content frame
                // NOTE: We do NOT pass close_bracket_id as a terminator!
                // This is important because nested brackets (like COUNT(*)) would
                // incorrectly match the terminator and cause early termination.
                // Instead, we rely on bracket_max_idx to constrain parsing via parent_max_idx.
                let context = FrameContext::BracketedTableDriven {
                    grammar_id: *grammar_id,
                    state: BracketedState::MatchingContent,
                    last_child_frame_id: *last_child_frame_id,
                    bracket_max_idx: *bracket_max_idx,
                    content_ids: content_ids.clone(),
                    content_idx: *content_idx,
                    parse_mode_override: *parse_mode_override,
                };
                let mut child_frame = create_table_driven_child_frame(
                    stack.frame_id_counter,
                    content_grammar_id,
                    self.pos,
                    &[], // Don't pass close bracket as terminator - use bracket_max_idx instead
                    context,
                    *bracket_max_idx,
                    *parse_mode_override, // Pass override to content
                );
                *last_child_frame_id = Some(stack.frame_id_counter);
                stack.increment_frame_id_counter();
                stack.push(&mut frame);
                stack.push(&mut child_frame);
                Ok(TableFrameResult::Done)
            }
            BracketedState::MatchingContent => {
                // Python reference: sequence.py Bracketed.match() lines ~530-570
                // In Python, Bracketed doesn't pre-compute the closing bracket position.
                // Instead, it lets Sequence.match() handle the content (which may return
                // unparsable segments in GREEDY mode), then matches the closing bracket.
                // This Rust logic optimizes by pre-computing the bracket position, but
                // must still respect GREEDY mode semantics.
                let grammar_inst = self.grammar_ctx.inst(frame.grammar_id);
                // Check for parse_mode_override first (though Bracketed itself shouldn't be overridden,
                // this is here for completeness)
                let parse_mode = frame.parse_mode_override.unwrap_or(grammar_inst.parse_mode);
                let allow_gaps = grammar_inst.flags.allow_gaps();
                let (_start_bracket_idx, end_bracket_idx) =
                    self.grammar_ctx.bracketed_config(*grammar_id);
                let close_bracket_id = all_children[end_bracket_idx];

                // Python parity: If child_match has child_matches, flatten them into accumulated.
                // If it's a wrapper (Ref, Sequence), we want the children, not the wrapper.
                if !child_is_empty {
                    if child_match.matched_class.is_some() && !child_match.child_matches.is_empty()
                    {
                        // Has a matched_class and children - add the whole match
                        frame.accumulated.push(Arc::new(child_match.clone()));
                    } else if !child_match.child_matches.is_empty() {
                        // No matched_class but has children - flatten the children
                        frame
                            .accumulated
                            .extend(child_match.child_matches.iter().cloned());
                    } else {
                        // Leaf match - add it directly
                        frame.accumulated.push(Arc::new(child_match.clone()));
                    }
                }

                let gap_start = *child_end_pos;
                self.pos = gap_start;
                vdebug!(
                    "DEBUG: After content, gap_start={}, current_pos={}",
                    gap_start,
                    self.pos
                );

                if allow_gaps {
                    let code_idx =
                        self.skip_start_index_forward_to_code(gap_start, self.tokens.len());
                    vdebug!(
                        "[BRACKET-DEBUG] After content, gap_start={}, code_idx={}, token at gap_start={:?}, token at code_idx={:?}",
                        gap_start, code_idx,
                        self.tokens.get(gap_start).map(|t| t.raw()),
                        self.tokens.get(code_idx).map(|t| t.raw()),
                    );
                    for pos in self.pos..code_idx {
                        if let Some(tok) = self.tokens.get(pos) {
                            // Check if already collected globally
                            if self.collected_transparent_positions.contains(&pos) {
                                continue;
                            }
                            let tok_type = tok.get_type();
                            // PYTHON PARITY: Only collect end_of_file explicitly
                            // Whitespace, newlines, comments captured implicitly by apply()
                            if tok_type == "end_of_file" {
                                frame.accumulated.push(Arc::new(MatchResult {
                                    matched_slice: pos..pos + 1,
                                    matched_class: None, // Inferred from token type
                                    ..Default::default()
                                }));
                                self.mark_position_collected(pos);
                            } else if tok_type == "whitespace"
                                || tok_type == "newline"
                                || tok_type == "comment"
                            {
                                vdebug!(
                                    "Bracketed[table]: Skipping explicit collection of {} at {} - will be captured as trailing",
                                    tok_type,
                                    pos
                                );
                            }
                        }
                    }
                    self.pos = code_idx;
                }
                vdebug!(
                    "DEBUG: Checking for more content or closing bracket - self.pos={}, content_idx={}, content_ids.len()={}, tokens.len={}",
                    self.pos,
                    *content_idx,
                    content_ids.len(),
                    self.tokens.len()
                );

                // CRITICAL: Check if there are more content elements to parse
                // Continue parsing even if current element returned Empty (optional elements)
                if *content_idx + 1 < content_ids.len() {
                    // More content elements remain - parse the next one
                    *content_idx += 1;
                    let next_content_id = content_ids[*content_idx];
                    vdebug!(
                        "Attempting MatchingContent: content_idx={}, content_ids.len()={}, child_empty={}, next_content_id={:?}",
                        *content_idx,
                        content_ids.len(),
                        child_is_empty,
                        next_content_id.0
                    );

                    // Stay in MatchingContent state and push next content child
                    // NOTE: We do NOT pass close_bracket_id as a terminator!
                    // This is important because nested brackets (like convert(varchar, col, 23))
                    // would incorrectly match the terminator and cause early termination.
                    // Instead, we rely on bracket_max_idx to constrain parsing via parent_max_idx.
                    let context = FrameContext::BracketedTableDriven {
                        grammar_id: *grammar_id,
                        state: BracketedState::MatchingContent,
                        last_child_frame_id: *last_child_frame_id,
                        bracket_max_idx: *bracket_max_idx,
                        content_ids: content_ids.clone(),
                        content_idx: *content_idx,
                        parse_mode_override: *parse_mode_override,
                    };
                    let mut child_frame = create_table_driven_child_frame(
                        stack.frame_id_counter,
                        next_content_id,
                        self.pos,
                        &[], // Don't pass close bracket as terminator - use bracket_max_idx instead
                        context,
                        *bracket_max_idx,
                        *parse_mode_override, // Pass override to content
                    );
                    *last_child_frame_id = Some(stack.frame_id_counter);
                    stack.increment_frame_id_counter();
                    stack.push(&mut frame);
                    stack.push(&mut child_frame);
                    return Ok(TableFrameResult::Done);
                }

                // All content elements parsed or current element failed - try closing bracket
                if self.pos >= self.tokens.len()
                    || self.peek().is_some_and(|t| t.get_type() == "end_of_file")
                {
                    vdebug!("DEBUG: No closing bracket found!");
                    if parse_mode == ParseMode::Strict {
                        self.pos = frame.pos;
                        // Transition to Combining to finalize Empty result
                        frame.end_pos = Some(frame.pos);
                        frame.state = FrameState::Combining;
                        stack.push(&mut frame);
                        Ok(TableFrameResult::Done)
                    } else {
                        // GREEDY mode: Create parse error result for unclosed bracket
                        // Python parity: raises SQLParseError which gets caught and converted to violation
                        vdebug!(
                            "Bracketed[table] GREEDY mode: No closing bracket found at EOF, creating parse error result"
                        );

                        // Create error result with position at opening bracket
                        // PYTHON PARITY: Message must match Python's SQLParseError message exactly
                        let error_match = MatchResult::with_error(
                            frame.pos,
                            self.pos,
                            "Couldn't find closing bracket for opening bracket.".to_string(),
                            frame.pos, // Error at opening bracket position
                        );

                        self.commit_collection_checkpoint(frame.frame_id);
                        stack
                            .results
                            .insert(frame.frame_id, (Arc::new(error_match), self.pos, None));
                        return Ok(TableFrameResult::Done);
                    }
                } else {
                    // STRICT mode check: All content elements must end at the closing bracket position
                    // This check should only happen AFTER all content elements have been processed.
                    let check_pos =
                        self.skip_start_index_forward_to_code(self.pos, self.tokens.len());
                    if let Some(expected_close_pos) = *bracket_max_idx {
                        if check_pos != expected_close_pos {
                            if parse_mode == ParseMode::Strict {
                                vdebug!("Bracketed[table] STRICT mode: content did not end at closing bracket (check_pos={}, expected={}), returning Empty for retry. frame_id={}, frame.pos={}", check_pos, expected_close_pos, frame.frame_id, frame.pos);
                                self.pos = frame.pos;
                                // Transition to Combining to finalize Empty result
                                frame.end_pos = Some(frame.pos);
                                frame.state = FrameState::Combining;
                                stack.push(&mut frame);
                                return Ok(TableFrameResult::Done);
                            } else {
                                // GREEDY mode: Create unparsable section for tokens between content end and closing bracket
                                vdebug!(
                                    "Bracketed[table] GREEDY mode: Creating unparsable section for tokens {}..{} (content ended at {}, closing bracket at {})",
                                    check_pos, expected_close_pos, check_pos, expected_close_pos
                                );

                                // Create an UnparsableSegment for the tokens we couldn't parse
                                let mut segment_kwargs = hashbrown::HashMap::new();
                                segment_kwargs
                                    .insert("expected".to_string(), "Nothing here.".to_string());

                                let unparsable_match = MatchResult {
                                    matched_slice: check_pos..expected_close_pos,
                                    matched_class: Some("UnparsableSegment".to_string()),
                                    segment_kwargs,
                                    ..Default::default()
                                };
                                frame.accumulated.push(Arc::new(unparsable_match));

                                // Move position to the closing bracket
                                self.pos = expected_close_pos;
                            }
                        } else {
                            vdebug!("[BRACKET-DEBUG] Bracketed content ends at expected closing bracket (check_pos == expected_close_pos)");
                        }
                    }

                    vdebug!("DEBUG: All content elements parsed, transitioning to MatchingClose!");
                    *bracket_state = BracketedState::MatchingClose;
                    let parent_limit = frame.parent_max_idx;
                    vdebug!(
                        "DEBUG: Creating closing bracket child at pos={}, parent_limit={:?}",
                        self.pos,
                        parent_limit
                    );
                    let mut child_frame = create_table_driven_child_frame(
                        stack.frame_id_counter,
                        close_bracket_id,
                        self.pos,
                        &[close_bracket_id],
                        FrameContext::None,
                        parent_limit,
                        None, // No override for closing bracket
                    );
                    *last_child_frame_id = Some(stack.frame_id_counter);
                    stack.increment_frame_id_counter();
                    stack.push(&mut frame);
                    stack.push(&mut child_frame);
                    Ok(TableFrameResult::Done)
                }
            }
            BracketedState::MatchingClose => {
                vdebug!(
                    "DEBUG: Bracketed[table] MatchingClose - child_is_empty={}, child_end_pos={}",
                    child_is_empty,
                    child_end_pos
                );
                let grammar_inst = self.grammar_ctx.inst(frame.grammar_id);
                // Check for parse_mode_override first (though Bracketed itself shouldn't be overridden,
                // this is here for completeness)
                let parse_mode = frame.parse_mode_override.unwrap_or(grammar_inst.parse_mode);

                if child_is_empty {
                    if parse_mode == ParseMode::Strict {
                        self.pos = frame.pos;
                        frame.end_pos = Some(frame.pos);
                        // Transition to Combining to finalize Empty result
                        frame.state = FrameState::Combining;
                        stack.push(&mut frame);
                        return Ok(TableFrameResult::Done);
                    } else {
                        // GREEDY mode: Closing bracket not found - raise parse error
                        // PYTHON PARITY: This matches Python's behavior where Bracketed.match()
                        // raises SQLParseError("Couldn't find closing bracket for opening bracket.")
                        vdebug!(
                            "Bracketed[table] GREEDY mode: Couldn't find closing bracket for opening bracket at pos {}, frame_id={}",
                            frame.pos,
                            frame.frame_id
                        );

                        // Create error result with position at opening bracket
                        let error_match = MatchResult::with_error(
                            frame.pos,
                            self.pos,
                            "Couldn't find closing bracket for opening bracket.".to_string(),
                            frame.pos, // Error at opening bracket position
                        );

                        self.commit_collection_checkpoint(frame.frame_id);
                        stack
                            .results
                            .insert(frame.frame_id, (Arc::new(error_match), self.pos, None));
                        return Ok(TableFrameResult::Done);
                    }
                } else {
                    frame.accumulated.push(Arc::new(child_match.clone()));
                    self.pos = *child_end_pos;
                    vdebug!(
                        "Bracketed[table] SUCCESS: {} children, transitioning to Combining at frame_id={}",
                        frame.accumulated.len(),
                        frame.frame_id
                    );
                    // Mark as Complete so the combining handler knows this is a successful match
                    *bracket_state = BracketedState::Complete;
                    frame.end_pos = Some(*child_end_pos);
                }
                // Transition to Combining to finalize result
                frame.state = FrameState::Combining;
                stack.push(&mut frame);
                Ok(TableFrameResult::Done)
            }
            BracketedState::Complete => {
                unreachable!(
                    "BracketedState::Complete should not occur in WaitingForChild handler"
                );
            }
        }
    }

    /// Handle Bracketed grammar Combining state - build final node from accumulated children.
    ///
    /// Called after all children have been collected in waiting_for_child state.
    /// Builds the final Bracketed node and transitions to Complete state.
    pub(crate) fn handle_bracketed_table_driven_combining(
        &mut self,
        mut frame: TableParseFrame,
    ) -> Result<TableFrameResult, ParseError> {
        #[cfg(feature = "verbose-debug")]
        let combine_end = frame.end_pos.unwrap_or(self.pos);
        vdebug!(
            "🔨 Bracketed combining at pos {}-{} - frame_id={}, accumulated={}",
            frame.pos,
            combine_end.saturating_sub(1),
            frame.frame_id,
            frame.accumulated.len()
        );

        // Extract the bracketed state and grammar from the frame context
        let (is_complete, bracket_persists) =
            if let FrameContext::BracketedTableDriven {
                state, grammar_id, ..
            } = &frame.context
            {
                let complete = matches!(state, BracketedState::Complete);

                // Determine bracket_persists using the GrammarInst for this GrammarId
                let persists = self.grammar_ctx.bracketed_persists(*grammar_id);

                (complete, persists)
            } else {
                (false, true)
            };

        // The result is determined by the bracketed state:
        // - If state is Complete, we successfully matched all parts (open + content + close)
        // - Otherwise, the match failed at some point and we return Empty

        let end_pos = frame.end_pos.unwrap_or(frame.pos);
        let result_match = if is_complete {
            vdebug!(
                "Bracketed combining with COMPLETE state → building MatchResult::bracketed, frame_id={}, bracket_persists={}",
                frame.frame_id,
                bracket_persists
            );
            // Use lazy evaluation - store child_matches instead of building Node
            let accumulated = std::mem::take(&mut frame.accumulated);
            MatchResult::bracketed(frame.pos, end_pos, accumulated.into_vec(), bracket_persists)
        } else {
            // Log the actual state for debugging
            #[cfg(feature = "verbose-debug")]
            let state_str = if let FrameContext::BracketedTableDriven { state, .. } = &frame.context
            {
                format!("{:?}", state)
            } else {
                "Unknown".to_string()
            };
            vdebug!(
                "Bracketed combining with INCOMPLETE state ({}) → returning Empty, frame_id={}, accumulated={}",
                state_str,
                frame.frame_id,
                frame.accumulated.len()
            );
            MatchResult::empty_at(frame.pos)
        };

        // Transition to Complete state with the final result
        frame.state = FrameState::Complete(Arc::new(result_match));
        frame.end_pos = Some(end_pos);

        Ok(TableFrameResult::Push(frame))
    }
}

fn initialize_table_driven_bracketed_frame(
    grammar_id: GrammarId,
    mut frame: TableParseFrame,
    stack: &mut TableParseFrameStack,
    all_terminators: &[GrammarId],
) {
    // Update frame with Bracketed context
    frame.state = FrameState::WaitingForChild {
        child_index: 0,
        total_children: 3, // open, content, close
    };
    frame.context = FrameContext::BracketedTableDriven {
        grammar_id,
        state: BracketedState::MatchingOpen,
        last_child_frame_id: None,
        bracket_max_idx: None,
        content_ids: Vec::new(), // Will be populated later
        content_idx: 0,
        parse_mode_override: None, // Will be set when creating content frames
    };
    frame.table_terminators = SmallVec::from_slice(all_terminators);
    stack.push(&mut frame);
}

fn create_table_driven_child_frame(
    frame_id: usize,
    grammar_id: GrammarId,
    start_idx: usize,
    terminators: &[GrammarId],
    context: FrameContext,
    parent_max_idx: Option<usize>,
    parse_mode_override: Option<ParseMode>,
) -> TableParseFrame {
    TableParseFrame {
        frame_id,
        grammar_id,
        pos: start_idx,
        table_terminators: smallvec::SmallVec::from_slice(terminators),
        state: FrameState::Initial,
        accumulated: smallvec::SmallVec::new(),
        context,
        parent_max_idx, // Propagate parent's limit!
        calculated_max_idx: None,
        end_pos: None,
        transparent_positions: None,
        element_key: None,
        parse_mode_override, // Propagate parse mode override!
    }
}
