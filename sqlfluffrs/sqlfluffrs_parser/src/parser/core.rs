//! Core Parser struct and implementation
//!
//! This module contains the Parser struct definition and its core methods
//! including the main entry point for parsing with grammar.

use crate::parser::match_result::{self, MatchedClass, SegmentKwargs};
use crate::vdebug;
use std::sync::Arc;

use crate::parser::table_driven::frame::{TableFrameResult, TableParseFrame};
use crate::parser::FrameState;
use crate::parser::{MatchResult, MetaSegment};

use super::{cache::TableParseCache, Node, ParseError};
use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_types::regex::RegexMode;
use sqlfluffrs_types::{SimpleHint, Token};
// NEW: Table-driven grammar support
use sqlfluffrs_types::{GrammarContext, GrammarId, GrammarVariant, RootGrammar};

/// Read a string-id list from aux_data region starting at ``offset``.
/// Layout is ``[count, string_id_0, string_id_1, ...]``.
///
/// Returns an empty Vec when data is absent/corrupt or pre-schema-extension.
fn read_string_ids_from_aux(
    tables: &sqlfluffrs_types::GrammarTables,
    offset: usize,
    aux_end: usize,
) -> Vec<u32> {
    if offset >= aux_end {
        return Vec::new();
    }
    let count = tables.aux_data[offset] as usize;
    let start = offset + 1;
    let end = start.saturating_add(count);
    if end > aux_end {
        return Vec::new();
    }
    tables.aux_data[start..end]
        .iter()
        .copied()
        .filter(|id| *id != 0xFFFFFFFF)
        .collect()
}

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
    pub table_cache: TableParseCache, // Frame-level cache
    pub cache_enabled: bool,
    pub collected_transparent_positions: Vec<usize>, // Track which token positions have had transparent tokens collected (Vec for O(1) truncate)
    /// Stack of collection checkpoints for backtracking.
    /// Each checkpoint records which tokens were marked as collected at that point.
    pub collection_stack: Vec<CollectionCheckpoint>,
    pub pruning_calls: std::cell::Cell<usize>, // Track number of prune_options calls
    pub pruning_total: std::cell::Cell<usize>, // Total options considered
    pub pruning_kept: std::cell::Cell<usize>,  // Options kept after pruning
    pub pruning_hinted: std::cell::Cell<usize>, // Options that had hints
    pub pruning_complex: std::cell::Cell<usize>, // Options that returned None (complex)
    pub match_attempts: std::cell::Cell<usize>, // Track number of match attempts (like Python's longest_match)
    pub match_successes: std::cell::Cell<usize>, // Track number of successful matches
    pub complete_match_early_exits: std::cell::Cell<usize>, // Track early exits from complete matches
    pub terminator_checks: std::cell::Cell<usize>,          // Track number of terminator checks
    pub terminator_hits: std::cell::Cell<usize>, // Track number of terminator hits (early exits)
    /// Cache for terminator match results: (position, grammar_id) -> matches
    /// Key insight: the same terminator at the same position will always give the same result.
    /// This avoids redundant parse_table_iterative calls from nested Delimited grammars.
    pub terminator_match_cache: std::cell::RefCell<hashbrown::HashMap<(usize, u32), bool>>,
    /// Cache for terminator hash computation: Vec<GrammarId> -> u64
    /// Many grammars share the same terminators, so we cache the computed hashes.
    /// OPTIMIZATION: This avoids recomputing the same hash thousands of times in
    /// expression-heavy queries (arithmetic_a.sql, expression_recursion.sql).
    pub terminator_hash_cache: std::cell::RefCell<hashbrown::HashMap<Vec<u32>, u64>>,
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
    /// Maximum number of main-loop iterations before aborting.
    /// Configurable via `rust_parser_max_iterations` in `.sqlfluff`.
    pub max_parser_iterations: usize,
    /// Iteration count at which a warning is emitted (the former hard limit).
    /// Configurable via `rust_parser_warn_threshold` in `.sqlfluff`.
    pub parser_warn_threshold: usize,
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
            collected_transparent_positions: Vec::new(),
            collection_stack: Vec::new(),
            pruning_calls: std::cell::Cell::new(0),
            pruning_total: std::cell::Cell::new(0),
            pruning_kept: std::cell::Cell::new(0),
            pruning_hinted: std::cell::Cell::new(0),
            pruning_complex: std::cell::Cell::new(0),
            match_attempts: std::cell::Cell::new(0),
            match_successes: std::cell::Cell::new(0),
            complete_match_early_exits: std::cell::Cell::new(0),
            terminator_checks: std::cell::Cell::new(0),
            terminator_hits: std::cell::Cell::new(0),
            terminator_match_cache: std::cell::RefCell::new(hashbrown::HashMap::new()),
            terminator_hash_cache: std::cell::RefCell::new(hashbrown::HashMap::new()),
            simple_hint_cache: hashbrown::HashMap::new(),
            cache_enabled: true,
            grammar_ctx,
            indent_config,
            root: None,
            regex_cache: std::cell::RefCell::new(hashbrown::HashMap::new()),
            max_parser_iterations: 3_000_000,
            parser_warn_threshold: 2_000_000,
        }
    }

    /// Override the iteration limits for this parser (builder pattern).
    pub fn with_parser_limits(
        mut self,
        max_parser_iterations: usize,
        parser_warn_threshold: usize,
    ) -> Self {
        self.max_parser_iterations = max_parser_iterations;
        self.parser_warn_threshold = parser_warn_threshold;
        self
    }

    /// Enable or disable the parse cache (for debugging)
    pub fn set_cache_enabled(&mut self, enabled: bool) {
        self.cache_enabled = enabled;
    }

    /// Parse and return MatchResult
    ///
    /// We can pass either Rust's or Python's implementation of `apply` to convert the MatchResult into a Node.
    pub fn call_rule_as_root(&mut self) -> Result<MatchResult, ParseError> {
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

    pub fn root_parse(&mut self) -> Result<Node, ParseError> {
        // Obtain the root grammar for this dialect
        let root_grammar = self.dialect.get_root_grammar().clone();

        // Find first code position (trim leading non-code), mirroring Python's _start_idx loop
        let mut first_code_pos = self.tokens.len();
        for (i, token) in self.tokens.iter().enumerate() {
            if token.is_code() {
                first_code_pos = i;
                break;
            }
        }

        // Find last code position (trim trailing non-code), mirroring Python's _end_idx loop
        let mut last_code_pos = self.tokens.len();
        for (i, token) in self.tokens.iter().enumerate().rev() {
            if token.is_code() {
                last_code_pos = i + 1;
                break;
            }
        }

        // No code tokens at all — return a file segment containing only non-code, mirroring
        // Python's `if _start_idx == _end_idx: return cls(segments, fname=fname)`.
        if first_code_pos >= last_code_pos {
            let file_mr = MatchResult {
                matched_slice: 0..self.tokens.len(),
                matched_class: Some(MatchedClass::root()),
                insert_segments: vec![],
                child_matches: vec![],
            };
            let nodes = file_mr.apply(self.tokens);
            return Ok(nodes.into_iter().next().unwrap_or_default());
        }

        let token_slice_orig = self.tokens;
        // Mirror Python: pass segments[:_end_idx] and start matching at _start_idx
        self.tokens = &token_slice_orig[..last_code_pos];
        self.pos = first_code_pos;

        // Parse using the root grammar
        let grammar_id = root_grammar.grammar_id;
        let tables = root_grammar.tables;
        self.grammar_ctx = GrammarContext::new(tables);
        let grammar_name = self.grammar_ctx.grammar_id_name(grammar_id).to_string();
        let match_result = self.parse_table_iterative_match_result(grammar_id, &[])?;
        let match_end = match_result.end();

        // Restore parser state
        self.tokens = token_slice_orig;
        self.pos = 0;

        // Build the content child, mirroring Python's three-way branch:
        //   if not match      → UnparsableSegment(segments[_start_idx:_end_idx])
        //   elif _unmatched   → matched + non-code gap + UnparsableSegment(first_code..)
        //   else              → matched (+ any trailing non-code via gap-fill)
        let content_child: Arc<MatchResult> = if match_result.is_empty() {
            // No match at all – wrap the entire code region as unparsable
            Arc::new(MatchResult::with_error(
                first_code_pos,
                last_code_pos,
                grammar_name,
                first_code_pos,
            ))
        } else if match_end < last_code_pos {
            // Partial match – find the first code token in the unmatched tail
            let first_code_in_unmatched = token_slice_orig[match_end..last_code_pos]
                .iter()
                .position(|t| t.is_code())
                .map(|i| match_end + i)
                .unwrap_or(last_code_pos);

            // Wrap the code tail as UnparsableSegment("Nothing else in FileSegment.")
            let unparsable = Arc::new(MatchResult::with_error(
                first_code_in_unmatched,
                last_code_pos,
                "Nothing else in FileSegment.".to_string(),
                first_code_in_unmatched,
            ));

            // A wrapper (no segment class) that holds both the matched result and
            // the unparsable tail; gap-fill handles non-code between them.
            Arc::new(MatchResult {
                matched_slice: first_code_pos..last_code_pos,
                matched_class: None,
                insert_segments: vec![],
                child_matches: vec![Arc::new(match_result), unparsable],
            })
        } else {
            // Full match — trailing non-code is captured by gap-fill in apply()
            Arc::new(match_result)
        };

        // Wrap content in a root (file) node spanning ALL tokens so that leading and
        // trailing non-code are gap-filled, mirroring Python's
        // `cls(segments[:_start_idx] + content + segments[_end_idx:], fname=fname)`.
        let file_mr = MatchResult {
            matched_slice: 0..token_slice_orig.len(),
            matched_class: Some(MatchedClass::root()),
            insert_segments: vec![],
            child_matches: vec![content_child],
        };
        let root_nodes = file_mr.apply(token_slice_orig);
        Ok(root_nodes.into_iter().next().unwrap_or_default())
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

        // StringParser stores either:
        //   old schema: [template_id, token_type_id, raw_class_id]
        //   new schema: [template_id, token_type_id, raw_class_id, inst_count, inst_type_ids...,
        //                class_types_count, class_type_ids...]
        // aux_data_offsets maps instruction -> aux_data start for variable-length aux.
        let aux_start = tables.aux_data_offsets[grammar_id.get() as usize] as usize;
        let aux_end = if (grammar_id.get() as usize + 1) < tables.aux_data_offsets.len() {
            tables.aux_data_offsets[grammar_id.get() as usize + 1] as usize
        } else {
            tables.aux_data.len()
        };
        let template_id = tables.aux_data[aux_start];
        let token_type_id = tables.aux_data[aux_start + 1];
        let raw_class_id = tables.aux_data[aux_start + 2];

        let template = tables.get_string(template_id);
        let token_type = tables.get_string(token_type_id);
        let raw_class = tables.get_string(raw_class_id);
        let (configured_instance_type_ids, raw_class_class_type_ids) = if aux_end >= aux_start + 4 {
            let inst_count = tables.aux_data[aux_start + 3] as usize;
            let inst_start = aux_start + 4;
            let inst_end = inst_start.saturating_add(inst_count);
            let inst_ids = if inst_end <= aux_end {
                tables.aux_data[inst_start..inst_end]
                    .iter()
                    .copied()
                    .filter(|id| *id != 0xFFFFFFFF)
                    .collect::<Vec<_>>()
            } else {
                vec![token_type_id]
            };
            // Read raw_class._class_types ids from aux_data (after instance_types)
            let ct_ids = read_string_ids_from_aux(tables, inst_end, aux_end);
            (inst_ids, ct_ids)
        } else {
            (vec![token_type_id], vec![])
        };
        let casefold = self.grammar_ctx.casefold(grammar_id);
        let grammar_trim_chars = self.grammar_ctx.trim_chars(grammar_id);

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
                let configured_instance_types = configured_instance_type_ids
                    .iter()
                    .map(|id| tables.get_string(*id).to_string())
                    .collect::<Vec<_>>();
                let raw_class_class_types = raw_class_class_type_ids
                    .iter()
                    .map(|id| tables.get_string(*id).to_string())
                    .collect::<Vec<_>>();
                let mut segment_kwargs = match_result::segment_kwargs_from_token(
                    tok,
                    token_type,
                    Some(configured_instance_types),
                    casefold,
                );
                segment_kwargs.class_types = Some(raw_class_class_types);
                if let Some(grammar_tc) = grammar_trim_chars {
                    segment_kwargs.trim_chars = Some(grammar_tc);
                }
                let result = MatchResult {
                    matched_slice: token_pos..token_pos + 1,
                    matched_class: Some(MatchedClass {
                        class_name: raw_class.to_string(),
                        segment_type: Some(token_type.to_string()),
                        segment_kwargs,
                    }),
                    ..Default::default()
                };

                #[cfg(feature = "verbose-debug")]
                {
                    let raw = tok.raw().to_string();

                    vdebug!(
                        "StringParser[table] MATCHED: token='{}' as {} (type={}) at pos={}",
                        raw,
                        raw_class,
                        token_type,
                        token_pos
                    );
                }
                self.bump();

                // PYTHON PARITY: matched_class is the raw_class (segment class name)
                // and instance_types contains the token_type from the parser
                // This matches Python's _match_at() which sets:
                // - matched_class=self.raw_class
                // - segment_kwargs with instance_types from segment_kwargs()
                Ok(result)
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

        // TypedParser stores either:
        //   old schema: [template_id, token_type_id, raw_class_id]
        //   new schema: [template_id, token_type_id, raw_class_id, inst_count, inst_type_ids...,
        //                class_types_count, class_type_ids...]
        // aux_data_offsets maps instruction -> aux_data start for variable-length aux.
        let aux_start = tables.aux_data_offsets[grammar_id.get() as usize] as usize;
        let aux_end = if (grammar_id.get() as usize + 1) < tables.aux_data_offsets.len() {
            tables.aux_data_offsets[grammar_id.get() as usize + 1] as usize
        } else {
            tables.aux_data.len()
        };
        let template_id = tables.aux_data[aux_start];
        let token_type_id = tables.aux_data[aux_start + 1];
        let raw_class_id = tables.aux_data[aux_start + 2];

        let template = tables.get_string(template_id);
        let token_type = tables.get_string(token_type_id);
        let raw_class = tables.get_string(raw_class_id);
        let (configured_instance_type_ids, raw_class_class_type_ids) = if aux_end >= aux_start + 4 {
            let inst_count = tables.aux_data[aux_start + 3] as usize;
            let inst_start = aux_start + 4;
            let inst_end = inst_start.saturating_add(inst_count);
            let inst_ids = if inst_end <= aux_end {
                tables.aux_data[inst_start..inst_end]
                    .iter()
                    .copied()
                    .filter(|id| *id != 0xFFFFFFFF)
                    .collect::<Vec<_>>()
            } else {
                vec![token_type_id]
            };
            let ct_ids = read_string_ids_from_aux(tables, inst_end, aux_end);
            (inst_ids, ct_ids)
        } else {
            (vec![token_type_id], vec![])
        };
        let casefold = self.grammar_ctx.casefold(grammar_id);
        let grammar_trim_chars = self.grammar_ctx.trim_chars(grammar_id);

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
                {
                    let raw = tok.raw().to_string();
                    let token_type_val = tok.token_type.clone();
                    let inst_types = tok.instance_types.clone();
                    let class_types = tok.class_types();

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
                }

                // Build instance_types following Python TypedParser logic.
                //
                // Python parity note: `Ref("CodeSegment")` in Python resolves to
                // `CodeSegment.match()` which uses `isinstance(seg, CodeSegment)`.
                // When a token matches via isinstance (e.g. WordSegment is-a CodeSegment),
                // Python returns the segment UNCHANGED - preserving its original type.
                //
                // TypedParser only overrides the type when an explicit `type=` argument
                // was given. This is detectable: if `_instance_types[0] == raw_class.type`
                // there was no explicit override. If they differ, there was.
                //
                // In Rust, "no explicit override" means `token_type == cls_type` (the
                // TypedParser's configured type equals the class's base type). In that
                // case we preserve the token's own type (isinstance semantics). Otherwise
                // we keep the TypedParser's configured override type.
                let mut configured_instance_types = configured_instance_type_ids
                    .iter()
                    .map(|id| tables.get_string(*id).to_string())
                    .collect::<Vec<_>>();
                if configured_instance_types.is_empty() {
                    configured_instance_types.push(token_type.to_string());
                }

                let class_type = self.dialect.get_segment_type(&raw_class);

                let (effective_segment_type, instance_types_vec) = if let Some(cls_type) =
                    class_type
                {
                    if token_type == cls_type {
                        // No explicit type override: TypedParser was invoked like Python's
                        // isinstance path. Preserve the token's own type and instance_types
                        // so that e.g. a WordSegment token matching Ref("CodeSegment") outputs
                        // `word: value` instead of `raw: value`, or a double_quote token outputs
                        // `double_quote: "value"` instead of `raw: "value"`.
                        //
                        // This mirrors Python's RawSegment.get_type():
                        //   if instance_types: return instance_types[0]
                        //   return super().get_type()  (= class type attribute)
                        let tok_effective_type = tok
                            .instance_types
                            .first()
                            .cloned()
                            .unwrap_or_else(|| tok.token_type.clone());
                        let tok_inst = tok.instance_types.clone();
                        vdebug!(
                            "TypedParser[table] isinstance-path: token_type='{}' == cls_type='{}', preserving effective_type='{}', instance_types={:?}",
                            token_type,
                            cls_type,
                            tok_effective_type,
                            tok_inst
                        );
                        (tok_effective_type, tok_inst)
                    } else {
                        // Explicit type override: use configured instance_types from
                        // codegen (Python parity), with old-schema fallback.
                        let mut vec = configured_instance_types;
                        if cls_type != token_type && !vec.iter().any(|t| t == cls_type) {
                            vec.push(cls_type.to_string());
                        }
                        if template != token_type
                            && template != cls_type
                            && !vec.iter().any(|t| t == &template)
                        {
                            vec.push(template.to_string());
                        }
                        let effective_type = vec
                            .first()
                            .cloned()
                            .unwrap_or_else(|| token_type.to_string());
                        vdebug!(
                            "TypedParser[table] explicit-override-path: token_type='{}' != cls_type='{}', instance_types={:?}",
                            token_type,
                            cls_type,
                            vec
                        );
                        (effective_type, vec)
                    }
                } else {
                    // Fallback: no class type info available, use TypedParser config as-is
                    log::warn!(
                        "Could not find segment type for class '{}', using fallback",
                        raw_class
                    );
                    let mut vec = configured_instance_types;
                    if template != token_type && !vec.iter().any(|t| t == template) {
                        vec.push(template.to_string());
                    }
                    let effective_type = vec
                        .first()
                        .cloned()
                        .unwrap_or_else(|| token_type.to_string());
                    (effective_type, vec)
                };

                vdebug!(
                    "TypedParser[table] final: effective_segment_type='{}', instance_types={:?} (raw_class={}, class_type={:?}, template={})",
                    effective_segment_type,
                    instance_types_vec,
                    raw_class,
                    class_type,
                    template
                );

                // Return MatchResult with raw_class as matched_class (segment class)
                // and computed instance_types (semantic type hierarchy)
                let mut segment_kwargs = match_result::segment_kwargs_from_token(
                    tok,
                    &effective_segment_type,
                    Some(instance_types_vec),
                    casefold,
                );
                let raw_class_class_types = raw_class_class_type_ids
                    .iter()
                    .map(|id| tables.get_string(*id).to_string())
                    .collect::<Vec<_>>();
                segment_kwargs.class_types = Some(raw_class_class_types);
                if let Some(grammar_tc) = grammar_trim_chars {
                    segment_kwargs.trim_chars = Some(grammar_tc);
                }
                let match_result = MatchResult {
                    matched_slice: token_pos..token_pos + 1,
                    matched_class: Some(MatchedClass {
                        class_name: raw_class.to_string(),
                        segment_type: Some(effective_segment_type.clone()),
                        segment_kwargs,
                    }),
                    ..Default::default()
                };

                // Advance position after capturing token data
                self.bump();

                frame.state = FrameState::Complete(Arc::new(match_result));
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
                frame.state = FrameState::Complete(Arc::new(MatchResult::empty_at(frame.pos)));
                frame.end_pos = Some(frame.pos);
                Ok(TableFrameResult::Push(frame))
            }

            None => {
                vdebug!("TypedParser[table] NOMATCH: EOF at pos={}", self.pos);
                frame.state = FrameState::Complete(Arc::new(MatchResult::empty_at(frame.pos)));
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

        // MultiStringParser stores either:
        //   old schema: [templates_start, templates_count, token_type_id, raw_class_id]
        //   new schema: [templates_start, templates_count, token_type_id, raw_class_id,
        //                inst_count, inst_type_ids..., class_types_count, class_type_ids...]
        // The aux_data offset is stored in the separate AUX_DATA_OFFSETS table, NOT in first_child_idx
        let aux_start = tables.aux_data_offsets[grammar_id.get() as usize] as usize;
        let aux_end = if (grammar_id.get() as usize + 1) < tables.aux_data_offsets.len() {
            tables.aux_data_offsets[grammar_id.get() as usize + 1] as usize
        } else {
            tables.aux_data.len()
        };
        let templates_start = tables.aux_data[aux_start] as usize;
        let templates_count = tables.aux_data[aux_start + 1] as usize;
        let token_type_id = tables.aux_data[aux_start + 2];
        let raw_class_id = tables.aux_data[aux_start + 3];

        // Guard against sentinel value 0xFFFFFFFF in aux data entries which
        // indicates "no value" in the tables. Skip sentinel entries and
        // collect only valid templates. Also guard token_type_id.
        let template_ids: Vec<u32> = (0..templates_count)
            .filter_map(|i| {
                let template_id = tables.aux_data[templates_start + i];
                if template_id == 0xFFFFFFFF {
                    None
                } else {
                    Some(template_id)
                }
            })
            .collect();

        let token_type = if token_type_id == 0xFFFFFFFF {
            // No token type specified; use empty string so matching will fail.
            ""
        } else {
            tables.get_string(token_type_id)
        };
        let (configured_instance_type_ids, raw_class_class_type_ids) = if aux_end >= aux_start + 5 {
            let inst_count = tables.aux_data[aux_start + 4] as usize;
            let inst_start = aux_start + 5;
            let inst_end = inst_start.saturating_add(inst_count);
            let inst_ids = if inst_end <= aux_end {
                tables.aux_data[inst_start..inst_end]
                    .iter()
                    .copied()
                    .filter(|id| *id != 0xFFFFFFFF)
                    .collect::<Vec<_>>()
            } else {
                vec![token_type_id]
            };
            let ct_ids = read_string_ids_from_aux(tables, inst_end, aux_end);
            (inst_ids, ct_ids)
        } else {
            (vec![token_type_id], vec![])
        };

        let raw_class = if raw_class_id == 0xFFFFFFFF {
            "RawSegment"
        } else {
            tables.get_string(raw_class_id)
        };

        let casefold = self.grammar_ctx.casefold(grammar_id);
        let grammar_trim_chars = self.grammar_ctx.trim_chars(grammar_id);

        vdebug!(
            "MultiStringParser[table]: pos={}, templates={:?}, token_type='{}', raw_class='{}'",
            self.pos,
            template_ids,
            token_type,
            raw_class
        );

        match self.peek() {
            Some(tok)
                if tok.is_code()
                    && template_ids
                        .iter()
                        .any(|id| tok.raw().eq_ignore_ascii_case(tables.get_string(*id))) =>
            {
                let token_pos = self.pos;
                #[cfg(feature = "verbose-debug")]
                {
                    let raw = tok.raw().to_string();

                    vdebug!(
                        "MultiStringParser[table] MATCHED: token='{}' as {} (type={}) at pos={}",
                        raw,
                        raw_class,
                        token_type,
                        token_pos
                    );
                }

                // PYTHON PARITY: matched_class is the raw_class (segment class name)
                // and instance_types contains the token_type from the parser
                let configured_instance_types = configured_instance_type_ids
                    .iter()
                    .map(|id| tables.get_string(*id).to_string())
                    .collect::<Vec<_>>();
                let raw_class_class_types = raw_class_class_type_ids
                    .iter()
                    .map(|id| tables.get_string(*id).to_string())
                    .collect::<Vec<_>>();
                let mut segment_kwargs = match_result::segment_kwargs_from_token(
                    tok,
                    token_type,
                    Some(configured_instance_types),
                    casefold,
                );
                segment_kwargs.class_types = Some(raw_class_class_types);
                if let Some(grammar_tc) = grammar_trim_chars {
                    segment_kwargs.trim_chars = Some(grammar_tc);
                }
                let result = MatchResult {
                    matched_slice: token_pos..token_pos + 1,
                    matched_class: Some(MatchedClass {
                        class_name: raw_class.to_string(),
                        segment_type: Some(token_type.to_string()),
                        segment_kwargs,
                    }),
                    ..Default::default()
                };
                self.bump();
                Ok(result)
            }
            _ => {
                vdebug!(
                    "MultiStringParser[table] NOMATCH: templates={:?}, token={:?}",
                    template_ids,
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

        // RegexParser stores either:
        //   old schema: [regex_id, anti_regex_id, token_type_id, raw_class_id]
        //   new schema: [regex_id, anti_regex_id, token_type_id, raw_class_id,
        //                inst_count, inst_type_ids..., class_types_count, class_type_ids...]
        let tables = self.grammar_ctx.tables();
        let aux_start = tables.aux_data_offsets[grammar_id.get() as usize] as usize;
        let aux_end = if (grammar_id.get() as usize + 1) < tables.aux_data_offsets.len() {
            tables.aux_data_offsets[grammar_id.get() as usize + 1] as usize
        } else {
            tables.aux_data.len()
        };
        let token_type_id = if aux_start + 2 < tables.aux_data.len() {
            tables.aux_data[aux_start + 2]
        } else {
            0xFFFFFFFF
        };
        let (configured_instance_type_ids, raw_class_class_type_ids) = if aux_end >= aux_start + 5 {
            let inst_count = tables.aux_data[aux_start + 4] as usize;
            let inst_start = aux_start + 5;
            let inst_end = inst_start.saturating_add(inst_count);
            let inst_ids = if inst_end <= aux_end {
                tables.aux_data[inst_start..inst_end]
                    .iter()
                    .copied()
                    .filter(|id| *id != 0xFFFFFFFF)
                    .collect::<Vec<_>>()
            } else {
                token_type_opt
                    .as_ref()
                    .map(|_| vec![token_type_id])
                    .unwrap_or_default()
            };
            let ct_ids = read_string_ids_from_aux(tables, inst_end, aux_end);
            (inst_ids, ct_ids)
        } else {
            (
                token_type_opt
                    .as_ref()
                    .map(|_| vec![token_type_id])
                    .unwrap_or_default(),
                vec![],
            )
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

                    vdebug!(
                        "RegexParser[table] MATCHED: token='{}' at pos={}",
                        raw,
                        token_pos
                    );

                    // Return MatchResult with raw_class as matched_class
                    let token_type = token_type_opt.unwrap_or_default();
                    let configured_instance_types = configured_instance_type_ids
                        .iter()
                        .map(|id| tables.get_string(*id).to_string())
                        .collect::<Vec<_>>();
                    let raw_class_class_types = raw_class_class_type_ids
                        .iter()
                        .map(|id| tables.get_string(*id).to_string())
                        .collect::<Vec<_>>();
                    let casefold = self.grammar_ctx.casefold(grammar_id);
                    let grammar_trim_chars = self.grammar_ctx.trim_chars(grammar_id);
                    let mut segment_kwargs = match_result::segment_kwargs_from_token(
                        tok,
                        &token_type,
                        Some(configured_instance_types),
                        casefold,
                    );
                    segment_kwargs.class_types = Some(raw_class_class_types);
                    if let Some(grammar_tc) = grammar_trim_chars {
                        segment_kwargs.trim_chars = Some(grammar_tc);
                    }
                    let result = MatchResult {
                        matched_slice: token_pos..token_pos + 1,
                        matched_class: Some(MatchedClass {
                            class_name: raw_class.clone(),
                            segment_type: Some(token_type.clone()),
                            segment_kwargs,
                        }),
                        ..Default::default()
                    };
                    self.bump();
                    Ok(result)
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

    fn skip_non_code_and_meta_backward(&self, mut idx: isize) -> isize {
        while idx >= 0 {
            let tok = &self.tokens[idx as usize];
            if !tok.is_code() || tok.is_meta {
                idx -= 1;
            } else {
                break;
            }
        }
        idx
    }

    pub(crate) fn handle_preceded_by_table_driven(
        &mut self,
        grammar_id: GrammarId,
    ) -> Result<MatchResult, ParseError> {
        let tables = self.grammar_ctx.tables();
        let aux_offset = tables.aux_data_offsets[grammar_id.get() as usize] as usize;
        let sequence_count = tables.aux_data[aux_offset] as usize;

        for sequence_idx in 0..sequence_count {
            let sequence_meta_offset = aux_offset + 1 + (sequence_idx * 2);
            let preceding_start = tables.aux_data[sequence_meta_offset] as usize;
            let preceding_count = tables.aux_data[sequence_meta_offset + 1] as usize;

            if self.match_preceding_sequence_table_driven(preceding_start, preceding_count) {
                if self.pos < self.tokens.len() {
                    return Ok(MatchResult {
                        matched_slice: self.pos..self.pos + 1,
                        ..Default::default()
                    });
                }

                return Ok(MatchResult::empty_at(self.pos));
            }
        }

        Ok(MatchResult::empty_at(self.pos))
    }

    fn match_preceding_sequence_table_driven(
        &self,
        preceding_start: usize,
        preceding_count: usize,
    ) -> bool {
        let tables = self.grammar_ctx.tables();
        let mut prev = self.pos as isize - 1;

        for i in 0..preceding_count {
            prev = self.skip_non_code_and_meta_backward(prev);
            if prev < 0 {
                return false;
            }

            let keyword_idx = tables.aux_data[preceding_start + (preceding_count - 1 - i)];
            let expected = tables.get_string(keyword_idx);
            if self.tokens[prev as usize].raw_upper() != expected {
                return false;
            }
            prev -= 1;
        }

        true
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
        let meta_type = match token_type.as_str() {
            "indent" => MetaSegment::Indent { is_implicit: false },
            "implicit_indent" => MetaSegment::Indent { is_implicit: true },
            "dedent" => MetaSegment::Dedent { is_implicit: false },
            _ => {
                log::warn!("Unknown meta token_type: {}", token_type);
                return Ok(MatchResult::empty_at(self.pos));
            }
        };

        // Return MatchResult with insert_segments
        Ok(MatchResult {
            matched_slice: self.pos..self.pos,
            insert_segments: vec![(self.pos, meta_type)],
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
            child_matches: child_matches.into_iter().map(Arc::new).collect(),
            ..Default::default()
        };
        frame.state = FrameState::Complete(Arc::new(result));
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
                    return Ok((*match_result).clone());
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
            matched_class: Some(MatchedClass {
                class_name: "SymbolSegment".to_string(),
                segment_type: Some("start_bracket".to_string()),
                segment_kwargs: SegmentKwargs {
                    instance_types: Some(vec!["start_bracket".to_string()]),
                    ..Default::default()
                },
            }),
            ..Default::default()
        };
        self.bump();

        // Collect nested child matches (for nested brackets inside)
        let mut inner_child_matches: Vec<Arc<MatchResult>> = vec![Arc::new(open_bracket_match)];

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
                    inner_child_matches.push(Arc::new(nested_match));
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
            matched_class: Some(MatchedClass {
                class_name: "SymbolSegment".to_string(),
                segment_type: Some("end_bracket".to_string()),
                segment_kwargs: SegmentKwargs {
                    instance_types: Some(vec!["end_bracket".to_string()]),
                    ..Default::default()
                },
            }),
            ..Default::default()
        };
        inner_child_matches.push(Arc::new(close_bracket_match));

        MatchResult::bracketed(bracket_start, bracket_end, inner_child_matches, persists)
    }
}
