use sqlfluffrs_types::{GrammarId, GrammarVariant};

use crate::parser::{
    cache::TableCacheKey,
    table_driven::frame::{TableFrameResult, TableParseFrame, TableParseFrameStack},
    FrameContext, FrameState, Node, ParseError, Parser,
};

impl Parser<'_> {
    // ========================================================================
    // Main Iterative Parser
    // ========================================================================

    /// Fully iterative parser using explicit stack
    ///
    /// This replaces recursive `parse_with_grammar` calls with an explicit
    /// stack-based state machine to avoid stack overflow on deeply nested grammars.
    pub fn parse_table_iterative(
        &mut self,
        grammar: GrammarId,
        parent_terminators: &[GrammarId],
    ) -> Result<Node, ParseError> {
        log::debug!(
            "Starting iterative parse for grammar: {} at pos {}",
            grammar,
            self.pos
        );

        // Check table cache first, unless disabled
        let start_pos = self.pos;
        let max_idx = self.tokens.len();

        if self.cache_enabled {
            let cache_key = TableCacheKey::new(start_pos, grammar, max_idx, parent_terminators);
            if let Some((node, end_pos, transparent_positions)) = self.table_cache.get(&cache_key) {
                log::debug!(
                    "TableCache HIT for grammar {} at pos {} -> end_pos {}",
                    grammar,
                    start_pos,
                    end_pos
                );

                // Restore parser position and transparent positions
                self.pos = *end_pos;
                if let Some(positions) = transparent_positions {
                    for &pos in positions {
                        self.collected_transparent_positions.insert(pos);
                    }
                }

                return Ok(node.clone());
            }
        }

        // Stack of parse frames and state
        let mut stack = TableParseFrameStack::new();
        let initial_frame_id = stack.frame_id_counter;
        stack.frame_id_counter += 1;
        stack.push(&mut TableParseFrame {
            frame_id: initial_frame_id,
            grammar_id: grammar,
            pos: self.pos,
            table_terminators: parent_terminators.to_vec(),
            state: FrameState::Initial,
            accumulated: vec![],
            context: FrameContext::None,
            parent_max_idx: None, // Top-level frame has no parent limit
            end_pos: None,
            transparent_positions: None,
            element_key: None,
        });

        let mut iteration_count = 0_usize;
        let max_iterations = 1_750_000_usize; // Higher limit for complex grammars

        while let Some(frame_from_stack) = stack.pop() {
            iteration_count += 1;

            // Re-check the cache ONLY for Initial frames
            // WaitingForChild frames have already started processing and have a child computing the result
            let mut frame = if matches!(frame_from_stack.state, FrameState::Initial) {
                match self.check_and_handle_table_frame_cache(frame_from_stack, &mut stack)? {
                    TableFrameResult::Done => continue,
                    TableFrameResult::Push(frame) => frame, // Cache miss - process this frame
                }
            } else {
                frame_from_stack
            };

            if iteration_count > max_iterations {
                self.handle_table_max_iterations_exceeded(&mut stack, max_iterations, &mut frame);
            }

            // Debug: Show what frame we're processing periodically
            // if iteration_count.is_multiple_of(5000) {
            //     Self::log_frame_debug_info(&frame, &stack, iteration_count);
            // }

            log::debug!(
                "Processing frame {}: grammar={}, pos={}, state={:?}, stack_size={} (BEFORE pop: {})",
                frame.frame_id,
                frame.grammar_id,
                frame.pos,
                frame.state,
                stack.len(),
                stack.len() + 1  // Add 1 because we just popped
            );

            match frame.state {
                FrameState::Initial => {
                    // Log grammar path when trying a match
                    log::debug!(
                        "🔍 Trying match at pos {}: {}",
                        frame.pos,
                        self.build_table_grammar_path(&frame, &stack)
                    );

                    match self.handle_table_driven_initial(frame, &mut stack, iteration_count)? {
                        TableFrameResult::Done => continue,
                        TableFrameResult::Push(mut updated_frame) => {
                            stack.push(&mut updated_frame);
                        }
                    }
                }
                FrameState::WaitingForChild {
                    child_index,
                    total_children,
                } => {
                    match self.handle_table_driven_waiting_for_child(
                        frame,
                        &mut stack,
                        iteration_count,
                        child_index,
                        total_children,
                    )? {
                        TableFrameResult::Done => continue,
                        TableFrameResult::Push(mut updated_frame) => {
                            stack.push(&mut updated_frame);
                        }
                    }
                }

                FrameState::Combining => {
                    // Log that we're combining child results, include range
                    let combine_end = frame.end_pos.unwrap_or(self.pos);
                    log::debug!(
                        "🔨 Combining at pos {}-{}: {}",
                        frame.pos,
                        combine_end.saturating_sub(1),
                        self.build_table_grammar_path(&frame, &stack)
                    );

                    // Delegate to specific handler based on grammar type
                    match self.handle_table_driven_combining(frame, &mut stack)? {
                        TableFrameResult::Done => {}
                        TableFrameResult::Push(mut updated_frame) => {
                            stack.push(&mut updated_frame);
                        }
                    }
                }

                FrameState::Complete(ref node) => {
                    // This state is reached when a handler has finished producing a result.
                    // The handler transitions the frame to Complete(node) and returns Push(frame).
                    // The main loop then stores the result in stack.results for parent frames to access.
                    // This separation keeps handlers focused on producing results, while the main
                    // loop coordinates result storage.
                    self.commit_table_frame_result(&mut stack, &frame, node);
                }
            }
        }

        // Return the result from the initial frame
        log::debug!("DEBUG: Main loop ended. Stack has {} frames left. Results has {} entries. Looking for frame_id={}",
            stack.len(),
            stack.results.len(),
            initial_frame_id
        );

        let ctx = self.grammar_ctx.ok_or_else(|| {
            ParseError::new("Table-driven parsing requires GrammarContext".to_string())
        })?;

        // Debug: Show what frames are left on the stack
        for (i, frame) in stack.iter().enumerate() {
            let grammar_desc = match ctx.variant(frame.grammar_id) {
                GrammarVariant::Ref => format!("Ref({})", ctx.ref_name(frame.grammar_id)),
                GrammarVariant::Bracketed => "Bracketed".to_string(),
                GrammarVariant::Delimited => "Delimited".to_string(),
                GrammarVariant::OneOf => {
                    format!("OneOf({} elements)", ctx.children_count(frame.grammar_id))
                }
                GrammarVariant::Sequence => {
                    format!(
                        "Sequence({} elements)",
                        ctx.children_count(frame.grammar_id)
                    )
                }
                GrammarVariant::AnyNumberOf => "AnyNumberOf".to_string(),
                GrammarVariant::AnySetOf => "AnySetOf".to_string(),
                GrammarVariant::StringParser => {
                    format!("StringParser('{}')", ctx.template(frame.grammar_id))
                }
                GrammarVariant::Token => format!("Token({})", ctx.template(frame.grammar_id)),
                _ => "Other".to_string(),
            };

            // Also show which child frame ID we're waiting for
            let waiting_for = get_waiting_for_frame_id(frame);

            log::debug!(
                "  Stack[{}]: frame_id={}, state={:?}, pos={}, grammar={}, waiting_for={}",
                i,
                frame.frame_id,
                frame.state,
                frame.pos,
                grammar_desc,
                waiting_for
            );
        }

        log::debug!(
            "Main loop ended. Stack empty. Results has {} entries. Looking for frame_id={}",
            stack.results.len(),
            initial_frame_id
        );
        if let Some((node, end_pos, _element_key)) = stack.results.get(&initial_frame_id) {
            log::debug!(
                "DEBUG: Found result for frame_id={}, end_pos={}",
                initial_frame_id,
                end_pos
            );
            self.pos = *end_pos;

            // Mark transparent tokens as globally collected now that we're using this result
            if let Some(transparent_positions) = stack.transparent_positions.get(&initial_frame_id)
            {
                for &pos in transparent_positions {
                    if !self.collected_transparent_positions.insert(pos) {
                        log::warn!("WARNING (initial): Position {} was already collected! Duplicate marking.", pos);
                    }
                }
            }

            // If the parse failed (returned Empty), provide diagnostic information
            if node.is_empty() {
                log::debug!("\n=== PARSE FAILED ===");
                log::debug!("Parser stopped at position: {}", end_pos);
                log::debug!("Total tokens: {}", self.tokens.len());

                if *end_pos < self.tokens.len() {
                    log::debug!("\nTokens around failure point:");
                    let start = end_pos.saturating_sub(3);
                    let end = (*end_pos + 4).min(self.tokens.len());
                    for i in start..end {
                        let marker = if i == *end_pos { " <<< HERE" } else { "" };
                        if let Some(tok) = self.tokens.get(i) {
                            log::debug!(
                                "  [{}]: '{}' (type: {}){}",
                                i,
                                tok.raw(),
                                tok.get_type(),
                                marker
                            );
                        }
                    }
                }

                log::debug!("\nGrammar that failed to match:");
                log::debug!("  {}", grammar);
                log::debug!("===================\n");
            }

            // Collect transparent positions that were touched during this parse
            let transparent_positions: Vec<usize> = self
                .collected_transparent_positions
                .iter()
                .filter(|&&pos| pos >= start_pos && pos < *end_pos)
                .copied()
                .collect();

            // Store successful parse in table cache
            if self.cache_enabled {
                let cache_key = TableCacheKey::new(start_pos, grammar, max_idx, parent_terminators);
                let transparent_opt = if transparent_positions.is_empty() {
                    None
                } else {
                    Some(transparent_positions)
                };
                self.table_cache
                    .put(cache_key, (node.clone(), *end_pos, transparent_opt));
            }

            Ok(node.clone())
        } else {
            // Parse error - don't cache errors for now (to keep it simple)
            let error = ParseError::new(format!(
                "Iterative parse produced no result (initial_frame_id={}, stack.results has {} entries)",
                initial_frame_id,
                stack.results.len()
            ));
            Err(error)
        }
    }

    /// Dispatch handler for table-driven Initial state.
    pub fn handle_table_driven_initial(
        &mut self,
        frame: TableParseFrame,
        stack: &mut TableParseFrameStack,
        _iteration_count: usize,
    ) -> Result<TableFrameResult, ParseError> {
        use sqlfluffrs_types::GrammarVariant;

        let ctx = self.grammar_ctx.ok_or_else(|| {
            ParseError::new("Table-driven parsing requires GrammarContext".to_string())
        })?;

        let grammar_id = frame.grammar_id;
        let inst = ctx.inst(grammar_id);
        let variant = inst.variant;
        let table_terminators = frame.table_terminators.clone();

        log::debug!(
            "Table-driven Initial: frame_id={}, grammar_id={}, variant={:?}",
            frame.frame_id,
            grammar_id.0,
            variant
        );

        // Ensure parser's current position reflects the frame's start position
        // so all table-driven handlers that use `self.pos` operate on the
        // intended token index. This keeps behavior consistent with
        // non-table-driven handlers which set `self.pos = frame.pos`.
        self.pos = frame.pos;

        match variant {
            GrammarVariant::OneOf => {
                self.handle_oneof_table_driven_initial(frame, &table_terminators, stack)
            }
            GrammarVariant::Sequence => {
                self.handle_sequence_table_driven_initial(frame, &table_terminators, stack)
            }
            GrammarVariant::Delimited => {
                self.handle_delimited_table_driven_initial(frame, &table_terminators, stack)
            }
            GrammarVariant::Bracketed => self.handle_bracketed_table_driven_initial(
                grammar_id,
                frame,
                &table_terminators,
                stack,
            ),
            GrammarVariant::AnyNumberOf | GrammarVariant::AnySetOf => {
                // AnySetOf currently delegates to AnyNumberOf semantics in table-driven handlers
                self.handle_anynumberof_table_driven_initial(frame, &table_terminators, stack)
            }
            GrammarVariant::Ref => {
                self.handle_ref_table_driven_initial(grammar_id, frame, &table_terminators, stack)
            }
            // Terminal/simple variants should be handled synchronously here
            GrammarVariant::StringParser => {
                // Synchronous match: call the table-driven string parser and store result for parent
                let res = self.handle_string_parser_table_driven(grammar_id, ctx);
                match res {
                    Ok(node) => {
                        // Insert result directly so parent frames can pick it up
                        log::debug!(
                            "[SYNC INSERT] frame_id={} StringParser result at pos {} -> node={:?}",
                            frame.frame_id,
                            self.pos,
                            node
                        );
                        stack.results.insert(frame.frame_id, (node, self.pos, None));
                        Ok(TableFrameResult::Done)
                    }
                    Err(e) => Err(e),
                }
            }
            GrammarVariant::TypedParser => self.handle_typed_parser_table_driven(frame),
            GrammarVariant::MultiStringParser => {
                let res = self.handle_multi_string_parser_table_driven(grammar_id, ctx);
                match res {
                    Ok(node) => {
                        log::debug!(
                            "[SYNC INSERT] frame_id={} MultiStringParser result at pos {} -> node={:?}",
                            frame.frame_id,
                            self.pos,
                            node
                        );
                        stack.results.insert(frame.frame_id, (node, self.pos, None));
                        Ok(TableFrameResult::Done)
                    }
                    Err(e) => Err(e),
                }
            }
            GrammarVariant::RegexParser => {
                let res = self.handle_regex_parser_table_driven(grammar_id);
                match res {
                    Ok(node) => {
                        log::debug!(
                            "[SYNC INSERT] frame_id={} RegexParser result at pos {} -> node={:?}",
                            frame.frame_id,
                            self.pos,
                            node
                        );
                        stack.results.insert(frame.frame_id, (node, self.pos, None));
                        Ok(TableFrameResult::Done)
                    }
                    Err(e) => Err(e),
                }
            }
            GrammarVariant::Nothing => {
                let res = self.handle_nothing_table_driven();
                match res {
                    Ok(node) => {
                        log::debug!(
                            "[SYNC INSERT] frame_id={} Nothing result at pos {} -> node={:?}",
                            frame.frame_id,
                            self.pos,
                            node
                        );
                        stack.results.insert(frame.frame_id, (node, self.pos, None));
                        Ok(TableFrameResult::Done)
                    }
                    Err(e) => Err(e),
                }
            }
            GrammarVariant::Empty => {
                let res = self.handle_empty_table_driven();
                match res {
                    Ok(node) => {
                        log::debug!(
                            "[SYNC INSERT] frame_id={} Empty result at pos {} -> node={:?}",
                            frame.frame_id,
                            self.pos,
                            node
                        );
                        stack.results.insert(frame.frame_id, (node, self.pos, None));
                        Ok(TableFrameResult::Done)
                    }
                    Err(e) => Err(e),
                }
            }
            GrammarVariant::Missing => {
                let res = self.handle_missing_table_driven();
                match res {
                    Ok(node) => {
                        log::debug!(
                            "[SYNC INSERT] frame_id={} Missing result at pos {} -> node={:?}",
                            frame.frame_id,
                            self.pos,
                            node
                        );
                        stack.results.insert(frame.frame_id, (node, self.pos, None));
                        Ok(TableFrameResult::Done)
                    }
                    Err(e) => Err(e),
                }
            }
            GrammarVariant::Token => {
                let res = self.handle_token_table_driven(grammar_id, ctx);
                match res {
                    Ok(node) => {
                        log::debug!(
                            "[SYNC INSERT] frame_id={} Token result at pos {} -> node={:?}",
                            frame.frame_id,
                            self.pos,
                            node
                        );
                        stack.results.insert(frame.frame_id, (node, self.pos, None));
                        Ok(TableFrameResult::Done)
                    }
                    Err(e) => Err(e),
                }
            }
            GrammarVariant::Meta => {
                let res = self.handle_meta_table_driven(grammar_id, ctx);
                match res {
                    Ok(node) => {
                        log::debug!(
                            "[SYNC INSERT] frame_id={} Meta result at pos {} -> node={:?}",
                            frame.frame_id,
                            self.pos,
                            node
                        );
                        stack.results.insert(frame.frame_id, (node, self.pos, None));
                        Ok(TableFrameResult::Done)
                    }
                    Err(e) => Err(e),
                }
            }
            GrammarVariant::NonCodeMatcher => {
                let res = self.handle_noncode_matcher_table_driven();
                match res {
                    Ok(node) => {
                        log::debug!(
                            "[SYNC INSERT] frame_id={} NonCodeMatcher result at pos {} -> node={:?}",
                            frame.frame_id,
                            self.pos,
                            node
                        );
                        stack.results.insert(frame.frame_id, (node, self.pos, None));
                        Ok(TableFrameResult::Done)
                    }
                    Err(e) => Err(e),
                }
            }
            GrammarVariant::Anything => {
                let res = self.handle_anything_table_driven(
                    grammar_id,
                    ctx,
                    &table_terminators,
                    frame.parent_max_idx,
                );
                match res {
                    Ok(node) => {
                        log::debug!(
                            "[SYNC INSERT] frame_id={} Anything result at pos {} -> node={:?}",
                            frame.frame_id,
                            self.pos,
                            node
                        );
                        stack.results.insert(frame.frame_id, (node, self.pos, None));
                        Ok(TableFrameResult::Done)
                    }
                    Err(e) => Err(e),
                }
            }
        }
    }

    /// Dispatch handler for WaitingForChild state.
    fn handle_table_driven_waiting_for_child(
        &mut self,
        mut frame: TableParseFrame,
        stack: &mut TableParseFrameStack,
        iteration_count: usize,
        child_index: usize,
        total_children: usize,
    ) -> Result<TableFrameResult, ParseError> {
        // A child parse just completed - get its result
        let child_frame_id = match &frame.context {
            FrameContext::OneOfTableDriven {
                last_child_frame_id,
                ..
            }
            | FrameContext::SequenceTableDriven {
                last_child_frame_id,
                ..
            }
            | FrameContext::RefTableDriven {
                last_child_frame_id,
                ..
            }
            | FrameContext::BracketedTableDriven {
                last_child_frame_id,
                ..
            }
            | FrameContext::DelimitedTableDriven {
                last_child_frame_id,
                ..
            }
            | FrameContext::AnyNumberOfTableDriven {
                last_child_frame_id,
                ..
            } => last_child_frame_id.expect("WaitingForChild should have last_child_frame_id set"),
            _ => {
                log::error!("WaitingForChild state without child frame ID tracking");
                return Ok(TableFrameResult::Done);
            }
        };

        let child = stack.results.get(&child_frame_id).cloned();
        log::debug!(
            "[RESULT GET] parent_frame_id={}, child_frame_id={}, child_found={}",
            frame.frame_id,
            child_frame_id,
            child.is_some()
        );

        if let Some((child_node, child_end_pos, _child_element_key)) = &child {
            log::debug!(
                "[RESULT FOUND] parent_frame_id={}, child_frame_id={}, child_end_pos={}",
                frame.frame_id,
                child_frame_id,
                child_end_pos
            );
            log::debug!(
                "Child {} of {} completed (frame_id={}): pos {} -> {}",
                child_index,
                total_children,
                child_frame_id,
                frame.pos,
                child_end_pos
            );

            // Note: We intentionally do NOT mark transparent positions globally here.
            // Marking happens only when frames commit their results, not when results are retrieved.
            // This prevents interference between speculative parses while still preventing duplicates
            // in the final committed AST.

            match &mut frame.context {
                FrameContext::OneOfTableDriven { .. } => {
                    match self.handle_oneof_table_driven_waiting_for_child(
                        frame,
                        child_node,
                        child_end_pos,
                        stack,
                    )? {
                        TableFrameResult::Done => {}
                        TableFrameResult::Push(mut updated_frame) => {
                            stack.push(&mut updated_frame);
                        }
                    }
                    Ok(TableFrameResult::Done)
                }
                FrameContext::SequenceTableDriven { .. } => {
                    match self.handle_sequence_table_driven_waiting_for_child(
                        frame,
                        child_node,
                        child_end_pos,
                        stack,
                    )? {
                        TableFrameResult::Done => {}
                        TableFrameResult::Push(mut updated_frame) => {
                            stack.push(&mut updated_frame);
                        }
                    }
                    Ok(TableFrameResult::Done)
                }
                FrameContext::RefTableDriven { .. } => {
                    match self.handle_ref_table_driven_waiting_for_child(
                        frame,
                        child_node,
                        child_end_pos,
                    )? {
                        TableFrameResult::Done => {}
                        TableFrameResult::Push(mut updated_frame) => {
                            stack.push(&mut updated_frame);
                        }
                    }
                    Ok(TableFrameResult::Done)
                }
                FrameContext::DelimitedTableDriven { .. } => {
                    match self.handle_delimited_table_driven_waiting_for_child(
                        frame,
                        child_node,
                        child_end_pos,
                        stack,
                    )? {
                        TableFrameResult::Done => {}
                        TableFrameResult::Push(mut updated_frame) => {
                            stack.push(&mut updated_frame);
                        }
                    }
                    Ok(TableFrameResult::Done)
                }
                FrameContext::BracketedTableDriven { .. } => {
                    match self.handle_bracketed_table_driven_waiting_for_child(
                        frame,
                        child_node,
                        child_end_pos,
                        stack,
                    )? {
                        TableFrameResult::Done => {}
                        TableFrameResult::Push(mut updated_frame) => {
                            stack.push(&mut updated_frame);
                        }
                    }
                    Ok(TableFrameResult::Done)
                }
                FrameContext::AnyNumberOfTableDriven { .. } => {
                    match self.handle_anynumberof_table_driven_waiting_for_child(
                        frame,
                        child_node,
                        child_end_pos,
                        stack,
                    )? {
                        TableFrameResult::Done => {}
                        TableFrameResult::Push(mut updated_frame) => {
                            stack.push(&mut updated_frame);
                        }
                    }
                    Ok(TableFrameResult::Done)
                }
                _ => {
                    // TODO: Handle other grammar types
                    unimplemented!("WaitingForChild for grammar type: {:?}", frame.grammar_id);
                }
            }
        } else {
            // Child result not found yet - push frame back onto stack and continue
            let last_child_frame_id = match &frame.context {
                FrameContext::OneOfTableDriven {
                    last_child_frame_id,
                    ..
                }
                | FrameContext::SequenceTableDriven {
                    last_child_frame_id,
                    ..
                }
                | FrameContext::RefTableDriven {
                    last_child_frame_id,
                    ..
                }
                | FrameContext::DelimitedTableDriven {
                    last_child_frame_id,
                    ..
                }
                | FrameContext::BracketedTableDriven {
                    last_child_frame_id,
                    ..
                }
                | FrameContext::AnyNumberOfTableDriven {
                    last_child_frame_id,
                    ..
                } => *last_child_frame_id,
                _ => None,
            };
            log::debug!(
                "Child result not found for frame_id={}, last_child_frame_id={:?}, pushing frame back onto stack",
                frame.frame_id,
                last_child_frame_id
            );

            // Check if we're in an infinite loop - frame waiting for child that doesn't exist
            if iteration_count > 100 && iteration_count.is_multiple_of(100) {
                log::debug!(
                    "WARNING: Frame {} waiting for child {:?} but result not found (iteration {})",
                    frame.frame_id,
                    last_child_frame_id,
                    iteration_count
                );

                // Check if child is on stack
                if let Some(child_id) = last_child_frame_id {
                    let child_on_stack = stack.iter().any(|f| f.frame_id == child_id);
                    if child_on_stack {
                        log::debug!(
                            "  -> Child frame {} IS on stack (still being processed)",
                            child_id
                        );
                    } else {
                        panic!("  -> Child frame {} NOT on stack (may have been lost or never created)", child_id);
                    }
                }
            }

            // Push frame back onto stack so it can be re-checked after child completes
            Ok(TableFrameResult::Push(frame))
        }
    }

    fn handle_table_driven_combining(
        &mut self,
        frame: TableParseFrame,
        stack: &mut TableParseFrameStack,
    ) -> Result<TableFrameResult, ParseError> {
        use sqlfluffrs_types::GrammarVariant;

        let ctx = self.grammar_ctx.ok_or_else(|| {
            ParseError::new("Table-driven parsing requires GrammarContext".to_string())
        })?;

        let grammar_id = frame.grammar_id;
        let inst = ctx.inst(grammar_id);
        let variant = inst.variant;

        log::debug!(
            "Table-driven Combining: frame_id={}, grammar_id={}, variant={:?}",
            frame.frame_id,
            grammar_id.0,
            variant
        );

        match variant {
            GrammarVariant::OneOf => self.handle_oneof_table_driven_combining(frame, stack),
            GrammarVariant::Sequence => self.handle_sequence_table_driven_combining(frame, stack),
            GrammarVariant::Delimited => self.handle_delimited_table_driven_combining(frame),
            GrammarVariant::Bracketed => self.handle_bracketed_table_driven_combining(frame),
            GrammarVariant::AnyNumberOf => self.handle_anynumberof_table_driven_combining(frame),
            GrammarVariant::AnySetOf => self.handle_anynumberof_table_driven_combining(frame),
            GrammarVariant::Ref => self.handle_ref_table_driven_combining(frame),
            _ => {
                // Combining should not be reached for terminal/simple variants
                unimplemented!(
                    "Combining not implemented for grammar variant: {:?}",
                    variant
                );
            }
        }
    }

    fn commit_table_frame_result(
        &mut self,
        stack: &mut TableParseFrameStack,
        frame: &TableParseFrame,
        node: &Node,
    ) {
        // Log grammar path - different indicator for Empty vs matched nodes
        let end_pos = frame.end_pos.unwrap_or(self.pos);
        match node {
            Node::Empty => {
                log::debug!(
                    "❌ No match at pos {}: {}",
                    frame.pos,
                    self.build_table_grammar_path(frame, stack)
                );
            }
            _ => {
                log::debug!(
                    "✅ Match at pos {}-{}: {}",
                    frame.pos,
                    end_pos.saturating_sub(1),
                    self.build_table_grammar_path(frame, stack)
                );
            }
        }

        // Use the end_pos stored in the frame (or fall back to self.pos)
        let end_pos = frame.end_pos.unwrap_or(self.pos);

        // Get element_key if any (set by OneOf for AnyNumberOf tracking)
        let element_key = frame.element_key;

        // This frame is done - insert result
        stack
            .results
            .insert(frame.frame_id, (node.clone(), end_pos, element_key));

        // Cache the result for future reuse
        // Cache non-empty results always, but only cache Empty results when
        // terminators are empty (otherwise the Empty might become non-Empty
        // with different terminator context)
        if self.cache_enabled {
            let should_cache_empty = node.is_empty() && frame.table_terminators.is_empty();
            let should_cache_success = !node.is_empty();

            if should_cache_empty || should_cache_success {
                let ctx = self
                    .grammar_ctx
                    .expect("GrammarContext required for caching");
                let variant = ctx.variant(frame.grammar_id);

                // Only cache compound grammars that are expensive to re-parse
                // Skip simple terminals (StringParser, TypedParser, etc.) - they're fast
                let should_cache = matches!(
                    variant,
                    GrammarVariant::Ref
                        | GrammarVariant::Sequence
                        | GrammarVariant::OneOf
                        | GrammarVariant::AnyNumberOf
                        | GrammarVariant::AnySetOf
                        | GrammarVariant::Delimited
                        | GrammarVariant::Bracketed
                );

                if should_cache {
                    let max_idx = frame.parent_max_idx.unwrap_or(self.tokens.len());
                    let cache_key = TableCacheKey::new(
                        frame.pos,
                        frame.grammar_id,
                        max_idx,
                        &frame.table_terminators,
                    );
                    // Get transparent positions for this frame
                    let transparent_opt = frame.transparent_positions.clone();
                    self.table_cache
                        .put(cache_key, (node.clone(), end_pos, transparent_opt));
                }
            }
        }
    }

    /// Checks the cache for a frame and handles cache hits. Returns FrameResult indicating what to do next.
    ///
    /// Cache hits are special: they bypass the normal state machine and insert results directly
    /// into stack.results. This is an optimization that avoids the overhead of pushing the frame
    /// back through the Complete state when we already have the result.
    ///
    /// - FrameResult::Done: Cache hit, result stored directly in stack.results, skip this frame
    /// - FrameResult::Push(frame): Cache miss, push frame back to process normally
    fn check_and_handle_table_frame_cache(
        &mut self,
        frame: TableParseFrame,
        stack: &mut TableParseFrameStack,
    ) -> Result<TableFrameResult, ParseError> {
        if self.cache_enabled {
            // Use frame's parent_max_idx if available, otherwise tokens.len()
            let max_idx = frame.parent_max_idx.unwrap_or(self.tokens.len());
            let cache_key = TableCacheKey::new(
                frame.pos,
                frame.grammar_id,
                max_idx,
                &frame.table_terminators,
            );
            if let Some((node, end_pos, transparent_positions)) = self.table_cache.get(&cache_key) {
                log::debug!(
                    "[LOOP] TableCache HIT for grammar {} at pos {} -> end_pos {} (frame_id={})",
                    frame.grammar_id,
                    frame.pos,
                    end_pos,
                    frame.frame_id
                );
                self.pos = *end_pos;
                if let Some(positions) = transparent_positions {
                    for &pos in positions {
                        self.collected_transparent_positions.insert(pos);
                    }
                }
                // Clone values before inserting (since we only have reference from cache)
                stack
                    .results
                    .insert(frame.frame_id, (node.clone(), *end_pos, None));
                return Ok(TableFrameResult::Done);
            }
        }
        // Cache miss or cache disabled - push frame back to process normally
        Ok(TableFrameResult::Push(frame))
    }

    fn handle_table_max_iterations_exceeded(
        &mut self,
        stack: &mut TableParseFrameStack,
        max_iterations: usize,
        frame: &mut TableParseFrame,
    ) {
        log::debug!("ERROR: Exceeded max iterations ({})", max_iterations);
        log::debug!("Last frame: {:?}", frame.grammar_id);
        log::debug!("Stack depth: {}", stack.len());
        log::debug!("Results count: {}", stack.results.len());

        // Print last 20 frames on stack for diagnosis
        log::debug!("\n=== Last 20 frames on stack ===");
        let ctx = self.grammar_ctx.unwrap();
        for (i, f) in stack.iter().rev().take(20).enumerate() {
            log::debug!(
                "  [{}] state={:?}, pos={}, grammar={}",
                i,
                f.state,
                f.pos,
                match ctx.variant(f.grammar_id) {
                    GrammarVariant::Ref => format!("Ref({})", ctx.ref_name(f.grammar_id)),
                    GrammarVariant::Bracketed => "Bracketed".to_string(),
                    GrammarVariant::Delimited => "Delimited".to_string(),
                    GrammarVariant::OneOf =>
                        format!("OneOf({} elements)", ctx.children_count(f.grammar_id)),
                    GrammarVariant::Sequence =>
                        format!("Sequence({} elements)", ctx.children_count(f.grammar_id)),
                    GrammarVariant::AnyNumberOf => "AnyNumberOf".to_string(),
                    GrammarVariant::AnySetOf => "AnySetOf".to_string(),
                    _ => "Other".to_string(),
                }
            );
        }

        self.print_cache_stats();

        println!("Parser at position: {}", self.pos);

        println!("\nTokens around failure point:");
        let start = self.pos.saturating_sub(3);
        let end = (self.pos + 4).min(self.tokens.len());
        for i in start..end {
            let marker = if i == self.pos { " <<< HERE" } else { "" };
            if let Some(tok) = self.tokens.get(i) {
                println!(
                    "  [{}]: '{}' (type: {}){}",
                    i,
                    tok.raw(),
                    tok.get_type(),
                    marker
                );
            }
        }

        panic!("Infinite loop detected in iterative parser");
    }

    /// Logs debug information about the current frame and stack.
    /// Build a grammar path string showing the hierarchy of grammars being parsed.
    /// Supports both Arc<Grammar> and table-driven (GrammarId) frames.
    /// Format: "file -> statement -> select_statement -> ..."
    fn build_table_grammar_path(
        &self,
        frame: &TableParseFrame,
        stack: &TableParseFrameStack,
    ) -> String {
        let mut path_parts = Vec::new();

        // Helper to get a name for either Grammar or GrammarId
        fn grammar_id_name(parser: &Parser, frame: &TableParseFrame) -> String {
            // Table-driven: show grammar_id and its name if available
            if let Some(ctx) = parser.grammar_ctx.as_ref() {
                let name = match ctx.variant(frame.grammar_id) {
                    sqlfluffrs_types::GrammarVariant::Ref => ctx.ref_name(frame.grammar_id),
                    sqlfluffrs_types::GrammarVariant::StringParser
                    | sqlfluffrs_types::GrammarVariant::TypedParser
                    | sqlfluffrs_types::GrammarVariant::MultiStringParser
                    | sqlfluffrs_types::GrammarVariant::RegexParser => {
                        ctx.template(frame.grammar_id)
                    }
                    _ => &format!("{:?}", ctx.variant(frame.grammar_id)),
                };
                format!("id[{}:{:?}]", frame.grammar_id.0, name)
            } else {
                format!("id[{}]", frame.grammar_id.0)
            }
        }

        // Add the current frame's grammar first (most specific)
        path_parts.push(grammar_id_name(self, frame));

        // Walk up the stack to build the full path, adding ancestors in order
        // Stack is in reverse order (top of stack is most recent), so we iterate in reverse
        for ancestor_frame in stack.iter().rev() {
            path_parts.push(grammar_id_name(self, ancestor_frame));
        }

        path_parts.join(" -> ")
    }
}

fn get_waiting_for_frame_id(frame: &TableParseFrame) -> String {
    let waiting_for = match &frame.context {
        FrameContext::OneOfTableDriven {
            last_child_frame_id,
            ..
        }
        | FrameContext::SequenceTableDriven {
            last_child_frame_id,
            ..
        }
        | FrameContext::RefTableDriven {
            last_child_frame_id,
            ..
        }
        | FrameContext::DelimitedTableDriven {
            last_child_frame_id,
            ..
        }
        | FrameContext::BracketedTableDriven {
            last_child_frame_id,
            ..
        }
        | FrameContext::AnyNumberOfTableDriven {
            last_child_frame_id,
            ..
        } => format!("{:?}", last_child_frame_id),
        _ => "None".to_string(),
    };
    waiting_for
}
