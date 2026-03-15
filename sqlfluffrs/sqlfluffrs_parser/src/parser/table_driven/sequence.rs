use crate::{
    parser::{match_result::MatchedClass, MetaSegment},
    vdebug,
};
use smallvec::SmallVec;
use sqlfluffrs_types::{GrammarId, GrammarVariant, ParseMode};
use std::sync::Arc;

use crate::parser::{
    table_driven::frame::{TableFrameResult, TableParseFrame, TableParseFrameStack},
    FrameContext, FrameState, MatchResult, ParseError, Parser,
};

impl Parser<'_> {
    // ========================================================================
    // Table-Driven Sequence Handlers
    // ========================================================================

    /// Handle Sequence Initial state using table-driven approach
    pub(crate) fn handle_sequence_table_driven_initial(
        &mut self,
        mut frame: TableParseFrame,
        stack: &mut TableParseFrameStack,
    ) -> Result<TableFrameResult, ParseError> {
        self.pos = frame.pos;
        let start_idx = self.pos;
        let seq_grammar_id = frame.grammar_id;
        let reset_terminators = self
            .grammar_ctx
            .inst(seq_grammar_id)
            .flags
            .reset_terminators();
        // Check for parse_mode_override first (Bracketed GREEDY mode inheritance)
        let parse_mode = frame
            .parse_mode_override
            .unwrap_or_else(|| self.grammar_ctx.inst(seq_grammar_id).parse_mode);
        let allow_gaps = self.grammar_ctx.inst(seq_grammar_id).flags.allow_gaps();
        let current_element_idx = 0;

        #[cfg(feature = "verbose-debug")]
        if frame.parse_mode_override.is_some() {
            vdebug!(
                "Sequence[table] Initial: Using parse_mode_override={:?} (native={:?})",
                parse_mode,
                self.grammar_ctx.inst(seq_grammar_id).parse_mode
            );
        }

        let local_terminators = self
            .grammar_ctx
            .terminators(seq_grammar_id)
            .collect::<Vec<_>>();
        let elements = self
            .grammar_ctx
            .children(seq_grammar_id)
            .collect::<Vec<_>>();

        // Handle empty elements case - sequence with no elements should succeed immediately
        if elements.is_empty() {
            // Transition to Combining to finalize empty Sequence result
            return Ok(stack.complete_frame_empty(&frame));
        }

        // combine parent and local terminators (read parent from frame directly)
        let all_terminators = self.combine_table_terminators(
            &local_terminators,
            &frame.table_terminators,
            reset_terminators,
        );

        // calculate max_idx with terminator and parent constraints
        let max_idx = self.calculate_max_idx_table_driven(
            start_idx,
            &all_terminators,
            parse_mode,
            frame.parent_max_idx,
        )?;

        // Store calculated max_idx in frame for cache consistency
        frame.calculated_max_idx = Some(max_idx);

        // make initial skip to first non-meta element if needed
        let child_start_pos = self.calculate_sequence_child_start_position(
            start_idx,
            allow_gaps,
            elements[current_element_idx],
            max_idx,
        );

        if child_start_pos >= max_idx {
            // at this point, we haven't matched anything yet, and we're already at or past max_idx
            // we should return empty
            vdebug!(
                "Sequence[table]: No tokens to consume (start_idx={}, max_idx={}), returning Empty",
                child_start_pos,
                max_idx
            );
            return Ok(stack.complete_frame_empty(&frame));
        }

        // Create initial child frame for the first element candidate and
        // let the WaitingForChild handler iterate remaining candidates.
        let child_frame_id = stack.frame_id_counter;
        let frame_pos = frame.pos;

        // Update frame with Sequence context
        frame.context = FrameContext::SequenceTableDriven {
            seq_grammar_id,
            start_idx: frame.pos,
            matched_idx: frame.pos,
            max_idx,
            original_max_idx: max_idx, // Store original before any GREEDY_ONCE_STARTED trimming
            last_child_frame_id: Some(child_frame_id),
            current_element_idx,         // Start at first element
            first_match: true,           // For GREEDY_ONCE_STARTED trimming
            meta_buffer: Vec::new(),     // Buffer for meta elements to flush
            insert_segments: Vec::new(), // (position, segments) to insert
            child_matches: Vec::new(),   // Store child matches here until sequence is complete
        };
        frame.table_terminators = SmallVec::from_vec(all_terminators);

        // Buffer any leading meta elements before creating first child
        self.buffer_trailing_meta_elements(&mut frame, &elements);

        // Get updated current_element_idx after meta buffering
        let current_element_idx = {
            let ctx = frame.context.as_sequence_mut().unwrap();
            *ctx.current_element_idx
        };

        // Check if we buffered all elements (all were meta)
        if current_element_idx >= elements.len() {
            // All elements were meta - transition to combining
            return Ok(stack.transition_to_combining(frame, Some(frame_pos)));
        }

        // Create child frame with potentially new element after meta buffering
        let child_frame = TableParseFrame::new_child(
            child_frame_id,
            elements[current_element_idx],
            child_start_pos,
            frame.table_terminators.to_vec(),
            Some(max_idx),
        );

        // Match the first child
        Ok(stack.push_child_and_wait(frame, child_frame, current_element_idx))
    }

    /// Helper function to buffer trailing meta elements starting from current_element_idx
    /// Returns the number of meta elements buffered
    #[inline]
    fn buffer_trailing_meta_elements(&self, frame: &mut TableParseFrame, elements: &[GrammarId]) {
        let mut ctx = frame.context.as_sequence_mut().unwrap();
        let current_idx = *ctx.current_element_idx;

        for child_id in &elements[current_idx..elements.len()] {
            if self.grammar_ctx.variant(*child_id) == GrammarVariant::Meta {
                let meta_segment = self.grammar_id_to_meta_segment(*child_id);
                if let Some(meta_segment) = meta_segment {
                    ctx.buffer_meta(meta_segment);
                }
                ctx.advance_element_idx();
            } else {
                return;
            }
        }
        vdebug!("End of elements, we should move to combining now.");
    }

    /// Handle Sequence grammar Waiting for child state
    /// child_match - the MatchResult from the child parse
    /// child_end_pos,
    /// child_element_key,
    /// stack,
    pub(crate) fn handle_sequence_table_driven_waiting_for_child(
        &mut self,
        mut frame: TableParseFrame,
        child_match: &Arc<MatchResult>,
        child_end_pos: &usize,
        stack: &mut TableParseFrameStack,
    ) -> Result<TableFrameResult, ParseError> {
        // Extract needed values from context ONCE before any mutable operations
        let (seq_grammar_id, current_element_idx, matched_idx, max_idx, start_idx, _first_match) = {
            let ctx = frame.context.as_sequence_mut().unwrap();
            (
                *ctx.seq_grammar_id,
                *ctx.current_element_idx,
                *ctx.matched_idx,
                *ctx.max_idx,
                *ctx.start_idx,
                *ctx.first_match,
            )
        };

        // Get parse mode and grammar properties (immutable lookups)
        let parse_mode = frame
            .parse_mode_override
            .unwrap_or_else(|| self.grammar_ctx.inst(seq_grammar_id).parse_mode);
        let allow_gaps = self.grammar_ctx.inst(seq_grammar_id).flags.allow_gaps();
        let elements: Vec<GrammarId> = self.grammar_ctx.children(seq_grammar_id).collect();
        let current_element_grammar_id = elements[current_element_idx];
        let current_element_optional = self.grammar_ctx.is_optional(current_element_grammar_id);

        vdebug!(
            "Sequence[table] WaitingForChild: frame_id={}, child_empty={}, child_end_pos={}, current_idx={}/{}, matched_idx={}, first_match={}",
            frame.frame_id,
            child_match.is_empty(),
            child_end_pos,
            current_element_idx,
            elements.len(),
            matched_idx,
            _first_match
        );

        // Handle failed match.
        // NOTE: A non-empty match that contains_unparsable() is still a VALID match
        // (the unparsable content is part of the result, e.g. from GREEDY mode).
        // Only truly empty matches indicate failure, matching Python's behaviour
        // which only checks `not result` (i.e. zero-length).
        if child_match.is_empty() {
            return self.handle_sequence_child_failure(
                frame,
                current_element_optional,
                current_element_grammar_id,
                parse_mode,
                matched_idx,
                start_idx,
                max_idx,
                allow_gaps,
                &elements,
                stack,
            );
        }

        // Handle successful match
        self.handle_sequence_child_success(
            frame,
            child_match,
            *child_end_pos,
            allow_gaps,
            parse_mode,
            &elements,
            stack,
        )
    }

    /// Handle failed child match in sequence
    #[allow(clippy::too_many_arguments)]
    #[inline]
    fn handle_sequence_child_failure(
        &mut self,
        mut frame: TableParseFrame,
        current_element_optional: bool,
        current_element_grammar_id: GrammarId,
        parse_mode: ParseMode,
        matched_idx: usize,
        start_idx: usize,
        max_idx: usize,
        allow_gaps: bool,
        elements: &[GrammarId],
        stack: &mut TableParseFrameStack,
    ) -> Result<TableFrameResult, ParseError> {
        vdebug!(
            "Sequence[table]: Child failed, optional={}, mode={:?}",
            current_element_optional,
            parse_mode
        );

        let next_element_idx = {
            let mut ctx = frame.context.as_sequence_mut().unwrap();
            ctx.advance_element_idx();
            *ctx.current_element_idx
        };

        // If element is optional or a Meta grammar, skip it and continue
        if current_element_optional
            || self.grammar_ctx.variant(current_element_grammar_id) == GrammarVariant::Meta
        {
            // Optional element - skip and continue to next
            if next_element_idx >= elements.len() {
                // Flush any buffered metas before going to combining
                let pending_metas = {
                    let mut ctx = frame.context.as_sequence_mut().unwrap();
                    ctx.take_meta_buffer()
                };
                if !pending_metas.is_empty() {
                    let insert_positions =
                        self.flush_meta_buffer(matched_idx, matched_idx, pending_metas);
                    let ctx = frame.context.as_sequence_mut().unwrap();
                    ctx.insert_segments.extend(insert_positions);
                }
                // All children processed - go to combining
                return Ok(stack.transition_to_combining(frame, Some(matched_idx)));
            }

            self.buffer_trailing_meta_elements(&mut frame, elements);

            // Update next_element_idx after buffering metas
            let next_element_idx = {
                let ctx = frame.context.as_sequence_mut().unwrap();
                *ctx.current_element_idx
            };

            // We should check again if we're done after buffering metas if we're out of elements
            if next_element_idx >= elements.len() {
                // Flush any buffered metas before going to combining
                let pending_metas = {
                    let mut ctx = frame.context.as_sequence_mut().unwrap();
                    ctx.take_meta_buffer()
                };
                if !pending_metas.is_empty() {
                    let insert_positions =
                        self.flush_meta_buffer(matched_idx, matched_idx, pending_metas);
                    let ctx = frame.context.as_sequence_mut().unwrap();
                    ctx.insert_segments.extend(insert_positions);
                }
                // All children processed - go to combining
                return Ok(stack.transition_to_combining(frame, Some(matched_idx)));
            }

            let child_start_pos = self.calculate_sequence_child_start_position(
                matched_idx,
                allow_gaps,
                elements[next_element_idx],
                max_idx,
            );

            // PYTHON PARITY: Check if we've run out of tokens before dispatching next child.
            // In Python's sequence.py, `_idx >= max_idx` is checked before trying to match
            // any element (including optional ones we've already skipped). If we're out of
            // tokens and the *next required* element cannot be matched, wrap what we've got
            // as an unparsable segment (in greedy modes), just as Python does.
            //
            // Only apply this when the next element is REQUIRED. If it's optional, we let it
            // be dispatched normally so that the optional-skip loop can continue until either
            // a required element is found or all elements are exhausted (-> combining).
            let next_is_optional = self.grammar_ctx.is_optional(elements[next_element_idx]);
            if child_start_pos >= max_idx && !next_is_optional {
                if parse_mode == ParseMode::Strict || matched_idx == start_idx {
                    return Ok(stack.complete_frame_empty_at_pos(&frame, start_idx));
                }
                // GREEDY modes with partial match - wrap as UnparsableSegment
                let (insert_segments, child_matches) = {
                    let ctx = frame.context.as_sequence_mut().unwrap();
                    let appending_meta_segments = ctx
                        .meta_buffer
                        .iter()
                        .cloned()
                        .map(|m| (matched_idx, m))
                        .collect::<Vec<_>>();
                    ctx.insert_segments.extend(appending_meta_segments);
                    (
                        std::mem::take(ctx.insert_segments),
                        std::mem::take(ctx.child_matches),
                    )
                };
                let element_desc = self.grammar_ctx.grammar_repr(elements[next_element_idx]);
                let error_token = self
                    .tokens
                    .get(matched_idx.saturating_sub(1))
                    .map(|t| format!("{}", t))
                    .unwrap_or_else(|| "start of input".to_string());
                let error_message =
                    format!("{} after {}. Found nothing.", element_desc, error_token);
                let unparsable_match = MatchResult {
                    matched_slice: start_idx..matched_idx,
                    insert_segments,
                    child_matches,
                    ..Default::default()
                }
                .wrap(
                    MatchedClass::unparsable(&error_message, matched_idx),
                    vec![],
                );
                let end_pos = unparsable_match.end();
                stack.insert_result(frame.frame_id, unparsable_match, end_pos);
                return Ok(TableFrameResult::Done);
            }

            let child_frame_id = stack.frame_id_counter;
            let child_frame = self.match_sequence_next_element(
                &frame,
                next_element_idx,
                matched_idx,
                max_idx,
                allow_gaps,
                elements,
                child_frame_id,
            );
            stack.push(frame);
            // continue to next element
            return Ok(stack.update_sequence_parent_and_push_child(child_frame, next_element_idx));
        }

        // Required element failed - handle based on parse mode
        if parse_mode == ParseMode::Strict
            || (matched_idx == start_idx && parse_mode != ParseMode::Greedy)
        {
            // STRICT mode or GREEDY_ONCE_STARTED with no matches yet
            // - return Empty, from the beginning of the sequence
            return Ok(stack.complete_frame_empty_at_pos(&frame, start_idx));
        }

        // GREEDY modes with partial match - create UnparsableSegment
        let child_start_pos = self.calculate_sequence_child_start_position(
            matched_idx,
            allow_gaps,
            elements
                .get(next_element_idx)
                .copied()
                .unwrap_or(current_element_grammar_id),
            max_idx,
        );

        if matched_idx == start_idx {
            let element_desc = self.grammar_ctx.grammar_repr(current_element_grammar_id);
            let error_token = self
                .tokens
                .get(child_start_pos)
                .map(|t| format!("{}", t))
                .unwrap_or_else(|| "start of input".to_string());
            let error_message =
                format!("{} to start sequence. Found {}.", element_desc, error_token);

            let unparsable_match = MatchResult {
                matched_slice: start_idx..max_idx,
                matched_class: Some(MatchedClass::unparsable(&error_message, child_start_pos)),
                ..Default::default()
            };
            let end_pos = unparsable_match.end();
            stack.insert_result(frame.frame_id, unparsable_match, end_pos);
            return Ok(TableFrameResult::Done);
        }

        // Failed after partial match
        let element_desc = self.grammar_ctx.grammar_repr(current_element_grammar_id);
        let error_token = self
            .tokens
            .get(child_start_pos)
            .map(|t| format!("{}", t))
            .unwrap_or_else(|| "end of input".to_string());
        let last_matched_token = self
            .tokens
            .get(matched_idx.saturating_sub(1))
            .map(|t| format!("{}", t))
            .expect("There should be at least one matched token here.");
        let error_message = format!(
            "{} after {}. Found {}.",
            element_desc, last_matched_token, error_token
        );

        let unparsable_match = MatchResult {
            matched_slice: child_start_pos..max_idx,
            matched_class: Some(MatchedClass::unparsable(&error_message, child_start_pos)),
            ..Default::default()
        };
        let end_pos = unparsable_match.end();
        stack.insert_result(frame.frame_id, unparsable_match, end_pos);
        Ok(TableFrameResult::Done)
    }

    /// Handle successful child match in sequence
    #[allow(clippy::too_many_arguments)]
    #[inline]
    fn handle_sequence_child_success(
        &mut self,
        mut frame: TableParseFrame,
        child_match: &Arc<MatchResult>,
        child_end_pos: usize,
        allow_gaps: bool,
        parse_mode: ParseMode,
        elements: &[GrammarId],
        stack: &mut TableParseFrameStack,
    ) -> Result<TableFrameResult, ParseError> {
        // Flush meta buffer before adding successful match
        let (matched_idx, max_idx, pending_metas, is_first) = {
            let mut ctx = frame.context.as_sequence_mut().unwrap();
            (
                ctx.matched_idx_value(),
                ctx.max_idx_value(),
                ctx.take_meta_buffer(),
                ctx.is_first_match(),
            )
        };

        if !pending_metas.is_empty() {
            let pre_code_idx = matched_idx;
            let post_code_idx = if allow_gaps {
                self.skip_start_index_forward_to_code(pre_code_idx, max_idx)
            } else {
                pre_code_idx
            };
            let insert_positions =
                self.flush_meta_buffer(pre_code_idx, post_code_idx, pending_metas);
            let ctx = frame.context.as_sequence_mut().unwrap();
            ctx.insert_segments.extend(insert_positions);
        }

        // Add child match to context
        {
            let mut ctx = frame.context.as_sequence_mut().unwrap();
            ctx.update_matched_idx(child_end_pos);
        }

        // Handle GREEDY_ONCE_STARTED mode trimming after first match
        if is_first && parse_mode == ParseMode::GreedyOnceStarted {
            let mut ctx = frame.context.as_sequence_mut().unwrap();
            ctx.mark_first_match_done();

            let matched_idx = ctx.matched_idx_value();
            let new_max_idx =
                self.trim_to_terminator_table_driven(matched_idx, &frame.table_terminators)?;

            let mut ctx = frame.context.as_sequence_mut().unwrap();
            ctx.trim_max_idx(new_max_idx);
        }

        // How we deal with child segments depends on whether it had a matched
        // class or not.
        // If it did, then just add it as a child match and we're done. Move on.
        {
            let mut ctx = frame.context.as_sequence_mut().unwrap();
            if child_match.matched_class.is_some() {
                ctx.child_matches.push(Arc::clone(child_match));
            } else {
                ctx.child_matches.extend(child_match.child_matches.clone());
                ctx.insert_segments
                    .extend(child_match.insert_segments.clone());
            }

            ctx.advance_element_idx();
        }

        // Buffer trailing META children after this match
        self.buffer_trailing_meta_elements(&mut frame, elements);

        // Check if sequence is complete or create next child
        let (current_idx, matched_idx, max_idx) = {
            let ctx = frame.context.as_sequence_mut().unwrap();
            (
                *ctx.current_element_idx,
                ctx.matched_idx_value(),
                ctx.max_idx_value(),
            )
        };

        if current_idx >= elements.len() {
            // Flush remaining metas and finalize
            let pending_metas = {
                let mut ctx = frame.context.as_sequence_mut().unwrap();
                ctx.take_meta_buffer()
            };
            if !pending_metas.is_empty() {
                let insert_positions =
                    self.flush_meta_buffer(matched_idx, matched_idx, pending_metas);
                let ctx = frame.context.as_sequence_mut().unwrap();
                ctx.insert_segments.extend(insert_positions);
            }
            self.pos = matched_idx;
            frame.end_pos = Some(matched_idx);
            frame.state = FrameState::Combining;
            stack.push(frame);
            return Ok(TableFrameResult::Done);
        }

        // Calculate start position for next child
        let next_element = elements[current_idx];
        let child_start_pos = if allow_gaps {
            self.skip_start_index_forward_to_code(matched_idx, max_idx)
        } else {
            matched_idx
        };

        // Have we prematurely run out of segments?
        if child_start_pos >= max_idx {
            // Check if next element is optional - if so, create child frame for it
            if self.grammar_ctx.is_optional(next_element) {
                let child_frame_id = stack.frame_id_counter;
                let child_frame = TableParseFrame::new_child(
                    child_frame_id,
                    next_element,
                    matched_idx,
                    frame.table_terminators.to_vec(),
                    Some(max_idx),
                );
                stack.push(frame);
                return Ok(stack.update_sequence_parent_and_push_child(child_frame, current_idx));
            }

            // Required element but no segments left
            let start_idx = frame.pos;

            if parse_mode == ParseMode::Strict || matched_idx == start_idx {
                // STRICT mode or nothing matched - return Empty
                return Ok(stack.complete_frame_empty_at_pos(&frame, start_idx));
            }

            // GREEDY modes with partial match - wrap as UnparsableSegment
            let (insert_segments, child_matches) = {
                let ctx = frame.context.as_sequence_mut().unwrap();
                let appending_meta_segments = ctx
                    .meta_buffer
                    .iter()
                    .cloned()
                    .map(|m| (matched_idx, m))
                    .collect::<Vec<_>>();
                ctx.insert_segments.extend(appending_meta_segments);
                (
                    std::mem::take(ctx.insert_segments),
                    std::mem::take(ctx.child_matches),
                )
            };

            let element_desc = self.grammar_ctx.grammar_repr(next_element);
            let error_token = self
                .tokens
                .get(matched_idx.saturating_sub(1))
                .map(|t| format!("{}", t))
                .unwrap_or_else(|| "start of input".to_string());
            let error_message = format!("{} after {}. Found nothing.", element_desc, error_token);

            let unparsable_match = MatchResult {
                matched_slice: start_idx..matched_idx,
                insert_segments,
                child_matches,
                ..Default::default()
            }
            .wrap(
                MatchedClass::unparsable(&error_message, matched_idx),
                vec![],
            );

            let end_pos = unparsable_match.end();
            stack.insert_result(frame.frame_id, unparsable_match, end_pos);
            return Ok(TableFrameResult::Done);
        }

        // Create child frame for next element
        let child_frame_id = stack.frame_id_counter;
        let child_frame = TableParseFrame::new_child(
            child_frame_id,
            next_element,
            child_start_pos,
            frame.table_terminators.to_vec(),
            Some(max_idx),
        );

        stack.push(frame);
        Ok(stack.update_sequence_parent_and_push_child(child_frame, current_idx))
    }

    #[allow(clippy::too_many_arguments)]
    #[inline]
    fn match_sequence_next_element(
        &self,
        frame: &TableParseFrame,
        next_element_idx: usize,
        matched_idx: usize,
        max_idx: usize,
        allow_gaps: bool,
        elements: &[GrammarId],
        child_frame_id: usize,
    ) -> TableParseFrame {
        let child_start_pos = self.calculate_sequence_child_start_position(
            matched_idx,
            allow_gaps,
            elements[next_element_idx],
            max_idx,
        );
        TableParseFrame::new_child(
            child_frame_id,
            elements[next_element_idx],
            child_start_pos,
            frame.table_terminators.to_vec(),
            Some(max_idx),
        )
    }

    /// Handle Sequence Combining state using table-driven approach
    pub(crate) fn handle_sequence_table_driven_combining(
        &mut self,
        mut frame: TableParseFrame,
        _stack: &mut TableParseFrameStack,
    ) -> Result<TableFrameResult, ParseError> {
        // Take ownership of the context fields we need, avoiding clones.
        // The frame is consumed after combining, so this is safe.
        let (grammar_id, matched_idx, max_idx, mut child_matches, insert_segments) = {
            let FrameContext::SequenceTableDriven {
                seq_grammar_id,
                matched_idx,
                max_idx,
                child_matches,
                insert_segments,
                ..
            } = &mut frame.context
            else {
                return Err(ParseError::new(
                    "Expected SequenceTableDriven context in combining".to_string(),
                ));
            };
            (
                *seq_grammar_id,
                *matched_idx,
                *max_idx,
                std::mem::take(child_matches),
                std::mem::take(insert_segments),
            )
        };

        // Get parse_mode from grammar
        let inst = self.grammar_ctx.inst(grammar_id);
        let parse_mode = inst.parse_mode;

        vdebug!(
            "Sequence[table] Combining: frame_id={}, accumulated={}, matched_idx={}, max_idx={}, parse_mode={:?}",
            frame.frame_id,
            child_matches.len(),
            matched_idx,
            max_idx,
            parse_mode
        );
        #[cfg(feature = "verbose-debug")]
        for (i, child) in child_matches.iter().enumerate() {
            vdebug!("  Combining accumulated[{}]: {:?}", i, child);
        }

        let result_match = if child_matches.is_empty()
            && matched_idx == frame.pos
            && insert_segments.is_empty()
        {
            Arc::new(MatchResult::empty_at(frame.pos))
        } else {
            let mut final_matched_idx = matched_idx;

            // PYTHON PARITY: If we're in GREEDY mode and there's leftover content,
            // create an UnparsableSegment for it.
            // This matches Python's sequence.py lines 346-365:
            //   if self.parse_mode in (ParseMode.GREEDY, ParseMode.GREEDY_ONCE_STARTED):
            //       if max_idx > matched_idx:
            //           ...create UnparsableSegment...
            if (parse_mode == ParseMode::Greedy || parse_mode == ParseMode::GreedyOnceStarted)
                && max_idx > matched_idx
            {
                // Skip to code token position
                let _idx = self.skip_start_index_forward_to_code(matched_idx, max_idx);
                let _stop_idx = self.skip_stop_index_backward_to_code(max_idx, _idx);

                if _stop_idx > _idx {
                    vdebug!(
                        "Sequence[table] Combining: GREEDY mode leftover content from {} to {}, creating UnparsableSegment",
                        _idx,
                        _stop_idx
                    );

                    let mut segment_kwargs = hashbrown::HashMap::new();
                    segment_kwargs.insert("expected".to_string(), "Nothing here.".to_string());

                    child_matches.push(Arc::new(MatchResult {
                        matched_slice: _idx.._stop_idx,
                        matched_class: Some(MatchedClass::unparsable("Nothing here.", _stop_idx)),
                        ..Default::default()
                    }));

                    // Match up to the end
                    final_matched_idx = _stop_idx;
                }
            }

            Arc::new(MatchResult {
                matched_slice: frame.pos..final_matched_idx,
                insert_segments,
                child_matches,
                ..Default::default()
            })
        };

        self.pos = result_match.end();
        frame.end_pos = Some(result_match.end());
        frame.state = FrameState::Complete(result_match);

        Ok(TableFrameResult::Push(frame))
    }

    /// Flush buffered meta segments, positioning them relative to whitespace boundary.
    /// Follows Python's _flush_metas() pattern from sequence.py.
    ///
    /// - `accumulated`: The accumulated match results to insert metas into
    /// - `pre_code_idx`: Position before whitespace (where positive indents go)
    /// - `post_code_idx`: Position after whitespace (where negative dedents go)
    /// - `meta_buffer`: The buffered meta grammar IDs to flush
    #[inline]
    pub(crate) fn flush_meta_buffer(
        &self,
        pre_code_idx: usize,
        post_code_idx: usize,
        meta_buffer: Vec<MetaSegment>,
    ) -> Vec<(usize, MetaSegment)> {
        // PYTHON PARITY: Check if ALL metas have positive indent values
        // If all positive → position at pre_code_idx (before whitespace)
        // If any negative → position at post_code_idx (after whitespace)

        let all_positive = meta_buffer
            .iter()
            .all(|meta_segment| !matches!(meta_segment, MetaSegment::Dedent { .. }));

        // Second pass: determine position and insert metas
        // PYTHON PARITY: Match Python's _flush_metas() logic exactly.
        // If all metas are positive (indents):
        //   - Search backward from post_code_idx to pre_code_idx for block_end placeholder
        //   - If found, position before it; otherwise use pre_code_idx
        // If any meta is negative (has dedent):
        //   - Search forward from pre_code_idx to post_code_idx for block_start placeholder
        //   - If found, position after it; otherwise use post_code_idx
        let meta_idx = if all_positive {
            // All indents - look backward for block_end placeholder
            let mut found_idx = None;
            for idx in (pre_code_idx + 1..=post_code_idx).rev() {
                if idx > 0 && idx <= self.tokens.len() {
                    let tok = &self.tokens[idx - 1];
                    if tok.is_type(&["placeholder"]) {
                        // Check if it's a block_end
                        if let Some(block_type) = tok.block_type.as_ref() {
                            if block_type == "block_end" {
                                found_idx = Some(idx);
                            } else {
                                // Found a placeholder but NOT block_end
                                // Python sets meta_idx = pre_nc_idx in this case
                                found_idx = Some(pre_code_idx);
                            }
                        } else {
                            // Placeholder with no block_type - treat as non-block_end
                            found_idx = Some(pre_code_idx);
                        }
                        break; // Stop after first placeholder
                    }
                }
            }
            found_idx.unwrap_or(pre_code_idx)
        } else {
            // Has dedents - look forward for block_start placeholder
            let mut found_idx = None;
            for idx in pre_code_idx..post_code_idx {
                if idx < self.tokens.len() {
                    let tok = &self.tokens[idx];
                    if tok.is_type(&["placeholder"]) {
                        // Check if it's a block_start
                        if let Some(block_type) = tok.block_type.as_ref() {
                            if block_type == "block_start" {
                                found_idx = Some(idx);
                            } else {
                                // Found a placeholder but NOT block_start
                                // Python sets meta_idx = post_nc_idx in this case
                                found_idx = Some(post_code_idx);
                            }
                        } else {
                            // Placeholder with no block_type - treat as non-block_start
                            found_idx = Some(post_code_idx);
                        }
                        break; // Stop after first placeholder
                    }
                }
            }
            found_idx.unwrap_or(post_code_idx)
        };

        // Build list of (position, MetaSegment) tuples
        meta_buffer
            .into_iter()
            .map(|meta_segment| (meta_idx, meta_segment))
            .collect()
    }

    #[inline]
    fn calculate_sequence_child_start_position(
        &self,
        end_of_last_match_idx: usize,
        allow_gaps: bool,
        next_child_grammar_id: GrammarId,
        max_idx: usize,
    ) -> usize {
        let child_start_pos = if self.grammar_ctx.inst(next_child_grammar_id).variant
            != GrammarVariant::Meta
            && allow_gaps
        {
            // Skip to first code token for first non-meta element
            self.skip_start_index_forward_to_code(end_of_last_match_idx, max_idx)
        } else {
            end_of_last_match_idx
        };
        child_start_pos
    }

    /// Convert a Grammar ID for a Meta element to a MetaSegment enum variant
    #[inline]
    pub(crate) fn grammar_id_to_meta_segment(&self, grammar_id: GrammarId) -> Option<MetaSegment> {
        // Meta elements have their token_type stored in aux_data
        let inst = self.grammar_ctx.inst(grammar_id);
        let is_conditional = inst.flags.is_conditional();

        if is_conditional {
            // Conditional meta - check config to see if it should be included
            let (meta_type_str, config_key, expected_value) =
                self.grammar_ctx.conditional_config(grammar_id);
            let actual_value = self.indent_config.get(config_key).copied().unwrap_or(false);

            if actual_value == expected_value {
                match meta_type_str {
                    "indent" => Some(MetaSegment::Indent { is_implicit: false }),
                    "implicit_indent" => Some(MetaSegment::Indent { is_implicit: true }),
                    "dedent" => Some(MetaSegment::Dedent { is_implicit: false }),
                    _ => None,
                }
            } else {
                None // Config doesn't match - skip this meta
            }
        } else {
            // Non-conditional meta - always include based on meta_type
            // (which reads from aux_data_offsets for non-conditional metas)
            let s = self.grammar_ctx.meta_type(grammar_id);
            match s {
                "indent" => Some(MetaSegment::Indent { is_implicit: false }),
                "implicit_indent" => Some(MetaSegment::Indent { is_implicit: true }),
                "dedent" => Some(MetaSegment::Dedent { is_implicit: false }),
                _ => {
                    log::warn!("Unknown meta type: {}", s);
                    None
                }
            }
        }
    }
}
