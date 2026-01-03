//! Core Parser struct and implementation
//!
//! This module contains the Parser struct definition and its core methods
//! including the main entry point for parsing with grammar.

use crate::vdebug;
use hashbrown::HashSet;

use crate::parser::table_driven::frame::{TableFrameResult, TableParseFrame};
use crate::parser::FrameState;
use crate::parser::{MatchResult, MetaSegmentType};

use super::{cache::TableParseCache, Node, ParseError};
use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_types::regex::RegexMode;
use sqlfluffrs_types::token::CaseFold;
use sqlfluffrs_types::{SimpleHint, Token};
// NEW: Table-driven grammar support
use sqlfluffrs_types::{GrammarContext, GrammarId, GrammarVariant, RootGrammar};

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
    pub simple_hint_cache: hashbrown::HashMap<u64, Option<SimpleHint>>,
    pub tokens: &'a [Token],
    pub pos: usize, // current position in tokens
    pub dialect: Dialect,
    pub table_cache: TableParseCache, // NEW: Table-driven parser cache
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
    // Table-driven grammar support
    pub grammar_ctx: GrammarContext<'static>,
    /// Indentation configuration (key -> enabled)
    /// Used by conditional meta segments (e.g., indented_joins=true enables Indent/Dedent)
    pub indent_config: hashbrown::HashMap<&'static str, bool>,
    /// Optional owned RootGrammar. When present, callers can use `parse_root`
    /// to parse starting from this root without having to pass grammar ids
    /// or contexts manually.
    pub root: Option<RootGrammar>,
    // Regex cache for table-driven RegexParser (pattern_string -> compiled RegexMode)
    regex_cache: std::cell::RefCell<hashbrown::HashMap<String, RegexMode>>,
}

impl<'a> Parser<'a> {
    /// Create a new Parser instance with table-driven grammar support
    pub fn new(
        tokens: &'a [Token],
        dialect: Dialect,
        indent_config: hashbrown::HashMap<&'static str, bool>,
    ) -> Parser<'a> {
        let root = dialect.get_root_grammar();
        let grammar_ctx = GrammarContext::new(root.tables);
        Parser {
            tokens,
            pos: 0,
            dialect,
            table_cache: TableParseCache::new(),
            collected_transparent_positions: HashSet::new(),
            collection_stack: Vec::new(),
            pruning_calls: std::cell::Cell::new(0),
            pruning_total: std::cell::Cell::new(0),
            pruning_kept: std::cell::Cell::new(0),
            pruning_hinted: std::cell::Cell::new(0),
            pruning_complex: std::cell::Cell::new(0),
            simple_hint_cache: hashbrown::HashMap::new(),
            cache_enabled: true,
            grammar_ctx,
            indent_config,
            root: None,
            regex_cache: std::cell::RefCell::new(hashbrown::HashMap::new()),
        }
    }

    /// Enable or disable the parse cache (for debugging)
    pub fn set_cache_enabled(&mut self, enabled: bool) {
        self.cache_enabled = enabled;
    }

    pub fn call_rule(
        &mut self,
        name: &str,
        parent_terminators: &[GrammarId],
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
        let node = self.parse_table_iterative(grammar, parent_terminators)?;

        // If the node is empty, return it as-is without wrapping
        // This prevents infinite loops when optional segments match nothing
        if node.is_empty() {
            return Ok(node);
        }

        // Use provided segment_type, or infer from Token nodes
        let final_segment_type = match &node {
            Node::Token {
                token_type: t,
                segment_type: _,
                raw: _,
                token_idx: _,
            } => Some(t.clone()),
            _ => None,
        };

        // Wrap in a Ref node for type clarity
        let result = Node::new_ref(name.to_string(), final_segment_type, node);

        // Deduplicate whitespace/newline nodes to handle cases where both
        // parent and child grammars collected the same tokens
        Ok(result.deduplicate())
    }

    pub fn call_rule_as_root(&mut self) -> Result<Node, ParseError> {
        // Obtain the root grammar for this dialect and dispatch based on its
        // variant (table-driven vs Arc-based). Clone to avoid holding borrows.
        let root_grammar = self.dialect.get_root_grammar().clone();

        // Find the last code token position (for trailing non-code tokens)
        let mut last_code_pos = self.tokens.len();
        for (i, token) in self.tokens.iter().enumerate().rev() {
            if token.is_code() {
                last_code_pos = i + 1;
                break;
            }
        }

        let token_slice_orig = self.tokens;
        let token_slice = &self.tokens[..last_code_pos];
        let end_nodes = self.end_children_nodes(last_code_pos);

        if token_slice.is_empty() {
            // Wrap in a Ref node for type clarity
            let result = Node::new_ref(
                "Root".to_string(),
                Some("file".to_string()),
                Node::Sequence {
                    children: end_nodes,
                },
            );
            return Ok(result.deduplicate());
        }

        self.tokens = token_slice;

        // Collect any leading transparent tokens (whitespace, newlines, COMMENTS)
        // before parsing starts. This ensures leading comments are included in the AST.
        let leading_transparent = self.collect_transparent_nodes(true);

        // Parse using the root grammar.
        let grammar_id = root_grammar.grammar_id;
        let tables = root_grammar.tables;
        // Update grammar context if needed
        self.grammar_ctx = GrammarContext::new(tables);
        let nodes = self.parse_table_iterative(grammar_id, &[]);
        self.tokens = token_slice_orig;
        match nodes {
            Ok(mut n) => {
                // Prepend leading transparent tokens and append trailing tokens
                if !leading_transparent.is_empty() || !end_nodes.is_empty() {
                    let mut all_children = leading_transparent;
                    all_children.push(n);
                    all_children.extend(end_nodes);
                    let len = all_children.len();
                    n = Node::Sequence {
                        children: all_children,
                    };
                    self.pos += len - 1; // -1 because n is included
                } else if !end_nodes.is_empty() {
                    let mut children = vec![n];
                    let end_len = end_nodes.len();
                    children.extend(end_nodes);
                    n = Node::Sequence { children };
                    self.pos += end_len;
                }
                let result = Node::new_ref("Root".to_string(), Some("file".to_string()), n);
                Ok(result.deduplicate())
            }
            Err(e) => Err(e),
        }
    }

    /// Parse and return MatchResult instead of Node
    ///
    /// This allows Python to apply the match result using its own apply() logic,
    /// avoiding double-counting issues in Rust's apply() implementation.
    pub fn call_rule_as_root_match_result(&mut self) -> Result<MatchResult, ParseError> {
        use crate::parser::match_result::MatchResult;

        // Obtain the root grammar for this dialect
        let root_grammar = self.dialect.get_root_grammar().clone();

        // Find the last code token position (for trailing non-code tokens)
        let mut last_code_pos = self.tokens.len();
        for (i, token) in self.tokens.iter().enumerate().rev() {
            if token.is_code() {
                last_code_pos = i + 1;
                break;
            }
        }

        let token_slice_orig = self.tokens;
        let token_slice = &self.tokens[..last_code_pos];

        if token_slice.is_empty() {
            // Return empty match result
            return Ok(MatchResult::empty_at(0));
        }

        self.tokens = token_slice;

        // Parse using the root grammar
        let grammar_id = root_grammar.grammar_id;
        let tables = root_grammar.tables;
        self.grammar_ctx = GrammarContext::new(tables);
        let result = self.parse_table_iterative_match_result(grammar_id, &[]);
        self.tokens = token_slice_orig;

        result
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
                "comment" => Node::Comment {
                    raw: token.raw().to_string(),
                    token_idx: start_idx + i,
                },
                other => Node::new_token(other.to_string(), token.raw().to_string(), start_idx + i),
            };
            children.push(node);
        }
        children
    }

    /// Lookup SegmentDef by name
    pub fn get_segment_grammar(&self, name: &str) -> Option<GrammarId> {
        self.dialect
            .get_segment_grammar(name)
            .map(|root| root.grammar_id)
    }

    /// Push a checkpoint onto the collection stack when starting to process a grammar.
    /// This records the current state so we can backtrack if needed.
    pub fn push_collection_checkpoint(&mut self, frame_id: usize) {
        self.collection_stack.push(CollectionCheckpoint {
            frame_id,
            positions: Vec::new(),
        });
        vdebug!(
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
                vdebug!(
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
    /// If the frame_id doesn't match the checkpoint on top of the stack, it means
    /// this grammar type (e.g., OneOf, Delimited) doesn't use checkpoints - this is OK.
    pub fn commit_collection_checkpoint(&mut self, frame_id: usize) {
        if let Some(checkpoint) = self.collection_stack.last() {
            if checkpoint.frame_id == frame_id {
                // This frame owns the checkpoint - pop and commit it
                #[cfg(feature = "verbose-debug")]
                let checkpoint = self.collection_stack.pop().unwrap();
                #[cfg(not(feature = "verbose-debug"))]
                let _ = self.collection_stack.pop();
                vdebug!(
                    "Committed {} collected positions for frame_id={}, stack depth now={}",
                    checkpoint.positions.len(),
                    frame_id,
                    self.collection_stack.len()
                );
                // Positions remain in collected_transparent_positions - they're committed
            } else {
                // This frame doesn't own a checkpoint (e.g., OneOf, Delimited, Ref)
                // This is normal - only Sequence creates checkpoints
                log::trace!(
                    "No checkpoint to commit for frame_id={} (top checkpoint is {})",
                    frame_id,
                    checkpoint.frame_id
                );
            }
        } else {
            // No checkpoints exist - this is fine for non-Sequence grammars
            log::trace!(
                "No checkpoint to commit for frame_id={} (stack empty)",
                frame_id
            );
        }
    }

    /// Pop a checkpoint and rollback its collections (unmark them).
    /// This is called when a grammar fails or is abandoned during backtracking.
    /// If the frame_id doesn't match the checkpoint on top of the stack, it means
    /// this grammar type (e.g., OneOf, Delimited) doesn't use checkpoints - this is OK.
    pub fn rollback_collection_checkpoint(&mut self, frame_id: usize) {
        if let Some(checkpoint) = self.collection_stack.last() {
            if checkpoint.frame_id == frame_id {
                // This frame owns the checkpoint - pop and rollback it
                let checkpoint = self.collection_stack.pop().unwrap();
                vdebug!(
                    "Rolling back {} collected positions for frame_id={}, stack depth now={}",
                    checkpoint.positions.len(),
                    frame_id,
                    self.collection_stack.len()
                );
                // Remove all positions that were marked during this checkpoint
                for pos in checkpoint.positions {
                    self.collected_transparent_positions.remove(&pos);
                }
            } else {
                // This frame doesn't own a checkpoint (e.g., OneOf, Delimited, Ref)
                // This is normal - only Sequence creates checkpoints
                log::trace!(
                    "No checkpoint to rollback for frame_id={} (top checkpoint is {})",
                    frame_id,
                    checkpoint.frame_id
                );
            }
        } else {
            // No checkpoints exist - this is fine for non-Sequence grammars
            log::trace!(
                "No checkpoint to rollback for frame_id={} (stack empty)",
                frame_id
            );
        }
    }

    // ============================================================================
    // Table-Driven Handler Methods (Base Parsers)
    // ============================================================================

    /// Handle StringParser using table-driven approach
    pub(crate) fn handle_string_parser_table_driven(
        &mut self,
        grammar_id: GrammarId,
    ) -> Result<MatchResult, ParseError> {
        // Extract all data from tables first (before any self methods)
        let tables = self.grammar_ctx.tables();

        // StringParser stores: [template_id, token_type_id, raw_class_id] in aux_data
        // aux_data_offsets maps instruction -> aux_data start for variable-length aux
        let aux_start = tables.aux_data_offsets[grammar_id.get() as usize] as usize;
        let template_id = tables.aux_data[aux_start];
        let token_type_id = tables.aux_data[aux_start + 1];
        let raw_class_id = tables.aux_data[aux_start + 2];

        let template = tables.get_string(template_id).to_string();
        let token_type = tables.get_string(token_type_id).to_string();
        let raw_class = tables.get_string(raw_class_id).to_string();

        vdebug!(
            "StringParser[table]: pos={}, template='{}', token_type='{}', raw_class='{}'",
            self.pos,
            template,
            token_type,
            raw_class
        );

        match self.peek() {
            Some(tok) if tok.raw().eq_ignore_ascii_case(&template) && tok.is_code() => {
                let token_pos = self.pos;
                #[cfg(feature = "verbose-debug")]
                let raw = tok.raw().to_string();
                self.bump();

                vdebug!(
                    "StringParser[table] MATCHED: token='{}' as {} (type={}) at pos={}",
                    raw,
                    raw_class,
                    token_type,
                    token_pos
                );

                // PYTHON PARITY: matched_class is the raw_class (segment class name)
                // and instance_types contains the token_type from the parser
                // This matches Python's _match_at() which sets:
                // - matched_class=self.raw_class
                // - segment_kwargs with instance_types from segment_kwargs()
                Ok(MatchResult {
                    matched_slice: token_pos..token_pos + 1,
                    matched_class: Some(raw_class),
                    instance_types: Some(vec![token_type]),
                    // TODO: Add trim_chars and casefold from grammar when available
                    trim_chars: None,
                    casefold: CaseFold::None,
                    ..Default::default()
                })
            }
            _ => {
                vdebug!(
                    "StringParser[table] NOMATCH: template='{}', token={:?}",
                    template,
                    self.peek().map(|t| t.raw())
                );
                Ok(MatchResult::empty_at(self.pos))
            }
        }
    }

    /// Handle TypedParser using table-driven approach
    pub(crate) fn handle_typed_parser_table_driven(
        &mut self,
        mut frame: TableParseFrame,
    ) -> Result<TableFrameResult, ParseError> {
        let ctx = &self.grammar_ctx;
        let grammar_id = frame.grammar_id;
        vdebug!(
            "START TypedParser: frame_id={}, pos={}, grammar_id={:?}",
            frame.frame_id,
            frame.pos,
            grammar_id
        );
        // Extract all data from tables first (before any self methods)
        let tables = ctx.tables();

        // TypedParser stores: [template_id, token_type_id, raw_class_id] in aux_data
        // aux_data_offsets maps instruction -> aux_data start for variable-length aux
        let aux_start = tables.aux_data_offsets[grammar_id.get() as usize] as usize;
        let template_id = tables.aux_data[aux_start];
        let token_type_id = tables.aux_data[aux_start + 1];
        let raw_class_id = tables.aux_data[aux_start + 2];

        let template = tables.get_string(template_id).to_string();
        let token_type = tables.get_string(token_type_id).to_string();
        let raw_class = tables.get_string(raw_class_id).to_string();

        self.pos = frame.pos;

        vdebug!(
            "TypedParser[table]: pos={}, template='{}', token_type='{}'",
            self.pos,
            template,
            token_type
        );

        match self.peek() {
            Some(tok) if tok.is_type(&[&template]) => {
                // Capture all token-derived data before mutating self
                let token_pos = self.pos;
                #[cfg(feature = "verbose-debug")]
                let raw = tok.raw().to_string();
                #[cfg(feature = "verbose-debug")]
                let token_type_val = tok.token_type.clone();
                #[cfg(feature = "verbose-debug")]
                let inst_types = tok.instance_types.clone();
                #[cfg(feature = "verbose-debug")]
                let class_types = tok.class_types();

                // Advance position after capturing token data
                self.bump();

                vdebug!(
                    "TypedParser[table] MATCHED: type='{}', raw='{}' at pos={}",
                    token_type_val,
                    raw,
                    token_pos
                );

                // Extra debug: show token instance/class types
                vdebug!(
                    "TypedParser[table] MATCH DETAILS: frame_id={}, grammar_id={:?}, token_idx={}, instance_types={:?}, class_types={:?}",
                    frame.frame_id,
                    grammar_id,
                    token_pos,
                    inst_types,
                    class_types
                );

                // Build instance_types following Python TypedParser logic:
                // 1. Override type (token_type) - e.g., "quoted_literal"
                // 2. Segment class type - e.g., "literal" from "LiteralSegment"
                // 3. Template type - e.g., "single_quote" (if not in class hierarchy)
                let mut instance_types_vec = vec![token_type.clone()];

                // Add the segment class type if different from override
                // Use the dialect's pre-built segment type lookup (robust, authoritative)
                let class_type = self.dialect.get_segment_type(&raw_class);
                if let Some(cls_type) = class_type {
                    if cls_type != token_type {
                        instance_types_vec.push(cls_type.to_string());
                    }

                    // Add template type if not already added
                    // The segment class (e.g., LiteralSegment) has a fixed hierarchy that
                    // doesn't include token-specific types like "single_quote", so we add it
                    // Python checks: if not raw_class.class_is_type(template)
                    // For simplicity, we add template if it's different from what we already have
                    if template != token_type && template != cls_type {
                        instance_types_vec.push(template.clone());
                    }
                } else {
                    // Fallback: if lookup fails, just add template if different from token_type
                    log::warn!(
                        "Could not find segment type for class '{}', using fallback",
                        raw_class
                    );
                    if template != token_type {
                        instance_types_vec.push(template.clone());
                    }
                }

                vdebug!(
                    "TypedParser[table] Built instance_types: {:?} (token_type={}, raw_class={}, class_type={:?}, template={})",
                    instance_types_vec,
                    token_type,
                    raw_class,
                    class_type,
                    template
                );

                // Return MatchResult with raw_class as matched_class (segment class)
                // and computed instance_types (semantic type hierarchy)
                let casefold = self
                    .grammar_ctx
                    .casefold(grammar_id)
                    .unwrap_or(CaseFold::None);
                let trim_chars = self.grammar_ctx.trim_chars(grammar_id);
                let match_result = MatchResult {
                    matched_slice: token_pos..token_pos + 1,
                    matched_class: Some(raw_class),
                    instance_types: Some(instance_types_vec),
                    trim_chars,
                    casefold,
                    ..Default::default()
                };

                frame.state = FrameState::Complete(match_result);
                frame.end_pos = Some(self.pos);
                Ok(TableFrameResult::Push(frame))
            }
            Some(_tok) => {
                // Include instance and class type diagnostics to help debug why a
                // typed parser didn't match (e.g. instance_types contains the
                // expected seg type but token_type differs).
                #[cfg(feature = "verbose-debug")]
                let inst_types = _tok.instance_types.clone();
                #[cfg(feature = "verbose-debug")]
                let class_types = _tok.class_types();
                vdebug!(
                    "TypedParser[table] NOMATCH: expected type='{}', token_type='{}', raw='{}', instance_types={:?}, class_types={:?}",
                    template,
                    _tok.get_type(),
                    _tok.raw(),
                    inst_types,
                    class_types
                );
                frame.state = FrameState::Complete(MatchResult::empty_at(frame.pos));
                frame.end_pos = Some(frame.pos);
                Ok(TableFrameResult::Push(frame))
            }

            None => {
                vdebug!("TypedParser[table] NOMATCH: EOF at pos={}", self.pos);
                frame.state = FrameState::Complete(MatchResult::empty_at(frame.pos));
                frame.end_pos = Some(frame.pos);
                Ok(TableFrameResult::Push(frame))
            }
        }
    }

    /// Handle MultiStringParser using table-driven approach
    pub(crate) fn handle_multi_string_parser_table_driven(
        &mut self,
        grammar_id: GrammarId,
    ) -> Result<MatchResult, ParseError> {
        // Extract all data from tables first (before any self methods)
        let tables = self.grammar_ctx.tables();

        // MultiStringParser stores: [templates_start, templates_count, token_type_id, raw_class_id] in aux_data
        // The aux_data offset is stored in the separate AUX_DATA_OFFSETS table, NOT in first_child_idx
        let aux_start = tables.aux_data_offsets[grammar_id.get() as usize] as usize;
        let templates_start = tables.aux_data[aux_start] as usize;
        let templates_count = tables.aux_data[aux_start + 1] as usize;
        let token_type_id = tables.aux_data[aux_start + 2];
        let raw_class_id = tables.aux_data[aux_start + 3];

        // Guard against sentinel value 0xFFFFFFFF in aux data entries which
        // indicates "no value" in the tables. Skip sentinel entries and
        // collect only valid templates. Also guard token_type_id.
        let templates: Vec<String> = (0..templates_count)
            .filter_map(|i| {
                let template_id = tables.aux_data[templates_start + i];
                if template_id == 0xFFFFFFFF {
                    None
                } else {
                    Some(tables.get_string(template_id).to_string())
                }
            })
            .collect();

        let token_type = if token_type_id == 0xFFFFFFFF {
            // No token type specified; use empty string so matching will fail.
            "".to_string()
        } else {
            tables.get_string(token_type_id).to_string()
        };

        let raw_class = if raw_class_id == 0xFFFFFFFF {
            "RawSegment".to_string()
        } else {
            tables.get_string(raw_class_id).to_string()
        };

        vdebug!(
            "MultiStringParser[table]: pos={}, templates={:?}, token_type='{}', raw_class='{}'",
            self.pos,
            templates,
            token_type,
            raw_class
        );

        match self.peek() {
            Some(tok)
                if tok.is_code() && templates.iter().any(|t| tok.raw().eq_ignore_ascii_case(t)) =>
            {
                let token_pos = self.pos;
                #[cfg(feature = "verbose-debug")]
                let raw = tok.raw().to_string();
                self.bump();

                vdebug!(
                    "MultiStringParser[table] MATCHED: token='{}' as {} (type={}) at pos={}",
                    raw,
                    raw_class,
                    token_type,
                    token_pos
                );

                // PYTHON PARITY: matched_class is the raw_class (segment class name)
                // and instance_types contains the token_type from the parser
                Ok(MatchResult {
                    matched_slice: token_pos..token_pos + 1,
                    matched_class: Some(raw_class),
                    instance_types: Some(vec![token_type]),
                    // TODO: Add trim_chars and casefold from grammar when available
                    trim_chars: None,
                    casefold: CaseFold::None,
                    ..Default::default()
                })
            }
            _ => {
                vdebug!(
                    "MultiStringParser[table] NOMATCH: templates={:?}, token={:?}",
                    templates,
                    self.peek().map(|t| t.raw())
                );
                Ok(MatchResult::empty_at(self.pos))
            }
        }
    }

    /// Dump table-driven grammar / table information useful for debugging
    /// (variants, children, terminators, aux data, regex patterns etc.).
    /// If `grammar_id` is None, dumps all grammars in the tables.
    pub fn dump_table_driven_grammar_info(
        &self,
        grammar_id: Option<GrammarId>,
    ) -> Result<String, ParseError> {
        let ctx = &self.grammar_ctx;
        let tables = ctx.tables();

        // Use aux_data_offsets length as the number of instructions
        let total = tables.aux_data_offsets.len();

        let ids: Vec<GrammarId> = if let Some(gid) = grammar_id {
            vec![gid]
        } else {
            (0..total).map(|i| GrammarId(i as u32)).collect()
        };

        let mut out = String::new();

        for gid in &ids {
            let inst = ctx.inst(*gid);
            out.push_str(&format!("GrammarId {}: variant={:?}, child_count={}, first_child_idx={}, flags={:?}, parse_mode={:?}\n", gid.0, inst.variant, inst.child_count, inst.first_child_idx, inst.flags, inst.parse_mode));

            // children / element_children / terminators
            let children: Vec<u32> = ctx.children(*gid).map(|g| g.0).collect();
            out.push_str(&format!("  children: {:?}\n", children));
            let element_children: Vec<u32> = ctx.element_children(*gid).map(|g| g.0).collect();
            out.push_str(&format!("  element_children: {:?}\n", element_children));
            let terminators: Vec<u32> = ctx.terminators(*gid).map(|g| g.0).collect();
            out.push_str(&format!("  terminators: {:?}\n", terminators));
            if let Some(ex) = ctx.exclude(*gid) {
                out.push_str(&format!("  exclude: {}\n", ex.0));
            }

            // Variant-specific diagnostics
            match ctx.variant(*gid) {
                GrammarVariant::Ref => {
                    let name = ctx.ref_name(*gid);
                    out.push_str(&format!("  Ref name: {}\n", name));
                }
                GrammarVariant::StringParser
                | GrammarVariant::TypedParser
                | GrammarVariant::MultiStringParser
                | GrammarVariant::RegexParser => {
                    let tpl = ctx.template(*gid);
                    out.push_str(&format!("  template: {}\n", tpl));

                    // Print a few aux_data entries around the instruction's aux offset
                    let aux_off = tables.aux_data_offsets[(*gid).get() as usize] as usize;
                    let mut aux_vals: Vec<u32> = Vec::new();
                    for j in 0..4 {
                        if aux_off + j < tables.aux_data.len() {
                            aux_vals.push(tables.aux_data[aux_off + j]);
                        }
                    }
                    out.push_str(&format!("  aux_data@{}: {:?}\n", aux_off, aux_vals));

                    // If RegexParser, attempt to resolve regex/anti ids to patterns
                    if let GrammarVariant::RegexParser = ctx.variant(*gid) {
                        // Resolve pattern / anti-pattern / token_type / raw_class using helper to
                        // ensure aux_data_offsets logic is centralized and correct.
                        if let Some((pattern, anti_opt, token_type_opt, raw_class)) =
                            self.regex_quad_for(*gid)
                        {
                            out.push_str(&format!("  regex_aux_resolved: pattern='{}'\n", pattern));
                            if let Some(anti) = anti_opt {
                                out.push_str(&format!("  anti_pattern: {}\n", anti));
                            }
                            if let Some(tt) = token_type_opt {
                                out.push_str(&format!("  token_type: {}\n", tt));
                            }
                            out.push_str(&format!("  raw_class: {}\n", raw_class));
                        }
                    }
                }
                other => {
                    out.push_str(&format!("  other_variant: {:?}\n", other));
                }
            }

            out.push('\n');
        }

        log::info!("Dumped {} grammars", ids.len());
        log::info!("{}", out);
        Ok(out)
    }

    /// Helper to resolve regex pattern, optional anti-pattern, optional token_type,
    /// and raw_class for a given table-driven grammar id. Returns None if context
    /// missing or aux data invalid.
    pub fn regex_quad_for(
        &self,
        grammar_id: GrammarId,
    ) -> Option<(String, Option<String>, Option<String>, String)> {
        let ctx = &self.grammar_ctx;
        let tables = ctx.tables();

        let aux_start = tables.aux_data_offsets[grammar_id.get() as usize] as usize;
        if aux_start + 3 >= tables.aux_data.len() {
            return None;
        }

        let regex_id_raw = tables.aux_data[aux_start];
        let anti_raw = tables.aux_data[aux_start + 1];
        let token_type_raw = tables.aux_data[aux_start + 2];
        let raw_class_raw = tables.aux_data[aux_start + 3];

        if regex_id_raw == 0xFFFFFFFF || (regex_id_raw as usize) >= tables.regex_patterns.len() {
            return None;
        }

        let pattern = tables.regex_patterns[regex_id_raw as usize].to_string();

        let anti_opt =
            if anti_raw != 0xFFFFFFFF && (anti_raw as usize) < tables.regex_patterns.len() {
                Some(tables.regex_patterns[anti_raw as usize].to_string())
            } else {
                None
            };

        let token_type_opt = if token_type_raw != 0xFFFFFFFF {
            Some(tables.get_string(token_type_raw).to_string())
        } else {
            None
        };

        let raw_class = tables.get_string(raw_class_raw).to_string();

        Some((pattern, anti_opt, token_type_opt, raw_class))
    }

    /// Handle RegexParser using table-driven approach
    pub(crate) fn handle_regex_parser_table_driven(
        &mut self,
        grammar_id: GrammarId,
    ) -> Result<MatchResult, ParseError> {
        // Use helper to resolve pattern/anti/token_type/raw_class to centralize aux indexing
        let (pattern_str, anti_opt, token_type_opt, raw_class) =
            match self.regex_quad_for(grammar_id) {
                Some((p, a, t, r)) => (p, a, t, r),
                None => {
                    log::warn!(
                        "RegexParser[table]: invalid aux for grammar_id={} when resolving pattern",
                        grammar_id
                    );
                    return Ok(MatchResult::empty_at(self.pos));
                }
            };

        // Compile regex patterns (with caching). Normalize patterns by
        // stripping a single pair of leading '^' and trailing '$' if present
        // because emitted aux_data sometimes contains explicitly anchored
        // templates (e.g., anti_templates like '^...$'). RegexMode::new will
        // itself wrap the pattern with anchors, so leaving anchors in the
        // stored pattern results in double-anchoring and prevents matches.
        fn normalize_for_compile(s: &str) -> &str {
            if s.starts_with('^') && s.ends_with('$') {
                // Safe to slice off the first and last char
                &s[1..s.len() - 1]
            } else {
                s
            }
        }

        let pattern = {
            let mut cache = self.regex_cache.borrow_mut();
            let comp_key = normalize_for_compile(&pattern_str).to_string();
            cache
                .entry(comp_key.clone())
                .or_insert_with(|| RegexMode::new(&comp_key))
                .clone()
        };

        let anti_pattern = if let Some(anti_str) = anti_opt.as_ref() {
            let mut cache = self.regex_cache.borrow_mut();
            let comp_key = normalize_for_compile(anti_str).to_string();
            Some(
                cache
                    .entry(comp_key.clone())
                    .or_insert_with(|| RegexMode::new(&comp_key))
                    .clone(),
            )
        } else {
            None
        };

        vdebug!(
            "RegexParser[table]: pos={}, pattern='{}', anti='{}', token_type='{}'",
            self.pos,
            pattern_str,
            anti_opt.as_deref().unwrap_or("<none>"),
            token_type_opt.as_deref().unwrap_or("")
        );

        match self.peek() {
            Some(tok) => {
                let raw = tok.raw();

                // Check anti-pattern first (if present, should NOT match)
                if let Some(ref anti) = anti_pattern {
                    vdebug!("RegexParser[table] checking anti-pattern against '{}'", raw);
                    if anti.is_match(&raw) {
                        vdebug!("RegexParser[table] anti-pattern matched, returning Empty");
                        return Ok(MatchResult::empty_at(self.pos));
                    }
                }

                // Check main pattern
                if pattern.is_match(&raw) {
                    let token_pos = self.pos;
                    self.bump();

                    vdebug!(
                        "RegexParser[table] MATCHED: token='{}' at pos={}",
                        raw,
                        token_pos
                    );

                    // Return MatchResult with raw_class as matched_class
                    let token_type = token_type_opt.unwrap_or_default();
                    let casefold = self
                        .grammar_ctx
                        .casefold(grammar_id)
                        .unwrap_or(CaseFold::None);
                    Ok(MatchResult {
                        matched_slice: token_pos..token_pos + 1,
                        matched_class: Some(raw_class),
                        instance_types: Some(vec![token_type]),
                        trim_chars: None, // TODO: Add trim_chars support from grammar
                        casefold,
                        ..Default::default()
                    })
                } else {
                    vdebug!(
                        "RegexParser[table] NOMATCH: pattern '{}' didn't match token='{}'",
                        pattern_str,
                        raw
                    );
                    Ok(MatchResult::empty_at(self.pos))
                }
            }
            None => {
                vdebug!("RegexParser[table] NOMATCH: EOF at pos={}", self.pos);
                Ok(MatchResult::empty_at(self.pos))
            }
        }
    }

    // ============================================================================
    // Table-Driven Handler Methods (Base Grammars)
    // ============================================================================

    /// Handle Nothing using table-driven approach
    pub(crate) fn handle_nothing_table_driven(&mut self) -> Result<MatchResult, ParseError> {
        vdebug!("Nothing[table]: pos={}, returning Empty", self.pos);
        Ok(MatchResult::empty_at(self.pos))
    }

    /// Handle Empty using table-driven approach
    pub(crate) fn handle_empty_table_driven(&mut self) -> Result<MatchResult, ParseError> {
        vdebug!("Empty[table]: pos={}, returning Empty", self.pos);
        Ok(MatchResult::empty_at(self.pos))
    }

    /// Handle Missing using table-driven approach
    pub(crate) fn handle_missing_table_driven(&mut self) -> Result<MatchResult, ParseError> {
        vdebug!("Missing[table]: encountered at pos={}", self.pos);
        Err(ParseError::with_context(
            "Encountered Missing grammar".into(),
            Some(self.pos),
            None,
        ))
    }

    /// Handle Token using table-driven approach
    pub(crate) fn handle_token_table_driven(
        &mut self,
        grammar_id: GrammarId,
    ) -> Result<MatchResult, ParseError> {
        // Extract token_type from tables
        let tables = self.grammar_ctx.tables();

        // Token stores token_type string id in aux_data at the instruction's
        // aux_data_offsets index (the generator emits the type id there).
        let token_type_id = tables.aux_data_offsets[grammar_id.get() as usize];
        // let token_type_id = tables.aux_data[aux_start];
        let token_type = tables.get_string(token_type_id).to_string();

        vdebug!(
            "Token[table]: pos={}, token_type='{}'",
            self.pos,
            token_type
        );

        match self.peek() {
            Some(tok) if tok.is_type(&[&token_type]) => {
                let token_pos = self.pos;
                #[cfg(feature = "verbose-debug")]
                let raw = tok.raw().to_string();
                self.bump();

                vdebug!(
                    "Token[table] MATCHED: type='{}', raw='{}' at pos={}",
                    token_type,
                    raw,
                    token_pos
                );

                // Return MatchResult spanning this single token
                // The apply() method will retrieve token data from the tokens array
                Ok(MatchResult {
                    matched_slice: token_pos..token_pos + 1,
                    ..Default::default()
                })
            }
            Some(_tok) => {
                // Don't return an Err here; return Empty so the table-driven
                // engine can try other branches instead of aborting the
                // sequence. Include instance/class types for diagnostics.
                #[cfg(feature = "verbose-debug")]
                let inst_types = _tok.instance_types.clone();
                #[cfg(feature = "verbose-debug")]
                let class_types = _tok.class_types();
                vdebug!(
                    "Token[table] NOMATCH: expected='{}', token_type='{}', raw='{}', instance_types={:?}, class_types={:?}'",
                    token_type,
                    _tok.get_type(),
                    _tok.raw(),
                    inst_types,
                    class_types
                );
                Ok(MatchResult::empty_at(self.pos))
            }
            None => {
                vdebug!("Token[table] NOMATCH: EOF at pos={}", self.pos);
                Ok(MatchResult::empty_at(self.pos))
            }
        }
    }

    /// Handle Meta using table-driven approach
    pub(crate) fn handle_meta_table_driven(
        &mut self,
        grammar_id: GrammarId,
    ) -> Result<MatchResult, ParseError> {
        // Extract token_type from tables
        let tables = self.grammar_ctx.tables();

        // Meta stores token_type string id in aux_data at the instruction's aux offset
        // (generator encodes it there). Read via aux_data_offsets to get the string id.
        let token_type_id = tables.aux_data_offsets[grammar_id.get() as usize] as usize;
        let token_type = tables.get_string(token_type_id as u32).to_string();

        vdebug!("Meta[table]: pos={}, token_type='{}'", self.pos, token_type);

        // Meta creates zero-length inserts. Determine type and is_implicit flag.
        let (meta_type, is_implicit) = match token_type.as_str() {
            "indent" => (MetaSegmentType::Indent, false),
            "implicit_indent" => (MetaSegmentType::Indent, true),
            "dedent" => (MetaSegmentType::Dedent, false),
            _ => {
                log::warn!("Unknown meta token_type: {}", token_type);
                return Ok(MatchResult::empty_at(self.pos));
            }
        };

        // Return MatchResult with insert_segments
        Ok(MatchResult {
            matched_slice: self.pos..self.pos,
            insert_segments: vec![(self.pos, meta_type, is_implicit)],
            ..Default::default()
        })
    }

    /// Handle NonCodeMatcher using table-driven approach
    ///
    /// Matches ALL consecutive non-code segments (whitespace, newline, comment, EOF).
    /// This implements Python parity with NonCodeMatcher.match() which loops through
    /// segments until finding a code token, returning MatchResult with the full slice.
    pub(crate) fn handle_noncode_matcher_table_driven(
        &mut self,
    ) -> Result<MatchResult, ParseError> {
        let start_pos = self.pos;
        vdebug!("NonCodeMatcher[table]: pos={}", start_pos);

        // Count consecutive non-code tokens
        let mut count = 0;

        while let Some(tok) = self.peek() {
            // Check if this is a code token
            if tok.is_code() {
                #[cfg(feature = "verbose-debug")]
                let typ = tok.get_type();
                vdebug!(
                    "NonCodeMatcher[table]: stopped at code token type='{}' at pos={}",
                    typ,
                    self.pos
                );
                break;
            }

            // This is a non-code token - skip it
            #[cfg(feature = "verbose-debug")]
            let typ = tok.get_type();
            #[cfg(feature = "verbose-debug")]
            let raw = tok.raw();
            self.bump();
            count += 1;

            vdebug!(
                "NonCodeMatcher[table]: matched non-code type='{}', raw='{}' at pos={}",
                typ,
                raw,
                self.pos - 1
            );
        }

        if count == 0 {
            vdebug!(
                "NonCodeMatcher[table] NOMATCH: no non-code tokens at pos={}",
                start_pos
            );
            Ok(MatchResult::empty_at(start_pos))
        } else {
            vdebug!(
                "NonCodeMatcher[table] MATCHED: {} non-code tokens from pos {} to {}",
                count,
                start_pos,
                self.pos
            );

            // Return MatchResult with slice spanning all non-code tokens
            // apply() will retrieve token data using the slice
            Ok(MatchResult {
                matched_slice: start_pos..self.pos,
                ..Default::default()
            })
        }
    }

    // ========================================================================
    // Table-Driven Anything Handler
    // ========================================================================

    /// Handle Anything using table-driven approach
    /// Consumes all tokens until terminator or EOF, preserving bracket structure
    pub(crate) fn handle_anything_table_initial(
        &mut self,
        mut frame: TableParseFrame,
        grammar_id: GrammarId,
        parent_terminators: &[GrammarId],
        parent_max_idx: Option<usize>,
    ) -> Result<TableFrameResult, ParseError> {
        let start_pos = self.pos;
        let mut child_matches: Vec<MatchResult> = vec![];
        vdebug!(
            "Anything[table]: pos={}, parent_terminators={}, parent_max_idx={:?}",
            start_pos,
            parent_terminators.len(),
            parent_max_idx
        );

        let mut terminators_vec: Vec<GrammarId> =
            self.grammar_ctx.terminators(grammar_id).collect();
        if !self.grammar_ctx.inst(grammar_id).flags.reset_terminators() {
            terminators_vec.extend(parent_terminators.iter().cloned());
        }

        loop {
            // Check if we've reached our parent_max_idx boundary
            if let Some(max_idx) = parent_max_idx {
                if self.pos >= max_idx {
                    vdebug!(
                        "Anything[table]: reached parent_max_idx={}, stopping at pos={}",
                        max_idx,
                        self.pos
                    );
                    break;
                }
            }

            if self.is_terminated_table_driven(&terminators_vec) || self.is_at_end() {
                break;
            }

            if let Some(tok) = self.peek() {
                let tok_raw = tok.raw();

                // Handle bracket openers - match entire bracketed section with nested brackets
                if tok_raw == "(" || tok_raw == "[" || tok_raw == "{" {
                    let bracket_match =
                        self.match_bracket_recursively(tok_raw.as_str(), tok_raw == "(");
                    child_matches.push(bracket_match);
                } else {
                    // Regular token - just bump, it'll be part of the raw content
                    self.bump();
                }
            }
        }

        vdebug!(
            "Anything[table]: matched {} child_matches, pos {} -> {}",
            child_matches.len(),
            start_pos,
            self.pos
        );

        // Return a MatchResult with child_matches for brackets
        // Python's apply() will use child_matches to reconstruct brackets
        let result = MatchResult {
            matched_slice: start_pos..self.pos,
            child_matches,
            ..Default::default()
        };
        frame.state = FrameState::Complete(result);
        frame.end_pos = Some(self.pos);

        Ok(TableFrameResult::Push(frame))
    }

    /// Compatibility wrapper expected by `core.rs`.
    /// `core.rs` calls `handle_anything_table_driven`; implement a thin wrapper
    /// that forwards to `handle_anything_table_initial` with a dummy frame.
    pub(crate) fn handle_anything_table_driven(
        &mut self,
        grammar_id: GrammarId,
        parent_terminators: &[GrammarId],
        parent_max_idx: Option<usize>,
    ) -> Result<MatchResult, ParseError> {
        // Create a temporary table-driven frame to use the initial handler and then extract MatchResult
        let frame =
            TableParseFrame::new_child(0, grammar_id, self.pos, parent_terminators.to_vec(), None);

        match self.handle_anything_table_initial(
            frame,
            grammar_id,
            parent_terminators,
            parent_max_idx,
        )? {
            TableFrameResult::Push(f) => {
                if let FrameState::Complete(match_result) = f.state {
                    return Ok(match_result);
                }
                Ok(MatchResult::empty_at(self.pos))
            }
            TableFrameResult::Done => Ok(MatchResult::empty_at(self.pos)),
        }
    }

    /// Recursively match brackets, handling nested brackets properly.
    /// This ensures that nested brackets inside Anything grammars produce
    /// proper BracketedSegment child_matches.
    fn match_bracket_recursively(&mut self, open_bracket: &str, persists: bool) -> MatchResult {
        let close_bracket = match open_bracket {
            "(" => ")",
            "[" => "]",
            "{" => "}",
            _ => unreachable!(),
        };

        let bracket_start = self.pos;

        // Record opening bracket position with SymbolSegment class
        let open_bracket_match = MatchResult {
            matched_slice: self.pos..self.pos + 1,
            matched_class: Some("SymbolSegment".to_string()),
            instance_types: Some(vec!["start_bracket".to_string()]),
            ..Default::default()
        };
        self.bump();

        // Collect nested child matches (for nested brackets inside)
        let mut inner_child_matches: Vec<MatchResult> = vec![open_bracket_match];

        // Match everything until matching close bracket, recursively handling nested brackets
        while !self.is_at_end() {
            if let Some(inner_tok) = self.peek() {
                let inner_raw = inner_tok.raw();

                if inner_raw == close_bracket {
                    // Found our closing bracket
                    break;
                } else if inner_raw == "(" || inner_raw == "[" || inner_raw == "{" {
                    // Found a nested bracket - recursively match it
                    let nested_persists = inner_raw == "(";
                    let nested_match =
                        self.match_bracket_recursively(inner_raw.as_str(), nested_persists);
                    inner_child_matches.push(nested_match);
                } else {
                    // Regular token - just bump
                    self.bump();
                }
            } else {
                break;
            }
        }

        // Record closing bracket position with SymbolSegment class
        let bracket_end = if !self.is_at_end() {
            self.bump(); // consume the close bracket
            self.pos
        } else {
            self.pos
        };

        let close_bracket_match = MatchResult {
            matched_slice: bracket_end - 1..bracket_end,
            matched_class: Some("SymbolSegment".to_string()),
            instance_types: Some(vec!["end_bracket".to_string()]),
            ..Default::default()
        };
        inner_child_matches.push(close_bracket_match);

        if persists {
            // Create a BracketedSegment match
            // Note: bracket_persists is NOT stored in segment_kwargs.
            // In Python, it's only used as a decision flag for whether to wrap in BracketedSegment.
            // When wrapping, Python stores start_bracket/end_bracket (extracted from children), not bracket_persists.
            MatchResult {
                matched_slice: bracket_start..bracket_end,
                matched_class: Some("BracketedSegment".to_string()),
                child_matches: inner_child_matches,
                insert_segments: vec![
                    (bracket_start + 1, MetaSegmentType::Indent, false),
                    (bracket_end - 1, MetaSegmentType::Dedent, false),
                ],
                ..Default::default()
            }
        } else {
            // For non-persisting brackets, return a simple match with indent/dedent
            // but no BracketedSegment wrapper
            MatchResult {
                matched_slice: bracket_start..bracket_end,
                child_matches: inner_child_matches,
                insert_segments: vec![
                    (bracket_start + 1, MetaSegmentType::Indent, false),
                    (bracket_end - 1, MetaSegmentType::Dedent, false),
                ],
                ..Default::default()
            }
        }
    }
}
