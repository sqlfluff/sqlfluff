use sqlfluffrs_types::GrammarId;
use std::borrow::Cow;
use std::sync::Arc;

use crate::parser::{
    match_result::{MatchedClass, SegmentKwargs},
    table_driven::frame::{TableFrameResult, TableParseFrame, TableParseFrameStack},
    FrameContext, FrameState, MatchResult, ParseError, Parser, RefState,
};

/// Sentinel prefix for an unresolvable Ref's [`ParseError`] message. The
/// Python side (`rust_parser.py`) recognises this prefix and re-raises
/// through the dialect's own `ref()`, so the resulting RuntimeError matches
/// the pure-Python parser. Exported to Python via the `sqlfluffrs` module so
/// both sides read the same constant instead of duplicating the literal.
pub const MISSING_REF_PREFIX: &str = "__MISSING_REF__:";

impl Parser<'_> {
    // ========================================================================
    // Table-Driven Ref Handlers
    // ========================================================================

    /// Build the sentinel [`ParseError`] for an unresolvable Ref.
    fn missing_ref_error(rule_name: &str, pos: usize) -> ParseError {
        ParseError::with_context(format!("{MISSING_REF_PREFIX}{rule_name}"), Some(pos), None)
    }

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
            // Try matching exclude grammar, otherwise raise RuntimeError
            let exclude_mr =
                self.parse_table_iterative_match_result(exclude_id, &frame.table_terminators)?;
            self.pos = start_pos;
            if !exclude_mr.is_empty() {
                vdebug!(
                    "Ref[table]: exclude grammar matched at pos {}, returning Empty",
                    frame.pos
                );
                return Ok(stack.complete_frame_empty(&frame));
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
            Some(&None) => return Err(Self::missing_ref_error(rule_name, start_pos)),
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
                        // PYTHON PARITY: an unresolvable Ref - a keyword or
                        // segment name the grammar references but the dialect
                        // never registered - is a hard error in Python:
                        // dialect.ref() raises RuntimeError the moment the branch
                        // is matched, rather than failing the branch. Mirror that
                        // instead of silently returning Empty (which diverged,
                        // producing an unparsable tree where Python raised).
                        vdebug!(
                            "Ref[table]: No element children and no dialect mapping for '{}', raising missing-ref error",
                            rule_name
                        );
                        return Err(Self::missing_ref_error(rule_name, start_pos));
                    }
                }
            }
        };

        // name/segment_class/segment_type are pure functions of grammar_id,
        // so build_ref_wrap looks them up itself rather than RefState
        // storing a redundant copy here.
        vdebug!(
            "Ref[table]: rule_name='{}', table_segment_class={:?}",
            rule_name,
            self.grammar_ctx.segment_class(grammar_id)
        );

        frame.context = FrameContext::Ref(RefState {
            grammar_id,
            last_child_frame_id: Some(stack.frame_id_counter),
            child_grammar_id,
            match_result: None,
        });

        // CRITICAL: Set parent frame state to WaitingForChild so it will
        // retrieve the child result on the next iteration
        frame.state = FrameState::WaitingForChild { child_index: 0 };

        // Combine the Ref's local terminators with the parent terminators so
        // the referenced child parsing respects both sets (parity with Arc path)
        let local_terminators = self.grammar_ctx.terminators_slice(grammar_id);
        let child_terminators = self.combine_terminators(
            local_terminators,
            &frame.table_terminators,
            reset_terminators,
        );

        // PYTHON PARITY: no leading-gap skip; only Sequence skips.
        let child_frame = TableParseFrame::new_child(
            stack.frame_id_counter,
            child_grammar_id,
            start_pos,
            &child_terminators,
            frame.parent_max_idx,
        );

        vdebug!(
            "Ref[table]: Parsing explicit child grammar_id={} (parent_frame_id={}, child_frame_id={}, start_pos={})",
            child_grammar_id.0,
            frame.frame_id,
            stack.frame_id_counter,
            start_pos
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
        let original_pos = frame.pos;
        let FrameContext::Ref(state) = &mut frame.context else {
            unreachable!("Expected Ref context");
        };

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
            // Restore the start so the parent can try alternatives.
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
            let grammar_id = state.grammar_id;
            let child_grammar_id = state.child_grammar_id;
            self.build_ref_wrap(grammar_id, child_grammar_id, frame.pos, final_pos, &child)
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
    ///
    /// `name`/`segment_class_name`/`segment_type` are pure functions of
    /// `grammar_id` (looked up here, not taken as separate parameters) -
    /// both call sites would otherwise have to fetch and thread through
    /// values already fully determined by `grammar_id`.
    pub(crate) fn build_ref_wrap(
        &mut self,
        grammar_id: GrammarId,
        child_grammar_id: GrammarId,
        start_pos: usize,
        final_pos: usize,
        ref_match_result: &Arc<MatchResult>,
    ) -> MatchResult {
        {
            let name = self.grammar_ctx.ref_name(grammar_id);
            let segment_class_name = self.grammar_ctx.segment_class(grammar_id);
            let segment_type = self.grammar_ctx.segment_type(grammar_id);

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
                    class_type: None,
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
                start_pos,
                final_pos,
                vec![Arc::clone(ref_match_result)],
            )
        }
    }

    /// Frame-free fast path for `Ref` grammars whose resolved target is a
    /// terminal parser.
    ///
    /// Mirrors the frame-based Ref handlers step for step: the
    /// parent-max-idx guard, the failed-child position semantics of
    /// `handle_ref_waiting_for_child`, and the result wrapping of
    /// `handle_ref_combining` (via `build_ref_wrap`). Refs with an exclude
    /// grammar, an unresolvable target, or a non-terminal target return
    /// `Ok(None)` and take the frame path - for an unresolvable target that
    /// lets `handle_ref_initial` raise its hard missing-ref error instead of
    /// this fast path silently yielding Empty.
    pub(crate) fn try_ref_terminal_inline(
        &mut self,
        grammar_id: GrammarId,
        parent_max_idx: Option<usize>,
    ) -> Result<Option<MatchResult>, ParseError> {
        // Excludes can be compound grammars; leave those to the frame path.
        if self.grammar_ctx.exclude(grammar_id).is_some() {
            return Ok(None);
        }
        let start_pos = self.pos;
        let Some(child_id) = self.resolve_ref_target(grammar_id) else {
            // No element child and no dialect mapping: this is the same
            // missing-ref condition handle_ref_initial treats as a hard
            // error. Fall back to the frame path instead of yielding a soft
            // Empty here, so its Err(missing_ref_error(...)) actually
            // propagates instead of being absorbed as an ordinary
            // non-match by the calling combinator.
            return Ok(None);
        };
        let child_variant = self.grammar_ctx.variant(child_id);
        if !Self::is_terminal_variant(child_variant) {
            return Ok(None);
        }
        // Python parity: beyond the parent's ceiling a Ref returns Empty.
        if let Some(parent_max) = parent_max_idx {
            if start_pos >= parent_max {
                return Ok(Some(MatchResult::empty_at(start_pos)));
            }
        }
        // No leading-gap skip (mirrors handle_ref_initial).
        let mr = self.dispatch_terminal_match(child_variant, child_id)?;
        if mr.is_empty() {
            self.pos = start_pos;
            return Ok(Some(MatchResult::empty_at(start_pos)));
        }
        let final_pos = self.pos;
        let child = Arc::new(mr);
        let wrapped = self.build_ref_wrap(grammar_id, child_id, start_pos, final_pos, &child);
        self.pos = final_pos;
        Ok(Some(wrapped))
    }
}

#[cfg(test)]
mod tests {
    use std::str::FromStr;

    use sqlfluffrs_dialects::Dialect;
    use sqlfluffrs_lexer::{LexInput, Lexer};
    use sqlfluffrs_types::{GrammarId, GrammarVariant};

    use crate::parser::Parser;

    /// Inline terminal Ref path; ends are Python's `Ref("FromKeywordSegment").match`.
    #[test]
    fn test_inline_terminal_ref_does_not_skip_leading_whitespace() {
        let dialect = Dialect::from_str("ansi").expect("dialect");
        let lexer = Lexer::new(None, dialect.get_lexers().to_vec());
        for (sql, expected_end) in [("FROM", Some(1)), (" FROM", None)] {
            let (tokens, _) = lexer.lex(LexInput::String(sql.to_string()), false);
            let mut parser = Parser::new(&tokens, dialect, hashbrown::HashMap::new());
            let ctx = &parser.grammar_ctx;
            let ref_id = (0..ctx.len() as u32)
                .map(GrammarId)
                .find(|&g| {
                    ctx.variant(g) == GrammarVariant::Ref && ctx.ref_name(g) == "FromKeywordSegment"
                })
                .expect("Ref(FromKeywordSegment)");
            let mr = parser
                .try_ref_terminal_inline(ref_id, None)
                .expect("parse")
                .expect("terminal target takes the inline path");
            let got = (!mr.is_empty()).then(|| mr.end());
            assert_eq!(got, expected_end, "{sql:?}");
            assert_eq!(parser.pos, expected_end.unwrap_or(0), "{sql:?} pos");
        }
    }
}
