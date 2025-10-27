//! Iterative Parser Implementation
//!
//! This module contains the iterative (stack-based) parser implementation
//! that avoids deep recursion by using an explicit frame stack.
//!
//! The iterative parser processes grammars by maintaining a stack of ParseFrames,
//! each representing a parsing state. This approach prevents stack overflow on
//! deeply nested or complex SQL grammars.

pub enum NextStep {
    Continue,
    Break,
    Fallthrough,
}
/// Stack structure for managing ParseFrames and related state
pub struct ParseFrameStack {
    stack: Vec<ParseFrame>,
    pub results: hashbrown::HashMap<usize, (Node, usize, Option<u64>)>,
    pub frame_id_counter: usize,
    // Add any additional state fields here as needed
}

impl Default for ParseFrameStack {
    fn default() -> Self {
        Self::new()
    }
}

impl ParseFrameStack {
    pub fn new() -> Self {
        ParseFrameStack {
            stack: Vec::new(),
            results: hashbrown::HashMap::new(),
            frame_id_counter: 0,
        }
    }

    pub fn push(&mut self, frame: &mut ParseFrame) {
        self.stack.push(frame.clone());
    }

    pub fn pop(&mut self) -> Option<ParseFrame> {
        self.stack.pop()
    }

    pub fn len(&self) -> usize {
        self.stack.len()
    }

    pub fn is_empty(&self) -> bool {
        self.stack.is_empty()
    }

    pub fn last_mut(&mut self) -> Option<&mut ParseFrame> {
        self.stack.last_mut()
    }

    pub fn iter(&'_ self) -> std::slice::Iter<'_, ParseFrame> {
        self.stack.iter()
    }

    pub fn increment_frame_id_counter(&mut self) {
        self.frame_id_counter += 1;
    }

    // Add more helper methods as needed for dispatch or state management
}

use std::sync::Arc;

use super::{FrameContext, FrameState, Node, ParseError, ParseFrame};

// Import Parser from core module
use super::core::Parser;

use sqlfluffrs_types::Grammar;

impl Parser<'_> {
    // ========================================================================
    // Iterative Parser Helper Functions
    // ========================================================================
    //
    // These helper functions handle each grammar type in the iterative parser.
    // Each function processes Initial state for a specific grammar type,
    // inserting results or pushing new frames as needed.

    // Handler for FrameState::Initial
    fn handle_frame_initial(
        &mut self,
        frame: &mut ParseFrame,
        stack: &mut ParseFrameStack,
        iteration_count: usize,
    ) -> Result<NextStep, ParseError> {
        let grammar = frame.grammar.clone();
        let terminators = frame.terminators.clone();

        match grammar.as_ref() {
            // Simple leaf grammars - parse directly without recursion
            Grammar::Token { .. } => {
                self.handle_token_initial(grammar, frame, &mut stack.results)?;
                Ok(NextStep::Fallthrough)
            }

            Grammar::StringParser { .. } => self.handle_string_parser_initial(
                grammar,
                frame,
                iteration_count,
                &mut stack.results,
            ),

            Grammar::MultiStringParser { .. } => {
                self.handle_multi_string_parser_initial(grammar, frame, &mut stack.results)
            }

            Grammar::TypedParser { .. } => {
                self.handle_typed_parser_initial(grammar, frame, &mut stack.results)
            }

            Grammar::RegexParser { .. } => {
                self.handle_regex_parser_initial(grammar, frame, &mut stack.results)
            }

            Grammar::Meta(_) => self.handle_meta_initial(grammar, frame, &mut stack.results),

            Grammar::Nothing() => self.handle_nothing_initial(frame, &mut stack.results),

            Grammar::Empty => self.handle_empty_initial(frame, &mut stack.results),

            Grammar::Missing => self.handle_missing_initial(),

            Grammar::Anything => {
                self.handle_anything_initial(frame, &terminators, &mut stack.results)
            }

            // Complex grammars - need special handling
            Grammar::Sequence { .. } => {
                self.handle_sequence_initial(grammar, frame, &terminators, &mut *stack)
            }

            Grammar::OneOf { .. } => self.handle_oneof_initial(grammar, frame, &terminators, stack),

            Grammar::Ref { .. } => {
                self.handle_ref_initial(grammar, frame, &terminators, stack, iteration_count)
            }

            Grammar::AnyNumberOf { .. } => self.handle_anynumberof_initial(
                grammar,
                frame,
                &terminators,
                stack,
                iteration_count,
            ),

            Grammar::Bracketed { .. } => {
                self.handle_bracketed_initial(grammar, frame, &terminators, stack)
            }

            Grammar::AnySetOf { .. } => {
                self.handle_anysetof_initial(grammar, frame, &terminators, stack)
            }

            Grammar::Delimited { .. } => {
                self.handle_delimited_initial(grammar, frame, &terminators, stack)
            }
        }
    }

    // ========================================================================
    // Main Iterative Parser
    // ========================================================================

    /// Fully iterative parser using explicit stack
    ///
    /// This replaces recursive `parse_with_grammar` calls with an explicit
    /// stack-based state machine to avoid stack overflow on deeply nested grammars.
    pub fn parse_iterative(
        &mut self,
        grammar: Arc<Grammar>,
        parent_terminators: &[Arc<Grammar>],
    ) -> Result<Node, ParseError> {
        use super::cache::CacheKey;

        log::debug!(
            "Starting iterative parse for grammar: {} at pos {}",
            grammar,
            self.pos
        );

        // Check cache first, unless disabled
        let start_pos = self.pos;
        let grammar_for_log = grammar.clone();
        let grammar_for_cache = grammar.clone();
        let cache_key = CacheKey::new(
            start_pos,
            grammar_for_cache,
            self.tokens,
            parent_terminators,
            &mut self.grammar_hash_cache,
        );

        if self.cache_enabled {
            if let Some(cached_result) = self.parse_cache.get(&cache_key) {
                match cached_result {
                    Ok((node, end_pos, transparent_positions)) => {
                        log::debug!(
                            "Cache HIT for grammar {} at pos {} -> end_pos {}",
                            grammar_for_log,
                            start_pos,
                            end_pos
                        );

                        // Restore parser position and transparent positions
                        self.pos = end_pos;
                        for &pos in &transparent_positions {
                            self.collected_transparent_positions.insert(pos);
                        }

                        return Ok(node);
                    }
                    Err(e) => {
                        log::debug!(
                            "Cache HIT (error) for grammar {} at pos {}",
                            grammar_for_log,
                            start_pos
                        );
                        return Err(e);
                    }
                }
            }
        }

        // Stack of parse frames and state
        let mut stack = ParseFrameStack::new();
        let initial_frame_id = stack.frame_id_counter;
        stack.frame_id_counter += 1;
        stack.push(&mut ParseFrame {
            frame_id: initial_frame_id,
            grammar: grammar,
            pos: self.pos,
            terminators: parent_terminators.to_vec(),
            state: FrameState::Initial,
            accumulated: vec![],
            context: FrameContext::None,
            parent_max_idx: None, // Top-level frame has no parent limit
        });

        let mut iteration_count = 0_usize;
        let max_iterations = 1500000_usize; // Higher limit for complex grammars

        'main_loop: while let Some(mut frame) = stack.pop() {
            iteration_count += 1;

            // Re-check the cache for this frame before processing, unless disabled
            if self.cache_enabled {
                let cache_key = CacheKey::new(
                    frame.pos,
                    frame.grammar.clone(),
                    self.tokens,
                    &frame.terminators,
                    &mut self.grammar_hash_cache,
                );
                if let Some(cached_result) = self.parse_cache.get(&cache_key) {
                    match cached_result {
                        Ok((node, end_pos, transparent_positions)) => {
                            log::debug!(
                                "[LOOP] Cache HIT for grammar {} at pos {} -> end_pos {} (frame_id={})",
                                frame.grammar,
                                frame.pos,
                                end_pos,
                                frame.frame_id
                            );
                            self.pos = end_pos;
                            for &pos in &transparent_positions {
                                self.collected_transparent_positions.insert(pos);
                            }
                            stack.results.insert(frame.frame_id, (node, end_pos, None));
                            continue 'main_loop;
                        }
                        Err(_e) => {
                            log::debug!(
                                "[LOOP] Cache HIT (error) for grammar {} at pos {} (frame_id={})",
                                frame.grammar,
                                frame.pos,
                                frame.frame_id
                            );
                            stack
                                .results
                                .insert(frame.frame_id, (Node::Empty, frame.pos, None));
                            continue 'main_loop;
                        }
                    }
                }
            }

            if iteration_count > max_iterations {
                eprintln!("ERROR: Exceeded max iterations ({})", max_iterations);
                eprintln!("Last frame: {:?}", frame.grammar);
                eprintln!("Stack depth: {}", stack.len());
                eprintln!("Results count: {}", stack.results.len());

                // Print last 20 frames on stack for diagnosis
                eprintln!("\n=== Last 20 frames on stack ===");
                for (i, f) in stack.iter().rev().take(20).enumerate() {
                    eprintln!(
                        "  [{}] state={:?}, pos={}, grammar={}",
                        i,
                        f.state,
                        f.pos,
                        match f.grammar.as_ref() {
                            Grammar::Ref { name, .. } => format!("Ref({})", name),
                            Grammar::Bracketed { .. } => "Bracketed".to_string(),
                            Grammar::Delimited { .. } => "Delimited".to_string(),
                            Grammar::OneOf { elements, .. } =>
                                format!("OneOf({} elements)", elements.len()),
                            Grammar::Sequence { elements, .. } =>
                                format!("Sequence({} elements)", elements.len()),
                            Grammar::AnyNumberOf { .. } => "AnyNumberOf".to_string(),
                            Grammar::AnySetOf { .. } => "AnySetOf".to_string(),
                            _ => "Other".to_string(),
                        }
                    );
                }

                self.print_cache_stats();

                panic!("Infinite loop detected in iterative parser");
            }

            // Debug: Show what frame we're processing periodically
            if iteration_count.is_multiple_of(5000) {
                log::debug!(
                    "\nDEBUG [iter {}]: Processing frame_id={}, state={:?}",
                    iteration_count,
                    frame.frame_id,
                    frame.state
                );
                log::debug!(
                    "  Stack size: {}, Results size: {}",
                    stack.len(),
                    stack.results.len()
                );
                match frame.grammar.as_ref() {
                    Grammar::Ref { name, .. } => log::debug!("  Grammar: Ref({})", name),
                    Grammar::Token { token_type } => {
                        log::debug!("  Grammar: Token({})", token_type)
                    }
                    g => log::debug!("  Grammar: {:?}", g),
                }
            }

            log::debug!(
                "Processing frame {}: grammar={}, pos={}, state={:?}, stack_size={} (BEFORE pop: {})",
                frame.frame_id,
                frame.grammar,
                frame.pos,
                frame.state,
                stack.len(),
                stack.len() + 1  // Add 1 because we just popped
            );

            match frame.state {
                FrameState::Initial => {
                    match self.handle_frame_initial(&mut frame, &mut stack, iteration_count)? {
                        NextStep::Continue => continue 'main_loop,
                        NextStep::Break => break 'main_loop,
                        _ => (),
                    }
                }
                FrameState::WaitingForChild {
                    child_index,
                    total_children,
                } => {
                    // A child parse just completed - get its result
                    // First get the child frame ID we're waiting for
                    let child_frame_id = match &frame.context {
                        FrameContext::Ref {
                            last_child_frame_id,
                            ..
                        } => last_child_frame_id
                            .expect("Ref WaitingForChild should have last_child_frame_id set"),
                        FrameContext::Sequence {
                            last_child_frame_id,
                            ..
                        } => last_child_frame_id
                            .expect("Sequence WaitingForChild should have last_child_frame_id set"),
                        FrameContext::AnyNumberOf {
                            last_child_frame_id,
                            ..
                        } => last_child_frame_id.expect(
                            "AnyNumberOf WaitingForChild should have last_child_frame_id set",
                        ),
                        FrameContext::OneOf {
                            last_child_frame_id,
                            ..
                        } => last_child_frame_id
                            .expect("OneOf WaitingForChild should have last_child_frame_id set"),
                        FrameContext::Bracketed {
                            last_child_frame_id,
                            ..
                        } => last_child_frame_id.expect(
                            "Bracketed WaitingForChild should have last_child_frame_id set",
                        ),
                        FrameContext::AnySetOf {
                            last_child_frame_id,
                            ..
                        } => last_child_frame_id
                            .expect("AnySetOf WaitingForChild should have last_child_frame_id set"),
                        FrameContext::Delimited {
                            last_child_frame_id,
                            ..
                        } => last_child_frame_id.expect(
                            "Delimited WaitingForChild should have last_child_frame_id set",
                        ),
                        _ => {
                            log::error!("WaitingForChild state without child frame ID tracking");
                            continue;
                        }
                    };

                    let child = stack.results.get(&child_frame_id).cloned();

                    if let Some((child_node, child_end_pos, child_element_key)) = &child {
                        log::debug!(
                            "Child {} of {} completed (frame_id={}): pos {} -> {}",
                            child_index,
                            total_children,
                            child_frame_id,
                            frame.pos,
                            child_end_pos
                        );

                        // Debug: Show when we find a child result
                        if iteration_count.is_multiple_of(100) || iteration_count < 200 {
                            log::debug!(
                                "DEBUG [iter {}]: Frame {} found child {} result, grammar: {:?}",
                                iteration_count,
                                frame.frame_id,
                                child_frame_id,
                                match frame.grammar.as_ref() {
                                    Grammar::Ref { name, .. } => format!("Ref({})", name),
                                    _ => format!("{:?}", frame.grammar),
                                }
                            );
                        }

                        // Extract frame data we'll need before borrowing
                        let frame_terminators = frame.terminators.clone();

                        match &mut frame.context {
                            FrameContext::Ref { .. } => {
                                self.handle_ref_waiting_for_child(
                                    &mut frame,
                                    &child_node,
                                    &child_end_pos,
                                    &mut stack,
                                );
                                continue 'main_loop; // Frame is complete, move to next frame
                            }

                            FrameContext::Sequence { .. } => {
                                self.handle_sequence_waiting_for_child(
                                    &mut frame,
                                    &child_node,
                                    &child_end_pos,
                                    &mut stack,
                                    iteration_count,
                                    frame_terminators,
                                );
                                continue 'main_loop;
                            }

                            FrameContext::AnyNumberOf { .. } => {
                                self.handle_anynumberof_waiting_for_child(
                                    &mut frame,
                                    &child_node,
                                    &child_end_pos,
                                    &child_element_key,
                                    &mut stack,
                                    iteration_count,
                                    frame_terminators,
                                );
                                continue 'main_loop;
                            }

                            FrameContext::Bracketed { .. } => {
                                self.handle_bracketed_waiting_for_child(
                                    &mut frame,
                                    &child_node,
                                    &child_end_pos,
                                    &mut stack,
                                );
                                continue 'main_loop;
                            }

                            FrameContext::AnySetOf {
                                count, matched_idx, ..
                            } => {
                                log::debug!("[ITERATIVE] AnySetOf WaitingForChild: count={}, matched_idx={}", count, matched_idx);
                                // Call the new function
                                self.handle_anysetof_waiting_for_child(
                                    &mut frame,
                                    &child_node,
                                    &child_end_pos,
                                    &child_element_key,
                                    &mut stack,
                                    frame_terminators,
                                )?;
                                continue 'main_loop;
                            }

                            FrameContext::OneOf { .. } => {
                                self.handle_oneof_waiting_for_child(
                                    &mut frame,
                                    &child_node,
                                    &child_end_pos,
                                    &child_element_key,
                                    &mut stack,
                                    frame_terminators,
                                );
                                continue 'main_loop;
                            }

                            FrameContext::Delimited { .. } => {
                                self.handle_delimited_waiting_for_child(
                                    &mut frame,
                                    &child_node,
                                    &child_end_pos,
                                    &child_element_key,
                                    &mut stack,
                                    frame_terminators,
                                );
                                continue 'main_loop;
                            }

                            _ => {
                                // TODO: Handle other grammar types
                                unimplemented!(
                                    "WaitingForChild for grammar type: {:?}",
                                    frame.grammar
                                );
                            }
                        }
                    } else {
                        // Child result not found yet - push frame back onto stack and continue
                        let child_id_str = match &frame.context {
                            FrameContext::Ref {
                                last_child_frame_id,
                                ..
                            } => format!("{:?}", last_child_frame_id),
                            FrameContext::Sequence {
                                last_child_frame_id,
                                ..
                            } => format!("{:?}", last_child_frame_id),
                            FrameContext::AnyNumberOf {
                                last_child_frame_id,
                                ..
                            } => format!("{:?}", last_child_frame_id),
                            FrameContext::OneOf {
                                last_child_frame_id,
                                ..
                            } => format!("{:?}", last_child_frame_id),
                            FrameContext::Bracketed {
                                last_child_frame_id,
                                ..
                            } => format!("{:?}", last_child_frame_id),
                            FrameContext::AnySetOf {
                                last_child_frame_id,
                                ..
                            } => format!("{:?}", last_child_frame_id),
                            FrameContext::Delimited {
                                last_child_frame_id,
                                ..
                            } => format!("{:?}", last_child_frame_id),
                            _ => "None".to_string(),
                        };
                        log::debug!(
                            "Child result not found for frame_id={}, last_child_frame_id={}, pushing frame back onto stack",
                            frame.frame_id,
                            child_id_str
                        );

                        // Check if we're in an infinite loop - frame waiting for child that doesn't exist
                        if iteration_count > 100 && iteration_count.is_multiple_of(100) {
                            log::debug!("WARNING: Frame {} waiting for child {} but result not found (iteration {})",
                                frame.frame_id, child_id_str, iteration_count);

                            // Check if child is on stack
                            if let Ok(child_id) = child_id_str.parse::<usize>() {
                                let child_on_stack = stack.iter().any(|f| f.frame_id == child_id);
                                if child_on_stack {
                                    log::debug!(
                                        "  -> Child frame {} IS on stack (still being processed)",
                                        child_id
                                    );
                                } else {
                                    log::debug!("  -> Child frame {} NOT on stack (may have been lost or never created)", child_id);
                                }
                            }
                        }

                        // Push frame back onto stack so it can be re-checked after child completes
                        // NOTE: We push (not insert at 0) so LIFO order is maintained
                        stack.push(&mut frame);
                        continue;
                    }
                }

                FrameState::Combining => {
                    // TODO: Handle combining stack.results
                    unimplemented!("Combining state not yet implemented");
                }

                FrameState::Complete(node) => {
                    // This frame is done
                    stack.results.insert(frame.frame_id, (node, self.pos, None));
                }
            }
        }

        // Return the result from the initial frame
        log::debug!("DEBUG: Main loop ended. Stack has {} frames left. Results has {} entries. Looking for frame_id={}",
            stack.len(),
            stack.results.len(),
            initial_frame_id
        );

        // Debug: Show what frames are left on the stack
        for (i, frame) in stack.iter().enumerate() {
            let grammar_desc = match frame.grammar.as_ref() {
                Grammar::Ref { name, .. } => format!("Ref({})", name),
                Grammar::Bracketed { .. } => "Bracketed".to_string(),
                Grammar::Delimited { .. } => "Delimited".to_string(),
                Grammar::OneOf { elements, .. } => format!("OneOf({} elements)", elements.len()),
                Grammar::Sequence { elements, .. } => {
                    format!("Sequence({} elements)", elements.len())
                }
                Grammar::AnyNumberOf { .. } => "AnyNumberOf".to_string(),
                Grammar::AnySetOf { .. } => "AnySetOf".to_string(),
                Grammar::StringParser { template, .. } => format!("StringParser('{}')", template),
                Grammar::Token { token_type } => format!("Token({})", token_type),
                _ => "Other".to_string(),
            };

            // Also show which child frame ID we're waiting for
            let waiting_for = match &frame.context {
                FrameContext::Ref {
                    last_child_frame_id,
                    ..
                } => format!("{:?}", last_child_frame_id),
                FrameContext::Sequence {
                    last_child_frame_id,
                    ..
                } => format!("{:?}", last_child_frame_id),
                FrameContext::OneOf {
                    last_child_frame_id,
                    ..
                } => format!("{:?}", last_child_frame_id),
                FrameContext::Delimited {
                    last_child_frame_id,
                    ..
                } => format!("{:?}", last_child_frame_id),
                FrameContext::Bracketed {
                    last_child_frame_id,
                    ..
                } => format!("{:?}", last_child_frame_id),
                FrameContext::AnySetOf {
                    last_child_frame_id,
                    ..
                } => format!("{:?}", last_child_frame_id),
                FrameContext::AnyNumberOf {
                    last_child_frame_id,
                    ..
                } => format!("{:?}", last_child_frame_id),
                _ => "None".to_string(),
            };

            log::debug!(
                "  Stack[{}]: frame_id={}, state={:?}, pos={}, grammar={}, waiting_for={}",
                i,
                frame.frame_id,
                frame.state,
                frame.pos,
                grammar_desc,
                waiting_for
            );
        }

        log::debug!(
            "Main loop ended. Stack empty. Results has {} entries. Looking for frame_id={}",
            stack.results.len(),
            initial_frame_id
        );
        for (fid, (_node, _pos, _key)) in stack.results.iter() {
            log::debug!("  Result frame_id={}", fid);
        }
        if let Some((node, end_pos, _element_key)) = stack.results.get(&initial_frame_id) {
            log::debug!(
                "DEBUG: Found result for frame_id={}, end_pos={}",
                initial_frame_id,
                end_pos
            );
            self.pos = *end_pos;

            // If the parse failed (returned Empty), provide diagnostic information
            if node.is_empty() {
                log::debug!("\n=== PARSE FAILED ===");
                log::debug!("Parser stopped at position: {}", end_pos);
                log::debug!("Total tokens: {}", self.tokens.len());

                if *end_pos < self.tokens.len() {
                    log::debug!("\nTokens around failure point:");
                    let start = end_pos.saturating_sub(3);
                    let end = (*end_pos + 4).min(self.tokens.len());
                    for i in start..end {
                        let marker = if i == *end_pos { " <<< HERE" } else { "" };
                        if let Some(tok) = self.tokens.get(i) {
                            log::debug!(
                                "  [{}]: '{}' (type: {}){}",
                                i,
                                tok.raw(),
                                tok.get_type(),
                                marker
                            );
                        }
                    }
                }

                log::debug!("\nGrammar that failed to match:");
                log::debug!("  {}", grammar_for_log);
                log::debug!("===================\n");
            }

            // Collect transparent positions that were touched during this parse
            let transparent_positions: Vec<usize> = self
                .collected_transparent_positions
                .iter()
                .filter(|&&pos| pos >= start_pos && pos < *end_pos)
                .copied()
                .collect();

            // Store successful parse in cache
            let cache_value = Ok((node.clone(), *end_pos, transparent_positions));
            self.parse_cache.put(cache_key, cache_value);

            Ok(node.clone())
        } else {
            // Store parse error in cache
            let error = ParseError::new(format!(
                "Iterative parse produced no result (initial_frame_id={}, stack.results has {} entries)",
                initial_frame_id,
                stack.results.len()
            ));
            self.parse_cache.put(cache_key, Err(error.clone()));
            Err(error)
        }
    }
}
