use sqlfluffrs_types::{GrammarId, GrammarVariant, ParseMode};

use crate::parser::{
    table_driven::frame::{TableFrameResult, TableParseFrame, TableParseFrameStack},
    BracketedState, DelimitedState, FrameContext, FrameState, Node, ParseError, Parser,
};

impl<'a> Parser<'_> {
    pub(crate) fn handle_bracketed_table_driven_initial(
        &mut self,
        grammar_id: GrammarId,
        mut frame: TableParseFrame,
        parent_terminators: &[GrammarId],
        stack: &mut TableParseFrameStack,
    ) -> Result<TableFrameResult, ParseError> {
        log::debug!(
            "Bracketed[table] Initial: grammar_id={}, frame_id={}, pos={}",
            grammar_id,
            frame.frame_id,
            frame.pos
        );
        let ctx = self.grammar_ctx.expect("GrammarContext required");
        let start_idx = frame.pos;
        let local_terminators = ctx.terminators(grammar_id).collect::<Vec<GrammarId>>();
        let reset_terminators = ctx.inst(grammar_id).flags.reset_terminators();
        let all_terminators = self.combine_table_terminators(
            &local_terminators,
            parent_terminators,
            reset_terminators,
        );
        let all_children: Vec<GrammarId> = ctx.children(grammar_id).collect();
        log::debug!(
            "Bracketed[table] children count={}, children={:?}",
            all_children.len(),
            all_children
        );
        if all_children.len() < 2 {
            log::debug!("Bracketed[table]: Not enough children (need bracket_pairs + elements)");
            stack
                .results
                .insert(frame.frame_id, (Node::Empty, start_idx, None));
            return Ok(TableFrameResult::Done);
        }
        let (start_bracket_idx, _end_bracket_idx) = ctx.bracketed_config(grammar_id);
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
        );
        log::debug!(
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
        child_node: &Node,
        child_end_pos: &usize,
        stack: &mut TableParseFrameStack,
    ) -> Result<TableFrameResult, ParseError> {
        let ctx = self.grammar_ctx.expect("GrammarContext required");
        // Extract needed fields from frame.context
        let FrameContext::BracketedTableDriven {
            grammar_id,
            state: bracket_state,
            bracket_max_idx,
            last_child_frame_id,
            content_ids,
            content_idx,
        } = &mut frame.context
        else {
            unreachable!("Expected BracketedTableDriven context");
        };

        let all_children: Vec<GrammarId> = ctx.children(*grammar_id).collect();
        let (start_bracket_idx, end_bracket_idx) = ctx.bracketed_config(*grammar_id);
        let close_bracket_id = all_children[end_bracket_idx];
        let content_ids_local = all_children
            .iter()
            .cloned()
            .enumerate()
            .filter(|(idx, _id)| *idx != start_bracket_idx && *idx != end_bracket_idx)
            .map(|(_, id)| id)
            .collect::<Vec<_>>();

        log::debug!(
            "Bracketed[table] WaitingForChild: frame_id={}, child_empty={}, state={:?}, bracket_max_idx={:?}, content_ids_local={:?}, content_ids_frame={:?}, content_idx={}, last_child_frame_id={:?}",
            frame.frame_id,
            child_node.is_empty(),
            bracket_state,
            bracket_max_idx,
            content_ids_local,
            content_ids,
            content_idx,
            last_child_frame_id
        );

        match bracket_state {
            BracketedState::MatchingOpen => {
                if child_node.is_empty() {
                    self.pos = frame.pos;
                    log::debug!("Bracketed[table] returning Empty (no opening bracket)",);
                    // Transition to Combining to finalize Empty result
                    frame.end_pos = Some(frame.pos);
                    frame.state = FrameState::Combining;
                    stack.push(&mut frame);
                    return Ok(TableFrameResult::Done);
                }

                let ctx = self.grammar_ctx.expect("GrammarContext required");
                let grammar_inst = ctx.inst(frame.grammar_id);
                let allow_gaps = grammar_inst.flags.allow_gaps();
                let parse_mode = grammar_inst.parse_mode;

                frame.accumulated.push(child_node.clone());
                let content_start_idx = *child_end_pos;
                // Compute and UPDATE the frame context's bracket_max_idx from the opening bracket
                let computed_bracket_max_idx = child_node
                    .get_token_idx()
                    .and_then(|i| self.get_matching_bracket_idx(i));
                if let Some(close_idx) = computed_bracket_max_idx {
                    log::debug!(
                        "Bracketed: Using pre-computed closing bracket at idx={} as max_idx",
                        close_idx
                    );
                }
                // CRITICAL: Update the frame context's bracket_max_idx field!
                *bracket_max_idx = computed_bracket_max_idx;

                // If allow_gaps is false and there's whitespace after opening bracket, fail in STRICT mode
                if !allow_gaps && parse_mode == ParseMode::Strict {
                    if let Some(ws_pos) = (content_start_idx..self.tokens.len())
                        .find(|&pos| !self.tokens[pos].is_code())
                    {
                        log::debug!("Bracketed: allow_gaps=false, found whitespace/newline at {}, failing in STRICT mode", ws_pos);
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
                            match &*tok.get_type() {
                                "whitespace" => frame.accumulated.push(Node::Whitespace {
                                    raw: tok.raw().to_string(),
                                    token_idx: pos,
                                }),
                                "newline" => frame.accumulated.push(Node::Newline {
                                    raw: tok.raw().to_string(),
                                    token_idx: pos,
                                }),
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

                // CRITICAL: Store all content IDs in the frame context.
                // Multiple content grammars (e.g., DatatypeSegment, "AS", DatatypeSegment)
                // will be parsed sequentially as an implicit Sequence.
                *content_ids = content_ids_local.clone();
                *content_idx = 0;

                let content_grammar_id = if content_ids_local.is_empty() {
                    // No elements - skip to closing bracket
                    // update the state in the frame context to MatchingClose
                    log::debug!("DEBUG: Transitioning to MatchingClose!");
                    *bracket_state = BracketedState::MatchingClose;
                    let parent_limit = frame.parent_max_idx;
                    log::debug!(
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
                    );

                    *last_child_frame_id = Some(stack.frame_id_counter);
                    stack.increment_frame_id_counter();
                    stack.push(&mut frame);
                    stack.push(&mut close_frame);
                    return Ok(TableFrameResult::Done);
                } else {
                    // Start with the first content element
                    log::debug!(
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
                };
                let mut child_frame = create_table_driven_child_frame(
                    stack.frame_id_counter,
                    content_grammar_id,
                    self.pos,
                    &[], // Don't pass close bracket as terminator - use bracket_max_idx instead
                    context,
                    *bracket_max_idx,
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
                let ctx = self.grammar_ctx.expect("GrammarContext required");
                let grammar_inst = ctx.inst(frame.grammar_id);
                let parse_mode = grammar_inst.parse_mode;
                let allow_gaps = grammar_inst.flags.allow_gaps();
                let (_start_bracket_idx, end_bracket_idx) = ctx.bracketed_config(*grammar_id);
                let close_bracket_id = all_children[end_bracket_idx];

                // Replace deep-clone traversal with a reference-based flattening.
                // Only clone the nodes that actually get pushed into `frame.accumulated`.
                if !child_node.is_empty() {
                    let mut to_process: Vec<&Node> = vec![child_node];
                    while let Some(node) = to_process.pop() {
                        match node {
                            Node::Sequence { children } | Node::DelimitedList { children } => {
                                // push children as references (reverse order to preserve original order)
                                for child in children.iter().rev() {
                                    to_process.push(child);
                                }
                            }
                            _ => {
                                // clone only the leaf node we actually keep
                                frame.accumulated.push(node.clone());
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

                if allow_gaps {
                    let code_idx =
                        self.skip_start_index_forward_to_code(gap_start, self.tokens.len());
                    log::debug!(
                        "[BRACKET-DEBUG] After content, gap_start={}, code_idx={}, token at gap_start={:?}, token at code_idx={:?}",
                        gap_start, code_idx,
                        self.tokens.get(gap_start).map(|t| t.raw()),
                        self.tokens.get(code_idx).map(|t| t.raw()),
                    );
                    for pos in self.pos..code_idx {
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
                    log::debug!(
                        "Bracketed[table]: Parsed content element {}/{} (empty={}), pushing next element grammar_id={}",
                        *content_idx,
                        content_ids.len(),
                        child_node.is_empty(),
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
                    };
                    let mut child_frame = create_table_driven_child_frame(
                        stack.frame_id_counter,
                        next_content_id,
                        self.pos,
                        &[], // Don't pass close bracket as terminator - use bracket_max_idx instead
                        context,
                        *bracket_max_idx,
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
                    log::debug!("DEBUG: No closing bracket found!");
                    if parse_mode == ParseMode::Strict {
                        self.pos = frame.pos;
                        // Transition to Combining to finalize Empty result
                        frame.end_pos = Some(frame.pos);
                        frame.state = FrameState::Combining;
                        stack.push(&mut frame);
                        Ok(TableFrameResult::Done)
                    } else {
                        panic!("Couldn't find closing bracket for opening bracket");
                    }
                } else {
                    // STRICT mode check: All content elements must end at the closing bracket position
                    // This check should only happen AFTER all content elements have been processed.
                    let check_pos =
                        self.skip_start_index_forward_to_code(self.pos, self.tokens.len());
                    if let Some(expected_close_pos) = *bracket_max_idx {
                        if check_pos != expected_close_pos {
                            if parse_mode == ParseMode::Strict {
                                log::debug!("Bracketed[table] STRICT mode: content did not end at closing bracket (check_pos={}, expected={}), returning Empty for retry. frame_id={}, frame.pos={}", check_pos, expected_close_pos, frame.frame_id, frame.pos);
                                self.pos = frame.pos;
                                // Transition to Combining to finalize Empty result
                                frame.end_pos = Some(frame.pos);
                                frame.state = FrameState::Combining;
                                stack.push(&mut frame);
                                return Ok(TableFrameResult::Done);
                            } else {
                                log::debug!("Bracketed[table] GREEDY mode: content did not end at closing bracket, but continuing (may contain unparsable). check_pos={}, expected_close_pos={}", check_pos, expected_close_pos);
                            }
                        } else {
                            log::debug!("[BRACKET-DEBUG] Bracketed content ends at expected closing bracket (check_pos == expected_close_pos)");
                        }
                    }

                    log::debug!(
                        "DEBUG: All content elements parsed, transitioning to MatchingClose!"
                    );
                    *bracket_state = BracketedState::MatchingClose;
                    let parent_limit = frame.parent_max_idx;
                    log::debug!(
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
                    );
                    *last_child_frame_id = Some(stack.frame_id_counter);
                    stack.increment_frame_id_counter();
                    stack.push(&mut frame);
                    stack.push(&mut child_frame);
                    Ok(TableFrameResult::Done)
                }
            }
            BracketedState::MatchingClose => {
                log::debug!(
                    "DEBUG: Bracketed[table] MatchingClose - child_node.is_empty={}, child_end_pos={}",
                    child_node.is_empty(),
                    child_end_pos
                );
                let ctx = self.grammar_ctx.expect("GrammarContext required");
                let grammar_inst = ctx.inst(frame.grammar_id);
                let parse_mode = grammar_inst.parse_mode;

                if child_node.is_empty() {
                    if parse_mode == ParseMode::Strict {
                        self.pos = frame.pos;
                        frame.end_pos = Some(frame.pos);
                    } else {
                        // In GREEDY mode, not finding a closing bracket is an error
                        // But we still need to store SOME result so the parent doesn't wait forever
                        log::debug!(
                            "Bracketed[table] GREEDY mode: Couldn't find closing bracket for opening bracket at pos {}, frame_id={}",
                            frame.pos,
                            frame.frame_id
                        );
                        self.pos = frame.pos;
                        frame.end_pos = Some(frame.pos);
                    }
                } else {
                    frame.accumulated.push(child_node.clone());
                    self.pos = *child_end_pos;
                    log::debug!(
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
        let combine_end = frame.end_pos.unwrap_or(self.pos);
        log::debug!(
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
                let ctx = self.grammar_ctx.expect("GrammarContext required");
                let persists = ctx.bracketed_persists(*grammar_id);

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
            // Log the actual state for debugging
            let state_str = if let FrameContext::Bracketed { state, .. } = &frame.context {
                format!("{:?}", state)
            } else {
                "Unknown".to_string()
            };
            log::debug!(
                "Bracketed combining with INCOMPLETE state ({}) → returning Node::Empty, frame_id={}, accumulated={}",
                state_str,
                frame.frame_id,
                frame.accumulated.len()
            );
            Node::Empty
        };

        // Transition to Complete state with the final result
        let end_pos = frame.end_pos.unwrap_or(frame.pos);
        frame.state = FrameState::Complete(result_node);
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
    };
    frame.table_terminators = all_terminators.to_vec();
    stack.push(&mut frame);
}

fn create_table_driven_child_frame(
    frame_id: usize,
    grammar_id: GrammarId,
    start_idx: usize,
    terminators: &[GrammarId],
    context: FrameContext,
    parent_max_idx: Option<usize>,
) -> TableParseFrame {
    TableParseFrame {
        frame_id,
        grammar_id,
        pos: start_idx,
        table_terminators: terminators.to_vec(),
        state: FrameState::Initial,
        accumulated: vec![],
        context,
        parent_max_idx, // Propagate parent's limit!
        end_pos: None,
        transparent_positions: None,
        element_key: None,
    }
}
