use std::vec;
use std::{
    fmt::Display,
    hash::{Hash, Hasher},
};

use crate::{
    dialect::Dialect,
    parser_cache::{CacheKey, ParseCache},
    token::Token,
    parser::{ParseFrame, FrameState, FrameContext, BracketedState, DelimitedState},
};

// Re-export types from the new parser module for backward compatibility
pub use crate::parser::{Grammar, ParseMode, Node, ParseError, SegmentDef, Parsed, ParseErrorType, ParseContext};

// Import utility functions
use crate::parser::utils::{
    tag_keyword_if_word, is_grammar_optional, apply_parse_mode_to_result
};

// Import macros
use crate::find_longest_match;

pub struct Parser<'a> {
    pub tokens: &'a [Token],
    pub pos: usize, // current position in tokens
    pub dialect: Dialect,
    pub parse_cache: ParseCache,
    pub collected_transparent_positions: std::collections::HashSet<usize>, // Track which token positions have had transparent tokens collected
    pub use_iterative_parser: bool, // Full iterative parser (experimental)
}

impl<'a> Parser<'_> {
    /// Fully iterative parser using explicit stack
    ///
    /// This replaces recursive `parse_with_grammar` calls with an explicit
    /// stack-based state machine to avoid stack overflow on deeply nested grammars.
    pub fn parse_iterative(
        &mut self,
        grammar: &Grammar,
        parent_terminators: &[Grammar],
    ) -> Result<Node, ParseError> {
        log::debug!(
            "Starting iterative parse for grammar: {} at pos {}",
            grammar,
            self.pos
        );

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
        let max_iterations = 50000_usize; // Higher limit for complex grammars

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

                panic!("Infinite loop detected in iterative parser");
            }

            // Debug: Show what frame we're processing periodically
            if iteration_count % 5000 == 0 {
                eprintln!(
                    "\nDEBUG [iter {}]: Processing frame_id={}, state={:?}",
                    iteration_count, frame.frame_id, frame.state
                );
                eprintln!(
                    "  Stack size: {}, Results size: {}",
                    stack.len(),
                    results.len()
                );
                match &frame.grammar {
                    Grammar::Ref { name, .. } => eprintln!("  Grammar: Ref({})", name),
                    Grammar::Token { token_type } => eprintln!("  Grammar: Token({})", token_type),
                    g => eprintln!("  Grammar: {:?}", g),
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
                        // Simple leaf grammars - parse directly using recursive parser
                        // We temporarily disable iterative flag to avoid infinite recursion
                        Grammar::Token { token_type } => {
                            eprintln!("DEBUG: Token grammar frame_id={}, pos={}, parent_max_idx={:?}, token_type={:?}, available_tokens={}",
                                frame.frame_id, pos, frame.parent_max_idx, token_type, self.tokens.len());
                            self.pos = pos;
                            let was_iterative = self.use_iterative_parser;
                            self.use_iterative_parser = false;
                            let result = self.parse_with_grammar_cached(&grammar, &terminators);
                            self.use_iterative_parser = was_iterative;
                            match result {
                                Ok(node) => {
                                    eprintln!("DEBUG: Token grammar frame_id={} matched, result end_pos={}", frame.frame_id, self.pos);
                                    results.insert(frame.frame_id, (node, self.pos, None));
                                }
                                Err(e) => {
                                    eprintln!(
                                        "DEBUG: Token grammar frame_id={} failed with error",
                                        frame.frame_id
                                    );
                                    return Err(e);
                                }
                            }
                        }

                        Grammar::StringParser {
                            template,
                            token_type,
                            optional: _optional,
                        } => {
                            // Handle StringParser directly in iterative mode
                            self.pos = pos;
                            self.skip_transparent(true);
                            let tok_raw = self.peek().cloned();

                            match tok_raw {
                                Some(tok) if tok.raw().eq_ignore_ascii_case(template) => {
                                    let token_pos = self.pos;
                                    self.bump();
                                    log::debug!("MATCHED String matched: {}", tok);

                                    let node = if *token_type == "keyword" {
                                        Node::Keyword(tok.raw(), token_pos)
                                    } else {
                                        Node::Code(tok.raw(), token_pos)
                                    };
                                    results.insert(frame.frame_id, (node, self.pos, None));
                                }
                                _ => {
                                    // StringParser didn't match - return Empty (not error)
                                    // This allows parent OneOf/AnyNumberOf/etc to try other options
                                    log::debug!(
                                        "String parser didn't match '{}', returning Empty",
                                        template
                                    );
                                    eprintln!("DEBUG [iter {}]: StringParser('{}') frame_id={} storing Empty result",
                                        iteration_count, template, frame.frame_id);
                                    results.insert(frame.frame_id, (Node::Empty, self.pos, None));
                                }
                            }
                        }

                        Grammar::MultiStringParser {
                            templates,
                            token_type,
                            optional: _optional,
                        } => {
                            // Handle MultiStringParser directly in iterative mode
                            self.pos = pos;
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

                                    let node = if *token_type == "keyword" {
                                        Node::Keyword(tok.raw(), token_pos)
                                    } else {
                                        Node::Code(tok.raw(), token_pos)
                                    };
                                    results.insert(frame.frame_id, (node, self.pos, None));
                                }
                                _ => {
                                    // MultiStringParser didn't match - return Empty
                                    log::debug!("MultiString parser didn't match any of {:?}, returning Empty", templates);
                                    results.insert(frame.frame_id, (Node::Empty, self.pos, None));
                                }
                            }
                        }

                        Grammar::TypedParser {
                            template,
                            token_type: _token_type,
                            optional: _optional,
                        } => {
                            // Handle TypedParser directly in iterative mode
                            eprintln!("DEBUG: TypedParser frame_id={}, pos={}, parent_max_idx={:?}, template={:?}",
                                frame.frame_id, pos, frame.parent_max_idx, template);
                            self.pos = pos;
                            self.skip_transparent(true);

                            if let Some(token) = self.peek() {
                                let tok = token.clone();
                                eprintln!(
                                    "DEBUG: TypedParser peeked token: type='{}', raw='{}', pos={}",
                                    tok.token_type,
                                    tok.raw(),
                                    self.pos
                                );
                                if tok.is_type(&[template]) {
                                    let raw = tok.raw().to_string();
                                    let token_pos = self.pos;
                                    self.bump();
                                    eprintln!("DEBUG: TypedParser MATCHED! frame_id={}, consumed token at pos={}",
                                        frame.frame_id, token_pos);
                                    log::debug!("MATCHED Typed matched: {}", tok.token_type);
                                    let node = Node::Code(raw, token_pos);
                                    results.insert(frame.frame_id, (node, self.pos, None));
                                } else {
                                    // No match - return Empty for parent to handle
                                    eprintln!("DEBUG: TypedParser FAILED to match! frame_id={}, expected='{}', found='{}'",
                                        frame.frame_id, template, tok.token_type);
                                    log::debug!(
                                        "Typed parser failed: expected '{}', found '{}'",
                                        template,
                                        tok.token_type
                                    );
                                    results.insert(frame.frame_id, (Node::Empty, pos, None));
                                }
                            } else {
                                // EOF - return Empty for parent to handle
                                eprintln!(
                                    "DEBUG: TypedParser at EOF! frame_id={}, pos={}",
                                    frame.frame_id, pos
                                );
                                log::debug!("Typed parser at EOF");
                                results.insert(frame.frame_id, (Node::Empty, pos, None));
                            }
                        }

                        Grammar::RegexParser {
                            template,
                            token_type: _token_type,
                            optional: _optional,
                            anti_template,
                        } => {
                            // Handle RegexParser directly in iterative mode
                            self.pos = pos;
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
                                            // Anti-template matched - no match, return Empty
                                            log::debug!("RegexParser anti-match, returning Empty");
                                            results.insert(
                                                frame.frame_id,
                                                (Node::Empty, self.pos, None),
                                            );
                                            continue; // Skip to next frame
                                        }
                                    }

                                    log::debug!(
                                        "MATCHED Regex matched and non anti-match: {}",
                                        tok
                                    );
                                    let token_pos = self.pos;
                                    self.bump();
                                    let node = Node::Code(tok.raw(), token_pos);
                                    results.insert(frame.frame_id, (node, self.pos, None));
                                }
                                _ => {
                                    // RegexParser didn't match - return Empty
                                    log::debug!(
                                        "RegexParser didn't match '{}', returning Empty",
                                        template
                                    );
                                    results.insert(frame.frame_id, (Node::Empty, self.pos, None));
                                }
                            }
                        }

                        Grammar::Meta(token_type) => {
                            // Meta tokens don't consume input, just create a node
                            log::debug!("Doing nothing with meta {}", token_type);
                            results.insert(frame.frame_id, (Node::Meta(token_type), pos, None));
                        }

                        Grammar::Symbol(sym) => {
                            // Handle Symbol directly in iterative mode
                            self.pos = pos;
                            let token = self.peek().cloned();

                            match token {
                                Some(tok) if tok.raw() == *sym => {
                                    let token_pos = self.pos;
                                    self.bump();
                                    log::debug!("MATCHED Symbol matched: {}", sym);
                                    let node = Node::Code(tok.raw(), token_pos);
                                    results.insert(frame.frame_id, (node, self.pos, None));
                                }
                                _ => {
                                    // Symbol didn't match - return Empty
                                    log::debug!("Symbol didn't match '{}', returning Empty", sym);
                                    results.insert(frame.frame_id, (Node::Empty, self.pos, None));
                                }
                            }
                        }

                        Grammar::Nothing() => {
                            // Nothing never matches - but in iterative mode, we return Empty
                            // to allow parent grammars to continue. The parent is responsible
                            // for handling the Empty result appropriately.
                            log::debug!("Nothing grammar encountered, returning Empty");
                            results.insert(frame.frame_id, (Node::Empty, pos, None));
                        }

                        Grammar::Empty => {
                            // Empty always succeeds without consuming input
                            results.insert(frame.frame_id, (Node::Empty, pos, None));
                        }

                        Grammar::Missing => {
                            // Missing is a placeholder that shouldn't be encountered
                            log::debug!("Trying missing grammar");
                            return Err(ParseError::new("Encountered Missing grammar".into()));
                        }

                        Grammar::Anything => {
                            // Matches anything until a terminator is found (greedy)
                            self.pos = pos;
                            log::debug!("Trying Anything grammar");
                            let mut anything_tokens = vec![];

                            loop {
                                if self.is_terminated(&terminators) || self.is_at_end() {
                                    break;
                                }
                                if let Some(tok) = self.peek() {
                                    anything_tokens
                                        .push(Node::Code(tok.raw().to_string(), self.pos));
                                    self.bump();
                                }
                            }

                            log::debug!("Anything matched tokens: {:?}", anything_tokens);
                            let node = Node::DelimitedList(anything_tokens);
                            results.insert(frame.frame_id, (node, self.pos, None));
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
                            // Initialize Sequence state
                            eprintln!("DEBUG: Sequence Initial at pos={}, parent_max_idx={:?}, allow_gaps={}, elements.len()={}",
                                      pos, frame.parent_max_idx, allow_gaps, elements.len());
                            let start_idx = pos;

                            // Combine parent and local terminators
                            let all_terminators: Vec<Grammar> = if *reset_terminators {
                                seq_terminators.clone()
                            } else {
                                seq_terminators
                                    .iter()
                                    .cloned()
                                    .chain(terminators.iter().cloned())
                                    .collect()
                            };

                            // Calculate max_idx for GREEDY mode
                            self.pos = start_idx;
                            let max_idx = if *parse_mode == ParseMode::Greedy {
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
                            frame.state = FrameState::WaitingForChild {
                                child_index: 0,
                                total_children: elements.len(),
                            };
                            frame.context = FrameContext::Sequence {
                                elements: elements.clone(),
                                allow_gaps: *allow_gaps,
                                optional: *optional,
                                parse_mode: *parse_mode,
                                matched_idx: start_idx,
                                tentatively_collected: vec![],
                                max_idx,
                                original_max_idx: max_idx, // Store original before any GREEDY_ONCE_STARTED trimming
                                last_child_frame_id: None,
                                current_element_idx: 0, // Start at first element
                                first_match: true,      // For GREEDY_ONCE_STARTED trimming
                            };
                            frame.terminators = all_terminators;
                            // No parent_max_idx set here - this is a top-level Sequence
                            let current_frame_id = frame.frame_id; // Save before moving frame
                            stack.push(frame);

                            // Skip to code if allow_gaps (matching Python's behavior at sequence.py line 196)
                            let first_child_pos = if *allow_gaps {
                                self.skip_start_index_forward_to_code(start_idx, max_idx)
                            } else {
                                start_idx
                            };

                            // Push first child to parse
                            if !elements.is_empty() {
                                // Check if we've run out of segments before first element
                                if first_child_pos >= max_idx {
                                    // Haven't matched anything yet and already at limit
                                    if *parse_mode == ParseMode::Strict {
                                        // In strict mode, return Empty
                                        results.insert(
                                            current_frame_id,
                                            (Node::Empty, start_idx, None),
                                        );
                                        continue;
                                    }
                                    // In greedy modes, check if first element is optional
                                    if elements[0].is_optional() {
                                        // First element is optional, can skip
                                        results.insert(
                                            current_frame_id,
                                            (Node::Empty, start_idx, None),
                                        );
                                        continue;
                                    } else {
                                        // Required element, no segments - this is unparsable in greedy mode
                                        results.insert(
                                            current_frame_id,
                                            (Node::Empty, start_idx, None),
                                        );
                                        continue;
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
                                                    match &parent_frame.accumulated[insert_pos - 1]
                                                    {
                                                        Node::Whitespace(_, _)
                                                        | Node::Newline(_, _) => {
                                                            insert_pos -= 1;
                                                        }
                                                        _ => break,
                                                    }
                                                }
                                                parent_frame
                                                    .accumulated
                                                    .insert(insert_pos, Node::Meta(meta_type));
                                            } else {
                                                parent_frame
                                                    .accumulated
                                                    .push(Node::Meta(meta_type));
                                            }

                                            // Update state to next child
                                            if let FrameState::WaitingForChild {
                                                child_index,
                                                total_children,
                                            } = &mut parent_frame.state
                                            {
                                                *child_index = child_idx + 1;
                                            }
                                        }
                                        child_idx += 1;
                                    } else {
                                        // Get max_idx from parent Sequence to pass to child
                                        let current_max_idx =
                                            if let Some(parent_frame) = stack.last() {
                                                if let FrameContext::Sequence { max_idx, .. } =
                                                    &parent_frame.context
                                                {
                                                    Some(*max_idx)
                                                } else {
                                                    None
                                                }
                                            } else {
                                                None
                                            };

                                        // Non-meta element - needs actual parsing
                                        eprintln!(
                                            "DEBUG: Creating FIRST child at pos={}, max_idx={}",
                                            first_child_pos, max_idx
                                        );
                                        let child_frame = ParseFrame {
                                            frame_id: frame_id_counter,
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
                                            &mut stack,
                                            child_frame,
                                            &mut frame_id_counter,
                                            child_idx,
                                        );
                                        continue 'main_loop; // Continue to process the child we just pushed
                                    }
                                }
                            }
                        }

                        Grammar::OneOf {
                            elements,
                            optional,
                            terminators: local_terminators,
                            reset_terminators,
                            allow_gaps,
                            parse_mode,
                        } => {
                            // Proper iterative OneOf with ParseFrame pattern
                            log::debug!(
                                "OneOf Initial state at pos {}, {} elements, parse_mode={:?}",
                                pos,
                                elements.len(),
                                parse_mode
                            );

                            // Collect leading whitespace
                            let leading_ws = if *allow_gaps {
                                self.collect_transparent(true)
                            } else {
                                Vec::new()
                            };
                            let post_skip_pos = self.pos;

                            // Combine terminators
                            let all_terminators: Vec<Grammar> = if *reset_terminators {
                                local_terminators.clone()
                            } else {
                                local_terminators
                                    .iter()
                                    .chain(terminators.iter())
                                    .cloned()
                                    .collect()
                            };

                            // Calculate max_idx based on parse_mode (for greedy matching)
                            let max_idx = if *parse_mode == ParseMode::Greedy {
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
                                let result = if *optional {
                                    Node::Empty
                                } else {
                                    apply_parse_mode_to_result(
                                        self.tokens,
                                        Node::Empty,
                                        pos,
                                        max_idx,
                                        *parse_mode,
                                    )
                                };

                                let final_pos = if matches!(result, Node::Empty) {
                                    pos
                                } else {
                                    max_idx
                                };
                                self.pos = final_pos;
                                results.insert(frame.frame_id, (result, final_pos, None));
                                continue 'main_loop;
                            }

                            // Prune options based on simple matchers
                            let available_options: Vec<Grammar> =
                                self.prune_options(elements).into_iter().cloned().collect();

                            if available_options.is_empty() {
                                log::debug!("OneOf: No viable options after pruning");
                                self.pos = pos;

                                // Apply parse_mode logic instead of throwing error
                                let result = if *optional {
                                    Node::Empty
                                } else {
                                    apply_parse_mode_to_result(
                                        self.tokens,
                                        Node::Empty,
                                        pos,
                                        max_idx,
                                        *parse_mode,
                                    )
                                };

                                let final_pos = if matches!(result, Node::Empty) {
                                    pos
                                } else {
                                    max_idx
                                };
                                self.pos = final_pos;
                                results.insert(frame.frame_id, (result, final_pos, None));
                                continue 'main_loop;
                            }

                            // Create context to track OneOf matching progress
                            frame.context = FrameContext::OneOf {
                                elements: available_options.clone(),
                                allow_gaps: *allow_gaps,
                                optional: *optional,
                                leading_ws: leading_ws.clone(),
                                post_skip_pos,
                                longest_match: None,
                                tried_elements: 0,
                                max_idx,
                                parse_mode: *parse_mode,
                                last_child_frame_id: Some(frame_id_counter), // Track the child we're about to create
                            };

                            // Create child frame for first element
                            let first_element = available_options[0].clone();
                            let element_key = first_element.cache_key();
                            log::debug!("OneOf: Trying first element (cache_key: {})", element_key);

                            // Use OUR computed max_idx for the child, not the parent's parent_max_idx
                            let child_frame = ParseFrame {
                                frame_id: frame_id_counter,
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

                            frame_id_counter += 1;
                            stack.push(frame); // Push parent back to stack first
                            stack.push(child_frame); // Then push child
                            continue 'main_loop; // Process the child frame we just pushed
                        }

                        Grammar::Ref {
                            name,
                            optional,
                            allow_gaps,
                            terminators: ref_terminators,
                            reset_terminators,
                        } => {
                            // Handle Ref by expanding into its grammar and pushing onto stack
                            log::debug!(
                                "Iterative Ref to segment: {}, optional: {}, allow_gaps: {}",
                                name,
                                optional,
                                allow_gaps
                            );
                            let saved = pos;
                            self.pos = pos;
                            self.skip_transparent(*allow_gaps);

                            // Combine parent and local terminators
                            let all_terminators: Vec<Grammar> = if *reset_terminators {
                                ref_terminators.clone()
                            } else {
                                ref_terminators
                                    .iter()
                                    .cloned()
                                    .chain(terminators.iter().cloned())
                                    .collect()
                            };

                            // Look up the grammar for this segment
                            let grammar_opt = self.get_segment_grammar(name);

                            match grammar_opt {
                                Some(child_grammar) => {
                                    // Get segment type for later wrapping
                                    let segment_type =
                                        self.dialect.get_segment_type(name).map(|s| s.to_string());

                                    // Create child frame to parse the target grammar
                                    let child_frame_id = frame_id_counter;
                                    frame_id_counter += 1;

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
                                    frame.state = FrameState::WaitingForChild {
                                        child_index: 0,
                                        total_children: 1,
                                    };
                                    frame.context = FrameContext::Ref {
                                        name: name.to_string(),
                                        optional: *optional,
                                        allow_gaps: *allow_gaps,
                                        segment_type,
                                        saved_pos: saved,
                                        last_child_frame_id: Some(child_frame_id), // Track the child we just created
                                    };

                                    // Push parent back first, then child (LIFO - child will be processed next)
                                    stack.push(frame);

                                    eprintln!("DEBUG [iter {}]: Ref({}) frame_id={} creating child frame_id={}, child grammar type: {}",
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
                                    eprintln!("DEBUG [iter {}]: ABOUT TO CONTINUE - Ref({}) pushed child {}, stack size now {}",
                                        iteration_count, name, child_frame_id, stack.len());
                                    eprintln!(
                                        "DEBUG [iter {}]: ==> CONTINUING 'MAIN_LOOP NOW! <==",
                                        iteration_count
                                    );
                                    continue 'main_loop; // Process the child frame we just pushed
                                }
                                None => {
                                    self.pos = saved;
                                    if *optional {
                                        log::debug!(
                                            "Iterative Ref optional (grammar not found), skipping"
                                        );
                                        results.insert(frame.frame_id, (Node::Empty, saved, None));
                                    } else {
                                        log::debug!("Iterative Ref failed (grammar not found), returning error");
                                        return Err(ParseError::unknown_segment(name.to_string()));
                                    }
                                }
                            }
                        }

                        Grammar::AnyNumberOf {
                            elements,
                            min_times,
                            max_times,
                            max_times_per_element,
                            optional,
                            terminators: any_terminators,
                            reset_terminators,
                            allow_gaps,
                            parse_mode,
                        } => {
                            // Initialize AnyNumberOf state
                            let start_idx = pos;
                            log::debug!(
                                "AnyNumberOf starting at {}, min_times={}, max_times={:?}, allow_gaps={}, parse_mode={:?}",
                                start_idx,
                                min_times,
                                max_times,
                                allow_gaps,
                                parse_mode
                            );

                            // Combine parent and local terminators
                            let all_terminators: Vec<Grammar> = if *reset_terminators {
                                any_terminators.clone()
                            } else {
                                any_terminators
                                    .iter()
                                    .cloned()
                                    .chain(terminators.iter().cloned())
                                    .collect()
                            };

                            // Calculate max_idx based on parse_mode
                            self.pos = start_idx;
                            let max_idx = if *parse_mode == ParseMode::Greedy {
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

                            eprintln!("DEBUG [iter {}]: AnyNumberOf Initial at pos={}, parent_max_idx={:?}, elements.len()={}",
                                iteration_count, frame.pos, frame.parent_max_idx, elements.len());

                            log::debug!(
                                "AnyNumberOf max_idx: {} (tokens.len: {})",
                                max_idx,
                                self.tokens.len()
                            );

                            // Update frame with AnyNumberOf context
                            frame.state = FrameState::WaitingForChild {
                                child_index: 0,
                                total_children: elements.len(), // We'll loop through elements
                            };
                            frame.context = FrameContext::AnyNumberOf {
                                elements: elements.clone(),
                                min_times: *min_times,
                                max_times: *max_times,
                                max_times_per_element: *max_times_per_element,
                                allow_gaps: *allow_gaps,
                                optional: *optional,
                                parse_mode: *parse_mode,
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
                                    elements: elements.clone(),
                                    optional: true, // Don't fail if no match (let AnyNumberOf handle it)
                                    terminators: all_terminators.clone(),
                                    reset_terminators: false,
                                    allow_gaps: *allow_gaps,
                                    parse_mode: *parse_mode,
                                };

                                let child_frame = ParseFrame {
                                    frame_id: frame_id_counter,
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
                                        *last_child_frame_id = Some(frame_id_counter);
                                    }
                                }

                                frame_id_counter += 1;
                                eprintln!("DEBUG [iter {}]: AnyNumberOf Initial pushing child frame_id={}, stack size before push={}",
                                    iteration_count, child_frame.frame_id, stack.len());
                                stack.push(child_frame);
                                eprintln!("DEBUG [iter {}]: AnyNumberOf Initial ABOUT TO CONTINUE after pushing child", iteration_count);
                                continue 'main_loop; // Process the child frame we just pushed
                            }
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
                            // Initialize Bracketed state
                            let start_idx = pos;
                            log::debug!(
                                "Bracketed starting at {}, allow_gaps={}, parse_mode={:?}",
                                start_idx,
                                allow_gaps,
                                parse_mode
                            );

                            // Combine parent and local terminators
                            let all_terminators: Vec<Grammar> = if *reset_terminators {
                                bracket_terminators.clone()
                            } else {
                                bracket_terminators
                                    .iter()
                                    .cloned()
                                    .chain(terminators.iter().cloned())
                                    .collect()
                            };

                            // Update frame with Bracketed context
                            frame.state = FrameState::WaitingForChild {
                                child_index: 0,
                                total_children: 3, // open, content, close
                            };
                            frame.context = FrameContext::Bracketed {
                                bracket_pairs: bracket_pairs.clone(),
                                elements: elements.clone(),
                                allow_gaps: *allow_gaps,
                                optional: *optional,
                                parse_mode: *parse_mode,
                                state: BracketedState::MatchingOpen,
                                last_child_frame_id: None,
                            };
                            frame.terminators = all_terminators.clone();
                            stack.push(frame);

                            // Start by trying to match the opening bracket
                            let child_frame = ParseFrame {
                                frame_id: frame_id_counter,
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
                                    *last_child_frame_id = Some(frame_id_counter);
                                }
                            }

                            frame_id_counter += 1;
                            stack.push(child_frame);
                            continue 'main_loop; // Process the child frame we just pushed
                        }

                        Grammar::AnySetOf {
                            elements,
                            min_times,
                            max_times,
                            optional,
                            terminators: local_terminators,
                            reset_terminators,
                            allow_gaps,
                            parse_mode,
                        } => {
                            log::debug!("[ITERATIVE] AnySetOf Initial state at pos {}", pos);

                            // Combine terminators
                            let all_terminators: Vec<Grammar> = if *reset_terminators {
                                local_terminators.clone()
                            } else {
                                local_terminators
                                    .iter()
                                    .cloned()
                                    .chain(terminators.iter().cloned())
                                    .collect()
                            };

                            // Calculate max_idx based on parse_mode
                            self.pos = pos;
                            let max_idx = if *parse_mode == ParseMode::Greedy {
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
                            frame.state = FrameState::WaitingForChild {
                                child_index: 0,
                                total_children: max_times.unwrap_or(usize::MAX).min(elements.len()),
                            };
                            frame.context = FrameContext::AnySetOf {
                                min_times: *min_times,
                                max_times: *max_times,
                                allow_gaps: *allow_gaps,
                                optional: *optional,
                                count: 0,
                                matched_idx: pos,
                                working_idx: pos,
                                matched_elements: std::collections::HashSet::new(),
                                max_idx,
                                last_child_frame_id: None,
                                elements: elements.clone(),
                                parse_mode: *parse_mode,
                            };
                            frame.terminators = all_terminators.clone();

                            stack.push(frame);

                            // Try first unmatched element
                            // For AnySetOf, we try all elements (not just first) via OneOf pattern
                            let child_grammar = Grammar::OneOf {
                                elements: elements.clone(),
                                optional: false,
                                terminators: vec![],
                                reset_terminators: false,
                                allow_gaps: *allow_gaps,
                                parse_mode: *parse_mode,
                            };

                            let child_frame = ParseFrame {
                                frame_id: frame_id_counter,
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
                                    *last_child_frame_id = Some(frame_id_counter);
                                }
                            }

                            frame_id_counter += 1;
                            stack.push(child_frame);
                            continue 'main_loop; // Process the child frame we just pushed
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
                            log::debug!("[ITERATIVE] Delimited Initial state at pos {}", pos);

                            // Combine terminators, filtering out delimiter from parent terminators
                            // This is critical - delimiter shouldn't terminate the delimited list itself
                            let filtered_parent: Vec<Grammar> = terminators
                                .iter()
                                .filter(|t| *t != delimiter.as_ref())
                                .cloned()
                                .collect();

                            let all_terminators: Vec<Grammar> = if *reset_terminators {
                                local_terminators.clone()
                            } else {
                                local_terminators
                                    .iter()
                                    .cloned()
                                    .chain(filtered_parent.into_iter())
                                    .collect()
                            };

                            // Calculate max_idx based on parse_mode and terminators
                            self.pos = pos;
                            let max_idx = if *parse_mode == ParseMode::Greedy {
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
                                "[ITERATIVE] Delimited max_idx: {} (tokens.len: {})",
                                max_idx,
                                self.tokens.len()
                            );

                            // Check if optional and already terminated
                            if *optional
                                && (self.is_at_end() || self.is_terminated(&all_terminators))
                            {
                                log::debug!("[ITERATIVE] Delimited: empty optional");
                                results.insert(
                                    frame.frame_id,
                                    (Node::DelimitedList(vec![]), pos, None),
                                );
                                continue;
                            }

                            // Create Delimited context
                            frame.state = FrameState::WaitingForChild {
                                child_index: 0,
                                total_children: usize::MAX, // Unknown number of children
                            };
                            frame.context = FrameContext::Delimited {
                                elements: elements.clone(),
                                delimiter: delimiter.clone(),
                                allow_trailing: *allow_trailing,
                                optional: *optional,
                                allow_gaps: *allow_gaps,
                                min_delimiters: *min_delimiters,
                                parse_mode: *parse_mode,
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
                                elements: elements.clone(),
                                optional: true, // Elements in Delimited are implicitly optional
                                terminators: vec![],
                                reset_terminators: false,
                                allow_gaps: *allow_gaps,
                                parse_mode: *parse_mode,
                            };

                            let child_frame = ParseFrame::new_child(
                                frame_id_counter,
                                child_grammar,
                                pos,
                                all_terminators,
                                Some(child_max_idx), // Use Delimited's max_idx!
                            );

                            // Update parent's last_child_frame_id and push child
                            ParseFrame::update_parent_last_child_id(
                                &mut stack,
                                "Delimited",
                                frame_id_counter,
                            );
                            frame_id_counter += 1;
                            stack.push(child_frame);
                            continue 'main_loop; // Process the child frame we just pushed
                        }

                        // For other grammar types, use recursive for now
                        _ => {
                            self.pos = pos;
                            match self.parse_with_grammar_cached(&grammar, &terminators) {
                                Ok(node) => {
                                    results.insert(frame.frame_id, (node, self.pos, None));
                                }
                                Err(e) => return Err(e),
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
                            eprintln!(
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

                                    // Check if this is a KeywordSegment and tag accordingly
                                    let processed_child = if name.ends_with("KeywordSegment") {
                                        tag_keyword_if_word(&child_node, self.tokens)
                                    } else {
                                        child_node.clone()
                                    };

                                    // Wrap in Ref node
                                    Node::Ref {
                                        name: name.clone(),
                                        segment_type: segment_type.clone(),
                                        child: Box::new(processed_child),
                                    }
                                };

                                self.pos = *child_end_pos;
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

                                        eprintln!("WARNING: Sequence failing - required element returned Empty!");
                                        eprintln!("  frame_id={}, element_idx={}/{}", frame.frame_id, *current_element_idx, elements.len());
                                        eprintln!("  Expected: {}", element_desc);
                                        eprintln!("  At position: {} (found: {})", element_start, found_token);

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
                                    eprintln!("DEBUG: Sequence completing - frame_id={}, self.pos={}, current_matched_idx={}, elements.len={}, accumulated.len={}",
                                        frame.frame_id, self.pos, current_matched_idx, elements_clone.len(), frame.accumulated.len());

                                    let result_node = if frame.accumulated.is_empty() {
                                        eprintln!("WARNING: Sequence completing with EMPTY accumulated! frame_id={}, current_elem_idx={}, elements.len={}",
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
                                    // Note: child_index is the index of the child we just processed
                                    // The next child to process is at child_index + 1
                                    log::debug!(
                                        "Sequence checking EOF: next_pos={}, current_max_idx={}, child_index={}, elements_clone.len()={}",
                                        next_pos,
                                        current_max_idx,
                                        child_index,
                                        elements_clone.len()
                                    );
                                    let next_child_index = child_index + 1;
                                    if next_pos >= current_max_idx
                                        && next_child_index < elements_clone.len()
                                    {
                                        log::debug!("  Entered EOF check block");
                                        // Check if next NON-META element is optional
                                        // Meta elements don't consume input, so we should skip them
                                        let mut check_idx = next_child_index;
                                        let mut next_element_optional = true; // Default to true if all remaining are Meta
                                        while check_idx < elements_clone.len() {
                                            if let Grammar::Meta(_) = &elements_clone[check_idx] {
                                                // Skip Meta elements
                                                check_idx += 1;
                                            } else {
                                                // Found a non-Meta element - check if it's optional
                                                next_element_optional = is_grammar_optional(
                                                    &elements_clone[check_idx],
                                                );
                                                break;
                                            }
                                        }
                                        log::debug!(
                                            "  next_element_optional={} (checked from idx {} to {})",
                                            next_element_optional,
                                            next_child_index,
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

                                            eprintln!("DEBUG [iter {}]: Sequence WaitingForChild - parent {}, creating child {}, grammar: {:?}",
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
                                            eprintln!("DEBUG [iter {}]: Sequence WaitingForChild ABOUT TO BREAK from while loop", iteration_count);
                                            created_child = true;
                                            break; // Exit the while loop - we've created the next child
                                        }
                                    }
                                    eprintln!("DEBUG [iter {}]: Sequence WaitingForChild AFTER while loop, created_child={}", iteration_count, created_child);
                                    // Only continue to process child if we actually created one
                                    if created_child {
                                        eprintln!("DEBUG [iter {}]: Sequence WaitingForChild ABOUT TO CONTINUE 'main_loop", iteration_count);
                                        continue 'main_loop;
                                    }
                                    // Otherwise, all remaining elements were Meta - complete the Sequence
                                    eprintln!("DEBUG [iter {}]: Sequence WaitingForChild - all remaining elements were Meta, completing frame_id={}", iteration_count, frame_id_for_debug);
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

                                    // Check if we've reached limits
                                    let should_continue = *count < *min_times
                                        || (*matched_idx < *max_idx
                                            && (max_times.is_none()
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
                                            eprintln!("DEBUG [iter {}]: AnyNumberOf pushed parent and child, stack.len()={}", iteration_count, stack.len());
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

                                            // Get parent_max_idx to propagate
                                            let parent_limit = frame.parent_max_idx;

                                            // Create content grammar (Sequence with closing bracket as terminator)
                                            let content_grammar = Grammar::Sequence {
                                                elements: elements.clone(),
                                                optional: false,
                                                terminators: vec![(*bracket_pairs.1).clone()],
                                                reset_terminators: true,
                                                allow_gaps: *allow_gaps,
                                                parse_mode: *parse_mode,
                                            };

                                            let child_frame = ParseFrame {
                                                frame_id: frame_id_counter,
                                                grammar: content_grammar,
                                                pos: self.pos,
                                                terminators: vec![(*bracket_pairs.1).clone()], // Use closing bracket as terminator, not parent's terminators!
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
                                    BracketedState::MatchingContent => {
                                        eprintln!("DEBUG: Bracketed MatchingContent - frame_id={}, child_end_pos={}, is_empty={}", frame.frame_id, child_end_pos, child_node.is_empty());
                                        // Content result
                                        if !child_node.is_empty() {
                                            // Extract children from the sequence node
                                            if let Node::Sequence(content_children) = child_node {
                                                frame.accumulated.extend(content_children.clone());
                                            } else {
                                                frame.accumulated.push(child_node.clone());
                                            }
                                        }

                                        let gap_start = *child_end_pos;
                                        self.pos = gap_start;
                                        eprintln!(
                                            "DEBUG: After content, gap_start={}, current_pos={}",
                                            gap_start, self.pos
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
                                        eprintln!("DEBUG: Checking for closing bracket - self.pos={}, tokens.len={}", self.pos, self.tokens.len());
                                        if self.pos >= self.tokens.len()
                                            || self
                                                .peek()
                                                .is_some_and(|t| t.get_type() == "end_of_file")
                                        {
                                            eprintln!("DEBUG: No closing bracket found!");
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
                                            eprintln!("DEBUG: Transitioning to MatchingClose!");
                                            // Transition to MatchingClose
                                            *state = BracketedState::MatchingClose;

                                            // Create child frame for closing bracket
                                            // Get parent_max_idx to propagate
                                            let parent_limit = frame.parent_max_idx;

                                            eprintln!("DEBUG: Creating closing bracket child at pos={}, parent_limit={:?}", self.pos, parent_limit);
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
                                        eprintln!("DEBUG: Bracketed MatchingClose - child_node.is_empty={}, child_end_pos={}", child_node.is_empty(), child_end_pos);
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
                                                Node::Sequence(frame.accumulated.clone());
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

                                    // Check termination conditions
                                    let should_terminate = *count >= *min_times
                                        && (*matched_idx >= *max_idx
                                            || (max_times.is_some()
                                                && *count >= max_times.unwrap())
                                            || matched_elements.len() >= elements.len()); // All unique elements matched

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
                                log::debug!("[ITERATIVE] Delimited WaitingForChild: state={:?}, delimiter_count={}", state, delimiter_count);

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
                            eprintln!("WARNING: Frame {} waiting for child {} but result not found (iteration {})",
                                frame.frame_id, child_id_str, iteration_count);

                            // Check if child is on stack
                            if let Ok(child_id) = child_id_str.parse::<usize>() {
                                let child_on_stack = stack.iter().any(|f| f.frame_id == child_id);
                                if child_on_stack {
                                    eprintln!(
                                        "  -> Child frame {} IS on stack (still being processed)",
                                        child_id
                                    );
                                } else {
                                    eprintln!("  -> Child frame {} NOT on stack (may have been lost or never created)", child_id);
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
        eprintln!("DEBUG: Main loop ended. Stack has {} frames left. Results has {} entries. Looking for frame_id={}",
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

            eprintln!(
                "  Stack[{}]: frame_id={}, state={:?}, pos={}, grammar={}, waiting_for={}",
                i, frame.frame_id, frame.state, frame.pos, grammar_desc, waiting_for
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
            eprintln!(
                "DEBUG: Found result for frame_id={}, end_pos={}",
                initial_frame_id, end_pos
            );
            self.pos = *end_pos;

            // If the parse failed (returned Empty), provide diagnostic information
            if node.is_empty() {
                eprintln!("\n=== PARSE FAILED ===");
                eprintln!("Parser stopped at position: {}", end_pos);
                eprintln!("Total tokens: {}", self.tokens.len());

                if *end_pos < self.tokens.len() {
                    eprintln!("\nTokens around failure point:");
                    let start = end_pos.saturating_sub(3);
                    let end = (*end_pos + 4).min(self.tokens.len());
                    for i in start..end {
                        let marker = if i == *end_pos { " <<< HERE" } else { "" };
                        if let Some(tok) = self.tokens.get(i) {
                            eprintln!("  [{}]: '{}' (type: {}){}", i, tok.raw(), tok.get_type(), marker);
                        }
                    }
                }

                eprintln!("\nGrammar that failed to match:");
                eprintln!("  {}", grammar);
                eprintln!("===================\n");
            }

            Ok(node.clone())
        } else {
            Err(ParseError::new(format!(
                "Iterative parse produced no result (initial_frame_id={}, results has {} entries)",
                initial_frame_id,
                results.len()
            )))
        }
    }

    /// Main entry point for parsing with grammar and caching.
    /// Dispatches to either iterative or recursive implementation based on flag.
    pub fn parse_with_grammar_cached(
        &mut self,
        grammar: &Grammar,
        parent_terminators: &[Grammar],
    ) -> Result<Node, ParseError> {
        if self.use_iterative_parser {
            self.parse_with_grammar_cached_iterative(grammar, parent_terminators)
        } else {
            self.parse_with_grammar_cached_recursive(grammar, parent_terminators)
        }
    }

    /// Iterative (frame-based) parser with caching.
    /// Uses a stack-based approach to avoid deep recursion.
    fn parse_with_grammar_cached_iterative(
        &mut self,
        grammar: &Grammar,
        parent_terminators: &[Grammar],
    ) -> Result<Node, ParseError> {
        self.parse_iterative(grammar, parent_terminators)
    }

    /// Recursive parser with caching.
    /// Uses traditional recursive descent with memoization for performance.
    fn parse_with_grammar_cached_recursive(
        &mut self,
        grammar: &Grammar,
        parent_terminators: &[Grammar],
    ) -> Result<Node, ParseError> {
        // Create cache key
        let cache_key = CacheKey::new(self.pos, grammar, self.tokens);

        // Check cache first
        if let Some(Ok((node, end_pos, collected_positions))) = self.parse_cache.get(&cache_key) {
            self.pos = end_pos; // Directly set to cached end position
                                // Restore collected transparent positions
            let num_positions = collected_positions.len();
            for pos in collected_positions {
                self.collected_transparent_positions.insert(pos);
            }
            log::debug!("Cache HIT restored {} collected positions", num_positions);
            return Ok(node);
        }

        // Cache miss - parse fresh
        let positions_before = self.collected_transparent_positions.clone();
        let result = self.parse_with_grammar(grammar, parent_terminators);

        // Store in cache with collected positions
        if let Ok(ref node) = result {
            // Collect positions that were added during this parse
            let new_positions: Vec<usize> = self
                .collected_transparent_positions
                .difference(&positions_before)
                .copied()
                .collect();

            self.parse_cache
                .put(cache_key, Ok((node.clone(), self.pos, new_positions)));
        }

        result
    }

    /// Prune options based on simple matchers before attempting full parse.
    ///
    /// This is the Rust equivalent of Python's `prune_options()` function.
    /// It filters the list of grammar options to only those that could possibly
    /// match the current token, based on quick checks of raw strings and types.
    fn prune_options<'g>(&self, options: &'g [Grammar]) -> Vec<&'g Grammar> {
        // Find first code (non-whitespace) token from current position
        let first_code_token = self.tokens.iter().skip(self.pos).find(|t| t.is_code());

        // If no code token found, can't prune - return all options
        let Some(first_token) = first_code_token else {
            return options.iter().collect();
        };

        // Get token properties for matching
        let first_raw = first_token.raw().to_uppercase();
        let first_type = first_token.get_type();

        log::debug!(
            "Pruning {} options at pos {} (token: '{}', type: {})",
            options.len(),
            self.pos,
            first_raw,
            first_type
        );

        let mut pruned = Vec::new();

        for opt in options {
            // Try to get simple representation
            match opt.simple() {
                None => {
                    // Complex grammar - must try full match
                    log::debug!("  Keeping complex grammar: {}", opt);
                    pruned.push(opt);
                }
                Some(simple) => {
                    // Check if simple matches current token
                    if simple.could_match(first_token) {
                        log::debug!("  Keeping matched grammar: {}", opt);
                        pruned.push(opt);
                    } else {
                        log::debug!("  PRUNED grammar: {}", opt);
                    }
                }
            }
        }

        log::debug!(
            "Pruned from {} to {} options ({:.1}% reduction)",
            options.len(),
            pruned.len(),
            100.0 * (1.0 - pruned.len() as f64 / options.len() as f64)
        );

        pruned
    }

    /// Print cache statistics
    pub fn print_cache_stats(&self) {
        let (hits, misses, hit_rate) = self.parse_cache.stats();
        eprintln!("Parse Cache Statistics:");
        eprintln!("  Hits: {}", hits);
        eprintln!("  Misses: {}", misses);
        eprintln!("  Hit Rate: {:.2}%", hit_rate * 100.0);
    }

    pub fn parse_with_grammar(
        &'_ mut self,
        grammar: &Grammar,
        parent_terminators: &[Grammar],
    ) -> Result<Node, ParseError> {
        log::debug!("Parsing with grammar: {}@{}", grammar, self.pos);
        // log::debug!("Parent terminators: {:?}", parent_terminators);
        match grammar {
            Grammar::Missing => {
                log::debug!("Trying missing grammar");
                todo!("Encountered Missing grammar in parse_with_grammar");
            }
            Grammar::Anything => {
                // This matches anything
                // it is greedy so will consume everything until a terminator is found
                log::debug!("Trying Anything grammar");
                let mut anything_tokens = vec![];
                loop {
                    if self.is_terminated(parent_terminators) || self.is_at_end() {
                        break;
                    }
                    if let Some(tok) = self.peek() {
                        anything_tokens.push(Node::Code(tok.raw().to_string(), self.pos));
                        self.bump();
                    }
                }
                log::debug!("Anything matched tokens: {:?}", anything_tokens);
                Ok(Node::DelimitedList(anything_tokens))
            }
            Grammar::Token { token_type } => {
                log::debug!("Trying token grammar, {}", token_type);
                if let Some(token) = self.peek() {
                    let tok = token.clone();
                    log::debug!("Current token: {:?}", tok.get_type());
                    if tok.get_type() == *token_type {
                        let node = Node::Code(tok.raw(), self.pos);
                        self.bump();
                        log::debug!("MATCHED Token matched: {:?}", tok);
                        Ok(node)
                    } else {
                        Err(ParseError::new(format!(
                            "Expected token type {}, found {}",
                            token_type,
                            tok.get_type()
                        )))
                    }
                } else {
                    Err(ParseError::new("Expected token, found EOF".into()))
                }
            }
            Grammar::Meta(token_type) => {
                log::debug!("Doing nothing with meta {}", token_type);
                Ok(Node::Meta(token_type))
                // Ok(Node::Empty)
            }
            Grammar::StringParser {
                template,
                token_type,
                optional,
            } => {
                log::debug!("Trying string parser: {}, type: {:?}", template, token_type);
                self.skip_transparent(true);
                let tok_raw = self.peek().cloned();
                match tok_raw {
                    Some(tok) if tok.raw().eq_ignore_ascii_case(template) => {
                        let token_pos = self.pos; // Save position before bumping
                        self.bump();
                        log::debug!("MATCHED String matched: {}", tok);
                        // Create Node::Keyword for keyword token_type, Node::Code otherwise
                        if *token_type == "keyword" {
                            Ok(Node::Keyword(tok.raw(), token_pos))
                        } else {
                            Ok(Node::Code(tok.raw(), token_pos))
                        }
                    }
                    _ => {
                        if *optional {
                            log::debug!("String parser optional, skipping");
                            Ok(Node::Empty)
                        } else {
                            Err(ParseError::new(format!("Expected string '{}'", template)))
                        }
                    }
                }
            }
            Grammar::MultiStringParser {
                templates,
                token_type,
                optional,
            } => {
                log::debug!(
                    "Trying multi string parser: {:?}, type: {:?}",
                    templates,
                    token_type
                );
                self.skip_transparent(true);
                let token = self.peek().cloned();
                match token {
                    Some(tok)
                        if templates
                            .iter()
                            .any(|&temp| tok.raw().eq_ignore_ascii_case(temp)) =>
                    {
                        let token_pos = self.pos; // Save position before bumping
                        self.bump();
                        log::debug!("MATCHED Multi string matched: {}", tok);
                        // Create Node::Keyword for keyword token_type, Node::Code otherwise
                        if *token_type == "keyword" {
                            Ok(Node::Keyword(tok.raw(), token_pos))
                        } else {
                            Ok(Node::Code(tok.raw(), token_pos))
                        }
                    }
                    _ => {
                        if *optional {
                            Ok(Node::Empty)
                        } else {
                            Err(ParseError::new(format!(
                                "Expected one of strings '{:?}'",
                                templates
                            )))
                        }
                    }
                }
            }
            Grammar::RegexParser {
                template,
                token_type,
                optional,
                anti_template,
            } => {
                log::debug!("Trying regex parser: {}, type: {:?}", template, token_type);
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
                        if let Some(anti) = anti_template {
                            if regex::RegexBuilder::new(anti)
                                .case_insensitive(true)
                                .build()
                                .unwrap()
                                .is_match(&tok.raw())
                            {
                                log::debug!("Regex anti-matched: {}", tok);
                                if *optional {
                                    return Ok(Node::Empty);
                                } else {
                                    return Err(ParseError::new(format!(
                                        "Token '{}' matches anti-template '{}'",
                                        tok, anti
                                    )));
                                }
                            }
                        }
                        log::debug!("MATCHED Regex matched and non anti-match: {}", tok);
                        let token_pos = self.pos; // Save position before bumping
                        self.bump();
                        Ok(Node::Code(tok.raw(), token_pos))
                    }
                    _ => {
                        if *optional {
                            Ok(Node::Empty)
                        } else {
                            Err(ParseError::new(format!(
                                "Expected token matching regex '{}'",
                                template
                            )))
                        }
                    }
                }
            }
            Grammar::TypedParser {
                template,
                token_type,
                optional,
            } => {
                log::debug!("Trying typed parser: {}, type: {}", template, token_type);
                self.skip_transparent(true);
                if let Some(token) = self.peek() {
                    let tok = token.clone();
                    if tok.is_type(&[template]) {
                        let raw = tok.raw().to_string(); // Clone the raw value to avoid borrowing issues
                        let node = Node::Code(raw, self.pos); // Pass the cloned raw value and the token reference
                        self.bump();
                        log::debug!("MATCHED Typed matched: {}", tok.token_type);
                        Ok(node)
                    } else if *optional {
                        log::debug!("Typed parser optional, skipping");
                        Ok(Node::Empty)
                    } else {
                        log::debug!(
                            "NOMATCH Typed parser expected '{}', found '{}'",
                            template,
                            tok.token_type
                        );
                        Err(ParseError::new(format!(
                            "Expected typed token '{}'",
                            template
                        )))
                    }
                } else if *optional {
                    log::debug!("Typed parser optional, skipping at EOF");
                    Ok(Node::Empty)
                } else {
                    log::debug!("NOMATCH Typed parser expected '{}', found EOF", template);
                    Err(ParseError::new(format!(
                        "Expected typed token '{}', found EOF",
                        template
                    )))
                }
            }
            Grammar::Symbol(sym) => {
                log::debug!("Trying symbol: {}", sym);
                let token = self.peek().cloned();
                match token {
                    Some(tok) if tok.raw() == *sym => {
                        let token_pos = self.pos; // Save position before bumping
                        self.bump();
                        log::debug!("MATCHED Symbol matched: {}", sym);
                        Ok(Node::Code(tok.raw(), token_pos))
                    }
                    _ => Err(ParseError::new(format!("Expected symbol '{}'", sym))),
                }
            }
            Grammar::Ref {
                name,
                optional,
                allow_gaps,
                terminators,
                reset_terminators,
            } => {
                log::debug!(
                    "Trying Ref to segment: {}, optional: {}, allow_gaps: {}",
                    name,
                    optional,
                    allow_gaps
                );
                let saved = self.pos;
                self.skip_transparent(*allow_gaps);

                // Combine parent and local terminators
                let all_terminators: Vec<Grammar> = if *reset_terminators {
                    terminators.clone()
                } else {
                    terminators
                        .iter()
                        .cloned()
                        .chain(parent_terminators.iter().cloned())
                        .collect()
                };

                let attempt = self.call_rule(name, &all_terminators);
                match attempt {
                    Ok(node) => {
                        log::debug!("MATCHED Ref matched segment: {}", name);
                        Ok(node)
                    }
                    Err(e) => {
                        self.pos = saved;
                        if *optional {
                            log::debug!("Ref optional, skipping");
                            Ok(Node::Empty)
                        } else {
                            Err(e)
                        }
                    }
                }
            }
            Grammar::Sequence {
                elements,
                optional,
                terminators,
                reset_terminators,
                allow_gaps,
                parse_mode,
            } => {
                let start_idx = self.pos; // Where did we start
                log::debug!(
                    "Sequence starting at {}, allow_gaps={}, parse_mode={:?}",
                    start_idx,
                    allow_gaps,
                    parse_mode
                );
                let mut matched_idx = self.pos; // Where have we got to
                let mut last_collected_idx = None::<usize>; // Track last position where we collected transparent tokens
                let mut max_idx = self.tokens.len(); // What is the limit
                let mut children: Vec<Node> = Vec::new();
                let mut first_match = true;
                let mut tentatively_collected_positions: Vec<usize> = Vec::new(); // Track positions we collected but haven't committed yet

                // Combine parent and local terminators
                let all_terminators: Vec<Grammar> = if *reset_terminators {
                    terminators.clone()
                } else {
                    terminators
                        .iter()
                        .cloned()
                        .chain(parent_terminators.iter().cloned())
                        .collect()
                };

                // GREEDY: In the GREEDY mode, we first look ahead to find a terminator
                // before matching any code.
                if *parse_mode == ParseMode::Greedy {
                    max_idx = self.trim_to_terminator(self.pos, &all_terminators);
                    log::debug!("GREEDY mode: trimmed max_idx to {}", max_idx);
                }

                // Iterate through elements
                for element in elements {
                    log::debug!("Sequence-@{}: matching {:?}", matched_idx, element);

                    // 1. Handle Meta segments (indent/dedent)
                    if let Grammar::Meta(meta_type) = element {
                        if *meta_type == "indent" {
                            log::debug!("Inserting Meta: {}", meta_type);
                            // Indent goes before whitespace
                            let mut insert_pos = children.len();
                            while insert_pos > 0 {
                                match &children[insert_pos - 1] {
                                    Node::Whitespace(_, _) | Node::Newline(_, _) => {
                                        insert_pos -= 1;
                                    }
                                    _ => break,
                                }
                            }
                            children.insert(insert_pos, Node::Meta(meta_type));
                        } else if *meta_type == "dedent" {
                            log::debug!("Inserting Meta: {}", meta_type);
                            children.push(Node::Meta(meta_type));
                        }
                        continue;
                    }

                    // 2. Skip whitespace/newlines if allow_gaps
                    self.pos = matched_idx;
                    let mut _idx = matched_idx;
                    log::debug!(
                        "Before collection: matched_idx={}, allow_gaps={}",
                        matched_idx,
                        *allow_gaps
                    );
                    if *allow_gaps {
                        _idx = self.skip_start_index_forward_to_code(matched_idx, max_idx);

                        // Check if any positions in the range matched_idx.._idx need to be collected
                        // We should collect if we haven't already collected from this range
                        let has_uncollected = (matched_idx.._idx).any(|pos| {
                            pos < self.tokens.len()
                                && !self.tokens[pos].is_code()
                                && !self.collected_transparent_positions.contains(&pos)
                        });

                        let should_collect = has_uncollected;

                        log::debug!(
                            "Collection check: matched_idx={}, _idx={}, has_uncollected={}, should_collect={}",
                            matched_idx,
                            _idx,
                            has_uncollected,
                            should_collect
                        );

                        if should_collect {
                            // Collect the transparent tokens we're skipping
                            while self.pos < _idx {
                                let current_pos = self.pos;
                                if let Some(tok) = self.peek() {
                                    let tok_type = tok.get_type();
                                    if tok_type == "whitespace" {
                                        log::debug!(
                                            "COLLECTING whitespace at token pos {}: {:?}",
                                            self.pos,
                                            tok.raw()
                                        );
                                        children.push(Node::Whitespace(
                                            tok.raw().to_string(),
                                            self.pos,
                                        ));
                                        // Mark as tentatively collected AND add to global set immediately
                                        // This prevents nested Sequences from re-collecting the same token
                                        tentatively_collected_positions.push(current_pos);
                                        self.collected_transparent_positions.insert(current_pos);
                                    } else if tok_type == "newline" {
                                        log::debug!(
                                            "COLLECTING newline at token pos {}: {:?}",
                                            self.pos,
                                            tok.raw()
                                        );
                                        children
                                            .push(Node::Newline(tok.raw().to_string(), self.pos));
                                        // Mark as tentatively collected AND add to global set immediately
                                        tentatively_collected_positions.push(current_pos);
                                        self.collected_transparent_positions.insert(current_pos);
                                    }
                                }
                                self.bump();
                            }
                            // Update last collected position
                            last_collected_idx = Some(matched_idx);
                        } else {
                            log::debug!(
                                "SKIPPING collection at matched_idx={} (already collected)",
                                matched_idx
                            );
                            // Still need to advance self.pos even if not collecting
                            self.pos = _idx;
                        }
                    }

                    // 3. Have we prematurely run out of segments?
                    if _idx >= max_idx {
                        // Check if this element is optional
                        let element_is_optional = match element {
                            Grammar::Sequence { optional, .. } => *optional,
                            Grammar::AnyNumberOf { optional, .. } => *optional,
                            Grammar::OneOf { optional, .. } => *optional,
                            Grammar::Delimited { optional, .. } => *optional,
                            Grammar::Bracketed { optional, .. } => *optional,
                            Grammar::Ref { optional, .. } => *optional,
                            Grammar::StringParser { optional, .. } => *optional,
                            Grammar::MultiStringParser { optional, .. } => *optional,
                            Grammar::TypedParser { optional, .. } => *optional,
                            Grammar::RegexParser { optional, .. } => *optional,
                            _ => false,
                        };

                        if element_is_optional {
                            log::debug!("Element is optional, continuing");
                            continue;
                        }

                        // Required element but ran out of segments
                        if *parse_mode == ParseMode::Strict || matched_idx == start_idx {
                            log::debug!(
                                "NOMATCH Ran out of segments in STRICT mode or nothing matched yet"
                            );
                            self.pos = start_idx;
                            // Rollback: remove tentatively collected positions from global set
                            for pos in &tentatively_collected_positions {
                                self.collected_transparent_positions.remove(pos);
                            }
                            return Ok(Node::Empty);
                        }

                        // GREEDY/GREEDY_ONCE_STARTED: return what we have with error marker
                        // TODO: Create proper UnparsableSegment representation
                        log::debug!(
                            "INCOMPLETE match in {:?} mode: expected {:?} but ran out of segments",
                            parse_mode,
                            element
                        );
                        self.pos = matched_idx;
                        return Ok(Node::Sequence(children));
                    }

                    // 4. Try to match the element
                    self.pos = _idx;
                    let elem_match = self.parse_with_grammar_cached(element, &all_terminators);

                    match elem_match {
                        Ok(node) => {
                            if node.is_empty() {
                                // Optional element didn't match
                                log::debug!("Element returned Empty, continuing");
                                continue;
                            }

                            // Successfully matched
                            let element_start = _idx; // Where the element started parsing
                            matched_idx = self.pos; // Where we ended up after parsing
                            log::debug!(
                                "MATCHED Sequence element, now at position {}",
                                matched_idx
                            );

                            // Add the matched node first
                            children.push(node);

                            // THEN handle retroactive collection of trailing transparent tokens
                            // If the Sequence has allow_gaps=false but the element skipped transparent tokens,
                            // we need to collect them retroactively!
                            if !*allow_gaps {
                                // The element was parsed starting at element_start
                                // After matching, we're at matched_idx
                                // We need to collect any transparent tokens between where the element
                                // actually consumed code tokens and where we ended up

                                // Find where the element actually consumed its last code token
                                // by working backwards from matched_idx
                                let mut last_code_consumed = element_start;
                                for check_pos in element_start..matched_idx {
                                    if check_pos < self.tokens.len()
                                        && self.tokens[check_pos].is_code()
                                    {
                                        last_code_consumed = check_pos;
                                    }
                                }

                                log::debug!(
                                    "Retroactive collection: element_start={}, last_code_consumed={}, matched_idx={}",
                                    element_start, last_code_consumed, matched_idx
                                );

                                // Collect transparent tokens from right after the last code token
                                // Continue collecting ALL transparent tokens until we hit code
                                let mut collect_end = matched_idx;
                                while collect_end < self.tokens.len()
                                    && !self.tokens[collect_end].is_code()
                                {
                                    collect_end += 1;
                                }

                                log::debug!(
                                    "Retroactive collection will collect from {} to {}",
                                    last_code_consumed + 1,
                                    collect_end
                                );

                                for check_pos in (last_code_consumed + 1)..collect_end {
                                    log::debug!(
                                        "Checking position {} for retroactive collection: is_code={}, in_global={}, in_tentative={}",
                                        check_pos,
                                        if check_pos < self.tokens.len() { self.tokens[check_pos].is_code() } else { true },
                                        self.collected_transparent_positions.contains(&check_pos),
                                        tentatively_collected_positions.contains(&check_pos)
                                    );
                                    if check_pos < self.tokens.len()
                                        && !self.tokens[check_pos].is_code()
                                        && !self
                                            .collected_transparent_positions
                                            .contains(&check_pos)
                                        && !tentatively_collected_positions.contains(&check_pos)
                                    {
                                        let tok = &self.tokens[check_pos];
                                        let tok_type = tok.get_type();
                                        if tok_type == "whitespace" {
                                            log::debug!("RETROACTIVELY collecting whitespace at token pos {}: {:?}", check_pos, tok.raw());
                                            children.push(Node::Whitespace(
                                                tok.raw().to_string(),
                                                check_pos,
                                            ));
                                            tentatively_collected_positions.push(check_pos);
                                            self.collected_transparent_positions.insert(check_pos);
                                        } else if tok_type == "newline" {
                                            log::debug!("RETROACTIVELY collecting newline at token pos {}: {:?}", check_pos, tok.raw());
                                            children.push(Node::Newline(
                                                tok.raw().to_string(),
                                                check_pos,
                                            ));
                                            tentatively_collected_positions.push(check_pos);
                                            self.collected_transparent_positions.insert(check_pos);
                                        }
                                    }
                                }
                                last_collected_idx = Some(matched_idx - 1);
                            }

                            // GREEDY_ONCE_STARTED: Trim to terminator after first match
                            if first_match && *parse_mode == ParseMode::GreedyOnceStarted {
                                max_idx = self.trim_to_terminator(matched_idx, &all_terminators);
                                log::debug!(
                                    "GREEDY_ONCE_STARTED: trimmed max_idx to {} after first match",
                                    max_idx
                                );
                                first_match = false;
                            }
                        }
                        Err(_e) => {
                            // Element failed to match
                            self.pos = _idx;

                            // Check if element is optional
                            let element_is_optional = match element {
                                Grammar::Sequence { optional, .. } => *optional,
                                Grammar::AnyNumberOf { optional, .. } => *optional,
                                Grammar::OneOf { optional, .. } => *optional,
                                Grammar::Delimited { optional, .. } => *optional,
                                Grammar::Bracketed { optional, .. } => *optional,
                                Grammar::Ref { optional, .. } => *optional,
                                Grammar::StringParser { optional, .. } => *optional,
                                Grammar::MultiStringParser { optional, .. } => *optional,
                                Grammar::TypedParser { optional, .. } => *optional,
                                Grammar::RegexParser { optional, .. } => *optional,
                                _ => false,
                            };

                            if element_is_optional {
                                log::debug!("NOMATCH Element is optional, continuing");
                                continue;
                            }

                            // Required element failed
                            if *parse_mode == ParseMode::Strict {
                                log::debug!("NOMATCH Required element failed in STRICT mode");
                                self.pos = start_idx;
                                // Rollback: remove tentatively collected positions from global set
                                for pos in &tentatively_collected_positions {
                                    self.collected_transparent_positions.remove(pos);
                                }
                                return Ok(Node::Empty);
                            }

                            if *parse_mode == ParseMode::GreedyOnceStarted
                                && matched_idx == start_idx
                            {
                                log::debug!(
                                    "NOMATCH Nothing matched yet in GREEDY_ONCE_STARTED mode"
                                );
                                self.pos = start_idx;
                                // Rollback: remove tentatively collected positions from global set
                                for pos in &tentatively_collected_positions {
                                    self.collected_transparent_positions.remove(pos);
                                }
                                return Ok(Node::Empty);
                            }

                            // GREEDY or GREEDY_ONCE_STARTED after first match:
                            // Return partial match (TODO: mark remaining as unparsable)
                            log::debug!(
                                "INCOMPLETE match in {:?} mode: expected {:?} at position {}",
                                parse_mode,
                                element,
                                _idx
                            );
                            self.pos = matched_idx;
                            // Already committed to global set, no need to commit again
                            return Ok(Node::Sequence(children));
                        }
                    }
                }

                // All elements matched (or were optional)
                self.pos = matched_idx;

                // Collect any trailing non-code tokens (whitespace, newlines, end_of_file)
                // Note: We always consume end_of_file even if allow_gaps is false
                while self.pos < max_idx {
                    if let Some(tok) = self.peek() {
                        if tok.is_code() {
                            break; // Stop at code tokens
                        }
                        let tok_type = tok.get_type();
                        if tok_type == "whitespace" {
                            if *allow_gaps
                                && !self.collected_transparent_positions.contains(&self.pos)
                            {
                                children.push(Node::Whitespace(tok.raw().to_string(), self.pos));
                                tentatively_collected_positions.push(self.pos);
                                self.collected_transparent_positions.insert(self.pos);
                            }
                        } else if tok_type == "newline" {
                            if *allow_gaps
                                && !self.collected_transparent_positions.contains(&self.pos)
                            {
                                children.push(Node::Newline(tok.raw().to_string(), self.pos));
                                tentatively_collected_positions.push(self.pos);
                                self.collected_transparent_positions.insert(self.pos);
                            }
                        } else if tok_type == "end_of_file" {
                            // Only collect end_of_file if it hasn't been collected yet
                            // Since we only collect it once globally, whichever Sequence reaches it first will claim it
                            // The format_tree function will always display it at file-level depth
                            if !self.collected_transparent_positions.contains(&self.pos) {
                                log::debug!("COLLECTING end_of_file at position {}", self.pos);
                                children.push(Node::EndOfFile(tok.raw().to_string(), self.pos));
                                tentatively_collected_positions.push(self.pos);
                                self.collected_transparent_positions.insert(self.pos);
                            }
                        }
                        self.bump();
                    } else {
                        break;
                    }
                }
                matched_idx = self.pos;

                // In GREEDY/GREEDY_ONCE_STARTED modes: if there's anything left unclaimed,
                // mark it as unparsable
                if (*parse_mode == ParseMode::Greedy || *parse_mode == ParseMode::GreedyOnceStarted)
                    && max_idx > matched_idx
                {
                    let _idx = self.skip_start_index_forward_to_code(matched_idx, max_idx);
                    let _stop_idx = self.skip_stop_index_backward_to_code(max_idx, _idx);

                    if _stop_idx > _idx {
                        log::debug!(
                            "GREEDY mode: {} unparsable tokens remaining from {} to {}",
                            _stop_idx - _idx,
                            _idx,
                            _stop_idx
                        );
                        // TODO: Create proper UnparsableSegment representation
                        // For now, just consume them
                        while self.pos < _stop_idx {
                            if let Some(tok) = self.peek() {
                                children.push(Node::Code(tok.raw().to_string(), self.pos));
                            }
                            self.bump();
                        }
                        matched_idx = _stop_idx;
                    }
                }

                self.pos = matched_idx;

                // If we have no children and the sequence itself is optional, return Empty
                if children.is_empty() && *optional {
                    log::debug!("Sequence matched no children and is optional, returning Empty");
                    // Rollback: remove tentatively collected positions from global set since we're returning Empty
                    for pos in &tentatively_collected_positions {
                        self.collected_transparent_positions.remove(pos);
                    }
                    Ok(Node::Empty)
                } else {
                    // Already committed to global set, positions were added immediately when collected
                    Ok(Node::Sequence(children))
                }
            }
            Grammar::OneOf {
                elements,
                optional,
                terminators,
                reset_terminators,
                allow_gaps,
                parse_mode,
            } => {
                log::debug!("Trying OneOf elements: {:?}", elements);
                let initial_pos = self.pos;

                // Collect leading whitespace
                let leading_ws = self.collect_transparent(*allow_gaps);
                let post_skip_pos = self.pos;

                // Combine parent and local terminators
                let all_terminators: Vec<Grammar> = if *reset_terminators {
                    terminators.clone()
                } else {
                    terminators
                        .iter()
                        .cloned()
                        .chain(parent_terminators.iter().cloned())
                        .collect()
                };

                if self.is_terminated(&all_terminators) {
                    self.pos = initial_pos;
                    return if *optional {
                        Ok(Node::Empty)
                    } else {
                        Err(ParseError::new(
                            "Expected one of choices, but terminated".into(),
                        ))
                    };
                }

                // Prune options based on simple matchers
                let available_options = self.prune_options(elements);

                if available_options.is_empty() {
                    self.pos = initial_pos;
                    return if *optional {
                        Ok(Node::Empty)
                    } else {
                        Err(ParseError::new("No viable options after pruning".into()))
                    };
                }

                // Use the common longest-match logic (macro for zero-cost abstraction)
                match find_longest_match!(
                    self,
                    elements,
                    post_skip_pos,
                    &all_terminators,
                    None::<&std::collections::HashSet<u64>>, // No exclude keys for OneOf
                    None::<&usize>,                          // No max count per element for OneOf
                    None::<&std::collections::HashMap<u64, usize>>  // No option counter for OneOf
                ) {
                    Some((node, end_pos, _element_key)) => {
                        // Early exit on complete/terminated match
                        self.pos = end_pos;
                        if self.is_at_end() || self.is_terminated(&all_terminators) {
                            log::debug!("OneOf: Early exit with complete/terminated match");
                            return Ok(node);
                        }

                        log::debug!("MATCHED OneOf matched longest element");

                        // Wrap with leading whitespace if any
                        if !leading_ws.is_empty() {
                            let mut children = leading_ws;
                            children.push(node);
                            return Ok(Node::Sequence(children));
                        }

                        Ok(node)
                    }
                    None => {
                        // No match found
                        self.pos = initial_pos;
                        if *optional {
                            Ok(Node::Empty)
                        } else {
                            Err(ParseError::new("Expected one of choices".into()))
                        }
                    }
                }
            }
            Grammar::AnyNumberOf {
                elements,
                min_times,
                max_times,
                max_times_per_element,
                optional,
                terminators,
                reset_terminators,
                allow_gaps,
                parse_mode,
            } => {
                log::debug!(
                    "Trying AnyNumberOf with {} elements, parse_mode: {:?}, max_times_per_element: {:?}",
                    elements.len(),
                    parse_mode,
                    max_times_per_element
                );
                let mut items = vec![];
                let mut count = 0;
                let initial_pos = self.pos;

                // Track how many times each option has been matched
                let mut option_counter: std::collections::HashMap<u64, usize> =
                    std::collections::HashMap::new();

                // Combine parent and local terminators
                let all_terminators: Vec<Grammar> = if *reset_terminators {
                    terminators.clone()
                } else {
                    terminators
                        .iter()
                        .cloned()
                        .chain(parent_terminators.iter().cloned())
                        .collect()
                };

                // Determine max_idx based on parse_mode
                let max_idx = if *parse_mode == ParseMode::Greedy {
                    self.trim_to_terminator(initial_pos, &all_terminators)
                } else {
                    self.tokens.len()
                };

                log::debug!(
                    "AnyNumberOf max_idx: {} (tokens.len: {})",
                    max_idx,
                    self.tokens.len()
                );

                // Track matched_idx and working_idx like Python
                let mut matched_idx = initial_pos;
                let mut working_idx = initial_pos;

                loop {
                    // Check if we've met min_times and reached limits
                    if count >= *min_times
                        && (matched_idx >= max_idx
                            || (max_times.is_some() && count >= max_times.unwrap()))
                    {
                        log::debug!(
                            "AnyNumberOf: reached limits at {} matches, matched_idx: {}, max_idx: {}",
                            count, matched_idx, max_idx
                        );
                        break;
                    }

                    // Is there nothing left to match?
                    if matched_idx >= max_idx {
                        // If we haven't met the hurdle rate, fail
                        if count < *min_times {
                            if *optional {
                                self.pos = initial_pos;
                                log::debug!("AnyNumberOf returning Empty (didn't meet min_times)");
                                return Ok(Node::Empty);
                            } else {
                                return Err(ParseError::new(format!(
                                    "Expected at least {} occurrences, found {}",
                                    min_times, count
                                )));
                            }
                        }
                        break;
                    }

                    // Save position before attempting match
                    let _pre_match_pos = working_idx;

                    // Update working_idx to skip whitespace if allowed
                    if *allow_gaps {
                        working_idx = self.skip_start_index_forward_to_code(working_idx, max_idx);
                    }

                    // Use the common longest-match logic (macro for zero-cost abstraction)
                    let longest_match_result = find_longest_match!(
                        self,
                        elements,
                        working_idx,
                        &all_terminators,
                        None::<&std::collections::HashSet<u64>>, // No exclude keys for AnyNumberOf
                        max_times_per_element.as_ref(),          // Max count per element
                        Some(&option_counter)                    // Option counter for tracking
                    );

                    // Did we fail to match?
                    if longest_match_result.is_none() {
                        log::debug!("AnyNumberOf: no match found at position {}", working_idx);
                        // If we haven't met the hurdle rate, fail
                        if count < *min_times {
                            if *optional {
                                self.pos = initial_pos;
                                log::debug!(
                                    "AnyNumberOf returning Empty (no match, didn't meet min_times)"
                                );
                                return Ok(Node::Empty);
                            } else {
                                return Err(ParseError::new(format!(
                                    "Expected at least {} occurrences, found {}",
                                    min_times, count
                                )));
                            }
                        }
                        // Otherwise we're done
                        break;
                    }

                    // We have a match!
                    let (node, end_pos, element_key) = longest_match_result.unwrap();

                    // Update the counter for this element
                    *option_counter.entry(element_key).or_insert(0) += 1;

                    // Check if we've now exceeded max_times_per_element for this element
                    if let Some(max_per_elem) = max_times_per_element {
                        let elem_count = option_counter.get(&element_key).copied().unwrap_or(0);
                        if elem_count > *max_per_elem {
                            log::debug!(
                                "AnyNumberOf: element exceeded max_times_per_element, stopping (without including this match)"
                            );
                            // Return the match so far, without the most recent match
                            break;
                        }
                    }

                    // Collect whitespace/non-code between matched_idx and working_idx
                    if *allow_gaps && matched_idx < working_idx {
                        while matched_idx < working_idx {
                            if let Some(tok) = self.tokens.get(matched_idx) {
                                let tok_type = tok.get_type();
                                if tok_type == "whitespace" {
                                    items
                                        .push(Node::Whitespace(tok.raw().to_string(), matched_idx));
                                } else if tok_type == "newline" {
                                    items.push(Node::Newline(tok.raw().to_string(), matched_idx));
                                }
                            }
                            matched_idx += 1;
                        }
                    }

                    // Add the matched node
                    items.push(node);
                    matched_idx = end_pos;
                    working_idx = matched_idx;
                    count += 1;

                    log::debug!(
                        "AnyNumberOf: matched element #{}, matched_idx now: {}",
                        count,
                        matched_idx
                    );

                    // Check max_times limit
                    if let Some(max) = max_times {
                        if count >= *max {
                            log::debug!("AnyNumberOf: reached max_times {}", max);
                            break;
                        }
                    }
                }

                // Update parser position to matched_idx
                self.pos = matched_idx;

                // Apply parse_mode logic for remaining content
                if *parse_mode == ParseMode::Greedy {
                    // Check if there's unparsable content remaining
                    if matched_idx < max_idx {
                        // Check if all remaining is non-code
                        let all_non_code = (matched_idx..max_idx)
                            .all(|i| self.tokens.get(i).map_or(true, |t| !t.is_code()));

                        if !all_non_code {
                            // There's code content we didn't match - create unparsable segment
                            let _trim_idx =
                                self.skip_start_index_forward_to_code(matched_idx, max_idx);

                            log::debug!(
                                "GREEDY mode: creating unparsable segment from {} to {}",
                                _trim_idx,
                                max_idx
                            );

                            // TODO: Create proper UnparsableSegment with expected message
                            // For now, consume as Code nodes
                            while self.pos < max_idx {
                                if let Some(tok) = self.peek() {
                                    let tok_type = tok.get_type();
                                    if tok_type == "whitespace" {
                                        items.push(Node::Whitespace(
                                            tok.raw().to_string(),
                                            self.pos,
                                        ));
                                    } else if tok_type == "newline" {
                                        items.push(Node::Newline(tok.raw().to_string(), self.pos));
                                    } else {
                                        items.push(Node::Code(tok.raw().to_string(), self.pos));
                                    }
                                }
                                self.bump();
                            }
                        }
                    }
                }

                log::debug!(
                    "MATCHED AnyNumberOf with {} items at position {}",
                    items.len(),
                    self.pos
                );
                Ok(Node::DelimitedList(items))
            }
            Grammar::AnySetOf {
                elements,
                min_times,
                max_times,
                optional,
                terminators,
                reset_terminators,
                allow_gaps,
                parse_mode,
            } => {
                // AnySetOf is AnyNumberOf with max_times_per_element=1
                // Each element can only be matched once
                log::debug!(
                    "Trying AnySetOf with {} elements, parse_mode: {:?}",
                    elements.len(),
                    parse_mode
                );

                let mut items = vec![];
                let mut count = 0;
                let initial_pos = self.pos;

                // Track which elements have been matched (by cache key)
                let mut matched_elements: std::collections::HashSet<u64> =
                    std::collections::HashSet::new();

                // Combine parent and local terminators
                let all_terminators: Vec<Grammar> = if *reset_terminators {
                    terminators.clone()
                } else {
                    terminators
                        .iter()
                        .cloned()
                        .chain(parent_terminators.iter().cloned())
                        .collect()
                };

                // Determine max_idx based on parse_mode
                let max_idx = if *parse_mode == ParseMode::Greedy {
                    self.trim_to_terminator(initial_pos, &all_terminators)
                } else {
                    self.tokens.len()
                };

                log::debug!(
                    "AnySetOf max_idx: {} (tokens.len: {})",
                    max_idx,
                    self.tokens.len()
                );

                // Track matched_idx and working_idx
                let mut matched_idx = initial_pos;
                let mut working_idx = initial_pos;

                loop {
                    // Check if we've met min_times and reached limits
                    if count >= *min_times
                        && (matched_idx >= max_idx
                            || (max_times.is_some() && count >= max_times.unwrap()))
                    {
                        log::debug!(
                            "AnySetOf: reached limits at {} matches, matched_idx: {}, max_idx: {}",
                            count,
                            matched_idx,
                            max_idx
                        );
                        break;
                    }

                    // Is there nothing left to match?
                    if matched_idx >= max_idx {
                        // If we haven't met the hurdle rate, fail
                        if count < *min_times {
                            if *optional {
                                self.pos = initial_pos;
                                log::debug!("AnySetOf returning Empty (didn't meet min_times)");
                                return Ok(Node::Empty);
                            } else {
                                return Err(ParseError::new(format!(
                                    "Expected at least {} occurrences, found {}",
                                    min_times, count
                                )));
                            }
                        }
                        break;
                    }

                    // Update working_idx to skip whitespace if allowed
                    if *allow_gaps {
                        working_idx = self.skip_start_index_forward_to_code(working_idx, max_idx);
                    }

                    // Use the common longest-match logic
                    let longest_match_result = find_longest_match!(
                        self,
                        elements,
                        working_idx,
                        &all_terminators,
                        Some(&matched_elements), // Exclude already-matched elements
                        None::<&usize>,          // No max count per element for AnySetOf
                        None::<&std::collections::HashMap<u64, usize>> // No option counter for AnySetOf
                    );

                    // Did we fail to match?
                    if longest_match_result.is_none() {
                        log::debug!("AnySetOf: no match found at position {}", working_idx);
                        // If we haven't met the hurdle rate, fail
                        if count < *min_times {
                            if *optional {
                                self.pos = initial_pos;
                                log::debug!("AnySetOf optional, returning Empty");
                                return Ok(Node::Empty);
                            } else {
                                return Err(ParseError::new(format!(
                                    "Expected at least {} occurrences, found {}",
                                    min_times, count
                                )));
                            }
                        } else {
                            // We met the hurdle, done
                            break;
                        }
                    }

                    // Success - add the match
                    let (node, end_pos, element_key) = longest_match_result.unwrap();

                    // Mark this element as matched (AnySetOf constraint)
                    matched_elements.insert(element_key);

                    items.push(node);
                    matched_idx = end_pos;
                    working_idx = matched_idx;
                    count += 1;

                    log::debug!(
                        "AnySetOf: matched element #{}, matched_idx now: {}",
                        count,
                        matched_idx
                    );

                    // Check max_times limit
                    if let Some(max) = max_times {
                        if count >= *max {
                            log::debug!("AnySetOf: reached max_times {}", max);
                            break;
                        }
                    }
                }

                // Update parser position to matched_idx
                self.pos = matched_idx;

                // Apply parse_mode logic for remaining content (GREEDY mode)
                if *parse_mode == ParseMode::Greedy {
                    // Check if there's unparsable content remaining
                    if matched_idx < max_idx {
                        // Check if all remaining is non-code
                        let all_non_code = (matched_idx..max_idx)
                            .all(|i| self.tokens.get(i).map_or(true, |t| !t.is_code()));

                        if !all_non_code {
                            // There's code content we didn't match - consume as tokens
                            log::debug!(
                                "AnySetOf GREEDY mode: consuming remaining tokens from {} to {}",
                                matched_idx,
                                max_idx
                            );

                            while self.pos < max_idx {
                                if let Some(tok) = self.peek() {
                                    let tok_type = tok.get_type();
                                    if tok_type == "whitespace" {
                                        items.push(Node::Whitespace(
                                            tok.raw().to_string(),
                                            self.pos,
                                        ));
                                    } else if tok_type == "newline" {
                                        items.push(Node::Newline(tok.raw().to_string(), self.pos));
                                    } else {
                                        items.push(Node::Code(tok.raw().to_string(), self.pos));
                                    }
                                }
                                self.bump();
                            }
                        }
                    }
                }

                log::debug!(
                    "MATCHED AnySetOf with {} items at position {}",
                    items.len(),
                    self.pos
                );
                Ok(Node::DelimitedList(items))
            }
            Grammar::Delimited {
                elements,
                delimiter,
                allow_trailing,
                optional,
                terminators,
                reset_terminators,
                allow_gaps,
                min_delimiters,
                parse_mode,
            } => {
                let delim_id = format!("{:p}", delimiter);
                log::debug!(
                    "Trying Delimited[{}] elements at position {}: {:?}",
                    &delim_id[..std::cmp::min(8, delim_id.len())],
                    self.pos,
                    elements
                );
                let mut items = vec![];

                // Combine parent and local terminators
                let filtered_terminators: Vec<Grammar> = terminators
                    .iter()
                    .cloned()
                    .chain(
                        parent_terminators
                            .iter()
                            .filter(|&t| t != delimiter.as_ref())
                            .cloned(),
                    )
                    .collect();

                let all_terminators: Vec<Grammar> = if *reset_terminators {
                    log::debug!(
                        "Delimited: reset_terminators=true, using only local terminators: {:?}",
                        terminators
                    );
                    terminators.clone()
                } else {
                    let before_filter: Vec<Grammar> = terminators
                        .iter()
                        .cloned()
                        .chain(parent_terminators.iter().cloned())
                        .collect();

                    log::debug!(
                        "Delimited: delimiter={},\n before_filter={:?},\n filtered_out={:?},\n all_terminators={:?}",
                        delimiter,
                        before_filter,
                        before_filter.iter().filter(|t| *t == delimiter.as_ref()).collect::<Vec<_>>(),
                        filtered_terminators
                    );

                    filtered_terminators
                };

                if *optional && (self.is_at_end() || self.is_terminated(&all_terminators)) {
                    log::debug!("  TERM Delimited: empty optional");
                    return Ok(Node::DelimitedList(items));
                }

                loop {
                    let mut longest_match: Option<(Node, usize)> = None;
                    let saved_pos = self.pos;

                    // Collect whitespace before element
                    let ws_before = self.collect_transparent(*allow_gaps);
                    let post_skip_saved_pos = self.pos;

                    // Try all elements and find the longest match
                    for elem in elements {
                        self.pos = post_skip_saved_pos;
                        if let Ok(node) = self.parse_with_grammar_cached(elem, &all_terminators) {
                            let consumed = self.pos - post_skip_saved_pos;
                            if consumed > 0 {
                                // Update if this is the longest match so far
                                if longest_match.is_none()
                                    || consumed > longest_match.as_ref().unwrap().1
                                {
                                    longest_match = Some((node, consumed));
                                }
                            }
                        }
                    }

                    // Apply the longest match
                    match longest_match {
                        Some((node, consumed)) => {
                            self.pos = post_skip_saved_pos + consumed;

                            // Add whitespace before the element
                            items.extend(ws_before);
                            items.push(node);
                        }
                        None => {
                            self.pos = saved_pos;
                            log::debug!("Delimited: no more elements matched");
                            break;
                        }
                    }

                    let saved_pos = self.pos;

                    // Collect whitespace before delimiter
                    let ws_before_delim = self.collect_transparent(*allow_gaps);

                    // Check if we're at EOF or a terminator BEFORE trying to match delimiter
                    // If so, we don't need a delimiter (it's only required between elements)
                    if self.is_at_end() || self.is_terminated(&all_terminators) {
                        self.pos = saved_pos; // Restore position to before whitespace collection
                        log::debug!(
                            "Delimited: at EOF or terminator after element, no delimiter required"
                        );
                        break;
                    }

                    if let Ok(delim_node) =
                        self.parse_with_grammar_cached(delimiter, &all_terminators)
                    {
                        if self.is_terminated(&all_terminators) {
                            if !*allow_trailing {
                                return Err(ParseError::new(
                                    "Trailing delimiter not allowed".to_string(),
                                ));
                            }
                            break;
                        }
                        log::debug!("MATCHED Delimited: found delimiter");

                        // Add whitespace before delimiter
                        items.extend(ws_before_delim);
                        items.push(delim_node);
                    } else {
                        self.pos = saved_pos;
                        log::debug!(
                            "Delimited: no delimiter found, ending at position {}",
                            self.pos
                        );
                        break;
                    }
                }

                log::debug!(
                    "Delimited[{}] returning at position {}",
                    &delim_id[..std::cmp::min(8, delim_id.len())],
                    self.pos
                );
                Ok(Node::DelimitedList(items))
            }
            Grammar::Bracketed {
                elements,
                bracket_pairs,
                optional,
                terminators,
                reset_terminators,
                allow_gaps,
                parse_mode,
            } => {
                log::debug!(
                    "Trying Bracketed with {} elements, parse_mode: {:?}",
                    elements.len(),
                    parse_mode
                );

                let start_idx = self.pos;

                // Combine parent and local terminators
                let all_terminators: Vec<Grammar> = if *reset_terminators {
                    terminators.clone()
                } else {
                    terminators
                        .iter()
                        .cloned()
                        .chain(parent_terminators.iter().cloned())
                        .collect()
                };

                // Try to match the opening bracket
                let open_match = self.parse_with_grammar_cached(&bracket_pairs.0, &all_terminators);

                if let Err(_e) = open_match {
                    // No opening bracket found
                    if *optional {
                        return Ok(Node::Empty);
                    } else {
                        return Err(ParseError::new("Expected opening bracket".to_string()));
                    }
                }

                let open_node = open_match.unwrap();
                let mut children = Vec::new();
                children.push(open_node);

                // Position after opening bracket
                let content_start_idx = self.pos;

                // Skip whitespace if allowed
                if *allow_gaps {
                    let _idx =
                        self.skip_start_index_forward_to_code(content_start_idx, self.tokens.len());
                    while self.pos < _idx {
                        if let Some(tok) = self.peek() {
                            let tok_type = tok.get_type();
                            if tok_type == "whitespace" {
                                children.push(Node::Whitespace(tok.raw().to_string(), self.pos));
                            } else if tok_type == "newline" {
                                children.push(Node::Newline(tok.raw().to_string(), self.pos));
                            }
                        }
                        self.bump();
                    }
                }

                // Match the content as a Sequence with the closing bracket as a terminator
                // Create a temporary Sequence grammar for the content
                let content_grammar = Grammar::Sequence {
                    elements: elements.clone(),
                    optional: false,
                    terminators: vec![*bracket_pairs.1.clone()],
                    reset_terminators: true, // Clear parent terminators, use only closing bracket
                    allow_gaps: *allow_gaps,
                    parse_mode: *parse_mode,
                };

                let content_match = self.parse_with_grammar_cached(&content_grammar, &[]);

                // Add content nodes (if any)
                if let Ok(content_node) = content_match {
                    if !content_node.is_empty() {
                        // Extract children from the sequence node
                        if let Node::Sequence(content_children) = content_node {
                            children.extend(content_children);
                        } else {
                            children.push(content_node);
                        }
                    }
                }

                let gap_start = self.pos;

                // Skip whitespace before closing bracket
                if *allow_gaps {
                    let _idx = self.skip_start_index_forward_to_code(self.pos, self.tokens.len());
                    if _idx > gap_start {
                        while self.pos < _idx {
                            if let Some(tok) = self.peek() {
                                let tok_type = tok.get_type();
                                if tok_type == "whitespace" {
                                    children
                                        .push(Node::Whitespace(tok.raw().to_string(), self.pos));
                                } else if tok_type == "newline" {
                                    children.push(Node::Newline(tok.raw().to_string(), self.pos));
                                }
                            }
                            self.bump();
                        }
                    }
                }

                // Check if we've run out of segments
                if self.pos >= self.tokens.len()
                    || self.peek().is_some_and(|t| t.get_type() == "end_of_file")
                {
                    // No end bracket found
                    if *parse_mode == ParseMode::Strict {
                        self.pos = start_idx;
                        return Ok(Node::Empty);
                    }
                    return Err(ParseError::new(
                        "Couldn't find closing bracket for opening bracket".to_string(),
                    ));
                }

                // Try to match the closing bracket
                let close_match =
                    self.parse_with_grammar_cached(&bracket_pairs.1, &[*bracket_pairs.1.clone()]);

                match close_match {
                    Ok(close_node) => {
                        children.push(close_node);
                        log::debug!(
                            "MATCHED Bracketed with {} children at position {}",
                            children.len(),
                            self.pos
                        );
                        Ok(Node::Sequence(children))
                    }
                    Err(_e) => {
                        // No end bracket found
                        if *parse_mode == ParseMode::Strict {
                            self.pos = start_idx;
                            return Ok(Node::Empty);
                        }
                        Err(ParseError::new(
                            "Couldn't find closing bracket for opening bracket".to_string(),
                        ))
                    }
                }
            }
            Grammar::Empty => Ok(Node::Empty),
            Grammar::Nothing() => {
                log::debug!("Expecting nothing grammar");
                Err(ParseError::new("Nothing grammar won't match".into()))
            }
            _ => Err(ParseError::new("Unsupported grammar type".into())),
        }
    }

    pub fn peek(&self) -> Option<&Token> {
        self.tokens.get(self.pos)
    }

    pub fn bump(&mut self) {
        self.pos += 1;
    }

    pub fn is_at_end(&self) -> bool {
        self.pos >= self.tokens.len()
    }

    /// Collect all transparent tokens (whitespace, newlines) as nodes
    pub fn collect_transparent(&mut self, allow_gaps: bool) -> Vec<Node> {
        let mut transparent_nodes = Vec::new();

        if !allow_gaps {
            return transparent_nodes;
        }

        while let Some(tok) = self.peek() {
            if tok.is_code() {
                break;
            }

            let token_pos = self.pos;

            // Skip if already collected
            if self.collected_transparent_positions.contains(&token_pos) {
                self.bump();
                continue;
            }

            let tok_type = tok.get_type();
            let node = if tok_type == "whitespace" {
                Node::Whitespace(tok.raw(), token_pos)
            } else if tok_type == "newline" {
                Node::Newline(tok.raw(), token_pos)
            } else if tok_type == "end_of_file" {
                Node::EndOfFile(tok.raw(), token_pos)
            } else {
                Node::Code(tok.raw(), token_pos) // Fallback for other non-code tokens
            };

            log::debug!(
                "TRANSPARENT collecting token at pos {}: {:?}",
                token_pos,
                tok
            );
            transparent_nodes.push(node);
            self.collected_transparent_positions.insert(token_pos);
            self.bump();
        }

        transparent_nodes
    }

    /// Skip all transparent tokens (whitespace, newlines) without collecting them
    pub fn skip_transparent(&mut self, allow_gaps: bool) {
        if !allow_gaps {
            return;
        }
        while let Some(tok) = self.peek() {
            match tok {
                tok if !tok.is_code() => {
                    log::debug!("NOCODE skipping token: {:?}", tok);
                    self.bump()
                }
                _ => break,
            }
        }
    }

    /// Move an index forward through tokens until tokens[index] is code.
    /// Returns the index of the first code token, or max_idx if none found.
    fn skip_start_index_forward_to_code(&self, start_idx: usize, max_idx: usize) -> usize {
        for _idx in start_idx..max_idx {
            if self.tokens[_idx].is_code() {
                return _idx;
            }
        }
        max_idx
    }

    /// Move an index backward through tokens until tokens[index - 1] is code.
    /// Returns the index after the last code token, or min_idx if none found.
    fn skip_stop_index_backward_to_code(&self, stop_idx: usize, min_idx: usize) -> usize {
        for _idx in (min_idx + 1..=stop_idx).rev() {
            if self.tokens[_idx - 1].is_code() {
                return _idx;
            }
        }
        min_idx
    }

    /// Trim forward segments based on terminators.
    ///
    /// Given a forward set of segments, find the first terminator and return
    /// the index to use as max_idx (trimmed to last code segment before terminator).
    ///
    /// If no terminators are found, returns the original tokens.len().
    fn trim_to_terminator(&mut self, start_idx: usize, terminators: &[Grammar]) -> usize {
        if start_idx >= self.tokens.len() {
            return self.tokens.len();
        }

        let saved_pos = self.pos;
        self.pos = start_idx;

        // Check if already at a terminator immediately
        if self.is_terminated(terminators) {
            self.pos = saved_pos;
            return start_idx;
        }

        // Find first terminator position
        let mut term_pos = self.tokens.len();
        for idx in start_idx..self.tokens.len() {
            self.pos = idx;
            if self.is_terminated(terminators) {
                term_pos = idx;
                break;
            }
        }

        self.pos = saved_pos;

        // Skip backward from terminator to last code
        self.skip_stop_index_backward_to_code(term_pos, start_idx)
    }

    pub fn is_terminated(&mut self, terminators: &[Grammar]) -> bool {
        let init_pos = self.pos;
        self.skip_transparent(true);
        let saved_pos = self.pos;

        // Check if we've reached end of file
        if self.is_at_end() {
            log::debug!("  TERMED Reached end of file");
            self.pos = init_pos; // restore to position before skipping transparent
            return true;
        }

        // Check if current token is end_of_file type
        if let Some(tok) = self.peek() {
            if tok.get_type() == "end_of_file" {
                log::debug!("  TERMED Found end_of_file token");
                self.pos = init_pos; // restore to position before skipping transparent
                return true;
            }
        }

        log::debug!(
            "  TERM Checking terminators: {:?} at pos {:?}",
            terminators,
            self.pos
        );

        // Temporarily disable iterative parser when checking terminators
        // to avoid nested iterative parses with conflicting frame IDs
        let was_iterative = self.use_iterative_parser;
        self.use_iterative_parser = false;

        for term in terminators {
            if let Ok(node) = self.parse_with_grammar_cached(term, &[]) {
                self.pos = saved_pos; // don't consume

                // Check if the node is "empty" in various ways
                let is_empty = node.is_empty();

                if !is_empty {
                    log::debug!("  TERMED Terminator matched: {}", term);
                    self.pos = init_pos; // restore original position
                    self.use_iterative_parser = was_iterative; // restore flag
                    return true;
                }
            }
            self.pos = saved_pos;
        }

        self.use_iterative_parser = was_iterative; // restore flag
        log::debug!("  NOTERM No terminators matched");
        self.pos = init_pos; // restore original position
        false
    }

    /// Get the grammar for a rule by name.
    /// This is used by the iterative parser to expand Ref nodes into their grammars.
    pub fn get_rule_grammar(&self, name: &str) -> Result<Grammar, ParseError> {
        // Look up the grammar for the segment
        match self.get_segment_grammar(name) {
            Some(g) => Ok(g.clone()),
            None => Err(ParseError::unknown_segment(name.to_string())),
        }
    }

    /// Call a grammar rule by name, producing a Node.
    pub fn call_rule(
        &mut self,
        name: &str,
        parent_terminators: &[Grammar],
    ) -> Result<Node, ParseError> {
        // Look up the grammar for the segment
        let grammar = match self.get_segment_grammar(name) {
            Some(g) => g,
            None => return Err(ParseError::unknown_segment(name.to_string())),
        };

        // Parse using the grammar
        let node = self.parse_with_grammar_cached(grammar, parent_terminators)?;

        // If the node is empty, return it as-is without wrapping
        // This prevents infinite loops when optional segments match nothing
        if node.is_empty() {
            return Ok(node);
        }

        // Get the segment type from the dialect
        let segment_type = self.dialect.get_segment_type(name).map(|s| s.to_string());

        // Check if this is a KeywordSegment and the child is a word token
        // If so, convert Node::Code to Node::Keyword
        let processed_node = if name.ends_with("KeywordSegment") {
            tag_keyword_if_word(&node, &self.tokens)
        } else {
            node
        };

        // Wrap in a Ref node for type clarity
        Ok(Node::Ref {
            name: name.to_string(),
            segment_type,
            child: Box::new(processed_node),
        })
    }

    /// Lookup SegmentDef by name
    pub fn get_segment_grammar(&self, name: &str) -> Option<&'static Grammar> {
        self.dialect.get_segment_grammar(name)
    }

    pub fn new(tokens: &'a [Token], dialect: Dialect) -> Parser<'a> {
        Parser {
            tokens,
            pos: 0,
            dialect,
            parse_cache: ParseCache::new(),
            collected_transparent_positions: std::collections::HashSet::new(),
            use_iterative_parser: true, // Default to iterative parser
        }
    }
}

// ParseContext, ParseError, Parsed, and ParseErrorType have been moved to src/parser/types.rs
