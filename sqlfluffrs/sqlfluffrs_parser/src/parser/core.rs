//! Core Parser struct and implementation
//!
//! This module contains the Parser struct definition and its core methods
//! including the main entry point for parsing with grammar.

use std::sync::Arc;

use hashbrown::HashSet;

use crate::parser::iterative::{FrameResult, ParseFrameStack};
use crate::parser::table_driven::frame::{TableFrameResult, TableParseFrame, TableParseFrameStack};
use crate::parser::{self, iterative, FrameContext, FrameState, ParseFrame};

use super::{cache::ParseCache, cache::TableParseCache, Node, ParseError};
use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_types::regex::RegexMode;
use sqlfluffrs_types::{Grammar, GrammarInstExt, ParseMode, SimpleHint, Token};
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
    pub grammar_hash_cache: hashbrown::HashMap<*const Grammar, u64>,
    pub simple_hint_cache: hashbrown::HashMap<u64, Option<SimpleHint>>,
    pub tokens: &'a [Token],
    pub pos: usize, // current position in tokens
    pub dialect: Dialect,
    pub parse_cache: ParseCache,
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
    // NEW: Table-driven grammar support (optional, for gradual migration)
    pub grammar_ctx: Option<&'a GrammarContext<'a>>,
    /// Optional owned RootGrammar (Arc or TableDriven). When present callers
    /// can use `parse_root` to parse starting from this root without having
    /// to pass grammar ids or contexts manually.
    pub root: Option<RootGrammar>,
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
            table_cache: TableParseCache::new(),
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
            root: None,
            regex_cache: std::cell::RefCell::new(hashbrown::HashMap::new()),
        }
    }

    /// Create a new Parser instance with table-driven grammar support
    pub fn new_with_tables(tokens: &'a [Token], dialect: Dialect) -> Parser<'a> {
        let root = dialect.get_root_grammar();
        let grammar_ctx = {
            match root {
                RootGrammar::TableDriven {
                    grammar_id: _,
                    tables,
                } => {
                    // Create a static GrammarContext from the static tables by leaking a Box.
                    // The tables are generated as `&'static GrammarTables`, so this leak
                    // is acceptable for the lifetime of the program.
                    let boxed = Box::new(GrammarContext::new(tables));
                    let static_ctx: &'static GrammarContext<'static> = Box::leak(boxed);
                    static_ctx
                }
                _ => {
                    // Not table-driven; return None
                    return Parser::new(tokens, dialect);
                }
            }
        };
        Parser {
            tokens,
            pos: 0,
            dialect,
            parse_cache: ParseCache::new(),
            table_cache: TableParseCache::new(),
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
            root: None,
            regex_cache: std::cell::RefCell::new(hashbrown::HashMap::new()),
        }
    }

    /// Create a new Parser instance with an explicit RootGrammar.
    /// This configures either Arc-based or table-driven parsing automatically.
    pub fn new_with_root(tokens: &'a [Token], dialect: Dialect, root: RootGrammar) -> Parser<'a> {
        let mut p = Parser::new(tokens, dialect);
        // If table-driven, set grammar_ctx to the provided tables
        if root.is_table_driven() {
            let (gid, tables) = root.as_table_driven();
            // Create a static GrammarContext from the static tables by leaking a Box.
            // The tables are generated as `&'static GrammarTables`, so this leak
            // is acceptable for the lifetime of the program.
            let boxed = Box::new(GrammarContext::new(tables));
            let static_ctx: &'static GrammarContext<'static> = Box::leak(boxed);
            p.grammar_ctx = Some(static_ctx);
        }
        p.root = Some(root);
        p
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
        // Dispatch parse using the root grammar variant.
        let nodes = match root_grammar {
            RootGrammar::Arc(arc) => self.parse_iterative(&arc, &[]),
            RootGrammar::TableDriven { grammar_id, tables } => {
                // Set grammar context and use iterative table-driven entry
                let boxed = Box::new(GrammarContext::new(tables));
                let static_ctx: &'static GrammarContext<'static> = Box::leak(boxed);
                self.grammar_ctx = Some(static_ctx);
                self.parse_table_iterative(grammar_id, &[])
            }
        };
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

    // /// Lookup SegmentDef by name
    // pub fn get_segment_grammar(&self, name: &str) -> Option<Arc<Grammar>> {
    //     // The dialect layer currently returns Option<RootGrammar>. Convert
    //     // Arc-based variants into Arc<Grammar> for legacy consumers. Table-driven
    //     // grammars cannot be represented as Arc<Grammar> here, so return None
    //     // in that case (callers that expect table-driven grammars should use
    //     // other APIs).
    //     match self.dialect.get_segment_grammar(name) {
    //         Some(RootGrammar::Arc(a)) => Some(a.clone()),
    //         Some(RootGrammar::TableDriven { .. }) => None,
    //         None => None,
    //     }
    // }

    /// Lookup SegmentDef by name
    pub fn get_segment_grammar(&self, name: &str) -> Option<GrammarId> {
        match self.dialect.get_segment_grammar(name) {
            Some(RootGrammar::Arc(_)) => None,
            Some(RootGrammar::TableDriven { grammar_id, .. }) => Some(grammar_id),
            None => None,
        }
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
        ctx: &GrammarContext,
    ) -> Result<Node, ParseError> {
        // Extract all data from tables first (before any self methods)
        let inst = ctx.inst(grammar_id);
        let tables = ctx.tables();

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
    pub(crate) fn handle_typed_parser_table_driven(
        &mut self,
        mut frame: TableParseFrame,
    ) -> Result<TableFrameResult, ParseError> {
        let ctx = self.grammar_ctx.ok_or_else(|| {
            ParseError::new(
                "TypedParser requires GrammarContext for table-driven parsing".to_string(),
            )
        })?;
        let grammar_id = frame.grammar_id;
        log::debug!(
            "START TypedParser: frame_id={}, pos={}, grammar_id={:?}",
            frame.frame_id,
            frame.pos,
            grammar_id
        );
        // Extract all data from tables first (before any self methods)
        let inst = ctx.inst(grammar_id);
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
        ctx: &GrammarContext,
    ) -> Result<Node, ParseError> {
        // Extract all data from tables first (before any self methods)
        let tables = ctx.tables();

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
        let ctx = self
            .grammar_ctx
            .ok_or_else(|| ParseError::new("GrammarContext required".to_string()))?;

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

            out.push_str("\n");
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
        let ctx = self.grammar_ctx?;
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
        ctx: &GrammarContext,
    ) -> Result<Node, ParseError> {
        // Extract all data from tables first (before any self methods)
        let inst = ctx.inst(grammar_id);
        let tables = ctx.tables();

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
        ctx: &GrammarContext,
    ) -> Result<Node, ParseError> {
        // Extract token_type from tables
        let inst = ctx.inst(grammar_id);
        let tables = ctx.tables();

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

    // /// Handle Ref using table-driven approach
    // fn handle_ref_table_driven(
    //     &mut self,
    //     mut frame: ParseFrame,
    //     grammar_id: GrammarId,
    //     ctx: &GrammarContext,
    //     parent_terminators: &[GrammarId],
    // ) -> Result<Node, ParseError> {
    //     // Resolve the referenced rule name from tables
    //     let name = ctx.ref_name(grammar_id);

    //     log::debug!(
    //         "Ref[table]: pos={}, resolving ref name='{}'",
    //         self.pos,
    //         name
    //     );

    //     // Ask dialect for the segment grammar. The dialect returns Option<RootGrammar>.
    //     match self.dialect.get_segment_grammar(name) {
    //         Some(RootGrammar::Arc(arc)) => {
    //             // Found an Arc-based grammar; delegate to existing Arc-based path
    //             // Note: parse_with_grammar_cached expects Arc<Grammar>
    //             let node = self.parse_with_grammar_cached(&arc, &[])?;
    //             // Wrap in Ref crate node as call_rule would
    //             if node.is_empty() {
    //                 return Ok(node);
    //             }
    //             let result = Node::Ref {
    //                 name: name.to_string(),
    //                 segment_type: None,
    //                 child: Box::new(node),
    //             };
    //             Ok(result.deduplicate())
    //         }
    //         Some(RootGrammar::TableDriven {
    //             grammar_id: target_gid,
    //             ..
    //         }) => {
    //             // Found a table-driven grammar id; dispatch to table-driven parser
    //             let node = self.parse_with_grammar_id(target_gid, parent_terminators)?;
    //             if node.is_empty() {
    //                 return Ok(node);
    //             }
    //             let result = Node::Ref {
    //                 name: name.to_string(),
    //                 segment_type: None,
    //                 child: Box::new(node),
    //             };
    //             Ok(result.deduplicate())
    //         }
    //         None => Err(ParseError::unknown_segment(
    //             name.to_string(),
    //             Some(self.pos),
    //         )),
    //     }
    // }

    /// Handle Meta using table-driven approach
    pub(crate) fn handle_meta_table_driven(
        &mut self,
        grammar_id: GrammarId,
        ctx: &GrammarContext,
    ) -> Result<Node, ParseError> {
        // Extract token_type from tables
        let inst = ctx.inst(grammar_id);
        let tables = ctx.tables();

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

    // // ============================================================================
    // // Table-Driven Handler Methods (Composite Grammars)
    // // ============================================================================

    // /// Handle Sequence using table-driven approach
    // /// Simplified recursive implementation - matches children in order
    // fn handle_sequence_table_driven(
    //     &mut self,
    //     grammar_id: GrammarId,
    //     ctx: &GrammarContext,
    //     parent_terminators: &[GrammarId],
    // ) -> Result<Node, ParseError> {
    //     let inst = ctx.inst(grammar_id);
    //     let start_pos = self.pos;

    //     log::debug!(
    //         "Sequence[table]: pos={}, children={}",
    //         start_pos,
    //         inst.child_count
    //     );

    //     let mut matched_nodes = Vec::new();

    //     // Iterate through child grammars
    //     for child_id in ctx.children(grammar_id) {
    //         let child_result = self.parse_with_grammar_id(child_id, parent_terminators)?;

    //         match child_result {
    //             Node::Empty => {
    //                 // Child didn't match - check if it's optional
    //                 if ctx.is_optional(child_id) {
    //                     log::debug!(
    //                         "Sequence[table]: child {} returned Empty (optional), skipping",
    //                         child_id.0
    //                     );
    //                     continue; // Skip optional element
    //                 } else {
    //                     // Required element didn't match
    //                     if inst.flags.optional() {
    //                         // Whole sequence is optional, return Empty
    //                         log::debug!(
    //                             "Sequence[table]: required child failed but sequence is optional"
    //                         );
    //                         self.pos = start_pos; // Backtrack
    //                         return Ok(Node::Empty);
    //                     } else {
    //                         // Required sequence with required element - fail
    //                         log::debug!("Sequence[table]: required child {} failed", child_id.0);
    //                         self.pos = start_pos; // Backtrack
    //                         return Err(ParseError::new(format!(
    //                             "Required element in sequence did not match at pos {}",
    //                             self.pos
    //                         )));
    //                     }
    //                 }
    //             }
    //             _ => {
    //                 // Child matched successfully
    //                 log::debug!(
    //                     "Sequence[table]: child {} matched, pos now {}",
    //                     child_id.0,
    //                     self.pos
    //                 );
    //                 matched_nodes.push(child_result);
    //             }
    //         }
    //     }

    //     if matched_nodes.is_empty() {
    //         log::debug!("Sequence[table]: no children matched, returning Empty");
    //         Ok(Node::Empty)
    //     } else {
    //         log::debug!(
    //             "Sequence[table]: matched {} children, pos {} -> {}",
    //             matched_nodes.len(),
    //             start_pos,
    //             self.pos
    //         );
    //         Ok(Node::Sequence {
    //             children: matched_nodes,
    //         })
    //     }
    // }

    // OneOf table-driven handlers migrated to `src/parser/handlers/anyof.rs`.
    // See `handlers/anyof.rs` for the table-driven `handle_oneof_...` implementations.

    // ========================================================================
    // Table-Driven Sequence Handlers
    // ========================================================================

    /// Handle Sequence Initial state using table-driven approach
    pub(crate) fn handle_sequence_table_driven_initial_old(
        &mut self,
        grammar_id: GrammarId,
        mut frame: parser::ParseFrame,
        parent_terminators: &[GrammarId],
        stack: &mut ParseFrameStack,
    ) -> Result<FrameResult, ParseError> {
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

        // Debug: log child ids and their variants/names to help diagnose mismatches
        let mut child_descrs: Vec<String> = Vec::new();
        for gid in &all_children {
            let var = ctx.variant(*gid);
            let descr = match var {
                sqlfluffrs_types::GrammarVariant::Ref => {
                    let name = ctx.ref_name(*gid);
                    format!("{}::Ref({})", gid.0, name)
                }
                sqlfluffrs_types::GrammarVariant::StringParser => {
                    let tpl = ctx.template(*gid);
                    format!("{}::String('{}')", gid.0, tpl)
                }
                sqlfluffrs_types::GrammarVariant::TypedParser => {
                    let tpl = ctx.template(*gid);
                    format!("{}::Typed('{}')", gid.0, tpl)
                }
                sqlfluffrs_types::GrammarVariant::Meta => {
                    // Read aux_data for meta token_type id
                    let aux = ctx.tables().aux_data_offsets[gid.get() as usize];
                    let name = ctx.tables().get_string(aux);
                    format!("{}::Meta('{}')", gid.0, name)
                }
                other => format!("{}::{:?}", gid.0, other),
            };
            child_descrs.push(descr);
        }
        log::debug!(
            "Sequence[table]: grammar_id={} children_list={:?}",
            grammar_id.0,
            child_descrs
        );

        if all_children.is_empty() {
            log::debug!("Sequence[table]: No children, returning Empty");
            frame.end_pos = Some(start_pos);
            frame.state = FrameState::Combining;
            stack.push(&mut frame);
            return Ok(FrameResult::Done);
        }

        // Combine terminators with parent_terminators
        let local_terminators: Vec<GrammarId> = ctx.terminators(grammar_id).collect();
        let all_terminators = Self::combine_terminators_table_driven(
            &local_terminators,
            parent_terminators,
            inst.flags.reset_terminators(),
        );

        // Convert parse_mode for calculate_max_idx
        let grammar_parse_mode = inst.parse_mode;

        // Calculate max_idx with terminators
        let max_idx = self.calculate_max_idx_table_driven(
            start_pos,
            &all_terminators,
            grammar_parse_mode,
            frame.parent_max_idx,
        );

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
            optional: inst.flags.optional(),
        };

        frame.state = FrameState::WaitingForChild {
            child_index: 0,
            total_children: all_children.len(),
        };

        // Create first child frame with combined terminators
        let first_child = all_children[0];
        let child_frame = parser::ParseFrame::new_table_driven_child(
            stack.frame_id_counter,
            first_child,
            start_pos,
            all_terminators.clone(),
            Some(max_idx),
        );

        log::debug!(
            "Sequence[table]: Trying first child grammar_id={} (frame_id={}, start_pos={})",
            first_child.0,
            frame.frame_id,
            start_pos
        );

        // Use helper to push parent and child, and set parent's last_child_frame_id
        parser::ParseFrame::push_sequence_child_and_update_parent(
            stack,
            &mut frame,
            child_frame,
            0,
        );

        Ok(FrameResult::Done)
    }

    /// Handle Sequence WaitingForChild state using table-driven approach
    pub(crate) fn handle_sequence_table_driven_waiting_for_child_old(
        &mut self,
        mut frame: parser::ParseFrame,
        child_node: &Node,
        child_end_pos: &usize,
        _child_element_key: &Option<u64>,
        stack: &mut ParseFrameStack,
    ) -> Result<FrameResult, ParseError> {
        use crate::parser::iterative::FrameResult;
        use crate::parser::{FrameContext, FrameState};

        let ctx = self.grammar_ctx.expect("GrammarContext required");

        // Avoid holding a long-lived mutable borrow of frame.context here.
        // Extract only the grammar_id for table lookups and read-only info for logging.
        let grammar_id = match &frame.context {
            FrameContext::SequenceTableDriven { grammar_id, .. } => *grammar_id,
            _ => unreachable!("Expected SequenceTableDriven context"),
        };

        let inst = ctx.inst(grammar_id);
        let all_children: Vec<GrammarId> = ctx.children(grammar_id).collect();

        // Read current index and first_match for logging (immutable borrow)
        let (current_element_idx_val, first_match_val) = match &frame.context {
            FrameContext::SequenceTableDriven {
                current_element_idx,
                first_match,
                ..
            } => (*current_element_idx, *first_match),
            _ => unreachable!("Expected SequenceTableDriven context"),
        };

        log::debug!(
            "Sequence[table] WaitingForChild: frame_id={}, child_empty={}, child_end_pos={}, current_idx={}/{}, first_match={}",
            frame.frame_id,
            child_node.is_empty(),
            child_end_pos,
            current_element_idx_val,
            all_children.len(),
            first_match_val
        );

        // Check if child matched
        if !child_node.is_empty() {
            // Child matched - update context in a short mutable scope to avoid borrow conflicts
            {
                log::debug!(
                    "Sequence[table]: frame_id={} child matched at pos {} (child_end_pos={}), pushing to accumulated. accumulated_before={}",
                    frame.frame_id,
                    self.pos,
                    child_end_pos,
                    frame.accumulated.len()
                );
                frame.accumulated.push(child_node.clone());

                // Mutably update context fields briefly and drop the borrow
                if let FrameContext::SequenceTableDriven {
                    matched_idx,
                    max_idx,
                    current_element_idx,
                    first_match,
                    original_max_idx: _,
                    ..
                } = &mut frame.context
                {
                    *matched_idx = *child_end_pos;
                    *current_element_idx += 1;

                    // GREEDY_ONCE_STARTED: After first match, trim max_idx to terminators
                    if *first_match && inst.parse_mode == ParseMode::GreedyOnceStarted {
                        log::debug!(
                            "Sequence[table]: First element matched in GREEDY_ONCE_STARTED, trimming max_idx"
                        );
                        *first_match = false;

                        // Recalculate max_idx with strict mode after first match
                        let all_terminators = frame.table_terminators.clone();
                        let new_max_idx = self.calculate_max_idx_table_driven(
                            *matched_idx,
                            &all_terminators,
                            sqlfluffrs_types::ParseMode::Strict,
                            frame.parent_max_idx,
                        );
                        *max_idx = new_max_idx;

                        log::debug!("Sequence[table]: Trimmed max_idx to {}", new_max_idx);
                    }
                }
            }
            // After the brief mutable update, re-read the relevant context fields into
            // local variables so we can use them without holding a mutable borrow.
            let (matched_idx_val, max_idx_val, current_element_idx_val) = match &frame.context {
                FrameContext::SequenceTableDriven {
                    matched_idx,
                    max_idx,
                    current_element_idx,
                    ..
                } => (*matched_idx, *max_idx, *current_element_idx),
                _ => unreachable!("Expected SequenceTableDriven context"),
            };

            // Check if we have more children to match
            if current_element_idx_val < all_children.len() {
                // Collect transparent tokens between elements if allow_gaps
                self.pos = matched_idx_val;
                let leading_ws = if inst.flags.allow_gaps() {
                    let ws = self.collect_transparent(true);
                    if !ws.is_empty() {
                        log::debug!(
                            "Sequence[table]: Collected {} transparent tokens between elements",
                            ws.len()
                        );
                        // Add to accumulated
                        for w in &ws {
                            frame.accumulated.push(w.clone());
                        }
                    }
                    ws
                } else {
                    Vec::new()
                };

                let next_start_pos = self.pos;

                // Try next child

                let next_child = all_children[current_element_idx_val];

                log::debug!(
                    "Sequence[table]: Trying next child grammar_id={}, pos={}, max_idx={}",
                    next_child.0,
                    next_start_pos,
                    max_idx_val
                );

                // Create child_frame first to avoid holding a mutable borrow on frame.context
                let child_frame = parser::ParseFrame::new_table_driven_child(
                    stack.frame_id_counter,
                    next_child,
                    next_start_pos,
                    frame.table_terminators.clone(),
                    Some(max_idx_val),
                );

                frame.state = FrameState::WaitingForChild {
                    child_index: current_element_idx_val,
                    total_children: all_children.len(),
                };

                // Use helper to push parent and child and also update current element idx
                parser::ParseFrame::push_sequence_child_and_update_parent(
                    stack,
                    &mut frame,
                    child_frame,
                    current_element_idx_val,
                );
                return Ok(FrameResult::Done);
            } else {
                // All children matched - transition to Combining
                log::debug!(
                    "Sequence[table]: All {} children matched, transitioning to Combining",
                    all_children.len()
                );
                self.pos = matched_idx_val;
                frame.end_pos = Some(matched_idx_val);
                frame.state = FrameState::Combining;
                stack.push(&mut frame);
                return Ok(FrameResult::Done);
            }
        } else {
            // Child failed (returned Empty)
            // Child failed (returned Empty)
            // If the element is optional, advance to the next child instead of failing.
            // Otherwise treat as failure.
            let failed_idx = current_element_idx_val;
            let failed_child = all_children[failed_idx];
            let failed_inst = ctx.inst(failed_child);

            if failed_inst.flags.optional() {
                log::debug!(
                    "Sequence[table]: Child {} returned Empty but is optional, advancing",
                    failed_idx
                );

                let next_index = failed_idx + 1;
                if next_index < all_children.len() {
                    // Prepare next child and push using helper. Create child_frame before any mutable borrows.
                    let next_child = all_children[next_index];
                    let child_frame = parser::ParseFrame::new_table_driven_child(
                        stack.frame_id_counter,
                        next_child,
                        frame.pos,
                        frame.table_terminators.clone(),
                        // Use parent's max_idx from context
                        match &frame.context {
                            FrameContext::SequenceTableDriven { max_idx, .. } => Some(*max_idx),
                            _ => None,
                        },
                    );

                    frame.state = FrameState::WaitingForChild {
                        child_index: next_index,
                        total_children: all_children.len(),
                    };

                    parser::ParseFrame::push_sequence_child_and_update_parent(
                        stack,
                        &mut frame,
                        child_frame,
                        next_index,
                    );

                    return Ok(FrameResult::Done);
                } else {
                    // No more children; transition to Combining
                    log::debug!(
                        "Sequence[table]: Optional child was the last element, transitioning to Combining"
                    );
                    self.rollback_collection_checkpoint(frame.frame_id);
                    frame.end_pos = Some(frame.pos);
                    frame.state = FrameState::Combining;
                    stack.push(&mut frame);
                    return Ok(FrameResult::Done);
                }
            } else {
                log::debug!(
                    "Sequence[table]: Child {} returned Empty, sequence failed",
                    failed_idx
                );

                // CRITICAL FIX: If this Sequence has optional=true at the grammar level,
                // return Empty immediately instead of going to Combining state.
                // This implements the correct behavior where an optional Sequence that fails
                // to match all required elements should return Empty, not a partial match.
                let sequence_optional = match &frame.context {
                    FrameContext::SequenceTableDriven { optional, .. } => *optional,
                    _ => false,
                };

                if sequence_optional {
                    log::debug!(
                        "Sequence[table]: Sequence-level optional=true - required element returned Empty, returning Empty immediately"
                    );
                    // Rollback collection checkpoint
                    self.rollback_collection_checkpoint(frame.frame_id);
                    // Return Empty directly
                    stack
                        .results
                        .insert(frame.frame_id, (Node::Empty, frame.pos, None));
                    return Ok(FrameResult::Done);
                }

                // Rollback collection checkpoint
                self.rollback_collection_checkpoint(frame.frame_id);

                frame.end_pos = Some(frame.pos);
                frame.state = FrameState::Combining;
                stack.push(&mut frame);
                return Ok(FrameResult::Done);
            }
        }
    }

    // ========================================================================
    // Table-Driven Bracketed Handlers
    // ========================================================================

    /// Handle Bracketed Initial state using table-driven approach
    pub(crate) fn handle_bracketed_table_driven_initial_old(
        &mut self,
        grammar_id: GrammarId,
        mut frame: parser::ParseFrame,
        parent_terminators: &[GrammarId],
        stack: &mut ParseFrameStack,
    ) -> Result<FrameResult, ParseError> {
        use crate::parser::iterative::FrameResult;
        use crate::parser::{BracketedState, FrameContext, FrameState};

        self.pos = frame.pos;
        let ctx = self.grammar_ctx.expect("GrammarContext required");

        let inst = ctx.inst(grammar_id);
        let start_pos = frame.pos;
        let terms = ctx.terminators(grammar_id).collect::<Vec<GrammarId>>();

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

        // Get bracket config from aux_data (indices into children array)
        let (start_bracket_idx, end_bracket_idx) = ctx.bracketed_config(grammar_id);

        log::debug!(
            "Bracketed[table]: start_bracket_idx={}, end_bracket_idx={}",
            start_bracket_idx,
            end_bracket_idx
        );

        // Get bracket GrammarIds using indices
        let open_bracket_id = all_children[start_bracket_idx];
        let _close_bracket_id = all_children[end_bracket_idx];

        // Store context for bracket matching
        frame.context = FrameContext::BracketedTableDriven {
            grammar_id,
            state: BracketedState::MatchingOpen,
            last_child_frame_id: Some(stack.frame_id_counter),
            bracket_max_idx: None, // Will be calculated after opening bracket matched
            content_ids: Vec::new(),
            content_idx: 0,
        };

        frame.state = FrameState::WaitingForChild {
            child_index: 0,
            total_children: 1,
        };

        // Create child frame to match opening bracket
        let mut open_frame = parser::ParseFrame::new_table_driven_child(
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

        // Push parent and opening-bracket child while updating parent's last_child_frame_id
        // parser::ParseFrame::push_child_and_update_parent(
        //     stack,
        //     &mut frame,
        //     open_frame,
        //     "Bracketed",
        // );
        let next_child_id = stack.frame_id_counter;
        if let Some(parent_frame) = stack.last_mut() {
            match &mut parent_frame.context {
                FrameContext::Bracketed {
                    last_child_frame_id,
                    ..
                } => *last_child_frame_id = Some(next_child_id),
                _ => {
                    todo!("implement update_parent_last_child_frame for this grammar type");
                }
            }
        }
        stack.increment_frame_id_counter();
        stack.push(&mut open_frame);
        Ok(FrameResult::Done)
    }

    /// Handle Bracketed WaitingForChild state using table-driven approach
    pub(crate) fn handle_bracketed_table_driven_waiting_for_child_old(
        &mut self,
        mut frame: parser::ParseFrame,
        child_node: &Node,
        child_end_pos: &usize,
        stack: &mut ParseFrameStack,
    ) -> Result<FrameResult, ParseError> {
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
                        let close_frame = parser::ParseFrame::new_table_driven_child(
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

                    let content_frame = parser::ParseFrame::new_table_driven_child(
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
                let close_frame = parser::ParseFrame::new_table_driven_child(
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

                // Push parent and close child while updating parent's last_child_frame_id
                parser::ParseFrame::push_child_and_update_parent(
                    stack,
                    &mut frame,
                    close_frame,
                    "Bracketed",
                );
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

    // /// Handle Bracketed Combining state using table-driven approach
    // pub(crate) fn handle_bracketed_table_driven_combining(
    //     &mut self,
    //     mut frame: TableParseFrame,
    //     stack: &mut TableParseFrameStack,
    // ) -> Result<TableFrameResult, ParseError> {
    //     let ctx = self.grammar_ctx.expect("GrammarContext required");
    //     let _stack = stack; // Suppress unused

    //     let FrameContext::BracketedTableDriven {
    //         grammar_id,
    //         state: bracket_state,
    //         ..
    //     } = &frame.context
    //     else {
    //         return Err(ParseError::new(
    //             "Expected BracketedTableDriven context in combining".to_string(),
    //         ));
    //     };

    //     let inst = ctx.inst(*grammar_id);

    //     log::debug!(
    //         "Bracketed[table] Combining: frame_id={}, accumulated={}, state={:?}",
    //         frame.frame_id,
    //         frame.accumulated.len(),
    //         bracket_state
    //     );

    //     // Build final result
    //     let (result_node, final_pos) = match bracket_state {
    //         parser::BracketedState::Complete => {
    //             // Successfully matched all three parts
    //             (
    //                 Node::Bracketed {
    //                     children: frame.accumulated.clone(),
    //                     bracket_persists: true, // TODO: Get from grammar config
    //                 },
    //                 frame.end_pos.unwrap_or(frame.pos),
    //             )
    //         }
    //         _ => {
    //             // Failed to match - return empty (with optional handling)
    //             if inst.flags.optional() {
    //                 (Node::Empty, frame.pos)
    //             } else {
    //                 (Node::Empty, frame.pos)
    //             }
    //         }
    //     };

    //     self.pos = final_pos;
    //     frame.end_pos = Some(final_pos);
    //     frame.state = FrameState::Complete(result_node);

    //     Ok(TableFrameResult::Push(frame))
    // }
}
