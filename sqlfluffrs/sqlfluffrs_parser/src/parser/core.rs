//! Core Parser struct and implementation
//!
//! This module contains the Parser struct definition and its core methods
//! including the main entry point for parsing with grammar.

use hashbrown::HashSet;

use crate::parser::table_driven::frame::{TableFrameResult, TableParseFrame};
use crate::parser::FrameState;

use super::{cache::TableParseCache, Node, ParseError};
use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_types::regex::RegexMode;
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
    /// Optional owned RootGrammar. When present, callers can use `parse_root`
    /// to parse starting from this root without having to pass grammar ids
    /// or contexts manually.
    pub root: Option<RootGrammar>,
    // Regex cache for table-driven RegexParser (pattern_string -> compiled RegexMode)
    regex_cache: std::cell::RefCell<hashbrown::HashMap<String, RegexMode>>,
}

impl<'a> Parser<'a> {
    /// Create a new Parser instance with table-driven grammar support
    pub fn new(tokens: &'a [Token], dialect: Dialect) -> Parser<'a> {
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
            root: None,
            regex_cache: std::cell::RefCell::new(hashbrown::HashMap::new()),
        }
    }

    /// Enable or disable the parse cache (for debugging)
    pub fn set_cache_enabled(&mut self, enabled: bool) {
        self.cache_enabled = enabled;
    }

    // /// Parse with table-driven grammar (new implementation).
    // /// This is the entry point for GrammarId-based parsing.
    // pub fn parse_with_grammar_id(
    //     &mut self,
    //     grammar_id: GrammarId,
    //     parent_terminators: &[GrammarId],
    // ) -> Result<Node, ParseError> {
    //     // Must have grammar context to use table-driven approach
    //     let ctx = self.grammar_ctx.ok_or_else(|| {
    //         ParseError::new("parse_with_grammar_id requires GrammarContext".to_string())
    //     })?;

    //     // Get the variant enum for this grammar
    //     let variant = ctx.variant(grammar_id);

    //     // Dispatch based on variant type
    //     match variant {
    //         GrammarVariant::Nothing => self.handle_nothing_table_driven(),
    //         GrammarVariant::Empty => self.handle_empty_table_driven(),
    //         GrammarVariant::Missing => self.handle_missing_table_driven(),
    //         GrammarVariant::Token => self.handle_token_table_driven(grammar_id, ctx),
    //         GrammarVariant::StringParser => self.handle_string_parser_table_driven(grammar_id, ctx),
    //         GrammarVariant::TypedParser => self.handle_typed_parser_table_driven(grammar_id, ctx),
    //         GrammarVariant::MultiStringParser => {
    //             self.handle_multi_string_parser_table_driven(grammar_id, ctx)
    //         }
    //         GrammarVariant::RegexParser => self.handle_regex_parser_table_driven(grammar_id, ctx),
    //         GrammarVariant::Sequence => {
    //             self.handle_sequence_table_driven(grammar_id, ctx, parent_terminators)
    //         }
    //         GrammarVariant::OneOf => {
    //             // Synchronous table-driven OneOf implementation (falls back to iterative logic)
    //             // Use GrammarContext helpers to enumerate children, prune options and try each child
    //             let inst = ctx.inst(grammar_id);

    //             // Collect leading transparent tokens if allow_gaps
    //             let leading_ws = if inst.flags.allow_gaps() {
    //                 self.collect_transparent(true)
    //             } else {
    //                 Vec::new()
    //             };
    //             let post_skip_pos = self.pos;

    //             // Combine terminators
    //             let local_terminators: Vec<GrammarId> = ctx.terminators(grammar_id).collect();
    //             let all_terminators = Self::combine_terminators_table_driven(
    //                 &local_terminators,
    //                 parent_terminators,
    //                 inst.flags.reset_terminators(),
    //             );

    //             // Parse mode conversion
    //             let grammar_parse_mode = match inst.parse_mode {
    //                 sqlfluffrs_types::grammar_inst::ParseMode::Strict => {
    //                     sqlfluffrs_types::ParseMode::Strict
    //                 }
    //                 sqlfluffrs_types::grammar_inst::ParseMode::Greedy => {
    //                     sqlfluffrs_types::ParseMode::Greedy
    //                 }
    //                 sqlfluffrs_types::grammar_inst::ParseMode::GreedyOnceStarted => {
    //                     sqlfluffrs_types::ParseMode::GreedyOnceStarted
    //                 }
    //             };

    //             let max_idx = self.calculate_max_idx_table_driven(
    //                 post_skip_pos,
    //                 &all_terminators,
    //                 grammar_parse_mode,
    //                 None,
    //             );

    //             // Early termination check for GREEDY mode
    //             if grammar_parse_mode == sqlfluffrs_types::ParseMode::Greedy {
    //                 let element_children: Vec<GrammarId> =
    //                     ctx.element_children(grammar_id).collect();
    //                 if self.is_terminated_with_elements_table_driven(
    //                     &all_terminators,
    //                     &element_children,
    //                 ) {
    //                     if inst.flags.optional() {
    //                         return Ok(Node::Empty);
    //                     }
    //                 }
    //             }

    //             let all_children: Vec<GrammarId> = ctx.element_children(grammar_id).collect();
    //             let pruned_children = self.prune_options_table_driven(&all_children);

    //             if pruned_children.is_empty() {
    //                 return Ok(Node::Empty);
    //             }

    //             // Try each child and pick the longest (prefer "clean" nodes)
    //             let mut best: Option<(Node, usize, GrammarId)> = None;
    //             for &child_id in &pruned_children {
    //                 self.pos = post_skip_pos;
    //                 match self.parse_with_grammar_id(child_id, &all_terminators) {
    //                     Ok(node) if !node.is_empty() => {
    //                         let end_pos = self.pos;
    //                         let consumed = end_pos - post_skip_pos;
    //                         let child_is_clean = Self::is_node_clean(&node);

    //                         let is_better =
    //                             if let Some((ref current_best, current_consumed, _)) = &best {
    //                                 let current_is_clean = Self::is_node_clean(current_best);
    //                                 if child_is_clean && !current_is_clean {
    //                                     true
    //                                 } else if !child_is_clean && current_is_clean {
    //                                     false
    //                                 } else {
    //                                     consumed > *current_consumed
    //                                 }
    //                             } else {
    //                                 true
    //                             };

    //                         if is_better {
    //                             best = Some((node, consumed, child_id));
    //                         }
    //                     }
    //                     Ok(_) => {}
    //                     Err(_) => {}
    //                 }
    //             }

    //             if let Some((best_node, best_consumed, _best_child)) = best {
    //                 let final_pos = post_skip_pos + best_consumed;
    //                 self.pos = final_pos;
    //                 let result = if !leading_ws.is_empty() {
    //                     let mut children = leading_ws.clone();
    //                     children.push(best_node);
    //                     Node::Sequence { children }
    //                 } else {
    //                     best_node
    //                 };
    //                 Ok(result)
    //             } else {
    //                 // No match
    //                 Ok(Node::Empty)
    //             }
    //         }
    //         GrammarVariant::Delimited => {
    //             // NOTE: synchronous delimited table-driven fallback removed. Table-driven
    //             // composite grammars are handled by the iterative engine via
    //             // parse_table_driven_iterative in iterative.rs.
    //             return Err(ParseError::new(
    //                 "Delimited grammar handling removed".to_string(),
    //             ));
    //         }
    //         GrammarVariant::Bracketed => {
    //             unimplemented!("Bracketed handler not yet migrated")
    //         }
    //         GrammarVariant::AnyNumberOf => {
    //             unimplemented!("AnyNumberOf handler not yet migrated")
    //         }
    //         GrammarVariant::AnySetOf => {
    //             unimplemented!("AnySetOf handler not yet migrated")
    //         }
    //         GrammarVariant::Ref => {
    //             // self.handle_ref_table_driven(grammar_id, ctx, parent_terminators)
    //             unimplemented!("Wrong Ref handler was here")
    //         }
    //         GrammarVariant::Anything => {
    //             self.handle_anything_table_driven(grammar_id, ctx, parent_terminators)
    //         }
    //         GrammarVariant::Meta => self.handle_meta_table_driven(grammar_id, ctx),
    //         GrammarVariant::NonCodeMatcher => self.handle_noncode_matcher_table_driven(),
    //     }
    // }

    // /// Get the grammar for a rule by name.
    // /// This is used by the iterative parser to expand Ref nodes into their grammars.
    // pub fn get_rule_grammar(&self, name: &str) -> Result<Arc<Grammar>, ParseError> {
    //     // Look up the grammar for the segment
    //     match self.get_segment_grammar(name) {
    //         Some(g) => Ok(g.clone()),
    //         None => Err(ParseError::unknown_segment(
    //             name.to_string(),
    //             Some(self.pos),
    //         )),
    //     }
    // }

    // /// Call a grammar rule by name, producing a Node.
    // pub fn call_rule(
    //     &mut self,
    //     name: &str,
    //     parent_terminators: &[Arc<Grammar>],
    // ) -> Result<Node, ParseError> {
    //     self.call_rule_with_type(name, parent_terminators, None)
    // }

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
                raw: _,
                token_idx: _,
            } => Some(t.clone()),
            _ => None,
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
        // Obtain the root grammar for this dialect and dispatch based on its
        // variant (table-driven vs Arc-based). Clone to avoid holding borrows.
        let root_grammar = self.dialect.get_root_grammar().clone();
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
        // Parse using the root grammar.
        let grammar_id = root_grammar.grammar_id;
        let tables = root_grammar.tables;
        // Update grammar context if needed
        self.grammar_ctx = GrammarContext::new(tables);
        let nodes = self.parse_table_iterative(grammar_id, &[]);
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
    pub(crate) fn handle_string_parser_table_driven(
        &mut self,
        grammar_id: GrammarId,
    ) -> Result<Node, ParseError> {
        // Extract all data from tables first (before any self methods)
        let tables = self.grammar_ctx.tables();

        // StringParser stores: [template_id, token_type_id, raw_class_id] in aux_data
        // aux_data_offsets maps instruction -> aux_data start for variable-length aux
        let aux_start = tables.aux_data_offsets[grammar_id.get() as usize] as usize;
        let template_id = tables.aux_data[aux_start];
        let token_type_id = tables.aux_data[aux_start + 1];

        let template = tables.get_string(template_id).to_string();
        let token_type = tables.get_string(token_type_id).to_string();

        // Ensure parser position reflects the frame's start position
        // (some table-driven handlers set `self.pos = frame.pos`; keep parity)
        // Note: the caller (iterative engine) expects handlers to operate
        // based on the current parser `self.pos` for consistency.
        // For string parsers we don't have `frame` here, so rely on the
        // iterative loop to set `self.pos` before invoking this method.
        // However, in some call sites the parser's `self.pos` may still
        // reflect a previous frame; set defensively to the current
        // value (no-op) to make intent explicit.
        log::debug!(
            "StringParser[table]: pos={}, template='{}', token_type='{}'",
            self.pos,
            template,
            token_type
        );

        match self.peek() {
            Some(tok) if tok.raw().eq_ignore_ascii_case(&template) && tok.is_code() => {
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
    pub(crate) fn handle_typed_parser_table_driven(
        &mut self,
        mut frame: TableParseFrame,
    ) -> Result<TableFrameResult, ParseError> {
        let ctx = &self.grammar_ctx;
        let grammar_id = frame.grammar_id;
        log::debug!(
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

        let template = tables.get_string(template_id).to_string();
        let token_type = tables.get_string(token_type_id).to_string();

        self.pos = frame.pos;

        log::debug!(
            "TypedParser[table]: pos={}, template='{}', token_type='{}'",
            self.pos,
            template,
            token_type
        );

        match self.peek() {
            Some(tok) if tok.is_type(&[&template]) => {
                // Capture all token-derived data before mutating self
                let token_pos = self.pos;
                let raw = tok.raw().to_string();
                let token_type_val = tok.token_type.clone();
                let inst_types = tok.instance_types.clone();
                let class_types = tok.class_types();

                // Advance position after capturing token data
                self.bump();

                log::debug!(
                    "TypedParser[table] MATCHED: type='{}', raw='{}' at pos={}",
                    token_type_val,
                    raw,
                    token_pos
                );

                // Extra debug: show token instance/class types
                log::debug!(
                    "TypedParser[table] MATCH DETAILS: frame_id={}, grammar_id={:?}, token_idx={}, instance_types={:?}, class_types={:?}",
                    frame.frame_id,
                    grammar_id,
                    token_pos,
                    inst_types,
                    class_types
                );

                let node = Node::Token {
                    token_type,
                    raw,
                    token_idx: token_pos,
                };

                frame.state = FrameState::Complete(node);
                frame.end_pos = Some(self.pos);
                Ok(TableFrameResult::Push(frame))
            }
            Some(tok) => {
                // Include instance and class type diagnostics to help debug why a
                // typed parser didn't match (e.g. instance_types contains the
                // expected seg type but token_type differs).
                let inst_types = tok.instance_types.clone();
                let class_types = tok.class_types();
                log::debug!(
                    "TypedParser[table] NOMATCH: expected type='{}', token_type='{}', raw='{}', instance_types={:?}, class_types={:?}",
                    template,
                    tok.get_type(),
                    tok.raw(),
                    inst_types,
                    class_types
                );
                frame.state = FrameState::Complete(Node::Empty);
                frame.end_pos = Some(frame.pos);
                Ok(TableFrameResult::Push(frame))
            }

            None => {
                log::debug!("TypedParser[table] NOMATCH: EOF at pos={}", self.pos);
                frame.state = FrameState::Complete(Node::Empty);
                frame.end_pos = Some(frame.pos);
                Ok(TableFrameResult::Push(frame))
            }
        }
    }

    /// Handle MultiStringParser using table-driven approach
    pub(crate) fn handle_multi_string_parser_table_driven(
        &mut self,
        grammar_id: GrammarId,
    ) -> Result<Node, ParseError> {
        // Extract all data from tables first (before any self methods)
        let tables = self.grammar_ctx.tables();

        // MultiStringParser stores: [templates_start, templates_count, token_type_id, raw_class_id] in aux_data
        // The aux_data offset is stored in the separate AUX_DATA_OFFSETS table, NOT in first_child_idx
        let aux_start = tables.aux_data_offsets[grammar_id.get() as usize] as usize;
        let templates_start = tables.aux_data[aux_start] as usize;
        let templates_count = tables.aux_data[aux_start + 1] as usize;
        let token_type_id = tables.aux_data[aux_start + 2];

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
                        // Resolve pattern / anti-pattern / token_type using helper to
                        // ensure aux_data_offsets logic is centralized and correct.
                        if let Some((pattern, anti_opt, token_type_opt)) = self.regex_pair_for(*gid)
                        {
                            out.push_str(&format!("  regex_aux_resolved: pattern='{}'\n", pattern));
                            if let Some(anti) = anti_opt {
                                out.push_str(&format!("  anti_pattern: {}\n", anti));
                            }
                            if let Some(tt) = token_type_opt {
                                out.push_str(&format!("  token_type: {}\n", tt));
                            }
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

    /// Helper to resolve regex pattern, optional anti-pattern and optional token_type
    /// for a given table-driven grammar id. Returns None if context missing or
    /// aux data invalid.
    pub fn regex_pair_for(
        &self,
        grammar_id: GrammarId,
    ) -> Option<(String, Option<String>, Option<String>)> {
        let ctx = &self.grammar_ctx;
        let tables = ctx.tables();

        let aux_start = tables.aux_data_offsets[grammar_id.get() as usize] as usize;
        if aux_start + 2 >= tables.aux_data.len() {
            return None;
        }

        let regex_id_raw = tables.aux_data[aux_start];
        let anti_raw = tables.aux_data[aux_start + 1];
        let token_type_raw = tables.aux_data[aux_start + 2];

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

        Some((pattern, anti_opt, token_type_opt))
    }

    /// Handle RegexParser using table-driven approach
    pub(crate) fn handle_regex_parser_table_driven(
        &mut self,
        grammar_id: GrammarId,
    ) -> Result<Node, ParseError> {
        // Use helper to resolve pattern/anti/token_type to centralize aux indexing
        let (pattern_str, anti_opt, token_type_opt) = match self.regex_pair_for(grammar_id) {
            Some((p, a, t)) => (p, a, t),
            None => {
                log::warn!(
                    "RegexParser[table]: invalid aux for grammar_id={} when resolving pattern",
                    grammar_id
                );
                return Ok(Node::Empty);
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

        log::debug!(
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
                    log::debug!("RegexParser[table] checking anti-pattern against '{}'", raw);
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
                        token_type: token_type_opt.unwrap_or_default(),
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
    pub(crate) fn handle_nothing_table_driven(&mut self) -> Result<Node, ParseError> {
        log::debug!("Nothing[table]: pos={}, returning Empty", self.pos);
        Ok(Node::Empty)
    }

    /// Handle Empty using table-driven approach
    pub(crate) fn handle_empty_table_driven(&mut self) -> Result<Node, ParseError> {
        log::debug!("Empty[table]: pos={}, returning Empty", self.pos);
        Ok(Node::Empty)
    }

    /// Handle Missing using table-driven approach
    pub(crate) fn handle_missing_table_driven(&mut self) -> Result<Node, ParseError> {
        log::debug!("Missing[table]: encountered at pos={}", self.pos);
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
    ) -> Result<Node, ParseError> {
        // Extract token_type from tables
        let tables = self.grammar_ctx.tables();

        // Token stores token_type string id in aux_data at the instruction's
        // aux_data_offsets index (the generator emits the type id there).
        let token_type_id = tables.aux_data_offsets[grammar_id.get() as usize];
        // let token_type_id = tables.aux_data[aux_start];
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
                // Don't return an Err here; return Empty so the table-driven
                // engine can try other branches instead of aborting the
                // sequence. Include instance/class types for diagnostics.
                let inst_types = tok.instance_types.clone();
                let class_types = tok.class_types();
                log::debug!(
                    "Token[table] NOMATCH: expected='{}', token_type='{}', raw='{}', instance_types={:?}, class_types={:?}'",
                    token_type,
                    tok.get_type(),
                    tok.raw(),
                    inst_types,
                    class_types
                );
                Ok(Node::Empty)
            }
            None => {
                log::debug!("Token[table] NOMATCH: EOF at pos={}", self.pos);
                Ok(Node::Empty)
            }
        }
    }

    /// Handle Meta using table-driven approach
    pub(crate) fn handle_meta_table_driven(
        &mut self,
        grammar_id: GrammarId,
    ) -> Result<Node, ParseError> {
        // Extract token_type from tables
        let tables = self.grammar_ctx.tables();

        // Meta stores token_type string id in aux_data at the instruction's aux offset
        // (generator encodes it there). Read via aux_data_offsets to get the string id.
        let token_type_id = tables.aux_data_offsets[grammar_id.get() as usize] as usize;
        let token_type = tables.get_string(token_type_id as u32).to_string();

        log::debug!("Meta[table]: pos={}, token_type='{}'", self.pos, token_type);

        Ok(Node::Meta {
            token_type,
            token_idx: None,
        })
    }

    /// Handle NonCodeMatcher using table-driven approach
    pub(crate) fn handle_noncode_matcher_table_driven(&mut self) -> Result<Node, ParseError> {
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
        let mut anything_tokens = vec![];
        log::debug!(
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
                    log::debug!(
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
    ) -> Result<Node, ParseError> {
        // Create a temporary table-driven frame to use the initial handler and then extract the Node
        let frame =
            TableParseFrame::new_child(0, grammar_id, self.pos, parent_terminators.to_vec(), None);

        match self.handle_anything_table_initial(
            frame,
            grammar_id,
            parent_terminators,
            parent_max_idx,
        )? {
            TableFrameResult::Push(f) => {
                if let FrameState::Complete(node) = f.state {
                    return Ok(node);
                }
                Ok(Node::Empty)
            }
            TableFrameResult::Done => Ok(Node::Empty),
        }
    }
}
