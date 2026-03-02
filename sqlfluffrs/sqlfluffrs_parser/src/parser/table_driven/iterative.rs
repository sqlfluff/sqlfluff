use crate::vdebug;
use sqlfluffrs_types::{GrammarId, GrammarVariant};
use std::sync::Arc;

use crate::parser::{
    cache::TableCacheKey,
    table_driven::frame::{TableFrameResult, TableParseFrame, TableParseFrameStack},
    FrameContext, FrameState, MatchResult, Node, ParseError, Parser,
};

impl Parser<'_> {
    // ========================================================================
    // Main Iterative Parser
    // ========================================================================

    /// Fully iterative parser using explicit stack - returns Node
    ///
    /// This is a convenience wrapper around `parse_table_iterative_match_result`
    /// that materializes the AST by calling `apply()` on the MatchResult.
    ///
    /// For Python interop where Python handles apply(), use
    /// `parse_table_iterative_match_result` directly.
    pub fn parse_table_iterative(
        &mut self,
        grammar: GrammarId,
        parent_terminators: &[GrammarId],
    ) -> Result<Node, ParseError> {
        vdebug!(
            "parse_table_iterative: delegating to match_result version for grammar {} at pos {}",
            grammar,
            self.pos
        );

        // Delegate to the MatchResult version
        let match_result = self.parse_table_iterative_match_result(grammar, parent_terminators)?;

        // Materialize the AST by calling apply() - now returns a single Node
        let node = match_result.apply(self.tokens);

        Ok(node)
    }

    /// Primary iterative parser - returns MatchResult for lazy AST construction
    ///
    /// This is the main entry point for table-driven parsing. It returns a
    /// MatchResult which describes what matched without materializing the full
    /// AST. This allows:
    ///
    /// 1. Python to call its own apply() method for Python-native segment construction
    /// 2. Rust to call apply() when a Node is needed
    /// 3. Efficient caching of parse results (MatchResult is lighter than Node)
    ///
    /// The MatchResult follows Python's match() semantics:
    /// - matched_slice: Range of token indices that matched
    /// - matched_class: The segment class to construct (Ref, Sequence, etc.)
    /// - child_matches: Nested MatchResults for compound grammars
    pub fn parse_table_iterative_match_result(
        &mut self,
        grammar: GrammarId,
        parent_terminators: &[GrammarId],
    ) -> Result<MatchResult, ParseError> {
        vdebug!(
            "Starting iterative parse (match_result mode) for grammar: {} at pos {}",
            grammar,
            self.pos
        );

        // Save and clear checkpoint stack state at the start of this parse session.
        // This is critical for proper whitespace collection when OneOf tries multiple children.
        let saved_checkpoint_stack = std::mem::take(&mut self.collection_stack);
        let saved_collected_count = self.collected_transparent_positions.len();

        // DON'T check cache here at the entry point!
        // Python's cache is checked INSIDE each grammar handler (via longest_match)
        // AFTER they've calculated their trimmed max_idx based on terminators.
        // We need to do the same - let the Initial state handler check cache
        // after calculating max_idx with terminators.
        //
        // The issue: Different grammars have different parse modes and terminators.
        // We can't calculate the "right" max_idx here without knowing which grammar
        // handler will run and what terminators it will use.

        // Stack of parse frames and state
        let mut stack = TableParseFrameStack::new();
        let initial_frame_id = stack.frame_id_counter;
        stack.frame_id_counter += 1;
        stack.push(&mut TableParseFrame {
            frame_id: initial_frame_id,
            grammar_id: grammar,
            pos: self.pos,
            table_terminators: smallvec::SmallVec::from_slice(parent_terminators),
            state: FrameState::Initial,
            accumulated: smallvec::SmallVec::new(),
            context: FrameContext::None,
            parent_max_idx: None, // No parent constraint at top level - let handler calculate
            calculated_max_idx: None, // Will be set by handler after calculation
            end_pos: None,
            transparent_positions: None,
            element_key: None,
            parse_mode_override: None, // No override for top-level frame
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

            vdebug!(
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
                    vdebug!(
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
                    #[cfg(feature = "verbose-debug")]
                    let combine_end = frame.end_pos.unwrap_or(self.pos);
                    vdebug!(
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

                FrameState::Complete(ref match_result) => {
                    // This state is reached when a handler has finished producing a result.
                    // The handler transitions the frame to Complete(match_result) and returns Push(frame).
                    // The main loop then stores the result in stack.results for parent frames to access.
                    // This separation keeps handlers focused on producing results, while the main
                    // loop coordinates result storage.
                    self.commit_table_frame_result(&mut stack, &frame, match_result);
                }
            }
        }

        // Return the result from the initial frame
        vdebug!("DEBUG: Main loop ended. Stack has {} frames left. Results has {} entries. Looking for frame_id={}",
            stack.len(),
            stack.results.len(),
            initial_frame_id
        );

        // Debug: Show what frames are left on the stack
        #[cfg(feature = "verbose-debug")]
        for (i, frame) in stack.iter().enumerate() {
            let grammar_desc = match self.grammar_ctx.variant(frame.grammar_id) {
                GrammarVariant::Ref => {
                    format!("Ref({})", self.grammar_ctx.ref_name(frame.grammar_id))
                }
                GrammarVariant::Bracketed => "Bracketed".to_string(),
                GrammarVariant::Delimited => "Delimited".to_string(),
                GrammarVariant::OneOf => {
                    format!(
                        "OneOf({} elements)",
                        self.grammar_ctx.children_count(frame.grammar_id)
                    )
                }
                GrammarVariant::Sequence => {
                    format!(
                        "Sequence({} elements)",
                        self.grammar_ctx.children_count(frame.grammar_id)
                    )
                }
                GrammarVariant::AnyNumberOf => "AnyNumberOf".to_string(),
                GrammarVariant::AnySetOf => "AnySetOf".to_string(),
                GrammarVariant::StringParser => {
                    format!(
                        "StringParser('{}')",
                        self.grammar_ctx.template(frame.grammar_id)
                    )
                }
                GrammarVariant::Token => {
                    format!("Token({})", self.grammar_ctx.template(frame.grammar_id))
                }
                _ => "Other".to_string(),
            };

            // Also show which child frame ID we're waiting for
            let waiting_for = get_waiting_for_frame_id(frame);

            vdebug!(
                "  Stack[{}]: frame_id={}, state={:?}, pos={}, grammar={}, waiting_for={}",
                i,
                frame.frame_id,
                frame.state,
                frame.pos,
                grammar_desc,
                waiting_for
            );
        }

        vdebug!(
            "Main loop ended. Stack empty. Results has {} entries. Looking for frame_id={}",
            stack.results.len(),
            initial_frame_id
        );
        if let Some((match_result, end_pos, _element_key)) = stack.results.get(&initial_frame_id) {
            vdebug!(
                "DEBUG: Found result for frame_id={}, end_pos={}",
                initial_frame_id,
                end_pos
            );
            self.pos = *end_pos;

            // If the parse failed (returned Empty), provide diagnostic information
            #[cfg(feature = "verbose-debug")]
            if match_result.is_empty() {
                vdebug!("\n=== PARSE FAILED ===");
                vdebug!("Parser stopped at position: {}", end_pos);
                vdebug!("Total tokens: {}", self.tokens.len());

                if *end_pos < self.tokens.len() {
                    vdebug!("\nTokens around failure point:");
                    let start = end_pos.saturating_sub(3);
                    let end = (*end_pos + 4).min(self.tokens.len());
                    for i in start..end {
                        let marker = if i == *end_pos { " <<< HERE" } else { "" };
                        if let Some(tok) = self.tokens.get(i) {
                            vdebug!(
                                "  [{}]: '{}' (type: {}){}",
                                i,
                                tok.raw(),
                                tok.get_type(),
                                marker
                            );
                        }
                    }
                }

                vdebug!("\nGrammar that failed to match:");
                vdebug!("  {}", grammar);
                vdebug!("===================\n");
            }

            // NOTE: We don't cache at this level anymore!
            // Python's cache happens inside longest_match() which is called AFTER
            // grammar handlers calculate their trimmed max_idx. Our equivalent is
            // commit_table_frame_result() which caches WITH the frame's calculated max_idx.

            // Restore checkpoint stack before returning
            self.collection_stack = saved_checkpoint_stack;

            // For Empty results (no match), restore collected_transparent_positions too.
            // Empty results didn't actually consume anything, so any whitespace they
            // "collected" while skipping should be available for other parsers.
            if match_result.is_empty() {
                vdebug!(
                    "parse_table_iterative_match_result: Restoring collected_transparent_positions for Empty result (grammar {})",
                    grammar.0
                );
                self.collected_transparent_positions
                    .truncate(saved_collected_count);
            }

            // Apply global deduplication to remove sibling duplicates
            Ok((**match_result).clone())
        } else {
            // Parse error - don't cache errors for now (to keep it simple)
            let error = ParseError::new(format!(
                "Iterative parse produced no result (initial_frame_id={}, stack.results has {} entries)",
                initial_frame_id,
                stack.results.len()
            ));
            // Restore checkpoint stack and collected positions before returning
            self.collection_stack = saved_checkpoint_stack;
            self.collected_transparent_positions
                .truncate(saved_collected_count);
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

        let grammar_id = frame.grammar_id;
        let inst = self.grammar_ctx.inst(grammar_id);
        let variant = inst.variant;
        let table_terminators = frame.table_terminators.clone();

        vdebug!(
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
                let res = self.handle_string_parser_table_driven(grammar_id);
                match res {
                    Ok(match_result) => {
                        // Insert result directly so parent frames can pick it up
                        vdebug!(
                            "[SYNC INSERT] frame_id={} StringParser result at pos {} -> match={:?}",
                            frame.frame_id,
                            self.pos,
                            match_result
                        );
                        stack.insert_result(frame.frame_id, match_result, self.pos);
                        Ok(TableFrameResult::Done)
                    }
                    Err(e) => Err(e),
                }
            }
            GrammarVariant::TypedParser => self.handle_typed_parser_table_driven(frame),
            GrammarVariant::MultiStringParser => {
                let res = self.handle_multi_string_parser_table_driven(grammar_id);
                match res {
                    Ok(match_result) => {
                        vdebug!(
                            "[SYNC INSERT] frame_id={} MultiStringParser result at pos {}",
                            frame.frame_id,
                            self.pos
                        );
                        stack.insert_result(frame.frame_id, match_result, self.pos);
                        Ok(TableFrameResult::Done)
                    }
                    Err(e) => Err(e),
                }
            }
            GrammarVariant::RegexParser => {
                let res = self.handle_regex_parser_table_driven(grammar_id);
                match res {
                    Ok(match_result) => {
                        vdebug!(
                            "[SYNC INSERT] frame_id={} RegexParser result at pos {} -> match={:?}",
                            frame.frame_id,
                            self.pos,
                            match_result
                        );
                        stack.insert_result(frame.frame_id, match_result, self.pos);
                        Ok(TableFrameResult::Done)
                    }
                    Err(e) => Err(e),
                }
            }
            GrammarVariant::Nothing => {
                let res = self.handle_nothing_table_driven();
                match res {
                    Ok(match_result) => {
                        vdebug!(
                            "[SYNC INSERT] frame_id={} Nothing result at pos {} -> MatchResult",
                            frame.frame_id,
                            self.pos
                        );
                        stack.insert_result(frame.frame_id, match_result, self.pos);
                        Ok(TableFrameResult::Done)
                    }
                    Err(e) => Err(e),
                }
            }
            GrammarVariant::Empty => {
                let res = self.handle_empty_table_driven();
                match res {
                    Ok(match_result) => {
                        vdebug!(
                            "[SYNC INSERT] frame_id={} Empty result at pos {} -> MatchResult",
                            frame.frame_id,
                            self.pos
                        );
                        stack.insert_result(frame.frame_id, match_result, self.pos);
                        Ok(TableFrameResult::Done)
                    }
                    Err(e) => Err(e),
                }
            }
            GrammarVariant::Missing => {
                let res = self.handle_missing_table_driven();
                match res {
                    Ok(match_result) => {
                        vdebug!(
                            "[SYNC INSERT] frame_id={} Missing result at pos {} -> MatchResult",
                            frame.frame_id,
                            self.pos
                        );
                        stack.insert_result(frame.frame_id, match_result, self.pos);
                        Ok(TableFrameResult::Done)
                    }
                    Err(e) => Err(e),
                }
            }
            GrammarVariant::Token => {
                let res = self.handle_token_table_driven(grammar_id);
                match res {
                    Ok(match_result) => {
                        vdebug!(
                            "[SYNC INSERT] frame_id={} Token result at pos {} -> MatchResult",
                            frame.frame_id,
                            self.pos
                        );
                        stack.insert_result(frame.frame_id, match_result, self.pos);
                        Ok(TableFrameResult::Done)
                    }
                    Err(e) => Err(e),
                }
            }
            GrammarVariant::PrecededBy => {
                let res = self.handle_preceded_by_table_driven(grammar_id);
                match res {
                    Ok(match_result) => {
                        vdebug!(
                            "[SYNC INSERT] frame_id={} PrecededBy result at pos {} -> MatchResult",
                            frame.frame_id,
                            self.pos
                        );
                        stack.insert_result(frame.frame_id, match_result, self.pos);
                        Ok(TableFrameResult::Done)
                    }
                    Err(e) => Err(e),
                }
            }
            GrammarVariant::Meta => {
                let res = self.handle_meta_table_driven(grammar_id);
                match res {
                    Ok(match_result) => {
                        vdebug!(
                            "[SYNC INSERT] frame_id={} Meta result at pos {} -> MatchResult",
                            frame.frame_id,
                            self.pos
                        );
                        stack.insert_result(frame.frame_id, match_result, self.pos);
                        Ok(TableFrameResult::Done)
                    }
                    Err(e) => Err(e),
                }
            }
            GrammarVariant::NonCodeMatcher => {
                let res = self.handle_noncode_matcher_table_driven();
                match res {
                    Ok(match_result) => {
                        vdebug!(
                            "[SYNC INSERT] frame_id={} NonCodeMatcher result at pos {} -> MatchResult",
                            frame.frame_id,
                            self.pos
                        );
                        stack.insert_result(frame.frame_id, match_result, self.pos);
                        Ok(TableFrameResult::Done)
                    }
                    Err(e) => Err(e),
                }
            }
            GrammarVariant::Anything => {
                let res = self.handle_anything_table_driven(
                    grammar_id,
                    &table_terminators,
                    frame.parent_max_idx,
                );
                match res {
                    Ok(match_result) => {
                        vdebug!(
                            "[SYNC INSERT] frame_id={} Anything result at pos {} -> MatchResult",
                            frame.frame_id,
                            self.pos
                        );
                        stack.insert_result(frame.frame_id, match_result, self.pos);
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
        _child_index: usize,
        _total_children: usize,
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
        vdebug!(
            "[RESULT GET] parent_frame_id={}, child_frame_id={}, child_found={}",
            frame.frame_id,
            child_frame_id,
            child.is_some()
        );

        if let Some((child_node, child_end_pos, _child_element_key)) = &child {
            vdebug!(
                "[RESULT FOUND] parent_frame_id={}, child_frame_id={}, child_end_pos={}",
                frame.frame_id,
                child_frame_id,
                child_end_pos
            );
            vdebug!(
                "Child {} of {} completed (frame_id={}): pos {} -> {}",
                _child_index,
                _total_children,
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
            vdebug!(
                "Child result not found for frame_id={}, last_child_frame_id={:?}, pushing frame back onto stack",
                frame.frame_id,
                last_child_frame_id
            );

            // Check if we're in an infinite loop - frame waiting for child that doesn't exist
            if iteration_count > 100 && iteration_count.is_multiple_of(100) {
                vdebug!(
                    "WARNING: Frame {} waiting for child {:?} but result not found (iteration {})",
                    frame.frame_id,
                    last_child_frame_id,
                    iteration_count
                );

                // Check if child is on stack
                if let Some(child_id) = last_child_frame_id {
                    let child_on_stack = stack.iter().any(|f| f.frame_id == child_id);
                    if child_on_stack {
                        vdebug!(
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

        let grammar_id = frame.grammar_id;
        let inst = self.grammar_ctx.inst(grammar_id);
        let variant = inst.variant;

        vdebug!(
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
        match_result: &MatchResult,
    ) {
        // Log grammar path - different indicator for Empty vs matched nodes
        #[cfg(feature = "verbose-debug")]
        let end_pos = frame.end_pos.unwrap_or(self.pos);
        if match_result.is_empty() {
            vdebug!(
                "❌ No match at pos {}: {}",
                frame.pos,
                self.build_table_grammar_path(frame, stack)
            );
        } else {
            vdebug!(
                "✅ Match at pos {}-{}: {}",
                frame.pos,
                end_pos.saturating_sub(1),
                self.build_table_grammar_path(frame, stack)
            );
        }

        // Use the end_pos stored in the frame (or fall back to self.pos)
        let end_pos = frame.end_pos.unwrap_or(self.pos);

        // Get element_key if any (set by OneOf for AnyNumberOf tracking)
        let element_key = frame.element_key;

        // This frame is done - insert result
        stack.insert_result_with_key(frame.frame_id, match_result.clone(), end_pos, element_key);

        // Cache the result for future reuse
        // Cache non-empty results always, but only cache Empty results when
        // terminators are empty (otherwise the Empty might become non-Empty
        // with different terminator context)
        if self.cache_enabled {
            let should_cache_empty = match_result.is_empty() && frame.table_terminators.is_empty();
            let should_cache_success = !match_result.is_empty();

            if should_cache_empty || should_cache_success {
                let variant = self.grammar_ctx.variant(frame.grammar_id);

                // Cache strategy to match Python behavior:
                // - Ref: Always cache (deterministic pointer)
                // - OneOf: Safe to cache (picks best of alternatives, no partial matches)
                // - Bracketed: Safe to cache (deterministic open/close)
                // - Delimited: Safe to cache (deterministic delimiter pattern)
                // - Sequence: NEVER cache (partial GREEDY matches pollute cache)
                // - AnyNumberOf: NEVER cache (can match N items, then later match N+M)
                // - AnySetOf: NEVER cache (similar to AnyNumberOf)
                //
                // Python avoids these issues by caching at element level (inside longest_match),
                // not at complete grammar level.
                let should_cache = matches!(
                    variant,
                    GrammarVariant::Ref
                        | GrammarVariant::OneOf
                        | GrammarVariant::Delimited
                        | GrammarVariant::Bracketed
                );

                if should_cache {
                    // Use handler-calculated max_idx if available, otherwise calculate it
                    // This should match what was used in check_and_handle_table_frame_cache
                    let max_idx = if let Some(calc_max) = frame.calculated_max_idx {
                        calc_max
                    } else {
                        // Fallback: calculate max_idx ourselves
                        // CRITICAL: Must use parse_mode_override if present (Bracketed inheritance)
                        let parse_mode = frame
                            .parse_mode_override
                            .unwrap_or_else(|| self.grammar_ctx.inst(frame.grammar_id).parse_mode);
                        match self.calculate_max_idx_table_driven(
                            frame.pos,
                            &frame.table_terminators,
                            parse_mode,
                            frame.parent_max_idx,
                        ) {
                            Ok(idx) => idx,
                            Err(_) => {
                                // If max_idx calculation fails, skip caching
                                return;
                            }
                        }
                    };

                    let cache_key = TableCacheKey::new(frame.pos, frame.grammar_id, max_idx);
                    // Get transparent positions for this frame
                    let transparent_opt = frame.transparent_positions.clone();
                    // Cache as Arc<MatchResult> (cheap to clone later)
                    self.table_cache.put(
                        cache_key,
                        (Arc::new(match_result.clone()), end_pos, transparent_opt),
                    );
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
            // Only check cache for grammar types we actually cache
            // This matches the caching strategy in handle_table_frame_complete
            let variant = self.grammar_ctx.variant(frame.grammar_id);
            let is_cacheable = matches!(
                variant,
                GrammarVariant::Ref
                    | GrammarVariant::OneOf
                    | GrammarVariant::Delimited
                    | GrammarVariant::Bracketed
            );

            if is_cacheable {
                // Use handler-calculated max_idx if available (set by handler after calculating)
                // Otherwise calculate it ourselves (for frames that haven't been processed yet)
                let max_idx = if let Some(calc_max) = frame.calculated_max_idx {
                    calc_max
                } else {
                    // Calculate max_idx the same way the grammar handler would
                    // CRITICAL: Must use parse_mode_override if present (Bracketed inheritance)
                    let parse_mode = frame
                        .parse_mode_override
                        .unwrap_or_else(|| self.grammar_ctx.inst(frame.grammar_id).parse_mode);
                    self.calculate_max_idx_table_driven(
                        frame.pos,
                        &frame.table_terminators,
                        parse_mode,
                        frame.parent_max_idx,
                    )?
                };

                let cache_key = TableCacheKey::new(frame.pos, frame.grammar_id, max_idx);
                if let Some((match_result, end_pos, transparent_positions)) =
                    self.table_cache.get(&cache_key)
                {
                    vdebug!(
                        "[LOOP] TableCache HIT for grammar {} at pos {} -> end_pos {} (frame_id={})",
                        frame.grammar_id,
                        frame.pos,
                        end_pos,
                        frame.frame_id
                    );
                    self.pos = *end_pos;
                    if let Some(positions) = transparent_positions {
                        for &pos in positions {
                            if !self.collected_transparent_positions.contains(&pos) {
                                self.collected_transparent_positions.push(pos);
                            }
                        }
                    }
                    // Insert cached MatchResult - match_result is &Arc, clone the Arc (cheap refcount)
                    stack.insert_arc_result(frame.frame_id, Arc::clone(match_result), *end_pos);
                    return Ok(TableFrameResult::Done);
                }
            }
        }
        // Cache miss or cache disabled or non-cacheable grammar - push frame back to process normally
        Ok(TableFrameResult::Push(frame))
    }

    fn handle_table_max_iterations_exceeded(
        &mut self,
        _stack: &mut TableParseFrameStack,
        _max_iterations: usize,
        _frame: &mut TableParseFrame,
    ) {
        vdebug!("ERROR: Exceeded max iterations ({})", _max_iterations);
        vdebug!("Last frame: {:?}", _frame.grammar_id);
        vdebug!("Stack depth: {}", _stack.len());
        vdebug!("Results count: {}", _stack.results.len());

        // Print last 20 frames on stack for diagnosis
        vdebug!("\n=== Last 20 frames on stack ===");
        #[cfg(feature = "verbose-debug")]
        for (i, f) in _stack.iter().rev().take(20).enumerate() {
            vdebug!(
                "  [{}] state={:?}, pos={}, grammar={}",
                i,
                f.state,
                f.pos,
                match self.grammar_ctx.variant(f.grammar_id) {
                    GrammarVariant::Ref =>
                        format!("Ref({})", self.grammar_ctx.ref_name(f.grammar_id)),
                    GrammarVariant::Bracketed => "Bracketed".to_string(),
                    GrammarVariant::Delimited => "Delimited".to_string(),
                    GrammarVariant::OneOf => format!(
                        "OneOf({} elements)",
                        self.grammar_ctx.children_count(f.grammar_id)
                    ),
                    GrammarVariant::Sequence => format!(
                        "Sequence({} elements)",
                        self.grammar_ctx.children_count(f.grammar_id)
                    ),
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
    #[cfg(feature = "verbose-debug")]
    fn build_table_grammar_path(
        &self,
        frame: &TableParseFrame,
        stack: &TableParseFrameStack,
    ) -> String {
        let mut path_parts = Vec::new();

        // Helper to get a name for either Grammar or GrammarId
        fn grammar_id_name(parser: &Parser, frame: &TableParseFrame) -> String {
            // Table-driven: show grammar_id and its name if available
            let ctx = &parser.grammar_ctx;
            let name = match ctx.variant(frame.grammar_id) {
                sqlfluffrs_types::GrammarVariant::Ref => ctx.ref_name(frame.grammar_id),
                sqlfluffrs_types::GrammarVariant::StringParser
                | sqlfluffrs_types::GrammarVariant::TypedParser
                | sqlfluffrs_types::GrammarVariant::MultiStringParser
                | sqlfluffrs_types::GrammarVariant::RegexParser => ctx.template(frame.grammar_id),
                _ => &format!("{:?}", ctx.variant(frame.grammar_id)),
            };
            format!("id[{}:{:?}]", frame.grammar_id.0, name)
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

#[cfg(feature = "verbose-debug")]
fn get_waiting_for_frame_id(frame: &TableParseFrame) -> String {
    match &frame.context {
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
    }
}
