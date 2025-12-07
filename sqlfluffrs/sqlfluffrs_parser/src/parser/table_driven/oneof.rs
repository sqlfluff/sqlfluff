use crate::parser::{
    table_driven::frame::{TableFrameResult, TableParseFrame, TableParseFrameStack},
    FrameContext, FrameState, ParseError, Parser,
};
use sqlfluffrs_types::GrammarId;

impl<'a> Parser<'_> {
    // ========================================================================
    // Table-driven OneOf Handlers (migrated from core.rs)
    // ========================================================================

    /// Handle OneOf Initial state using table-driven approach
    pub(crate) fn handle_oneof_table_driven_initial(
        &mut self,
        mut frame: TableParseFrame,
        parent_terminators: &[GrammarId],
        stack: &mut TableParseFrameStack,
    ) -> Result<TableFrameResult, ParseError> {
        // CRITICAL: Restore parser position from frame
        self.pos = frame.pos;
        let ctx = self
            .grammar_ctx
            .expect("GrammarContext required for table-driven parsing");

        let grammar_id = frame.grammar_id;
        let inst = ctx.inst(grammar_id);
        let start_pos = frame.pos;

        log::debug!(
            "OneOf[table] Initial: frame_id={}, pos={}, grammar_id={}, children={}",
            frame.frame_id,
            start_pos,
            grammar_id.0,
            inst.child_count
        );

        // Check exclude grammar first (before any other logic)
        if let Some(exclude_id) = ctx.exclude(grammar_id) {
            // Try matching exclude grammar
            if let Ok(exclude_result) = self.parse_table_iterative(exclude_id, parent_terminators) {
                if !exclude_result.is_empty() {
                    log::debug!(
                        "OneOf[table]: exclude grammar matched at pos {}, returning Empty",
                        start_pos
                    );
                    stack.results.insert(
                        frame.frame_id,
                        (crate::parser::Node::Empty, start_pos, None),
                    );
                    return Ok(TableFrameResult::Done);
                }
            }
            log::debug!("OneOf[table]: exclude grammar did not match, continuing");
        }

        // Collect leading transparent tokens if allow_gaps
        let leading_ws = if inst.flags.allow_gaps() {
            self.collect_transparent(true)
        } else {
            Vec::new()
        };
        let post_skip_pos = self.pos;

        // Combine terminators
        let local_terminators: Vec<GrammarId> = ctx.terminators(grammar_id).collect();
        let all_terminators = crate::parser::core::Parser::combine_terminators_table_driven(
            &local_terminators,
            parent_terminators,
            inst.flags.reset_terminators(),
        );

        // Calculate max_idx with terminators
        let grammar_parse_mode = inst.parse_mode;
        let max_idx = self.calculate_max_idx_with_elements_table_driven(
            post_skip_pos,
            &all_terminators,
            &[],
            grammar_parse_mode,
            frame.parent_max_idx,
        );

        log::debug!(
            "OneOf[table]: post_skip_pos={}, max_idx={}, terminators={}",
            post_skip_pos,
            max_idx,
            all_terminators.len()
        );

        // Early termination check for GREEDY mode
        if grammar_parse_mode == sqlfluffrs_types::ParseMode::Greedy {
            // Get element children (excluding exclude grammar)
            let element_children: Vec<GrammarId> = ctx.element_children(grammar_id).collect();

            if self.is_terminated_with_elements_table_driven(&all_terminators, &element_children) {
                log::debug!("OneOf[table]: Early termination - at terminator position");
                if inst.flags.optional() {
                    stack.results.insert(
                        frame.frame_id,
                        (crate::parser::Node::Empty, post_skip_pos, None),
                    );
                    return Ok(TableFrameResult::Done);
                }
            }
        }

        // Get element children (excluding exclude grammar if present)
        let all_children: Vec<GrammarId> = ctx.element_children(grammar_id).collect();

        // Prune options based on simple hints (conservative - keeps all for now)
        let pruned_children = self.prune_options_table_driven(&all_children);

        // Debug: list kept children names
        let mut kept_names: Vec<String> = Vec::new();
        for gid in &pruned_children {
            let var = ctx.variant(*gid);
            let name = match var {
                sqlfluffrs_types::GrammarVariant::Ref => ctx.ref_name(*gid).to_string(),
                sqlfluffrs_types::GrammarVariant::StringParser
                | sqlfluffrs_types::GrammarVariant::TypedParser
                | sqlfluffrs_types::GrammarVariant::RegexParser => ctx.template(*gid).to_string(),
                other => format!("{:?}", other),
            };
            kept_names.push(name);
        }
        log::debug!(
            "OneOf[table]: kept_children_count={} names={:?}",
            pruned_children.len(),
            kept_names
        );

        if pruned_children.is_empty() {
            log::debug!("OneOf[table]: No children after pruning, returning Empty");
            stack.results.insert(
                frame.frame_id,
                (crate::parser::Node::Empty, post_skip_pos, None),
            );
            return Ok(TableFrameResult::Done);
        }

        // Try first child
        let first_child = pruned_children[0];

        log::debug!(
            "OneOf[table]: Trying first of {} pruned children, grammar_id={}",
            pruned_children.len(),
            first_child.0
        );

        // Store context for WaitingForChild state
        frame.context = FrameContext::OneOfTableDriven {
            grammar_id,
            pruned_children: pruned_children.clone(),
            leading_ws,
            post_skip_pos,
            longest_match: None,
            tried_elements: 0,
            max_idx,
            last_child_frame_id: Some(stack.frame_id_counter),
            current_child_id: Some(first_child),
        };

        frame.state = FrameState::WaitingForChild {
            child_index: 0,
            total_children: 1,
        };

        // CRITICAL: Store terminators in frame for use when trying subsequent children
        frame.table_terminators = all_terminators.clone();

        // Create table-driven child frame with filtered terminators
        let mut child_frame = TableParseFrame::new_child(
            stack.frame_id_counter,
            first_child,
            post_skip_pos,
            all_terminators.clone(),
            Some(max_idx),
        );

        log::debug!(
            "OneOf[table]: Pushing child frame: parent_frame_id={}, child_frame_id={}, child_gid={}",
            frame.frame_id,
            child_frame.frame_id,
            first_child.0
        );

        stack.increment_frame_id_counter();
        stack.push(&mut frame);
        stack.push(&mut child_frame);
        Ok(TableFrameResult::Done)
    }

    /// Handle OneOf WaitingForChild state using table-driven approach
    pub(crate) fn handle_oneof_table_driven_waiting_for_child(
        &mut self,
        mut frame: TableParseFrame,
        child_node: &crate::parser::Node,
        child_end_pos: &usize,
        _child_element_key: &Option<u64>,
        stack: &mut TableParseFrameStack,
    ) -> Result<TableFrameResult, ParseError> {
        let ctx = self.grammar_ctx.expect("GrammarContext required");

        let FrameContext::OneOfTableDriven {
            grammar_id,
            pruned_children,
            post_skip_pos,
            longest_match,
            tried_elements,
            max_idx,
            current_child_id,
            ..
        } = &mut frame.context
        else {
            unreachable!("Expected OneOfTableDriven context");
        };

        let consumed = *child_end_pos - *post_skip_pos;
        let current_child = current_child_id.expect("current_child_id should be set");

        // Compute values for per-candidate logging
        let child_end_pos_val = *child_end_pos;
        let child_consumed = consumed;
        let child_name = match ctx.variant(current_child) {
            sqlfluffrs_types::GrammarVariant::Ref => ctx.ref_name(current_child).to_string(),
            sqlfluffrs_types::GrammarVariant::StringParser
            | sqlfluffrs_types::GrammarVariant::TypedParser
            | sqlfluffrs_types::GrammarVariant::RegexParser => {
                ctx.template(current_child).to_string()
            }
            other => format!("{:?}", other),
        };

        let child_is_clean = if child_node.is_empty() {
            false
        } else {
            Self::is_node_clean(child_node)
        };
        // Collect the raw tokens consumed by this candidate for debugging (bounded)
        let mut candidate_tokens: Vec<String> = Vec::new();
        if child_end_pos_val > *post_skip_pos {
            let start_idx = (*post_skip_pos).min(self.tokens.len());
            let end_idx = child_end_pos_val.min(self.tokens.len());
            if start_idx < end_idx {
                for tok in &self.tokens[start_idx..end_idx] {
                    candidate_tokens.push(tok.raw().to_string());
                }
            }
        }

        log::debug!(
            "OneOf[table] WaitingForChild: frame_id={}, child_empty={}, consumed={}, tried={}/{}, candidate_id={}, candidate_name={}, candidate_end_pos={}, candidate_consumed={}, candidate_clean={}, candidate_tokens={:?}",
            frame.frame_id,
            child_node.is_empty(),
            consumed,
            tried_elements,
            pruned_children.len(),
            current_child.0,
            child_name,
            child_end_pos_val,
            child_consumed,
            child_is_clean,
            candidate_tokens
        );

        // Update longest match if this is better
        let mut should_early_terminate = false;
        if !child_node.is_empty() {
            let is_better = if let Some((ref current_best, current_consumed, _)) = longest_match {
                let current_is_clean = Self::is_node_clean(current_best);

                if child_is_clean && !current_is_clean {
                    true
                } else if !child_is_clean && current_is_clean {
                    false
                } else {
                    consumed > *current_consumed
                }
            } else {
                true
            };

            if is_better {
                *longest_match = Some((child_node.clone(), consumed, current_child));
                log::debug!(
                    "OneOf[table]: longest_match set: child_id={}, consumed={}, node={:?}",
                    current_child.0,
                    consumed,
                    child_node
                );

                // Python parity: Check for early termination with terminators
                // If we have a match and there's a terminator at the next position,
                // we can stop trying other options (significant performance improvement)
                let next_pos_after_match = child_end_pos_val;

                // Skip to next code position to check for terminators
                let next_code_pos =
                    self.skip_start_index_forward_to_code(next_pos_after_match, *max_idx);

                // If we've reached the end, consider it terminated
                if next_code_pos >= self.tokens.len() {
                    log::debug!("OneOf[table]: Early termination - reached end of tokens");
                    should_early_terminate = true;
                } else if !frame.table_terminators.is_empty() {
                    // Check if any terminator matches at this position
                    for terminator_id in &frame.table_terminators {
                        // Skip NONCODE sentinel value - it's handled separately in is_terminated
                        if *terminator_id == sqlfluffrs_types::GrammarId::NONCODE {
                            // Check if there's a non-code token at the current position
                            if next_code_pos < self.tokens.len() {
                                let tok = &self.tokens[next_code_pos];
                                if !tok.is_code() {
                                    log::debug!(
                                        "OneOf[table]: Early termination - NONCODE terminator matched non-code token at pos {}",
                                        next_code_pos
                                    );
                                    should_early_terminate = true;
                                    break;
                                }
                            }
                            continue;
                        }

                        self.pos = next_code_pos;
                        if let Ok(term_result) = self.parse_table_iterative(*terminator_id, &[]) {
                            if !term_result.is_empty() {
                                log::debug!(
                                    "OneOf[table]: Early termination - terminator {} matched at pos {}",
                                    terminator_id.0,
                                    next_code_pos
                                );
                                should_early_terminate = true;
                                break;
                            }
                        }
                    }
                }
            }
        }

        *tried_elements += 1;

        // Early termination: If last option OR terminated by terminators, go straight to Combining
        let is_last_option = *tried_elements >= pruned_children.len();
        if should_early_terminate || is_last_option {
            log::debug!(
                "OneOf[table]: {} - transitioning to Combining (tried {}/{})",
                if should_early_terminate {
                    "Early termination"
                } else {
                    "Last option"
                },
                tried_elements,
                pruned_children.len()
            );
            frame.state = FrameState::Combining;
            stack.push(&mut frame);
            return Ok(TableFrameResult::Done);
        }

        // Try next child
        if *tried_elements < pruned_children.len() {
            // Try next child
            self.pos = *post_skip_pos;
            let next_child = pruned_children[*tried_elements];
            *current_child_id = Some(next_child);

            log::debug!(
                "OneOf[table]: Trying next child grammar_id={}",
                next_child.0
            );

            frame.state = FrameState::WaitingForChild {
                child_index: 0,
                total_children: 1,
            };

            // Build child frame using same table_terminators as parent
            let child_frame = TableParseFrame::new_child(
                stack.frame_id_counter,
                next_child,
                *post_skip_pos,
                frame.table_terminators.clone(),
                Some(*max_idx),
            );

            TableParseFrame::push_child_and_update_parent(stack, &mut frame, child_frame, "OneOf");
            Ok(TableFrameResult::Done)
        } else {
            // Should never reach here due to early termination logic above
            unreachable!("OneOf should have terminated in early termination check")
        }
    }

    /// Handle OneOf Combining state using table-driven approach
    pub(crate) fn handle_oneof_table_driven_combining(
        &mut self,
        mut frame: TableParseFrame,
        _stack: &mut TableParseFrameStack,
    ) -> Result<TableFrameResult, ParseError> {
        let ctx = self.grammar_ctx.expect("GrammarContext required");

        let FrameContext::OneOfTableDriven {
            grammar_id,
            leading_ws,
            post_skip_pos,
            longest_match,
            max_idx: _,
            ..
        } = &frame.context
        else {
            return Err(ParseError::new(
                "Expected OneOfTableDriven context in combining".to_string(),
            ));
        };

        let inst = ctx.inst(*grammar_id);

        log::debug!(
            "OneOf[table] Combining: frame_id={}, has_match={}",
            frame.frame_id,
            longest_match.is_some()
        );

        if let Some((best_node, best_consumed, best_child_id)) = longest_match {
            log::debug!(
                "OneOf[table] Combining DEBUG: best_child_id={}, best_consumed={}, best_node={:?}",
                best_child_id.0,
                best_consumed,
                best_node
            );
        } else {
            log::debug!(
                "OneOf[table] Combining DEBUG: no match found, frame.accumulated={}",
                frame.accumulated.len()
            );
        }

        // Build final result
        let (result_node, final_pos, _child_id) =
            if let Some((best_node, best_consumed, best_child_id)) = longest_match {
                let final_pos = *post_skip_pos + *best_consumed;
                self.pos = final_pos;

                let result = if !leading_ws.is_empty() {
                    let mut children = leading_ws.clone();
                    children.push(best_node.clone());
                    crate::parser::Node::Sequence { children }
                } else {
                    best_node.clone()
                };

                (result, final_pos, Some(*best_child_id))
            } else {
                // No match found
                let result_node = if inst.flags.optional() {
                    crate::parser::Node::Empty
                } else {
                    // TODO: Apply parse_mode (Greedy vs Strict)
                    crate::parser::Node::Empty
                };
                let final_pos = frame.pos;
                self.pos = final_pos;

                (result_node, final_pos, None)
            };

        // Transition to Complete
        frame.end_pos = Some(final_pos);
        frame.state = FrameState::Complete(result_node);

        Ok(TableFrameResult::Push(frame))
    }
}
