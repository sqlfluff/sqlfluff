//! Core Parser struct and implementation
//!
//! This module contains the Parser struct definition and its core methods
//! including the main entry point for parsing with grammar.

use std::sync::Arc;

use hashbrown::HashSet;

use super::{cache::ParseCache, Node, ParseError};
use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_types::regex::RegexMode;
use sqlfluffrs_types::{Grammar, SimpleHint, Token};
// NEW: Table-driven grammar support
use sqlfluffrs_types::{GrammarContext, GrammarId, GrammarVariant};

/// A checkpoint in the collection history that tracks which tokens were collected
/// at a specific point. Used for backtracking.
#[derive(Debug, Clone)]
pub struct CollectionCheckpoint {
    /// Frame ID associated with this checkpoint
    pub frame_id: usize,
    /// Token positions that were marked as collected at this checkpoint
    pub positions: Vec<usize>,
}

/// The main parser struct that holds parsing state and provides parsing methods.
pub struct Parser<'a> {
    pub grammar_hash_cache: hashbrown::HashMap<*const Grammar, u64>,
    pub simple_hint_cache: hashbrown::HashMap<u64, Option<SimpleHint>>,
    pub tokens: &'a [Token],
    pub pos: usize, // current position in tokens
    pub dialect: Dialect,
    pub parse_cache: ParseCache,
    pub cache_enabled: bool,
    pub collected_transparent_positions: HashSet<usize>, // Track which token positions have had transparent tokens collected
    /// Stack of collection checkpoints for backtracking.
    /// Each checkpoint records which tokens were marked as collected at that point.
    pub collection_stack: Vec<CollectionCheckpoint>,
    pub pruning_calls: std::cell::Cell<usize>, // Track number of prune_options calls
    pub pruning_total: std::cell::Cell<usize>, // Total options considered
    pub pruning_kept: std::cell::Cell<usize>,  // Options kept after pruning
    pub pruning_hinted: std::cell::Cell<usize>, // Options that had hints
    pub pruning_complex: std::cell::Cell<usize>, // Options that returned None (complex)
    // NEW: Table-driven grammar support (optional, for gradual migration)
    pub grammar_ctx: Option<&'a GrammarContext<'a>>,
    // Regex cache for table-driven RegexParser (pattern_string -> compiled RegexMode)
    regex_cache: std::cell::RefCell<hashbrown::HashMap<String, RegexMode>>,
}

impl<'a> Parser<'a> {
    /// Create a new Parser instance (legacy Arc<Grammar> mode)
    pub fn new(tokens: &'a [Token], dialect: Dialect) -> Parser<'a> {
        Parser {
            tokens,
            pos: 0,
            dialect,
            parse_cache: ParseCache::new(),
            collected_transparent_positions: HashSet::new(),
            collection_stack: Vec::new(),
            pruning_calls: std::cell::Cell::new(0),
            pruning_total: std::cell::Cell::new(0),
            pruning_kept: std::cell::Cell::new(0),
            pruning_hinted: std::cell::Cell::new(0),
            pruning_complex: std::cell::Cell::new(0),
            simple_hint_cache: hashbrown::HashMap::new(),
            grammar_hash_cache: hashbrown::HashMap::new(),
            cache_enabled: true,
            grammar_ctx: None, // NEW: No table-driven grammar initially
            regex_cache: std::cell::RefCell::new(hashbrown::HashMap::new()),
        }
    }

    /// Create a new Parser instance with table-driven grammar support
    pub fn new_with_tables(
        tokens: &'a [Token],
        dialect: Dialect,
        grammar_ctx: &'a GrammarContext<'a>,
    ) -> Parser<'a> {
        Parser {
            tokens,
            pos: 0,
            dialect,
            parse_cache: ParseCache::new(),
            collected_transparent_positions: HashSet::new(),
            collection_stack: Vec::new(),
            pruning_calls: std::cell::Cell::new(0),
            pruning_total: std::cell::Cell::new(0),
            pruning_kept: std::cell::Cell::new(0),
            pruning_hinted: std::cell::Cell::new(0),
            pruning_complex: std::cell::Cell::new(0),
            simple_hint_cache: hashbrown::HashMap::new(),
            grammar_hash_cache: hashbrown::HashMap::new(),
            cache_enabled: true,
            grammar_ctx: Some(grammar_ctx), // NEW: Table-driven grammar enabled
            regex_cache: std::cell::RefCell::new(hashbrown::HashMap::new()),
        }
    }

    /// Enable or disable the parse cache (for debugging)
    pub fn set_cache_enabled(&mut self, enabled: bool) {
        self.cache_enabled = enabled;
    }

    /// Main entry point for parsing with grammar and caching.
    /// Dispatches to either iterative or recursive implementation based on flag.
    pub fn parse_with_grammar_cached(
        &mut self,
        grammar: &Arc<Grammar>,
        parent_terminators: &[Arc<Grammar>],
    ) -> Result<Node, ParseError> {
        self.parse_with_grammar_cached_iterative(grammar, parent_terminators)
    }

    /// Iterative (frame-based) parser with caching.
    /// Uses a stack-based approach to avoid deep recursion.
    fn parse_with_grammar_cached_iterative(
        &mut self,
        grammar: &Arc<Grammar>,
        parent_terminators: &[Arc<Grammar>],
    ) -> Result<Node, ParseError> {
        self.parse_iterative(grammar, parent_terminators)
    }

    /// Parse with table-driven grammar (new implementation).
    /// This is the entry point for GrammarId-based parsing.
    pub fn parse_with_grammar_id(
        &mut self,
        grammar_id: GrammarId,
        parent_terminators: &[GrammarId],
    ) -> Result<Node, ParseError> {
        // Must have grammar context to use table-driven approach
        let ctx = self.grammar_ctx.ok_or_else(|| {
            ParseError::new("parse_with_grammar_id requires GrammarContext".to_string())
        })?;

        // Get the variant enum for this grammar
        let variant = ctx.variant(grammar_id);

        // Dispatch based on variant type
        match variant {
            GrammarVariant::Nothing => self.handle_nothing_table_driven(),
            GrammarVariant::Empty => self.handle_empty_table_driven(),
            GrammarVariant::Missing => self.handle_missing_table_driven(),
            GrammarVariant::Token => self.handle_token_table_driven(grammar_id, ctx),
            GrammarVariant::StringParser => self.handle_string_parser_table_driven(grammar_id, ctx),
            GrammarVariant::TypedParser => self.handle_typed_parser_table_driven(grammar_id, ctx),
            GrammarVariant::MultiStringParser => {
                self.handle_multi_string_parser_table_driven(grammar_id, ctx)
            }
            GrammarVariant::RegexParser => self.handle_regex_parser_table_driven(grammar_id, ctx),
            GrammarVariant::Sequence => {
                self.handle_sequence_table_driven(grammar_id, ctx, parent_terminators)
            }
            GrammarVariant::OneOf => {
                // Table-driven OneOf not yet integrated with iterative parser
                // For now, return an error
                Err(ParseError::new(
                    "OneOf table-driven handler requires iterative parser integration".to_string(),
                ))
            }
            GrammarVariant::Delimited => {
                unimplemented!("Delimited handler not yet migrated")
            }
            GrammarVariant::Bracketed => {
                unimplemented!("Bracketed handler not yet migrated")
            }
            GrammarVariant::AnyNumberOf => {
                unimplemented!("AnyNumberOf handler not yet migrated")
            }
            GrammarVariant::AnySetOf => {
                unimplemented!("AnySetOf handler not yet migrated")
            }
            GrammarVariant::Ref => {
                unimplemented!("Ref handler not yet migrated")
            }
            GrammarVariant::Anything => {
                self.handle_anything_table_driven(grammar_id, ctx, parent_terminators)
            }
            GrammarVariant::Meta => self.handle_meta_table_driven(grammar_id, ctx),
            GrammarVariant::NonCodeMatcher => self.handle_noncode_matcher_table_driven(),
        }
    }

    /// Get the grammar for a rule by name.
    /// This is used by the iterative parser to expand Ref nodes into their grammars.
    pub fn get_rule_grammar(&self, name: &str) -> Result<Arc<Grammar>, ParseError> {
        // Look up the grammar for the segment
        match self.get_segment_grammar(name) {
            Some(g) => Ok(g.clone()),
            None => Err(ParseError::unknown_segment(
                name.to_string(),
                Some(self.pos),
            )),
        }
    }

    /// Call a grammar rule by name, producing a Node.
    pub fn call_rule(
        &mut self,
        name: &str,
        parent_terminators: &[Arc<Grammar>],
    ) -> Result<Node, ParseError> {
        self.call_rule_with_type(name, parent_terminators, None)
    }

    pub fn call_rule_with_type(
        &mut self,
        name: &str,
        parent_terminators: &[Arc<Grammar>],
        segment_type: Option<&str>,
    ) -> Result<Node, ParseError> {
        // Look up the grammar for the segment
        let grammar = match self.get_segment_grammar(name) {
            Some(g) => g,
            None => {
                return Err(ParseError::unknown_segment(
                    name.to_string(),
                    Some(self.pos),
                ))
            }
        };

        // Parse using the grammar
        let node = self.parse_with_grammar_cached(&grammar, parent_terminators)?;

        // If the node is empty, return it as-is without wrapping
        // This prevents infinite loops when optional segments match nothing
        if node.is_empty() {
            return Ok(node);
        }

        // Use provided segment_type, or infer from Token nodes
        let final_segment_type = match segment_type {
            Some(st) => Some(st.to_string()),
            None => match &node {
                Node::Token {
                    token_type: t,
                    raw: _,
                    token_idx: _,
                } => Some(t.clone()),
                _ => None,
            },
        };

        // Wrap in a Ref node for type clarity
        let result = Node::Ref {
            name: name.to_string(),
            segment_type: final_segment_type,
            child: Box::new(node),
        };

        // Deduplicate whitespace/newline nodes to handle cases where both
        // parent and child grammars collected the same tokens
        Ok(result.deduplicate())
    }

    pub fn call_rule_as_root(&mut self) -> Result<Node, ParseError> {
        let root_grammar = self.dialect.get_root_grammar();
        let mut last_non_code_pos = self.tokens.len();
        for (i, token) in self.tokens.iter().enumerate().rev() {
            if !token.is_code() {
                last_non_code_pos = i;
                break;
            }
        }
        let token_slice_orig = self.tokens;
        let token_slice = &self.tokens[..last_non_code_pos];
        let end_nodes = self.end_children_nodes(last_non_code_pos);

        if token_slice.is_empty() {
            // Wrap in a Ref node for type clarity
            let result = Node::Ref {
                name: "Root".to_string(),
                segment_type: Some("file".to_string()),
                child: Box::new(Node::Sequence {
                    children: end_nodes,
                }),
            };
            return Ok(result.deduplicate());
        }

        self.tokens = token_slice;
        let nodes = self.parse_with_grammar_cached(&root_grammar, &[]);
        self.tokens = token_slice_orig;
        match nodes {
            Ok(mut n) => {
                // If we have end nodes, wrap in File
                if !end_nodes.is_empty() {
                    let mut children = vec![n];
                    let end_len = end_nodes.len();
                    children.extend(end_nodes);
                    n = Node::Sequence { children };
                    self.pos += end_len;
                }
                let result = Node::Ref {
                    name: "Root".to_string(),
                    segment_type: Some("file".to_string()),
                    child: Box::new(n),
                };
                Ok(result.deduplicate())
            }
            Err(e) => Err(e),
        }
    }

    fn end_children_nodes(&mut self, start_idx: usize) -> Vec<Node> {
        // Only non-code tokens present; return them as nodes with type mapping
        let mut children = Vec::new();
        for (i, token) in self.tokens[start_idx..].iter().enumerate() {
            if token.is_code() {
                break;
            }
            let node = match token.get_type().as_str() {
                "meta" => Node::Meta {
                    token_type: "meta".to_string(),
                    token_idx: Some(start_idx + i),
                },
                "dedent" => Node::Meta {
                    token_type: "dedent".to_string(),
                    token_idx: Some(start_idx + i),
                },
                "whitespace" => Node::Whitespace {
                    raw: token.raw().to_string(),
                    token_idx: start_idx + i,
                },
                "newline" => Node::Newline {
                    raw: token.raw().to_string(),
                    token_idx: start_idx + i,
                },
                "end_of_file" => Node::EndOfFile {
                    raw: token.raw().to_string(),
                    token_idx: start_idx + i,
                },
                other => Node::Token {
                    token_type: other.to_string(),
                    raw: token.raw().to_string(),
                    token_idx: start_idx + i,
                },
            };
            children.push(node);
        }
        children
    }

    /// Lookup SegmentDef by name
    pub fn get_segment_grammar(&self, name: &str) -> Option<Arc<Grammar>> {
        self.dialect.get_segment_grammar(name)
    }

    /// Push a checkpoint onto the collection stack when starting to process a grammar.
    /// This records the current state so we can backtrack if needed.
    pub fn push_collection_checkpoint(&mut self, frame_id: usize) {
        self.collection_stack.push(CollectionCheckpoint {
            frame_id,
            positions: Vec::new(),
        });
        log::debug!(
            "Pushed collection checkpoint for frame_id={}, stack depth={}",
            frame_id,
            self.collection_stack.len()
        );
    }

    /// Mark a token position as collected and record it in the current checkpoint.
    /// Returns true if the position was newly inserted, false if it was already collected.
    pub fn mark_position_collected(&mut self, pos: usize) -> bool {
        let was_new = self.collected_transparent_positions.insert(pos);
        if was_new {
            // Record this collection in the current checkpoint
            if let Some(checkpoint) = self.collection_stack.last_mut() {
                checkpoint.positions.push(pos);
                log::debug!(
                    "Marked position {} as collected in checkpoint for frame_id={}",
                    pos,
                    checkpoint.frame_id
                );
            }
        }
        was_new
    }

    /// Pop a checkpoint and commit its collections (keep them marked).
    /// This is called when a grammar successfully produces a result that will be used.
    pub fn commit_collection_checkpoint(&mut self, frame_id: usize) {
        if let Some(checkpoint) = self.collection_stack.pop() {
            if checkpoint.frame_id != frame_id {
                log::warn!(
                    "Checkpoint frame_id mismatch: expected {}, got {}",
                    frame_id,
                    checkpoint.frame_id
                );
            }
            log::debug!(
                "Committed {} collected positions for frame_id={}, stack depth now={}",
                checkpoint.positions.len(),
                frame_id,
                self.collection_stack.len()
            );
            // Positions remain in collected_transparent_positions - they're committed
        }
    }

    /// Pop a checkpoint and rollback its collections (unmark them).
    /// This is called when a grammar fails or is abandoned during backtracking.
    pub fn rollback_collection_checkpoint(&mut self, frame_id: usize) {
        if let Some(checkpoint) = self.collection_stack.pop() {
            if checkpoint.frame_id != frame_id {
                log::warn!(
                    "Checkpoint frame_id mismatch during rollback: expected {}, got {}",
                    frame_id,
                    checkpoint.frame_id
                );
            }
            log::debug!(
                "Rolling back {} collected positions for frame_id={}, stack depth now={}",
                checkpoint.positions.len(),
                frame_id,
                self.collection_stack.len()
            );
            // Remove all positions that were marked during this checkpoint
            for pos in checkpoint.positions {
                self.collected_transparent_positions.remove(&pos);
            }
        }
    }

    // ============================================================================
    // Table-Driven Handler Methods (Base Parsers)
    // ============================================================================

    /// Handle StringParser using table-driven approach
    fn handle_string_parser_table_driven(
        &mut self,
        grammar_id: GrammarId,
        ctx: &GrammarContext,
    ) -> Result<Node, ParseError> {
        // Extract all data from tables first (before any self methods)
        let inst = ctx.inst(grammar_id);
        let tables = ctx.tables();

        // StringParser stores: [template_id, token_type_id, raw_class_id] in aux_data
        // first_child_idx holds the aux_data offset
        let aux_start = inst.first_child_idx as usize;
        let template_id = tables.aux_data[aux_start];
        let token_type_id = tables.aux_data[aux_start + 1];

        let template = tables.get_string(template_id).to_string();
        let token_type = tables.get_string(token_type_id).to_string();

        log::debug!(
            "StringParser[table]: pos={}, template='{}', token_type='{}'",
            self.pos,
            template,
            token_type
        );

        match self.peek() {
            Some(tok) if tok.raw().eq_ignore_ascii_case(&template) => {
                let token_pos = self.pos;
                let raw = tok.raw().to_string();
                self.bump();

                log::debug!(
                    "StringParser[table] MATCHED: token='{}' at pos={}",
                    raw,
                    token_pos
                );

                Ok(Node::Token {
                    token_type,
                    raw,
                    token_idx: token_pos,
                })
            }
            _ => {
                log::debug!(
                    "StringParser[table] NOMATCH: template='{}', token={:?}",
                    template,
                    self.peek().map(|t| t.raw())
                );
                Ok(Node::Empty)
            }
        }
    }

    /// Handle TypedParser using table-driven approach
    fn handle_typed_parser_table_driven(
        &mut self,
        grammar_id: GrammarId,
        ctx: &GrammarContext,
    ) -> Result<Node, ParseError> {
        // Extract all data from tables first (before any self methods)
        let inst = ctx.inst(grammar_id);
        let tables = ctx.tables();

        // TypedParser stores: [template_id, token_type_id, raw_class_id] in aux_data
        // first_child_idx holds the aux_data offset
        let aux_start = inst.first_child_idx as usize;
        let template_id = tables.aux_data[aux_start];
        let token_type_id = tables.aux_data[aux_start + 1];

        let template = tables.get_string(template_id).to_string();
        let token_type = tables.get_string(token_type_id).to_string();

        log::debug!(
            "TypedParser[table]: pos={}, template='{}', token_type='{}'",
            self.pos,
            template,
            token_type
        );

        match self.peek() {
            Some(tok) if tok.is_type(&[&template]) => {
                let token_pos = self.pos;
                let raw = tok.raw().to_string();
                let token_type_val = tok.token_type.clone();
                self.bump();

                log::debug!(
                    "TypedParser[table] MATCHED: type='{}', raw='{}' at pos={}",
                    token_type_val,
                    raw,
                    token_pos
                );

                Ok(Node::Token {
                    token_type,
                    raw,
                    token_idx: token_pos,
                })
            }
            Some(tok) => {
                log::debug!(
                    "TypedParser[table] NOMATCH: expected type '{}', found type '{}', raw '{}'",
                    template,
                    tok.token_type,
                    tok.raw()
                );
                Ok(Node::Empty)
            }
            None => {
                log::debug!("TypedParser[table] NOMATCH: EOF at pos={}", self.pos);
                Ok(Node::Empty)
            }
        }
    }

    /// Handle MultiStringParser using table-driven approach
    fn handle_multi_string_parser_table_driven(
        &mut self,
        grammar_id: GrammarId,
        ctx: &GrammarContext,
    ) -> Result<Node, ParseError> {
        // Extract all data from tables first (before any self methods)
        let inst = ctx.inst(grammar_id);
        let tables = ctx.tables();

        // MultiStringParser stores: [templates_start, templates_count, token_type_id, raw_class_id] in aux_data
        // first_child_idx holds the aux_data offset
        let aux_start = inst.first_child_idx as usize;
        let templates_start = tables.aux_data[aux_start] as usize;
        let templates_count = tables.aux_data[aux_start + 1] as usize;
        let token_type_id = tables.aux_data[aux_start + 2];

        let templates: Vec<String> = (0..templates_count)
            .map(|i| {
                let template_id = tables.aux_data[templates_start + i];
                tables.get_string(template_id).to_string()
            })
            .collect();

        let token_type = tables.get_string(token_type_id).to_string();

        log::debug!(
            "MultiStringParser[table]: pos={}, templates={:?}, token_type='{}'",
            self.pos,
            templates,
            token_type
        );

        match self.peek() {
            Some(tok) if templates.iter().any(|t| tok.raw().eq_ignore_ascii_case(t)) => {
                let token_pos = self.pos;
                let raw = tok.raw().to_string();
                self.bump();

                log::debug!(
                    "MultiStringParser[table] MATCHED: token='{}' at pos={}",
                    raw,
                    token_pos
                );

                Ok(Node::Token {
                    token_type,
                    raw,
                    token_idx: token_pos,
                })
            }
            _ => {
                log::debug!(
                    "MultiStringParser[table] NOMATCH: templates={:?}, token={:?}",
                    templates,
                    self.peek().map(|t| t.raw())
                );
                Ok(Node::Empty)
            }
        }
    }

    /// Handle RegexParser using table-driven approach
    fn handle_regex_parser_table_driven(
        &mut self,
        grammar_id: GrammarId,
        ctx: &GrammarContext,
    ) -> Result<Node, ParseError> {
        // Extract all data from tables first (before any self methods)
        let inst = ctx.inst(grammar_id);
        let tables = ctx.tables();

        // RegexParser stores: [regex_id, anti_regex_id, token_type_id, raw_class_id] in aux_data
        // first_child_idx holds the aux_data offset
        let aux_start = inst.first_child_idx as usize;
        let regex_id = tables.aux_data[aux_start] as usize;
        let anti_regex_id = tables.aux_data[aux_start + 1];
        let token_type_id = tables.aux_data[aux_start + 2];

        let pattern_str = tables.regex_patterns[regex_id];
        let anti_pattern_str = if anti_regex_id != 0xFFFFFFFF {
            Some(tables.regex_patterns[anti_regex_id as usize])
        } else {
            None
        };
        let token_type = tables.get_string(token_type_id).to_string();

        // Compile regex patterns (with caching)
        let pattern = {
            let mut cache = self.regex_cache.borrow_mut();
            cache
                .entry(pattern_str.to_string())
                .or_insert_with(|| RegexMode::new(pattern_str))
                .clone()
        };

        let anti_pattern = if let Some(anti_str) = anti_pattern_str {
            let mut cache = self.regex_cache.borrow_mut();
            Some(
                cache
                    .entry(anti_str.to_string())
                    .or_insert_with(|| RegexMode::new(anti_str))
                    .clone(),
            )
        } else {
            None
        };

        log::debug!(
            "RegexParser[table]: pos={}, pattern='{}', token_type='{}'",
            self.pos,
            pattern_str,
            token_type
        );

        match self.peek() {
            Some(tok) => {
                let raw = tok.raw();

                // Check anti-pattern first (if present, should NOT match)
                if let Some(ref anti) = anti_pattern {
                    if anti.is_match(&raw) {
                        log::debug!("RegexParser[table] anti-pattern matched, returning Empty");
                        return Ok(Node::Empty);
                    }
                }

                // Check main pattern
                if pattern.is_match(&raw) {
                    let token_pos = self.pos;
                    let raw = raw.to_string();
                    self.bump();

                    log::debug!(
                        "RegexParser[table] MATCHED: token='{}' at pos={}",
                        raw,
                        token_pos
                    );

                    Ok(Node::Token {
                        token_type,
                        raw,
                        token_idx: token_pos,
                    })
                } else {
                    log::debug!(
                        "RegexParser[table] NOMATCH: pattern '{}' didn't match token='{}'",
                        pattern_str,
                        raw
                    );
                    Ok(Node::Empty)
                }
            }
            None => {
                log::debug!("RegexParser[table] NOMATCH: EOF at pos={}", self.pos);
                Ok(Node::Empty)
            }
        }
    }

    // ============================================================================
    // Table-Driven Handler Methods (Base Grammars)
    // ============================================================================

    /// Handle Nothing using table-driven approach
    fn handle_nothing_table_driven(&mut self) -> Result<Node, ParseError> {
        log::debug!("Nothing[table]: pos={}, returning Empty", self.pos);
        Ok(Node::Empty)
    }

    /// Handle Empty using table-driven approach
    fn handle_empty_table_driven(&mut self) -> Result<Node, ParseError> {
        log::debug!("Empty[table]: pos={}, returning Empty", self.pos);
        Ok(Node::Empty)
    }

    /// Handle Missing using table-driven approach
    fn handle_missing_table_driven(&mut self) -> Result<Node, ParseError> {
        log::debug!("Missing[table]: encountered at pos={}", self.pos);
        Err(ParseError::with_context(
            "Encountered Missing grammar".into(),
            Some(self.pos),
            None,
        ))
    }

    /// Handle Token using table-driven approach
    fn handle_token_table_driven(
        &mut self,
        grammar_id: GrammarId,
        ctx: &GrammarContext,
    ) -> Result<Node, ParseError> {
        // Extract token_type from tables
        let inst = ctx.inst(grammar_id);
        let tables = ctx.tables();

        // Token stores token_type string id in first_child_idx
        let token_type_id = inst.first_child_idx;
        let token_type = tables.get_string(token_type_id).to_string();

        log::debug!(
            "Token[table]: pos={}, token_type='{}'",
            self.pos,
            token_type
        );

        match self.peek() {
            Some(tok) if tok.is_type(&[&token_type]) => {
                let token_pos = self.pos;
                let raw = tok.raw().to_string();
                self.bump();

                log::debug!(
                    "Token[table] MATCHED: type='{}', raw='{}' at pos={}",
                    token_type,
                    raw,
                    token_pos
                );

                Ok(Node::Token {
                    token_type,
                    raw,
                    token_idx: token_pos,
                })
            }
            Some(tok) => {
                log::debug!(
                    "Token[table] NOMATCH: expected type '{}', found type '{}'",
                    token_type,
                    tok.get_type()
                );
                Err(ParseError::new(format!(
                    "Expected token type {}, found {}",
                    token_type,
                    tok.get_type()
                )))
            }
            None => {
                log::debug!("Token[table] NOMATCH: EOF at pos={}", self.pos);
                Err(ParseError::new("Expected token, found EOF".into()))
            }
        }
    }

    /// Handle Meta using table-driven approach
    fn handle_meta_table_driven(
        &mut self,
        grammar_id: GrammarId,
        ctx: &GrammarContext,
    ) -> Result<Node, ParseError> {
        // Extract token_type from tables
        let inst = ctx.inst(grammar_id);
        let tables = ctx.tables();

        // Meta stores token_type string id in first_child_idx
        let token_type_id = inst.first_child_idx;
        let token_type = tables.get_string(token_type_id).to_string();

        log::debug!("Meta[table]: pos={}, token_type='{}'", self.pos, token_type);

        Ok(Node::Meta {
            token_type,
            token_idx: None,
        })
    }

    /// Handle NonCodeMatcher using table-driven approach
    fn handle_noncode_matcher_table_driven(&mut self) -> Result<Node, ParseError> {
        log::debug!("NonCodeMatcher[table]: pos={}", self.pos);

        match self.peek() {
            Some(tok) => {
                let typ = tok.get_type();
                if typ == "whitespace" || typ == "newline" {
                    let token_pos = self.pos;
                    let raw = tok.raw().to_string();
                    self.bump();

                    log::debug!(
                        "NonCodeMatcher[table] MATCHED: type='{}', raw='{}' at pos={}",
                        typ,
                        raw,
                        token_pos
                    );

                    Ok(Node::Token {
                        token_type: typ.to_string(),
                        raw,
                        token_idx: token_pos,
                    })
                } else {
                    log::debug!(
                        "NonCodeMatcher[table] NOMATCH: found code token type='{}'",
                        typ
                    );
                    Ok(Node::Empty)
                }
            }
            None => {
                log::debug!("NonCodeMatcher[table] NOMATCH: EOF at pos={}", self.pos);
                Ok(Node::Empty)
            }
        }
    }

    // ============================================================================
    // Table-Driven Handler Methods (Composite Grammars)
    // ============================================================================

    /// Handle Sequence using table-driven approach
    /// Simplified recursive implementation - matches children in order
    fn handle_sequence_table_driven(
        &mut self,
        grammar_id: GrammarId,
        ctx: &GrammarContext,
        parent_terminators: &[GrammarId],
    ) -> Result<Node, ParseError> {
        let inst = ctx.inst(grammar_id);
        let start_pos = self.pos;

        log::debug!(
            "Sequence[table]: pos={}, children={}",
            start_pos,
            inst.child_count
        );

        let mut matched_nodes = Vec::new();

        // Iterate through child grammars
        for child_id in ctx.children(grammar_id) {
            let child_result = self.parse_with_grammar_id(child_id, parent_terminators)?;

            match child_result {
                Node::Empty => {
                    // Child didn't match - check if it's optional
                    if ctx.is_optional(child_id) {
                        log::debug!(
                            "Sequence[table]: child {} returned Empty (optional), skipping",
                            child_id.0
                        );
                        continue; // Skip optional element
                    } else {
                        // Required element didn't match
                        if inst.flags.optional() {
                            // Whole sequence is optional, return Empty
                            log::debug!(
                                "Sequence[table]: required child failed but sequence is optional"
                            );
                            self.pos = start_pos; // Backtrack
                            return Ok(Node::Empty);
                        } else {
                            // Required sequence with required element - fail
                            log::debug!("Sequence[table]: required child {} failed", child_id.0);
                            self.pos = start_pos; // Backtrack
                            return Err(ParseError::new(format!(
                                "Required element in sequence did not match at pos {}",
                                self.pos
                            )));
                        }
                    }
                }
                _ => {
                    // Child matched successfully
                    log::debug!(
                        "Sequence[table]: child {} matched, pos now {}",
                        child_id.0,
                        self.pos
                    );
                    matched_nodes.push(child_result);
                }
            }
        }

        if matched_nodes.is_empty() {
            log::debug!("Sequence[table]: no children matched, returning Empty");
            Ok(Node::Empty)
        } else {
            log::debug!(
                "Sequence[table]: matched {} children, pos {} -> {}",
                matched_nodes.len(),
                start_pos,
                self.pos
            );
            Ok(Node::Sequence {
                children: matched_nodes,
            })
        }
    }

    /// Handle OneOf Initial state using table-driven approach
    /// This is the entry point - pushes first child onto stack
    pub(crate) fn handle_oneof_table_driven_initial(
        &mut self,
        grammar_id: GrammarId,
        mut frame: crate::parser::ParseFrame,
        parent_terminators: &[GrammarId],
        stack: &mut crate::parser::iterative::ParseFrameStack,
    ) -> Result<crate::parser::iterative::FrameResult, ParseError> {
        use crate::parser::iterative::FrameResult;
        use crate::parser::{FrameContext, FrameState};

        // CRITICAL: Restore parser position from frame
        self.pos = frame.pos;
        let ctx = self
            .grammar_ctx
            .expect("GrammarContext required for table-driven parsing");

        let inst = ctx.inst(grammar_id);
        let start_pos = frame.pos;

        log::debug!(
            "OneOf[table] Initial: frame_id={}, pos={}, grammar_id={}, children={}",
            frame.frame_id,
            start_pos,
            grammar_id.0,
            inst.child_count
        );

        // TODO: Handle exclude grammar, pruning, allow_gaps
        // For now, simple implementation without those features

        // TODO: Calculate max_idx with terminators
        let max_idx = self.tokens.len();

        // Get all children
        let all_children: Vec<GrammarId> = ctx.children(grammar_id).collect();

        if all_children.is_empty() {
            log::debug!("OneOf[table]: No children, returning Empty");
            stack
                .results
                .insert(frame.frame_id, (Node::Empty, start_pos, None));
            return Ok(FrameResult::Done);
        }

        // Try first child
        let first_child = all_children[0];

        log::debug!(
            "OneOf[table]: Trying first child grammar_id={}",
            first_child.0
        );

        // Store context for WaitingForChild state
        frame.context = FrameContext::OneOfTableDriven {
            grammar_id,
            pruned_children: all_children.clone(),
            leading_ws: Vec::new(),
            post_skip_pos: start_pos,
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

        // Create table-driven child frame
        // TODO: Convert parent_terminators from Vec<GrammarId> to proper terminators
        let child_frame = crate::parser::ParseFrame::new_table_driven_child(
            stack.frame_id_counter,
            first_child,
            start_pos,
            parent_terminators.to_vec(),
            Some(max_idx),
        );

        stack.increment_frame_id_counter();
        stack.push(&mut frame);
        stack.push(&mut child_frame.clone());

        Ok(FrameResult::Done)
    }

    /// Handle OneOf WaitingForChild state using table-driven approach
    /// Processes child result and tries next option or finalizes
    pub(crate) fn handle_oneof_table_driven_waiting_for_child(
        &mut self,
        mut frame: crate::parser::ParseFrame,
        child_node: &Node,
        child_end_pos: &usize,
        _child_element_key: &Option<u64>,
        stack: &mut crate::parser::iterative::ParseFrameStack,
    ) -> Result<crate::parser::iterative::FrameResult, ParseError> {
        use crate::parser::iterative::FrameResult;
        use crate::parser::{FrameContext, FrameState};

        let _ctx = self.grammar_ctx.expect("GrammarContext required");

        let FrameContext::OneOfTableDriven {
            grammar_id: _,
            pruned_children,
            post_skip_pos,
            longest_match,
            tried_elements,
            max_idx: _,
            current_child_id,
            ..
        } = &mut frame.context
        else {
            unreachable!("Expected OneOfTableDriven context");
        };

        let consumed = *child_end_pos - *post_skip_pos;
        let current_child = current_child_id.expect("current_child_id should be set");

        log::debug!(
            "OneOf[table] WaitingForChild: frame_id={}, child_empty={}, consumed={}, tried={}/{}",
            frame.frame_id,
            child_node.is_empty(),
            consumed,
            tried_elements,
            pruned_children.len()
        );

        // Update longest match if this is better
        if !child_node.is_empty() {
            let child_is_clean = Self::is_node_clean(child_node);
            let is_better = if let Some((ref current_best, current_consumed, _)) = longest_match {
                let current_is_clean = Self::is_node_clean(current_best);

                // Prioritize clean matches over unclean, then by length
                if child_is_clean && !current_is_clean {
                    true
                } else if !child_is_clean && current_is_clean {
                    false
                } else {
                    consumed > *current_consumed
                }
            } else {
                true // No previous match
            };

            if is_better {
                log::debug!(
                    "OneOf[table]: Found better match! child={}, consumed={}, clean={}",
                    current_child.0,
                    consumed,
                    child_is_clean
                );
                *longest_match = Some((child_node.clone(), consumed, current_child));

                // TODO: Check early termination conditions (reached max_idx, terminators)
            }
        }

        *tried_elements += 1;

        // Try next child or finalize
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

            // TODO: Push next child frame
            stack.push(&mut frame);
            return Ok(FrameResult::Done);
        } else {
            // All children tried - transition to Combining
            log::debug!(
                "OneOf[table]: All {} children tried, transitioning to Combining",
                pruned_children.len()
            );
            frame.state = FrameState::Combining;
            stack.push(&mut frame);
            return Ok(FrameResult::Done);
        }
    }

    /// Handle OneOf Combining state using table-driven approach
    /// Builds final result from longest match
    pub(crate) fn handle_oneof_table_driven_combining(
        &mut self,
        mut frame: crate::parser::ParseFrame,
        stack: &mut crate::parser::iterative::ParseFrameStack,
    ) -> Result<crate::parser::iterative::FrameResult, ParseError> {
        use crate::parser::iterative::FrameResult;
        use crate::parser::{FrameContext, FrameState};

        let ctx = self.grammar_ctx.expect("GrammarContext required");
        let _stack = stack; // Suppress unused warning - will be used when child pushing is implemented

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

        // Build final result
        let (result_node, final_pos, _child_id) =
            if let Some((best_node, best_consumed, best_child_id)) = longest_match {
                let final_pos = *post_skip_pos + *best_consumed;
                self.pos = final_pos;

                let result = if !leading_ws.is_empty() {
                    let mut children = leading_ws.clone();
                    children.push(best_node.clone());
                    Node::Sequence { children }
                } else {
                    best_node.clone()
                };

                (result, final_pos, Some(*best_child_id))
            } else {
                // No match found
                let result_node = if inst.flags.optional() {
                    Node::Empty
                } else {
                    // TODO: Apply parse_mode (Greedy vs Strict)
                    Node::Empty
                };
                let final_pos = frame.pos;
                self.pos = final_pos;

                (result_node, final_pos, None)
            };

        // Transition to Complete
        frame.end_pos = Some(final_pos);
        frame.state = FrameState::Complete(result_node);

        Ok(FrameResult::Push(frame))
    }

    // ========================================================================
    // Table-Driven Sequence Handlers
    // ========================================================================

    /// Handle Sequence Initial state using table-driven approach
    pub(crate) fn handle_sequence_table_driven_initial(
        &mut self,
        grammar_id: GrammarId,
        mut frame: crate::parser::ParseFrame,
        parent_terminators: &[GrammarId],
        stack: &mut crate::parser::iterative::ParseFrameStack,
    ) -> Result<crate::parser::iterative::FrameResult, ParseError> {
        use crate::parser::iterative::FrameResult;
        use crate::parser::{FrameContext, FrameState};

        self.pos = frame.pos;
        let ctx = self.grammar_ctx.expect("GrammarContext required");

        let inst = ctx.inst(grammar_id);
        let start_pos = frame.pos;

        log::debug!(
            "Sequence[table] Initial: frame_id={}, pos={}, grammar_id={}, children={}",
            frame.frame_id,
            start_pos,
            grammar_id.0,
            inst.child_count
        );

        // Get all children
        let all_children: Vec<GrammarId> = ctx.children(grammar_id).collect();

        if all_children.is_empty() {
            log::debug!("Sequence[table]: No children, returning Empty");
            frame.end_pos = Some(start_pos);
            frame.state = FrameState::Combining;
            stack.push(&mut frame);
            return Ok(FrameResult::Done);
        }

        // TODO: Calculate max_idx with terminators, handle parse_mode
        let max_idx = self.tokens.len();

        // Push collection checkpoint for backtracking
        self.push_collection_checkpoint(frame.frame_id);

        // Store context
        frame.context = FrameContext::SequenceTableDriven {
            grammar_id,
            matched_idx: start_pos,
            tentatively_collected: vec![],
            max_idx,
            original_max_idx: max_idx,
            last_child_frame_id: Some(stack.frame_id_counter),
            current_element_idx: 0,
            first_match: true,
        };

        frame.state = FrameState::WaitingForChild {
            child_index: 0,
            total_children: all_children.len(),
        };

        // Create first child frame
        let first_child = all_children[0];
        let child_frame = crate::parser::ParseFrame::new_table_driven_child(
            stack.frame_id_counter,
            first_child,
            start_pos,
            parent_terminators.to_vec(),
            Some(max_idx),
        );

        log::debug!(
            "Sequence[table]: Trying first child grammar_id={}",
            first_child.0
        );

        stack.increment_frame_id_counter();
        stack.push(&mut frame);
        stack.push(&mut child_frame.clone());

        Ok(FrameResult::Done)
    }

    /// Handle Sequence WaitingForChild state using table-driven approach
    pub(crate) fn handle_sequence_table_driven_waiting_for_child(
        &mut self,
        mut frame: crate::parser::ParseFrame,
        child_node: &Node,
        child_end_pos: &usize,
        _child_element_key: &Option<u64>,
        stack: &mut crate::parser::iterative::ParseFrameStack,
    ) -> Result<crate::parser::iterative::FrameResult, ParseError> {
        use crate::parser::iterative::FrameResult;
        use crate::parser::{FrameContext, FrameState};

        let ctx = self.grammar_ctx.expect("GrammarContext required");

        let FrameContext::SequenceTableDriven {
            grammar_id,
            matched_idx,
            tentatively_collected: _,
            max_idx,
            original_max_idx: _,
            current_element_idx,
            first_match: _,
            ..
        } = &mut frame.context
        else {
            unreachable!("Expected SequenceTableDriven context");
        };

        let inst = ctx.inst(*grammar_id);
        let all_children: Vec<GrammarId> = ctx.children(*grammar_id).collect();

        log::debug!(
            "Sequence[table] WaitingForChild: frame_id={}, child_empty={}, child_end_pos={}, current_idx={}/{}",
            frame.frame_id,
            child_node.is_empty(),
            child_end_pos,
            current_element_idx,
            all_children.len()
        );

        // Check if child matched
        if !child_node.is_empty() {
            // Child matched - add to accumulated results
            frame.accumulated.push(child_node.clone());
            *matched_idx = *child_end_pos;
            *current_element_idx += 1;

            // Check if we have more children to match
            if *current_element_idx < all_children.len() {
                // Try next child
                let next_child = all_children[*current_element_idx];

                log::debug!(
                    "Sequence[table]: Trying next child grammar_id={}",
                    next_child.0
                );

                self.pos = *matched_idx;

                let child_frame = crate::parser::ParseFrame::new_table_driven_child(
                    stack.frame_id_counter,
                    next_child,
                    *matched_idx,
                    frame.table_terminators.clone(),
                    Some(*max_idx),
                );

                frame.state = FrameState::WaitingForChild {
                    child_index: *current_element_idx,
                    total_children: all_children.len(),
                };

                stack.increment_frame_id_counter();
                stack.push(&mut frame);
                stack.push(&mut child_frame.clone());
                return Ok(FrameResult::Done);
            } else {
                // All children matched - transition to Combining
                log::debug!(
                    "Sequence[table]: All {} children matched, transitioning to Combining",
                    all_children.len()
                );
                self.pos = *matched_idx;
                frame.end_pos = Some(*matched_idx);
                frame.state = FrameState::Combining;
                stack.push(&mut frame);
                return Ok(FrameResult::Done);
            }
        } else {
            // Child failed (returned Empty)
            // TODO: Check if element is optional vs required
            // TODO: Handle parse_mode (Strict vs Greedy)
            // For now, treat as failure
            log::debug!(
                "Sequence[table]: Child {} returned Empty, sequence failed",
                current_element_idx
            );

            // Rollback collection checkpoint
            self.rollback_collection_checkpoint(frame.frame_id);

            frame.end_pos = Some(frame.pos);
            frame.state = FrameState::Combining;
            stack.push(&mut frame);
            return Ok(FrameResult::Done);
        }
    }

    /// Handle Sequence Combining state using table-driven approach
    pub(crate) fn handle_sequence_table_driven_combining(
        &mut self,
        mut frame: crate::parser::ParseFrame,
        stack: &mut crate::parser::iterative::ParseFrameStack,
    ) -> Result<crate::parser::iterative::FrameResult, ParseError> {
        use crate::parser::iterative::FrameResult;
        use crate::parser::{FrameContext, FrameState};

        let ctx = self.grammar_ctx.expect("GrammarContext required");
        let _stack = stack; // Suppress unused warning

        let FrameContext::SequenceTableDriven {
            grammar_id,
            matched_idx,
            ..
        } = &frame.context
        else {
            return Err(ParseError::new(
                "Expected SequenceTableDriven context in combining".to_string(),
            ));
        };

        let inst = ctx.inst(*grammar_id);

        log::debug!(
            "Sequence[table] Combining: frame_id={}, accumulated={}",
            frame.frame_id,
            frame.accumulated.len()
        );

        // Commit collection checkpoint on success
        if !frame.accumulated.is_empty() {
            self.commit_collection_checkpoint(frame.frame_id);
        } else {
            self.rollback_collection_checkpoint(frame.frame_id);
        }

        // Build final result
        let (result_node, final_pos) = if frame.accumulated.is_empty() {
            // No children matched
            if inst.flags.optional() {
                (Node::Empty, frame.pos)
            } else {
                // TODO: Apply parse_mode
                (Node::Empty, frame.pos)
            }
        } else {
            // Children matched
            (
                Node::Sequence {
                    children: frame.accumulated.clone(),
                },
                *matched_idx,
            )
        };

        self.pos = final_pos;
        frame.end_pos = Some(final_pos);
        frame.state = FrameState::Complete(result_node);

        Ok(FrameResult::Push(frame))
    }

    // ========================================================================
    // Table-Driven Ref Handlers
    // ========================================================================

    /// Handle Ref Initial state using table-driven approach
    pub(crate) fn handle_ref_table_driven_initial(
        &mut self,
        grammar_id: GrammarId,
        mut frame: crate::parser::ParseFrame,
        parent_terminators: &[GrammarId],
        stack: &mut crate::parser::iterative::ParseFrameStack,
    ) -> Result<crate::parser::iterative::FrameResult, ParseError> {
        use crate::parser::iterative::FrameResult;
        use crate::parser::{FrameContext, FrameState};

        self.pos = frame.pos;
        let ctx = self.grammar_ctx.expect("GrammarContext required");

        let inst = ctx.inst(grammar_id);
        let start_pos = frame.pos;
        let tables = ctx.tables();

        // Get rule name from strings table (stored in first_child_idx for Ref)
        let rule_name = if inst.first_child_idx > 0 {
            let name_idx = inst.first_child_idx as usize;
            if name_idx < tables.strings.len() {
                tables.strings[name_idx].to_string()
            } else {
                "UnknownRule".to_string()
            }
        } else {
            "UnknownRule".to_string()
        };

        log::debug!(
            "Ref[table] Initial: frame_id={}, pos={}, grammar_id={}, rule={}",
            frame.frame_id,
            start_pos,
            grammar_id.0,
            rule_name
        );

        // TODO: Handle exclude, allow_gaps, optional
        // TODO: Calculate max_idx with terminators

        // For now, look up the child grammar and parse it
        // In the full implementation, this would lookup from dialect
        // For now, just create a placeholder child

        let saved_pos = start_pos;
        let leading_transparent = Vec::new(); // TODO: collect if allow_gaps

        // Store context
        frame.context = FrameContext::RefTableDriven {
            grammar_id,
            segment_type: Some(rule_name.clone()),
            saved_pos,
            last_child_frame_id: Some(stack.frame_id_counter),
            leading_transparent,
        };

        frame.state = FrameState::WaitingForChild {
            child_index: 0,
            total_children: 1,
        };

        // Create child frame - get the first child (should be the referenced grammar)
        let children: Vec<GrammarId> = ctx.children(grammar_id).collect();
        if children.is_empty() {
            // No child grammar - return Empty
            log::debug!("Ref[table]: No child grammar, returning Empty");
            stack
                .results
                .insert(frame.frame_id, (Node::Empty, start_pos, None));
            return Ok(FrameResult::Done);
        }

        let child_grammar_id = children[0];
        let child_frame = crate::parser::ParseFrame::new_table_driven_child(
            stack.frame_id_counter,
            child_grammar_id,
            start_pos,
            parent_terminators.to_vec(),
            frame.parent_max_idx,
        );

        log::debug!(
            "Ref[table]: Parsing child grammar_id={}",
            child_grammar_id.0
        );

        stack.increment_frame_id_counter();
        stack.push(&mut frame);
        stack.push(&mut child_frame.clone());

        Ok(FrameResult::Done)
    }

    /// Handle Ref WaitingForChild state using table-driven approach
    pub(crate) fn handle_ref_table_driven_waiting_for_child(
        &mut self,
        mut frame: crate::parser::ParseFrame,
        child_node: &Node,
        child_end_pos: &usize,
        stack: &mut crate::parser::iterative::ParseFrameStack,
    ) -> Result<crate::parser::iterative::FrameResult, ParseError> {
        use crate::parser::iterative::FrameResult;
        use crate::parser::{FrameContext, FrameState};

        let _ctx = self.grammar_ctx.expect("GrammarContext required");

        let FrameContext::RefTableDriven {
            segment_type: _, ..
        } = &frame.context
        else {
            unreachable!("Expected RefTableDriven context");
        };

        log::debug!(
            "Ref[table] WaitingForChild: frame_id={}, child_empty={}, child_end_pos={}",
            frame.frame_id,
            child_node.is_empty(),
            child_end_pos
        );

        // Store child result and transition to Combining
        if !child_node.is_empty() {
            frame.accumulated.push(child_node.clone());
            self.pos = *child_end_pos;
            frame.end_pos = Some(*child_end_pos);
        } else {
            frame.end_pos = Some(frame.pos);
        }

        frame.state = FrameState::Combining;
        stack.push(&mut frame);
        Ok(FrameResult::Done)
    }

    /// Handle Ref Combining state using table-driven approach
    pub(crate) fn handle_ref_table_driven_combining(
        &mut self,
        mut frame: crate::parser::ParseFrame,
        stack: &mut crate::parser::iterative::ParseFrameStack,
    ) -> Result<crate::parser::iterative::FrameResult, ParseError> {
        use crate::parser::iterative::FrameResult;
        use crate::parser::{FrameContext, FrameState};

        let ctx = self.grammar_ctx.expect("GrammarContext required");
        let _stack = stack; // Suppress unused

        let FrameContext::RefTableDriven {
            grammar_id,
            segment_type,
            leading_transparent,
            ..
        } = &frame.context
        else {
            return Err(ParseError::new(
                "Expected RefTableDriven context in combining".to_string(),
            ));
        };

        let inst = ctx.inst(*grammar_id);

        log::debug!(
            "Ref[table] Combining: frame_id={}, accumulated={}",
            frame.frame_id,
            frame.accumulated.len()
        );

        // Build final result
        let final_pos = frame.end_pos.unwrap_or(frame.pos);
        let result_node = if frame.accumulated.is_empty() {
            // Child didn't match
            if inst.flags.optional() {
                Node::Empty
            } else {
                Node::Empty // TODO: Apply parse_mode
            }
        } else {
            // Wrap child in Ref node with segment type
            let mut children = leading_transparent.clone();
            children.extend(frame.accumulated.clone());

            Node::Ref {
                name: segment_type
                    .clone()
                    .unwrap_or_else(|| "UnknownRef".to_string()),
                segment_type: segment_type.clone(),
                child: Box::new(if children.len() == 1 {
                    children[0].clone()
                } else {
                    Node::Sequence { children }
                }),
            }
        };

        self.pos = final_pos;
        frame.end_pos = Some(final_pos);
        frame.state = FrameState::Complete(result_node);

        Ok(FrameResult::Push(frame))
    }

    // ========================================================================
    // Table-Driven Anything Handler
    // ========================================================================

    /// Handle Anything using table-driven approach
    /// Consumes all tokens until terminator or EOF, preserving bracket structure
    fn handle_anything_table_driven(
        &mut self,
        _grammar_id: GrammarId,
        _ctx: &GrammarContext,
        parent_terminators: &[GrammarId],
    ) -> Result<Node, ParseError> {
        let start_pos = self.pos;
        let mut anything_tokens = vec![];

        log::debug!(
            "Anything[table]: pos={}, parent_terminators={}",
            start_pos,
            parent_terminators.len()
        );

        // TODO: Check terminators properly (need to convert GrammarId to Arc<Grammar> for is_terminated)
        // For now, just consume until EOF

        loop {
            if self.is_at_end() {
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

        Ok(Node::DelimitedList {
            children: anything_tokens,
        })
    }

    // ========================================================================
    // Table-Driven Delimited Handlers
    // ========================================================================

    /// Handle Delimited Initial state using table-driven approach
    pub(crate) fn handle_delimited_table_driven_initial(
        &mut self,
        grammar_id: GrammarId,
        mut frame: crate::parser::ParseFrame,
        parent_terminators: &[GrammarId],
        stack: &mut crate::parser::iterative::ParseFrameStack,
    ) -> Result<crate::parser::iterative::FrameResult, ParseError> {
        use crate::parser::iterative::FrameResult;
        use crate::parser::{DelimitedState, FrameContext, FrameState};

        self.pos = frame.pos;
        let ctx = self.grammar_ctx.expect("GrammarContext required");

        let inst = ctx.inst(grammar_id);
        let start_pos = frame.pos;

        log::debug!(
            "Delimited[table] Initial: frame_id={}, pos={}, grammar_id={}, children={}",
            frame.frame_id,
            start_pos,
            grammar_id.0,
            inst.child_count
        );

        // Get children: elements + delimiter
        let all_children: Vec<GrammarId> = ctx.children(grammar_id).collect();
        if all_children.len() < 2 {
            log::debug!("Delimited[table]: Not enough children (need elements + delimiter)");
            stack
                .results
                .insert(frame.frame_id, (Node::Empty, start_pos, None));
            return Ok(FrameResult::Done);
        }

        // Last child is delimiter, others are elements
        let delimiter_id = *all_children.last().unwrap();
        let element_ids: Vec<GrammarId> = all_children[..all_children.len() - 1].to_vec();

        // TODO: Calculate max_idx, handle min_delimiters, allow_trailing, etc.
        let max_idx = self.tokens.len();

        // Store context
        frame.context = FrameContext::DelimitedTableDriven {
            grammar_id,
            delimiter_count: 0,
            matched_idx: start_pos,
            working_idx: start_pos,
            max_idx,
            state: DelimitedState::MatchingElement,
            last_child_frame_id: Some(stack.frame_id_counter),
            delimiter_match: None,
            pos_before_delimiter: None,
        };

        frame.state = FrameState::WaitingForChild {
            child_index: 0,
            total_children: element_ids.len(),
        };

        // Create OneOf child with all element options
        // For simplicity, try first element for now
        // TODO: Create proper OneOf with all elements
        let first_element = element_ids[0];
        let child_frame = crate::parser::ParseFrame::new_table_driven_child(
            stack.frame_id_counter,
            first_element,
            start_pos,
            parent_terminators.to_vec(),
            Some(max_idx),
        );

        log::debug!(
            "Delimited[table]: Trying first element grammar_id={}",
            first_element.0
        );

        stack.increment_frame_id_counter();
        stack.push(&mut frame);
        stack.push(&mut child_frame.clone());

        Ok(FrameResult::Done)
    }

    /// Handle Delimited WaitingForChild state using table-driven approach
    pub(crate) fn handle_delimited_table_driven_waiting_for_child(
        &mut self,
        mut frame: crate::parser::ParseFrame,
        child_node: &Node,
        child_end_pos: &usize,
        stack: &mut crate::parser::iterative::ParseFrameStack,
    ) -> Result<crate::parser::iterative::FrameResult, ParseError> {
        use crate::parser::iterative::FrameResult;
        use crate::parser::{DelimitedState, FrameContext, FrameState};

        let ctx = self.grammar_ctx.expect("GrammarContext required");

        let FrameContext::DelimitedTableDriven {
            grammar_id,
            delimiter_count,
            matched_idx,
            working_idx,
            max_idx: _,
            state: delim_state,
            ..
        } = &mut frame.context
        else {
            unreachable!("Expected DelimitedTableDriven context");
        };

        let all_children: Vec<GrammarId> = ctx.children(*grammar_id).collect();
        let delimiter_id = *all_children.last().unwrap();

        log::debug!(
            "Delimited[table] WaitingForChild: frame_id={}, child_empty={}, state={:?}, delim_count={}",
            frame.frame_id,
            child_node.is_empty(),
            delim_state,
            delimiter_count
        );

        match delim_state {
            DelimitedState::MatchingElement => {
                if !child_node.is_empty() {
                    // Element matched
                    frame.accumulated.push(child_node.clone());
                    *matched_idx = *child_end_pos;
                    *working_idx = *child_end_pos;

                    // Try to match delimiter next
                    *delim_state = DelimitedState::MatchingDelimiter;
                    self.pos = *working_idx;

                    let delimiter_frame = crate::parser::ParseFrame::new_table_driven_child(
                        stack.frame_id_counter,
                        delimiter_id,
                        *working_idx,
                        frame.table_terminators.clone(),
                        frame.parent_max_idx,
                    );

                    frame.state = FrameState::WaitingForChild {
                        child_index: 0,
                        total_children: 1,
                    };

                    stack.increment_frame_id_counter();
                    stack.push(&mut frame);
                    stack.push(&mut delimiter_frame.clone());
                    return Ok(FrameResult::Done);
                } else {
                    // Element failed - finalize
                    log::debug!("Delimited[table]: Element failed, finalizing");
                    frame.end_pos = Some(*matched_idx);
                    frame.state = FrameState::Combining;
                    stack.push(&mut frame);
                    return Ok(FrameResult::Done);
                }
            }
            DelimitedState::MatchingDelimiter => {
                if !child_node.is_empty() {
                    // Delimiter matched
                    frame.accumulated.push(child_node.clone());
                    *delimiter_count += 1;
                    *matched_idx = *child_end_pos;
                    *working_idx = *child_end_pos;

                    // Try to match next element
                    *delim_state = DelimitedState::MatchingElement;
                    self.pos = *working_idx;

                    // For simplicity, use first element again
                    // TODO: Create proper OneOf
                    let first_element = all_children[0];
                    let element_frame = crate::parser::ParseFrame::new_table_driven_child(
                        stack.frame_id_counter,
                        first_element,
                        *working_idx,
                        frame.table_terminators.clone(),
                        frame.parent_max_idx,
                    );

                    frame.state = FrameState::WaitingForChild {
                        child_index: 0,
                        total_children: 1,
                    };

                    stack.increment_frame_id_counter();
                    stack.push(&mut frame);
                    stack.push(&mut element_frame.clone());
                    return Ok(FrameResult::Done);
                } else {
                    // Delimiter failed - finalize (successful if we have min_delimiters)
                    log::debug!("Delimited[table]: Delimiter failed, finalizing");
                    frame.end_pos = Some(*matched_idx);
                    frame.state = FrameState::Combining;
                    stack.push(&mut frame);
                    return Ok(FrameResult::Done);
                }
            }
        }
    }

    /// Handle Delimited Combining state using table-driven approach
    pub(crate) fn handle_delimited_table_driven_combining(
        &mut self,
        mut frame: crate::parser::ParseFrame,
        stack: &mut crate::parser::iterative::ParseFrameStack,
    ) -> Result<crate::parser::iterative::FrameResult, ParseError> {
        use crate::parser::iterative::FrameResult;
        use crate::parser::{FrameContext, FrameState};

        let ctx = self.grammar_ctx.expect("GrammarContext required");
        let _stack = stack; // Suppress unused

        let FrameContext::DelimitedTableDriven {
            grammar_id,
            delimiter_count,
            matched_idx,
            ..
        } = &frame.context
        else {
            return Err(ParseError::new(
                "Expected DelimitedTableDriven context in combining".to_string(),
            ));
        };

        let inst = ctx.inst(*grammar_id);

        log::debug!(
            "Delimited[table] Combining: frame_id={}, accumulated={}, delim_count={}",
            frame.frame_id,
            frame.accumulated.len(),
            delimiter_count
        );

        // Build final result
        let (result_node, final_pos) = if frame.accumulated.is_empty() {
            // No matches
            if inst.flags.optional() {
                (Node::Empty, frame.pos)
            } else {
                // TODO: Check min_delimiters
                (Node::Empty, frame.pos)
            }
        } else {
            // Matches found
            (
                Node::DelimitedList {
                    children: frame.accumulated.clone(),
                },
                *matched_idx,
            )
        };

        self.pos = final_pos;
        frame.end_pos = Some(final_pos);
        frame.state = FrameState::Complete(result_node);

        Ok(FrameResult::Push(frame))
    }

    // ========================================================================
    // Table-Driven Bracketed Handlers
    // ========================================================================

    /// Handle Bracketed Initial state using table-driven approach
    pub(crate) fn handle_bracketed_table_driven_initial(
        &mut self,
        grammar_id: GrammarId,
        mut frame: crate::parser::ParseFrame,
        parent_terminators: &[GrammarId],
        stack: &mut crate::parser::iterative::ParseFrameStack,
    ) -> Result<crate::parser::iterative::FrameResult, ParseError> {
        use crate::parser::iterative::FrameResult;
        use crate::parser::{BracketedState, FrameContext, FrameState};

        self.pos = frame.pos;
        let ctx = self.grammar_ctx.expect("GrammarContext required");

        let inst = ctx.inst(grammar_id);
        let start_pos = frame.pos;

        log::debug!(
            "Bracketed[table] Initial: frame_id={}, pos={}, grammar_id={}, children={}",
            frame.frame_id,
            start_pos,
            grammar_id.0,
            inst.child_count
        );

        // Get children: bracket_pairs (open, close) + elements
        let all_children: Vec<GrammarId> = ctx.children(grammar_id).collect();
        if all_children.len() < 2 {
            log::debug!("Bracketed[table]: Not enough children (need bracket_pairs + elements)");
            stack
                .results
                .insert(frame.frame_id, (Node::Empty, start_pos, None));
            return Ok(FrameResult::Done);
        }

        // First two children are opening and closing brackets
        let open_bracket_id = all_children[0];
        let _close_bracket_id = all_children[1];

        // Store context for bracket matching
        frame.context = FrameContext::BracketedTableDriven {
            grammar_id,
            state: BracketedState::MatchingOpen,
            last_child_frame_id: Some(stack.frame_id_counter),
            bracket_max_idx: None, // Will be calculated after opening bracket matched
        };

        frame.state = FrameState::WaitingForChild {
            child_index: 0,
            total_children: 1,
        };

        // Create child frame to match opening bracket
        let open_frame = crate::parser::ParseFrame::new_table_driven_child(
            stack.frame_id_counter,
            open_bracket_id,
            start_pos,
            parent_terminators.to_vec(),
            frame.parent_max_idx,
        );

        log::debug!(
            "Bracketed[table]: Trying opening bracket grammar_id={}",
            open_bracket_id.0
        );

        stack.increment_frame_id_counter();
        stack.push(&mut frame);
        stack.push(&mut open_frame.clone());

        Ok(FrameResult::Done)
    }

    /// Handle Bracketed WaitingForChild state using table-driven approach
    pub(crate) fn handle_bracketed_table_driven_waiting_for_child(
        &mut self,
        mut frame: crate::parser::ParseFrame,
        child_node: &Node,
        child_end_pos: &usize,
        stack: &mut crate::parser::iterative::ParseFrameStack,
    ) -> Result<crate::parser::iterative::FrameResult, ParseError> {
        use crate::parser::iterative::FrameResult;
        use crate::parser::{BracketedState, FrameContext, FrameState};

        let ctx = self.grammar_ctx.expect("GrammarContext required");

        let FrameContext::BracketedTableDriven {
            grammar_id,
            state: bracket_state,
            bracket_max_idx,
            ..
        } = &mut frame.context
        else {
            unreachable!("Expected BracketedTableDriven context");
        };

        let all_children: Vec<GrammarId> = ctx.children(*grammar_id).collect();
        let _open_bracket_id = all_children[0];
        let close_bracket_id = all_children[1];
        let element_ids: Vec<GrammarId> = all_children[2..].to_vec();

        log::debug!(
            "Bracketed[table] WaitingForChild: frame_id={}, child_empty={}, state={:?}",
            frame.frame_id,
            child_node.is_empty(),
            bracket_state
        );

        match bracket_state {
            BracketedState::MatchingOpen => {
                if child_node.is_empty() {
                    // Opening bracket failed - return empty (optional handling)
                    log::debug!("Bracketed[table]: Opening bracket failed");
                    frame.end_pos = Some(frame.pos);
                    frame.state = FrameState::Combining;
                    stack.push(&mut frame);
                    return Ok(FrameResult::Done);
                } else {
                    // Opening bracket matched
                    frame.accumulated.push(child_node.clone());

                    // Calculate bracket_max_idx if we can find matching closing bracket
                    if let Some(open_idx) = child_node.get_token_idx() {
                        *bracket_max_idx = self.get_matching_bracket_idx(open_idx);
                        log::debug!(
                            "Bracketed[table]: Opening bracket at idx={}, closing at idx={:?}",
                            open_idx,
                            bracket_max_idx
                        );
                    }

                    // Move to MatchingContent state
                    *bracket_state = BracketedState::MatchingContent;
                    self.pos = *child_end_pos;

                    // Create Sequence-like child to match content (all elements)
                    // For simplicity, try first element
                    // TODO: Create proper Sequence with all elements
                    let content_grammar_id = if !element_ids.is_empty() {
                        element_ids[0]
                    } else {
                        // No elements - skip to closing bracket
                        *bracket_state = BracketedState::MatchingClose;
                        let close_frame = crate::parser::ParseFrame::new_table_driven_child(
                            stack.frame_id_counter,
                            close_bracket_id,
                            self.pos,
                            frame.table_terminators.clone(),
                            *bracket_max_idx,
                        );

                        frame.state = FrameState::WaitingForChild {
                            child_index: 0,
                            total_children: 1,
                        };

                        stack.increment_frame_id_counter();
                        stack.push(&mut frame);
                        stack.push(&mut close_frame.clone());
                        return Ok(FrameResult::Done);
                    };

                    let content_frame = crate::parser::ParseFrame::new_table_driven_child(
                        stack.frame_id_counter,
                        content_grammar_id,
                        self.pos,
                        vec![close_bracket_id], // Close bracket terminates content
                        *bracket_max_idx,
                    );

                    frame.state = FrameState::WaitingForChild {
                        child_index: 0,
                        total_children: 1,
                    };

                    stack.increment_frame_id_counter();
                    stack.push(&mut frame);
                    stack.push(&mut content_frame.clone());
                    return Ok(FrameResult::Done);
                }
            }
            BracketedState::MatchingContent => {
                // Content matched (or empty) - now match closing bracket
                if !child_node.is_empty() {
                    // Flatten Sequence/DelimitedList children
                    let mut to_process = vec![child_node.clone()];
                    while let Some(node) = to_process.pop() {
                        match node {
                            Node::Sequence { children } | Node::DelimitedList { children } => {
                                to_process.extend(children.into_iter().rev());
                            }
                            _ => {
                                frame.accumulated.push(node);
                            }
                        }
                    }
                }

                *bracket_state = BracketedState::MatchingClose;
                self.pos = *child_end_pos;

                // Create child frame to match closing bracket
                let close_frame = crate::parser::ParseFrame::new_table_driven_child(
                    stack.frame_id_counter,
                    close_bracket_id,
                    self.pos,
                    frame.table_terminators.clone(),
                    *bracket_max_idx,
                );

                frame.state = FrameState::WaitingForChild {
                    child_index: 0,
                    total_children: 1,
                };

                stack.increment_frame_id_counter();
                stack.push(&mut frame);
                stack.push(&mut close_frame.clone());
                return Ok(FrameResult::Done);
            }
            BracketedState::MatchingClose => {
                if child_node.is_empty() {
                    // Closing bracket failed - return empty
                    log::debug!("Bracketed[table]: Closing bracket failed");
                    frame.end_pos = Some(frame.pos);
                    frame.state = FrameState::Combining;
                    stack.push(&mut frame);
                    return Ok(FrameResult::Done);
                } else {
                    // Closing bracket matched - success!
                    frame.accumulated.push(child_node.clone());
                    *bracket_state = BracketedState::Complete;
                    frame.end_pos = Some(*child_end_pos);
                    frame.state = FrameState::Combining;
                    stack.push(&mut frame);
                    return Ok(FrameResult::Done);
                }
            }
            BracketedState::Complete => {
                unreachable!("Should not receive child in Complete state");
            }
        }
    }

    /// Handle Bracketed Combining state using table-driven approach
    pub(crate) fn handle_bracketed_table_driven_combining(
        &mut self,
        mut frame: crate::parser::ParseFrame,
        stack: &mut crate::parser::iterative::ParseFrameStack,
    ) -> Result<crate::parser::iterative::FrameResult, ParseError> {
        use crate::parser::iterative::FrameResult;
        use crate::parser::{FrameContext, FrameState};

        let ctx = self.grammar_ctx.expect("GrammarContext required");
        let _stack = stack; // Suppress unused

        let FrameContext::BracketedTableDriven {
            grammar_id,
            state: bracket_state,
            ..
        } = &frame.context
        else {
            return Err(ParseError::new(
                "Expected BracketedTableDriven context in combining".to_string(),
            ));
        };

        let inst = ctx.inst(*grammar_id);

        log::debug!(
            "Bracketed[table] Combining: frame_id={}, accumulated={}, state={:?}",
            frame.frame_id,
            frame.accumulated.len(),
            bracket_state
        );

        // Build final result
        let (result_node, final_pos) = match bracket_state {
            crate::parser::BracketedState::Complete => {
                // Successfully matched all three parts
                (
                    Node::Bracketed {
                        children: frame.accumulated.clone(),
                        bracket_persists: true, // TODO: Get from grammar config
                    },
                    frame.end_pos.unwrap_or(frame.pos),
                )
            }
            _ => {
                // Failed to match - return empty (with optional handling)
                if inst.flags.optional() {
                    (Node::Empty, frame.pos)
                } else {
                    (Node::Empty, frame.pos)
                }
            }
        };

        self.pos = final_pos;
        frame.end_pos = Some(final_pos);
        frame.state = FrameState::Complete(result_node);

        Ok(FrameResult::Push(frame))
    }

    // ========================================================================
    // Table-Driven AnyNumberOf Handlers
    // ========================================================================

    /// Handle AnyNumberOf Initial state using table-driven approach
    pub(crate) fn handle_anynumberof_table_driven_initial(
        &mut self,
        grammar_id: GrammarId,
        mut frame: crate::parser::ParseFrame,
        parent_terminators: &[GrammarId],
        stack: &mut crate::parser::iterative::ParseFrameStack,
    ) -> Result<crate::parser::iterative::FrameResult, ParseError> {
        use crate::parser::iterative::FrameResult;
        use crate::parser::{FrameContext, FrameState};

        self.pos = frame.pos;
        let ctx = self.grammar_ctx.expect("GrammarContext required");

        let inst = ctx.inst(grammar_id);
        let start_pos = frame.pos;

        log::debug!(
            "AnyNumberOf[table] Initial: frame_id={}, pos={}, grammar_id={}, children={}",
            frame.frame_id,
            start_pos,
            grammar_id.0,
            inst.child_count
        );

        // Get all element children
        let element_ids: Vec<GrammarId> = ctx.children(grammar_id).collect();
        if element_ids.is_empty() {
            log::debug!("AnyNumberOf[table]: No elements to match");
            stack
                .results
                .insert(frame.frame_id, (Node::Empty, start_pos, None));
            return Ok(FrameResult::Done);
        }

        // Initialize option counter for max_times_per_element tracking
        let option_counter: hashbrown::HashMap<u64, usize> =
            element_ids.iter().map(|id| (id.0 as u64, 0)).collect();

        // TODO: Calculate max_idx with terminators
        let max_idx = self.tokens.len();

        // Store context
        frame.context = FrameContext::AnyNumberOfTableDriven {
            grammar_id,
            count: 0,
            matched_idx: start_pos,
            working_idx: start_pos,
            option_counter,
            max_idx,
            last_child_frame_id: Some(stack.frame_id_counter),
        };

        frame.state = FrameState::WaitingForChild {
            child_index: 0,
            total_children: element_ids.len(),
        };

        // Create OneOf child with all elements (optional=true for loop behavior)
        // For simplicity, try first element
        // TODO: Create proper OneOf with all elements
        let first_element = element_ids[0];
        let child_frame = crate::parser::ParseFrame::new_table_driven_child(
            stack.frame_id_counter,
            first_element,
            start_pos,
            parent_terminators.to_vec(),
            Some(max_idx),
        );

        log::debug!(
            "AnyNumberOf[table]: Trying first element grammar_id={}",
            first_element.0
        );

        stack.increment_frame_id_counter();
        stack.push(&mut frame);
        stack.push(&mut child_frame.clone());

        Ok(FrameResult::Done)
    }

    /// Handle AnyNumberOf WaitingForChild state using table-driven approach
    pub(crate) fn handle_anynumberof_table_driven_waiting_for_child(
        &mut self,
        mut frame: crate::parser::ParseFrame,
        child_node: &Node,
        child_end_pos: &usize,
        stack: &mut crate::parser::iterative::ParseFrameStack,
    ) -> Result<crate::parser::iterative::FrameResult, ParseError> {
        use crate::parser::iterative::FrameResult;
        use crate::parser::{FrameContext, FrameState};

        let ctx = self.grammar_ctx.expect("GrammarContext required");

        let FrameContext::AnyNumberOfTableDriven {
            grammar_id,
            count,
            matched_idx,
            working_idx,
            option_counter,
            max_idx,
            ..
        } = &mut frame.context
        else {
            unreachable!("Expected AnyNumberOfTableDriven context");
        };

        let inst = ctx.inst(*grammar_id);
        let element_ids: Vec<GrammarId> = ctx.children(*grammar_id).collect();
        let first_element = element_ids[0];

        log::debug!(
            "AnyNumberOf[table] WaitingForChild: frame_id={}, child_empty={}, count={}, matched_idx={}",
            frame.frame_id,
            child_node.is_empty(),
            count,
            matched_idx
        );

        if !child_node.is_empty() {
            // Check for zero-width match to prevent infinite loops
            if *child_end_pos == *working_idx {
                log::warn!(
                    "AnyNumberOf[table]: zero-width match at {}, stopping to prevent infinite loop",
                    working_idx
                );
                frame.end_pos = Some(*matched_idx);
                frame.state = FrameState::Combining;
                stack.push(&mut frame);
                return Ok(FrameResult::Done);
            }

            // Match succeeded - accumulate and increment count
            frame.accumulated.push(child_node.clone());
            *matched_idx = *child_end_pos;
            *working_idx = *matched_idx;
            *count += 1;

            // Update option counter for max_times_per_element
            let element_key = first_element.0 as u64;
            *option_counter.entry(element_key).or_insert(0) += 1;

            log::debug!(
                "AnyNumberOf[table]: Match #{}, element_key={}, matched_idx={}",
                count,
                element_key,
                matched_idx
            );

            // Check if we've reached max_idx
            if *matched_idx >= *max_idx {
                log::debug!(
                    "AnyNumberOf[table]: Reached max_idx={}, finalizing",
                    max_idx
                );
                frame.end_pos = Some(*matched_idx);
                frame.state = FrameState::Combining;
                stack.push(&mut frame);
                return Ok(FrameResult::Done);
            }

            // TODO: Check max_times constraint (stored in auxiliary table)
            // For now, assume unlimited

            // Continue matching - push another child frame
            self.pos = *working_idx;
            let next_child_frame = crate::parser::ParseFrame::new_table_driven_child(
                stack.frame_id_counter,
                first_element,
                *working_idx,
                frame.table_terminators.clone(),
                Some(*max_idx),
            );

            frame.state = FrameState::WaitingForChild {
                child_index: 0,
                total_children: 1,
            };

            stack.increment_frame_id_counter();
            stack.push(&mut frame);
            stack.push(&mut next_child_frame.clone());
            return Ok(FrameResult::Done);
        } else {
            // Child failed - check if we met min_times
            log::debug!(
                "AnyNumberOf[table]: Child failed, count={}, min_times={}",
                count,
                inst.min_times
            );

            if *count >= inst.min_times as usize {
                // Success - we have enough matches
                frame.end_pos = Some(*matched_idx);
                frame.state = FrameState::Combining;
                stack.push(&mut frame);
                return Ok(FrameResult::Done);
            } else {
                // Failure - didn't meet min_times
                frame.end_pos = Some(frame.pos);
                frame.state = FrameState::Combining;
                stack.push(&mut frame);
                return Ok(FrameResult::Done);
            }
        }
    }

    /// Handle AnyNumberOf Combining state using table-driven approach
    pub(crate) fn handle_anynumberof_table_driven_combining(
        &mut self,
        mut frame: crate::parser::ParseFrame,
        stack: &mut crate::parser::iterative::ParseFrameStack,
    ) -> Result<crate::parser::iterative::FrameResult, ParseError> {
        use crate::parser::iterative::FrameResult;
        use crate::parser::{FrameContext, FrameState};

        let ctx = self.grammar_ctx.expect("GrammarContext required");
        let _stack = stack; // Suppress unused

        let FrameContext::AnyNumberOfTableDriven {
            grammar_id,
            count,
            matched_idx,
            ..
        } = &frame.context
        else {
            return Err(ParseError::new(
                "Expected AnyNumberOfTableDriven context in combining".to_string(),
            ));
        };

        let inst = ctx.inst(*grammar_id);

        log::debug!(
            "AnyNumberOf[table] Combining: frame_id={}, accumulated={}, count={}",
            frame.frame_id,
            frame.accumulated.len(),
            count
        );

        // Build final result
        let (result_node, final_pos) = if *count >= inst.min_times as usize {
            // Success - return sequence of matches
            if frame.accumulated.is_empty() {
                (Node::Empty, frame.pos)
            } else {
                (
                    Node::Sequence {
                        children: frame.accumulated.clone(),
                    },
                    *matched_idx,
                )
            }
        } else {
            // Failure - didn't meet min_times
            if inst.flags.optional() {
                (Node::Empty, frame.pos)
            } else {
                (Node::Empty, frame.pos)
            }
        };

        self.pos = final_pos;
        frame.end_pos = Some(final_pos);
        frame.state = FrameState::Complete(result_node);

        Ok(FrameResult::Push(frame))
    }
}
