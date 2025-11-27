use sqlfluffrs_types::{GrammarId, ParseMode, RootGrammar};

use crate::parser::{
    table_driven::frame::{TableFrameResult, TableParseFrame, TableParseFrameStack},
    FrameContext, FrameState, Node, ParseError, Parser,
};

impl<'a> Parser<'_> {
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
        self.pos = frame.pos;
        let ctx = self.grammar_ctx.expect("GrammarContext required");

        let inst = ctx.inst(grammar_id);
        let start_pos = frame.pos;

        // Get rule name via GrammarContext helper which knows how names are
        // stored in aux_data (generator packs ref names into aux_data).
        let rule_name = ctx.ref_name(grammar_id).to_string();

        log::debug!(
            "Ref[table] Initial: frame_id={}, pos={}, grammar_id={}, rule={}",
            frame.frame_id,
            start_pos,
            grammar_id.0,
            rule_name
        );

        // Python parity: If parent's max_idx is set and we're beyond it,
        // return Empty rather than error so parents (OneOf etc.) can try
        // other options. This mirrors the Arc-based Ref behavior.
        if let Some(parent_max) = frame.parent_max_idx {
            if frame.pos >= parent_max {
                log::debug!(
                    "Ref[table]: pos {} >= parent_max_idx {}, returning Empty",
                    frame.pos,
                    parent_max
                );
                stack
                    .results
                    .insert(frame.frame_id, (Node::Empty, frame.pos, None));
                return Ok(TableFrameResult::Done);
            }
        }

        // Check exclude grammar first (table-driven exclude id if present).
        if let Some(exclude_id) = ctx.exclude(grammar_id) {
            if let Ok(exclude_node) = self.parse_table_iterative(exclude_id, parent_terminators) {
                if !exclude_node.is_empty() {
                    log::debug!(
                        "Ref[table]: exclude grammar matched at pos {}, returning Empty",
                        frame.pos
                    );
                    stack
                        .results
                        .insert(frame.frame_id, (Node::Empty, frame.pos, None));
                    return Ok(TableFrameResult::Done);
                }
            }
            log::debug!("Ref[table]: exclude grammar did not match, continuing");
        }

        let saved_pos = start_pos;
        let children: Vec<GrammarId> = ctx.children(grammar_id).collect();

        // Use first child grammar id if present, otherwise resolve by name via dialect mapping.
        let child_grammar_id = if !children.is_empty() {
            children[0]
        } else {
            match self.dialect.get_segment_grammar(&rule_name) {
                Some(RootGrammar::TableDriven {
                    grammar_id: target_gid,
                    ..
                }) => target_gid,
                _ => {
                    log::debug!(
                "Ref[table]: No child grammar and no dialect mapping for '{}', returning Empty",
                rule_name
                );
                    stack
                        .results
                        .insert(frame.frame_id, (Node::Empty, start_pos, None));
                    return Ok(TableFrameResult::Done);
                }
            }
        };

        // If the explicit child grammar allows gaps, collect leading transparent
        // tokens so child parsing starts at the next non-transparent token.
        let mut leading_transparent: Vec<Node> = Vec::new();
        let child_inst = ctx.inst(child_grammar_id);
        if child_inst.flags.allow_gaps() {
            let ws = self.collect_transparent(true);
            if !ws.is_empty() {
                log::debug!(
                    "Ref[table]: Collected {} leading transparent tokens for explicit child",
                    ws.len()
                );
                leading_transparent = ws;
            }
        }

        // Determine the segment_type from tables if available, otherwise use rule_name
        // let table_segment_type = self.dialect.get_segment_type(&rule_name).map(|s| s.to_string());
        let table_segment_type = ctx.segment_type(grammar_id).map(|s| s.to_string());

        // Store context with collected leading transparent tokens
        frame.context = FrameContext::RefTableDriven {
            grammar_id,
            name: rule_name,
            segment_type: table_segment_type,
            saved_pos,
            last_child_frame_id: Some(stack.frame_id_counter),
            leading_transparent,
        };

        // CRITICAL: Set parent frame state to WaitingForChild so it will
        // retrieve the child result on the next iteration
        frame.state = FrameState::WaitingForChild {
            child_index: 0,
            total_children: 1,
        };

        // Combine the Ref's local terminators with the parent terminators so
        // the referenced child parsing respects both sets (parity with Arc path)
        let local_terminators: Vec<GrammarId> = ctx.terminators(grammar_id).collect();
        let child_terminators = Self::combine_terminators_table_driven(
            &local_terminators,
            parent_terminators,
            inst.flags.reset_terminators(),
        );

        let child_frame = TableParseFrame::new_child(
            stack.frame_id_counter,
            child_grammar_id,
            self.pos,
            child_terminators,
            frame.parent_max_idx,
        );

        log::debug!(
            "Ref[table]: Parsing explicit child grammar_id={} (parent_frame_id={}, child_frame_id={}, start_pos={})",
            child_grammar_id.0,
            frame.frame_id,
            stack.frame_id_counter,
            self.pos
        );

        stack.increment_frame_id_counter();
        stack.push(&mut frame);
        stack.push(&mut child_frame.clone());

        Ok(TableFrameResult::Done)
    }

    /// Handle Ref WaitingForChild state using table-driven approach
    pub(crate) fn handle_ref_table_driven_waiting_for_child(
        &mut self,
        mut frame: TableParseFrame,
        child_node: &Node,
        child_end_pos: &usize,
        stack: &mut TableParseFrameStack,
    ) -> Result<TableFrameResult, ParseError> {
        let _ctx = self.grammar_ctx.expect("GrammarContext required");

        let FrameContext::RefTableDriven { .. } = &frame.context else {
            unreachable!("Expected RefTableDriven context");
        };

        log::debug!(
            "Ref[table] WaitingForChild: frame_id={}, child_empty={}, child_end_pos={}",
            frame.frame_id,
            child_node.is_empty(),
            child_end_pos
        );

        // Store child result and transition to Combining
        if !child_node.is_empty() {
            log::debug!(
                "Ref[table]: frame_id={} child matched, accumulated_before={}, setting pos to {}",
                frame.frame_id,
                frame.accumulated.len(),
                child_end_pos
            );
            frame.accumulated.push(child_node.clone());
            self.pos = *child_end_pos;
            frame.end_pos = Some(*child_end_pos);
        } else {
            log::debug!(
                "Ref[table]: frame_id={} child was Empty, reverting pos {} -> {} and setting end_pos to {}",
                frame.frame_id,
                self.pos,
                frame.pos,
                frame.pos
            );
            // CRITICAL: Revert parser position when child returns Empty.
            // The Ref may have collected leading transparent tokens via collect_transparent
            // which advanced self.pos, but if the child fails, we must restore the original
            // position so the parent can try alternative grammars from the correct location.
            self.pos = frame.pos;
            frame.end_pos = Some(frame.pos);
        }

        frame.state = FrameState::Combining;
        Ok(TableFrameResult::Push(frame))
    }

    /// Handle Ref Combining state using table-driven approach
    pub(crate) fn handle_ref_table_driven_combining(
        &mut self,
        mut frame: TableParseFrame,
    ) -> Result<TableFrameResult, ParseError> {
        let ctx = self.grammar_ctx.expect("GrammarContext required");

        let FrameContext::RefTableDriven {
            grammar_id,
            name,
            segment_type,
            leading_transparent,
            ..
        } = &frame.context
        else {
            return Err(ParseError::new(
                "Expected RefTableDriven context in combining".to_string(),
            ));
        };

        log::debug!(
            "Ref[table] Combining: frame_id={}, accumulated={}",
            frame.frame_id,
            frame.accumulated.len()
        );

        // Debug: print accumulated children to inspect whether typed tokens are present
        if !frame.accumulated.is_empty() {
            log::debug!(
                "Ref[table] Combining DEBUG: accumulated nodes={:?}",
                frame.accumulated
            );
        }

        // Build final result
        let final_pos = frame.end_pos.unwrap_or(frame.pos);
        let result_node = if frame.accumulated.is_empty() {
            // Child didn't match
            Node::Empty
        } else {
            // Wrap child in Ref node with segment type/name from the tables
            let mut children = leading_transparent.clone();
            children.extend(frame.accumulated.clone());

            Node::Ref {
                name: name.clone(),
                segment_type: segment_type.clone(),
                child: Box::new(if children.len() == 1 {
                    children[0].clone()
                } else {
                    Node::Sequence { children }
                }),
            }
        };

        self.pos = final_pos;
        frame.end_pos = Some(final_pos);
        frame.state = FrameState::Complete(result_node);

        Ok(TableFrameResult::Push(frame))
    }
}
