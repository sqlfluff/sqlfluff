//! Recursive Parser Implementation
//!
//! This module contains the traditional recursive descent parser implementation
//! with memoization for performance.

use super::{Grammar, ParseMode, Node, ParseError};
use super::core::Parser;
use super::utils::{tag_keyword_if_word, is_grammar_optional, apply_parse_mode_to_result};

use crate::find_longest_match;

impl<'a> Parser<'_> {
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
}
