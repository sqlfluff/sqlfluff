//! MatchResult type for the parser.
//!
//! This module implements a Python-parity MatchResult approach where match operations
//! return a description of what matched (slices, classes, inserts) rather than
//! eagerly building the AST. The AST is built later via `apply()`.
//!
//! This eliminates the need for global state tracking of collected whitespace positions,
//! and makes the parser more functional and composable.

use crate::vdebug;
use std::ops::Range;
use std::sync::Arc;

use crate::parser::types::Node;
use hashbrown::{HashMap, HashSet};
use sqlfluffrs_types::regex::RegexModeGroup;
use sqlfluffrs_types::token::{self, CaseFold};
use sqlfluffrs_types::{PositionMarker, Token};

/// Meta-segment types that can be inserted (like Python's Indent/Dedent)
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum MetaSegmentType {
    Indent,
    Dedent,
}

/// Describes a transparent token (whitespace/newline/comment/EOF) to insert
#[derive(Debug, Clone, PartialEq)]
pub struct TransparentInsert {
    pub token: Token,
}

/// Types of transparent tokens
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum TransparentType {
    Whitespace,
    Newline,
    Comment,
    EndOfFile,
}

/// A match result describing what was matched and how to construct the AST.
///
/// This is the functional alternative to mutating global state during parsing.
/// Each match operation returns a MatchResult, which can be combined via
/// `append()` and wrapped via `wrap()`. The final AST is built by calling `apply()`.
#[derive(Debug, Clone)]
pub struct MatchResult {
    /// Range in the token array that this match spans [start, end)
    pub matched_slice: Range<usize>,

    /// The class/type of segment to create when applying
    pub matched_class: Option<String>,

    /// Meta-segments to insert at specific positions (Indent/Dedent)
    /// Tuple is (position, meta_type, is_implicit)
    pub insert_segments: Vec<(usize, MetaSegmentType, bool)>,

    /// Transparent tokens (whitespace/newlines/comments) to insert
    pub insert_transparent: Vec<TransparentInsert>,

    /// Child matches (recursive structure using Rc for cheap sharing)
    pub child_matches: Vec<Arc<MatchResult>>,

    /// Pre-built child nodes (for Token matches that are already resolved)
    pub child_nodes: Vec<Node>,

    /// Optional kwargs for segment creation (e.g., expected message for Unparsable)
    pub segment_kwargs: HashMap<String, String>,

    pub instance_types: Option<Vec<String>>,
    pub trim_chars: Option<Vec<String>>,
    pub casefold: CaseFold,
    pub quoted_value: Option<(String, RegexModeGroup)>,
    pub escape_replacement: Option<(String, String)>,

    /// Parse error information (message and token position)
    pub parse_error: Option<(String, usize)>,
}

impl Default for MatchResult {
    fn default() -> Self {
        MatchResult {
            matched_slice: 0..0,
            matched_class: None,
            insert_segments: vec![],
            insert_transparent: vec![],
            child_matches: vec![],
            child_nodes: vec![],
            segment_kwargs: HashMap::new(),
            instance_types: None,
            trim_chars: None,
            casefold: CaseFold::None,
            quoted_value: None,
            escape_replacement: None,
            parse_error: None,
        }
    }
}

impl MatchResult {
    /// Create an empty match at a position
    pub fn empty_at(idx: usize) -> Self {
        MatchResult {
            matched_slice: idx..idx,
            ..Default::default()
        }
    }

    /// Create a match for a single token
    pub fn token(idx: usize, node: Node) -> Self {
        MatchResult {
            matched_slice: idx..idx + 1,
            matched_class: None,
            child_nodes: vec![node],
            ..Default::default()
        }
    }

    /// Flatten transparent grammar nodes for Python compatibility.
    ///
    /// Transparent nodes (those without a matched_class) are intermediate
    /// grammar constructs that shouldn't appear in the final match tree.
    /// This method recursively flattens them by promoting their children
    /// and insert_segments to the parent level.
    ///
    /// This eliminates the need to do this filtering on the Python side,
    /// reducing the amount of data transferred across the FFI boundary.
    pub fn flatten_transparent(mut self) -> Self {
        // Recursively flatten children first (bottom-up)
        let mut flattened_children = Vec::new();
        let mut promoted_insert_segments = Vec::new();

        for child_rc in self.child_matches {
            // Extract and flatten the child
            let child = Arc::try_unwrap(child_rc).unwrap_or_else(|rc| (*rc).clone());
            let flattened_child = child.flatten_transparent();

            // If the child is transparent (no matched_class), promote its contents
            if flattened_child.matched_class.is_none() {
                // Add the child's children directly to our children list
                flattened_children.extend(flattened_child.child_matches);
                // Collect insert_segments to promote them
                promoted_insert_segments.extend(flattened_child.insert_segments);
            } else {
                // Real segment - keep it
                flattened_children.push(Arc::new(flattened_child));
            }
        }

        // Merge promoted insert_segments with our own
        self.insert_segments.extend(promoted_insert_segments);
        self.child_matches = flattened_children;
        self
    }

    pub fn match_token_at(idx: usize, matched_class: Option<String>, token: &Token) -> Self {
        MatchResult {
            matched_slice: idx..idx + 1,
            matched_class,
            instance_types: Some(token.instance_types.clone()),
            trim_chars: token.trim_chars.clone(),
            casefold: token.casefold.clone(),
            quoted_value: token.quoted_value().cloned(),
            escape_replacement: token.escape_replacement().cloned(),
            parse_error: None,
            ..Default::default()
        }
    }

    // /// Bridge method: Create a MatchResult from an existing Node.
    // /// Used during migration to wrap legacy Node results.
    /// Create a MatchResult from a Node (temporary bridge during refactoring)
    ///
    /// For Token nodes, extracts the segment class name to ensure proper
    /// Python segment wrapping (KeywordSegment, IdentifierSegment, etc.)
    pub fn from_node(node: Node, start_idx: usize, end_idx: usize) -> Self {
        if node.is_empty() {
            return MatchResult::empty_at(start_idx);
        }
        let matched_class = node.get_type();

        MatchResult {
            matched_slice: start_idx..end_idx,
            matched_class,
            child_nodes: vec![node],
            ..Default::default()
        }
    }

    pub fn from_token(token: &Token, start_idx: usize) -> Self {
        let end_idx = start_idx + 1;

        MatchResult {
            matched_slice: start_idx..end_idx,
            matched_class: Some(token.get_type().to_string()),
            parse_error: None,
            ..Default::default()
        }
    }

    pub fn from_token_type(token: &Token, start_idx: usize) -> Self {
        let end_idx = start_idx + 1;

        MatchResult {
            matched_slice: start_idx..end_idx,
            matched_class: Some(token.get_type().to_string()),
            parse_error: None,
            ..Default::default()
        }
    }

    /// Create a MatchResult wrapping a single Node at a specific token position
    /// Used for inserting whitespace, meta segments, etc.
    pub fn from_node_at(node: Node, token_idx: usize) -> Self {
        if node.is_empty() {
            return MatchResult::empty_at(token_idx);
        }
        let matched_class = None;

        MatchResult {
            matched_slice: token_idx..token_idx + 1,
            matched_class,
            child_nodes: vec![node],
            ..Default::default()
        }
    }

    /// Create a MatchResult for a Sequence with child matches (lazy evaluation)
    pub fn sequence(start_idx: usize, end_idx: usize, children: Vec<Arc<MatchResult>>) -> Self {
        MatchResult {
            matched_slice: start_idx..end_idx,
            // PYTHON PARITY: Sequence is a grammar construct, not a segment class
            // Set matched_class to None so Python's apply() will:
            // 1. Process insert_segments (creating metas at correct positions)
            // 2. Process child_matches (recursively)
            // 3. Return all results unwrapped (no Sequence wrapper in final tree)
            matched_class: None,
            child_matches: children,
            ..Default::default()
        }
    }

    /// Create a MatchResult for a Ref with child matches (lazy evaluation)
    pub fn ref_match(
        _name: String,
        segment_type: Option<String>,
        segment_class: Option<String>,
        start_idx: usize,
        end_idx: usize,
        children: Vec<Arc<MatchResult>>,
    ) -> Self {
        // Only set matched_class if segment_type is explicitly provided from tables
        // Refs without segment_type are grammar-only (not Python segment classes)
        // and should not create a matched_class wrapper
        let class_name = segment_class;
        let class_type = segment_type;

        // PYTHON PARITY: If we have a segment class AND a single grammar wrapper child
        // (matched_class=None with insert_segments), lift insert_segments to the parent
        // and unwrap the child's children. This matches Python's behavior where metas
        // are attached to the segment class, not intermediate grammar wrappers.
        // BUT: Only do this if the child doesn't contain an UnparsableSegment, because
        // unwrapping in that case can cause issues with segment boundaries.
        if class_name.is_some() && children.len() == 1 {
            let child = &children[0];
            // Don't unwrap if the child contains an unparsable - keep structure intact
            if child.matched_class.is_none()
                // && !child.insert_segments.is_empty()
                && !child.contains_unparsable()
            {
                // Lift insert_segments from grammar wrapper to segment class
                let insert_segments = child.insert_segments.clone();
                // Use the child's children directly (unwrap the grammar wrapper)
                let unwrapped_children = child.child_matches.clone();
                return MatchResult {
                    matched_slice: start_idx..end_idx,
                    matched_class: class_type,
                    child_matches: unwrapped_children,
                    insert_segments,
                    ..Default::default()
                };
            }
        }

        MatchResult {
            matched_slice: start_idx..end_idx,
            matched_class: class_name,
            child_matches: children,
            ..Default::default()
        }
    }

    /// Create a MatchResult for Bracketed with child matches (lazy evaluation)
    /// When bracket_persists is true, wraps in BracketedSegment.
    /// When bracket_persists is false, returns children without wrapper (like Python).
    pub fn bracketed(
        start_idx: usize,
        end_idx: usize,
        children: Vec<Arc<MatchResult>>,
        bracket_persists: bool,
    ) -> Self {
        // Python parity: Insert Indent after opening bracket and Dedent before closing bracket
        // Python code (sequence.py Bracketed.match() lines ~580-582):
        //   insert_segments=(
        //       (start_match.matched_slice.stop, Indent),
        //       (end_match.matched_slice.start, Dedent),
        //   )
        let mut insert_segments = Vec::new();
        if let Some(first_child) = children.first() {
            // Indent after opening bracket
            let indent_pos = first_child.matched_slice.end;
            insert_segments.push((indent_pos, MetaSegmentType::Indent, false));
        }
        if let Some(last_child) = children.last() {
            // Dedent before closing bracket
            let dedent_pos = last_child.matched_slice.start;
            insert_segments.push((dedent_pos, MetaSegmentType::Dedent, false));
        }

        // Python parity: When bracket_persists is false (e.g., square/curly brackets),
        // don't wrap in BracketedSegment - just return the match with children inline.
        // When bracket_persists is true (parentheses), wrap in BracketedSegment.
        let matched_class = if bracket_persists {
            Some("BracketedSegment".to_string())
        } else {
            None
        };

        MatchResult {
            matched_slice: start_idx..end_idx,
            matched_class,
            child_matches: children,
            segment_kwargs: HashMap::new(),
            insert_segments,
            parse_error: None,
            ..Default::default()
        }
    }

    /// Create a MatchResult representing a parse error.
    /// Used when parsing fails and we need to report the error location.
    pub fn with_error(start_idx: usize, end_idx: usize, message: String, error_pos: usize) -> Self {
        MatchResult {
            matched_slice: start_idx..end_idx,
            matched_class: None,
            parse_error: Some((message, error_pos)),
            ..Default::default()
        }
    }

    /// Check if this match is empty (no tokens matched and no inserts)
    pub fn is_empty(&self) -> bool {
        self.matched_slice.is_empty()
            && self.insert_segments.is_empty()
            && self.insert_transparent.is_empty()
            && self.child_matches.is_empty()
            && self.child_nodes.is_empty()
    }

    /// Length of the match in tokens
    pub fn len(&self) -> usize {
        self.matched_slice.len()
    }

    /// Start position of the match
    pub fn start(&self) -> usize {
        self.matched_slice.start
    }

    /// End position of the match
    pub fn end(&self) -> usize {
        self.matched_slice.end
    }

    /// Compare two matches - longer is better, ties broken by "cleaner" match
    pub fn is_better_than(&self, other: &MatchResult) -> bool {
        if self.len() != other.len() {
            return self.len() > other.len();
        }
        // For equal length, prefer matches without Unparsable
        let self_clean = !self.contains_unparsable();
        let other_clean = !other.contains_unparsable();
        self_clean && !other_clean
    }

    /// Check if this match or any children contain Unparsable
    pub fn contains_unparsable(&self) -> bool {
        if let Some(ref class_name) = self.matched_class {
            if class_name == "UnparsableSegment" {
                return true;
            }
        }
        self.child_matches.iter().any(|c| c.contains_unparsable())
    }

    /// Combine another sequential match onto this one.
    ///
    /// If either match is empty, returns the other.
    /// The two matches must be sequential (self.end <= other.start).
    /// Gaps between matches are allowed and preserved.
    pub fn append(self, other: MatchResult) -> MatchResult {
        // If current is empty, return other
        if self.is_empty() {
            return other;
        }
        // If other is empty, return self
        if other.is_empty() {
            return self;
        }

        // They should be sequential (gap allowed)
        debug_assert!(
            self.matched_slice.end <= other.matched_slice.start,
            "Matches must be sequential: self ends at {}, other starts at {}",
            self.matched_slice.end,
            other.matched_slice.start
        );

        let new_slice = self.matched_slice.start..other.matched_slice.end;
        let mut insert_segments = vec![];
        let mut insert_transparent = vec![];
        let mut child_matches = vec![];
        let mut child_nodes = vec![];

        // Process both matches
        for m in [self, other] {
            match &m.matched_class {
                None => {
                    // No class, flatten into parent
                    insert_segments.extend(m.insert_segments);
                    insert_transparent.extend(m.insert_transparent);
                    child_matches.extend(m.child_matches);
                    child_nodes.extend(m.child_nodes);
                }
                _ => {
                    // Has a class, add as child match (wrapped in Rc)
                    child_matches.push(Arc::new(m));
                }
            }
        }

        MatchResult {
            matched_slice: new_slice,
            matched_class: None,
            insert_segments,
            insert_transparent,
            child_matches,
            child_nodes,
            segment_kwargs: HashMap::new(),
            instance_types: None,
            trim_chars: None,
            casefold: CaseFold::None,
            quoted_value: None,
            escape_replacement: None,
            parse_error: None,
        }
    }

    /// Wrap this result with an outer segment class.
    ///
    /// If the match is empty, returns it unchanged (can't wrap empty).
    pub fn wrap(self, outer_class: String) -> MatchResult {
        if self.is_empty() {
            return self;
        }

        // CRITICAL: If we're trying to wrap an UnparsableSegment, return it as-is.
        // Unparsable results should bubble up to the top without being wrapped in
        // parent segments, so they appear in the tree and generate violations.
        if let Some(ref class) = self.matched_class {
            if class == "UnparsableSegment" {
                return self;
            }
        }

        let (insert_segments, insert_transparent, child_matches, child_nodes) =
            match &self.matched_class {
                None => {
                    // No current class, flatten existing children into new wrapper
                    (
                        self.insert_segments,
                        self.insert_transparent,
                        self.child_matches,
                        self.child_nodes,
                    )
                }
                Some(_) => {
                    // Already has a class, make current match a child (wrapped in Rc)
                    (vec![], vec![], vec![Arc::new(self.clone())], vec![])
                }
            };

        MatchResult {
            matched_slice: self.matched_slice.clone(),
            matched_class: Some(outer_class),
            insert_segments,
            insert_transparent,
            child_matches,
            child_nodes,
            segment_kwargs: self.segment_kwargs.clone(),
            instance_types: self.instance_types.clone(),
            trim_chars: self.trim_chars.clone(),
            casefold: self.casefold.clone(),
            quoted_value: self.quoted_value.clone(),
            escape_replacement: self.escape_replacement.clone(),
            parse_error: self.parse_error.clone(),
        }
    }

    /// Add transparent tokens to this match result
    pub fn with_transparent(mut self, transparent: Vec<TransparentInsert>) -> MatchResult {
        self.insert_transparent.extend(transparent);
        self
    }

    /// Add meta segments (Indent/Dedent) to this match result
    pub fn with_meta(mut self, meta: Vec<(usize, MetaSegmentType, bool)>) -> MatchResult {
        self.insert_segments.extend(meta);
        self
    }

    /// Set casefold mode on this match result
    pub fn with_casefold(mut self, casefold: sqlfluffrs_types::token::CaseFold) -> MatchResult {
        self.casefold = casefold;
        self
    }

    /// Apply this match to tokens to create actual AST nodes.
    ///
    /// This is where materialization happens - converting the match description
    /// into the actual nested Node structure.
    pub fn apply(self, tokens: &[Token]) -> Node {
        // DEBUG: Log apply() entry for all named segments
        #[cfg(feature = "verbose-debug")]
        if let Some(ref class_name) = self.matched_class {
            vdebug!(
                "[APPLY-ENTRY] {}: matched_slice={:?}, child_matches={}, insert_segments={}, child_nodes={}",
                class_name,
                self.matched_slice,
                self.child_matches.len(),
                self.insert_segments.len(),
                self.child_nodes.len()
            );
        }
        println!(
            "[APPLY-ENTRY] matched_slice={:?}, child_matches={}, insert_segments={}, child_nodes={}, instance_types={:?}, matched_class={:?}",
            self.matched_slice,
            self.child_matches.len(),
            self.insert_segments.len(),
            self.child_nodes.len(),
            self.instance_types,
            self.matched_class,
        );

        if self.matched_slice.is_empty()
            && self.child_matches.is_empty()
            && self.child_nodes.is_empty()
        {
            // Build insert nodes functionally from insert_segments
            let inserts: Vec<Node> = self
                .insert_segments
                .iter()
                .map(|(idx, meta_type, is_implicit)| {
                    meta_to_node(*idx, meta_type, *is_implicit, tokens)
                })
                .collect();

            // If we have inserts and no matched_class, return them wrapped as a Sequence.
            if !inserts.is_empty() && self.matched_class.is_none() {
                return Node::Sequence { children: inserts };
            }

            panic!("Tried to apply zero length MatchResult with `matched_class`. This MatchResult is invalid.");
        }

        // Build a map of positions to things to insert/apply
        let mut trigger_map: HashMap<usize, Vec<TriggerItem>> = HashMap::new();

        // Add meta segments
        for (idx, meta_type, is_implicit) in &self.insert_segments {
            trigger_map
                .entry(*idx)
                .or_default()
                .push(TriggerItem::Meta(meta_type.clone(), *is_implicit));
        }

        // // Add transparent tokens
        // for insert in &self.insert_transparent {
        //     trigger_map
        //         .entry(insert.token_idx)
        //         .or_default()
        //         .push(TriggerItem::Transparent(insert.clone()));
        // }

        // Add child matches
        for child_rc in &self.child_matches {
            trigger_map
                .entry(child_rc.matched_slice.start)
                .or_default()
                .push(TriggerItem::ChildMatch((**child_rc).clone()));
        }

        // Add pre-built child nodes (keyed by their token_idx if available)
        for (i, node) in self.child_nodes.iter().enumerate() {
            let idx = node.get_token_idx().unwrap_or(self.matched_slice.start + i);
            trigger_map
                .entry(idx)
                .or_default()
                .push(TriggerItem::ChildNode(node.clone()));
        }

        // Walk through the slice, processing triggers at each position
        let mut result_nodes: Vec<Node> = vec![];
        let mut current_idx = self.matched_slice.start;

        // Get sorted trigger positions
        let mut positions: Vec<usize> = trigger_map.keys().copied().collect();
        positions.sort();

        for pos in positions {
            // PYTHON PARITY: Fill gap with raw tokens - any segments between child matches
            // should be included unchanged (this captures whitespace/comments between code)
            if pos > current_idx {
                for idx in current_idx..pos {
                    if idx < tokens.len() {
                        let tok = &tokens[idx];
                        result_nodes.push(Node::from_token(tok.clone()));
                    }
                }
                current_idx = pos;
            }

            // Process triggers at this position
            if let Some(triggers) = trigger_map.get(&pos) {
                for trigger in triggers {
                    match trigger {
                        TriggerItem::Meta(meta_type, is_implicit) => {
                            result_nodes.push(meta_to_node(pos, meta_type, *is_implicit, tokens));
                        }
                        TriggerItem::Transparent(insert) => {
                            result_nodes.push(Node::from_token(insert.token.clone()));
                            // if insert.token_idx >= current_idx {
                            //     current_idx = insert.token_idx + 1;
                            // }
                            current_idx += 1;
                        }
                        TriggerItem::ChildMatch(child) => {
                            let child_node = child.clone().apply(tokens);
                            // Only add non-empty nodes
                            if !matches!(child_node, Node::Empty) {
                                result_nodes.push(child_node);
                            }
                            if child.matched_slice.end > current_idx {
                                current_idx = child.matched_slice.end;
                            }
                        }
                        TriggerItem::ChildNode(node) => {
                            result_nodes.push(node.clone());
                            if let Some(idx) = node.get_token_idx() {
                                if idx + 1 > current_idx {
                                    current_idx = idx + 1;
                                }
                            }
                        }
                    }
                }
            }
        }

        // PYTHON PARITY: If we finish processing triggers and there are still tokens
        // left in the matched_slice, add them too (captures trailing whitespace/comments)
        if current_idx < self.matched_slice.end {
            for idx in current_idx..self.matched_slice.end {
                if idx < tokens.len() {
                    let tok = &tokens[idx];
                    result_nodes.push(Node::from_token(tok.clone()));
                }
            }
        }

        // Now wrap result_nodes with the matched_class if present
        if let Some(class_name) = self.matched_class {
            // Create the appropriate wrapper node based on class_name
            if result_nodes.is_empty() {
                vdebug!(
                    "[APPLY-DEBUG] {} result_nodes is EMPTY - returning Node::Empty",
                    class_name
                );
                return Node::Empty;
            }

            vdebug!(
                "[APPLY-DEBUG] {} wrapping {} nodes",
                class_name,
                result_nodes.len()
            );

            // For segment classes (end with "Segment"), wrap in Ref
            // For other cases, wrap in Sequence
            if class_name.ends_with("Segment") {
                // Get segment_type from grammar context if available
                // For now, derive it from class name
                let segment_type = class_name.strip_suffix("Segment").map(|s| {
                    // Convert CamelCase to snake_case
                    let mut result = String::new();
                    for (i, c) in s.chars().enumerate() {
                        if c.is_uppercase() && i > 0 {
                            result.push('_');
                        }
                        result.push(c.to_ascii_lowercase());
                    }
                    result
                });

                // Wrap children in a Sequence first, then in Ref
                let child = if result_nodes.len() == 1 {
                    result_nodes.into_iter().next().unwrap()
                } else {
                    Node::Sequence {
                        children: result_nodes,
                    }
                };

                Node::new_ref(class_name.clone(), segment_type, Some(class_name), child)
            } else {
                // Non-segment classes get wrapped in Sequence
                if result_nodes.len() == 1 {
                    result_nodes.into_iter().next().unwrap()
                } else {
                    Node::Sequence {
                        children: result_nodes,
                    }
                }
            }
        } else {
            // No matched_class - return as-is
            if result_nodes.is_empty() {
                Node::Empty
            } else if result_nodes.len() == 1 {
                println!(
                    "[APPLY-DEBUG] No matched_class, single result node: {:?}, instance_types={:?}",
                    result_nodes[0], self.instance_types,
                );
                result_nodes.into_iter().next().unwrap()
            } else {
                Node::Sequence {
                    children: result_nodes,
                }
            }
        }
    }
}

/// Internal enum for tracking what to process at each position
#[derive(Debug, Clone)]
enum TriggerItem {
    Meta(MetaSegmentType, bool), // (type, is_implicit)
    Transparent(TransparentInsert),
    ChildMatch(MatchResult),
    ChildNode(Node),
}

// /// Convert a transparent insert to a Node
// fn transparent_to_node(insert: &TransparentInsert) -> Node {
//     match insert.token_type {
//         TransparentType::Whitespace => Node::Whitespace {
//             raw: insert.raw.clone(),
//             token_idx: insert.token_idx,
//         },
//         TransparentType::Newline => Node::Newline {
//             raw: insert.raw.clone(),
//             token_idx: insert.token_idx,
//         },
//         TransparentType::Comment => Node::Comment {
//             raw: insert.raw.clone(),
//             token_idx: insert.token_idx,
//         },
//         TransparentType::EndOfFile => Node::EndOfFile {
//             raw: insert.raw.clone(),
//             token_idx: insert.token_idx,
//         },
//     }
// }

fn get_point_pos_at_idx(tokens: &[Token], idx: usize) -> PositionMarker {
    if idx < tokens.len() {
        let token = &tokens[idx];
        token.pos_marker
            .as_ref()
            .expect("Tokens passed to .apply() should all have position.")
            .start_point_marker()
    } else {
        // If idx is beyond the end, use the end position of the last token.
        let last = tokens
            .last()
            .expect("No tokens available to determine position.");
        last.pos_marker.as_ref()
            .expect("Tokens passed to .apply() should all have position.")
            .end_point_marker()
    }
}

/// Convert a meta segment type to a Node
fn meta_to_node(
    idx: usize,
    meta_type: &MetaSegmentType,
    is_implicit: bool,
    tokens: &[Token],
) -> Node {
    let pos = get_point_pos_at_idx(tokens, idx);
    let token = match (meta_type, is_implicit) {
        (MetaSegmentType::Indent, false) => Token::indent_token(pos, false, None, HashSet::new()),
        (MetaSegmentType::Indent, true) => {
            Token::implicit_indent_token(pos, true, None, HashSet::new())
        }
        (MetaSegmentType::Dedent, _) => Token::dedent_token(pos, false, None, HashSet::new()),
    };
    Node::from_token(token)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_empty_at() {
        let m = MatchResult::empty_at(5);
        assert!(m.is_empty());
        assert_eq!(m.len(), 0);
        assert_eq!(m.start(), 5);
        assert_eq!(m.end(), 5);
    }

    #[test]
    fn test_token_match() {
        let node = Node::new_token("keyword".to_string(), "SELECT".to_string(), 0);
        let m = MatchResult::token(0, node);
        assert!(!m.is_empty());
        assert_eq!(m.len(), 1);
        assert_eq!(m.start(), 0);
        assert_eq!(m.end(), 1);
    }

    #[test]
    fn test_append_empty() {
        let m1 = MatchResult::empty_at(0);
        let m2 = MatchResult::token(
            0,
            Node::new_token("keyword".to_string(), "SELECT".to_string(), 0),
        );

        let result = m1.append(m2.clone());
        assert_eq!(result.len(), m2.len());
    }

    #[test]
    fn test_append_sequential() {
        let m1 = MatchResult::token(
            0,
            Node::new_token("keyword".to_string(), "SELECT".to_string(), 0),
        );
        let m2 = MatchResult::token(
            2,
            Node::new_token("identifier".to_string(), "x".to_string(), 2),
        );

        let result = m1.append(m2);
        assert_eq!(result.matched_slice, 0..3);
        assert_eq!(result.child_nodes.len(), 2);
    }

    #[test]
    fn test_wrap() {
        let m = MatchResult::token(
            0,
            Node::new_token("keyword".to_string(), "SELECT".to_string(), 0),
        );
        let wrapped = m.wrap("SequenceSegment".to_string());

        assert_eq!(wrapped.matched_class, Some("SequenceSegment".to_string()));
        assert_eq!(wrapped.child_nodes.len(), 1);
    }

    #[test]
    fn test_is_better_than() {
        let m1 = MatchResult {
            matched_slice: 0..3,
            ..Default::default()
        };
        let m2 = MatchResult {
            matched_slice: 0..2,
            ..Default::default()
        };

        assert!(m1.is_better_than(&m2));
        assert!(!m2.is_better_than(&m1));
    }
}
