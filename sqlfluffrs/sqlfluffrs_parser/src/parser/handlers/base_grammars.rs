use std::sync::Arc;

use crate::parser::cache::CacheKey;
use crate::parser::iterative::NextStep;
use crate::parser::iterative::ParseFrameStack;
use crate::parser::FrameContext;
use crate::parser::FrameState;
use crate::parser::Parser;
use crate::parser::{Node, ParseError, ParseFrame};
use hashbrown::HashMap;
use sqlfluffrs_types::Grammar;

impl Parser<'_> {
    /// Handle Empty grammar in iterative parser
    pub fn handle_empty_initial(
        &mut self,
        frame: &ParseFrame,
        results: &mut HashMap<usize, (Node, usize, Option<u64>)>,
    ) -> Result<NextStep, ParseError> {
        log::debug!(
            "START Empty: frame_id={}, pos={}",
            frame.frame_id,
            frame.pos
        );
        results.insert(frame.frame_id, (Node::Empty, frame.pos, None));
        Ok(NextStep::Fallthrough)
    }

    /// Handle Missing grammar in iterative parser
    pub fn handle_missing_initial(&mut self) -> Result<NextStep, ParseError> {
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
        frame: &ParseFrame,
        results: &mut HashMap<usize, (Node, usize, Option<u64>)>,
    ) -> Result<NextStep, ParseError> {
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
        results.insert(
            frame.frame_id,
            (
                Node::Meta {
                    token_type,
                    token_idx: None,
                },
                frame.pos,
                None,
            ),
        );
        Ok(NextStep::Fallthrough)
    }

    /// Handle Anything grammar in iterative parser
    pub fn handle_anything_initial(
        &mut self,
        frame: &ParseFrame,
        parent_terminators: &[Arc<Grammar>],
        results: &mut HashMap<usize, (Node, usize, Option<u64>)>,
    ) -> Result<NextStep, ParseError> {
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
                anything_tokens.push(Node::Token {
                    token_type: "anything".to_string(),
                    raw: tok.raw().to_string(),
                    token_idx: self.pos,
                });
                self.bump();
            }
        }

        log::debug!("Anything matched tokens: {:?}", anything_tokens);
        results.insert(
            frame.frame_id,
            (
                Node::DelimitedList {
                    children: anything_tokens,
                },
                self.pos,
                None,
            ),
        );
        Ok(NextStep::Fallthrough)
    }

    /// Handle Nothing grammar in iterative parser
    pub fn handle_nothing_initial(
        &mut self,
        frame: &ParseFrame,
        results: &mut HashMap<usize, (Node, usize, Option<u64>)>,
    ) -> Result<NextStep, ParseError> {
        log::debug!(
            "START Nothing: frame_id={}, pos={}",
            frame.frame_id,
            frame.pos
        );
        log::debug!("Nothing grammar encountered, returning Empty");
        results.insert(frame.frame_id, (Node::Empty, frame.pos, None));
        Ok(NextStep::Fallthrough)
    }

    /// Handle Ref grammar Initial state in iterative parser
    pub(crate) fn handle_ref_initial(
        &mut self,
        grammar: Arc<Grammar>,
        frame: &mut ParseFrame,
        parent_terminators: &[Arc<Grammar>],
        stack: &mut ParseFrameStack,
        iteration_count: usize,
    ) -> Result<NextStep, ParseError> {
        log::debug!(
            "START Ref: frame_id={}, pos={}, parent_max_idx={:?}, grammar={:?}",
            frame.frame_id,
            frame.pos,
            frame.parent_max_idx,
            grammar
        );
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
        if let Some(exclude_grammar) = exclude {
            let exclude_match =
                self.try_match_grammar((**exclude_grammar).clone(), frame.pos, parent_terminators);
            if exclude_match.is_ok() {
                stack
                    .results
                    .insert(frame.frame_id, (Node::Empty, frame.pos, None));
                log::debug!("exclude grammar hit: {:?}!", exclude_match);
                return Ok(NextStep::Fallthrough);
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
        let grammar_opt = self.get_segment_grammar(name);

        match grammar_opt {
            Some(child_grammar) => {
                // Get segment type for later wrapping
                let segment_type = self.dialect.get_segment_type(name).map(|s| s.to_string());

                // Create child frame to parse the target grammar
                let child_frame_id = stack.frame_id_counter;
                stack.increment_frame_id_counter();

                // Clone child_grammar for debug log before moving it into child_frame
                let child_grammar_for_debug = child_grammar.clone();

                log::debug!(
                    "DEBUG Ref frame_id={} creating child frame_id={} with parent_max_idx={:?}",
                    frame.frame_id, child_frame_id, frame.parent_max_idx
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
                eprintln!("[REF PUSH] frame_id={}, name={}, pushing parent back onto stack",
                    frame.frame_id, name);
                stack.push(frame);

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
                Ok(NextStep::Continue) // Signal caller to continue main loop
            }
            None => {
                self.pos = saved;
                if *optional {
                    log::debug!("Iterative Ref optional (grammar not found), skipping");
                    stack
                        .results
                        .insert(frame.frame_id, (Node::Empty, saved, None));
                    Ok(NextStep::Fallthrough) // Don't continue, we stored a result
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
        frame: &mut ParseFrame,
        child_node: &Node,
        child_end_pos: &usize,
        stack: &mut ParseFrameStack,
    ) {
        eprintln!("[REF WAITING] frame_id={}, child_end_pos={}, child_empty={}",
            frame.frame_id, child_end_pos, child_node.is_empty());

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

        self.pos = *child_end_pos;
        eprintln!("[REF CHILD] frame_id={}, name={}, child_end_pos={}, setting self.pos={}",
            frame.frame_id, name, child_end_pos, self.pos);

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
            stack.transparent_positions.get(child_frame_id).cloned().unwrap_or_default()
        } else {
            Vec::new()
        };

        log::debug!(
            "Storing Ref({}) result in cache: pos {} -> {}, {} transparent positions",
            name,
            *saved_pos,
            *child_end_pos,
            transparent_positions.len()
        );

        self.parse_cache.put(
            cache_key,
            Ok((final_node.clone(), self.pos, transparent_positions)),
        );

        eprintln!("[REF RESULT] frame_id={}, name={}, storing result with pos={}",
            frame.frame_id, name, self.pos);
        stack
            .results
            .insert(frame.frame_id, (final_node, self.pos, None));
    }

    /// Handle NonCodeMatcher grammar in iterative parser
    pub fn handle_noncode_matcher_initial(
        &mut self,
        frame: &ParseFrame,
        results: &mut HashMap<usize, (Node, usize, Option<u64>)>,
    ) -> Result<NextStep, ParseError> {
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
                return Ok(NextStep::Fallthrough);
            }
        }
        // No match
        results.insert(frame.frame_id, (Node::Empty, frame.pos, None));
        Ok(NextStep::Fallthrough)
    }
}
