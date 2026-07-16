use sqlfluffrs_types::GrammarId;
use std::borrow::Cow;
use std::sync::Arc;

use crate::parser::{
    match_result::{MatchedClass, SegmentKwargs},
    table_driven::frame::{TableFrameResult, TableParseFrame, TableParseFrameStack},
    FrameContext, FrameState, MatchResult, ParseError, Parser, RefState,
};
#[cfg(feature = "verbose-debug")]
use crate::vdebug;

impl Parser<'_> {
    // ========================================================================
    // Table-Driven Ref Handlers
    // ========================================================================

    /// Handle Ref Initial state using table-driven approach
    pub(crate) fn handle_ref_initial(
        &mut self,
        mut frame: TableParseFrame,
        stack: &mut TableParseFrameStack,
    ) -> Result<TableFrameResult, ParseError> {
        let grammar_id = frame.grammar_id;
        let reset_terminators = self.grammar_ctx.inst(grammar_id).flags.reset_terminators();
        let start_pos = frame.pos;

        // Get rule name via GrammarContext helper which knows how names are
        // stored in aux_data (generator packs ref names into aux_data).
        let rule_name = self.grammar_ctx.ref_name(grammar_id);

        vdebug!(
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
                vdebug!(
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
            if let Ok(exclude_mr) =
                self.parse_table_iterative_match_result(exclude_id, &frame.table_terminators)
            {
                self.pos = start_pos;
                if !exclude_mr.is_empty() {
                    vdebug!(
                        "Ref[table]: exclude grammar matched at pos {}, returning Empty",
                        frame.pos
                    );
                    return Ok(stack.complete_frame_empty(&frame));
                }
            }
            vdebug!("Ref[table]: exclude grammar did not match, continuing");
        }

        self.pos = start_pos;

        // Resolve the Ref's child grammar. This depends only on `grammar_id`
        // (first element child if present, else a by-name dialect lookup), but the
        // same Ref is hit thousands of times per parse, so memoize it — the by-name
        // `get_*_segment_grammar` match is otherwise ~20% of parse self-time.
        let child_grammar_id = match self.ref_child_cache.get(&grammar_id.0) {
            Some(&Some(id)) => GrammarId(id),
            Some(&None) => return Ok(stack.complete_frame_empty(&frame)),
            None => {
                // First element child if present, otherwise resolve by name.
                // CRITICAL: For Ref grammars with an exclude, `children` contains ONLY
                // the exclude grammar, so the referenced segment is resolved by name.
                let resolved = self
                    .grammar_ctx
                    .element_children(grammar_id)
                    .next()
                    .or_else(|| {
                        self.dialect
                            .get_segment_grammar(rule_name)
                            .map(|root| root.grammar_id)
                    });
                self.ref_child_cache
                    .insert(grammar_id.0, resolved.map(|g| g.0));
                match resolved {
                    Some(id) => id,
                    None => {
                        vdebug!(
                            "Ref[table]: No element children and no dialect mapping for '{}', returning Empty",
                            rule_name
                        );
                        return Ok(stack.complete_frame_empty(&frame));
                    }
                }
            }
        };

        // If the explicit child grammar allows gaps, collect leading transparent
        // tokens so child parsing starts at the next non-transparent token.
        let child_allows_gaps = self.grammar_ctx.inst(child_grammar_id).flags.allow_gaps();
        let this_type = self.grammar_ctx.segment_type(grammar_id);
        let child_start_pos = if child_allows_gaps {
            self.skip_start_index_forward_to_code(start_pos, self.tokens.len())
        } else {
            start_pos
        };

        // Determine the segment_class (Python class name) from tables
        // This is what gets stored in matched_class for Python lookup
        // e.g., "ProcedureDefinitionGrammar", "SelectStatementSegment", etc.
        let table_segment_class = self.grammar_ctx.segment_class(grammar_id);

        vdebug!(
            "Ref[table]: rule_name='{}', table_segment_class={:?}",
            rule_name,
            table_segment_class
        );

        // Store context with collected leading transparent tokens
        frame.context = FrameContext::Ref(RefState {
            grammar_id,
            name: rule_name,
            segment_class_name: table_segment_class,
            segment_type: this_type,
            saved_pos: child_start_pos,
            last_child_frame_id: Some(stack.frame_id_counter),
            child_grammar_id,
            match_result: None,
        });

        // CRITICAL: Set parent frame state to WaitingForChild so it will
        // retrieve the child result on the next iteration
        frame.state = FrameState::WaitingForChild { child_index: 0 };

        // Combine the Ref's local terminators with the parent terminators so
        // the referenced child parsing respects both sets (parity with Arc path)
        let local_terminators: Vec<GrammarId> = self.grammar_ctx.terminators(grammar_id).collect();
        let child_terminators = Self::combine_terminators(
            &local_terminators,
            &frame.table_terminators,
            reset_terminators,
        );

        let child_frame = TableParseFrame::new_child(
            stack.frame_id_counter,
            child_grammar_id,
            child_start_pos,
            &child_terminators,
            frame.parent_max_idx,
        );

        vdebug!(
            "Ref[table]: Parsing explicit child grammar_id={} (parent_frame_id={}, child_frame_id={}, start_pos={})",
            child_grammar_id.0,
            frame.frame_id,
            stack.frame_id_counter,
            child_start_pos
        );

        Ok(stack.push_child_and_wait(frame, child_frame, 0))
    }

    /// Handle Ref WaitingForChild state using table-driven approach
    pub(crate) fn handle_ref_waiting_for_child(
        &mut self,
        mut frame: TableParseFrame,
        child_match: &Arc<MatchResult>,
        child_end_pos: &usize,
    ) -> Result<TableFrameResult, ParseError> {
        let FrameContext::Ref(state) = &mut frame.context else {
            unreachable!("Expected Ref context");
        };
        let original_pos = state.saved_pos;

        vdebug!(
            "Ref[table] WaitingForChild: frame_id={}, child_empty={}, child_end_pos={}",
            frame.frame_id,
            child_match.is_empty(),
            child_end_pos
        );

        // Store child result and transition to Combining
        if !child_match.is_empty() {
            vdebug!(
                "Ref[table]: frame_id={} child matched, setting pos to {}",
                frame.frame_id,
                child_end_pos
            );
            state.match_result = Some(Arc::clone(child_match));
            self.pos = *child_end_pos;
            frame.end_pos = Some(*child_end_pos);
        } else {
            vdebug!(
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
    pub(crate) fn handle_ref_combining(
        &mut self,
        mut frame: TableParseFrame,
    ) -> Result<TableFrameResult, ParseError> {
        let FrameContext::Ref(state) = &mut frame.context else {
            return Err(ParseError::new(
                "Expected Ref context in combining".to_string(),
            ));
        };

        vdebug!("Ref[table] Combining: frame_id={}", frame.frame_id,);

        // Build final result
        let final_pos = frame.end_pos.unwrap_or(frame.pos);
        let result_match = if let Some(ref_match_result) = &state.match_result {
            let child = Arc::clone(ref_match_result);
            let name = state.name;
            let grammar_id = state.grammar_id;
            let child_grammar_id = state.child_grammar_id;
            let segment_class_name = state.segment_class_name.take();
            let segment_type = state.segment_type;
            let saved_pos = state.saved_pos;
            self.build_ref_wrap(
                name,
                grammar_id,
                child_grammar_id,
                segment_class_name,
                segment_type,
                saved_pos,
                final_pos,
                &child,
            )
        } else {
            MatchResult::empty_at(frame.pos)
        };

        self.pos = final_pos;
        frame.end_pos = Some(final_pos);
        frame.state = FrameState::Complete(Arc::new(result_match));

        Ok(TableFrameResult::Push(frame))
    }

    /// Wrap a Ref target's match result exactly as `handle_ref_combining`
    /// does: build the MatchedClass from the grammar tables (or skip it
    /// entirely for a bare Token target, mirroring Python's isinstance
    /// path) and produce the final `ref_match`. Shared by the frame-based
    /// combining handler and the frame-free Ref fast path.
    #[allow(clippy::too_many_arguments)]
    pub(crate) fn build_ref_wrap(
        &mut self,
        name: &'static str,
        grammar_id: GrammarId,
        child_grammar_id: GrammarId,
        segment_class_name: Option<&'static str>,
        segment_type: Option<&'static str>,
        saved_pos: usize,
        final_pos: usize,
        ref_match_result: &Arc<MatchResult>,
    ) -> MatchResult {
        {
            // Debug: print accumulated children to inspect whether typed tokens are present
            vdebug!(
                "Ref[table] Combining DEBUG: accumulated nodes={:?}",
                ref_match_result
            );
            // A Ref to a bare (match_grammar-less) class mirrors native
            // BaseSegment.match's isinstance path: consume the matched token
            // unchanged, no class wrap, so its lexed type/class chain survives.
            let is_token_target = self.grammar_ctx.variant(child_grammar_id)
                == sqlfluffrs_types::GrammarVariant::Token;

            vdebug!(
                "Ref[table] Combining: name='{}', is_token_target={}, creating ref_match",
                name,
                is_token_target
            );
            let matched_class = if is_token_target {
                None
            } else if segment_type.is_some_and(|t| !t.is_empty()) || segment_class_name.is_some() {
                // `segment_type` is `Option<&'static str>` (Copy), so
                // binding by value keeps the `'static` lifetime — this
                // borrows the grammar-table string into the node with no
                // allocation.
                let segment_type: Cow<'static, str> =
                    Cow::Borrowed(segment_type.unwrap_or_default());
                // Look up the Python _class_types hierarchy for this grammar from codegen tables.
                let class_types = self.grammar_ctx.segment_class_types(grammar_id);
                Some(MatchedClass {
                    // segment_class_name is Option<&'static str> (PR #8002), so
                    // borrow the grammar-table class name straight into the node.
                    class_name: Cow::Borrowed(segment_class_name.unwrap_or_default()),
                    segment_type: Some(segment_type),
                    segment_kwargs: SegmentKwargs {
                        class_types,
                        ..Default::default()
                    },
                })
            } else {
                None
            };

            MatchResult::ref_match(
                name,
                matched_class,
                saved_pos,
                final_pos,
                vec![Arc::clone(ref_match_result)],
            )
        }
    }

    /// Frame-free fast path for `Ref` grammars whose resolved target is a
    /// terminal parser.
    ///
    /// Mirrors the frame-based Ref handlers step for step: the
    /// parent-max-idx guard and failed-resolution behaviour of
    /// `handle_ref_initial` (empty result at the pre-skip position), the
    /// leading-gap skip when the target allows gaps, the failed-child
    /// position semantics of `handle_ref_waiting_for_child` (position and
    /// reported extent at the post-skip position), and the result wrapping
    /// of `handle_ref_combining` (via `build_ref_wrap`). Refs with an
    /// exclude grammar or a non-terminal target return `Ok(None)` and take
    /// the frame path.
    pub(crate) fn try_ref_terminal_inline(
        &mut self,
        grammar_id: GrammarId,
        parent_max_idx: Option<usize>,
    ) -> Result<Option<MatchResult>, ParseError> {
        use sqlfluffrs_types::GrammarVariant;

        // Excludes can be compound grammars; leave those to the frame path.
        if self.grammar_ctx.exclude(grammar_id).is_some() {
            return Ok(None);
        }
        let start_pos = self.pos;
        let Some(child_id) = self.resolve_ref_target(grammar_id) else {
            // No element child and no dialect mapping: Ref yields Empty.
            return Ok(Some(MatchResult::empty_at(start_pos)));
        };
        let child_variant = self.grammar_ctx.variant(child_id);
        let is_terminal = matches!(
            child_variant,
            GrammarVariant::StringParser
                | GrammarVariant::TypedParser
                | GrammarVariant::MultiStringParser
                | GrammarVariant::RegexParser
                | GrammarVariant::Token
        );
        if !is_terminal {
            return Ok(None);
        }
        // Python parity: beyond the parent's ceiling a Ref returns Empty.
        if let Some(parent_max) = parent_max_idx {
            if start_pos >= parent_max {
                return Ok(Some(MatchResult::empty_at(start_pos)));
            }
        }
        // Skip leading non-code when the target allows gaps (mirrors
        // handle_ref_initial's child_start_pos).
        let child_allows_gaps = self.grammar_ctx.inst(child_id).flags.allow_gaps();
        let child_start_pos = if child_allows_gaps {
            self.skip_start_index_forward_to_code(start_pos, self.tokens.len())
        } else {
            start_pos
        };
        self.pos = child_start_pos;
        let mr = match child_variant {
            GrammarVariant::StringParser => self.handle_string_parser(child_id)?,
            GrammarVariant::TypedParser => self.typed_parser_match(child_id)?,
            GrammarVariant::MultiStringParser => self.handle_multi_string_parser(child_id)?,
            GrammarVariant::RegexParser => self.handle_regex_parser(child_id)?,
            GrammarVariant::Token => self.handle_token(child_id)?,
            _ => unreachable!(),
        };
        if mr.is_empty() {
            // Failed child: extent and position are the post-skip position
            // (handle_ref_waiting_for_child's original_pos semantics), while
            // the empty result itself sits at the Ref's own position
            // (handle_ref_combining's `empty_at(frame.pos)`).
            self.pos = child_start_pos;
            return Ok(Some(MatchResult::empty_at(start_pos)));
        }
        let final_pos = self.pos;
        let rule_name = self.grammar_ctx.ref_name(grammar_id);
        let segment_class_name = self.grammar_ctx.segment_class(grammar_id);
        let segment_type = self.grammar_ctx.segment_type(grammar_id);
        let child = Arc::new(mr);
        let wrapped = self.build_ref_wrap(
            rule_name,
            grammar_id,
            child_id,
            segment_class_name,
            segment_type,
            child_start_pos,
            final_pos,
            &child,
        );
        self.pos = final_pos;
        Ok(Some(wrapped))
    }
}
