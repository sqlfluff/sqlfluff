//! MatchResult type for the parser.
//!
//! This module implements a Python-parity MatchResult approach where match operations
//! return a description of what matched (slices, classes, inserts) rather than
//! eagerly building the AST. The AST is built later via `apply()`.
//!
//! This eliminates the need for global state tracking of collected whitespace positions,
//! and makes the parser more functional and composable.

use crate::vdebug;
use std::fmt::Display;
use std::ops::Range;
use std::sync::Arc;

use crate::parser::types::{MetaType, Node, RawSegmentKwargs};
use hashbrown::HashMap;
use sqlfluffrs_types::regex::RegexModeGroup;
use sqlfluffrs_types::token::CaseFold;
use sqlfluffrs_types::{PositionMarker, Token};

/// Meta-segment types that can be inserted (like Python's Indent/Dedent)
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum MetaSegment {
    Indent { is_implicit: bool },
    Dedent { is_implicit: bool },
}

#[derive(Debug, Clone)]
pub struct SegmentKwargs {
    pub instance_types: Option<Vec<String>>,
    /// Class types inherited from the raw_class hierarchy (e.g. ``SymbolSegment``
    /// → ``["symbol", "raw", "base"]``).  Populated from codegen aux_data.
    pub raw_class_class_types: Option<Vec<String>>,
    pub trim_chars: Option<Vec<String>>,
    pub casefold: CaseFold,
    pub quoted_value: Option<(String, RegexModeGroup)>,
    pub escape_replacement: Option<(String, String)>,
    pub parse_error: Option<(String, usize)>,
}

impl Default for SegmentKwargs {
    fn default() -> Self {
        SegmentKwargs {
            instance_types: None,
            raw_class_class_types: None,
            trim_chars: None,
            casefold: CaseFold::None,
            quoted_value: None,
            escape_replacement: None,
            parse_error: None,
        }
    }
}

#[derive(Debug, Clone, Default)]
pub struct MatchedClass {
    pub class_name: String,
    pub segment_type: Option<String>,
    pub segment_kwargs: SegmentKwargs,
}

impl MatchedClass {
    pub fn root() -> Self {
        MatchedClass {
            class_name: "Root".to_string(),
            segment_type: Some("file".to_string()),
            segment_kwargs: SegmentKwargs::default(),
        }
    }

    pub fn unparsable(message: &str, error_pos: usize) -> Self {
        MatchedClass {
            class_name: "UnparsableSegment".to_string(),
            segment_type: Some("unparsable".to_string()),
            segment_kwargs: SegmentKwargs {
                parse_error: Some((message.to_string(), error_pos)),
                ..Default::default()
            },
        }
    }

    fn is_unparsable(&self) -> bool {
        self.class_name == "UnparsableSegment"
    }
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
    pub matched_class: Option<MatchedClass>,

    /// Meta-segments to insert at specific positions (Indent/Dedent)
    /// Tuple is (position, meta_type, is_implicit)
    pub insert_segments: Vec<(usize, MetaSegment)>,

    /// Child matches (recursive structure using Rc for cheap sharing)
    pub child_matches: Vec<Arc<MatchResult>>,
}

impl Default for MatchResult {
    fn default() -> Self {
        MatchResult {
            matched_slice: 0..0,
            matched_class: None,
            insert_segments: vec![],
            child_matches: vec![],
        }
    }
}

impl Display for MatchResult {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "Match ({:?}): {:?}, inserts={:?}, children={}",
            self.matched_class.as_ref().map(|c| &c.class_name),
            self.matched_slice,
            self.insert_segments,
            self.child_matches
                .iter()
                .map(|c| format!("\n  {}", c))
                .collect::<Vec<_>>()
                .join("")
        )
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

    /// Create a MatchResult for a Ref with child matches (lazy evaluation)
    pub fn ref_match(
        _name: String,
        matched_class: Option<MatchedClass>,
        start_idx: usize,
        end_idx: usize,
        children: Vec<Arc<MatchResult>>,
    ) -> Self {
        // Only set matched_class if segment_type is explicitly provided from tables
        // Refs without segment_type are grammar-only (not Python segment classes)
        // and should not create a matched_class wrapper

        // PYTHON PARITY: If we have a segment class AND a single grammar wrapper child
        // (matched_class=None with insert_segments), lift insert_segments to the parent
        // and unwrap the child's children. This matches Python's behavior where metas
        // are attached to the segment class, not intermediate grammar wrappers.
        // BUT: Only do this if the child doesn't contain an UnparsableSegment, because
        // unwrapping in that case can cause issues with segment boundaries.
        if matched_class.is_some() && children.len() == 1 {
            let child = &children[0];
            // Don't unwrap if the child contains an unparsable - keep structure intact
            if child.matched_class.is_none()
                && !child.insert_segments.is_empty()
                && !child.contains_unparsable()
            {
                // Try to move data out of the Arc instead of cloning
                let mut children = children;
                let child_arc = children.pop().unwrap();
                match Arc::try_unwrap(child_arc) {
                    Ok(owned) => {
                        return MatchResult {
                            matched_slice: start_idx..end_idx,
                            matched_class,
                            child_matches: owned.child_matches,
                            insert_segments: owned.insert_segments,
                        };
                    }
                    Err(shared) => {
                        return MatchResult {
                            matched_slice: start_idx..end_idx,
                            matched_class,
                            child_matches: shared.child_matches.clone(),
                            insert_segments: shared.insert_segments.clone(),
                        };
                    }
                }
            }
        }

        MatchResult {
            matched_slice: start_idx..end_idx,
            matched_class,
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
        // Python code:
        //   insert_segments=(
        //       (start_match.matched_slice.stop, Indent),
        //       (end_match.matched_slice.start, Dedent),
        //   )
        let mut insert_segments = Vec::new();
        if let Some(first_child) = children.first() {
            // Indent after opening bracket
            let indent_pos = first_child.matched_slice.end;
            insert_segments.push((indent_pos, MetaSegment::Indent { is_implicit: false }));
        }
        if let Some(last_child) = children.last() {
            // Dedent before closing bracket
            let dedent_pos = last_child.matched_slice.start;
            insert_segments.push((dedent_pos, MetaSegment::Dedent { is_implicit: false }));
        }

        // Python parity: When bracket_persists is false (e.g., square/curly brackets),
        // don't wrap in BracketedSegment - just return the match with children inline.
        // When bracket_persists is true (parentheses), wrap in BracketedSegment.
        let matched_class = if bracket_persists {
            Some(MatchedClass {
                class_name: "BracketedSegment".to_string(),
                segment_type: Some("bracketed".to_string()),
                segment_kwargs: SegmentKwargs::default(),
            })
        } else {
            None
        };

        MatchResult {
            matched_slice: start_idx..end_idx,
            matched_class,
            child_matches: children,
            insert_segments,
        }
    }

    /// Create a MatchResult representing a parse error.
    /// Used when parsing fails and we need to report the error location.
    pub fn with_error(start_idx: usize, end_idx: usize, message: String, error_pos: usize) -> Self {
        let matched_class = Some(MatchedClass::unparsable(&message, error_pos));
        MatchResult {
            matched_slice: start_idx..end_idx,
            matched_class,
            ..Default::default()
        }
    }

    /// Check if this match is empty (no tokens matched and no inserts)
    pub fn is_empty(&self) -> bool {
        self.matched_slice.is_empty()
            && self.insert_segments.is_empty()
            && self.child_matches.is_empty()
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
        if let Some(ref class) = self.matched_class {
            if class.is_unparsable() {
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
    pub fn append(self: Arc<Self>, other: Arc<MatchResult>) -> Arc<MatchResult> {
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
        let mut child_matches = vec![];

        // Process both matches — use try_unwrap to move data when refcount==1
        // instead of cloning. This is critical for the delimited handler's repeated
        // append pattern: avoids O(n²) child copies over N elements.
        for m in [self, other] {
            if m.matched_class.is_some() {
                // Has a class, add as child match
                child_matches.push(m);
            } else {
                // No class, flatten into parent
                match Arc::try_unwrap(m) {
                    Ok(owned) => {
                        // Refcount was 1 — move data out, no cloning
                        insert_segments.extend(owned.insert_segments);
                        child_matches.extend(owned.child_matches);
                    }
                    Err(shared) => {
                        // Shared — must clone
                        insert_segments.extend(shared.insert_segments.iter().cloned());
                        child_matches.extend(shared.child_matches.iter().cloned());
                    }
                }
            }
        }

        Arc::new(MatchResult {
            matched_slice: new_slice,
            matched_class: None,
            insert_segments,
            child_matches,
        })
    }

    /// In-place append: swaps out the current Arc, giving `append()` sole ownership
    /// so that `Arc::try_unwrap` succeeds and data is moved instead of cloned.
    /// This avoids the O(n²) repeated-clone problem in the old `x = x.clone().append(y)` pattern.
    #[inline]
    pub fn append_into(target: &mut Arc<MatchResult>, other: Arc<MatchResult>) {
        // Swap a temporary empty Arc into the field, giving us sole ownership of the old value.
        let old = std::mem::replace(target, Arc::new(MatchResult::empty_at(0)));
        *target = old.append(other);
    }

    /// Wrap this result with an outer segment class.
    ///
    /// If the match is empty, returns it unchanged (can't wrap empty).
    pub fn wrap(
        self,
        outer_class: MatchedClass,
        insert_segments: Vec<(usize, MetaSegment)>,
    ) -> MatchResult {
        if self.is_empty() {
            if insert_segments.is_empty() {
                return self;
            }
            panic!("Cannot wrap inserts onto an empty MatchResult.");
        }

        if self.matched_class.is_some() {
            // Already has a class — wrap self as a child.
            // Extract matched_slice before moving self into Arc.
            let matched_slice = self.matched_slice.clone();
            MatchResult {
                matched_slice,
                matched_class: Some(outer_class),
                insert_segments,
                child_matches: vec![Arc::new(self)],
            }
        } else {
            // No current class, flatten children into new wrapper.
            // Move fields out of self instead of cloning.
            let mut new_insert_segments = self.insert_segments;
            new_insert_segments.extend(insert_segments);
            MatchResult {
                matched_slice: self.matched_slice,
                matched_class: Some(outer_class),
                insert_segments: new_insert_segments,
                child_matches: self.child_matches,
            }
        }
    }

    /// Apply this match to tokens to create actual AST nodes.
    ///
    /// This is where materialization happens - converting the match description
    /// into the actual nested Node structure.
    pub fn apply(self, tokens: &[Token]) -> Vec<Node> {
        // DEBUG: Log apply() entry for all named segments
        #[cfg(feature = "verbose-debug")]
        if let Some(ref class) = self.matched_class {
            vdebug!(
                "[APPLY-ENTRY] {:?}: matched_slice={:?}, child_matches={}, insert_segments={}",
                class.class_name,
                self.matched_slice,
                self.child_matches.len(),
                self.insert_segments.len(),
            );
        }

        let mut result = vec![];

        // If empty, return Empty node
        if self.matched_slice.is_empty() {
            if let Some(matched_class) = self.matched_class {
                panic!("Tried to apply zero-length MatchResult with matched_class. This MatchResult is invalid. {:?} @{:?}", matched_class, self.matched_slice);
            }
            if !self.child_matches.is_empty() {
                panic!("Tried to apply zero-length MatchResult with child_matches. This MatchResult is invalid. Result: @{:?}", self);
            }
            // Only meta/transparent inserts - create them as children
            for (idx, meta_type) in &self.insert_segments {
                let pos_marker = get_point_pos_at_token_idx(tokens, *idx);
                result.push(meta_to_node(meta_type, pos_marker));
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

        // Add child matches — store Arc directly, avoid deep clone
        for child_rc in &self.child_matches {
            trigger_map
                .entry(child_rc.matched_slice.start)
                .or_default()
                .push(TriggerItem::ChildMatch(Arc::clone(child_rc)));
        }

        // Walk through the slice, processing triggers at each position
        let mut result_nodes: Vec<Node> = vec![];
        let mut current_idx = self.matched_slice.start;

        // Get sorted trigger positions
        let mut positions: Vec<usize> = trigger_map.keys().copied().collect();
        positions.sort();

        for pos in positions {
            // PYTHON PARITY: Fill gap with all tokens between child matches.
            // Meta tokens become Node::Meta, non-meta become Node::Raw.
            // This matches Python's `result_segments += segments[max_idx:idx]`
            // which includes ALL segments (including meta) in gap-fill.
            if pos > current_idx {
                for idx in current_idx..pos {
                    if idx < tokens.len() {
                        result_nodes.push(token_to_node(&tokens[idx]));
                    }
                }
                current_idx = pos;
            } else if pos < current_idx {
                panic!(
                    "Trigger position {} is before current_idx {}",
                    pos, current_idx
                );
            }

            // Process triggers at this position — remove from map to take ownership
            if let Some(triggers) = trigger_map.remove(&pos) {
                for trigger in triggers {
                    match trigger {
                        TriggerItem::Meta(meta_type) => {
                            let pos_marker = get_point_pos_at_token_idx(tokens, pos);
                            result_nodes.push(meta_to_node(&meta_type, pos_marker));
                        }
                        TriggerItem::ChildMatch(child_arc) => {
                            let end = child_arc.matched_slice.end;
                            // try_unwrap avoids a deep clone when refcount==1
                            let child_owned =
                                Arc::try_unwrap(child_arc).unwrap_or_else(|arc| (*arc).clone());
                            let child_node = child_owned.apply(tokens);
                            // Only add non-empty nodes
                            result_nodes.extend(child_node);
                            current_idx = end;
                        }
                    }
                }
            }
        }

        // PYTHON PARITY: If we finish processing triggers and there are still tokens
        // left in the matched_slice, add them too (captures trailing whitespace/comments).
        // Include ALL tokens (meta and non-meta) to match Python's gap-fill behavior.
        if current_idx < self.matched_slice.end {
            for idx in current_idx..self.matched_slice.end {
                if idx < tokens.len() {
                    result_nodes.push(token_to_node(&tokens[idx]));
                }
            }
        }

        // self is owned — consume matched_class directly without clone
        if let Some(match_class) = self.matched_class {
            vdebug!(
                "[APPLY-DEBUG] {:?} wrapping {} nodes",
                match_class.class_name,
                result_nodes.len()
            );

            // PYTHON PARITY: Base parser matches (String/Typed/MultiString)
            // produce a RawSegment with parser-provided instance_types.
            // In Rust, those arrive as a single-token match with no child
            // matches/inserts. Retag the raw node directly rather than wrapping
            // it in a synthetic Segment node.
            //
            // This path fires for ALL single-token base parser matches (no
            // hardcoded allowlist) so that every parser-assigned type gets
            // correct class_types from the codegen-provided raw_class hierarchy.
            if self.child_matches.is_empty()
                && self.insert_segments.is_empty()
                && self.matched_slice.end == self.matched_slice.start + 1
                && result_nodes.len() == 1
                && !match_class.is_unparsable()
                && match_class.segment_type.is_some()
            {
                if let Some(Node::Raw {
                    raw, pos_marker, ..
                }) = result_nodes.pop()
                {
                    let mut instance_types = match_class
                        .segment_kwargs
                        .instance_types
                        .unwrap_or_default();
                    if instance_types.is_empty() {
                        if let Some(seg_type) = &match_class.segment_type {
                            instance_types.push(seg_type.clone());
                        }
                    }

                    let effective_segment_type = match_class
                        .segment_type
                        .clone()
                        .or_else(|| instance_types.first().cloned())
                        .unwrap_or_else(|| "raw".to_string());

                    let raw_class_ct = match_class
                        .segment_kwargs
                        .raw_class_class_types
                        .unwrap_or_default();

                    let quoted_value =
                        match_class
                            .segment_kwargs
                            .quoted_value
                            .map(|(pattern, group)| {
                                let group_str = match group {
                                    RegexModeGroup::Index(idx) => idx.to_string(),
                                    RegexModeGroup::Name(name) => name,
                                };
                                (pattern, group_str)
                            });
                    let escape_replacements = match_class
                        .segment_kwargs
                        .escape_replacement
                        .map(|(pattern, replacement)| vec![(pattern, replacement)]);

                    return vec![Node::new_raw_with_class_types(
                        match_class.class_name,
                        effective_segment_type,
                        raw,
                        pos_marker,
                        instance_types,
                        &raw_class_ct,
                        RawSegmentKwargs {
                            trim_chars: match_class.segment_kwargs.trim_chars,
                            quoted_value,
                            escape_replacements,
                        },
                    )];
                }
            }

            // Calculate position marker from first child
            let pos_marker = result_nodes.first().and_then(|n| match n {
                Node::Raw { pos_marker, .. }
                | Node::Segment { pos_marker, .. }
                | Node::Meta { pos_marker, .. }
                | Node::Unparsable { pos_marker, .. } => pos_marker.clone(),
                _ => None,
            });

            // Create Segment node — move class_name/segment_type without clone
            vec![Node::Segment {
                segment_class: match_class.class_name,
                segment_type: match_class.segment_type,
                pos_marker,
                children: result_nodes,
            }]
        } else {
            // No wrapping class - return children as-is
            result_nodes
        }
    }

    /// Build a root `Node::Segment` (FileSegment) from this match result,
    /// optionally prepending `leading` and appending `trailing` non-code
    /// tokens as direct children of the root.
    ///
    /// This is the single entry-point for constructing the Rust AST node
    /// that is attached to the Python segment tree for Rust-side linting.
    ///
    /// * `tokens` — the code-only token slice that match indices refer to.
    /// * `leading` — non-code tokens before the first code token (e.g.
    ///   leading whitespace/newlines).  Pass `&[]` when there are none.
    /// * `trailing` — non-code tokens after the last code token (e.g.
    ///   trailing newline + end_of_file).  Pass `&[]` when there are none.
    pub fn apply_as_root(self, tokens: &[Token], leading: &[Token], trailing: &[Token]) -> Node {
        let file_mr = MatchResult {
            matched_slice: 0..tokens.len(),
            matched_class: Some(MatchedClass::root()),
            insert_segments: vec![],
            child_matches: vec![Arc::new(self)],
        };
        let root_node = file_mr.apply(tokens);
        if root_node.len() > 1 {
            panic!(
                "Root apply did not produce a single node, got {} nodes",
                root_node.len()
            );
        }
        let mut root = root_node.first().cloned().unwrap_or_default();

        // Prepend leading and append trailing token-derived children.
        if let Node::Segment { children, .. } = &mut root {
            if !trailing.is_empty() {
                children.extend(trailing.iter().map(token_to_node));
            }
            if !leading.is_empty() {
                let leading_nodes: Vec<Node> = leading.iter().map(token_to_node).collect();
                let mut new_children = leading_nodes;
                new_children.extend(children.drain(..));
                *children = new_children;
            }
        }

        root
    }

    pub fn stringify(&self, indent: usize) -> String {
        let indent_str = "  ".repeat(indent);
        let mut s = format!(
            "Match ({:?}): {:?}\n  {}-{:?}\n",
            self.matched_class.as_ref().map(|c| &c.class_name),
            self.matched_slice,
            indent_str,
            self.matched_class.as_ref().map(|c| &c.segment_kwargs)
        );
        for (idx, meta) in &self.insert_segments {
            s.push_str(&format!("  {}+{}: {:?}\n", indent_str, idx, meta));
        }
        for child in &self.child_matches {
            s.push_str(&format!("  {}+{}", indent_str, child.stringify(indent + 1)));
        }
        s
    }
}

/// Build a `SegmentKwargs` from a lexer `Token` and an instance token type.
/// This centralizes token-to-segment kwargs mapping used by table-driven parsers.
pub fn segment_kwargs_from_token(
    tok: &Token,
    token_type: &str,
    instance_types: Option<Vec<String>>,
    casefold: Option<CaseFold>,
) -> SegmentKwargs {
    SegmentKwargs {
        instance_types: instance_types.or_else(|| Some(vec![token_type.to_string()])),
        casefold: casefold.unwrap_or_else(|| tok.casefold.clone()),
        trim_chars: tok.trim_chars.clone(),
        escape_replacement: tok.escape_replacement().cloned(),
        quoted_value: tok.quoted_value().cloned(),
        ..Default::default()
    }
}

/// Internal enum for tracking what to process at each position
#[derive(Debug)]
enum TriggerItem {
    Meta(MetaSegment),
    ChildMatch(Arc<MatchResult>),
}

/// Get a point position marker at a given token index.
/// Mirrors Python's `_get_point_pos_at_idx`:
/// - If `idx < tokens.len()`: use the start point of `tokens[idx]`
/// - Otherwise: use the end point of `tokens[idx - 1]`
fn get_point_pos_at_token_idx(tokens: &[Token], idx: usize) -> Option<PositionMarker> {
    if idx < tokens.len() {
        tokens[idx]
            .pos_marker
            .as_ref()
            .map(|pm| pm.start_point_marker())
    } else if idx > 0 {
        tokens[idx - 1]
            .pos_marker
            .as_ref()
            .map(|pm| pm.end_point_marker())
    } else {
        None
    }
}

/// Convert a single Token into a Node suitable for use as a trailing child.
///
/// Meta tokens (is_meta=true) become `Node::Meta` using the token_type to
/// determine the variant.  All other tokens become `Node::Raw`.
fn token_to_node(tok: &Token) -> Node {
    if tok.is_meta {
        let meta_type = match tok.token_type.as_str() {
            "end_of_file" => MetaType::EndOfFile,
            "indent" => MetaType::Indent { is_implicit: false },
            "dedent" => MetaType::Dedent { is_implicit: false },
            "template_loop" => MetaType::TemplateLoop,
            _ => MetaType::Template {
                source_str: tok.raw(),
                block_type: tok.block_type().expect("block_type for template"),
            },
        };
        Node::Meta {
            meta_type,
            pos_marker: tok.pos_marker.clone(),
        }
    } else {
        // Populate class_types from the Token's own class_types (from lexer)
        // + instance_types.  This mirrors Python's RawSegment.class_types
        // property which is frozenset(instance_types) | super().class_types.
        let raw_class_ct: Vec<String> = tok.class_types.iter().cloned().collect();
        // PYTHON PARITY: RawSegment.get_type() returns instance_types[0] if
        // instance_types is set, otherwise falls back to the class `type` attr.
        // In Rust, tok.token_type holds the class-level type (e.g. "raw") while
        // tok.instance_types holds the per-instance override (e.g. ["double_quote"]).
        // Use instance_types[0] as the segment_type to match Python's behavior.
        let segment_type = tok
            .instance_types
            .first()
            .cloned()
            .unwrap_or_else(|| tok.token_type.clone());
        Node::new_raw_with_class_types(
            tok.class_name.clone(),
            segment_type,
            tok.raw.to_string(),
            tok.pos_marker.clone(),
            tok.instance_types.clone(),
            &raw_class_ct,
            RawSegmentKwargs::default(),
        )
    }
}

/// Convert a meta segment type to a Node with an optional position marker.
fn meta_to_node(meta_type: &MetaSegment, pos_marker: Option<PositionMarker>) -> Node {
    match meta_type {
        MetaSegment::Indent { is_implicit } => Node::Meta {
            meta_type: MetaType::Indent {
                is_implicit: *is_implicit,
            },
            pos_marker,
        },
        MetaSegment::Dedent { is_implicit } => Node::Meta {
            meta_type: MetaType::Dedent {
                is_implicit: *is_implicit,
            },
            pos_marker,
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
