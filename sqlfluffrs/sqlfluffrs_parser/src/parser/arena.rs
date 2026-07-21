//! Mutable, id-addressable arena tree for Rust-side linting & fixing.
//!
//! Today the Rust parser produces an immutable [`Node`] tree (see
//! [`super::types`]) which Python materialises into a pure-Python
//! `BaseSegment` tree where all linting and fixing happens.  The arena here is
//! the foundation for moving that work onto the Rust side: it is a flattened,
//! parent-linked tree addressed by stable [`NodeId`]s, so navigation
//! (`recursive_crawl`, `path_to`, ancestor walks) and — in later milestones —
//! edits become cheap, and Python only ever holds lightweight handles
//! (`(tree, node_id)`) rather than cloned subtrees.
//!
//! ## Milestone 1 scope (read-only navigation)
//!
//! This module currently implements ingest-from-[`Node`] plus the read-only
//! navigation/accessor surface that the Python rule API depends on.  uuids are
//! minted at ingest time (sufficient for read-only linting); threading a stable
//! uuid through `apply_as_root` is deferred to the fixing milestone where
//! cross-reingest identity matters for `LintFix` anchoring.

// Milestone 1 scaffolding: `ArenaKind`, `PathStep`, `Arena::from_node`, `Arena::path_to`,
// and their construction helpers aren't wired up outside this module's own tests yet
// (see module docs above).
#![allow(dead_code)]

use std::borrow::Cow;
use std::cell::RefCell;
use std::sync::Arc;

use hashbrown::{HashMap, HashSet};
use sqlfluffrs_types::PositionMarker;

use super::types::{MetaType, Node, RawSegmentKwargs};

/// Stable, arena-local identity for a node.  A plain index for milestone 1
/// (read-only); generational keys will be introduced alongside deletion in the
/// fixing milestone so that stale ids fail loudly instead of aliasing.
#[derive(Copy, Clone, PartialEq, Eq, Hash, Debug)]
pub struct NodeId(u32);

impl NodeId {
    #[inline]
    fn idx(self) -> usize {
        self.0 as usize
    }
}

/// The payload of an arena node, mirroring the variants of [`Node`] but without
/// owned children (children live in [`ArenaNode::children`] as ids).
#[derive(Debug, Clone, PartialEq)]
enum ArenaKind {
    Raw {
        segment_class: Cow<'static, str>,
        segment_type: Cow<'static, str>,
        raw: String,
        instance_types: Vec<String>,
        class_types: Vec<String>,
        kwargs: RawSegmentKwargs,
    },
    Segment {
        segment_class: Cow<'static, str>,
        segment_type: Option<Cow<'static, str>>,
        class_types: Vec<String>,
    },
    Meta {
        meta_type: MetaType,
    },
    Unparsable {
        expected: String,
    },
    Empty,
}

/// A single node in the arena: payload, structural links, position, and lazily
/// computed caches.
struct ArenaNode {
    uuid: u128,
    parent: Option<NodeId>,
    parent_idx: usize,
    children: Vec<NodeId>,
    pos_marker: Option<PositionMarker>,
    kind: ArenaKind,
    /// Cached joined raw for containers (mirrors `BaseSegment.raw`).  Reset on
    /// any structural mutation of this node or its descendants.
    cached_raw: RefCell<Option<String>>,
    /// Cached `descendant_type_set` (mirrors `BaseSegment.descendant_type_set`),
    /// used by the crawler to prune subtrees.
    descendant_types: RefCell<Option<Arc<HashSet<String>>>>,
}

/// A flattened, parent-linked, id-addressable parse tree.
pub struct Arena {
    nodes: Vec<ArenaNode>,
    root: NodeId,
    by_uuid: HashMap<u128, NodeId>,
}

/// A single step on a path between two nodes — mirrors Python's `PathStep`
/// dataclass (`segment`, `idx`, `len`, `code_idxs`).
#[derive(Debug, Clone, PartialEq)]
pub(crate) struct PathStep {
    pub(crate) node: NodeId,
    pub(crate) idx: usize,
    pub(crate) len: usize,
    pub(crate) code_idxs: Vec<usize>,
}

impl Arena {
    // -- construction --------------------------------------------------------

    /// Build an arena from an existing [`Node`] tree.
    pub(crate) fn from_node(node: &Node) -> Self {
        let mut arena = Arena {
            nodes: Vec::new(),
            root: NodeId(0),
            by_uuid: HashMap::new(),
        };
        let root = arena.ingest(node, None, 0);
        arena.root = root;
        arena
    }

    fn next_uuid(&self) -> u128 {
        // Random v4 uuid, mirroring Python's `uuid4().int` identity semantics.
        uuid::Uuid::new_v4().as_u128()
    }

    fn alloc(
        &mut self,
        kind: ArenaKind,
        pos_marker: Option<PositionMarker>,
        parent: Option<NodeId>,
        parent_idx: usize,
    ) -> NodeId {
        let id = NodeId(self.nodes.len() as u32);
        let uuid = self.next_uuid();
        self.nodes.push(ArenaNode {
            uuid,
            parent,
            parent_idx,
            children: Vec::new(),
            pos_marker,
            kind,
            cached_raw: RefCell::new(None),
            descendant_types: RefCell::new(None),
        });
        self.by_uuid.insert(uuid, id);
        id
    }

    fn ingest(&mut self, node: &Node, parent: Option<NodeId>, parent_idx: usize) -> NodeId {
        match node {
            Node::Raw {
                segment_class,
                segment_type,
                raw,
                pos_marker,
                instance_types,
                class_types,
                segment_kwargs,
            } => self.alloc(
                ArenaKind::Raw {
                    segment_class: segment_class.clone(),
                    segment_type: segment_type.clone(),
                    raw: raw.clone(),
                    instance_types: instance_types.clone(),
                    class_types: class_types.clone(),
                    kwargs: segment_kwargs.clone(),
                },
                pos_marker.clone(),
                parent,
                parent_idx,
            ),
            Node::Segment {
                segment_class,
                segment_type,
                pos_marker,
                class_types,
                children,
            } => {
                let id = self.alloc(
                    ArenaKind::Segment {
                        segment_class: segment_class.clone(),
                        segment_type: segment_type.clone(),
                        class_types: class_types.clone(),
                    },
                    pos_marker.clone(),
                    parent,
                    parent_idx,
                );
                let child_ids: Vec<NodeId> = children
                    .iter()
                    .enumerate()
                    .map(|(i, c)| self.ingest(c, Some(id), i))
                    .collect();
                self.nodes[id.idx()].children = child_ids;
                id
            }
            Node::Unparsable {
                expected,
                pos_marker,
                children,
            } => {
                let id = self.alloc(
                    ArenaKind::Unparsable {
                        expected: expected.clone(),
                    },
                    pos_marker.clone(),
                    parent,
                    parent_idx,
                );
                let child_ids: Vec<NodeId> = children
                    .iter()
                    .enumerate()
                    .map(|(i, c)| self.ingest(c, Some(id), i))
                    .collect();
                self.nodes[id.idx()].children = child_ids;
                id
            }
            Node::Meta {
                meta_type,
                pos_marker,
            } => self.alloc(
                ArenaKind::Meta {
                    meta_type: meta_type.clone(),
                },
                pos_marker.clone(),
                parent,
                parent_idx,
            ),
            Node::Empty => self.alloc(ArenaKind::Empty, None, parent, parent_idx),
        }
    }

    // -- basic access --------------------------------------------------------

    #[inline]
    pub fn root(&self) -> NodeId {
        self.root
    }

    #[inline]
    fn node(&self, id: NodeId) -> &ArenaNode {
        &self.nodes[id.idx()]
    }

    #[inline]
    pub fn len(&self) -> usize {
        self.nodes.len()
    }

    // Companion to `len()` for the accessor surface; not yet wired up on the
    // Python side (the façade will use it), so allow it to be unused for now.
    #[inline]
    #[allow(dead_code)]
    pub fn is_empty(&self) -> bool {
        self.nodes.is_empty()
    }

    pub fn node_by_uuid(&self, uuid: u128) -> Option<NodeId> {
        self.by_uuid.get(&uuid).copied()
    }

    #[inline]
    pub fn children(&self, id: NodeId) -> &[NodeId] {
        &self.nodes[id.idx()].children
    }

    #[inline]
    pub fn parent(&self, id: NodeId) -> Option<NodeId> {
        self.nodes[id.idx()].parent
    }

    #[inline]
    pub fn uuid(&self, id: NodeId) -> u128 {
        self.nodes[id.idx()].uuid
    }

    #[inline]
    pub fn pos_marker(&self, id: NodeId) -> Option<PositionMarker> {
        self.nodes[id.idx()].pos_marker.clone()
    }

    // -- payload accessors (mirror Node / BaseSegment) -----------------------

    /// Joined raw text (cached for containers).
    pub fn raw(&self, id: NodeId) -> String {
        let n = self.node(id);
        match &n.kind {
            ArenaKind::Raw { raw, .. } => raw.clone(),
            ArenaKind::Meta { .. } | ArenaKind::Empty => String::new(),
            ArenaKind::Segment { .. } | ArenaKind::Unparsable { .. } => {
                if let Some(cached) = n.cached_raw.borrow().as_ref() {
                    return cached.clone();
                }
                let mut s = String::new();
                for &c in &n.children {
                    s.push_str(&self.raw(c));
                }
                *n.cached_raw.borrow_mut() = Some(s.clone());
                s
            }
        }
    }

    pub fn raw_upper(&self, id: NodeId) -> String {
        self.raw(id).to_uppercase()
    }

    /// Semantic type string (mirrors [`Node::get_type`]).
    pub fn get_type(&self, id: NodeId) -> String {
        match &self.node(id).kind {
            ArenaKind::Raw { segment_type, .. } => segment_type.to_string(),
            ArenaKind::Segment { segment_type, .. } => {
                segment_type.as_deref().unwrap_or_default().to_string()
            }
            ArenaKind::Meta { meta_type } => meta_type_str(meta_type).to_string(),
            ArenaKind::Unparsable { .. } => "unparsable".to_string(),
            ArenaKind::Empty => "empty".to_string(),
        }
    }

    /// The structural class types every node of a given kind carries, mirroring
    /// the Python `RawSegment`/`MetaSegment`/`BaseSegment` class hierarchy
    /// (which always contributes `raw`/`base`/`meta` to `_class_types`).  These
    /// are deterministic by node kind, unlike the dialect-specific raw-class
    /// ancestors (e.g. `word` for `KeywordSegment`) which come from the parser's
    /// codegen data.
    fn structural_types(&self, id: NodeId) -> &'static [&'static str] {
        match &self.node(id).kind {
            ArenaKind::Raw { .. } => &["raw", "base"],
            ArenaKind::Segment { .. } => &["base"],
            // Python's `Dedent` subclasses `Indent`, so a dedent node carries
            // `indent` in its `_class_types` in addition to `dedent`.  Metas are
            // parser-inserted (not token-matched), so this core hierarchy isn't
            // in the grammar tables and must be encoded here.
            ArenaKind::Meta {
                meta_type: MetaType::Dedent { .. },
            } => &["dedent", "indent", "meta", "raw", "base"],
            ArenaKind::Meta { .. } => &["meta", "raw", "base"],
            ArenaKind::Unparsable { .. } => &["unparsable", "base"],
            ArenaKind::Empty => &[],
        }
    }

    /// Mirrors [`Node::is_type`], plus the structural hierarchy types.
    pub fn is_type(&self, id: NodeId, target: &str) -> bool {
        if self.structural_types(id).contains(&target) {
            return true;
        }
        match &self.node(id).kind {
            ArenaKind::Raw {
                segment_type,
                class_types,
                ..
            } => segment_type.as_ref() == target || class_types.iter().any(|t| t == target),
            ArenaKind::Segment {
                segment_type,
                class_types,
                ..
            } => segment_type.as_deref() == Some(target) || class_types.iter().any(|t| t == target),
            _ => self.get_type(id) == target,
        }
    }

    pub fn is_any_type(&self, id: NodeId, targets: &[String]) -> bool {
        targets.iter().any(|t| self.is_type(id, t))
    }

    /// The set of types this node "is" — `class_types`, the semantic type, and
    /// the structural hierarchy types.
    fn node_type_set(&self, id: NodeId) -> Vec<String> {
        let mut out: Vec<String> = match &self.node(id).kind {
            ArenaKind::Raw { class_types, .. } => class_types.clone(),
            ArenaKind::Segment { class_types, .. } => class_types.clone(),
            _ => Vec::new(),
        };
        let push_unique = |out: &mut Vec<String>, t: String| {
            if !out.iter().any(|x| x == &t) {
                out.push(t);
            }
        };
        push_unique(&mut out, self.get_type(id));
        for t in self.structural_types(id) {
            push_unique(&mut out, t.to_string());
        }
        out
    }

    pub fn class_types(&self, id: NodeId) -> Vec<String> {
        self.node_type_set(id)
    }

    pub fn instance_types(&self, id: NodeId) -> Vec<String> {
        match &self.node(id).kind {
            ArenaKind::Raw { instance_types, .. } => instance_types.clone(),
            _ => Vec::new(),
        }
    }

    pub fn segment_class(&self, id: NodeId) -> Option<String> {
        match &self.node(id).kind {
            ArenaKind::Raw { segment_class, .. } | ArenaKind::Segment { segment_class, .. } => {
                Some(segment_class.to_string())
            }
            _ => None,
        }
    }

    /// `is_implicit` flag for Indent/Dedent meta nodes (`None` for non-metas).
    pub fn is_implicit(&self, id: NodeId) -> Option<bool> {
        match &self.node(id).kind {
            ArenaKind::Meta {
                meta_type: MetaType::Indent { is_implicit } | MetaType::Dedent { is_implicit },
            } => Some(*is_implicit),
            _ => None,
        }
    }

    /// Characters to trim from both ends of a raw token (if set on the token).
    pub fn trim_chars(&self, id: NodeId) -> Option<Vec<String>> {
        match &self.node(id).kind {
            ArenaKind::Raw { kwargs, .. } => kwargs.trim_chars.clone(),
            _ => None,
        }
    }

    /// The `(pattern, group)` quote-extraction spec for a quoted raw token.
    pub fn quoted_value(&self, id: NodeId) -> Option<(String, String)> {
        match &self.node(id).kind {
            ArenaKind::Raw { kwargs, .. } => kwargs.quoted_value.clone(),
            _ => None,
        }
    }

    /// The escape `(pattern, replacement)` pairs for a raw token.
    pub fn escape_replacements(&self, id: NodeId) -> Option<Vec<(String, String)>> {
        match &self.node(id).kind {
            ArenaKind::Raw { kwargs, .. } => kwargs.escape_replacements.as_deref().cloned(),
            _ => None,
        }
    }

    pub fn is_raw(&self, id: NodeId) -> bool {
        // Mirrors `BaseSegment.is_raw` (`len(self.segments) == 0`): any leaf,
        // including meta segments (which are RawSegment subclasses in Python).
        self.children(id).is_empty()
    }

    pub fn is_meta(&self, id: NodeId) -> bool {
        matches!(self.node(id).kind, ArenaKind::Meta { .. })
    }

    /// Mirrors [`Node::is_code`].
    pub fn is_code(&self, id: NodeId) -> bool {
        match &self.node(id).kind {
            ArenaKind::Meta { .. } | ArenaKind::Empty => false,
            ArenaKind::Raw {
                segment_type,
                instance_types,
                class_types,
                ..
            } => {
                let non_code_by_instance = instance_types.iter().any(|t| {
                    matches!(
                        t.as_str(),
                        "whitespace"
                            | "newline"
                            | "comment"
                            | "inline_comment"
                            | "block_comment"
                            | "trailing_newline"
                    )
                });
                let non_code_by_type = segment_type.contains("comment")
                    || matches!(segment_type.as_ref(), "whitespace" | "newline");
                let non_code_by_class = class_types.iter().any(|t| t == "comment");
                !(non_code_by_instance || non_code_by_type || non_code_by_class)
            }
            ArenaKind::Segment { .. } => self.children(id).iter().any(|&c| self.is_code(c)),
            ArenaKind::Unparsable { .. } => true,
        }
    }

    pub fn is_whitespace(&self, id: NodeId) -> bool {
        match &self.node(id).kind {
            ArenaKind::Raw { instance_types, .. } => instance_types
                .iter()
                .any(|t| matches!(t.as_str(), "whitespace" | "newline")),
            ArenaKind::Segment { .. } | ArenaKind::Unparsable { .. } => {
                let kids = self.children(id);
                !kids.is_empty() && kids.iter().all(|&c| self.is_whitespace(c))
            }
            _ => false,
        }
    }

    pub fn is_comment(&self, id: NodeId) -> bool {
        match &self.node(id).kind {
            ArenaKind::Raw {
                segment_type,
                class_types,
                ..
            } => segment_type.contains("comment") || class_types.iter().any(|t| t == "comment"),
            ArenaKind::Segment { .. } | ArenaKind::Unparsable { .. } => {
                let kids = self.children(id);
                !kids.is_empty() && kids.iter().all(|&c| self.is_comment(c))
            }
            _ => false,
        }
    }

    /// Whether any descendant raw carries templated source (best-effort mirror
    /// of `BaseSegment.is_templated`: a non-literal, non-point source slice).
    pub fn is_templated(&self, id: NodeId) -> bool {
        match self.node(id).pos_marker.as_ref() {
            Some(pm) => !pm.is_literal() && !pm.is_point(),
            None => false,
        }
    }

    // -- navigation ----------------------------------------------------------

    /// First child matching any of `seg_type` (mirrors `get_child`).
    pub fn get_child(&self, id: NodeId, seg_type: &[String]) -> Option<NodeId> {
        self.children(id)
            .iter()
            .copied()
            .find(|&c| self.is_any_type(c, seg_type))
    }

    /// All children matching any of `seg_type` (mirrors `get_children`).
    pub fn get_children(&self, id: NodeId, seg_type: &[String]) -> Vec<NodeId> {
        self.children(id)
            .iter()
            .copied()
            .filter(|&c| self.is_any_type(c, seg_type))
            .collect()
    }

    /// Depth-first leaf nodes (mirrors `raw_segments` / `get_raw_segments`).
    pub fn raw_segments(&self, id: NodeId) -> Vec<NodeId> {
        let mut out = Vec::new();
        self.collect_raw_segments(id, &mut out);
        out
    }

    fn collect_raw_segments(&self, id: NodeId, out: &mut Vec<NodeId>) {
        let kids = self.children(id);
        if kids.is_empty() {
            // Leaf: Raw, Meta, Empty, or empty container all count as a "raw".
            out.push(id);
        } else {
            for &c in kids {
                self.collect_raw_segments(c, out);
            }
        }
    }

    /// Mirrors `BaseSegment.recursive_crawl`.  `no_recursive_seg_type` stops
    /// recursion (but the stopping node is still yielded if it matches).
    pub fn recursive_crawl(
        &self,
        id: NodeId,
        seg_type: &[String],
        recurse_into: bool,
        no_recursive_seg_type: &[String],
        allow_self: bool,
    ) -> Vec<NodeId> {
        let mut out = Vec::new();
        self.recursive_crawl_into(
            id,
            seg_type,
            recurse_into,
            no_recursive_seg_type,
            allow_self,
            &mut out,
        );
        out
    }

    fn recursive_crawl_into(
        &self,
        id: NodeId,
        seg_type: &[String],
        recurse_into: bool,
        no_recursive_seg_type: &[String],
        allow_self: bool,
        out: &mut Vec<NodeId>,
    ) {
        let matches = allow_self && self.is_any_type(id, seg_type);
        if matches {
            out.push(id);
        }
        // Early-exit if no target type is reachable below here (mirrors Python's
        // `descendant_type_set.intersection(seg_type)` check on *self*).
        let dts = self.descendant_type_set(id);
        if !seg_type.iter().any(|t| dts.contains(t)) {
            return;
        }
        if recurse_into || !matches {
            for &c in self.children(id) {
                // `no_recursive_seg_type` is applied to each CHILD before
                // recursing into it — never to `self` — so that crawling *from*
                // a node of a no_recursive type (e.g. a `with_compound_statement`
                // when excluding nested ones) still inspects its children.
                if no_recursive_seg_type.is_empty() || !self.is_any_type(c, no_recursive_seg_type) {
                    self.recursive_crawl_into(
                        c,
                        seg_type,
                        recurse_into,
                        no_recursive_seg_type,
                        true,
                        out,
                    );
                }
            }
        }
    }

    /// All descendants in document order (mirrors `recursive_crawl_all`).
    pub fn recursive_crawl_all(&self, id: NodeId) -> Vec<NodeId> {
        let mut out = Vec::new();
        self.crawl_all_into(id, &mut out);
        out
    }

    fn crawl_all_into(&self, id: NodeId, out: &mut Vec<NodeId>) {
        out.push(id);
        for &c in self.children(id) {
            self.crawl_all_into(c, out);
        }
    }

    /// Mirrors `BaseSegment.descendant_type_set` — the union over direct
    /// children of `(child.class_types ∪ child.descendant_type_set)`.
    pub fn descendant_type_set(&self, id: NodeId) -> Arc<HashSet<String>> {
        if let Some(cached) = self.node(id).descendant_types.borrow().as_ref() {
            return cached.clone();
        }
        let mut set: HashSet<String> = HashSet::new();
        for &c in self.children(id) {
            for t in self.node_type_set(c) {
                set.insert(t);
            }
            for t in self.descendant_type_set(c).iter() {
                set.insert(t.clone());
            }
        }
        let rc = Arc::new(set);
        *self.node(id).descendant_types.borrow_mut() = Some(rc.clone());
        rc
    }

    /// Parent and the index of `id` within it (mirrors `get_parent`).
    pub fn get_parent(&self, id: NodeId) -> Option<(NodeId, usize)> {
        self.parent(id).map(|p| (p, self.node(id).parent_idx))
    }

    /// Path from `self` (an ancestor) down to `other`.  Returns the steps from
    /// `self` toward `other` (mirroring the common ancestor->descendant use of
    /// `BaseSegment.path_to`).  Empty if `self` is not an ancestor of `other`.
    pub(crate) fn path_to(&self, from: NodeId, to: NodeId) -> Vec<PathStep> {
        // Walk up from `to` collecting ancestors until we reach `from`.
        let mut chain: Vec<NodeId> = Vec::new();
        let mut cur = to;
        while cur != from {
            chain.push(cur);
            match self.parent(cur) {
                Some(p) => cur = p,
                None => return Vec::new(), // `from` is not an ancestor of `to`
            }
        }
        // chain is [to, ..., child_of_from]; reverse to top-down order.
        chain.reverse();
        let mut steps = Vec::with_capacity(chain.len());
        let mut parent = from;
        for node in chain {
            let idx = self.node(node).parent_idx;
            let siblings = self.children(parent);
            let code_idxs: Vec<usize> = siblings
                .iter()
                .enumerate()
                .filter(|(_, &s)| self.is_code(s))
                .map(|(i, _)| i)
                .collect();
            steps.push(PathStep {
                node: parent,
                idx,
                len: siblings.len(),
                code_idxs,
            });
            parent = node;
        }
        steps
    }
}

fn meta_type_str(meta_type: &MetaType) -> &'static str {
    match meta_type {
        MetaType::Indent { .. } => "indent",
        MetaType::Dedent { .. } => "dedent",
        MetaType::Template { .. } => "placeholder",
        MetaType::TemplateLoop => "template_loop",
        MetaType::EndOfFile => "end_of_file",
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser::types::RawSegmentKwargs;

    fn raw(class: &str, ty: &str, text: &str, instance: &[&str]) -> Node {
        Node::new_raw(
            class.to_string(),
            ty.to_string(),
            text.to_string(),
            None,
            instance.iter().map(|s| s.to_string()).collect(),
            RawSegmentKwargs::default(),
        )
    }

    fn select_tree() -> Node {
        // statement( select_statement( keyword "SELECT", ws " ", column_reference( naked_identifier "a" ) ) )
        let kw = raw("KeywordSegment", "keyword", "SELECT", &["keyword"]);
        let ws = raw("WhitespaceSegment", "whitespace", " ", &["whitespace"]);
        let ident = raw(
            "IdentifierSegment",
            "naked_identifier",
            "a",
            &["identifier"],
        );
        let col = Node::Segment {
            segment_class: "ColumnReferenceSegment".into(),
            segment_type: Some("column_reference".into()),
            pos_marker: None,
            class_types: vec!["column_reference".to_string()],
            children: vec![ident],
        };
        let select = Node::Segment {
            segment_class: "SelectStatementSegment".into(),
            segment_type: Some("select_statement".into()),
            pos_marker: None,
            class_types: vec!["select_statement".to_string(), "statement".to_string()],
            children: vec![kw, ws, col],
        };
        Node::Segment {
            segment_class: "StatementSegment".into(),
            segment_type: Some("statement".into()),
            pos_marker: None,
            class_types: vec!["statement".to_string()],
            children: vec![select],
        }
    }

    #[test]
    fn raw_matches_node() {
        let node = select_tree();
        let arena = Arena::from_node(&node);
        assert_eq!(arena.raw(arena.root()), node.raw());
        assert_eq!(arena.raw(arena.root()), "SELECT a");
    }

    #[test]
    fn is_type_uses_class_types() {
        let arena = Arena::from_node(&select_tree());
        let root = arena.root();
        // statement node
        assert!(arena.is_type(root, "statement"));
        // select_statement child is also a "statement" via class_types
        let select = arena.children(root)[0];
        assert!(arena.is_type(select, "select_statement"));
        assert!(arena.is_type(select, "statement"));
        assert!(!arena.is_type(select, "keyword"));
    }

    #[test]
    fn recursive_crawl_finds_descendants() {
        let arena = Arena::from_node(&select_tree());
        let kws = arena.recursive_crawl(arena.root(), &["keyword".to_string()], true, &[], true);
        assert_eq!(kws.len(), 1);
        assert_eq!(arena.raw(kws[0]), "SELECT");

        let idents = arena.recursive_crawl(
            arena.root(),
            &["naked_identifier".to_string()],
            true,
            &[],
            true,
        );
        assert_eq!(idents.len(), 1);
        assert_eq!(arena.raw(idents[0]), "a");
    }

    #[test]
    fn raw_segments_in_order() {
        let arena = Arena::from_node(&select_tree());
        let raws = arena.raw_segments(arena.root());
        let texts: Vec<String> = raws.iter().map(|&r| arena.raw(r)).collect();
        assert_eq!(texts, vec!["SELECT", " ", "a"]);
    }

    #[test]
    fn parent_links_and_path() {
        let arena = Arena::from_node(&select_tree());
        let root = arena.root();
        let raws = arena.raw_segments(root);
        let ident = *raws.last().unwrap();
        // path from root down to the identifier
        let steps = arena.path_to(root, ident);
        assert!(!steps.is_empty());
        // first step is at the root, last step's parent is the column_reference
        assert_eq!(steps[0].node, root);
        // get_parent of identifier should be the column_reference
        let (p, idx) = arena.get_parent(ident).unwrap();
        assert_eq!(arena.get_type(p), "column_reference");
        assert_eq!(idx, 0);
    }

    #[test]
    fn descendant_type_set_includes_nested() {
        let arena = Arena::from_node(&select_tree());
        let dts = arena.descendant_type_set(arena.root());
        assert!(dts.contains("keyword"));
        assert!(dts.contains("naked_identifier"));
        assert!(dts.contains("select_statement"));
    }

    #[test]
    fn is_code_and_whitespace() {
        let arena = Arena::from_node(&select_tree());
        let raws = arena.raw_segments(arena.root());
        // SELECT is code, " " is whitespace
        assert!(arena.is_code(raws[0]));
        assert!(!arena.is_code(raws[1]));
        assert!(arena.is_whitespace(raws[1]));
    }

    #[test]
    fn get_child_includes_meta() {
        // Mirror `BaseSegment.get_child`/`get_children`, which consider *all*
        // children including metas: a query for `indent` must return the meta.
        let tree = Node::Segment {
            segment_class: "SelectStatementSegment".into(),
            segment_type: Some("select_statement".into()),
            pos_marker: None,
            class_types: vec!["select_statement".to_string()],
            children: vec![
                raw("KeywordSegment", "keyword", "SELECT", &["keyword"]),
                Node::Meta {
                    meta_type: MetaType::Indent { is_implicit: false },
                    pos_marker: None,
                },
                raw("WhitespaceSegment", "whitespace", " ", &["whitespace"]),
            ],
        };
        let arena = Arena::from_node(&tree);
        let root = arena.root();
        let indent = vec!["indent".to_string()];
        let child = arena.get_child(root, &indent).expect("indent meta found");
        assert!(arena.is_meta(child));
        assert_eq!(arena.get_type(child), "indent");
        assert_eq!(arena.get_children(root, &indent).len(), 1);
        // A non-meta query still works alongside metas.
        assert!(arena.get_child(root, &["keyword".to_string()]).is_some());
    }
}
