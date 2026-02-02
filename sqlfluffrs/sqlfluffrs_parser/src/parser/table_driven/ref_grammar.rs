use sqlfluffrs_types::GrammarId;
use std::sync::Arc;

use crate::parser::{
    match_result::{MatchedClass, SegmentKwargs},
    table_driven::frame::{TableFrameResult, TableParseFrame, TableParseFrameStack},
    FrameContext, FrameState, MatchResult, ParseError, Parser,
};

impl Parser<'_> {
    // ========================================================================
    // Table-Driven Ref Handlers
    // ========================================================================

    /// Handle Ref Initial state using table-driven approach
    pub(crate) fn handle_ref_table_driven_initial(
        &mut self,
        grammar_id: GrammarId,
        mut frame: TableParseFrame,
        parent_terminators: &[GrammarId],
        stack: &mut TableParseFrameStack,
    ) -> Result<TableFrameResult, ParseError> {
        let reset_terminators = self.grammar_ctx.inst(grammar_id).flags.reset_terminators();
        let start_pos = frame.pos;

        // Get rule name via GrammarContext helper which knows how names are
        // stored in aux_data (generator packs ref names into aux_data).
        let rule_name = self.grammar_ctx.ref_name(grammar_id).to_string();

        log::debug!(
            "Ref[table] Initial: frame_id={}, pos={}, grammar_id={}, rule={}",
            frame.frame_id,
            start_pos,
            grammar_id.0,
            rule_name
        );

        // Python parity: If parent's max_idx is set and we're beyond it,
        // return Empty rather than error so parents (OneOf etc.) can try
        // other options. This matches the Python Ref behavior.
        if let Some(parent_max) = frame.parent_max_idx {
            if start_pos >= parent_max {
                log::debug!(
                    "Ref[table]: pos {} >= parent_max_idx {}, returning Empty",
                    frame.pos,
                    parent_max
                );
                return Ok(stack.complete_frame_empty(&frame));
            }
        }

        // Check exclude grammar first (table-driven exclude id if present).
        let exclude_id_opt = self.grammar_ctx.exclude(grammar_id);
        if let Some(exclude_id) = exclude_id_opt {
            self.pos = start_pos;
            if let Ok(exclude_node) = self.parse_table_iterative(exclude_id, parent_terminators) {
                self.pos = start_pos;
                if !exclude_node.is_empty() {
                    log::debug!(
                        "Ref[table]: exclude grammar matched at pos {}, returning Empty",
                        frame.pos
                    );
                    return Ok(stack.complete_frame_empty(&frame));
                }
            }
            log::debug!("Ref[table]: exclude grammar did not match, continuing");
        }

        self.pos = start_pos;

        // Get element children (excludes the exclude grammar if present).
        // For a Ref with only an exclude (no explicit match_grammar child), this will be empty.
        let element_children: Vec<GrammarId> =
            self.grammar_ctx.element_children(grammar_id).collect();

        // Use first element child if present, otherwise resolve by name via dialect mapping.
        // CRITICAL: For Ref grammars with an exclude, the `children` list contains ONLY the
        // exclude grammar. The actual referenced segment must be resolved by name.
        let child_grammar_id = if !element_children.is_empty() {
            element_children[0]
        } else {
            match self.dialect.get_segment_grammar(&rule_name) {
                Some(root) => root.grammar_id,
                None => {
                    log::debug!(
                        "Ref[table]: No element children and no dialect mapping for '{}', returning Empty",
                        rule_name
                    );
                    return Ok(stack.complete_frame_empty(&frame));
                }
            }
        };

        // If the explicit child grammar allows gaps, collect leading transparent
        // tokens so child parsing starts at the next non-transparent token.
        let child_allows_gaps = self.grammar_ctx.inst(child_grammar_id).flags.allow_gaps();
        let child_type = self.grammar_ctx.get_type(child_grammar_id);
        let child_start_pos = if child_allows_gaps {
            self.skip_start_index_forward_to_code(start_pos, self.tokens.len())
        } else {
            start_pos
        };

        // Determine the segment_class (Python class name) from tables
        // This is what gets stored in matched_class for Python lookup
        // e.g., "ProcedureDefinitionGrammar", "SelectStatementSegment", etc.
        let table_segment_class = self
            .grammar_ctx
            .segment_class(grammar_id)
            .map(|s| s.to_string());

        // eprintln!("Ref[table]: child_type={:?}, table_segment_class={:?}", child_type, table_segment_class);

        log::debug!(
            "Ref[table]: rule_name='{}', table_segment_class={:?}",
            rule_name,
            table_segment_class
        );

        // Store context with collected leading transparent tokens
        frame.context = FrameContext::RefTableDriven {
            grammar_id,
            name: rule_name,
            segment_class_name: table_segment_class,
            segment_type: child_type,
            saved_pos: child_start_pos,
            last_child_frame_id: Some(stack.frame_id_counter),
            child_grammar_id,
        };

        // CRITICAL: Set parent frame state to WaitingForChild so it will
        // retrieve the child result on the next iteration
        frame.state = FrameState::WaitingForChild { child_index: 0 };

        // Combine the Ref's local terminators with the parent terminators so
        // the referenced child parsing respects both sets (parity with Arc path)
        let local_terminators: Vec<GrammarId> = self.grammar_ctx.terminators(grammar_id).collect();
        let child_terminators = Self::combine_terminators_table_driven(
            &local_terminators,
            parent_terminators,
            reset_terminators,
        );

        let child_frame = TableParseFrame::new_child(
            stack.frame_id_counter,
            child_grammar_id,
            child_start_pos,
            child_terminators,
            frame.parent_max_idx,
        );

        log::debug!(
            "Ref[table]: Parsing explicit child grammar_id={} (parent_frame_id={}, child_frame_id={}, start_pos={})",
            child_grammar_id.0,
            frame.frame_id,
            stack.frame_id_counter,
            child_start_pos
        );

        Ok(stack.push_child_and_wait(&mut frame, child_frame, 0))
    }

    /// Handle Ref WaitingForChild state using table-driven approach
    pub(crate) fn handle_ref_table_driven_waiting_for_child(
        &mut self,
        mut frame: TableParseFrame,
        child_match: &MatchResult,
        child_end_pos: &usize,
    ) -> Result<TableFrameResult, ParseError> {
        let FrameContext::RefTableDriven { saved_pos, .. } = &frame.context else {
            unreachable!("Expected RefTableDriven context");
        };
        let original_pos = *saved_pos;

        log::debug!(
            "Ref[table] WaitingForChild: frame_id={}, child_empty={}, child_end_pos={}",
            frame.frame_id,
            child_match.is_empty(),
            child_end_pos
        );

        // Store child result and transition to Combining
        if !child_match.is_empty() {
            log::debug!(
                "Ref[table]: frame_id={} child matched, accumulated_before={}, setting pos to {}",
                frame.frame_id,
                frame.accumulated_matches.len(),
                child_end_pos
            );
            frame.accumulated_matches.push(Arc::new(child_match.clone()));
            self.pos = *child_end_pos;
            frame.end_pos = Some(*child_end_pos);
        } else {
            log::debug!(
                "Ref[table]: frame_id={} child was Empty, reverting pos {} -> {} and setting end_pos to {} (original_pos)",
                frame.frame_id,
                self.pos,
                original_pos,
                original_pos
            );
            // CRITICAL: Revert parser position when child returns Empty.
            // The Ref may have collected leading transparent tokens via collect_transparent
            // which advanced self.pos, but if the child fails, we must restore the original
            // position (saved_pos from before transparent collection) so the parent can try
            // alternative grammars from the correct location.
            // ALSO CRITICAL: Set frame.end_pos to original_pos, not frame.pos, because
            // frame.pos might still be at the advanced position after transparent collection.
            self.pos = original_pos;
            frame.end_pos = Some(original_pos);
        }

        frame.state = FrameState::Combining;
        Ok(TableFrameResult::Push(frame))
    }

    /// Handle Ref Combining state using table-driven approach
    pub(crate) fn handle_ref_table_driven_combining(
        &mut self,
        mut frame: TableParseFrame,
        stack: &mut TableParseFrameStack,
    ) -> Result<TableFrameResult, ParseError> {
        let FrameContext::RefTableDriven {
            name,
            segment_class_name,
            segment_type,
            saved_pos,
            ..
        } = &mut frame.context
        else {
            return Err(ParseError::new(
                "Expected RefTableDriven context in combining".to_string(),
            ));
        };

        log::debug!(
            "Ref[table] Combining: frame_id={}, accumulated={}",
            frame.frame_id,
            frame.accumulated_matches.len()
        );

        // Debug: print accumulated children to inspect whether typed tokens are present
        if !frame.accumulated_matches.is_empty() {
            log::debug!(
                "Ref[table] Combining DEBUG: accumulated nodes={:?}",
                frame.accumulated_matches
            );
        }

        // Build final result
        let final_pos = frame.end_pos.unwrap_or(frame.pos);
        let result_match = if frame.accumulated_matches.is_empty() {
            MatchResult::empty_at(frame.pos)
        } else {
            log::debug!(
                "Ref[table] Combining: name='{}', segment_type={:?}, creating ref_match",
                name,
                segment_type
            );
            let matched_class = if segment_type.is_some() || segment_class_name.is_some() {
                Some(MatchedClass {
                    class_name: segment_class_name.clone().unwrap_or_default(),
                    segment_type: segment_type.clone(),
                    segment_kwargs: SegmentKwargs {
                        // TODO: Add back later
                        // instance_types: segment_type.clone().map(|t| vec![t]),
                        ..Default::default()
                    },
                })
            } else {
                None
            };

            // let start_idx = self.skip_start_index_forward_to_code(*saved_pos, final_pos);

            MatchResult::ref_match(
                name.clone(),
                matched_class,
                // start_idx,
                *saved_pos,
                final_pos,
                frame.accumulated_matches.to_vec(),
            )
        };

        self.pos = final_pos;
        frame.end_pos = Some(final_pos);
        frame.state = FrameState::Complete(Arc::new(result_match));

        Ok(TableFrameResult::Push(frame))
    }
}
