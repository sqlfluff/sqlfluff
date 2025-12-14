//! MatchResult type for the parser.
//!
//! This module implements a Python-parity MatchResult approach where match operations
//! return a description of what matched (slices, classes, inserts) rather than
//! eagerly building the AST. The AST is built later via `apply()`.
//!
//! This eliminates the need for global state tracking of collected whitespace positions,
//! and makes the parser more functional and composable.

use std::ops::Range;

use crate::parser::types::Node;
use hashbrown::HashMap;
use sqlfluffrs_types::token::CaseFold;
use sqlfluffrs_types::Token;

/// Meta-segment types that can be inserted (like Python's Indent/Dedent)
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum MetaSegmentType {
    Indent,
    Dedent,
}

/// Describes a transparent token (whitespace/newline/comment/EOF) to insert
#[derive(Debug, Clone, PartialEq)]
pub struct TransparentInsert {
    /// Position in the token array
    pub token_idx: usize,
    /// The raw text from the token
    pub raw: String,
    /// Type of transparent token
    pub token_type: TransparentType,
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
    pub insert_segments: Vec<(usize, MetaSegmentType)>,

    /// Transparent tokens (whitespace/newlines/comments) to insert
    pub insert_transparent: Vec<TransparentInsert>,

    /// Child matches (recursive structure)
    pub child_matches: Vec<MatchResult>,

    /// Pre-built child nodes (for Token matches that are already resolved)
    pub child_nodes: Vec<Node>,

    /// Optional kwargs for segment creation (e.g., expected message for Unparsable)
    pub segment_kwargs: HashMap<String, String>,

    pub instance_types: Option<Vec<String>>,
    pub trim_chars: Option<Vec<String>>,
    pub casefold: CaseFold,
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

    /// Create a match with just transparent tokens (for collecting whitespace without code)
    pub fn transparent_only(start_idx: usize, transparent: Vec<TransparentInsert>) -> Self {
        let end_idx = transparent
            .last()
            .map(|t| t.token_idx + 1)
            .unwrap_or(start_idx);
        MatchResult {
            matched_slice: start_idx..end_idx,
            matched_class: None,
            insert_transparent: transparent,
            ..Default::default()
        }
    }

    /// Recursively deduplicate a MatchResult tree globally.
    ///
    /// Removes duplicate slices not just within sibling groups, but across
    /// the entire tree. This prevents a slice from appearing both as a parent
    /// and as its own child, which would cause duplicates when Python's apply()
    /// materializes them. Needed because the table-driven parser can create
    /// redundant nesting during grammar matching.
    pub fn global_deduplicate(mut self) -> Self {
        use std::collections::HashSet;

        // Track all slices we've seen among siblings at this level only
        // We do NOT mark the parent's slice as seen, because children can
        // legitimately have the same slice as their parent (wrapping).
        let mut seen_slices: HashSet<(usize, usize)> = HashSet::new();

        // Recursively deduplicate children first (bottom-up)
        let mut deduped_children = Vec::new();
        for child in self.child_matches {
            let deduped_child = child.global_deduplicate();
            let slice_key = (
                deduped_child.matched_slice.start,
                deduped_child.matched_slice.end,
            );

            // Only keep this child if we haven't seen this exact slice in a sibling
            if !seen_slices.contains(&slice_key) {
                seen_slices.insert(slice_key);
                deduped_children.push(deduped_child);
            }
        }

        self.child_matches = deduped_children;
        self
    }

    /// Deduplicate child matches to prevent the same slice appearing multiple times.
    ///
    /// This is needed because nested Ref/Sequence wrappers can create duplicate children.
    /// We keep the first occurrence of each unique slice and discard duplicates.
    ///
    /// Additionally, if a child fully spans the parent's range and has no class,
    /// we can flatten it by using its children instead (avoiding redundant wrappers).
    fn deduplicate_children(children: Vec<MatchResult>) -> Vec<MatchResult> {
        use std::collections::HashSet;

        // If there's only one child or no children, no deduplication needed
        if children.len() <= 1 {
            return children;
        }

        // Helper function to check if a MatchResult contains a child with the exact slice
        fn contains_exact_slice(result: &MatchResult, start: usize, end: usize) -> bool {
            for child in &result.child_matches {
                if child.matched_slice.start == start && child.matched_slice.end == end {
                    return true;
                }
                // Recursively check grandchildren
                if contains_exact_slice(child, start, end) {
                    return true;
                }
            }
            false
        }

        // First pass: identify redundant bare leaves
        // A bare leaf at position X..Y is redundant if any sibling starts at X, extends to Z > Y,
        // AND has a nested child covering the exact X..Y slice.
        let mut redundant_indices = HashSet::new();
        for (i, child) in children.iter().enumerate() {
            if matches!(child.matched_class, None) && child.child_matches.is_empty() {
                // This is a bare leaf node. Check if any sibling makes it redundant.
                for (j, sibling) in children.iter().enumerate() {
                    if i == j {
                        continue; // Skip self-comparison
                    }
                    // Check if sibling starts at the same position and extends further
                    if sibling.matched_slice.start == child.matched_slice.start
                        && sibling.matched_slice.end > child.matched_slice.end
                    {
                        // Sibling is longer and starts at same position.
                        // Only mark as redundant if the sibling contains a nested child
                        // with the exact same slice, meaning the content is duplicated.
                        if contains_exact_slice(
                            sibling,
                            child.matched_slice.start,
                            child.matched_slice.end,
                        ) {
                            redundant_indices.insert(i);
                            break;
                        }
                    }
                }
            }
        }

        let mut seen_slices: HashSet<(usize, usize)> = HashSet::new();
        let mut deduped = Vec::new();

        for (i, child) in children.into_iter().enumerate() {
            // Skip if marked as redundant
            if redundant_indices.contains(&i) {
                continue;
            }

            let slice_key = (child.matched_slice.start, child.matched_slice.end);

            // Skip if we've already seen this exact slice
            if seen_slices.contains(&slice_key) {
                continue;
            }

            // If this child has no class and has children, check if any of its children
            // have the same slice. If so, prefer keeping those children instead.
            let mut should_flatten = false;
            if matches!(child.matched_class, None) && !child.child_matches.is_empty() {
                // Check if any of this child's children cover the same range
                for grandchild in &child.child_matches {
                    let grandchild_key =
                        (grandchild.matched_slice.start, grandchild.matched_slice.end);
                    if grandchild_key == slice_key {
                        // A grandchild covers the same range - flatten by using grandchildren
                        should_flatten = true;
                        break;
                    }
                }
            }

            if should_flatten {
                // Mark the parent slice as seen even though we're flattening it
                // This prevents duplicate flattened nodes from being added
                seen_slices.insert(slice_key);

                // Add the child's children instead of the child itself
                for grandchild in child.child_matches {
                    let grandchild_key =
                        (grandchild.matched_slice.start, grandchild.matched_slice.end);
                    if !seen_slices.contains(&grandchild_key) {
                        seen_slices.insert(grandchild_key);
                        deduped.push(grandchild);
                    }
                }
            } else {
                seen_slices.insert(slice_key);
                deduped.push(child);
            }
        }

        deduped
    }

    pub fn match_token_at(idx: usize, matched_class: Option<String>, token: &Token) -> Self {
        MatchResult {
            matched_slice: idx..idx + 1,
            matched_class,
            instance_types: Some(token.instance_types.clone()),
            trim_chars: token.trim_chars.clone(),
            casefold: token.casefold.clone(),
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
            ..Default::default()
        }
    }

    pub fn from_token_type(token: &Token, start_idx: usize) -> Self {
        let end_idx = start_idx + 1;

        MatchResult {
            matched_slice: start_idx..end_idx,
            matched_class: Some(token.get_type().to_string()),
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
    pub fn sequence(start_idx: usize, end_idx: usize, children: Vec<MatchResult>) -> Self {
        let deduped_children = Self::deduplicate_children(children);
        MatchResult {
            matched_slice: start_idx..end_idx,
            matched_class: Some("SequenceSegment".to_string()),
            child_matches: deduped_children,
            ..Default::default()
        }
    }

    /// Create a MatchResult for a Ref with child matches (lazy evaluation)
    pub fn ref_match(
        name: String,
        segment_type: Option<String>,
        start_idx: usize,
        end_idx: usize,
        children: Vec<MatchResult>,
    ) -> Self {
        let deduped_children = Self::deduplicate_children(children);
        // Only set matched_class if segment_type is explicitly provided from tables
        // Refs without segment_type are grammar-only (not Python segment classes)
        // and should not create a matched_class wrapper
        let class_name = segment_type;
        MatchResult {
            matched_slice: start_idx..end_idx,
            matched_class: class_name,
            child_matches: deduped_children,
            ..Default::default()
        }
    }

    /// Create a MatchResult for a DelimitedList with child matches (lazy evaluation)
    pub fn delimited(start_idx: usize, end_idx: usize, children: Vec<MatchResult>) -> Self {
        let deduped_children = Self::deduplicate_children(children);
        MatchResult {
            matched_slice: start_idx..end_idx,
            matched_class: Some("DelimitedSegment".to_string()),
            child_matches: deduped_children,
            ..Default::default()
        }
    }

    /// Create a MatchResult for Bracketed with child matches (lazy evaluation)
    pub fn bracketed(
        start_idx: usize,
        end_idx: usize,
        children: Vec<MatchResult>,
        bracket_persists: bool,
    ) -> Self {
        let deduped_children = Self::deduplicate_children(children);
        let mut segment_kwargs = HashMap::new();
        segment_kwargs.insert("bracket_persists".to_string(), bracket_persists.to_string());
        MatchResult {
            matched_slice: start_idx..end_idx,
            matched_class: Some("BracketedSegment".to_string()),
            child_matches: deduped_children,
            segment_kwargs,
            ..Default::default()
        }
    }

    /// Bridge method: Convert this MatchResult back to a Node.
    /// Used during migration when callers still expect Node.
    pub fn to_node(self, tokens: &[sqlfluffrs_types::Token]) -> Node {
        let nodes = self.apply(tokens);
        if nodes.is_empty() {
            Node::Empty
        } else if nodes.len() == 1 {
            nodes.into_iter().next().unwrap()
        } else {
            Node::Sequence { children: nodes }
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
                    // Has a class, add as child match
                    child_matches.push(m);
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
        }
    }

    /// Wrap this result with an outer segment class.
    ///
    /// If the match is empty, returns it unchanged (can't wrap empty).
    pub fn wrap(self, outer_class: String) -> MatchResult {
        if self.is_empty() {
            return self;
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
                    // Already has a class, make current match a child
                    (vec![], vec![], vec![self.clone()], vec![])
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
        }
    }

    /// Add transparent tokens to this match result
    pub fn with_transparent(mut self, transparent: Vec<TransparentInsert>) -> MatchResult {
        self.insert_transparent.extend(transparent);
        self
    }

    /// Add meta segments (Indent/Dedent) to this match result
    pub fn with_meta(mut self, meta: Vec<(usize, MetaSegmentType)>) -> MatchResult {
        self.insert_segments.extend(meta);
        self
    }

    /// Apply this match to tokens to create actual AST nodes.
    ///
    /// This is where materialization happens - converting the match description
    /// into the actual nested Node structure.
    pub fn apply(self, tokens: &[Token]) -> Vec<Node> {
        // If empty, return empty vec (or just inserts)
        if self.matched_slice.is_empty()
            && self.child_matches.is_empty()
            && self.child_nodes.is_empty()
        {
            // Only meta/transparent inserts - create them
            let mut result = vec![];
            for insert in &self.insert_transparent {
                result.push(transparent_to_node(insert));
            }
            for (idx, meta_type) in &self.insert_segments {
                result.push(meta_to_node(*idx, meta_type));
            }
            return result;
        }

        // Build a map of positions to things to insert/apply
        let mut trigger_map: HashMap<usize, Vec<TriggerItem>> = HashMap::new();

        // Add meta segments
        for (idx, meta_type) in &self.insert_segments {
            trigger_map
                .entry(*idx)
                .or_default()
                .push(TriggerItem::Meta(meta_type.clone()));
        }

        // Add transparent tokens
        for insert in &self.insert_transparent {
            trigger_map
                .entry(insert.token_idx)
                .or_default()
                .push(TriggerItem::Transparent(insert.clone()));
        }

        // Add child matches
        for child in &self.child_matches {
            trigger_map
                .entry(child.matched_slice.start)
                .or_default()
                .push(TriggerItem::ChildMatch(child.clone()));
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
                        let raw = tok.raw().to_string();
                        let tok_type = tok.get_type().to_string();
                        result_nodes.push(Node::new_token(tok_type, raw, idx));
                    }
                }
                current_idx = pos;
            }

            // Process triggers at this position
            if let Some(triggers) = trigger_map.get(&pos) {
                for trigger in triggers {
                    match trigger {
                        TriggerItem::Meta(meta_type) => {
                            result_nodes.push(meta_to_node(pos, meta_type));
                        }
                        TriggerItem::Transparent(insert) => {
                            result_nodes.push(transparent_to_node(insert));
                            if insert.token_idx >= current_idx {
                                current_idx = insert.token_idx + 1;
                            }
                        }
                        TriggerItem::ChildMatch(child) => {
                            let child_nodes = child.clone().apply(tokens);
                            result_nodes.extend(child_nodes);
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
                    let raw = tok.raw().to_string();
                    let tok_type = tok.get_type().to_string();
                    result_nodes.push(Node::new_token(tok_type, raw, idx));
                }
            }
        }

        result_nodes
    }
}

/// Internal enum for tracking what to process at each position
#[derive(Debug, Clone)]
enum TriggerItem {
    Meta(MetaSegmentType),
    Transparent(TransparentInsert),
    ChildMatch(MatchResult),
    ChildNode(Node),
}

/// Convert a transparent insert to a Node
fn transparent_to_node(insert: &TransparentInsert) -> Node {
    match insert.token_type {
        TransparentType::Whitespace => Node::Whitespace {
            raw: insert.raw.clone(),
            token_idx: insert.token_idx,
        },
        TransparentType::Newline => Node::Newline {
            raw: insert.raw.clone(),
            token_idx: insert.token_idx,
        },
        TransparentType::Comment => Node::Comment {
            raw: insert.raw.clone(),
            token_idx: insert.token_idx,
        },
        TransparentType::EndOfFile => Node::EndOfFile {
            raw: insert.raw.clone(),
            token_idx: insert.token_idx,
        },
    }
}

/// Convert a meta segment type to a Node
fn meta_to_node(idx: usize, meta_type: &MetaSegmentType) -> Node {
    match meta_type {
        MetaSegmentType::Indent => Node::Meta {
            token_type: "indent".to_string(),
            token_idx: Some(idx),
        },
        MetaSegmentType::Dedent => Node::Meta {
            token_type: "dedent".to_string(),
            token_idx: Some(idx),
        },
    }
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
