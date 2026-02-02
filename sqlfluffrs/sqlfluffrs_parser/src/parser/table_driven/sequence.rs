use crate::vdebug;
use smallvec::SmallVec;
use sqlfluffrs_types::{GrammarId, ParseMode};
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
        parent_terminators: &[GrammarId],
        stack: &mut TableParseFrameStack,
    ) -> Result<TableFrameResult, ParseError> {
        self.pos = frame.pos;
        let start_idx = self.pos;
        let grammar_id = frame.grammar_id;
        let reset_terminators = self.grammar_ctx.inst(grammar_id).flags.reset_terminators();
        // Check for parse_mode_override first (Bracketed GREEDY mode inheritance)
        let parse_mode = frame
            .parse_mode_override
            .unwrap_or_else(|| self.grammar_ctx.inst(grammar_id).parse_mode);

        if frame.parse_mode_override.is_some() {
            vdebug!(
                "Sequence[table] Initial: Using parse_mode_override={:?} (native={:?})",
                parse_mode,
                self.grammar_ctx.inst(grammar_id).parse_mode
            );
        }

        let local_terminators = self.grammar_ctx.terminators(grammar_id).collect::<Vec<_>>();
        let elements = self.grammar_ctx.children(grammar_id).collect::<Vec<_>>();

        // combine parent and local terminators
        let all_terminators = self.combine_table_terminators(
            &local_terminators,
            parent_terminators,
            reset_terminators,
        );

        // calculate max_idx with terminator and parent constraints
        let max_idx = self.calculate_max_idx_table_driven(
            start_idx,
            &all_terminators,
            parse_mode,
            frame.parent_max_idx,
        )?;

        // Push a checkpoint for transparent token collection.
        // If this Sequence fails, we'll rollback to release collected positions.
        // If it succeeds, we'll commit to keep them marked.
        self.push_collection_checkpoint(frame.frame_id);

        // Store calculated max_idx in frame for cache consistency
        frame.calculated_max_idx = Some(max_idx);

        // Update frame with Sequence context
        frame.state = FrameState::WaitingForChild {
            child_index: 0,
            total_children: elements.len(),
        };
        frame.context = FrameContext::SequenceTableDriven {
            grammar_id,
            matched_idx: start_idx,
            max_idx,
            original_max_idx: max_idx, // Store original before any GREEDY_ONCE_STARTED trimming
            last_child_frame_id: None,
            current_element_idx: 0, // Start at first element
            first_match: true,      // For GREEDY_ONCE_STARTED trimming
            optional: self.grammar_ctx.inst(grammar_id).flags.optional(), // Store Sequence-level optional flag
            meta_buffer: Vec::new(), // Buffer for meta elements to flush
        };
        frame.table_terminators = SmallVec::from_vec(all_terminators);
        let current_frame_id = frame.frame_id; // Save before moving frame
        stack.push(&mut frame);

        // Don't skip whitespace here! Python's Sequence.match skips whitespace IN THE LOOP
        let first_child_pos = start_idx; // Start at the original position

        // Handle empty elements case - sequence with no elements should succeed immediately
        if elements.is_empty() {
            // Pop the frame we just pushed
            stack.pop();
            // Transition to Combining to finalize empty Sequence result
            frame.end_pos = Some(start_idx);
            frame.state = FrameState::Combining;
            stack.push(&mut frame);
            return Ok(TableFrameResult::Done);
        }

        if first_child_pos >= max_idx {
            stack.pop();

            if parse_mode == ParseMode::Strict {
                // Rollback checkpoint before returning Empty
                self.rollback_collection_checkpoint(current_frame_id);
                stack.insert_empty_result(current_frame_id, start_idx);
                return Ok(TableFrameResult::Done);
            }

            // In greedy modes, check if first element is optional
            if self.grammar_ctx.is_optional(elements[0]) {
                // Rollback checkpoint before returning Empty
                self.rollback_collection_checkpoint(current_frame_id);
                stack.insert_empty_result(current_frame_id, start_idx);
                return Ok(TableFrameResult::Done);
            } else {
                // If start_idx == max_idx, there are no tokens to wrap - return Empty
                // This happens when terminators are found immediately at the start position
                if start_idx >= max_idx {
                    vdebug!(
                        "Sequence[table]: GREEDY mode with no tokens to consume (start_idx={}, max_idx={}), returning Empty",
                        start_idx, max_idx
                    );
                    // Rollback checkpoint before returning Empty
                    self.rollback_collection_checkpoint(current_frame_id);
                    stack.insert_empty_result(current_frame_id, start_idx);
                    return Ok(TableFrameResult::Done);
                }

                // Wrap remaining content as an Unparsable segment (Python parity)
                let element_desc = format!("GrammarId({})", elements[0]);

                // Create segment_kwargs for the Unparsable segment
                let mut segment_kwargs = hashbrown::HashMap::new();
                segment_kwargs.insert("expected".to_string(), element_desc);

                // Create MatchResult with matched_class="UnparsableSegment" and segment_kwargs
                let unparsable_match = MatchResult {
                    matched_slice: start_idx..max_idx,
                    matched_class: Some("UnparsableSegment".to_string()),
                    segment_kwargs,
                    ..Default::default()
                };

                // Commit checkpoint since we're producing a result (even if unparsable)
                self.commit_collection_checkpoint(current_frame_id);
                stack.insert_result(current_frame_id, unparsable_match, max_idx);
                return Ok(TableFrameResult::Done);
            }
        }

        let mut child_idx = 0;
        while child_idx < elements.len() {
            if self.grammar_ctx.variant(elements[child_idx])
                == sqlfluffrs_types::GrammarVariant::Meta
            {
                // PYTHON PARITY: Buffer metas instead of inserting them directly!
                // In Python, metas are buffered and only flushed when the next
                // non-meta element successfully matches. This ensures that if a
                // Sequence like Sequence(Indent, Delimited(...), Dedent) fails at
                // the Delimited, the Indent is NOT included in the output.
                let meta_id = elements[child_idx];
                let inst = self.grammar_ctx.inst(meta_id);
                let is_conditional = inst.flags.is_conditional();

                // Determine if this meta should be added
                let should_add = if is_conditional {
                    // Conditional meta - check config to see if it should be included
                    let (_, config_key, expected_value) =
                        self.grammar_ctx.conditional_config(meta_id);
                    let actual_value = self.indent_config.get(config_key).copied().unwrap_or(false);
                    actual_value == expected_value
                } else {
                    true // Non-conditional metas are always added
                };

                if should_add {
                    // Add to meta_buffer - will be flushed on next successful match
                    if let Some(ref mut parent_frame) = stack.last_mut() {
                        if let FrameContext::SequenceTableDriven {
                            meta_buffer,
                            current_element_idx,
                            ..
                        } = &mut parent_frame.context
                        {
                            meta_buffer.push(meta_id);
                            *current_element_idx = child_idx + 1;
                        }
                        // Update state to next child
                        if let FrameState::WaitingForChild {
                            child_index,
                            total_children: _,
                        } = &mut parent_frame.state
                        {
                            *child_index = child_idx + 1;
                        }
                    }
                }
                child_idx += 1;
            } else {
                // Get max_idx from parent Sequence to pass to child
                let current_max_idx = if let Some(parent_frame) = stack.last_mut() {
                    if let FrameContext::SequenceTableDriven { max_idx, .. } = &parent_frame.context
                    {
                        Some(*max_idx)
                    } else {
                        None
                    }
                } else {
                    None
                };

                // Non-meta element - needs actual parsing
                vdebug!(
                    "DEBUG: Creating FIRST child at pos={}, max_idx={}",
                    first_child_pos,
                    max_idx
                );

                let child_frame = TableParseFrame {
                    frame_id: stack.frame_id_counter,
                    grammar_id: elements[child_idx],
                    pos: first_child_pos, // Use position after skipping to code!
                    table_terminators: stack
                        .last_mut()
                        .map(|f| f.table_terminators.clone())
                        .unwrap_or_default(),
                    state: FrameState::Initial,
                    accumulated: smallvec::SmallVec::new(),
                    context: FrameContext::None,
                    parent_max_idx: current_max_idx, // Pass Sequence's max_idx to child!
                    calculated_max_idx: None,        // Will be set by child's handler
                    end_pos: None,
                    transparent_positions: None,
                    element_key: None,
                    parse_mode_override: frame.parse_mode_override, // Propagate override to children
                };

                // Update parent (already on stack) and push child
                TableParseFrame::update_sequence_parent_and_push_child(
                    stack,
                    child_frame,
                    child_idx,
                );
                return Ok(TableFrameResult::Done);
            }
        }

        Ok(TableFrameResult::Done)
    }

    /// Handle Sequence grammar Waiting for child state
    /// child_match - the MatchResult from the child parse
    /// child_end_pos,
    /// child_element_key,
    /// stack,
    pub(crate) fn handle_sequence_table_driven_waiting_for_child(
        &mut self,
        mut frame: TableParseFrame,
        child_match: &MatchResult,
        child_end_pos: &usize,
        stack: &mut TableParseFrameStack,
    ) -> Result<TableFrameResult, ParseError> {
        // Extract grammar id and instance for table-driven logic
        let grammar_id = match &frame.context {
            FrameContext::SequenceTableDriven { grammar_id, .. } => *grammar_id,
            _ => unreachable!("Expected SequenceTableDriven context"),
        };

        // Check for parse_mode_override first (Bracketed GREEDY mode inheritance)
        let parse_mode = frame
            .parse_mode_override
            .unwrap_or_else(|| self.grammar_ctx.inst(grammar_id).parse_mode);
        let allow_gaps = self.grammar_ctx.inst(grammar_id).flags.allow_gaps();
        let all_children: Vec<GrammarId> = self.grammar_ctx.children(grammar_id).collect();

        // Read current index and first_match for logging (immutable borrow)
        let (current_element_idx_val, _first_match_val) = match &frame.context {
            FrameContext::SequenceTableDriven {
                current_element_idx,
                first_match,
                ..
            } => (*current_element_idx, *first_match),
            _ => unreachable!("Expected SequenceTableDriven context"),
        };

        vdebug!(
            "Sequence[table] WaitingForChild: frame_id={}, child_empty={}, child_end_pos={}, current_idx={}/{}, first_match={}",
            frame.frame_id,
            child_match.is_empty(),
            child_end_pos,
            current_element_idx_val,
            all_children.len(),
            _first_match_val
        );

        // Child matched - PYTHON PARITY: Flush any pending meta_buffer BEFORE adding this match
        // This matches Python's _flush_metas which happens at line 312 in sequence.py:
        // "Flush any metas..." RIGHT BEFORE "Otherwise we _do_ have a match. Update the position."
        if !child_match.is_empty() {
            // First, extract and flush any pending metas from previous iteration
            let (matched_idx_for_flush, max_idx_val) = match &frame.context {
                FrameContext::SequenceTableDriven {
                    matched_idx,
                    max_idx,
                    ..
                } => (*matched_idx, *max_idx),
                _ => unreachable!("Expected SequenceTableDriven context"),
            };

            // Flush pending meta_buffer BEFORE adding the new child match
            let pending_metas = match &mut frame.context {
                FrameContext::SequenceTableDriven { meta_buffer, .. } => {
                    std::mem::take(meta_buffer)
                }
                _ => Vec::new(),
            };

            if !pending_metas.is_empty() {
                // Calculate the whitespace boundary for flushing
                let pre_code_idx = matched_idx_for_flush;
                let post_code_idx = if allow_gaps {
                    self.skip_start_index_forward_to_code(pre_code_idx, max_idx_val)
                } else {
                    pre_code_idx
                };
                self.flush_meta_buffer(
                    &mut frame.accumulated,
                    pre_code_idx,
                    post_code_idx,
                    pending_metas,
                );
            }

            // NOW add the matched child to accumulated
            frame.accumulated.push(Arc::new(child_match.clone()));

            if let FrameContext::SequenceTableDriven {
                matched_idx,
                max_idx,
                current_element_idx,
                first_match,
                original_max_idx,
                ..
            } = &mut frame.context
            {
                *matched_idx = *child_end_pos;
                *current_element_idx += 1;

                // If child consumed past current max_idx, update max_idx to allow
                // transparent token collection and subsequent children to continue
                // from the correct position. This handles cases where a child
                // (like Bracketed/Delimited) legitimately consumed past the
                // terminator-based max_idx constraint (e.g., TRIM(BOTH FROM 'x')
                // where FROM inside brackets isn't a terminator).
                if *matched_idx > *max_idx {
                    vdebug!(
                        "Sequence[table]: Child consumed past max_idx ({}->{}), updating max_idx to matched_idx",
                        *max_idx, *matched_idx
                    );
                    *max_idx = *matched_idx;
                }

                if *first_match && parse_mode == ParseMode::GreedyOnceStarted {
                    *first_match = false;
                    // Use element-aware trimming so we don't treat terminators that are
                    // actually the start of upcoming elements (e.g., FROM) as terminators.
                    let remaining_children: Vec<GrammarId> = all_children
                        .iter()
                        .skip(*current_element_idx)
                        .cloned()
                        .collect();

                    #[cfg(feature = "verbose-debug")]
                    let grammar_name = self.grammar_ctx.grammar_id_name(grammar_id);
                    vdebug!(
                        "Sequence[table]: About to trim at matched_idx={}, grammar='{}', grammar_id={}, parse_mode={:?}, terminators.len()={}, remaining_children.len()={}",
                        *matched_idx,
                        grammar_name,
                        grammar_id.0,
                        parse_mode,
                        frame.table_terminators.len(),
                        remaining_children.len()
                    );

                    let new_max_idx = self.trim_to_terminator_with_elements_table_driven(
                        *matched_idx,
                        &frame.table_terminators,
                        &remaining_children,
                    )?;
                    // Respect original parent max constraint
                    *max_idx = new_max_idx.min(*original_max_idx);
                    vdebug!(
                        "Sequence[table]: Trimmed max_idx from {} to {}",
                        new_max_idx,
                        *max_idx
                    );
                }
            }

            // PYTHON-STYLE META HANDLING: Buffer trailing META children after this match
            // They will be flushed BEFORE the next successful child match (or at end of sequence)
            // Store in frame's meta_buffer, NOT a local variable
            if let FrameContext::SequenceTableDriven {
                current_element_idx,
                meta_buffer,
                ..
            } = &mut frame.context
            {
                while *current_element_idx < all_children.len() {
                    let child_id = all_children[*current_element_idx];
                    if self.grammar_ctx.variant(child_id) == sqlfluffrs_types::GrammarVariant::Meta
                    {
                        meta_buffer.push(child_id);
                        *current_element_idx += 1;
                    } else {
                        break;
                    }
                }
            }

            let (matched_idx_val, max_idx_val) = match &frame.context {
                FrameContext::SequenceTableDriven {
                    matched_idx,
                    max_idx,
                    ..
                } => (*matched_idx, *max_idx),
                _ => unreachable!("Expected SequenceTableDriven context"),
            };

            // PYTHON PARITY: Loop to skip optional elements when we've run out of segments.
            // When max_idx is trimmed (GREEDY_ONCE_STARTED), we must skip all optional elements
            // and only stop at a required element or when all elements are processed.
            // We use a loop here to avoid re-entering this function with stale child results.
            loop {
                // Re-read current_element_idx each iteration since we modify it
                let current_idx = match &frame.context {
                    FrameContext::SequenceTableDriven {
                        current_element_idx,
                        ..
                    } => *current_element_idx,
                    _ => unreachable!(),
                };

                if current_idx >= all_children.len() {
                    // All children processed - go to combining
                    let pending_metas = match &mut frame.context {
                        FrameContext::SequenceTableDriven { meta_buffer, .. } => {
                            std::mem::take(meta_buffer)
                        }
                        _ => Vec::new(),
                    };
                    if !pending_metas.is_empty() {
                        self.flush_meta_buffer(
                            &mut frame.accumulated,
                            matched_idx_val,
                            matched_idx_val,
                            pending_metas,
                        );
                    }
                    self.pos = matched_idx_val;
                    frame.end_pos = Some(matched_idx_val);
                    frame.state = FrameState::Combining;
                    stack.push(&mut frame);
                    return Ok(TableFrameResult::Done);
                }

                // Move parser position to where the child ended
                self.pos = matched_idx_val;

                // When gaps are allowed, skip forward to find the next code token.
                let next_start_pos = if allow_gaps {
                    self.skip_start_index_forward_to_code(matched_idx_val, max_idx_val)
                } else {
                    matched_idx_val
                };

                let next_child = all_children[current_idx];
                let next_child_optional = self.grammar_ctx.is_optional(next_child);

                // PYTHON PARITY: Check if we've run out of segments BEFORE trying to match.
                // This corresponds to Python's check at line 199:
                //   if _idx >= max_idx:
                if next_start_pos >= max_idx_val {
                    // If the next element is optional, skip it and continue the loop
                    if next_child_optional {
                        if let FrameContext::SequenceTableDriven {
                            current_element_idx,
                            meta_buffer,
                            ..
                        } = &mut frame.context
                        {
                            *current_element_idx += 1;
                            // Also buffer any consecutive Meta elements after this skip
                            while *current_element_idx < all_children.len() {
                                let child_id = all_children[*current_element_idx];
                                if self.grammar_ctx.variant(child_id)
                                    == sqlfluffrs_types::GrammarVariant::Meta
                                {
                                    meta_buffer.push(child_id);
                                    *current_element_idx += 1;
                                } else {
                                    break;
                                }
                            }
                        }
                        // Loop continues to check the next element
                        continue;
                    }

                    // Required element but no segments left - handle "ran out of segments" case
                    let start_idx = frame.pos;

                    // STRICT or nothing matched yet: return Empty
                    if parse_mode == ParseMode::Strict || matched_idx_val == start_idx {
                        vdebug!(
                            "Sequence[table]: Ran out of segments at idx {}, mode={:?}, matched_idx={}, start_idx={} - returning Empty",
                            next_start_pos, parse_mode, matched_idx_val, start_idx
                        );
                        self.pos = start_idx;
                        self.rollback_collection_checkpoint(frame.frame_id);
                        stack.insert_empty_result(frame.frame_id, start_idx);
                        return Ok(TableFrameResult::Done);
                    }

                    // GREEDY modes with partial match: wrap existing matches as UnparsableSegment
                    vdebug!(
                        "Sequence[table]: Ran out of segments at idx {} in {:?} mode (matched_idx={}, start_idx={}) - wrapping as UnparsableSegment",
                        next_start_pos, parse_mode, matched_idx_val, start_idx
                    );

                    // Flush any pending metas first
                    let pending_metas = match &mut frame.context {
                        FrameContext::SequenceTableDriven { meta_buffer, .. } => {
                            std::mem::take(meta_buffer)
                        }
                        _ => Vec::new(),
                    };
                    if !pending_metas.is_empty() {
                        self.flush_meta_buffer(
                            &mut frame.accumulated,
                            matched_idx_val,
                            matched_idx_val,
                            pending_metas,
                        );
                    }

                    // Build expected message in Python-compatible format
                    // Python format: f"{elem} after {segments[matched_idx - 1]}. Found nothing."
                    // Where elem is the grammar repr and segments[matched_idx - 1] is the segment repr
                    let next_elem_repr = self.grammar_ctx.grammar_repr(next_child);
                    let prev_segment_repr =
                        if matched_idx_val > 0 && matched_idx_val - 1 < self.tokens.len() {
                            let tok = &self.tokens[matched_idx_val - 1];
                            // Format like Python's segment repr: <ClassName: (pos_marker) 'raw'>
                            // Map token_type to Python class name format (e.g., "word" -> "WordSegment")
                            let type_name = tok.get_type();
                            let class_name = format!(
                                "{}Segment",
                                type_name
                                    .chars()
                                    .next()
                                    .map(|c| c.to_uppercase().collect::<String>())
                                    .unwrap_or_default()
                                    + &type_name.chars().skip(1).collect::<String>()
                            );
                            let pos = tok
                                .pos_marker
                                .as_ref()
                                .map(|p| p.to_string())
                                .unwrap_or_else(|| "unknown".to_string());
                            format!("<{}: ({}) '{}'>", class_name, pos, tok.raw())
                        } else {
                            "nothing".to_string()
                        };
                    let expected_msg = format!(
                        "{} after {}. Found nothing.",
                        next_elem_repr, prev_segment_repr
                    );

                    // Create result with matched portion wrapped as UnparsableSegment
                    let mut segment_kwargs = hashbrown::HashMap::new();
                    segment_kwargs.insert("expected".to_string(), expected_msg);

                    let result = MatchResult {
                        matched_slice: start_idx..matched_idx_val,
                        matched_class: Some("UnparsableSegment".to_string()),
                        child_matches: frame.accumulated.to_vec(),
                        segment_kwargs,
                        ..Default::default()
                    };

                    self.pos = matched_idx_val;
                    self.commit_collection_checkpoint(frame.frame_id);
                    stack.insert_result(frame.frame_id, result, matched_idx_val);
                    return Ok(TableFrameResult::Done);
                }

                // We have segments left and a next child to match - create a child frame
                let child_parent_max = Some(max_idx_val);

                if next_start_pos < self.tokens.len() {
                    #[cfg(feature = "verbose-debug")]
                    let tok = &self.tokens[next_start_pos];
                    vdebug!(
                        "Sequence[table] about to push child {} at pos {} (token='{}', type='{}')",
                        next_child,
                        next_start_pos,
                        tok.raw(),
                        tok.get_type()
                    );
                } else {
                    vdebug!(
                        "Sequence[table] about to push child {} at pos {} (EOF)",
                        next_child,
                        next_start_pos
                    );
                }

                let child_frame = TableParseFrame::new_child(
                    stack.frame_id_counter,
                    next_child,
                    next_start_pos,
                    frame.table_terminators.to_vec(),
                    child_parent_max,
                );

                frame.state = FrameState::WaitingForChild {
                    child_index: current_idx,
                    total_children: all_children.len(),
                };

                TableParseFrame::push_sequence_child_and_update_parent(
                    stack,
                    &mut frame,
                    child_frame,
                    current_idx,
                );
                return Ok(TableFrameResult::Done);
            }
            // This point is unreachable due to the loop always returning
        }

        // Child failed (Empty)
        let failed_idx = current_element_idx_val;
        let failed_child = all_children[failed_idx];
        let failed_inst = self.grammar_ctx.inst(failed_child);

        // REMOVED: The "TABLE FIX" that was resetting position based on element_start.
        // After fixing Ref (and other grammars) to properly set end_pos when returning Empty,
        // we should trust the child's end_pos directly. The child is responsible for ensuring
        // that if it returns Empty, its end_pos reflects where parsing should continue from
        // (typically the position it started at, before any speculative token collection).

        // Simply use the child_end_pos as reported by the child
        let corrected_child_end_pos = *child_end_pos;

        if self.pos != corrected_child_end_pos {
            vdebug!(
                "[SEQUENCE] Adjusting self.pos from {} to child_end_pos {}",
                self.pos,
                corrected_child_end_pos
            );
            self.pos = corrected_child_end_pos;
        }

        if failed_inst.flags.optional() {
            let mut next_index = failed_idx + 1;

            // PYTHON-STYLE META HANDLING: Buffer trailing META children after optional skip
            // Store in frame's meta_buffer, NOT a local variable - they will be flushed
            // BEFORE the next successful child match or at end of sequence
            if let FrameContext::SequenceTableDriven {
                meta_buffer,
                current_element_idx,
                ..
            } = &mut frame.context
            {
                while next_index < all_children.len() {
                    let child_id = all_children[next_index];
                    if self.grammar_ctx.variant(child_id) == sqlfluffrs_types::GrammarVariant::Meta
                    {
                        meta_buffer.push(child_id);
                        next_index += 1;
                    } else {
                        // Non-META child - stop skipping
                        break;
                    }
                }
                // Update current_element_idx to reflect the metas we've buffered
                *current_element_idx = next_index;
            }

            if next_index < all_children.len() {
                // Determine a sensible start position for the next child.
                // Use the sequence's matched_idx (last successful match) as the base
                // so we don't accidentally start at an earlier frame.pos that doesn't
                // reflect the position after previous successful children.
                let (base_matched_idx, base_max_idx) = match &frame.context {
                    FrameContext::SequenceTableDriven {
                        matched_idx,
                        max_idx,
                        ..
                    } => (*matched_idx, *max_idx),
                    _ => (frame.pos, frame.pos),
                };

                // Respect allow_gaps: if allowed, advance to next code token.
                // We DON'T explicitly collect transparent tokens here because they'll
                // be captured implicitly as "trailing segments" by apply() when
                // processing the matched_slice.
                let next_start_pos = if allow_gaps {
                    self.skip_start_index_forward_to_code(base_matched_idx, base_max_idx)
                } else {
                    base_matched_idx
                };

                // NOTE: Do NOT flush meta_buffer here! Metas will be flushed BEFORE
                // the next successful match or at the end of the sequence.

                let next_child = all_children[next_index];
                let child_frame = TableParseFrame::new_child(
                    stack.frame_id_counter,
                    next_child,
                    next_start_pos,
                    frame.table_terminators.to_vec(),
                    match &frame.context {
                        FrameContext::SequenceTableDriven { max_idx, .. } => Some(*max_idx),
                        _ => None,
                    },
                );

                frame.state = FrameState::WaitingForChild {
                    child_index: next_index,
                    total_children: all_children.len(),
                };

                TableParseFrame::push_sequence_child_and_update_parent(
                    stack,
                    &mut frame,
                    child_frame,
                    next_index,
                );

                Ok(TableFrameResult::Done)
            } else {
                // Child failure at end of sequence - flush any remaining buffered metas from frame
                // Use matched_idx from frame context as the position (not frame.pos which is the start)
                let (end_matched_idx, pending_metas) = match &mut frame.context {
                    FrameContext::SequenceTableDriven {
                        matched_idx,
                        meta_buffer,
                        ..
                    } => (*matched_idx, std::mem::take(meta_buffer)),
                    _ => (frame.pos, Vec::new()),
                };
                if !pending_metas.is_empty() {
                    self.flush_meta_buffer(
                        &mut frame.accumulated,
                        end_matched_idx,
                        end_matched_idx,
                        pending_metas,
                    );
                }

                // ensure parser position is restored to the sequence's starting position
                // before completing with Empty.
                self.pos = frame.pos;
                frame.end_pos = Some(frame.pos);
                frame.state = FrameState::Combining;
                stack.push(&mut frame);
                Ok(TableFrameResult::Done)
            }
        } else {
            // Required child failed: behavior depends on parse_mode (Python parity)
            let start_idx = frame.pos;
            let (matched_idx, max_idx) = match &frame.context {
                FrameContext::SequenceTableDriven {
                    matched_idx,
                    max_idx,
                    ..
                } => (*matched_idx, *max_idx),
                _ => (start_idx, start_idx),
            };

            // 1. In STRICT mode, failing to match required element means no match
            if parse_mode == ParseMode::Strict {
                vdebug!(
                    "Sequence[table]: Required element {} returned Empty in STRICT mode - Sequence fails completely",
                    failed_idx
                );
                self.pos = start_idx;
                self.rollback_collection_checkpoint(frame.frame_id);
                stack.insert_empty_result(frame.frame_id, start_idx);
                return Ok(TableFrameResult::Done);
            }

            // 2. In GREEDY_ONCE_STARTED, if nothing matched yet, no match
            if parse_mode == ParseMode::GreedyOnceStarted && matched_idx == start_idx {
                vdebug!(
                    "Sequence[table]: Required element {} returned Empty in GREEDY_ONCE_STARTED but nothing matched yet - Sequence fails completely",
                    failed_idx
                );
                self.pos = start_idx;
                self.rollback_collection_checkpoint(frame.frame_id);
                stack.insert_empty_result(frame.frame_id, start_idx);
                return Ok(TableFrameResult::Done);
            }

            // 3. For GREEDY modes with partial match OR GREEDY mode without match:
            //    Return result with UnparsableSegment
            vdebug!(
                "Sequence[table]: Required element {} returned Empty in {:?} mode (matched_idx={}, start_idx={}, max_idx={}) - creating UnparsableSegment",
                failed_idx, parse_mode, matched_idx, start_idx, max_idx
            );

            // Build expected message like Python does
            let failed_elem_name = self.grammar_ctx.grammar_id_name(failed_child);
            let expected_msg = if matched_idx == start_idx {
                // Nothing matched yet - use "to start sequence" message
                let token_at_idx = if corrected_child_end_pos < self.tokens.len() {
                    format!("{}", self.tokens[corrected_child_end_pos].raw())
                } else {
                    "EOF".to_string()
                };
                format!(
                    "{} to start sequence. Found {}",
                    failed_elem_name, token_at_idx
                )
            } else {
                // Partial match - use "after X. Found Y" message
                let prev_token = if matched_idx > 0 && matched_idx - 1 < self.tokens.len() {
                    format!("{}", self.tokens[matched_idx - 1].raw())
                } else {
                    "nothing".to_string()
                };
                let token_at_idx = if corrected_child_end_pos < self.tokens.len() {
                    format!("{}", self.tokens[corrected_child_end_pos].raw())
                } else {
                    "nothing".to_string()
                };
                format!(
                    "{} after {}. Found {}",
                    failed_elem_name, prev_token, token_at_idx
                )
            };

            let mut segment_kwargs = hashbrown::HashMap::new();
            segment_kwargs.insert("expected".to_string(), expected_msg);

            if matched_idx == start_idx {
                // Case 3a: GREEDY mode, nothing matched - wrap everything as UnparsableSegment
                let unparsable_match = MatchResult {
                    matched_slice: start_idx..max_idx,
                    matched_class: Some("UnparsableSegment".to_string()),
                    segment_kwargs,
                    ..Default::default()
                };

                self.pos = max_idx;
                self.commit_collection_checkpoint(frame.frame_id);
                stack.insert_result(frame.frame_id, unparsable_match, max_idx);
            } else {
                // Case 3b: Partial match - return accumulated matches + remaining as UnparsableSegment child
                // Find where unparsable section starts (skip whitespace forward)
                let allow_gaps = self.grammar_ctx.inst(grammar_id).flags.allow_gaps();
                let unparsable_start = if allow_gaps {
                    self.skip_start_index_forward_to_code(matched_idx, max_idx)
                } else {
                    matched_idx
                };

                // PYTHON PARITY: Do NOT flush meta_buffer here!
                // In Python, metas are only flushed after a SUCCESSFUL match.
                // When a required child fails in a partial match, the pending metas
                // (e.g., Indent before Delimited) should NOT be included in the output.
                // They are simply discarded.

                // Only create UnparsableSegment child if there's actually content to wrap
                if unparsable_start < max_idx {
                    // Create UnparsableSegment child for the remaining unmatched portion
                    let unparsable_child = MatchResult {
                        matched_slice: unparsable_start..max_idx,
                        matched_class: Some("UnparsableSegment".to_string()),
                        segment_kwargs,
                        ..Default::default()
                    };

                    // Add the unparsable child to accumulated matches
                    frame.accumulated.push(Arc::new(unparsable_child));
                }

                // Build result with all child_matches
                let result = MatchResult {
                    matched_slice: start_idx..max_idx,
                    child_matches: frame.accumulated.to_vec(),
                    ..Default::default()
                };

                self.pos = max_idx;
                self.commit_collection_checkpoint(frame.frame_id);
                stack.insert_result(frame.frame_id, result, max_idx);
            }

            Ok(TableFrameResult::Done)
        }
    }

    /// Handle Sequence Combining state using table-driven approach
    pub(crate) fn handle_sequence_table_driven_combining(
        &mut self,
        mut frame: TableParseFrame,
        _stack: &mut TableParseFrameStack,
    ) -> Result<TableFrameResult, ParseError> {
        let FrameContext::SequenceTableDriven {
            grammar_id,
            matched_idx,
            max_idx,
            ..
        } = &frame.context
        else {
            return Err(ParseError::new(
                "Expected SequenceTableDriven context in combining".to_string(),
            ));
        };

        // Copy values before mutable borrow
        let grammar_id = *grammar_id;
        let matched_idx = *matched_idx;
        let max_idx = *max_idx;

        // Get parse_mode from grammar
        let inst = self.grammar_ctx.inst(grammar_id);
        let parse_mode = inst.parse_mode;

        vdebug!(
            "Sequence[table] Combining: frame_id={}, accumulated={}, matched_idx={}, max_idx={}, parse_mode={:?}",
            frame.frame_id,
            frame.accumulated.len(),
            matched_idx,
            max_idx,
            parse_mode
        );
        #[cfg(feature = "verbose-debug")]
        for (i, child) in frame.accumulated.iter().enumerate() {
            vdebug!("  Combining accumulated[{}]: {:?}", i, child);
        }

        let (result_match, final_pos) = if frame.accumulated.is_empty() {
            // Empty result - rollback collected positions
            self.rollback_collection_checkpoint(frame.frame_id);
            (Arc::new(MatchResult::empty_at(frame.pos)), frame.pos)
        } else {
            // Successful match - commit collected positions
            self.commit_collection_checkpoint(frame.frame_id);

            let mut accumulated = std::mem::take(&mut frame.accumulated);
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

                    accumulated.push(Arc::new(MatchResult {
                        matched_slice: _idx.._stop_idx,
                        matched_class: Some("UnparsableSegment".to_string()),
                        segment_kwargs,
                        ..Default::default()
                    }));

                    // Match up to the end
                    final_matched_idx = _stop_idx;
                }
            }

            (
                Arc::new(MatchResult::sequence(
                    frame.pos,
                    final_matched_idx,
                    accumulated.into_vec(),
                )),
                final_matched_idx,
            )
        };

        self.pos = final_pos;
        frame.end_pos = Some(final_pos);
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
    pub(crate) fn flush_meta_buffer(
        &self,
        accumulated: &mut SmallVec<[Arc<MatchResult>; 2]>,
        pre_code_idx: usize,
        post_code_idx: usize,
        meta_buffer: Vec<GrammarId>,
    ) {
        // PYTHON PARITY: Check if ALL metas have positive indent values
        // If all positive → position at pre_code_idx (before whitespace)
        // If any negative → position at post_code_idx (after whitespace)

        // First pass: collect metas and check their signs
        let mut meta_types = Vec::new();
        let mut all_positive = true;

        for meta_id in &meta_buffer {
            // Check if this is a conditional meta
            let inst = self.grammar_ctx.inst(*meta_id);
            let is_conditional = inst.flags.is_conditional();

            let meta_type_opt: Option<(crate::parser::MetaSegmentType, bool)> = if is_conditional {
                // Conditional meta - check config to see if it should be included
                let (meta_type_str, config_key, expected_value) =
                    self.grammar_ctx.conditional_config(*meta_id);
                let actual_value = self.indent_config.get(config_key).copied().unwrap_or(false);

                if actual_value == expected_value {
                    match meta_type_str {
                        "indent" => Some((crate::parser::MetaSegmentType::Indent, false)),
                        "implicit_indent" => Some((crate::parser::MetaSegmentType::Indent, true)),
                        "dedent" => Some((crate::parser::MetaSegmentType::Dedent, false)),
                        _ => None,
                    }
                } else {
                    None // Config doesn't match - skip this meta
                }
            } else {
                // Non-conditional meta - always include based on meta_type
                // (which reads from aux_data_offsets for non-conditional metas)
                let s = self.grammar_ctx.meta_type(*meta_id);
                match s {
                    "indent" => Some((crate::parser::MetaSegmentType::Indent, false)),
                    "implicit_indent" => Some((crate::parser::MetaSegmentType::Indent, true)),
                    "dedent" => Some((crate::parser::MetaSegmentType::Dedent, false)),
                    _ => {
                        log::warn!("Unknown meta type: {}", s);
                        None
                    }
                }
            };

            if let Some((meta_type, is_implicit)) = meta_type_opt {
                // Check if it's a dedent (negative)
                if matches!(meta_type, crate::parser::MetaSegmentType::Dedent) {
                    all_positive = false;
                }
                meta_types.push((meta_type, is_implicit));
            }
        }

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

        // Insert metas at the determined position
        if all_positive {
            // All indents - search backward past trailing whitespace in accumulated
            let mut insert_pos = accumulated.len();
            while insert_pos > 0 {
                let prev_match = &accumulated[insert_pos - 1];
                let is_whitespace = if !prev_match.matched_slice.is_empty() {
                    let token_idx = prev_match.matched_slice.start;
                    if token_idx < self.tokens.len() {
                        let tok_type = self.tokens[token_idx].get_type();
                        tok_type == "whitespace" || tok_type == "newline"
                    } else {
                        false
                    }
                } else {
                    false
                };
                if is_whitespace {
                    insert_pos -= 1;
                } else {
                    break;
                }
            }

            // Insert all metas at this position
            for (meta_type, is_implicit) in meta_types {
                accumulated.insert(
                    insert_pos,
                    Arc::new(MatchResult {
                        matched_slice: meta_idx..meta_idx,
                        insert_segments: vec![(meta_idx, meta_type, is_implicit)],
                        ..Default::default()
                    }),
                );
            }
        } else {
            // Has dedents - append at end
            for (meta_type, is_implicit) in meta_types {
                accumulated.push(Arc::new(MatchResult {
                    matched_slice: meta_idx..meta_idx,
                    insert_segments: vec![(meta_idx, meta_type, is_implicit)],
                    ..Default::default()
                }));
            }
        }
    }
}
