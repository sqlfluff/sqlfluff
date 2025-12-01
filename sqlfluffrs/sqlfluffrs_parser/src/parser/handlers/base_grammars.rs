use std::sync::Arc;

use crate::parser::cache::CacheKey;

use crate::parser::iterative::{FrameResult, ParseFrameStack};
use crate::parser::FrameContext;
use crate::parser::FrameState;
use crate::parser::Parser;
use crate::parser::{Node, ParseError, ParseFrame};
use hashbrown::HashMap;
use sqlfluffrs_types::{Grammar, GrammarContext, GrammarFlags, GrammarId};

impl Parser<'_> {
    /// Handle Empty grammar in iterative parser
    pub fn handle_empty_initial(
        &mut self,
        mut frame: ParseFrame,
    ) -> Result<FrameResult, ParseError> {
        log::debug!(
            "START Empty: frame_id={}, pos={}",
            frame.frame_id,
            frame.pos
        );
        frame.state = FrameState::Complete(Node::Empty);
        frame.end_pos = Some(frame.pos);
        Ok(FrameResult::Push(frame))
    }

    /// Handle Missing grammar in iterative parser
    pub fn handle_missing_initial(&mut self) -> Result<FrameResult, ParseError> {
        log::debug!("START Missing");
        log::debug!("Trying missing grammar");
        Err(ParseError::with_context(
            "Encountered Missing grammar".into(),
            Some(self.pos),
            None,
        ))
    }

    /// Handle Meta grammar in iterative parser
    pub(crate) fn handle_meta_initial(
        &mut self,
        grammar: Arc<Grammar>,
        mut frame: ParseFrame,
    ) -> Result<FrameResult, ParseError> {
        log::debug!(
            "START Meta: frame_id={}, pos={}, grammar={:?}",
            frame.frame_id,
            frame.pos,
            grammar
        );
        let token_type = match grammar.as_ref() {
            Grammar::Meta(token_type) => *token_type,
            _ => {
                return Err(ParseError::with_context(
                    "handle_meta_initial called with non-Meta grammar".into(),
                    Some(self.pos),
                    Some(grammar),
                ));
            }
        };
        log::debug!("Doing nothing with meta {}", token_type);
        frame.state = FrameState::Complete(Node::Meta {
            token_type: token_type.to_string(),
            token_idx: None,
        });
        frame.end_pos = Some(frame.pos);
        Ok(FrameResult::Push(frame))
    }

    /// Handle Anything grammar in iterative parser
    ///
    /// Python parity: Implements greedy_match with nested_match=True
    /// This means we preserve bracket structure while matching greedily.
    pub fn handle_anything_initial(
        &mut self,
        mut frame: ParseFrame, // Take ownership
        parent_terminators: &[Arc<Grammar>],
    ) -> Result<FrameResult, ParseError> {
        log::debug!(
            "START Anything: frame_id={}, pos={}",
            frame.frame_id,
            frame.pos
        );
        self.pos = frame.pos;
        let mut anything_tokens = vec![];

        loop {
            if self.is_terminated(parent_terminators) || self.is_at_end() {
                break;
            }
            if let Some(tok) = self.peek() {
                let tok_type = tok.get_type();
                let tok_raw = tok.raw();

                // Python parity: nested_match=True in greedy_match
                // If we hit a bracket opener, match the entire bracketed section
                if tok_raw == "(" || tok_raw == "[" || tok_raw == "{" {
                    let close_bracket = match tok_raw.as_str() {
                        "(" => ")",
                        "[" => "]",
                        "{" => "}",
                        _ => unreachable!(),
                    };

                    // Collect all tokens in the bracketed section
                    let start_idx = self.pos;
                    let mut bracket_depth = 0;
                    let mut bracket_tokens = vec![];

                    // Add start bracket
                    bracket_tokens.push(Node::Token {
                        token_type: "start_bracket".to_string(),
                        raw: tok_raw.to_string(),
                        token_idx: self.pos,
                    });
                    bracket_depth += 1;
                    self.bump();

                    // Match everything until we find the matching close bracket
                    while bracket_depth > 0 && !self.is_at_end() {
                        if let Some(inner_tok) = self.peek() {
                            let inner_raw = inner_tok.raw();

                            if inner_raw == tok_raw {
                                bracket_depth += 1;
                            } else if inner_raw == close_bracket {
                                bracket_depth -= 1;
                            }

                            // Python parity: Preserve token types as-is
                            // Just like outer tokens, bracketed tokens keep their original types
                            let node_type = if bracket_depth == 0 {
                                "end_bracket".to_string()
                            } else {
                                inner_tok.get_type().to_string()
                            };

                            bracket_tokens.push(Node::Token {
                                token_type: node_type,
                                raw: inner_raw.to_string(),
                                token_idx: self.pos,
                            });
                            self.bump();
                        } else {
                            break;
                        }
                    }

                    // Create a bracketed node
                    // Python parity: round brackets persist=True, square/curly persist=False
                    let bracket_persists = tok_raw == "(";

                    anything_tokens.push(Node::Bracketed {
                        children: bracket_tokens,
                        bracket_persists,
                    });
                } else {
                    // Regular token - preserve the token type as-is
                    // Python's Anything just returns a slice of segments with their original types
                    anything_tokens.push(Node::Token {
                        token_type: tok_type.to_string(),
                        raw: tok_raw.to_string(),
                        token_idx: self.pos,
                    });
                    self.bump();
                }
            }
        }

        log::debug!("Anything matched {} nodes", anything_tokens.len());
        frame.state = FrameState::Complete(Node::DelimitedList {
            children: anything_tokens,
        });
        frame.end_pos = Some(self.pos);
        Ok(FrameResult::Push(frame))
    }

    // ========================================================================
    // Table-Driven Anything Handler
    // ========================================================================

    /// Handle Anything using table-driven approach
    /// Consumes all tokens until terminator or EOF, preserving bracket structure
    pub(crate) fn handle_anything_table_initial(
        &mut self,
        mut frame: ParseFrame,
        grammar_id: GrammarId,
        ctx: &GrammarContext,
        parent_terminators: &[GrammarId],
    ) -> Result<FrameResult, ParseError> {
        let start_pos = self.pos;
        let mut anything_tokens = vec![];
        log::debug!(
            "Anything[table]: pos={}, parent_terminators={}",
            start_pos,
            parent_terminators.len()
        );

        let mut terminators_vec: Vec<GrammarId> = ctx.terminators(grammar_id).collect();
        if !ctx.inst(grammar_id).flags.reset_terminators() {
            terminators_vec.extend(parent_terminators.iter().cloned());
        }

        // TODO: Check terminators properly (need to convert GrammarId to Arc<Grammar> for is_terminated)
        // For now, just consume until EOF

        loop {
            if self.is_terminated_with_elements_table_driven(&terminators_vec, &[])
                || self.is_at_end()
            {
                break;
            }

            if let Some(tok) = self.peek() {
                let tok_type = tok.get_type();
                let tok_raw = tok.raw();

                // Handle bracket openers - match entire bracketed section
                if tok_raw == "(" || tok_raw == "[" || tok_raw == "{" {
                    let close_bracket = match tok_raw.as_str() {
                        "(" => ")",
                        "[" => "]",
                        "{" => "}",
                        _ => unreachable!(),
                    };

                    let mut bracket_depth = 0;
                    let mut bracket_tokens = vec![];

                    // Add start bracket
                    bracket_tokens.push(Node::Token {
                        token_type: "start_bracket".to_string(),
                        raw: tok_raw.to_string(),
                        token_idx: self.pos,
                    });
                    bracket_depth += 1;
                    self.bump();

                    // Match everything until matching close bracket
                    while bracket_depth > 0 && !self.is_at_end() {
                        if let Some(inner_tok) = self.peek() {
                            let inner_raw = inner_tok.raw();

                            if inner_raw == tok_raw {
                                bracket_depth += 1;
                            } else if inner_raw == close_bracket {
                                bracket_depth -= 1;
                            }

                            let node_type = if bracket_depth == 0 {
                                "end_bracket".to_string()
                            } else {
                                inner_tok.get_type().to_string()
                            };

                            bracket_tokens.push(Node::Token {
                                token_type: node_type,
                                raw: inner_raw.to_string(),
                                token_idx: self.pos,
                            });
                            self.bump();
                        } else {
                            break;
                        }
                    }

                    // Round brackets persist, square/curly don't
                    let bracket_persists = tok_raw == "(";

                    anything_tokens.push(Node::Bracketed {
                        children: bracket_tokens,
                        bracket_persists,
                    });
                } else {
                    // Regular token - preserve type as-is
                    anything_tokens.push(Node::Token {
                        token_type: tok_type.to_string(),
                        raw: tok_raw.to_string(),
                        token_idx: self.pos,
                    });
                    self.bump();
                }
            }
        }

        log::debug!(
            "Anything[table]: matched {} nodes, pos {} -> {}",
            anything_tokens.len(),
            start_pos,
            self.pos
        );

        frame.state = FrameState::Complete(Node::Sequence {
            children: anything_tokens,
        });
        frame.end_pos = Some(self.pos);

        Ok(FrameResult::Push(frame))
    }

    /// Compatibility wrapper expected by `core.rs`.
    /// `core.rs` calls `handle_anything_table_driven`; implement a thin wrapper
    /// that forwards to `handle_anything_table_initial` with a dummy frame.
    pub(crate) fn handle_anything_table_driven(
        &mut self,
        grammar_id: GrammarId,
        ctx: &GrammarContext,
        parent_terminators: &[GrammarId],
    ) -> Result<Node, ParseError> {
        // Create a temporary table-driven frame to use the initial handler and then extract the Node
        let frame = ParseFrame::new_table_driven_child(
            0,
            grammar_id,
            self.pos,
            parent_terminators.to_vec(),
            None,
        );

        match self.handle_anything_table_initial(frame, grammar_id, ctx, parent_terminators)? {
            FrameResult::Push(f) => {
                if let FrameState::Complete(node) = f.state {
                    return Ok(node);
                }
                Ok(Node::Empty)
            }
            FrameResult::Done => Ok(Node::Empty),
        }
    }

    /// Handle Nothing grammar in iterative parser
    pub fn handle_nothing_initial(
        &mut self,
        mut frame: ParseFrame,
    ) -> Result<FrameResult, ParseError> {
        log::debug!(
            "START Nothing: frame_id={}, pos={}",
            frame.frame_id,
            frame.pos
        );
        log::debug!("Nothing grammar encountered, returning Empty");
        frame.state = FrameState::Complete(Node::Empty);
        frame.end_pos = Some(frame.pos);
        Ok(FrameResult::Push(frame))
    }

    /// Handle Ref grammar Initial state in iterative parser
    pub(crate) fn handle_ref_initial(
        &mut self,
        grammar: Arc<Grammar>,
        mut frame: ParseFrame,
        parent_terminators: &[Arc<Grammar>],
        stack: &mut ParseFrameStack,
        iteration_count: usize,
    ) -> Result<FrameResult, ParseError> {
        log::debug!(
            "START Ref: frame_id={}, pos={}, parent_max_idx={:?}, grammar={:?}",
            frame.frame_id,
            frame.pos,
            frame.parent_max_idx,
            grammar
        );

        // Python parity: In Python, segments are sliced to max_idx before matching.
        // segments[:max_idx] means positions 0..max_idx-1 are accessible, position max_idx is NOT.
        // So if pos >= parent_max_idx, we're beyond the slice boundary.
        // Return Empty node rather than Err so parent (e.g. OneOf) can try other options.
        if let Some(parent_max) = frame.parent_max_idx {
            if frame.pos >= parent_max {
                log::debug!(
                    "Ref: pos {} >= parent_max_idx {}, returning Empty",
                    frame.pos,
                    parent_max
                );
                stack
                    .results
                    .insert(frame.frame_id, (Node::Empty, frame.pos, None));
                return Ok(FrameResult::Done);
            }
        }

        // Destructure Grammar::Ref fields
        let (name, optional, allow_gaps, ref_terminators, reset_terminators, exclude) =
            match grammar.as_ref() {
                Grammar::Ref {
                    name,
                    optional,
                    allow_gaps,
                    terminators: ref_terminators,
                    reset_terminators,
                    exclude,
                    ..
                } => (
                    name,
                    optional,
                    allow_gaps,
                    ref_terminators,
                    reset_terminators,
                    exclude,
                ),
                _ => panic!("handle_ref_initial called with non-Ref grammar"),
            };
        // Add exclude logic: if exclude grammar matches, return empty result
        // For exclude, we use early-exit matching - stop as soon as ANY alternative matches
        if let Some(exclude_grammar) = exclude {
            let exclude_match = self.try_match_exclude_grammar(
                (**exclude_grammar).clone(),
                frame.pos,
                parent_terminators,
            );
            if exclude_match.is_ok() {
                stack
                    .results
                    .insert(frame.frame_id, (Node::Empty, frame.pos, None));
                log::debug!("exclude grammar hit: {:?}!", exclude_match);
                return Ok(FrameResult::Done);
            }
            log::debug!("exclude grammar missed!");
        }
        log::debug!(
            "Ref to segment: {}, optional: {}, allow_gaps: {}",
            name,
            optional,
            allow_gaps
        );
        let saved = frame.pos;
        self.pos = frame.pos;

        // Combine parent and local terminators
        let all_terminators: Vec<Arc<Grammar>> = if *reset_terminators {
            ref_terminators.into_iter().cloned().collect()
        } else {
            ref_terminators
                .into_iter()
                .chain(parent_terminators.iter())
                .cloned()
                .collect()
        };

        // Look up the grammar for this segment
        // let grammar_opt = self.get_segment_grammar(name);
        let grammar_opt: Option<Arc<Grammar>> = None;

        match grammar_opt {
            Some(child_grammar) => {
                // Get segment type for later wrapping
                // let segment_type = self.dialect.get_segment_type(name).map(|s| s.to_string());
                let segment_type = None;

                // Create child frame to parse the target grammar
                let child_frame_id = stack.frame_id_counter;
                stack.increment_frame_id_counter();

                // Clone child_grammar for debug log before moving it into child_frame
                let child_grammar_for_debug = child_grammar.clone();

                log::debug!(
                    "DEBUG Ref frame_id={} creating child frame_id={} with parent_max_idx={:?}",
                    frame.frame_id,
                    child_frame_id,
                    frame.parent_max_idx
                );

                let mut child_frame = ParseFrame {
                    frame_id: child_frame_id,
                    grammar: child_grammar,
                    pos: self.pos,
                    terminators: all_terminators,
                    state: FrameState::Initial,
                    accumulated: vec![],
                    context: FrameContext::None,
                    parent_max_idx: frame.parent_max_idx, // CRITICAL: Propagate parent's limit
                    end_pos: None,
                    transparent_positions: None,
                    element_key: None,
                    grammar_id: None,
                    table_terminators: vec![],
                };

                // Update current frame to wait for child and store Ref metadata
                frame.state = FrameState::WaitingForChild {
                    child_index: 0,
                    total_children: 1,
                };
                frame.context = FrameContext::Ref {
                    grammar: grammar.clone(),
                    segment_type,
                    saved_pos: saved,
                    last_child_frame_id: Some(child_frame_id), // Track the child we just created
                    leading_transparent: vec![], // Empty - Sequence handles transparent tokens
                };

                // Push parent back first, then child (LIFO - child will be processed next)
                log::debug!(
                    "[REF PUSH] frame_id={}, name={}, pushing parent back onto stack",
                    frame.frame_id,
                    name
                );
                stack.push(&mut frame);

                log::debug!("DEBUG [iter {}]: Ref({}) frame_id={} creating child frame_id={}, child grammar type: {}",
                    iteration_count,
                    name,
                    stack.last_mut().unwrap().frame_id,
                    child_frame_id,
                    match child_grammar_for_debug.as_ref() {
                        Grammar::Ref { name, .. } => format!("Ref({})", name),
                        Grammar::Token { token_type } => format!("Token({})", token_type),
                        Grammar::Sequence { elements, .. } => format!("Sequence({} elements)", elements.len()),
                        Grammar::OneOf { elements, .. } => format!("OneOf({} elements)", elements.len()),
                        _ => format!("{:?}", child_grammar_for_debug),
                    }
                );

                stack.push(&mut child_frame);
                log::debug!("DEBUG [iter {}]: ABOUT TO CONTINUE - Ref({}) pushed child {}, stack size now {}",
                    iteration_count, name, child_frame_id, stack.len());
                log::debug!(
                    "DEBUG [iter {}]: ==> CONTINUING 'MAIN_LOOP NOW! <==",
                    iteration_count
                );
                Ok(FrameResult::Done) // Signal caller to continue main loop
            }
            None => {
                self.pos = saved;
                if *optional {
                    log::debug!("Iterative Ref optional (grammar not found), skipping");
                    stack
                        .results
                        .insert(frame.frame_id, (Node::Empty, saved, None));
                    Ok(FrameResult::Done) // Don't continue, we stored a result
                } else {
                    log::debug!("Iterative Ref failed (grammar not found), returning error");
                    Err(ParseError::unknown_segment(
                        name.to_string(),
                        Some(self.pos),
                    ))
                }
            }
        }
    }

    /// Handle Ref grammar WaitingForChild state in iterative parser
    pub(crate) fn handle_ref_waiting_for_child(
        &mut self,
        mut frame: ParseFrame,
        child_node: &Node,
        child_end_pos: &usize,
        stack: &mut ParseFrameStack,
    ) -> Result<FrameResult, ParseError> {
        log::debug!(
            "[REF WAITING] frame_id={}, child_end_pos={}, child_empty={}",
            frame.frame_id,
            child_end_pos,
            child_node.is_empty()
        );

        let FrameContext::Ref {
            grammar,
            segment_type,
            saved_pos,
            last_child_frame_id,
            leading_transparent: _,
            ..
        } = &mut frame.context
        else {
            panic!("Expected FrameContext::Ref in handle_ref_waiting_for_child");
        };

        let Grammar::Ref { name, .. } = grammar.as_ref() else {
            panic!("Expected Grammar::Ref in FrameContext::Ref");
        };

        // Wrap the child node in a Ref node
        let final_node = if child_node.is_empty() {
            if grammar.is_optional() {
                log::debug!("Ref {} returned empty (optional), accepting", name);
                child_node.clone()
            } else {
                log::debug!("Ref {} returned empty (not optional), backtracking", name);
                self.pos = *saved_pos;
                child_node.clone()
            }
        } else {
            log::debug!("MATCHED Ref {} successfully", name);
            Node::Ref {
                name: name.to_string(),
                segment_type: segment_type.clone(),
                child: Box::new(child_node.clone()),
            }
        };

        // CRITICAL: When child returns Empty, position should not advance beyond saved_pos.
        // In Python, an empty MatchResult has slice(idx, idx) - zero length.
        // If child_end_pos > saved_pos, the child consumed tokens before returning Empty,
        // which is a bug. We need to ensure the result position is saved_pos in this case.
        //
        // CRITICAL: When child returns non-empty, strip trailing whitespace from child_end_pos.
        // Child grammars with allow_gaps=True may consume trailing whitespace, but Ref should
        // only report the position after actual content, not trailing whitespace. The parent
        // Sequence will handle whitespace between elements using its own allow_gaps logic.
        let result_pos = if child_node.is_empty() {
            // Empty result: use saved_pos (no advancement)
            if *child_end_pos != *saved_pos {
                log::warn!(
                    "[REF BUG] Ref({}) child returned Empty with child_end_pos={} != saved_pos={}. Correcting to saved_pos.",
                    name, child_end_pos, saved_pos
                );
            }
            *saved_pos
        } else {
            // Non-empty result: strip trailing whitespace from child_end_pos
            // This ensures that only the actual matched content is included, not trailing whitespace
            // that the child may have consumed due to its allow_gaps setting.
            log::debug!(
                "[REF STRIP PRE] Ref({}) before strip: saved_pos={}, child_end_pos={}",
                name,
                saved_pos,
                child_end_pos
            );

            let stripped_pos = crate::parser::utils::strip_trailing_non_code(
                self.tokens,
                *saved_pos,
                *child_end_pos,
            );

            log::debug!(
                "[REF STRIP POST] Ref({}) after strip: stripped_pos={}",
                name,
                stripped_pos
            );

            if stripped_pos != *child_end_pos {
                log::debug!(
                    "[REF STRIP] Ref({}) stripping trailing whitespace: child_end_pos={} -> {}",
                    name,
                    child_end_pos,
                    stripped_pos
                );
            }

            stripped_pos
        };

        self.pos = result_pos;
        log::debug!("[REF CHILD] frame_id={}, name={}, child_empty={}, saved_pos={}, child_end_pos={}, result_pos={}, setting self.pos={}",
            frame.frame_id, name, child_node.is_empty(), saved_pos, child_end_pos, result_pos, self.pos);

        // Store Ref result in cache for future reuse
        // Use frame's parent_max_idx if available, otherwise tokens.len()
        let max_idx = frame.parent_max_idx.unwrap_or(self.tokens.len());
        let cache_key = CacheKey::new(
            *saved_pos,
            frame.grammar.clone(),
            self.tokens,
            max_idx,
            &frame.terminators,
            &mut self.grammar_hash_cache,
        );
        // Get transparent positions from the child's result in stack, not from the global set.
        // This avoids double-marking when the cache is later retrieved.
        let transparent_positions: Vec<usize> = if let Some(child_frame_id) = last_child_frame_id {
            stack
                .transparent_positions
                .get(child_frame_id)
                .cloned()
                .unwrap_or_default()
        } else {
            Vec::new()
        };

        log::debug!(
            "Storing Ref({}) result in cache: pos {} -> {}, {} transparent positions",
            name,
            *saved_pos,
            result_pos,
            transparent_positions.len()
        );

        self.parse_cache.put(
            cache_key,
            Ok((
                final_node.clone(),
                result_pos,
                transparent_positions.clone(),
            )),
        );

        log::debug!(
            "[REF RESULT] frame_id={}, name={}, storing accumulated result, transitioning to Combining",
            frame.frame_id,
            name
        );

        // Store the final node and result position in frame for Combining state
        frame.accumulated = vec![final_node];
        frame.end_pos = Some(result_pos);

        // Store transparent positions in frame for Combining to use
        frame.transparent_positions = Some(transparent_positions);

        // Transition to Combining state
        frame.state = FrameState::Combining;

        // Return frame to be pushed back onto stack so Combining handler can process it
        Ok(FrameResult::Push(frame))
    }

    /// Handle Ref combining - build final result after child completes
    pub(crate) fn handle_ref_combining(
        &mut self,
        mut frame: ParseFrame,
    ) -> Result<FrameResult, ParseError> {
        let FrameContext::Ref {
            grammar, saved_pos, ..
        } = &frame.context
        else {
            return Err(ParseError::new(
                "Expected FrameContext::Ref in handle_ref_combining".to_string(),
            ));
        };

        let Grammar::Ref { name, .. } = grammar.as_ref() else {
            return Err(ParseError::new(
                "Expected Grammar::Ref in FrameContext::Ref".to_string(),
            ));
        };

        // Get the final node from accumulated (should be exactly one)
        if frame.accumulated.len() != 1 {
            return Err(ParseError::new(format!(
                "Ref combining expected 1 accumulated node, got {}",
                frame.accumulated.len()
            )));
        }

        let final_node = frame.accumulated[0].clone();
        let result_pos = frame.end_pos.unwrap_or(*saved_pos);

        log::debug!(
            "[REF COMBINING] frame_id={}, name={}, result_pos={}, empty={}",
            frame.frame_id,
            name,
            result_pos,
            final_node.is_empty()
        );

        // Store result in cache
        let max_idx = frame.parent_max_idx.unwrap_or(self.tokens.len());
        let cache_key = CacheKey::new(
            *saved_pos,
            frame.grammar.clone(),
            self.tokens,
            max_idx,
            &frame.terminators,
            &mut self.grammar_hash_cache,
        );

        let transparent_positions = frame.transparent_positions.clone().unwrap_or_default();

        log::debug!(
            "Storing Ref({}) result in cache: pos {} -> {}, {} transparent positions",
            name,
            *saved_pos,
            result_pos,
            transparent_positions.len()
        );

        self.parse_cache.put(
            cache_key,
            Ok((final_node.clone(), result_pos, transparent_positions)),
        );

        // Update parser position
        self.pos = result_pos;

        // Transition to Complete state
        frame.state = FrameState::Complete(final_node);
        frame.end_pos = Some(result_pos);

        Ok(FrameResult::Push(frame))
    }

    /// Handle NonCodeMatcher grammar in iterative parser
    pub fn handle_noncode_matcher_initial(
        &mut self,
        frame: &ParseFrame,
        results: &mut HashMap<usize, (Node, usize, Option<u64>)>,
    ) -> Result<FrameResult, ParseError> {
        log::debug!(
            "START NonCodeMatcher: frame_id={}, pos={}",
            frame.frame_id,
            frame.pos
        );
        self.pos = frame.pos;
        if let Some(tok) = self.peek() {
            let typ = tok.get_type();
            if typ == "whitespace" || typ == "newline" {
                results.insert(
                    frame.frame_id,
                    (
                        Node::Token {
                            token_type: typ.to_string(),
                            raw: tok.raw().to_string(),
                            token_idx: self.pos,
                        },
                        self.pos + 1,
                        None,
                    ),
                );
                self.bump();
                return Ok(FrameResult::Done);
            }
        }
        // No match
        results.insert(frame.frame_id, (Node::Empty, frame.pos, None));
        Ok(FrameResult::Done)
    }
}

#[cfg(test)]
mod table_driven_anything_tests {
    use super::*;
    use crate::parser::Parser;
    use env_logger;
    use sqlfluffrs_dialects::dialect::ansi::parser::get_ansi_segment_grammar;
    use sqlfluffrs_dialects::Dialect;
    use sqlfluffrs_lexer::{LexInput, Lexer};

    // Smoke test: ensure bracketed tokens are preserved properly by table-driven Anything
    #[test]
    fn table_driven_anything_bracket_persistence() {
        let _ = env_logger::builder().is_test(true).try_init();

        // SQL with different bracket types
        let sql = "FOO VARCHAR(100)";
        let dialect = Dialect::Ansi;

        // Choose a root grammar that will exercise expression/bracket parsing
        let lexer = Lexer::new(None, dialect.get_lexers().to_vec());
        let (tokens, _violations) = lexer.lex(LexInput::String(sql.to_string()), true);

        // Create parser using the RootGrammar (table-driven)
        let mut parser = Parser::new_with_tables(&tokens, dialect);
        let node = parser
            .call_rule("ColumnDefinitionSegment", &[])
            .expect("parse_root should not error");

        // Basic assertions: parse should be non-empty and contain bracketed nodes
        assert!(!node.is_empty(), "Expected non-empty parse");

        // Walk tree and ensure we find at least one Bracketed node with expected persistence
        fn find_bracketed(n: &crate::parser::Node) -> Option<(bool, Vec<String>)> {
            use crate::parser::Node;
            match n {
                Node::Bracketed {
                    children: _,
                    bracket_persists,
                } => {
                    // We don't check contents here, just the persistence flag
                    return Some((*bracket_persists, vec![]));
                }
                Node::Sequence { children } | Node::DelimitedList { children } => {
                    for c in children {
                        if let Some(found) = find_bracketed(c) {
                            return Some(found);
                        }
                    }
                    None
                }
                Node::Ref { child, .. } => find_bracketed(child),
                _ => None,
            }
        }

        let found = find_bracketed(&node);
        assert!(
            found.is_some(),
            "Expected to find a Bracketed node in parse tree"
        );
    }

    // Test: parent terminator stops Anything from consuming beyond terminator
    #[test]
    fn table_driven_anything_parent_terminator() {
        let _ = env_logger::builder().is_test(true).try_init();

        // SQL where the keyword END should act as a terminator
        let sql = "foo bar baz END trailing";
        let dialect = Dialect::Ansi;

        // Use SelectClauseSegment as a root that will have terminators including keywords
        let root = get_ansi_segment_grammar("SelectClauseSegment")
            .expect("SelectClauseSegment not found in ANSI tables");

        let lexer = Lexer::new(None, dialect.get_lexers().to_vec());
        let (tokens, _violations) = lexer.lex(LexInput::String(sql.to_string()), true);

        let mut parser = Parser::new_with_root(&tokens, dialect, root);
        let node = parser
            .call_rule_as_root()
            .expect("parse_root should not error");

        // Ensure parse consumed only up to END (i.e., trailing token remains unconsumed)
        // We check that at least one Token node with raw == "trailing" still exists in tokens
        // but not inside the parsed node.
        let trailing_in_parse = format!("trailing");

        fn contains_raw(n: &crate::parser::Node, raw: &str) -> bool {
            use crate::parser::Node;
            match n {
                Node::Token { raw: r, .. } => r == raw,
                Node::Sequence { children } | Node::DelimitedList { children } => {
                    children.iter().any(|c| contains_raw(c, raw))
                }
                Node::Bracketed { children, .. } => children.iter().any(|c| contains_raw(c, raw)),
                Node::Ref { child, .. } => contains_raw(child, raw),
                _ => false,
            }
        }

        assert!(
            !contains_raw(&node, &trailing_in_parse),
            "Expected trailing token not to be consumed by root parse"
        );
    }
}
