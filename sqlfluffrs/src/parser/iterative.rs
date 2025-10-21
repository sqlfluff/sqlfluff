//! Iterative Parser Implementation
//!
//! This module contains the iterative (stack-based) parser implementation
//! that avoids deep recursion by using an explicit frame stack.
//!
//! The iterative parser processes grammars by maintaining a stack of ParseFrames,
//! each representing a parsing state. This approach prevents stack overflow on
//! deeply nested or complex SQL grammars.

use std::collections::{HashMap, HashSet};

use crate::token;
use crate::{dialect::Dialect, token::Token};

use super::{
    BracketedState, DelimitedState, FrameContext, FrameState, Grammar, Node, ParseError,
    ParseFrame, ParseMode,
};

use super::utils::{apply_parse_mode_to_result, is_grammar_optional};

// Import Parser from core module
use super::core::Parser;

impl<'a> Parser<'_> {
    // ========================================================================
    // Iterative Parser Helper Functions
    // ========================================================================
    //
    // These helper functions handle each grammar type in the iterative parser.
    // Each function processes Initial state for a specific grammar type,
    // inserting results or pushing new frames as needed.

    /// Handle Token grammar in iterative parser
    fn handle_token_initial(
        &mut self,
        token_type: &str,
        frame: &ParseFrame,
        results: &mut std::collections::HashMap<usize, (Node, usize, Option<u64>)>,
    ) -> Result<(), ParseError> {
        log::debug!("DEBUG: Token grammar frame_id={}, pos={}, parent_max_idx={:?}, token_type={:?}, available_tokens={}",
            frame.frame_id, frame.pos, frame.parent_max_idx, token_type, self.tokens.len());

        self.pos = frame.pos;
        log::debug!("Trying token grammar, {}", token_type);

        if let Some(token) = self.peek() {
            let tok = token.clone();
            log::debug!("Current token: {:?}", tok.get_type());

            if tok.get_type() == token_type {
                let token_pos = self.pos;
                self.bump();
                log::debug!("MATCHED Token matched: {:?}", tok);
                log::debug!(
                    "DEBUG: Token grammar frame_id={} matched, result end_pos={}",
                    frame.frame_id,
                    self.pos
                );

                let node = Node::Token(token_type.to_string(), tok.raw(), token_pos);
                results.insert(frame.frame_id, (node, self.pos, None));
                Ok(())
            } else {
                log::debug!(
                    "DEBUG: Token grammar frame_id={} failed with error",
                    frame.frame_id
                );
                Err(ParseError::new(format!(
                    "Expected token type {}, found {}",
                    token_type,
                    tok.get_type()
                )))
            }
        } else {
            log::debug!(
                "DEBUG: Token grammar frame_id={} failed - at EOF",
                frame.frame_id
            );
            Err(ParseError::new("Expected token, found EOF".into()))
        }
    }

    /// Handle StringParser grammar in iterative parser
    fn handle_string_parser_initial(
        &mut self,
        template: &str,
        token_type: &str,
        frame: &ParseFrame,
        iteration_count: usize,
        results: &mut std::collections::HashMap<usize, (Node, usize, Option<u64>)>,
    ) {
        self.pos = frame.pos;
        self.skip_transparent(true);
        let tok_raw = self.peek().cloned();

        match tok_raw {
            Some(tok) if tok.raw().eq_ignore_ascii_case(template) => {
                let token_pos = self.pos;
                self.bump();
                log::debug!("MATCHED String matched: {}", tok);

                let node = Node::Token(token_type.to_string(), tok.raw(), token_pos);
                results.insert(frame.frame_id, (node, self.pos, None));
            }
            _ => {
                log::debug!("String parser didn't match '{}', returning Empty", template);
                log::debug!(
                    "DEBUG [iter {}]: StringParser('{}') frame_id={} storing Empty result",
                    iteration_count,
                    template,
                    frame.frame_id
                );
                results.insert(frame.frame_id, (Node::Empty, self.pos, None));
            }
        }
    }

    /// Handle MultiStringParser grammar in iterative parser
    fn handle_multi_string_parser_initial(
        &mut self,
        templates: &[&str],
        token_type: &str,
        frame: &ParseFrame,
        results: &mut std::collections::HashMap<usize, (Node, usize, Option<u64>)>,
    ) {
        self.pos = frame.pos;
        self.skip_transparent(true);
        let token = self.peek().cloned();

        match token {
            Some(tok)
                if templates
                    .iter()
                    .any(|&temp| tok.raw().eq_ignore_ascii_case(temp)) =>
            {
                let token_pos = self.pos;
                self.bump();
                log::debug!("MATCHED MultiString matched: {}", tok);

                let node = Node::Token(token_type.to_string(), tok.raw(), token_pos);
                results.insert(frame.frame_id, (node, self.pos, None));
            }
            _ => {
                log::debug!("MultiString parser didn't match, returning Empty");
                results.insert(frame.frame_id, (Node::Empty, self.pos, None));
            }
        }
    }

    /// Handle TypedParser grammar in iterative parser
    fn handle_typed_parser_initial(
        &mut self,
        template: &str,
        token_type: &str,
        frame: &ParseFrame,
        results: &mut std::collections::HashMap<usize, (Node, usize, Option<u64>)>,
    ) {
        log::debug!(
            "DEBUG: TypedParser frame_id={}, pos={}, parent_max_idx={:?}, template={:?}",
            frame.frame_id,
            frame.pos,
            frame.parent_max_idx,
            template
        );

        self.pos = frame.pos;
        self.skip_transparent(true);

        if let Some(token) = self.peek() {
            let tok = token.clone();
            log::debug!(
                "DEBUG: TypedParser peeked token: type='{}', raw='{}', pos={}",
                tok.token_type,
                tok.raw(),
                self.pos
            );

            if tok.is_type(&[template]) {
                let raw = tok.raw().to_string();
                let token_pos = self.pos;
                self.bump();
                log::debug!(
                    "DEBUG: TypedParser MATCHED! frame_id={}, consumed token at pos={}",
                    frame.frame_id,
                    token_pos
                );
                log::debug!("MATCHED Typed matched: {}", tok.token_type);
                let node = Node::Token(token_type.to_string(), raw, token_pos);
                results.insert(frame.frame_id, (node, self.pos, None));
            } else {
                log::debug!(
                    "DEBUG: TypedParser FAILED to match! frame_id={}, expected='{}', found='{}'",
                    frame.frame_id,
                    template,
                    tok.token_type
                );
                log::debug!(
                    "Typed parser failed: expected '{}', found '{}'",
                    template,
                    tok.token_type
                );
                results.insert(frame.frame_id, (Node::Empty, frame.pos, None));
            }
        } else {
            log::debug!(
                "DEBUG: TypedParser at EOF! frame_id={}, pos={}",
                frame.frame_id,
                frame.pos
            );
            log::debug!("Typed parser at EOF");
            results.insert(frame.frame_id, (Node::Empty, frame.pos, None));
        }
    }

    /// Handle RegexParser grammar in iterative parser
    /// Returns true if the caller should continue to the next frame (anti-template matched)
    fn handle_regex_parser_initial(
        &mut self,
        template: &str,
        anti_template: &Option<&'static str>,
        token_type: &str,
        frame: &ParseFrame,
        results: &mut std::collections::HashMap<usize, (Node, usize, Option<u64>)>,
    ) -> bool {
        self.pos = frame.pos;
        self.skip_transparent(true);
        let token = self.peek().cloned();

        match token {
            Some(tok)
                if regex::RegexBuilder::new(template)
                    .case_insensitive(true)
                    .build()
                    .unwrap()
                    .is_match(&tok.raw()) =>
            {
                log::debug!("Regex matched: {}", tok);

                // Check anti-template if present
                if let Some(anti) = anti_template {
                    if regex::RegexBuilder::new(anti)
                        .case_insensitive(true)
                        .build()
                        .unwrap()
                        .is_match(&tok.raw())
                    {
                        log::debug!("Regex anti-matched: {}", tok);
                        log::debug!("RegexParser anti-match, returning Empty");
                        results.insert(frame.frame_id, (Node::Empty, self.pos, None));
                        return true; // Signal caller to continue to next frame
                    }
                }

                log::debug!("MATCHED Regex matched and non anti-match: {}", tok);
                let token_pos = self.pos;
                self.bump();
                let node = Node::Token(token_type.to_string(), tok.raw(), token_pos);
                results.insert(frame.frame_id, (node, self.pos, None));
                false
            }
            _ => {
                log::debug!("RegexParser didn't match '{}', returning Empty", template);
                results.insert(frame.frame_id, (Node::Empty, self.pos, None));
                false
            }
        }
    }

    /// Handle Meta grammar in iterative parser
    fn handle_meta_initial(
        &mut self,
        token_type: &'static str,
        frame: &ParseFrame,
        results: &mut std::collections::HashMap<usize, (Node, usize, Option<u64>)>,
    ) {
        log::debug!("Doing nothing with meta {}", token_type);
        results.insert(frame.frame_id, (Node::Meta(token_type), frame.pos, None));
    }

    /// Handle Nothing grammar in iterative parser
    fn handle_nothing_initial(
        &mut self,
        frame: &ParseFrame,
        results: &mut std::collections::HashMap<usize, (Node, usize, Option<u64>)>,
    ) {
        log::debug!("Nothing grammar encountered, returning Empty");
        results.insert(frame.frame_id, (Node::Empty, frame.pos, None));
    }

    /// Handle Empty grammar in iterative parser
    fn handle_empty_initial(
        &mut self,
        frame: &ParseFrame,
        results: &mut std::collections::HashMap<usize, (Node, usize, Option<u64>)>,
    ) {
        results.insert(frame.frame_id, (Node::Empty, frame.pos, None));
    }

    /// Handle Missing grammar in iterative parser
    fn handle_missing_initial(&mut self) -> Result<Node, ParseError> {
        log::debug!("Trying missing grammar");
        Err(ParseError::new("Encountered Missing grammar".into()))
    }

    /// Handle Anything grammar in iterative parser
    fn handle_anything_initial(
        &mut self,
        frame: &ParseFrame,
        parent_terminators: &[Grammar],
        results: &mut std::collections::HashMap<usize, (Node, usize, Option<u64>)>,
    ) {
        self.pos = frame.pos;
        let mut anything_tokens = vec![];

        loop {
            if self.is_terminated(parent_terminators) || self.is_at_end() {
                break;
            }
            if let Some(tok) = self.peek() {
                anything_tokens.push(Node::Token(
                    "anything".to_string(),
                    tok.raw().to_string(),
                    self.pos,
                ));
                self.bump();
            }
        }

        log::debug!("Anything matched tokens: {:?}", anything_tokens);
        results.insert(
            frame.frame_id,
            (Node::DelimitedList(anything_tokens), self.pos, None),
        );
    }

    /// Handle Bracketed grammar Initial state in iterative parser
    fn handle_bracketed_initial(
        &mut self,
        bracket_pairs: &(Box<Grammar>, Box<Grammar>),
        elements: &[Grammar],
        optional: bool,
        bracket_terminators: &[Grammar],
        reset_terminators: bool,
        allow_gaps: bool,
        parse_mode: ParseMode,
        frame: ParseFrame,
        parent_terminators: &[Grammar],
        stack: &mut Vec<ParseFrame>,
        frame_id_counter: &mut usize,
    ) {
        let start_idx = frame.pos;
        log::debug!(
            "Bracketed starting at {}, allow_gaps={}, parse_mode={:?}",
            start_idx,
            allow_gaps,
            parse_mode
        );

        // Combine parent and local terminators
        let all_terminators: Vec<Grammar> = if reset_terminators {
            bracket_terminators.to_vec()
        } else {
            bracket_terminators
                .iter()
                .cloned()
                .chain(parent_terminators.iter().cloned())
                .collect()
        };

        // Update frame with Bracketed context
        let mut frame = frame;
        frame.state = FrameState::WaitingForChild {
            child_index: 0,
            total_children: 3, // open, content, close
        };
        frame.context = FrameContext::Bracketed {
            bracket_pairs: bracket_pairs.clone(),
            elements: elements.to_vec(),
            allow_gaps,
            optional,
            parse_mode,
            state: BracketedState::MatchingOpen,
            last_child_frame_id: None,
        };
        frame.terminators = all_terminators.clone();
        stack.push(frame);

        // Start by trying to match the opening bracket
        let child_frame = ParseFrame {
            frame_id: *frame_id_counter,
            grammar: (*bracket_pairs.0).clone(),
            pos: start_idx,
            terminators: all_terminators,
            state: FrameState::Initial,
            accumulated: vec![],
            context: FrameContext::None,
            parent_max_idx: stack.last().unwrap().parent_max_idx, // Propagate parent's limit!
        };

        // Update parent's last_child_frame_id
        if let Some(parent_frame) = stack.last_mut() {
            if let FrameContext::Bracketed {
                last_child_frame_id,
                ..
            } = &mut parent_frame.context
            {
                *last_child_frame_id = Some(*frame_id_counter);
            }
        }

        *frame_id_counter += 1;
        stack.push(child_frame);
    }

    /// Handle Ref grammar Initial state in iterative parser
    /// Returns true if the caller should continue to the next iteration
    fn handle_ref_initial(
        &mut self,
        name: &str,
        optional: bool,
        allow_gaps: bool,
        ref_terminators: &[Grammar],
        reset_terminators: bool,
        frame: ParseFrame,
        parent_terminators: &[Grammar],
        stack: &mut Vec<ParseFrame>,
        frame_id_counter: &mut usize,
        iteration_count: usize,
        results: &mut std::collections::HashMap<usize, (Node, usize, Option<u64>)>,
    ) -> Result<bool, ParseError> {
        log::debug!(
            "Iterative Ref to segment: {}, optional: {}, allow_gaps: {}",
            name,
            optional,
            allow_gaps
        );
        let saved = frame.pos;
        self.pos = frame.pos;
        self.skip_transparent(allow_gaps);

        // Combine parent and local terminators
        let all_terminators: Vec<Grammar> = if reset_terminators {
            ref_terminators.to_vec()
        } else {
            ref_terminators
                .iter()
                .cloned()
                .chain(parent_terminators.iter().cloned())
                .collect()
        };

        // Look up the grammar for this segment
        let grammar_opt = self.get_segment_grammar(name);

        match grammar_opt {
            Some(child_grammar) => {
                // Get segment type for later wrapping
                let segment_type = self.dialect.get_segment_type(name).map(|s| s.to_string());

                // Create child frame to parse the target grammar
                let child_frame_id = *frame_id_counter;
                *frame_id_counter += 1;

                let child_frame = ParseFrame {
                    frame_id: child_frame_id,
                    grammar: child_grammar.clone(),
                    pos: self.pos,
                    terminators: all_terminators,
                    state: FrameState::Initial,
                    accumulated: vec![],
                    context: FrameContext::None,
                    parent_max_idx: frame.parent_max_idx, // CRITICAL: Propagate parent's limit
                };

                // Update current frame to wait for child and store Ref metadata
                let mut frame = frame;
                frame.state = FrameState::WaitingForChild {
                    child_index: 0,
                    total_children: 1,
                };
                frame.context = FrameContext::Ref {
                    name: name.to_string(),
                    optional,
                    allow_gaps,
                    segment_type,
                    saved_pos: saved,
                    last_child_frame_id: Some(child_frame_id), // Track the child we just created
                };

                // Push parent back first, then child (LIFO - child will be processed next)
                stack.push(frame);

                log::debug!("DEBUG [iter {}]: Ref({}) frame_id={} creating child frame_id={}, child grammar type: {}",
                    iteration_count,
                    name,
                    stack.last().unwrap().frame_id,
                    child_frame_id,
                    match &child_grammar {
                        Grammar::Ref { name, .. } => format!("Ref({})", name),
                        Grammar::Token { token_type } => format!("Token({})", token_type),
                        Grammar::Sequence { elements, .. } => format!("Sequence({} elements)", elements.len()),
                        Grammar::OneOf { elements, .. } => format!("OneOf({} elements)", elements.len()),
                        _ => format!("{:?}", child_grammar),
                    }
                );

                stack.push(child_frame);
                log::debug!("DEBUG [iter {}]: ABOUT TO CONTINUE - Ref({}) pushed child {}, stack size now {}",
                    iteration_count, name, child_frame_id, stack.len());
                log::debug!(
                    "DEBUG [iter {}]: ==> CONTINUING 'MAIN_LOOP NOW! <==",
                    iteration_count
                );
                Ok(true) // Signal caller to continue main loop
            }
            None => {
                self.pos = saved;
                if optional {
                    log::debug!("Iterative Ref optional (grammar not found), skipping");
                    results.insert(frame.frame_id, (Node::Empty, saved, None));
                    Ok(false) // Don't continue, we stored a result
                } else {
                    log::debug!("Iterative Ref failed (grammar not found), returning error");
                    Err(ParseError::unknown_segment(name.to_string()))
                }
            }
        }
    }

    /// Try to match a grammar at a specific position without consuming tokens
    /// Returns Some(end_pos) if the grammar matches, None otherwise
    ///
    /// This uses the same parsing logic as the main parser but in a non-destructive way,
    /// similar to how terminators are checked.
    fn try_match_grammar(
        &mut self,
        grammar: &Grammar,
        pos: usize,
        terminators: &[Grammar],
    ) -> Option<usize> {
        // Save current state
        let saved_pos = self.pos;

        // Try to parse the grammar using parse_with_grammar_cached
        // This will temporarily move the parser position but we'll restore it
        self.pos = pos;

        let result = self.parse_with_grammar_cached(grammar, terminators);

        // Get the end position before restoring
        let end_pos = self.pos;

        // Restore position regardless of match success
        self.pos = saved_pos;

        // If the grammar matched, return the end position
        match result {
            Ok(node) => {
                // Only consider it a match if we actually consumed something
                // or if it's an empty match at the exact position
                if end_pos > pos {
                    Some(end_pos)
                } else if matches!(node, Node::Empty) {
                    // Empty nodes might still be valid matches (like optional elements)
                    None
                } else {
                    Some(end_pos)
                }
            }
            Err(_) => None,
        }
    }

    /// Handle AnySetOf grammar Initial state in iterative parser
    fn handle_anysetof_initial(
        &mut self,
        elements: &[Grammar],
        min_times: usize,
        max_times: Option<usize>,
        exclude: &Option<Box<Grammar>>,
        optional: bool,
        local_terminators: &[Grammar],
        reset_terminators: bool,
        allow_gaps: bool,
        parse_mode: ParseMode,
        frame: ParseFrame,
        parent_terminators: &[Grammar],
        stack: &mut Vec<ParseFrame>,
        frame_id_counter: &mut usize,
    ) {
        let pos = frame.pos;
        log::debug!("[ITERATIVE] AnySetOf Initial state at pos {}", pos);

        // Check exclude grammar first
        if let Some(exclude_grammar) = exclude {
            // Try to match the exclude grammar at current position
            let test_result = self.try_match_grammar(exclude_grammar, pos, parent_terminators);
            if test_result.is_some() {
                // Exclude matched, so AnySetOf should return empty
                log::debug!(
                    "AnySetOf: exclude grammar matched at pos {}, returning empty",
                    pos
                );
                // Don't push frame, just return
                return;
            }
        }

        // Combine terminators
        let all_terminators: Vec<Grammar> = if reset_terminators {
            local_terminators.to_vec()
        } else {
            local_terminators
                .iter()
                .cloned()
                .chain(parent_terminators.iter().cloned())
                .collect()
        };

        // Calculate max_idx based on parse_mode
        self.pos = pos;
        let max_idx = if parse_mode == ParseMode::Greedy {
            self.trim_to_terminator(pos, &all_terminators)
        } else {
            self.tokens.len()
        };

        // Apply parent's max_idx limit (simulates Python's segments[:max_idx])
        let max_idx = if let Some(parent_limit) = frame.parent_max_idx {
            max_idx.min(parent_limit)
        } else {
            max_idx
        };

        log::debug!(
            "[ITERATIVE] AnySetOf max_idx: {} (tokens.len: {})",
            max_idx,
            self.tokens.len()
        );

        // Create AnySetOf context
        let mut frame = frame;
        frame.state = FrameState::WaitingForChild {
            child_index: 0,
            total_children: max_times.unwrap_or(usize::MAX).min(elements.len()),
        };
        frame.context = FrameContext::AnySetOf {
            min_times,
            max_times,
            allow_gaps,
            optional,
            count: 0,
            matched_idx: pos,
            working_idx: pos,
            matched_elements: std::collections::HashSet::new(),
            max_idx,
            last_child_frame_id: None,
            elements: elements.to_vec(),
            parse_mode,
        };
        frame.terminators = all_terminators.clone();

        stack.push(frame);

        // Try first unmatched element
        // For AnySetOf, we try all elements (not just first) via OneOf pattern
        let child_grammar = Grammar::OneOf {
            elements: elements.to_vec(),
            exclude: None,
            optional: false,
            terminators: vec![],
            reset_terminators: false,
            allow_gaps,
            parse_mode,
        };

        let child_frame = ParseFrame {
            frame_id: *frame_id_counter,
            grammar: child_grammar,
            pos,
            terminators: all_terminators,
            state: FrameState::Initial,
            accumulated: vec![],
            context: FrameContext::None,
            parent_max_idx: Some(max_idx), // Pass AnySetOf's max_idx to child!
        };

        // Update parent's last_child_frame_id
        if let Some(parent_frame) = stack.last_mut() {
            if let FrameContext::AnySetOf {
                last_child_frame_id,
                ..
            } = &mut parent_frame.context
            {
                *last_child_frame_id = Some(*frame_id_counter);
            }
        }

        *frame_id_counter += 1;
        stack.push(child_frame);
    }

    /// Handle AnyNumberOf grammar Initial state in iterative parser
    fn handle_anynumberof_initial(
        &mut self,
        elements: &[Grammar],
        min_times: usize,
        max_times: Option<usize>,
        max_times_per_element: Option<usize>,
        exclude: &Option<Box<Grammar>>,
        optional: bool,
        any_terminators: &[Grammar],
        reset_terminators: bool,
        allow_gaps: bool,
        parse_mode: ParseMode,
        frame: ParseFrame,
        parent_terminators: &[Grammar],
        stack: &mut Vec<ParseFrame>,
        frame_id_counter: &mut usize,
        iteration_count: usize,
    ) {
        let start_idx = frame.pos;
        log::debug!(
            "AnyNumberOf starting at {}, min_times={}, max_times={:?}, allow_gaps={}, parse_mode={:?}",
            start_idx,
            min_times,
            max_times,
            allow_gaps,
            parse_mode
        );

        // Check exclude grammar first
        if let Some(exclude_grammar) = exclude {
            // Try to match the exclude grammar at current position
            let test_result =
                self.try_match_grammar(exclude_grammar, start_idx, parent_terminators);
            if test_result.is_some() {
                // Exclude matched, so AnyNumberOf should return empty
                log::debug!(
                    "AnyNumberOf: exclude grammar matched at pos {}, returning empty",
                    start_idx
                );
                // Pop the frame we would have pushed
                // Actually, we haven't pushed yet at this point, so just return
                return;
            }
        }

        // Combine parent and local terminators
        let all_terminators: Vec<Grammar> = if reset_terminators {
            any_terminators.to_vec()
        } else {
            any_terminators
                .iter()
                .cloned()
                .chain(parent_terminators.iter().cloned())
                .collect()
        };

        // Calculate max_idx based on parse_mode
        self.pos = start_idx;
        let max_idx = if parse_mode == ParseMode::Greedy {
            self.trim_to_terminator(start_idx, &all_terminators)
        } else {
            self.tokens.len()
        };

        // Apply parent's max_idx limit (simulates Python's segments[:max_idx])
        let max_idx = if let Some(parent_limit) = frame.parent_max_idx {
            max_idx.min(parent_limit)
        } else {
            max_idx
        };

        log::debug!("DEBUG [iter {}]: AnyNumberOf Initial at pos={}, parent_max_idx={:?}, elements.len()={}",
            iteration_count, frame.pos, frame.parent_max_idx, elements.len());

        log::debug!(
            "AnyNumberOf max_idx: {} (tokens.len: {})",
            max_idx,
            self.tokens.len()
        );

        // Update frame with AnyNumberOf context
        let mut frame = frame;
        frame.state = FrameState::WaitingForChild {
            child_index: 0,
            total_children: elements.len(), // We'll loop through elements
        };
        frame.context = FrameContext::AnyNumberOf {
            elements: elements.to_vec(),
            min_times,
            max_times,
            max_times_per_element,
            allow_gaps,
            optional,
            parse_mode,
            count: 0,
            matched_idx: start_idx,
            working_idx: start_idx,
            option_counter: std::collections::HashMap::new(),
            max_idx,
            last_child_frame_id: None,
        };
        frame.terminators = all_terminators.clone();

        stack.push(frame);

        // Use OneOf wrapper to try all elements and find longest match
        if !elements.is_empty() {
            // Always wrap in OneOf to ensure optional behavior
            // This ensures that if a child fails, AnyNumberOf can handle it gracefully
            let child_grammar = Grammar::OneOf {
                elements: elements.to_vec(),
                exclude: None,
                optional: true, // Don't fail if no match (let AnyNumberOf handle it)
                terminators: all_terminators.clone(),
                reset_terminators: false,
                allow_gaps,
                parse_mode,
            };

            let child_frame = ParseFrame {
                frame_id: *frame_id_counter,
                grammar: child_grammar,
                pos: start_idx,
                terminators: all_terminators,
                state: FrameState::Initial,
                accumulated: vec![],
                context: FrameContext::None,
                parent_max_idx: Some(max_idx), // Pass AnyNumberOf's max_idx to child!
            };

            // Update parent's last_child_frame_id
            if let Some(parent_frame) = stack.last_mut() {
                if let FrameContext::AnyNumberOf {
                    last_child_frame_id,
                    ..
                } = &mut parent_frame.context
                {
                    *last_child_frame_id = Some(*frame_id_counter);
                }
            }

            *frame_id_counter += 1;
            log::debug!("DEBUG [iter {}]: AnyNumberOf Initial pushing child frame_id={}, stack size before push={}",
                iteration_count, child_frame.frame_id, stack.len());
            stack.push(child_frame);
            log::debug!(
                "DEBUG [iter {}]: AnyNumberOf Initial ABOUT TO CONTINUE after pushing child",
                iteration_count
            );
        }
    }

    /// Handle OneOf grammar Initial state in iterative parser
    /// Returns true if caller should continue main loop
    fn handle_oneof_initial(
        &mut self,
        elements: &[Grammar],
        exclude: &Option<Box<Grammar>>,
        optional: bool,
        local_terminators: &[Grammar],
        reset_terminators: bool,
        allow_gaps: bool,
        parse_mode: ParseMode,
        frame: ParseFrame,
        parent_terminators: &[Grammar],
        stack: &mut Vec<ParseFrame>,
        frame_id_counter: &mut usize,
        results: &mut std::collections::HashMap<usize, (Node, usize, Option<u64>)>,
    ) -> bool {
        let pos = frame.pos;
        log::debug!(
            "OneOf Initial state at pos {}, {} elements, parse_mode={:?}",
            pos,
            elements.len(),
            parse_mode
        );

        // Check exclude grammar first
        if let Some(exclude_grammar) = exclude {
            // Try to match the exclude grammar at current position
            let test_result = self.try_match_grammar(exclude_grammar, pos, parent_terminators);
            if test_result.is_some() {
                // Exclude matched, so OneOf should return empty
                log::debug!(
                    "OneOf: exclude grammar matched at pos {}, returning empty",
                    pos
                );
                results.insert(frame.frame_id, (Node::Empty, pos, None));
                return false; // Don't continue
            }
        }

        // Collect leading whitespace
        let leading_ws = if allow_gaps {
            self.collect_transparent(true)
        } else {
            Vec::new()
        };
        let post_skip_pos = self.pos;

        // Combine terminators
        let all_terminators: Vec<Grammar> = if reset_terminators {
            local_terminators.to_vec()
        } else {
            local_terminators
                .iter()
                .chain(parent_terminators.iter())
                .cloned()
                .collect()
        };

        // Calculate max_idx based on parse_mode (for greedy matching)
        let max_idx = if parse_mode == ParseMode::Greedy {
            self.trim_to_terminator(post_skip_pos, &all_terminators)
        } else {
            self.tokens.len()
        };

        // Apply parent's max_idx limit (simulates Python's segments[:max_idx])
        let max_idx = if let Some(parent_limit) = frame.parent_max_idx {
            max_idx.min(parent_limit)
        } else {
            max_idx
        };

        // Check if already terminated
        if self.is_terminated(&all_terminators) {
            log::debug!("OneOf: Already at terminator");
            self.pos = pos;

            // Apply parse_mode logic instead of throwing error
            let result = if optional {
                Node::Empty
            } else {
                apply_parse_mode_to_result(self.tokens, Node::Empty, pos, max_idx, parse_mode)
            };

            let final_pos = if matches!(result, Node::Empty) {
                pos
            } else {
                max_idx
            };
            self.pos = final_pos;
            results.insert(frame.frame_id, (result, final_pos, None));
            return false; // Don't continue, we stored a result
        }

        // Prune options based on simple matchers
        let available_options: Vec<Grammar> =
            self.prune_options(elements).into_iter().cloned().collect();

        if available_options.is_empty() {
            log::debug!("OneOf: No viable options after pruning");
            self.pos = pos;

            // Apply parse_mode logic instead of throwing error
            let result = if optional {
                Node::Empty
            } else {
                apply_parse_mode_to_result(self.tokens, Node::Empty, pos, max_idx, parse_mode)
            };

            let final_pos = if matches!(result, Node::Empty) {
                pos
            } else {
                max_idx
            };
            self.pos = final_pos;
            results.insert(frame.frame_id, (result, final_pos, None));
            return false; // Don't continue, we stored a result
        }

        // Create context to track OneOf matching progress
        let mut frame = frame;
        frame.context = FrameContext::OneOf {
            elements: available_options.clone(),
            allow_gaps,
            optional,
            leading_ws: leading_ws.clone(),
            post_skip_pos,
            longest_match: None,
            tried_elements: 0,
            max_idx,
            parse_mode,
            last_child_frame_id: Some(*frame_id_counter), // Track the child we're about to create
        };

        // Create child frame for first element
        let first_element = available_options[0].clone();
        let element_key = first_element.cache_key();
        log::debug!("OneOf: Trying first element (cache_key: {})", element_key);

        // Use OUR computed max_idx for the child, not the parent's parent_max_idx
        let child_frame = ParseFrame {
            frame_id: *frame_id_counter,
            grammar: first_element,
            pos: post_skip_pos,
            terminators: all_terminators.clone(),
            state: FrameState::Initial,
            accumulated: Vec::new(),
            context: FrameContext::None,
            parent_max_idx: Some(max_idx), // Pass OUR computed max_idx!
        };

        frame.state = FrameState::WaitingForChild {
            child_index: 0,
            total_children: 1, // OneOf only has one child at a time
        };

        // Context already set above, just keep it

        *frame_id_counter += 1;
        stack.push(frame); // Push parent back to stack first
        stack.push(child_frame); // Then push child
        true // Continue main loop
    }

    /// Handle Sequence grammar Initial state in iterative parser
    /// Returns true if caller should continue main loop
    fn handle_sequence_initial(
        &mut self,
        elements: &[Grammar],
        optional: bool,
        seq_terminators: &[Grammar],
        reset_terminators: bool,
        allow_gaps: bool,
        parse_mode: ParseMode,
        frame: ParseFrame,
        parent_terminators: &[Grammar],
        stack: &mut Vec<ParseFrame>,
        frame_id_counter: &mut usize,
        results: &mut std::collections::HashMap<usize, (Node, usize, Option<u64>)>,
    ) -> bool {
        let pos = frame.pos;
        log::debug!("DEBUG: Sequence Initial at pos={}, parent_max_idx={:?}, allow_gaps={}, elements.len()={}",
                  pos, frame.parent_max_idx, allow_gaps, elements.len());
        let start_idx = pos;

        // Combine parent and local terminators
        let all_terminators: Vec<Grammar> = if reset_terminators {
            seq_terminators.to_vec()
        } else {
            seq_terminators
                .iter()
                .cloned()
                .chain(parent_terminators.iter().cloned())
                .collect()
        };

        // Calculate max_idx for GREEDY mode
        self.pos = start_idx;
        let max_idx = if parse_mode == ParseMode::Greedy {
            self.trim_to_terminator(start_idx, &all_terminators)
        } else {
            self.tokens.len()
        };

        // Apply parent's max_idx limit (simulates Python's segments[:max_idx])
        let max_idx = if let Some(parent_limit) = frame.parent_max_idx {
            max_idx.min(parent_limit)
        } else {
            max_idx
        };

        // Update frame with Sequence context
        let mut frame = frame;
        frame.state = FrameState::WaitingForChild {
            child_index: 0,
            total_children: elements.len(),
        };
        frame.context = FrameContext::Sequence {
            elements: elements.to_vec(),
            allow_gaps,
            optional,
            parse_mode,
            matched_idx: start_idx,
            tentatively_collected: vec![],
            max_idx,
            original_max_idx: max_idx, // Store original before any GREEDY_ONCE_STARTED trimming
            last_child_frame_id: None,
            current_element_idx: 0, // Start at first element
            first_match: true,      // For GREEDY_ONCE_STARTED trimming
        };
        frame.terminators = all_terminators;
        let current_frame_id = frame.frame_id; // Save before moving frame
        stack.push(frame);

        // Skip to code if allow_gaps (matching Python's behavior at sequence.py line 196)
        let first_child_pos = if allow_gaps {
            self.skip_start_index_forward_to_code(start_idx, max_idx)
        } else {
            start_idx
        };

        // Push first child to parse
        if !elements.is_empty() {
            // Check if we've run out of segments before first element
            if first_child_pos >= max_idx {
                // Haven't matched anything yet and already at limit
                // Pop the frame we just pushed since we're returning early
                stack.pop();

                if parse_mode == ParseMode::Strict {
                    // In strict mode, return Empty
                    results.insert(current_frame_id, (Node::Empty, start_idx, None));
                    return false; // Don't continue, we stored a result
                }
                // In greedy modes, check if first element is optional
                if elements[0].is_optional() {
                    // First element is optional, can skip
                    results.insert(current_frame_id, (Node::Empty, start_idx, None));
                    return false;
                } else {
                    // Required element, no segments - this is unparsable in greedy mode
                    results.insert(current_frame_id, (Node::Empty, start_idx, None));
                    return false;
                }
            }

            // Handle Meta elements specially
            let mut child_idx = 0;
            while child_idx < elements.len() {
                if let Grammar::Meta(meta_type) = &elements[child_idx] {
                    // Meta doesn't need parsing - just add to accumulated
                    if let Some(ref mut parent_frame) = stack.last_mut() {
                        if *meta_type == "indent" {
                            // Indent goes before whitespace
                            let mut insert_pos = parent_frame.accumulated.len();
                            while insert_pos > 0 {
                                match &parent_frame.accumulated[insert_pos - 1] {
                                    Node::Whitespace(_, _) | Node::Newline(_, _) => {
                                        insert_pos -= 1;
                                    }
                                    _ => break,
                                }
                            }
                            parent_frame
                                .accumulated
                                .insert(insert_pos, Node::Meta(meta_type));
                        } else {
                            parent_frame.accumulated.push(Node::Meta(meta_type));
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
                    child_idx += 1;
                } else {
                    // Get max_idx from parent Sequence to pass to child
                    let current_max_idx = if let Some(parent_frame) = stack.last() {
                        if let FrameContext::Sequence { max_idx, .. } = &parent_frame.context {
                            Some(*max_idx)
                        } else {
                            None
                        }
                    } else {
                        None
                    };

                    // Non-meta element - needs actual parsing
                    log::debug!(
                        "DEBUG: Creating FIRST child at pos={}, max_idx={}",
                        first_child_pos,
                        max_idx
                    );
                    let child_frame = ParseFrame {
                        frame_id: *frame_id_counter,
                        grammar: elements[child_idx].clone(),
                        pos: first_child_pos, // Use position after skipping to code!
                        terminators: stack
                            .last()
                            .map(|f| f.terminators.clone())
                            .unwrap_or_default(),
                        state: FrameState::Initial,
                        accumulated: vec![],
                        context: FrameContext::None,
                        parent_max_idx: current_max_idx, // Pass Sequence's max_idx to child!
                    };

                    // Update parent (already on stack) and push child
                    ParseFrame::update_sequence_parent_and_push_child(
                        stack,
                        child_frame,
                        frame_id_counter,
                        child_idx,
                    );
                    return true; // Continue to process the child we just pushed
                }
            }
        }

        false // No child pushed, don't continue
    }

    /// Handle Delimited grammar Initial state in iterative parser
    /// Returns true if caller should continue main loop
    fn handle_delimited_initial(
        &mut self,
        elements: &[Grammar],
        delimiter: &Box<Grammar>,
        allow_trailing: bool,
        optional: bool,
        local_terminators: &[Grammar],
        reset_terminators: bool,
        allow_gaps: bool,
        min_delimiters: usize,
        parse_mode: ParseMode,
        frame: ParseFrame,
        parent_terminators: &[Grammar],
        stack: &mut Vec<ParseFrame>,
        frame_id_counter: &mut usize,
        results: &mut std::collections::HashMap<usize, (Node, usize, Option<u64>)>,
    ) -> bool {
        let pos = frame.pos;
        log::debug!("[ITERATIVE] Delimited Initial state at pos {}", pos);

        // Combine terminators, filtering out delimiter from parent terminators
        // This is critical - delimiter shouldn't terminate the delimited list itself
        let filtered_parent: Vec<Grammar> = parent_terminators
            .iter()
            .filter(|t| *t != delimiter.as_ref())
            .cloned()
            .collect();

        let all_terminators: Vec<Grammar> = if reset_terminators {
            local_terminators.to_vec()
        } else {
            local_terminators
                .iter()
                .cloned()
                .chain(filtered_parent.into_iter())
                .collect()
        };

        // Calculate max_idx based on parse_mode and terminators
        self.pos = pos;
        let max_idx = if parse_mode == ParseMode::Greedy {
            // In GREEDY mode, actively look for terminators
            self.trim_to_terminator(pos, &all_terminators)
        } else {
            // In STRICT mode, still need to respect terminators if they exist
            // Check if there's a terminator anywhere ahead
            if all_terminators.is_empty() {
                self.tokens.len()
            } else {
                self.trim_to_terminator(pos, &all_terminators)
            }
        };

        // Apply parent's max_idx limit (simulates Python's segments[:max_idx])
        let max_idx = if let Some(parent_limit) = frame.parent_max_idx {
            max_idx.min(parent_limit)
        } else {
            max_idx
        };

        log::debug!(
            "[ITERATIVE] Delimited max_idx: {} (tokens.len: {}), parse_mode={:?}, terminators.len={}",
            max_idx,
            self.tokens.len(),
            parse_mode,
            all_terminators.len()
        );

        // Debug terminators for function-related Delimited
        if elements.iter().any(|e| {
            matches!(e, Grammar::Ref { name, .. } if name.contains("FunctionContents") || name.contains("DatetimeUnit"))
        }) {
            log::debug!("[DELIMITED-DEBUG] Active terminators (count={}):", all_terminators.len());
            for (i, term) in all_terminators.iter().enumerate() {
                match term {
                    Grammar::StringParser { template, .. } => {
                        log::debug!("  [{}] StringParser('{}')", i, template);
                    }
                    Grammar::Ref { name, .. } => {
                        log::debug!("  [{}] Ref({})", i, name);
                    }
                    _ => {
                        log::debug!("  [{}] {:?}", i, format!("{:?}", term).chars().take(80).collect::<String>());
                    }
                }
            }
        }

        // Check if optional and already terminated
        if optional && (self.is_at_end() || self.is_terminated(&all_terminators)) {
            log::debug!("[ITERATIVE] Delimited: empty optional");
            results.insert(frame.frame_id, (Node::DelimitedList(vec![]), pos, None));
            return false; // Don't continue, we stored a result
        }

        // Create Delimited context
        let mut frame = frame;
        frame.state = FrameState::WaitingForChild {
            child_index: 0,
            total_children: usize::MAX, // Unknown number of children
        };
        frame.context = FrameContext::Delimited {
            elements: elements.to_vec(),
            delimiter: delimiter.clone(),
            allow_trailing,
            optional,
            allow_gaps,
            min_delimiters,
            parse_mode,
            delimiter_count: 0,
            matched_idx: pos,
            working_idx: pos,
            max_idx,
            state: DelimitedState::MatchingElement,
            last_child_frame_id: None,
        };
        frame.terminators = all_terminators.clone();

        // Extract max_idx before moving frame - this is the limit for children!
        // Children should be constrained by the Delimited's calculated max_idx
        let child_max_idx = max_idx;
        stack.push(frame);

        // Create first child to match element (try all elements via OneOf)
        let child_grammar = Grammar::OneOf {
            elements: elements.to_vec(),
            exclude: None,
            optional: true, // Elements in Delimited are implicitly optional
            terminators: vec![],
            reset_terminators: false,
            allow_gaps,
            parse_mode,
        };

        // Debug logging for specific grammars
        if elements.iter().any(|e| {
            matches!(e, Grammar::Ref { name, .. } if name.contains("FunctionContents") || name.contains("DatetimeUnit"))
        }) {
            log::debug!("[DELIMITED-DEBUG] Creating Delimited OneOf with {} elements at pos {}, max_idx={}", elements.len(), pos, child_max_idx);
            for (i, elem) in elements.iter().enumerate() {
                match elem {
                    Grammar::Ref { name, optional, .. } => {
                        log::debug!("  [{}] Ref({}) optional={}", i, name, optional);
                    }
                    _ => {
                        log::debug!("  [{}] {:?}", i, elem);
                    }
                }
            }
        }

        let child_frame = ParseFrame::new_child(
            *frame_id_counter,
            child_grammar,
            pos,
            all_terminators,
            Some(child_max_idx), // Use Delimited's max_idx!
        );

        // Update parent's last_child_frame_id and push child
        ParseFrame::update_parent_last_child_id(stack, "Delimited", *frame_id_counter);
        *frame_id_counter += 1;
        stack.push(child_frame);
        true // Continue to process the child frame we just pushed
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

        // NOTE: We do NOT disable use_iterative_parser here anymore.
        // All grammars should use frame-based implementation inside the loop below.
        // If a grammar calls parse_with_grammar_cached(), it will check the flag
        // and come back here, maintaining the iterative approach.

        // Track results for completed parses
        // HashMap: frame_id -> (node, pos, element_key)
        // element_key is Some(key) for OneOf matches, None for other grammars
        let mut results: std::collections::HashMap<usize, (Node, usize, Option<u64>)> =
            std::collections::HashMap::new();
        let mut frame_id_counter = 0_usize;

        // Stack of parse frames
        let initial_frame_id = frame_id_counter;
        frame_id_counter += 1;

        let mut stack: Vec<ParseFrame> = vec![ParseFrame {
            frame_id: initial_frame_id,
            grammar: grammar.clone(),
            pos: self.pos,
            terminators: parent_terminators.to_vec(),
            state: FrameState::Initial,
            accumulated: vec![],
            context: FrameContext::None,
            parent_max_idx: None, // Top-level frame has no parent limit
        }];

        let mut iteration_count = 0_usize;
        let max_iterations = 1500000_usize; // Higher limit for complex grammars

        'main_loop: while let Some(mut frame) = stack.pop() {
            iteration_count += 1;

            if iteration_count > max_iterations {
                eprintln!("ERROR: Exceeded max iterations ({})", max_iterations);
                eprintln!("Last frame: {:?}", frame.grammar);
                eprintln!("Stack depth: {}", stack.len());
                eprintln!("Results count: {}", results.len());

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
            if iteration_count % 5000 == 0 {
                log::debug!(
                    "\nDEBUG [iter {}]: Processing frame_id={}, state={:?}",
                    iteration_count,
                    frame.frame_id,
                    frame.state
                );
                log::debug!(
                    "  Stack size: {}, Results size: {}",
                    stack.len(),
                    results.len()
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
                    // Start parsing this grammar - clone the grammar to avoid borrow issues
                    let grammar = frame.grammar.clone();
                    let terminators = frame.terminators.clone();
                    let pos = frame.pos;

                    match &grammar {
                        // Simple leaf grammars - parse directly without recursion
                        Grammar::Token { token_type } => {
                            self.handle_token_initial(token_type, &frame, &mut results)?;
                        }

                        Grammar::StringParser {
                            template,
                            token_type,
                            ..
                        } => {
                            self.handle_string_parser_initial(
                                template,
                                token_type,
                                &frame,
                                iteration_count,
                                &mut results,
                            );
                        }

                        Grammar::MultiStringParser {
                            templates,
                            token_type,
                            ..
                        } => {
                            self.handle_multi_string_parser_initial(
                                templates,
                                token_type,
                                &frame,
                                &mut results,
                            );
                        }

                        Grammar::TypedParser {
                            template,
                            token_type,
                            ..
                        } => {
                            self.handle_typed_parser_initial(
                                template,
                                token_type,
                                &frame,
                                &mut results,
                            );
                        }

                        Grammar::RegexParser {
                            template,
                            token_type,
                            anti_template,
                            ..
                        } => {
                            if self.handle_regex_parser_initial(
                                template,
                                anti_template,
                                token_type,
                                &frame,
                                &mut results,
                            ) {
                                continue 'main_loop; // Anti-template matched, skip to next frame
                            }
                        }

                        Grammar::Meta(token_type) => {
                            self.handle_meta_initial(token_type, &frame, &mut results);
                        }

                        Grammar::Nothing() => {
                            self.handle_nothing_initial(&frame, &mut results);
                        }

                        Grammar::Empty => {
                            self.handle_empty_initial(&frame, &mut results);
                        }

                        Grammar::Missing => {
                            return self.handle_missing_initial();
                        }

                        Grammar::Anything => {
                            self.handle_anything_initial(&frame, &terminators, &mut results);
                        }

                        // Complex grammars - need special handling
                        Grammar::Sequence {
                            elements,
                            optional,
                            terminators: seq_terminators,
                            reset_terminators,
                            allow_gaps,
                            parse_mode,
                        } => {
                            if self.handle_sequence_initial(
                                elements,
                                *optional,
                                seq_terminators,
                                *reset_terminators,
                                *allow_gaps,
                                *parse_mode,
                                frame,
                                &terminators,
                                &mut stack,
                                &mut frame_id_counter,
                                &mut results,
                            ) {
                                continue 'main_loop;
                            }
                        }

                        Grammar::OneOf {
                            elements,
                            exclude,
                            optional,
                            terminators: local_terminators,
                            reset_terminators,
                            allow_gaps,
                            parse_mode,
                        } => {
                            if self.handle_oneof_initial(
                                elements,
                                exclude,
                                *optional,
                                local_terminators,
                                *reset_terminators,
                                *allow_gaps,
                                *parse_mode,
                                frame,
                                &terminators,
                                &mut stack,
                                &mut frame_id_counter,
                                &mut results,
                            ) {
                                continue 'main_loop;
                            }
                        }

                        Grammar::Ref {
                            name,
                            optional,
                            allow_gaps,
                            terminators: ref_terminators,
                            reset_terminators,
                        } => {
                            if self.handle_ref_initial(
                                name,
                                *optional,
                                *allow_gaps,
                                ref_terminators,
                                *reset_terminators,
                                frame,
                                &terminators,
                                &mut stack,
                                &mut frame_id_counter,
                                iteration_count,
                                &mut results,
                            )? {
                                continue 'main_loop;
                            }
                        }

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
                        } => {
                            self.handle_anynumberof_initial(
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
                                &mut stack,
                                &mut frame_id_counter,
                                iteration_count,
                            );
                            continue 'main_loop;
                        }

                        Grammar::Bracketed {
                            elements,
                            bracket_pairs,
                            optional,
                            terminators: bracket_terminators,
                            reset_terminators,
                            allow_gaps,
                            parse_mode,
                        } => {
                            self.handle_bracketed_initial(
                                bracket_pairs,
                                elements,
                                *optional,
                                bracket_terminators,
                                *reset_terminators,
                                *allow_gaps,
                                *parse_mode,
                                frame,
                                &terminators,
                                &mut stack,
                                &mut frame_id_counter,
                            );
                            continue 'main_loop;
                        }

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
                        } => {
                            self.handle_anysetof_initial(
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
                                &mut stack,
                                &mut frame_id_counter,
                            );
                            continue 'main_loop;
                        }

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
                        } => {
                            if self.handle_delimited_initial(
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
                                &mut stack,
                                &mut frame_id_counter,
                                &mut results,
                            ) {
                                continue 'main_loop;
                            }
                        }
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
                        results.get(&child_frame_id)
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
                        if iteration_count % 100 == 0 || iteration_count < 200 {
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

                                results.insert(frame.frame_id, (final_node, self.pos, None));
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
                                        results
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
                                                        frame.accumulated.push(Node::Whitespace(
                                                            tok.raw().to_string(),
                                                            check_pos,
                                                        ));
                                                        tentatively_collected.push(check_pos);
                                                    } else if tok_type == "newline" {
                                                        log::debug!("RETROACTIVELY collecting newline at {}: {:?}", check_pos, tok.raw());
                                                        frame.accumulated.push(Node::Newline(
                                                            tok.raw().to_string(),
                                                            check_pos,
                                                        ));
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
                                    self.pos = current_matched_idx;
                                    log::debug!(
                                        "Sequence frame_id={}: Collecting trailing tokens from pos {} to {}, allow_gaps={}",
                                        frame.frame_id, self.pos, self.tokens.len(), current_allow_gaps
                                    );
                                    while self.pos < self.tokens.len() {
                                        if let Some(tok) = self.peek() {
                                            if tok.is_code() {
                                                log::debug!("Sequence frame_id={}: Stopped at code token at pos {}", frame.frame_id, self.pos);
                                                break; // Stop at code tokens
                                            }
                                            let tok_type = tok.get_type();
                                            let already_collected = self
                                                .collected_transparent_positions
                                                .contains(&self.pos);
                                            log::debug!(
                                                "Sequence frame_id={}: Checking pos {}, type={}, already_collected={}",
                                                frame.frame_id, self.pos, tok_type, already_collected
                                            );
                                            if tok_type == "whitespace" {
                                                if current_allow_gaps
                                                    && !self
                                                        .collected_transparent_positions
                                                        .contains(&self.pos)
                                                    && !tentatively_collected.contains(&self.pos)
                                                {
                                                    frame.accumulated.push(Node::Whitespace(
                                                        tok.raw().to_string(),
                                                        self.pos,
                                                    ));
                                                    tentatively_collected.push(self.pos);
                                                }
                                            } else if tok_type == "newline" {
                                                if current_allow_gaps
                                                    && !self
                                                        .collected_transparent_positions
                                                        .contains(&self.pos)
                                                    && !tentatively_collected.contains(&self.pos)
                                                {
                                                    frame.accumulated.push(Node::Newline(
                                                        tok.raw().to_string(),
                                                        self.pos,
                                                    ));
                                                    tentatively_collected.push(self.pos);
                                                }
                                            } else if tok_type == "end_of_file" {
                                                // Always collect end_of_file if it hasn't been collected yet
                                                if !self
                                                    .collected_transparent_positions
                                                    .contains(&self.pos)
                                                    && !tentatively_collected.contains(&self.pos)
                                                {
                                                    log::debug!("Sequence frame_id={}: COLLECTING end_of_file at position {}", frame.frame_id, self.pos);
                                                    frame.accumulated.push(Node::EndOfFile(
                                                        tok.raw().to_string(),
                                                        self.pos,
                                                    ));
                                                    tentatively_collected.push(self.pos);
                                                }
                                            }
                                            self.bump();
                                        } else {
                                            break;
                                        }
                                    }
                                    // Update matched_idx to current position after collecting trailing tokens
                                    let current_matched_idx = self.pos;
                                    log::debug!("DEBUG: Sequence completing - frame_id={}, self.pos={}, current_matched_idx={}, elements.len={}, accumulated.len={}",
                                        frame.frame_id, self.pos, current_matched_idx, elements_clone.len(), frame.accumulated.len());

                                    let result_node = if frame.accumulated.is_empty() {
                                        log::debug!("WARNING: Sequence completing with EMPTY accumulated! frame_id={}, current_elem_idx={}, elements.len={}",
                                                  frame.frame_id, current_elem_idx, elements_clone.len());
                                        Node::Empty
                                    } else {
                                        Node::Sequence(frame.accumulated.clone())
                                    };
                                    log::debug!(
                                        "Sequence COMPLETE: Storing result at frame_id={}",
                                        frame.frame_id
                                    );
                                    results.insert(
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
                                                    if tok_type == "whitespace" {
                                                        log::debug!(
                                                            "COLLECTING whitespace at {}: {:?}",
                                                            collect_pos,
                                                            tok.raw()
                                                        );
                                                        frame.accumulated.push(Node::Whitespace(
                                                            tok.raw().to_string(),
                                                            collect_pos,
                                                        ));
                                                        tentatively_collected.push(collect_pos);
                                                    } else if tok_type == "newline" {
                                                        log::debug!(
                                                            "COLLECTING newline at {}: {:?}",
                                                            collect_pos,
                                                            tok.raw()
                                                        );
                                                        frame.accumulated.push(Node::Newline(
                                                            tok.raw().to_string(),
                                                            collect_pos,
                                                        ));
                                                        tentatively_collected.push(collect_pos);
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
                                                Node::Sequence(frame.accumulated.clone())
                                            };
                                            results.insert(
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
                                                results.insert(
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
                                                let result_node =
                                                    Node::Sequence(frame.accumulated.clone());
                                                results.insert(
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
                                                        Node::Whitespace(_, _)
                                                        | Node::Newline(_, _) => {
                                                            insert_pos -= 1;
                                                        }
                                                        _ => break,
                                                    }
                                                }
                                                final_accumulated
                                                    .insert(insert_pos, Node::Meta(meta_type));
                                                frame
                                                    .accumulated
                                                    .insert(insert_pos, Node::Meta(meta_type));
                                            } else {
                                                final_accumulated.push(Node::Meta(meta_type));
                                                frame.accumulated.push(Node::Meta(meta_type));
                                            }
                                            next_elem_idx += 1;
                                        } else {
                                            // Non-Meta element - create frame for it
                                            log::debug!(
                                                "Creating child frame for element {}: frame_id={}, parent_max_idx={}",
                                                next_elem_idx,
                                                frame_id_counter,
                                                current_original_max_idx
                                            );

                                            let child_frame = ParseFrame::new_child(
                                                frame_id_counter,
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
                                                &mut frame_id_counter,
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
                                        Node::Sequence(final_accumulated)
                                    };
                                    results.insert(
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
                                max_times_per_element,
                                allow_gaps,
                                optional,
                                parse_mode,
                                count,
                                matched_idx,
                                working_idx,
                                option_counter,
                                max_idx,
                                last_child_frame_id: _last_child_frame_id,
                            } => {
                                log::debug!(
                                    "AnyNumberOf WaitingForChild: count={}, child_node empty={}, matched_idx={}, working_idx={}",
                                    count,
                                    child_node.is_empty(),
                                    matched_idx,
                                    working_idx
                                );

                                // Handle the child result
                                if !child_node.is_empty() {
                                    // Successfully matched!

                                    // Collect transparent tokens if allow_gaps
                                    if *allow_gaps && *matched_idx < *working_idx {
                                        while *matched_idx < *working_idx {
                                            if let Some(tok) = self.tokens.get(*matched_idx) {
                                                let tok_type = tok.get_type();
                                                if tok_type == "whitespace" {
                                                    frame.accumulated.push(Node::Whitespace(
                                                        tok.raw().to_string(),
                                                        *matched_idx,
                                                    ));
                                                } else if tok_type == "newline" {
                                                    frame.accumulated.push(Node::Newline(
                                                        tok.raw().to_string(),
                                                        *matched_idx,
                                                    ));
                                                }
                                            }
                                            *matched_idx += 1;
                                        }
                                    }

                                    // Add the matched node
                                    frame.accumulated.push(child_node.clone());
                                    *matched_idx = *child_end_pos;
                                    *working_idx = *matched_idx;
                                    *count += 1;

                                    // Update option_counter with the element_key from OneOf child
                                    let element_key = child_element_key.unwrap_or(0);
                                    *option_counter.entry(element_key).or_insert(0) += 1;

                                    log::debug!(
                                        "AnyNumberOf: matched element #{}, element_key={}, matched_idx now: {}",
                                        count, element_key, matched_idx
                                    );

                                    // Python behavior: Check for complete match (consumed all to max_idx)
                                    // If we've consumed all available segments, stop trying more matches
                                    let reached_max = *matched_idx >= *max_idx;

                                    if reached_max {
                                        log::debug!(
                                            "AnyNumberOf: Complete match (reached max_idx={}), stopping iteration",
                                            max_idx
                                        );
                                    }

                                    // Check if we've reached limits
                                    let should_continue = !reached_max
                                        && (*count < *min_times
                                            || (max_times.is_none()
                                                || *count < max_times.unwrap()));

                                    if should_continue {
                                        // Continue loop - try matching next element
                                        // Update working_idx to skip whitespace if allowed
                                        if *allow_gaps {
                                            *working_idx = self.skip_start_index_forward_to_code(
                                                *working_idx,
                                                *max_idx,
                                            );
                                        }

                                        // Create OneOf wrapper to try all elements (proper longest-match)
                                        if !elements.is_empty() {
                                            // Optimization: if only one element, use it directly (avoid OneOf overhead)
                                            let child_grammar = if elements.len() == 1 {
                                                elements[0].clone()
                                            } else {
                                                // Multiple elements: wrap in OneOf for longest-match selection
                                                Grammar::OneOf {
                                                    elements: elements.clone(),
                                                    exclude: None,
                                                    optional: true, // Let AnyNumberOf handle empty
                                                    terminators: frame_terminators.clone(),
                                                    reset_terminators: false,
                                                    allow_gaps: *allow_gaps,
                                                    parse_mode: *parse_mode,
                                                }
                                            };

                                            let child_frame = ParseFrame::new_child(
                                                frame_id_counter,
                                                child_grammar,
                                                *working_idx,
                                                frame_terminators.clone(),
                                                Some(*max_idx), // Pass AnyNumberOf's max_idx to child!
                                            );

                                            ParseFrame::push_child_and_update_parent(
                                                &mut stack,
                                                frame,
                                                child_frame,
                                                &mut frame_id_counter,
                                                "AnyNumberOf",
                                            );
                                            log::debug!("DEBUG [iter {}]: AnyNumberOf pushed parent and child, stack.len()={}", iteration_count, stack.len());
                                            continue 'main_loop; // Exit the WaitingForChild handler - continue to next iteration
                                        }
                                    } else {
                                        // Done with loop - complete the frame
                                        self.pos = *matched_idx;
                                        let result_node =
                                            Node::DelimitedList(frame.accumulated.clone());
                                        log::debug!(
                                            "AnyNumberOf COMPLETE: {} matches, storing result at frame_id={}",
                                            count,
                                            frame.frame_id
                                        );
                                        results.insert(
                                            frame.frame_id,
                                            (result_node, *matched_idx, None),
                                        );
                                        continue; // Frame is complete, move to next frame
                                    }
                                } else {
                                    // Child failed to match
                                    log::debug!(
                                        "AnyNumberOf: child failed to match at position {}",
                                        working_idx
                                    );

                                    // Check if we've met min_times
                                    if *count < *min_times {
                                        // Haven't met minimum occurrences - return Empty
                                        // Let the parent grammar decide if this is a failure or not
                                        self.pos = frame.pos;
                                        log::debug!(
                                            "AnyNumberOf returning Empty (didn't meet min_times {} < {})",
                                            count,
                                            min_times
                                        );
                                        results
                                            .insert(frame.frame_id, (Node::Empty, frame.pos, None));
                                        continue; // Frame is complete, move to next frame
                                    } else {
                                        // We've met min_times - complete with what we have
                                        self.pos = *matched_idx;
                                        let result_node =
                                            Node::DelimitedList(frame.accumulated.clone());
                                        log::debug!(
                                            "AnyNumberOf COMPLETE (child failed): {} matches, storing result at frame_id={}",
                                            count,
                                            frame.frame_id
                                        );
                                        results.insert(
                                            frame.frame_id,
                                            (result_node, *matched_idx, None),
                                        );
                                        continue; // Frame is complete, move to next frame
                                    }
                                }
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
                                            results.insert(
                                                frame.frame_id,
                                                (Node::Empty, frame.pos, None),
                                            );
                                        } else {
                                            // Opening bracket matched!
                                            frame.accumulated.push(child_node.clone());
                                            let content_start_idx = *child_end_pos;

                                            // OPTIMIZATION: Use pre-computed matching bracket to set tight max_idx
                                            // This prevents exploring beyond the closing bracket
                                            let bracket_max_idx = child_node
                                                .get_token_idx()
                                                .and_then(|open_idx| self.get_matching_bracket_idx(open_idx));

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
                                                                Node::Whitespace(
                                                                    tok.raw().to_string(),
                                                                    pos,
                                                                ),
                                                            );
                                                        } else if tok_type == "newline" {
                                                            frame.accumulated.push(Node::Newline(
                                                                tok.raw().to_string(),
                                                                pos,
                                                            ));
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
                                            let child_frame = ParseFrame {
                                                frame_id: frame_id_counter,
                                                grammar: content_grammar,
                                                pos: self.pos,
                                                terminators: vec![(*bracket_pairs.1).clone()],
                                                state: FrameState::Initial,
                                                accumulated: vec![],
                                                context: FrameContext::None,
                                                parent_max_idx: bracket_max_idx, // Tight boundary from pre-computed bracket!
                                            };

                                            // Update this frame's last_child_frame_id
                                            *last_child_frame_id = Some(frame_id_counter);

                                            frame_id_counter += 1;

                                            // Push parent frame back first, then child (LIFO - child will be processed next)
                                            stack.push(frame);
                                            stack.push(child_frame);
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
                                                    Node::Sequence(children)
                                                    | Node::DelimitedList(children) => {
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
                                                        frame.accumulated.push(Node::Whitespace(
                                                            tok.raw().to_string(),
                                                            pos,
                                                        ));
                                                    } else if tok_type == "newline" {
                                                        frame.accumulated.push(Node::Newline(
                                                            tok.raw().to_string(),
                                                            pos,
                                                        ));
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
                                                results.insert(
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
                                            let child_frame = ParseFrame {
                                                frame_id: frame_id_counter,
                                                grammar: (*bracket_pairs.1).clone(),
                                                pos: self.pos,
                                                terminators: vec![(*bracket_pairs.1).clone()],
                                                state: FrameState::Initial,
                                                accumulated: vec![],
                                                context: FrameContext::None,
                                                parent_max_idx: parent_limit, // Propagate parent's limit!
                                            };

                                            // Update this frame's last_child_frame_id
                                            *last_child_frame_id = Some(frame_id_counter);

                                            frame_id_counter += 1;

                                            // Push parent frame back first, then child (LIFO - child will be processed next)
                                            stack.push(frame);
                                            stack.push(child_frame);
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
                                                results.insert(
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

                                            let result_node =
                                                Node::Bracketed(frame.accumulated.clone());
                                            log::debug!(
                                                "Bracketed COMPLETE: {} children, storing result at frame_id={}",
                                                frame.accumulated.len(),
                                                frame.frame_id
                                            );
                                            results.insert(
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
                                            results.insert(
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
                                        let result_node =
                                            Node::DelimitedList(frame.accumulated.clone());
                                        results.insert(
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
                                                    frame.accumulated.push(Node::Whitespace(
                                                        tok.raw().to_string(),
                                                        check_pos,
                                                    ));
                                                    self.collected_transparent_positions
                                                        .insert(check_pos);
                                                } else if tok_type == "newline" {
                                                    frame.accumulated.push(Node::Newline(
                                                        tok.raw().to_string(),
                                                        check_pos,
                                                    ));
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
                                        let result_node =
                                            Node::DelimitedList(frame.accumulated.clone());
                                        results.insert(
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
                                            let result_node =
                                                Node::DelimitedList(frame.accumulated.clone());
                                            results.insert(
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
                                                frame_id_counter,
                                                child_grammar,
                                                *working_idx,
                                                frame_terminators.clone(),
                                                parent_limit, // Propagate parent's limit!
                                            );

                                            ParseFrame::push_child_and_update_parent(
                                                &mut stack,
                                                frame,
                                                child_frame,
                                                &mut frame_id_counter,
                                                "AnySetOf",
                                            );
                                            continue 'main_loop; // Continue to process the child we just pushed
                                        }
                                    }
                                }
                            }

                            FrameContext::OneOf {
                                elements,
                                allow_gaps,
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
                                        frame_id_counter,
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
                                        &mut frame_id_counter,
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
                                            Node::Sequence(children)
                                        } else {
                                            best_node.clone()
                                        };

                                        log::debug!(
                                            "OneOf: Returning longest match with element_key={}",
                                            best_element_key
                                        );
                                        // Store result WITH element_key so parent grammars can use it
                                        results.insert(
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
                                        results
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
                                            Node::Sequence(items) => format!("Sequence({} items)", items.len()),
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
                                            results.insert(
                                                frame.frame_id,
                                                (
                                                    Node::DelimitedList(frame.accumulated.clone()),
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
                                                                Node::Whitespace(
                                                                    tok.raw().to_string(),
                                                                    check_pos,
                                                                ),
                                                            );
                                                            self.collected_transparent_positions
                                                                .insert(check_pos);
                                                        } else if tok_type == "newline" {
                                                            frame.accumulated.push(Node::Newline(
                                                                tok.raw().to_string(),
                                                                check_pos,
                                                            ));
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
                                                results.insert(
                                                    frame.frame_id,
                                                    (
                                                        Node::DelimitedList(
                                                            frame.accumulated.clone(),
                                                        ),
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
                                                    frame_id_counter,
                                                    (**delimiter).clone(),
                                                    *working_idx,
                                                    frame_terminators.clone(),
                                                    Some(child_max_idx),
                                                );

                                                ParseFrame::push_child_and_update_parent(
                                                    &mut stack,
                                                    frame,
                                                    child_frame,
                                                    &mut frame_id_counter,
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
                                                    results.insert(
                                                        frame.frame_id,
                                                        (
                                                            Node::DelimitedList(
                                                                frame.accumulated.clone(),
                                                            ),
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
                                                results.insert(
                                                    frame.frame_id,
                                                    (
                                                        Node::DelimitedList(
                                                            frame.accumulated.clone(),
                                                        ),
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
                                                                Node::Whitespace(
                                                                    tok.raw().to_string(),
                                                                    check_pos,
                                                                ),
                                                            );
                                                            self.collected_transparent_positions
                                                                .insert(check_pos);
                                                        } else if tok_type == "newline" {
                                                            frame.accumulated.push(Node::Newline(
                                                                tok.raw().to_string(),
                                                                check_pos,
                                                            ));
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
                                                results.insert(
                                                    frame.frame_id,
                                                    (
                                                        Node::DelimitedList(
                                                            frame.accumulated.clone(),
                                                        ),
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
                                                    results.insert(
                                                        frame.frame_id,
                                                        (
                                                            Node::DelimitedList(
                                                                frame.accumulated.clone(),
                                                            ),
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
                                                    frame_id_counter,
                                                    child_grammar,
                                                    *working_idx,
                                                    frame_terminators.clone(),
                                                    Some(child_max_idx),
                                                );

                                                ParseFrame::push_child_and_update_parent(
                                                    &mut stack,
                                                    frame,
                                                    child_frame,
                                                    &mut frame_id_counter,
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
                        if iteration_count > 100 && iteration_count % 100 == 0 {
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
                        stack.push(frame);
                        continue;
                    }
                }

                FrameState::Combining => {
                    // TODO: Handle combining results
                    unimplemented!("Combining state not yet implemented");
                }

                FrameState::Complete(node) => {
                    // This frame is done
                    results.insert(frame.frame_id, (node, self.pos, None));
                }
            }
        }

        // Return the result from the initial frame
        log::debug!("DEBUG: Main loop ended. Stack has {} frames left. Results has {} entries. Looking for frame_id={}",
            stack.len(),
            results.len(),
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
            results.len(),
            initial_frame_id
        );
        for (fid, (_node, _pos, _key)) in results.iter() {
            log::debug!("  Result frame_id={}", fid);
        }
        if let Some((node, end_pos, _element_key)) = results.get(&initial_frame_id) {
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
                "Iterative parse produced no result (initial_frame_id={}, results has {} entries)",
                initial_frame_id,
                results.len()
            ));
            self.parse_cache.put(cache_key, Err(error.clone()));
            Err(error)
        }
    }
}
