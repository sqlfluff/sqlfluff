use crate::{parser::match_result::MatchedClass, vdebug};
use smallvec::SmallVec;
use sqlfluffrs_types::{GrammarId, GrammarVariant, ParseMode};
use std::sync::Arc;

use crate::parser::{
    table_driven::frame::{TableFrameResult, TableParseFrame, TableParseFrameStack},
    BracketedState, FrameContext, FrameState, MatchResult, ParseError, Parser,
};

impl Parser<'_> {
    pub(crate) fn handle_bracketed_table_driven_initial(
        &mut self,
        frame: TableParseFrame,
        stack: &mut TableParseFrameStack,
    ) -> Result<TableFrameResult, ParseError> {
        let grammar_id = frame.grammar_id;
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
            &frame.table_terminators,
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
            return Ok(stack.complete_frame_empty(&frame));
        }
        let (start_bracket_idx, _end_bracket_idx) = self.grammar_ctx.bracketed_config(grammar_id);
        let open_bracket_id = all_children[start_bracket_idx];
        initialize_table_driven_bracketed_frame(grammar_id, frame, stack, &all_terminators);
        let parent_max_idx = stack.last_mut().unwrap().parent_max_idx;
        let child_frame = create_table_driven_child_frame(
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
        stack.update_parent_last_child_id(GrammarVariant::Bracketed, stack.frame_id_counter);
        // update_parent_last_child_frame(stack);
        stack.increment_frame_id_counter();
        stack.push(child_frame);
        Ok(TableFrameResult::Done) // Child pushed, continue main loop
    }

    /// Handle Bracketed WaitingForChild state using table-driven approach
    pub(crate) fn handle_bracketed_table_driven_waiting_for_child(
        &mut self,
        mut frame: TableParseFrame,
        child_match: &Arc<MatchResult>,
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
            child_matches,
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
                    stack.push(frame);
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

                child_matches.push(Arc::clone(child_match));
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
                        stack.push(frame);
                        return Ok(TableFrameResult::Done);
                    }
                }

                // Skip whitespace/newlines after opening bracket if allow_gaps
                self.pos = if allow_gaps {
                    self.skip_start_index_forward_to_code(content_start_idx, self.tokens.len())
                } else {
                    content_start_idx
                };

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
                *content_ids = content_ids_local; // Move instead of clone
                *content_idx = 0;

                // Consume any leading Meta content elements inline.
                // Meta grammar elements must not be pushed as child frames - handle them directly
                // so the parser never hits the "Meta grammar should be consumed by a sequence or
                // bracketed" warning path in iterative.rs.
                while *content_idx < content_ids.len()
                    && self.grammar_ctx.variant(content_ids[*content_idx]) == GrammarVariant::Meta
                {
                    vdebug!(
                        "Bracketed[table]: consuming leading Meta at content_idx={} inline",
                        *content_idx
                    );
                    if let Some(meta_seg) =
                        self.grammar_id_to_meta_segment(content_ids[*content_idx])
                    {
                        let meta_match = MatchResult {
                            matched_slice: self.pos..self.pos,
                            insert_segments: vec![(self.pos, meta_seg)],
                            ..Default::default()
                        };
                        child_matches.push(Arc::new(meta_match));
                    }
                    *content_idx += 1;
                }

                let content_grammar_id = if *content_idx >= content_ids.len() {
                    // No (remaining) elements - skip to closing bracket
                    // update the state in the frame context to MatchingClose
                    vdebug!("DEBUG: Transitioning to MatchingClose!");
                    *bracket_state = BracketedState::MatchingClose;
                    let parent_limit = frame.parent_max_idx;
                    vdebug!(
                        "DEBUG: Creating closing bracket child at pos={}, parent_limit={:?}",
                        self.pos,
                        parent_limit
                    );
                    let close_frame = create_table_driven_child_frame(
                        stack.frame_id_counter,
                        close_bracket_id,
                        self.pos,
                        &[close_bracket_id],
                        FrameContext::None,
                        parent_limit,
                        None, // No override for closing bracket
                    );

                    *last_child_frame_id = Some(stack.frame_id_counter);
                    return Ok(stack.push_child_and_wait(frame, close_frame, 0));
                } else {
                    // Start with the first non-Meta content element
                    vdebug!(
                        "Bracketed[table]: content_ids.len()={}, starting with element {}",
                        content_ids.len(),
                        *content_idx
                    );
                    content_ids[*content_idx]
                };

                // Push content frame
                // NOTE: We do NOT pass close_bracket_id as a terminator!
                // This is important because nested brackets (like COUNT(*)) would
                // incorrectly match the terminator and cause early termination.
                // Instead, we rely on bracket_max_idx to constrain parsing via parent_max_idx.
                // NOTE: The child frame's context is always overwritten by the handler that
                // processes it (Sequence, OneOf, etc.), so we pass None to avoid cloning
                // content_ids and child_matches into dead storage.
                let child_frame = create_table_driven_child_frame(
                    stack.frame_id_counter,
                    content_grammar_id,
                    self.pos,
                    &[], // Don't pass close bracket as terminator - use bracket_max_idx instead
                    FrameContext::None,
                    *bracket_max_idx,
                    *parse_mode_override, // Pass override to content
                );
                *last_child_frame_id = Some(stack.frame_id_counter);
                Ok(stack.push_child_and_wait(frame, child_frame, 0))
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
                        child_matches.push(Arc::clone(child_match));
                    } else if !child_match.child_matches.is_empty() {
                        // No matched_class but has children - flatten the children
                        child_matches.extend(child_match.child_matches.iter().cloned());
                    } else {
                        // Leaf match - add it directly
                        child_matches.push(Arc::clone(child_match));
                    }
                }

                self.pos = if allow_gaps {
                    self.skip_start_index_forward_to_code(*child_end_pos, self.tokens.len())
                } else {
                    *child_end_pos
                };
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

                    // Consume consecutive Meta elements inline, same reasoning as above.
                    while *content_idx < content_ids.len()
                        && self.grammar_ctx.variant(content_ids[*content_idx])
                            == GrammarVariant::Meta
                    {
                        vdebug!(
                            "Bracketed[table]: consuming Meta at content_idx={} inline",
                            *content_idx
                        );
                        if let Some(meta_seg) =
                            self.grammar_id_to_meta_segment(content_ids[*content_idx])
                        {
                            let meta_match = MatchResult {
                                matched_slice: self.pos..self.pos,
                                insert_segments: vec![(self.pos, meta_seg)],
                                ..Default::default()
                            };
                            child_matches.push(Arc::new(meta_match));
                        }
                        *content_idx += 1;
                    }

                    if *content_idx < content_ids.len() {
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
                        // NOTE: The child frame's context is always overwritten by the handler that
                        // processes it, so we pass None to avoid cloning content_ids and child_matches.
                        let child_frame = create_table_driven_child_frame(
                            stack.frame_id_counter,
                            next_content_id,
                            self.pos,
                            &[], // Don't pass close bracket as terminator - use bracket_max_idx instead
                            FrameContext::None,
                            *bracket_max_idx,
                            *parse_mode_override, // Pass override to content
                        );
                        *last_child_frame_id = Some(stack.frame_id_counter);
                        return Ok(stack.push_child_and_wait(frame, child_frame, 0));
                    }
                    // All remaining content elements were Meta - fall through to MatchingClose
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
                        stack.push(frame);
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

                        stack.insert_result(frame.frame_id, error_match, self.pos);
                        Ok(TableFrameResult::Done)
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
                                stack.push(frame);
                                return Ok(TableFrameResult::Done);
                            } else {
                                // GREEDY mode: Create unparsable section for tokens between content end and closing bracket
                                vdebug!(
                                    "Bracketed[table] GREEDY mode: Creating unparsable section for tokens {}..{} (content ended at {}, closing bracket at {})",
                                    check_pos, expected_close_pos, check_pos, expected_close_pos
                                );

                                // Create an UnparsableSegment for the tokens we couldn't parse
                                let unparsable_match = MatchResult {
                                    matched_slice: check_pos..expected_close_pos,
                                    matched_class: Some(MatchedClass::unparsable(
                                        "Nothing here.",
                                        expected_close_pos,
                                    )),
                                    ..Default::default()
                                };
                                child_matches.push(Arc::new(unparsable_match));

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
                    let child_frame = create_table_driven_child_frame(
                        stack.frame_id_counter,
                        close_bracket_id,
                        self.pos,
                        &[close_bracket_id],
                        FrameContext::None,
                        parent_limit,
                        None, // No override for closing bracket
                    );
                    *last_child_frame_id = Some(stack.frame_id_counter);
                    Ok(stack.push_child_and_wait(frame, child_frame, 0))
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
                        stack.push(frame);
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

                        stack.insert_result(frame.frame_id, error_match, self.pos);
                        return Ok(TableFrameResult::Done);
                    }
                } else {
                    child_matches.push(Arc::clone(child_match));
                    self.pos = *child_end_pos;
                    vdebug!(
                        "Bracketed[table] SUCCESS: {} children, transitioning to Combining at frame_id={}",
                        child_matches.len(),
                        frame.frame_id
                    );
                    // Mark as Complete so the combining handler knows this is a successful match
                    *bracket_state = BracketedState::Complete;
                    frame.end_pos = Some(*child_end_pos);
                }
                // Transition to Combining to finalize result
                frame.state = FrameState::Combining;
                stack.push(frame);
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
        stack: &mut TableParseFrameStack,
    ) -> Result<TableFrameResult, ParseError> {
        // Extract the bracketed state and grammar from the frame context
        let (is_complete, bracket_persists, child_matches) =
            if let FrameContext::BracketedTableDriven {
                state,
                grammar_id,
                child_matches,
                ..
            } = &mut frame.context
            {
                let complete = matches!(state, BracketedState::Complete);

                // Determine bracket_persists using the GrammarInst for this GrammarId
                let persists = self.grammar_ctx.bracketed_persists(*grammar_id);

                (complete, persists, std::mem::take(child_matches))
            } else {
                panic!("Expected BracketedTableDriven context in combining state");
            };

        #[cfg(feature = "verbose-debug")]
        let combine_end = frame.end_pos.unwrap_or(self.pos);
        vdebug!(
            "🔨 Bracketed combining at pos {}-{} - frame_id={}, accumulated={}",
            frame.pos,
            combine_end.saturating_sub(1),
            frame.frame_id,
            child_matches.len()
        );

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
            MatchResult::bracketed(frame.pos, end_pos, child_matches, bracket_persists)
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
                child_matches.len()
            );
            return Ok(stack.complete_frame_empty(&frame));
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
    frame.state = FrameState::WaitingForChild { child_index: 0 };
    frame.context = FrameContext::BracketedTableDriven {
        grammar_id,
        state: BracketedState::MatchingOpen,
        last_child_frame_id: None,
        bracket_max_idx: None,
        content_ids: Vec::new(), // Will be populated later
        content_idx: 0,
        parse_mode_override: None, // Will be set when creating content frames
        child_matches: Vec::new(),
    };
    frame.table_terminators = SmallVec::from_slice(all_terminators);
    stack.push(frame);
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
        context,
        parent_max_idx, // Propagate parent's limit!
        calculated_max_idx: None,
        end_pos: None,
        transparent_positions: None,
        element_key: None,
        parse_mode_override, // Propagate parse mode override!
    }
}
