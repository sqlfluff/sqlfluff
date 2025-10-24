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

use super::{
    BracketedState, DelimitedState, FrameContext, FrameState, Grammar, Node, ParseError,
    ParseFrame, ParseMode,
};

use super::utils::{apply_parse_mode_to_result, is_grammar_optional};

// Import Parser from core module
use super::core::Parser;

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
        // let pos = frame.pos;

        match &grammar {
            // Simple leaf grammars - parse directly without recursion
            Grammar::Token { token_type } => {
                self.handle_token_initial(token_type, frame, &mut stack.results)?;
                Ok(NextStep::Fallthrough)
            }

            Grammar::StringParser {
                template,
                token_type,
                ..
            } => self.handle_string_parser_initial(
                template,
                token_type,
                frame,
                iteration_count,
                &mut stack.results,
            ),

            Grammar::MultiStringParser {
                templates,
                token_type,
                ..
            } => self.handle_multi_string_parser_initial(
                templates,
                token_type,
                frame,
                &mut stack.results,
            ),

            Grammar::TypedParser {
                template,
                token_type,
                ..
            } => self.handle_typed_parser_initial(template, token_type, frame, &mut stack.results),

            Grammar::RegexParser {
                template,
                token_type,
                anti_template,
                ..
            } => self.handle_regex_parser_initial(
                template,
                anti_template,
                token_type,
                frame,
                &mut stack.results,
            ),

            Grammar::Meta(token_type) => {
                self.handle_meta_initial(token_type, frame, &mut stack.results)
            }

            Grammar::Nothing() => self.handle_nothing_initial(frame, &mut stack.results),

            Grammar::Empty => self.handle_empty_initial(frame, &mut stack.results),

            Grammar::Missing => self.handle_missing_initial(),

            Grammar::Anything => {
                self.handle_anything_initial(frame, &terminators, &mut stack.results)
            }

            // Complex grammars - need special handling
            Grammar::Sequence {
                elements,
                optional,
                terminators: seq_terminators,
                reset_terminators,
                allow_gaps,
                parse_mode,
            } => self.handle_sequence_initial(
                elements,
                *optional,
                seq_terminators,
                *reset_terminators,
                *allow_gaps,
                *parse_mode,
                frame,
                &terminators,
                &mut *stack,
            ),

            Grammar::OneOf {
                elements,
                exclude,
                optional,
                terminators: local_terminators,
                reset_terminators,
                allow_gaps,
                parse_mode,
            } => self.handle_oneof_initial(
                elements,
                exclude,
                *optional,
                local_terminators,
                *reset_terminators,
                *allow_gaps,
                *parse_mode,
                frame,
                &terminators,
                stack,
            ),

            Grammar::Ref {
                name,
                optional,
                allow_gaps,
                terminators: ref_terminators,
                reset_terminators,
            } => self.handle_ref_initial(
                name,
                *optional,
                *allow_gaps,
                ref_terminators,
                *reset_terminators,
                frame,
                &terminators,
                stack,
                iteration_count,
            ),

            Grammar::AnyNumberOf {
                elements,
                min_times,
                max_times,
                max_times_per_element,
                exclude,
                optional,
                terminators: any_terminators,
                reset_terminators,
                allow_gaps,
                parse_mode,
            } => self.handle_anynumberof_initial(
                elements,
                *min_times,
                *max_times,
                *max_times_per_element,
                exclude,
                *optional,
                any_terminators,
                *reset_terminators,
                *allow_gaps,
                *parse_mode,
                frame,
                &terminators,
                stack,
                iteration_count,
            ),

            Grammar::Bracketed {
                elements,
                bracket_pairs,
                optional,
                terminators: bracket_terminators,
                reset_terminators,
                allow_gaps,
                parse_mode,
            } => self.handle_bracketed_initial(
                bracket_pairs,
                elements,
                *optional,
                bracket_terminators,
                *reset_terminators,
                *allow_gaps,
                *parse_mode,
                frame,
                &terminators,
                stack,
            ),

            Grammar::AnySetOf {
                elements,
                min_times,
                max_times,
                exclude,
                optional,
                terminators: local_terminators,
                reset_terminators,
                allow_gaps,
                parse_mode,
            } => self.handle_anysetof_initial(
                elements,
                *min_times,
                *max_times,
                exclude,
                *optional,
                local_terminators,
                *reset_terminators,
                *allow_gaps,
                *parse_mode,
                frame,
                &terminators,
                stack,
            ),

            Grammar::Delimited {
                elements,
                delimiter,
                allow_trailing,
                optional,
                terminators: local_terminators,
                reset_terminators,
                allow_gaps,
                min_delimiters,
                parse_mode,
            } => self.handle_delimited_initial(
                elements,
                delimiter,
                *allow_trailing,
                *optional,
                local_terminators,
                *reset_terminators,
                *allow_gaps,
                *min_delimiters,
                *parse_mode,
                frame,
                &terminators,
                stack,
            ),
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
        grammar: &Grammar,
        parent_terminators: &[Grammar],
    ) -> Result<Node, ParseError> {
        use super::cache::CacheKey;

        log::debug!(
            "Starting iterative parse for grammar: {} at pos {}",
            grammar,
            self.pos
        );

        // Check cache first
        let start_pos = self.pos;
        let cache_key = CacheKey::new(start_pos, grammar, self.tokens, parent_terminators);

        if let Some(cached_result) = self.parse_cache.get(&cache_key) {
            match cached_result {
                Ok((node, end_pos, transparent_positions)) => {
                    log::debug!(
                        "Cache HIT for grammar {} at pos {} -> end_pos {}",
                        grammar,
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
                        grammar,
                        start_pos
                    );
                    return Err(e);
                }
            }
        }

        // Stack of parse frames and state
        let mut stack = ParseFrameStack::new();
        let initial_frame_id = stack.frame_id_counter;
        stack.frame_id_counter += 1;
        stack.push(&mut ParseFrame {
            frame_id: initial_frame_id,
            grammar: grammar.clone(),
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
                        match &f.grammar {
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
                match &frame.grammar {
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

                    if let Some((child_node, child_end_pos, child_element_key)) =
                        stack.results.get(&child_frame_id)
                    {
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
                                match &frame.grammar {
                                    Grammar::Ref { name, .. } => format!("Ref({})", name),
                                    _ => format!("{:?}", frame.grammar),
                                }
                            );
                        }

                        // Extract frame data we'll need before borrowing
                        let frame_terminators = frame.terminators.clone();

                        match &mut frame.context {
                            FrameContext::Ref {
                                name,
                                optional,
                                segment_type,
                                saved_pos,
                                last_child_frame_id: _last_child_frame_id,
                                ..
                            } => {
                                // Wrap the child node in a Ref node
                                let final_node = if child_node.is_empty() {
                                    // Empty result
                                    if *optional {
                                        log::debug!(
                                            "Ref {} returned empty (optional), accepting",
                                            name
                                        );
                                        child_node.clone()
                                    } else {
                                        log::debug!(
                                            "Ref {} returned empty (not optional), backtracking",
                                            name
                                        );
                                        self.pos = *saved_pos;
                                        child_node.clone()
                                    }
                                } else {
                                    // Successful match
                                    log::debug!("MATCHED Ref {} successfully", name);

                                    // Wrap in Ref node
                                    Node::Ref {
                                        name: name.clone(),
                                        segment_type: segment_type.clone(),
                                        child: Box::new(child_node.clone()),
                                    }
                                };

                                self.pos = *child_end_pos;

                                // Store Ref result in cache for future reuse
                                // This enables nested function calls to be cached separately
                                let cache_key = super::cache::CacheKey::new(
                                    *saved_pos,
                                    &frame.grammar,
                                    self.tokens,
                                    &frame.terminators,
                                );
                                let transparent_positions: Vec<usize> = self
                                    .collected_transparent_positions
                                    .iter()
                                    .filter(|&&pos| pos >= *saved_pos && pos < *child_end_pos)
                                    .copied()
                                    .collect();

                                log::debug!(
                                    "Storing Ref({}) result in cache: pos {} -> {}",
                                    name,
                                    *saved_pos,
                                    *child_end_pos
                                );

                                self.parse_cache.put(
                                    cache_key,
                                    Ok((final_node.clone(), self.pos, transparent_positions)),
                                );

                                stack
                                    .results
                                    .insert(frame.frame_id, (final_node, self.pos, None));
                                continue 'main_loop; // Frame is complete, move to next frame
                            }
                            FrameContext::Sequence {
                                elements,
                                allow_gaps,
                                optional: _optional,
                                parse_mode,
                                matched_idx,
                                tentatively_collected,
                                max_idx,
                                original_max_idx,
                                last_child_frame_id: _last_child_frame_id,
                                current_element_idx,
                                first_match,
                            } => {
                                let element_start = *matched_idx;

                                // Handle the child result
                                if child_node.is_empty() {
                                    // Child returned Empty - check if it's optional
                                    let current_element = &elements[*current_element_idx];
                                    if current_element.is_optional() {
                                        log::debug!("Sequence: child returned Empty and is optional, continuing");
                                        // Fall through to "move to next child" logic below
                                    } else {
                                        // Required element returned Empty - sequence fails
                                        let element_desc = match current_element {
                                            Grammar::Ref { name, .. } => format!("Ref({})", name),
                                            Grammar::StringParser { template, .. } => {
                                                format!("StringParser('{}')", template)
                                            }
                                            _ => format!("{:?}", current_element),
                                        };

                                        // Get info about what token was found
                                        let found_token = if element_start < self.tokens.len() {
                                            let tok = &self.tokens[element_start];
                                            format!("'{}' (type: {})", tok.raw(), tok.get_type())
                                        } else {
                                            "EOF".to_string()
                                        };

                                        log::debug!("WARNING: Sequence failing - required element returned Empty!");
                                        log::debug!(
                                            "  frame_id={}, element_idx={}/{}",
                                            frame.frame_id,
                                            *current_element_idx,
                                            elements.len()
                                        );
                                        log::debug!("  Expected: {}", element_desc);
                                        log::debug!(
                                            "  At position: {} (found: {})",
                                            element_start,
                                            found_token
                                        );

                                        log::debug!("Sequence: required element returned Empty, returning Empty");
                                        self.pos = frame.pos; // Reset position
                                                              // Rollback tentatively collected positions
                                        for pos in tentatively_collected.iter() {
                                            self.collected_transparent_positions.remove(pos);
                                        }
                                        stack
                                            .results
                                            .insert(frame.frame_id, (Node::Empty, frame.pos, None));
                                        continue 'main_loop; // Skip to next frame
                                    }
                                } else {
                                    // Successfully matched
                                    *matched_idx = *child_end_pos;

                                    // Add the matched node
                                    frame.accumulated.push(child_node.clone());

                                    // Handle retroactive collection for allow_gaps=false
                                    if !*allow_gaps {
                                        // Find where the element actually consumed its last code token
                                        let mut last_code_consumed = element_start;
                                        for check_pos in element_start..*matched_idx {
                                            if check_pos < self.tokens.len()
                                                && self.tokens[check_pos].is_code()
                                            {
                                                last_code_consumed = check_pos;
                                            }
                                        }

                                        // Collect ALL transparent tokens until we hit code
                                        let mut collect_end = *matched_idx;
                                        while collect_end < self.tokens.len()
                                            && !self.tokens[collect_end].is_code()
                                        {
                                            collect_end += 1;
                                        }

                                        log::debug!(
                                            "Retroactive collection for frame_id={}: element_start={}, last_code_consumed={}, matched_idx={}, collect_end={}",
                                            frame.frame_id, element_start, last_code_consumed, *matched_idx, collect_end
                                        );

                                        // Collect transparent tokens
                                        for check_pos in (last_code_consumed + 1)..collect_end {
                                            if check_pos < self.tokens.len()
                                                && !self.tokens[check_pos].is_code()
                                            {
                                                // Check if already collected OR already in this frame's accumulated
                                                let already_in_accumulated =
                                                    tentatively_collected.contains(&check_pos);
                                                let globally_collected = self
                                                    .collected_transparent_positions
                                                    .contains(&check_pos);

                                                if !already_in_accumulated && !globally_collected {
                                                    let tok = &self.tokens[check_pos];
                                                    let tok_type = tok.get_type();
                                                    if tok_type == "whitespace" {
                                                        log::debug!("RETROACTIVELY collecting whitespace at {}: {:?}", check_pos, tok.raw());
                                                        frame.accumulated.push(Node::Whitespace {
                                                            raw: tok.raw().to_string(),
                                                            token_idx: check_pos,
                                                        });
                                                        tentatively_collected.push(check_pos);
                                                    } else if tok_type == "newline" {
                                                        log::debug!("RETROACTIVELY collecting newline at {}: {:?}", check_pos, tok.raw());
                                                        frame.accumulated.push(Node::Newline {
                                                            raw: tok.raw().to_string(),
                                                            token_idx: check_pos,
                                                        });
                                                        tentatively_collected.push(check_pos);
                                                    }
                                                }
                                            }
                                        }
                                    }

                                    // GREEDY_ONCE_STARTED: Trim max_idx after first match
                                    // This matches Python's behavior (sequence.py lines 319-327)
                                    if *first_match && *parse_mode == ParseMode::GreedyOnceStarted {
                                        log::debug!(
                                            "GREEDY_ONCE_STARTED: Trimming max_idx after first match from {} to terminator",
                                            *max_idx
                                        );
                                        *max_idx = self
                                            .trim_to_terminator(*matched_idx, &frame_terminators);
                                        *first_match = false;
                                        log::debug!("  New max_idx: {}", *max_idx);
                                    }
                                }

                                let current_matched_idx = *matched_idx;
                                let current_allow_gaps = *allow_gaps;
                                let current_parse_mode = *parse_mode;
                                let current_max_idx = *max_idx;
                                let current_original_max_idx = *original_max_idx; // Use this for children!
                                let current_elem_idx = *current_element_idx;

                                // Increment current_element_idx for next iteration
                                *current_element_idx += 1;

                                let elements_clone = elements.clone();

                                // Check if we've processed all elements in the grammar
                                // (not just attempted all children - optional elements that fail shouldn't count)
                                // The Python implementation iterates through all elements with a for-loop,
                                // using "continue" to skip optional elements that fail. We need similar logic.
                                // current_elem_idx tracks which element index we last processed
                                // We're done when we've moved past the last element
                                let all_elements_processed =
                                    current_elem_idx + 1 >= elements_clone.len();

                                if all_elements_processed {
                                    // All elements processed
                                    // NOTE: We do NOT commit tentatively_collected here because this Sequence
                                    // result might be discarded by a parent OneOf that chooses a different option.
                                    // Tentatively collected tokens are already in frame.accumulated, which is enough.
                                    log::debug!(
                                        "Sequence completing: current_elem_idx={}, elements_clone.len()={}",
                                        current_elem_idx,
                                        elements_clone.len()
                                    );

                                    // Collect any trailing transparent tokens (whitespace, newlines, end_of_file)
                                    // Note: We always consume end_of_file even if allow_gaps is false
                                    // Use self.tokens.len() as the upper bound to collect all trailing tokens
                                    // self.pos = current_matched_idx;
                                    // log::debug!(
                                    //     "Sequence frame_id={}: Collecting trailing tokens from pos {} to {}, allow_gaps={}",
                                    //     frame.frame_id, self.pos, self.tokens.len(), current_allow_gaps
                                    // );
                                    // while self.pos < self.tokens.len() {
                                    //     if let Some(tok) = self.peek() {
                                    //         if tok.is_code() {
                                    //             log::debug!("Sequence frame_id={}: Stopped at code token at pos {}", frame.frame_id, self.pos);
                                    //             break; // Stop at code tokens
                                    //         }
                                    //         let tok_type = tok.get_type();
                                    //         let already_collected = self
                                    //             .collected_transparent_positions
                                    //             .contains(&self.pos);
                                    //         log::debug!(
                                    //             "Sequence frame_id={}: Checking pos {}, type={}, already_collected={}",
                                    //             frame.frame_id, self.pos, tok_type, already_collected
                                    //         );
                                    //         if tok_type == "whitespace" {
                                    //             if current_allow_gaps
                                    //                 && !self
                                    //                     .collected_transparent_positions
                                    //                     .contains(&self.pos)
                                    //                 && !tentatively_collected.contains(&self.pos)
                                    //             {
                                    //                 frame.accumulated.push(Node::Whitespace(
                                    //                     tok.raw().to_string(),
                                    //                     self.pos,
                                    //                 ));
                                    //                 tentatively_collected.push(self.pos);
                                    //             }
                                    //         } else if tok_type == "newline" {
                                    //             if current_allow_gaps
                                    //                 && !self
                                    //                     .collected_transparent_positions
                                    //                     .contains(&self.pos)
                                    //                 && !tentatively_collected.contains(&self.pos)
                                    //             {
                                    //                 frame.accumulated.push(Node::Newline(
                                    //                     tok.raw().to_string(),
                                    //                     self.pos,
                                    //                 ));
                                    //                 tentatively_collected.push(self.pos);
                                    //             }
                                    //             // } else if tok_type == "end_of_file" {
                                    //             //     // Always collect end_of_file if it hasn't been collected yet
                                    //             //     if !self
                                    //             //         .collected_transparent_positions
                                    //             //         .contains(&self.pos)
                                    //             //         && !tentatively_collected.contains(&self.pos)
                                    //             //     {
                                    //             //         log::debug!("Sequence frame_id={}: COLLECTING end_of_file at position {}", frame.frame_id, self.pos);
                                    //             //         frame.accumulated.push(Node::EndOfFile(
                                    //             //             tok.raw().to_string(),
                                    //             //             self.pos,
                                    //             //         ));
                                    //             //         tentatively_collected.push(self.pos);
                                    //             //     }
                                    //         }
                                    //         self.bump();
                                    //     } else {
                                    //         break;
                                    //     }
                                    // }
                                    // Update matched_idx to current position after collecting trailing tokens
                                    // let current_matched_idx = self.pos;
                                    log::debug!("DEBUG: Sequence completing - frame_id={}, self.pos={}, current_matched_idx={}, elements.len={}, accumulated.len={}",
                                        frame.frame_id, self.pos, current_matched_idx, elements_clone.len(), frame.accumulated.len());

                                    let result_node = if frame.accumulated.is_empty() {
                                        log::debug!("WARNING: Sequence completing with EMPTY accumulated! frame_id={}, current_elem_idx={}, elements.len={}",
                                                  frame.frame_id, current_elem_idx, elements_clone.len());
                                        Node::Empty
                                    } else {
                                        Node::Sequence {
                                            children: frame.accumulated.clone(),
                                        }
                                    };
                                    log::debug!(
                                        "Sequence COMPLETE: Storing result at frame_id={}",
                                        frame.frame_id
                                    );
                                    stack.results.insert(
                                        frame.frame_id,
                                        (result_node, current_matched_idx, None),
                                    );
                                    continue; // Frame is complete, move to next frame
                                } else {
                                    // Before processing next element, handle transparent token collection for allow_gaps=true
                                    let mut next_pos = current_matched_idx;
                                    if current_allow_gaps && child_index < elements_clone.len() {
                                        // Skip forward to next code token
                                        let _idx = self.skip_start_index_forward_to_code(
                                            current_matched_idx,
                                            current_max_idx,
                                        );

                                        // Check if we need to collect these transparent tokens
                                        let has_uncollected =
                                            (current_matched_idx.._idx).any(|pos| {
                                                pos < self.tokens.len()
                                                    && !self.tokens[pos].is_code()
                                                    && !self
                                                        .collected_transparent_positions
                                                        .contains(&pos)
                                            });

                                        if has_uncollected {
                                            log::debug!(
                                                "Collecting transparent tokens from {} to {}",
                                                current_matched_idx,
                                                _idx
                                            );

                                            // Collect transparent tokens
                                            for collect_pos in current_matched_idx.._idx {
                                                if collect_pos < self.tokens.len()
                                                    && !self.tokens[collect_pos].is_code()
                                                {
                                                    let tok = &self.tokens[collect_pos];
                                                    let tok_type = tok.get_type();
                                                    // Only collect if not already present in frame.accumulated
                                                    let already_collected = frame
                                                        .accumulated
                                                        .iter()
                                                        .any(|node| match node {
                                                            Node::Whitespace {
                                                                raw: _,
                                                                token_idx: pos,
                                                            }
                                                            | Node::Newline {
                                                                raw: _,
                                                                token_idx: pos,
                                                            } => *pos == collect_pos,
                                                            _ => false,
                                                        });
                                                    if !already_collected {
                                                        if tok_type == "whitespace" {
                                                            log::debug!(
                                                                "COLLECTING whitespace at {}: {:?}",
                                                                collect_pos,
                                                                tok.raw()
                                                            );
                                                            frame.accumulated.push(
                                                                Node::Whitespace {
                                                                    raw: tok.raw().to_string(),
                                                                    token_idx: collect_pos,
                                                                },
                                                            );
                                                            tentatively_collected.push(collect_pos);
                                                        } else if tok_type == "newline" {
                                                            log::debug!(
                                                                "COLLECTING newline at {}: {:?}",
                                                                collect_pos,
                                                                tok.raw()
                                                            );
                                                            frame.accumulated.push(Node::Newline {
                                                                raw: tok.raw().to_string(),
                                                                token_idx: collect_pos,
                                                            });
                                                            tentatively_collected.push(collect_pos);
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                        next_pos = _idx;
                                    }

                                    // Check if we've run out of segments
                                    // Note: current_elem_idx is the element index we just processed
                                    // The next element to process is at current_elem_idx + 1
                                    log::debug!(
                                        "Sequence checking EOF: next_pos={}, current_max_idx={}, current_elem_idx={}, elements_clone.len()={}",
                                        next_pos,
                                        current_max_idx,
                                        current_elem_idx,
                                        elements_clone.len()
                                    );
                                    let next_elem_idx = current_elem_idx + 1;
                                    if next_pos >= current_max_idx
                                        && next_elem_idx < elements_clone.len()
                                    {
                                        log::debug!("  Entered EOF check block");
                                        // Check if remaining elements (starting from next_elem_idx) are all optional
                                        // We skip Meta elements since they don't consume input
                                        let mut check_idx = next_elem_idx;
                                        let mut next_element_optional = true; // Default to true if all remaining are Meta
                                        while check_idx < elements_clone.len() {
                                            if let Grammar::Meta(_) = &elements_clone[check_idx] {
                                                // Skip Meta elements - they don't consume input
                                                check_idx += 1;
                                            } else {
                                                // Found a non-Meta element - check if it's optional
                                                next_element_optional =
                                                    is_grammar_optional(&elements_clone[check_idx]);
                                                break;
                                            }
                                        }
                                        log::debug!(
                                            "  next_element_optional={} (checked from elem_idx {} to {})",
                                            next_element_optional,
                                            next_elem_idx,
                                            check_idx
                                        );

                                        if next_element_optional {
                                            // Next element is optional and we're at EOF - complete the sequence
                                            log::debug!(
                                                "COMPLETE: ran out of segments but next element is optional"
                                            );
                                            for pos in tentatively_collected.iter() {
                                                self.collected_transparent_positions.insert(*pos);
                                            }
                                            self.pos = current_matched_idx;
                                            let result_node = if frame.accumulated.is_empty() {
                                                Node::Empty
                                            } else {
                                                Node::Sequence {
                                                    children: frame.accumulated.clone(),
                                                }
                                            };
                                            stack.results.insert(
                                                frame.frame_id,
                                                (result_node, current_matched_idx, None),
                                            );
                                            continue;
                                        } else {
                                            // Handle based on parse mode
                                            if current_parse_mode == ParseMode::Strict
                                                || frame.accumulated.is_empty()
                                            {
                                                log::debug!(
                                                    "NOMATCH Ran out of segments in STRICT mode"
                                                );
                                                stack.results.insert(
                                                    frame.frame_id,
                                                    (Node::Empty, element_start, None),
                                                );
                                                continue;
                                            } else {
                                                // GREEDY/GREEDY_ONCE_STARTED: return what we have
                                                log::debug!(
                                                    "INCOMPLETE match: ran out of segments"
                                                );
                                                for pos in tentatively_collected.iter() {
                                                    self.collected_transparent_positions
                                                        .insert(*pos);
                                                }
                                                self.pos = current_matched_idx;
                                                let result_node = Node::Sequence {
                                                    children: frame.accumulated.clone(),
                                                };
                                                stack.results.insert(
                                                    frame.frame_id,
                                                    (result_node, current_matched_idx, None),
                                                );
                                                continue;
                                            }
                                        }
                                    }

                                    // Push next child - skip Meta elements
                                    frame.state = FrameState::WaitingForChild {
                                        child_index: child_index + 1,
                                        total_children,
                                    };

                                    // Find next non-Meta element
                                    // child_index is the count of non-Meta children processed so far
                                    // current_element_idx tracks which element index we last processed
                                    let mut next_elem_idx = current_elem_idx + 1;
                                    let mut created_child = false;
                                    let frame_id_for_debug = frame.frame_id; // Save before potentially moving frame
                                    let mut final_accumulated = frame.accumulated.clone(); // Save before potentially moving frame
                                    log::debug!("Looking for next child: next_elem_idx={}, elements_clone.len()={}", next_elem_idx, elements_clone.len());
                                    while next_elem_idx < elements_clone.len() {
                                        log::debug!(
                                            "Checking element {}: {:?}",
                                            next_elem_idx,
                                            &elements_clone[next_elem_idx]
                                        );
                                        if let Grammar::Meta(meta_type) =
                                            &elements_clone[next_elem_idx]
                                        {
                                            // Add Meta to accumulated directly
                                            if *meta_type == "indent" {
                                                let mut insert_pos = final_accumulated.len();
                                                while insert_pos > 0 {
                                                    match &final_accumulated[insert_pos - 1] {
                                                        Node::Whitespace {
                                                            raw: _,
                                                            token_idx: _,
                                                        }
                                                        | Node::Newline {
                                                            raw: _,
                                                            token_idx: _,
                                                        } => {
                                                            insert_pos -= 1;
                                                        }
                                                        _ => break,
                                                    }
                                                }
                                                final_accumulated.insert(
                                                    insert_pos,
                                                    Node::Meta {
                                                        token_type: meta_type,
                                                        token_idx: None,
                                                    },
                                                );
                                                frame.accumulated.insert(
                                                    insert_pos,
                                                    Node::Meta {
                                                        token_type: meta_type,
                                                        token_idx: None,
                                                    },
                                                );
                                            } else {
                                                final_accumulated.push(Node::Meta {
                                                    token_type: meta_type,
                                                    token_idx: None,
                                                });
                                                frame.accumulated.push(Node::Meta {
                                                    token_type: meta_type,
                                                    token_idx: None,
                                                });
                                            }
                                            next_elem_idx += 1;
                                        } else {
                                            // Non-Meta element - create frame for it
                                            log::debug!(
                                                "Creating child frame for element {}: frame_id={}, parent_max_idx={}",
                                                next_elem_idx,
                                                stack.frame_id_counter,
                                                current_original_max_idx
                                            );

                                            let child_frame = ParseFrame::new_child(
                                                stack.frame_id_counter,
                                                elements_clone[next_elem_idx].clone(),
                                                next_pos,
                                                frame_terminators.clone(),
                                                Some(current_original_max_idx), // Use original max_idx before GREEDY_ONCE_STARTED trimming!
                                            );

                                            log::debug!("DEBUG [iter {}]: Sequence WaitingForChild - parent {}, creating child {}, grammar: {:?}",
                                                iteration_count, frame_id_for_debug, child_frame.frame_id, child_frame.grammar);

                                            // Use helper to push parent, update it, and push child
                                            ParseFrame::push_sequence_child_and_update_parent(
                                                &mut stack,
                                                frame,
                                                child_frame,
                                                next_elem_idx,
                                            );

                                            log::debug!(
                                                "Pushed child frame, continuing to process it"
                                            );
                                            log::debug!("DEBUG [iter {}]: Sequence WaitingForChild ABOUT TO BREAK from while loop", iteration_count);
                                            created_child = true;
                                            break; // Exit the while loop - we've created the next child
                                        }
                                    }
                                    log::debug!("DEBUG [iter {}]: Sequence WaitingForChild AFTER while loop, created_child={}", iteration_count, created_child);
                                    // Only continue to process child if we actually created one
                                    if created_child {
                                        log::debug!("DEBUG [iter {}]: Sequence WaitingForChild ABOUT TO CONTINUE 'main_loop", iteration_count);
                                        continue 'main_loop;
                                    }
                                    // Otherwise, all remaining elements were Meta - complete the Sequence
                                    log::debug!("DEBUG [iter {}]: Sequence WaitingForChild - all remaining elements were Meta, completing frame_id={}", iteration_count, frame_id_for_debug);
                                    self.pos = current_matched_idx;
                                    let result_node = if final_accumulated.is_empty() {
                                        Node::Empty
                                    } else {
                                        Node::Sequence {
                                            children: final_accumulated,
                                        }
                                    };
                                    stack.results.insert(
                                        frame_id_for_debug,
                                        (result_node, current_matched_idx, None),
                                    );
                                    continue 'main_loop; // Frame is complete, move to next frame
                                }
                            }

                            FrameContext::AnyNumberOf {
                                elements,
                                min_times,
                                max_times,
                                max_times_per_element: _max_times_per_element,
                                allow_gaps,
                                optional: _optional,
                                parse_mode,
                                count,
                                matched_idx,
                                working_idx,
                                option_counter,
                                max_idx,
                                last_child_frame_id: _last_child_frame_id,
                            } => {
                                handle_anynumberof_waiting_for_child!(
                                    self,
                                    frame,
                                    stack,
                                    child_node,
                                    child_end_pos,
                                    child_element_key,
                                    elements,
                                    min_times,
                                    max_times,
                                    max_times_per_element,
                                    allow_gaps,
                                    optional,
                                    parse_mode,
                                    count,
                                    matched_idx,
                                    working_idx,
                                    option_counter,
                                    max_idx,
                                    frame_terminators,
                                    iteration_count
                                );
                            }

                            FrameContext::Bracketed {
                                bracket_pairs,
                                elements,
                                allow_gaps,
                                optional,
                                parse_mode,
                                state,
                                last_child_frame_id,
                            } => {
                                log::debug!(
                                    "Bracketed WaitingForChild: state={:?}, child_node empty={}",
                                    state,
                                    child_node.is_empty()
                                );

                                match state {
                                    BracketedState::MatchingOpen => {
                                        // Opening bracket result
                                        if child_node.is_empty() {
                                            // No opening bracket found - return Empty to let parent try other options
                                            self.pos = frame.pos;
                                            log::debug!("Bracketed returning Empty (no opening bracket, optional={})", optional);
                                            stack.results.insert(
                                                frame.frame_id,
                                                (Node::Empty, frame.pos, None),
                                            );
                                        } else {
                                            // Opening bracket matched!
                                            frame.accumulated.push(child_node.clone());
                                            let content_start_idx = *child_end_pos;

                                            // OPTIMIZATION: Use pre-computed matching bracket to set tight max_idx
                                            // This prevents exploring beyond the closing bracket
                                            let bracket_max_idx =
                                                child_node.get_token_idx().and_then(|open_idx| {
                                                    self.get_matching_bracket_idx(open_idx)
                                                });

                                            if let Some(close_idx) = bracket_max_idx {
                                                log::debug!(
                                                    "Bracketed: Using pre-computed closing bracket at idx={} as max_idx",
                                                    close_idx
                                                );
                                            }

                                            // Collect whitespace after opening bracket if allow_gaps
                                            if *allow_gaps {
                                                let code_idx = self
                                                    .skip_start_index_forward_to_code(
                                                        content_start_idx,
                                                        self.tokens.len(),
                                                    );
                                                for pos in content_start_idx..code_idx {
                                                    if let Some(tok) = self.tokens.get(pos) {
                                                        let tok_type = tok.get_type();
                                                        if tok_type == "whitespace" {
                                                            frame.accumulated.push(
                                                                Node::Whitespace {
                                                                    raw: tok.raw().to_string(),
                                                                    token_idx: pos,
                                                                },
                                                            );
                                                        } else if tok_type == "newline" {
                                                            frame.accumulated.push(Node::Newline {
                                                                raw: tok.raw().to_string(),
                                                                token_idx: pos,
                                                            });
                                                        }
                                                    }
                                                }
                                                self.pos = code_idx;
                                            } else {
                                                self.pos = content_start_idx;
                                            }

                                            // Transition to MatchingContent
                                            *state = BracketedState::MatchingContent;

                                            // Create content grammar (Sequence with closing bracket as terminator)
                                            let content_grammar = Grammar::Sequence {
                                                elements: elements.clone(),
                                                optional: false,
                                                terminators: vec![(*bracket_pairs.1).clone()],
                                                reset_terminators: true, // Clear parent terminators!
                                                allow_gaps: *allow_gaps,
                                                parse_mode: *parse_mode,
                                            };

                                            // OPTIMIZATION: Use pre-computed closing bracket as max_idx!
                                            // This prevents the parser from exploring tokens beyond the closing bracket,
                                            // significantly reducing unnecessary grammar matching for nested brackets.
                                            // The content must end before the closing bracket, so we can safely limit it.
                                            let mut child_frame = ParseFrame {
                                                frame_id: stack.frame_id_counter,
                                                grammar: content_grammar,
                                                pos: self.pos,
                                                terminators: vec![(*bracket_pairs.1).clone()],
                                                state: FrameState::Initial,
                                                accumulated: vec![],
                                                context: FrameContext::None,
                                                parent_max_idx: bracket_max_idx, // Tight boundary from pre-computed bracket!
                                            };

                                            // Update this frame's last_child_frame_id
                                            *last_child_frame_id = Some(stack.frame_id_counter);

                                            stack.frame_id_counter += 1;

                                            // Push parent frame back first, then child (LIFO - child will be processed next)
                                            stack.push(&mut frame);
                                            stack.push(&mut child_frame);
                                            continue 'main_loop; // Skip the result check - child hasn't been processed yet
                                        }
                                    }
                                    BracketedState::MatchingContent => {
                                        log::debug!("Bracketed MatchingContent - frame_id={}, child_end_pos={}, is_empty={}", frame.frame_id, child_end_pos, child_node.is_empty());
                                        // Content result
                                        if !child_node.is_empty() {
                                            // Recursively flatten sequence/delimited nodes to get a flat list of content
                                            let mut to_process = vec![child_node.clone()];
                                            while let Some(node) = to_process.pop() {
                                                match node {
                                                    Node::Sequence { children }
                                                    | Node::DelimitedList { children } => {
                                                        // Add children to processing queue in reverse order to maintain order
                                                        to_process
                                                            .extend(children.into_iter().rev());
                                                    }
                                                    _ => {
                                                        // Leaf node or Ref - add directly to accumulated
                                                        frame.accumulated.push(node);
                                                    }
                                                }
                                            }
                                        }

                                        let gap_start = *child_end_pos;
                                        self.pos = gap_start;
                                        log::debug!(
                                            "DEBUG: After content, gap_start={}, current_pos={}",
                                            gap_start,
                                            self.pos
                                        );

                                        // Collect whitespace before closing bracket if allow_gaps
                                        if *allow_gaps {
                                            let code_idx = self.skip_start_index_forward_to_code(
                                                gap_start,
                                                self.tokens.len(),
                                            );
                                            for pos in gap_start..code_idx {
                                                if let Some(tok) = self.tokens.get(pos) {
                                                    let tok_type = tok.get_type();
                                                    if tok_type == "whitespace" {
                                                        frame.accumulated.push(Node::Whitespace {
                                                            raw: tok.raw().to_string(),
                                                            token_idx: pos,
                                                        });
                                                    } else if tok_type == "newline" {
                                                        frame.accumulated.push(Node::Newline {
                                                            raw: tok.raw().to_string(),
                                                            token_idx: pos,
                                                        });
                                                    }
                                                }
                                            }
                                            self.pos = code_idx;
                                        }

                                        // Check if we've run out of segments
                                        log::debug!("DEBUG: Checking for closing bracket - self.pos={}, tokens.len={}", self.pos, self.tokens.len());
                                        if self.pos >= self.tokens.len()
                                            || self
                                                .peek()
                                                .is_some_and(|t| t.get_type() == "end_of_file")
                                        {
                                            log::debug!("DEBUG: No closing bracket found!");
                                            // No end bracket found
                                            if *parse_mode == ParseMode::Strict {
                                                self.pos = frame.pos;
                                                stack.results.insert(
                                                    frame.frame_id,
                                                    (Node::Empty, frame.pos, None),
                                                );
                                                continue 'main_loop; // Frame is complete (failed), move to next frame
                                            } else {
                                                return Err(ParseError::new(
                                                    "Couldn't find closing bracket for opening bracket".to_string(),
                                                ));
                                            }
                                        } else {
                                            log::debug!("DEBUG: Transitioning to MatchingClose!");
                                            // Transition to MatchingClose
                                            *state = BracketedState::MatchingClose;

                                            // Create child frame for closing bracket
                                            // Get parent_max_idx to propagate
                                            let parent_limit = frame.parent_max_idx;

                                            log::debug!("DEBUG: Creating closing bracket child at pos={}, parent_limit={:?}", self.pos, parent_limit);
                                            let mut child_frame = ParseFrame {
                                                frame_id: stack.frame_id_counter,
                                                grammar: (*bracket_pairs.1).clone(),
                                                pos: self.pos,
                                                terminators: vec![(*bracket_pairs.1).clone()],
                                                state: FrameState::Initial,
                                                accumulated: vec![],
                                                context: FrameContext::None,
                                                parent_max_idx: parent_limit, // Propagate parent's limit!
                                            };

                                            // Update this frame's last_child_frame_id
                                            *last_child_frame_id = Some(stack.frame_id_counter);

                                            stack.frame_id_counter += 1;

                                            // Push parent frame back first, then child (LIFO - child will be processed next)
                                            stack.push(&mut frame);
                                            stack.push(&mut child_frame);
                                            continue 'main_loop; // Skip the result check - child hasn't been processed yet
                                        }
                                    }
                                    BracketedState::MatchingClose => {
                                        log::debug!("DEBUG: Bracketed MatchingClose - child_node.is_empty={}, child_end_pos={}", child_node.is_empty(), child_end_pos);
                                        // Closing bracket result
                                        if child_node.is_empty() {
                                            // No closing bracket found
                                            if *parse_mode == ParseMode::Strict {
                                                self.pos = frame.pos;
                                                stack.results.insert(
                                                    frame.frame_id,
                                                    (Node::Empty, frame.pos, None),
                                                );
                                                continue 'main_loop; // Frame is complete (failed), move to next frame
                                            } else {
                                                return Err(ParseError::new(
                                                    "Couldn't find closing bracket for opening bracket".to_string(),
                                                ));
                                            }
                                        } else {
                                            // Closing bracket matched!
                                            frame.accumulated.push(child_node.clone());
                                            self.pos = *child_end_pos;

                                            let result_node = Node::Bracketed {
                                                children: frame.accumulated.clone(),
                                            };
                                            log::debug!(
                                                "Bracketed COMPLETE: {} children, storing result at frame_id={}",
                                                frame.accumulated.len(),
                                                frame.frame_id
                                            );
                                            stack.results.insert(
                                                frame.frame_id,
                                                (result_node, *child_end_pos, None),
                                            );
                                            continue 'main_loop; // Frame is complete, move to next frame
                                        }
                                    }
                                }
                            }

                            FrameContext::AnySetOf {
                                elements,
                                min_times,
                                max_times,
                                allow_gaps,
                                optional,
                                count,
                                matched_idx,
                                working_idx,
                                matched_elements,
                                max_idx,
                                last_child_frame_id: _last_child_frame_id,
                                parse_mode,
                            } => {
                                log::debug!("[ITERATIVE] AnySetOf WaitingForChild: count={}, matched_idx={}", count, matched_idx);

                                // Handle child result
                                if child_node.is_empty() {
                                    // Child match failed
                                    log::debug!(
                                        "[ITERATIVE] AnySetOf child failed at position {}",
                                        frame.pos
                                    );

                                    // Check if we've met min_times requirement
                                    if *count < *min_times {
                                        if *optional {
                                            self.pos = frame.pos;
                                            log::debug!(
                                                "[ITERATIVE] AnySetOf optional, returning Empty"
                                            );
                                            stack.results.insert(
                                                frame.frame_id,
                                                (Node::Empty, frame.pos, None),
                                            );
                                            continue; // Frame is complete, move to next frame
                                        } else {
                                            return Err(ParseError::new(format!(
                                                "Expected at least {} occurrences in AnySetOf, found {}",
                                                min_times, count
                                            )));
                                        }
                                    } else {
                                        // Met min_times, complete with what we have
                                        log::debug!("[ITERATIVE] AnySetOf met min_times, completing with {} items", frame.accumulated.len());
                                        self.pos = *matched_idx;
                                        let result_node = Node::DelimitedList {
                                            children: frame.accumulated.clone(),
                                        };
                                        stack.results.insert(
                                            frame.frame_id,
                                            (result_node, *matched_idx, None),
                                        );
                                        continue; // Frame is complete, move to next frame
                                    }
                                } else {
                                    // Child matched successfully!
                                    log::debug!(
                                        "[ITERATIVE] AnySetOf child matched: pos {} -> {}",
                                        frame.pos,
                                        child_end_pos
                                    );

                                    // Collect transparent tokens between matched_idx and working_idx if allow_gaps
                                    if *allow_gaps {
                                        for check_pos in *matched_idx..*working_idx {
                                            if check_pos < self.tokens.len()
                                                && !self.tokens[check_pos].is_code()
                                                && !self
                                                    .collected_transparent_positions
                                                    .contains(&check_pos)
                                            {
                                                let tok = &self.tokens[check_pos];
                                                let tok_type = tok.get_type();
                                                if tok_type == "whitespace" {
                                                    frame.accumulated.push(Node::Whitespace {
                                                        raw: tok.raw().to_string(),
                                                        token_idx: check_pos,
                                                    });
                                                    self.collected_transparent_positions
                                                        .insert(check_pos);
                                                } else if tok_type == "newline" {
                                                    frame.accumulated.push(Node::Newline {
                                                        raw: tok.raw().to_string(),
                                                        token_idx: check_pos,
                                                    });
                                                    self.collected_transparent_positions
                                                        .insert(check_pos);
                                                }
                                            }
                                        }
                                    }

                                    // Add matched node
                                    frame.accumulated.push(child_node.clone());
                                    *matched_idx = *child_end_pos;
                                    *working_idx = *matched_idx;
                                    *count += 1;

                                    // Extract element_key from OneOf result and add to matched_elements
                                    let element_key = child_element_key.unwrap_or(0);
                                    matched_elements.insert(element_key);

                                    log::debug!(
                                        "[ITERATIVE] AnySetOf matched item #{}, element_key={}, matched_idx now: {}, matched_elements: {:?}",
                                        count, element_key, matched_idx, matched_elements
                                    );

                                    // Python behavior: Check for complete match (consumed all to max_idx)
                                    let reached_max = *matched_idx >= *max_idx;

                                    if reached_max {
                                        log::debug!(
                                            "[ITERATIVE] AnySetOf: Complete match (reached max_idx={}), stopping iteration",
                                            max_idx
                                        );
                                    }

                                    // Check termination conditions
                                    let should_terminate = reached_max
                                        || (*count >= *min_times
                                            && ((max_times.is_some()
                                                && *count >= max_times.unwrap())
                                                || matched_elements.len() >= elements.len())); // All unique elements matched

                                    if should_terminate {
                                        log::debug!(
                                            "[ITERATIVE] AnySetOf terminating: count={}, min_times={}, matched_idx={}, max_idx={}",
                                            count, min_times, matched_idx, max_idx
                                        );
                                        self.pos = *matched_idx;
                                        let result_node = Node::DelimitedList {
                                            children: frame.accumulated.clone(),
                                        };
                                        stack.results.insert(
                                            frame.frame_id,
                                            (result_node, *matched_idx, None),
                                        );
                                        continue; // Frame is complete, move to next frame
                                    } else {
                                        // Continue - create next child to try remaining elements
                                        *working_idx = if *allow_gaps {
                                            self.skip_start_index_forward_to_code(
                                                *working_idx,
                                                *max_idx,
                                            )
                                        } else {
                                            *working_idx
                                        };

                                        // Filter out already matched elements by element_key
                                        let unmatched_elements: Vec<Grammar> = elements
                                            .iter()
                                            .filter(|elem| {
                                                !matched_elements.contains(&elem.cache_key())
                                            })
                                            .cloned()
                                            .collect();

                                        log::debug!(
                                            "[ITERATIVE] AnySetOf continuing: {} unmatched elements of {} total",
                                            unmatched_elements.len(),
                                            elements.len()
                                        );

                                        if unmatched_elements.is_empty() {
                                            // All elements matched - complete
                                            log::debug!("[ITERATIVE] AnySetOf: all elements matched, completing");
                                            self.pos = *matched_idx;
                                            let result_node = Node::DelimitedList {
                                                children: frame.accumulated.clone(),
                                            };
                                            stack.results.insert(
                                                frame.frame_id,
                                                (result_node, *matched_idx, None),
                                            );
                                            continue; // Frame is complete, move to next frame
                                        } else {
                                            // Create OneOf with only unmatched elements
                                            let child_grammar = Grammar::OneOf {
                                                elements: unmatched_elements,
                                                exclude: None,
                                                optional: false,
                                                terminators: vec![],
                                                reset_terminators: false,
                                                allow_gaps: *allow_gaps,
                                                parse_mode: *parse_mode,
                                            };

                                            // Get parent_max_idx to propagate
                                            let parent_limit = frame.parent_max_idx;

                                            let child_frame = ParseFrame::new_child(
                                                stack.frame_id_counter,
                                                child_grammar,
                                                *working_idx,
                                                frame_terminators.clone(),
                                                parent_limit, // Propagate parent's limit!
                                            );

                                            ParseFrame::push_child_and_update_parent(
                                                &mut stack,
                                                frame,
                                                child_frame,
                                                "AnySetOf",
                                            );
                                            continue 'main_loop; // Continue to process the child we just pushed
                                        }
                                    }
                                }
                            }

                            FrameContext::OneOf {
                                elements,
                                allow_gaps: _allow_gaps,
                                optional,
                                leading_ws,
                                post_skip_pos,
                                longest_match,
                                tried_elements,
                                max_idx,
                                parse_mode,
                                last_child_frame_id: _last_child_frame_id, // Managed by helper
                            } => {
                                log::debug!(
                                    "OneOf WaitingForChild: tried_elements={}, child_empty={}",
                                    tried_elements,
                                    child_node.is_empty()
                                );

                                // Get child end position and element_key
                                let child_end_pos = self.pos;
                                let consumed = child_end_pos - *post_skip_pos;

                                // Get the element_key for the element we just tried
                                let element_key = if *tried_elements < elements.len() {
                                    elements[*tried_elements].cache_key()
                                } else {
                                    0 // Fallback
                                };

                                // Check if this match is better than current longest
                                if !child_node.is_empty() {
                                    let is_better = longest_match.is_none()
                                        || consumed > longest_match.as_ref().unwrap().1;

                                    if is_better {
                                        log::debug!("OneOf: New longest match with {} consumed tokens (element_key={})",
                                                   consumed, element_key);
                                        *longest_match =
                                            Some((child_node.clone(), consumed, element_key));
                                    }

                                    // OPTIMIZATION: Early termination for "complete" matches
                                    // A match is complete if it consumed all available segments up to max_idx.
                                    // Once we've consumed to max_idx, no later alternative can consume MORE,
                                    // so we can stop trying alternatives early (in ANY parse mode).
                                    // This significantly reduces operations for nested functions.
                                    if child_end_pos >= *max_idx {
                                        log::debug!(
                                            "OneOf: Complete match at element {} (consumed all to max_idx={}), early termination (parse_mode={:?})",
                                            *tried_elements,
                                            *max_idx,
                                            *parse_mode
                                        );
                                        // Force loop exit by setting tried_elements to end
                                        *tried_elements = elements.len();
                                    }
                                }

                                // Move to next element
                                *tried_elements += 1;

                                if *tried_elements < elements.len() {
                                    // More elements to try - reset state and create next child
                                    log::debug!(
                                        "OneOf: Trying next element ({}/{})",
                                        tried_elements,
                                        elements.len()
                                    );

                                    // Reset parser position to start of OneOf
                                    self.pos = *post_skip_pos;

                                    // Create child frame for next element
                                    let next_element = elements[*tried_elements].clone();
                                    let next_element_key = next_element.cache_key();
                                    log::debug!(
                                        "OneOf: Next element cache_key={}",
                                        next_element_key
                                    );

                                    // Use the OneOf's max_idx, not the parent's parent_max_idx
                                    let child_frame = ParseFrame::new_child(
                                        stack.frame_id_counter,
                                        next_element,
                                        *post_skip_pos,
                                        frame.terminators.clone(),
                                        Some(*max_idx), // Use OneOf's computed max_idx!
                                    );

                                    frame.state = FrameState::WaitingForChild {
                                        child_index: 0,
                                        total_children: 1,
                                    };

                                    log::debug!("OneOf: Pushing parent frame {} and child frame {} onto stack", frame.frame_id, child_frame.frame_id);

                                    ParseFrame::push_child_and_update_parent(
                                        &mut stack,
                                        frame,
                                        child_frame,
                                        "OneOf",
                                    );

                                    log::debug!("OneOf: Stack size after pushing: {}", stack.len());
                                    log::debug!("OneOf: Continuing to process child frame");
                                    continue 'main_loop; // Skip the result check below - child hasn't been processed yet
                                } else {
                                    // All elements tried - return longest match
                                    log::debug!(
                                        "OneOf: All elements tried, longest_match={:?}",
                                        longest_match
                                            .as_ref()
                                            .map(|(_, consumed, key)| (consumed, key))
                                    );

                                    if let Some((best_node, best_consumed, best_element_key)) =
                                        longest_match
                                    {
                                        // Set position to end of longest match
                                        self.pos = *post_skip_pos + *best_consumed;

                                        // Wrap with leading whitespace if any
                                        let result = if !leading_ws.is_empty() {
                                            let mut children = leading_ws.clone();
                                            children.push(best_node.clone());
                                            Node::Sequence { children }
                                        } else {
                                            best_node.clone()
                                        };

                                        log::debug!(
                                            "OneOf: Returning longest match with element_key={}",
                                            best_element_key
                                        );
                                        // Store result WITH element_key so parent grammars can use it
                                        stack.results.insert(
                                            frame.frame_id,
                                            (result, self.pos, Some(*best_element_key)),
                                        );
                                        continue; // Don't fall through to Complete state
                                    } else {
                                        // No matches found
                                        log::debug!(
                                            "OneOf: No matches found, optional={}, applying parse_mode logic",
                                            optional
                                        );

                                        // Apply parse_mode logic (creates UnparsableSegment in GREEDY mode)
                                        let result_node = apply_parse_mode_to_result(
                                            self.tokens,
                                            Node::Empty,
                                            frame.pos,
                                            *max_idx,
                                            *parse_mode,
                                        );

                                        // Determine final position
                                        let final_pos = if matches!(result_node, Node::Empty) {
                                            frame.pos // Empty match, stay at start
                                        } else {
                                            *max_idx // Unparsable consumed up to max_idx
                                        };

                                        self.pos = final_pos;
                                        stack
                                            .results
                                            .insert(frame.frame_id, (result_node, final_pos, None));
                                        continue;
                                    }
                                }
                            }

                            FrameContext::Delimited {
                                elements,
                                delimiter,
                                allow_trailing,
                                optional,
                                allow_gaps,
                                min_delimiters,
                                parse_mode,
                                delimiter_count,
                                matched_idx,
                                working_idx,
                                max_idx,
                                state,
                                last_child_frame_id: _last_child_frame_id,
                            } => {
                                log::debug!("[ITERATIVE] Delimited WaitingForChild: state={:?}, delimiter_count={}, child_node is_empty={}",
                                    state, delimiter_count, child_node.is_empty());

                                // Debug: Show element types for function-related Delimited
                                if elements.iter().any(|e| {
                                    matches!(e, Grammar::Ref { name, .. } if name.contains("FunctionContents") || name.contains("DatetimeUnit"))
                                }) {
                                    log::debug!("[DELIMITED-DEBUG] Processing child result at pos {}, child_end_pos={}, state={:?}",
                                        frame.pos, child_end_pos, state);
                                    log::debug!("[DELIMITED-DEBUG] Child node: {:?}",
                                        match child_node {
                                            Node::Empty => "Empty".to_string(),
                                            Node::Ref { name, .. } => format!("Ref({})", name),
                                            Node::Sequence { children: items } => format!("Sequence({} items)", items.len()),
                                            _ => format!("{:?}", child_node).chars().take(100).collect(),
                                        });
                                }

                                match state {
                                    DelimitedState::MatchingElement => {
                                        // We were trying to match an element
                                        if child_node.is_empty() {
                                            // No element matched
                                            log::debug!("[ITERATIVE] Delimited: no element matched at position {}", frame.pos);

                                            // Delimited always returns DelimitedList (possibly empty), not Empty
                                            // This matches the recursive parser behavior
                                            log::debug!(
                                                "[ITERATIVE] Delimited completing with {} items",
                                                frame.accumulated.len()
                                            );
                                            self.pos = *matched_idx;
                                            stack.results.insert(
                                                frame.frame_id,
                                                (
                                                    Node::DelimitedList {
                                                        children: frame.accumulated.clone(),
                                                    },
                                                    *matched_idx,
                                                    None,
                                                ),
                                            );
                                            continue; // Frame is complete, move to next frame
                                        } else {
                                            // Element matched!
                                            log::debug!("[ITERATIVE] Delimited element matched: pos {} -> {}", frame.pos, child_end_pos);

                                            // Collect whitespace between matched_idx and working_idx if allow_gaps
                                            if *allow_gaps {
                                                for check_pos in *matched_idx..*working_idx {
                                                    if check_pos < self.tokens.len()
                                                        && !self.tokens[check_pos].is_code()
                                                        && !self
                                                            .collected_transparent_positions
                                                            .contains(&check_pos)
                                                    {
                                                        let tok = &self.tokens[check_pos];
                                                        let tok_type = tok.get_type();
                                                        if tok_type == "whitespace" {
                                                            frame.accumulated.push(
                                                                Node::Whitespace {
                                                                    raw: tok.raw().to_string(),
                                                                    token_idx: check_pos,
                                                                },
                                                            );
                                                            self.collected_transparent_positions
                                                                .insert(check_pos);
                                                        } else if tok_type == "newline" {
                                                            frame.accumulated.push(Node::Newline {
                                                                raw: tok.raw().to_string(),
                                                                token_idx: check_pos,
                                                            });
                                                            self.collected_transparent_positions
                                                                .insert(check_pos);
                                                        }
                                                    }
                                                }
                                            }

                                            // Add matched element
                                            frame.accumulated.push(child_node.clone());
                                            *matched_idx = *child_end_pos;
                                            *working_idx = *matched_idx;

                                            // Skip whitespace before delimiter
                                            if *allow_gaps {
                                                *working_idx = self
                                                    .skip_start_index_forward_to_code(
                                                        *working_idx,
                                                        *max_idx,
                                                    );
                                            }

                                            // Check if we're at EOF or terminator
                                            // If so, no delimiter is required (delimiters are only between elements)
                                            self.pos = *working_idx;
                                            if self.is_at_end()
                                                || self.is_terminated(&frame_terminators)
                                            {
                                                log::debug!(
                                                    "[ITERATIVE] Delimited: at EOF or terminator after element, completing at position {}",
                                                    matched_idx
                                                );
                                                self.pos = *matched_idx;
                                                stack.results.insert(
                                                    frame.frame_id,
                                                    (
                                                        Node::DelimitedList {
                                                            children: frame.accumulated.clone(),
                                                        },
                                                        *matched_idx,
                                                        None,
                                                    ),
                                                );
                                                continue; // Frame is complete, move to next frame
                                            } else {
                                                // Transition to MatchingDelimiter state
                                                *state = DelimitedState::MatchingDelimiter;

                                                // Use Delimited frame's max_idx for children, not parent's
                                                let child_max_idx = *max_idx;

                                                // Create child frame for delimiter
                                                let child_frame = ParseFrame::new_child(
                                                    stack.frame_id_counter,
                                                    (**delimiter).clone(),
                                                    *working_idx,
                                                    frame_terminators.clone(),
                                                    Some(child_max_idx),
                                                );

                                                ParseFrame::push_child_and_update_parent(
                                                    &mut stack,
                                                    frame,
                                                    child_frame,
                                                    "Delimited",
                                                );
                                                continue 'main_loop; // Skip to processing the child frame
                                            }
                                        }
                                    }
                                    DelimitedState::MatchingDelimiter => {
                                        // We were trying to match a delimiter
                                        if child_node.is_empty() {
                                            // No delimiter found - list is complete
                                            log::debug!("[ITERATIVE] Delimited: no delimiter found, completing at position {}", matched_idx);

                                            // Check if we have enough delimiters
                                            if *delimiter_count < *min_delimiters {
                                                if *optional {
                                                    self.pos = frame.pos;
                                                    stack.results.insert(
                                                        frame.frame_id,
                                                        (
                                                            Node::DelimitedList {
                                                                children: frame.accumulated.clone(),
                                                            },
                                                            frame.pos,
                                                            None,
                                                        ),
                                                    );
                                                } else {
                                                    return Err(ParseError::new(format!(
                                                        "Expected at least {} delimiters, found {}",
                                                        min_delimiters, delimiter_count
                                                    )));
                                                }
                                            } else {
                                                self.pos = *matched_idx;
                                                stack.results.insert(
                                                    frame.frame_id,
                                                    (
                                                        Node::DelimitedList {
                                                            children: frame.accumulated.clone(),
                                                        },
                                                        *matched_idx,
                                                        None,
                                                    ),
                                                );
                                            }
                                        } else {
                                            // Delimiter matched!
                                            log::debug!("[ITERATIVE] Delimited delimiter matched: pos {} -> {}", working_idx, child_end_pos);

                                            // Collect whitespace before delimiter
                                            if *allow_gaps {
                                                for check_pos in *matched_idx..*working_idx {
                                                    if check_pos < self.tokens.len()
                                                        && !self.tokens[check_pos].is_code()
                                                        && !self
                                                            .collected_transparent_positions
                                                            .contains(&check_pos)
                                                    {
                                                        let tok = &self.tokens[check_pos];
                                                        let tok_type = tok.get_type();
                                                        if tok_type == "whitespace" {
                                                            frame.accumulated.push(
                                                                Node::Whitespace {
                                                                    raw: tok.raw().to_string(),
                                                                    token_idx: check_pos,
                                                                },
                                                            );
                                                            self.collected_transparent_positions
                                                                .insert(check_pos);
                                                        } else if tok_type == "newline" {
                                                            frame.accumulated.push(Node::Newline {
                                                                raw: tok.raw().to_string(),
                                                                token_idx: check_pos,
                                                            });
                                                            self.collected_transparent_positions
                                                                .insert(check_pos);
                                                        }
                                                    }
                                                }
                                            }

                                            // Add delimiter
                                            frame.accumulated.push(child_node.clone());
                                            *matched_idx = *child_end_pos;
                                            *working_idx = *matched_idx;
                                            *delimiter_count += 1;

                                            // Check if we're at a terminator
                                            self.pos = *matched_idx;
                                            if self.is_terminated(&frame_terminators) {
                                                log::debug!("[ITERATIVE] Delimited: terminated after delimiter");
                                                if !*allow_trailing {
                                                    return Err(ParseError::new(
                                                        "Trailing delimiter not allowed"
                                                            .to_string(),
                                                    ));
                                                }
                                                // Complete with trailing delimiter
                                                stack.results.insert(
                                                    frame.frame_id,
                                                    (
                                                        Node::DelimitedList {
                                                            children: frame.accumulated.clone(),
                                                        },
                                                        *matched_idx,
                                                        None,
                                                    ),
                                                );
                                            } else {
                                                // Transition back to MatchingElement state
                                                *state = DelimitedState::MatchingElement;

                                                // Skip whitespace before next element
                                                if *allow_gaps {
                                                    *working_idx = self
                                                        .skip_start_index_forward_to_code(
                                                            *working_idx,
                                                            *max_idx,
                                                        );
                                                }

                                                // Check if we're at a terminator or EOF BEFORE creating child
                                                // This matches Python's behavior of checking terminators before matching
                                                self.pos = *working_idx;
                                                if self.is_at_end()
                                                    || self.is_terminated(&frame_terminators)
                                                {
                                                    log::debug!("[ITERATIVE] Delimited: at terminator/EOF before next element, completing");
                                                    self.pos = *matched_idx;
                                                    stack.results.insert(
                                                        frame.frame_id,
                                                        (
                                                            Node::DelimitedList {
                                                                children: frame.accumulated.clone(),
                                                            },
                                                            *matched_idx,
                                                            None,
                                                        ),
                                                    );
                                                    continue; // Frame complete
                                                }

                                                // Use Delimited frame's max_idx for children, not parent's
                                                let child_max_idx = *max_idx;

                                                // Create child frame for next element
                                                let child_grammar = Grammar::OneOf {
                                                    elements: elements.clone(),
                                                    exclude: None,
                                                    optional: true, // Elements in Delimited are implicitly optional
                                                    terminators: vec![],
                                                    reset_terminators: false,
                                                    allow_gaps: *allow_gaps,
                                                    parse_mode: *parse_mode,
                                                };

                                                let child_frame = ParseFrame::new_child(
                                                    stack.frame_id_counter,
                                                    child_grammar,
                                                    *working_idx,
                                                    frame_terminators.clone(),
                                                    Some(child_max_idx),
                                                );

                                                ParseFrame::push_child_and_update_parent(
                                                    &mut stack,
                                                    frame,
                                                    child_frame,
                                                    "Delimited",
                                                );
                                                continue 'main_loop; // Skip to processing the child frame
                                            }
                                        }
                                    }
                                }
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
            let grammar_desc = match &frame.grammar {
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
                log::debug!("  {}", grammar);
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
