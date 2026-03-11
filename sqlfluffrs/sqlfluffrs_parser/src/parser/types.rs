//! Core types for the parser: Grammar, Node, ParseMode

use serde_yaml_ng::{Mapping, Value};
use sqlfluffrs_types::{GrammarId, PositionMarker};

/// Helper enum for tuple serialization, similar to Python's TupleSerialisedSegment.
#[derive(Debug, Clone, PartialEq)]
pub enum NodeTupleValue {
    Raw(String, String),
    Tuple(String, Vec<NodeTupleValue>),
}

/// Type of meta segment (from lexer or parser)
#[derive(Debug, Clone, PartialEq)]
pub enum MetaType {
    Indent {
        is_implicit: bool,
    },
    Dedent {
        is_implicit: bool,
    },
    Template {
        source_str: String,
        block_type: String,
    },
    TemplateLoop,
    EndOfFile,
}

/// Additional segment properties for Raw segments
#[derive(Debug, Clone, PartialEq, Default)]
pub struct RawSegmentKwargs {
    pub trim_chars: Option<Vec<String>>,
    pub quoted_value: Option<(String, String)>,
    pub escape_replacements: Option<Vec<(String, String)>>,
}

/// AST Node - represents parsed SQL structure
#[derive(Debug, Clone, PartialEq, Default)]
pub enum Node {
    /// Leaf: Raw token/segment from lexer (RawSegment, KeywordSegment, etc.)
    Raw {
        segment_class: String, // "KeywordSegment", "LiteralSegment"
        segment_type: String,  // "keyword", "literal", "whitespace"
        raw: String,           // Actual text
        pos_marker: Option<PositionMarker>,
        instance_types: Vec<String>, // ["keyword"], ["numeric_literal", "literal"]
        /// Full class type hierarchy (mirrors Python's ``class_types`` property).
        /// Includes ``instance_types`` ∪ ``raw_class._class_types`` so that
        /// ``is_type("symbol")`` works for ``binary_operator`` segments that
        /// descend from ``SymbolSegment``.
        class_types: Vec<String>,
        segment_kwargs: RawSegmentKwargs,
    },

    /// Container: Parsed segment with children (BaseSegment subclasses)
    Segment {
        segment_class: String,        // "SelectStatementSegment"
        segment_type: Option<String>, // "select_statement"
        pos_marker: Option<PositionMarker>,
        children: Vec<Node>,
    },

    /// Meta nodes (Indent, Dedent, Template markers, EOF)
    Meta {
        meta_type: MetaType,
        pos_marker: Option<PositionMarker>,
    },

    /// Parse errors
    Unparsable {
        expected: String,
        pos_marker: Option<PositionMarker>,
        children: Vec<Node>,
    },

    /// Empty placeholder
    #[default]
    Empty,
}

impl Node {
    /// Construct a ``Node::Raw`` with ``class_types`` automatically computed
    /// as ``instance_types ∪ {segment_type}``.
    ///
    /// Use this for nodes whose raw-class hierarchy isn't known (tests,
    /// synthetic helper nodes).  When the codegen-provided ``raw_class_
    /// class_types`` are available, call ``new_raw_with_class_types``
    /// instead.
    pub fn new_raw(
        segment_class: String,
        segment_type: String,
        raw: String,
        pos_marker: Option<PositionMarker>,
        instance_types: Vec<String>,
        segment_kwargs: RawSegmentKwargs,
    ) -> Self {
        let class_types = Self::build_class_types(&segment_type, &instance_types, &[]);
        Node::Raw {
            segment_class,
            segment_type,
            raw,
            pos_marker,
            instance_types,
            class_types,
            segment_kwargs,
        }
    }

    /// Construct a ``Node::Raw`` with explicit ``raw_class_class_types``
    /// (from codegen aux_data or Token.class_types).
    ///
    /// ``class_types`` is computed as
    /// ``instance_types ∪ {segment_type} ∪ raw_class_class_types``.
    pub fn new_raw_with_class_types(
        segment_class: String,
        segment_type: String,
        raw: String,
        pos_marker: Option<PositionMarker>,
        instance_types: Vec<String>,
        raw_class_class_types: &[String],
        segment_kwargs: RawSegmentKwargs,
    ) -> Self {
        let class_types =
            Self::build_class_types(&segment_type, &instance_types, raw_class_class_types);
        Node::Raw {
            segment_class,
            segment_type,
            raw,
            pos_marker,
            instance_types,
            class_types,
            segment_kwargs,
        }
    }

    /// Merge ``instance_types``, ``segment_type``, and ``raw_class_class_types``
    /// into a deduplicated ``class_types`` vector.
    fn build_class_types(
        segment_type: &str,
        instance_types: &[String],
        raw_class_class_types: &[String],
    ) -> Vec<String> {
        let mut ct: Vec<String> = Vec::with_capacity(
            instance_types.len() + raw_class_class_types.len() + 1,
        );
        ct.extend_from_slice(instance_types);
        if !ct.iter().any(|t| t == segment_type) {
            ct.push(segment_type.to_string());
        }
        for t in raw_class_class_types {
            if !ct.iter().any(|x| x == t) {
                ct.push(t.clone());
            }
        }
        ct
    }

    /// Get the raw text (no tokens parameter needed!)
    pub fn raw(&self) -> String {
        match self {
            Node::Raw { raw, .. } => raw.clone(),
            Node::Meta { .. } | Node::Empty => String::new(),
            Node::Segment { children, .. } | Node::Unparsable { children, .. } => {
                children.iter().map(|c| c.raw()).collect()
            }
        }
    }

    /// Get the semantic type
    pub fn segment_type(&self) -> Option<&str> {
        match self {
            Node::Raw { segment_type, .. } => Some(segment_type),
            Node::Segment { segment_type, .. } => segment_type.as_deref(),
            Node::Meta { .. } => Some("meta"),
            Node::Unparsable { .. } => Some("unparsable"),
            Node::Empty => None,
        }
    }

    /// Return a tuple structure from this node, similar to Python BaseSegment::to_tuple.
    /// This is useful for serialization to YAML/JSON and for parity with Python tests.
    pub fn to_tuple(&self, code_only: bool, show_raw: bool, include_meta: bool) -> NodeTupleValue {
        match self {
            Node::Raw {
                segment_type,
                raw,
                instance_types,
                ..
            } => {
                // Check if this is code
                let is_code = !instance_types
                    .iter()
                    .any(|t| matches!(t.as_str(), "whitespace" | "newline" | "comment"));

                // Filter in code_only mode (except comments which stay)
                if code_only && !is_code {
                    return NodeTupleValue::Tuple(segment_type.clone(), vec![]);
                }

                if show_raw {
                    NodeTupleValue::Raw(segment_type.clone(), raw.clone())
                } else {
                    NodeTupleValue::Tuple(segment_type.clone(), vec![])
                }
            }
            Node::Meta { meta_type, .. } => {
                let type_str = match meta_type {
                    MetaType::Indent { .. } => "indent",
                    MetaType::Dedent { .. } => "dedent",
                    MetaType::Template { .. } => "placeholder",
                    MetaType::TemplateLoop => "template_loop",
                    MetaType::EndOfFile => "end_of_file",
                };

                if include_meta {
                    NodeTupleValue::Raw(type_str.to_string(), String::new())
                } else {
                    NodeTupleValue::Tuple(type_str.to_string(), vec![])
                }
            }
            Node::Segment { children, .. } => {
                // Collect relevant children (respecting code_only and include_meta).
                let relevant_children: Vec<&Node> = children
                    .iter()
                    .filter(|c| {
                        if code_only && !c.is_code() {
                            return false;
                        }
                        if !include_meta && c.is_meta() {
                            return false;
                        }
                        true
                    })
                    .collect();

                // Special case: if the segment has exactly one child that is a Raw node
                // with the SAME segment_type as this Segment, treat this segment as a leaf.
                // This handles cases where a Segment wrapper still exists around a single
                // token of matching type (e.g. WordSegment wrapping word Raw node).
                //
                // We do NOT apply this when types differ (e.g. select_clause_element
                // wrapping numeric_literal) — that must remain nested to match Python output.
                if show_raw && relevant_children.len() == 1 {
                    if let Node::Raw {
                        raw,
                        segment_type: child_type,
                        ..
                    } = relevant_children[0]
                    {
                        if self.get_type() == *child_type {
                            return NodeTupleValue::Raw(self.get_type(), raw.clone());
                        }
                    }
                }

                // Normal case: tuple of all relevant children.
                let tupled = relevant_children
                    .iter()
                    .map(|c| c.to_tuple(code_only, show_raw, include_meta))
                    .collect();
                NodeTupleValue::Tuple(self.get_type(), tupled)
            }
            Node::Unparsable { children, .. } => {
                let mut tupled = vec![];
                for child in children {
                    if code_only && !child.is_code() {
                        continue;
                    }
                    let val = child.to_tuple(code_only, show_raw, include_meta);
                    tupled.push(val);
                }
                NodeTupleValue::Tuple("unparsable".to_string(), tupled)
            }
            Node::Empty => NodeTupleValue::Tuple("empty".to_string(), vec![]),
        }
    }

    /// Simplify the structure recursively so it serializes nicely in json/yaml.
    /// Mirrors Python's BaseSegment::structural_simplify.
    fn structural_simplify(elem: &NodeTupleValue) -> serde_yaml_ng::Value {
        match elem {
            NodeTupleValue::Raw(key, s) => {
                let mut map = Mapping::new();
                map.insert(Value::String(key.clone()), Value::String(s.clone()));
                Value::Mapping(map)
            }
            NodeTupleValue::Tuple(key, value) => {
                if value.is_empty() {
                    let mut map = Mapping::new();
                    map.insert(Value::String(key.clone()), Value::Null);
                    Value::Mapping(map)
                } else {
                    // Simplify all the child elements
                    let contents: Vec<Value> =
                        value.iter().map(Node::structural_simplify).collect();

                    // Any duplicate elements?
                    let mut subkeys = Vec::new();
                    for child in &contents {
                        if let Value::Mapping(m) = child {
                            for k in m.keys() {
                                subkeys.push(k.clone());
                            }
                        }
                    }
                    let unique_keys: std::collections::HashSet<_> =
                        subkeys.iter().cloned().collect();
                    let has_duplicates = unique_keys.len() != subkeys.len();
                    if has_duplicates {
                        // Yes: use a list of single dicts.
                        let mut map = Mapping::new();
                        map.insert(Value::String(key.clone()), Value::Sequence(contents));
                        Value::Mapping(map)
                    } else {
                        // Otherwise there aren't duplicates, un-nest the list into a dict:
                        let mut content_dict = Mapping::new();
                        for record in contents {
                            if let Value::Mapping(m) = record {
                                for (k, v) in m {
                                    content_dict.insert(k, v);
                                }
                            }
                        }
                        let mut map = Mapping::new();
                        map.insert(Value::String(key.clone()), Value::Mapping(content_dict));
                        Value::Mapping(map)
                    }
                }
            }
        }
    }

    /// Serialize the Node AST to a simplified record structure for YAML/JSON output.
    /// Mirrors Python's BaseSegment::as_record logic.
    pub fn as_record(
        &self,
        code_only: bool,
        show_raw: bool,
        include_meta: bool,
    ) -> Option<serde_yaml_ng::Value> {
        // Use to_tuple with the same configuration as Python's structural_simplify
        let tuple_val = self.to_tuple(code_only, show_raw, include_meta);

        // Apply structural_simplify equivalent
        let yaml_val = Node::structural_simplify(&tuple_val);

        Some(yaml_val)
    }

    pub fn is_empty(&self) -> bool {
        match &self {
            Node::Empty => true,
            Node::Segment { children, .. } | Node::Unparsable { children, .. } => {
                children.is_empty()
                    || children
                        .iter()
                        .all(|n| matches!(n, Node::Empty | Node::Meta { .. }))
            }
            _ => false,
        }
    }

    /// Check if this node represents code (not whitespace or meta)
    pub fn is_code(&self) -> bool {
        match self {
            Node::Meta { .. } | Node::Empty => false,
            Node::Raw {
                segment_type,
                instance_types,
                class_types,
                ..
            } => {
                // A node is non-code if any of its instance types or its
                // segment_type indicates whitespace or comment content.
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
                    || matches!(segment_type.as_str(), "whitespace" | "newline");
                // Also check class_types for "comment" — this covers non-standard
                // comment types like obevo_annotation, prompt_command, notebook_start
                // whose segment_type doesn't literally contain "comment" but whose
                // class_types hierarchy includes "comment" (from CommentSegment parent).
                let non_code_by_class = class_types.iter().any(|t| t == "comment");
                !(non_code_by_instance || non_code_by_type || non_code_by_class)
            }
            Node::Segment { children, .. } => children.iter().any(|c| c.is_code()),
            Node::Unparsable { .. } => true,
        }
    }

    /// Check if this node is whitespace (spaces, tabs, newlines)
    pub fn is_whitespace(&self) -> bool {
        match self {
            Node::Raw { instance_types, .. } => instance_types
                .iter()
                .any(|t| matches!(t.as_str(), "whitespace" | "newline")),
            _ => false,
        }
    }

    /// Check if this node is a meta node (indent, dedent, etc.)
    pub fn is_meta(&self) -> bool {
        matches!(self, Node::Meta { .. })
    }

    /// Check if this node should be included in code-only serialization
    /// This matches Python's behavior for `code_only=True`
    pub fn should_include_in_code_only(&self) -> bool {
        self.is_code() && !self.is_meta()
    }

    /// Get the type of this node based on its variant
    pub fn get_type(&self) -> String {
        match self {
            Node::Raw { segment_type, .. } => segment_type.clone(),
            Node::Segment { segment_type, .. } => segment_type.clone().unwrap_or_default(),
            Node::Meta { meta_type, .. } => match meta_type {
                MetaType::Indent { .. } => "indent".to_string(),
                MetaType::Dedent { .. } => "dedent".to_string(),
                MetaType::Template { .. } => "placeholder".to_string(),
                MetaType::TemplateLoop => "template_loop".to_string(),
                MetaType::EndOfFile => "end_of_file".to_string(),
            },
            Node::Unparsable { .. } => "unparsable".to_string(),
            Node::Empty => "empty".to_string(),
        }
    }

    /// Check if this node is of a specific type (including class_types for Raw nodes)
    pub fn is_type(&self, target: &str) -> bool {
        match self {
            Node::Raw {
                segment_type,
                class_types,
                ..
            } => segment_type == target || class_types.iter().any(|t| t == target),
            _ => self.get_type() == target,
        }
    }
}

#[derive(Debug, Clone)]
pub struct ParseError {
    pub message: String,
    pub pos: Option<usize>,
    pub grammar: Option<GrammarId>,
    pub children: Vec<ParseError>,
}

impl ParseError {
    pub fn new(message: String) -> Self {
        ParseError {
            message,
            pos: None,
            grammar: None,
            children: vec![],
        }
    }

    pub fn with_context(message: String, pos: Option<usize>, grammar: Option<GrammarId>) -> Self {
        ParseError {
            message,
            pos,
            grammar,
            children: vec![],
        }
    }

    pub fn with_child(mut self, child: ParseError) -> Self {
        self.children.push(child);
        self
    }

    pub fn with_children(mut self, children: Vec<ParseError>) -> Self {
        self.children.extend(children);
        self
    }

    pub fn unknown_segment(name: String, pos: Option<usize>) -> ParseError {
        ParseError {
            message: format!("Unknown segment: {}", name),
            pos,
            grammar: None,
            children: vec![],
        }
    }
}

pub enum ParseErrorType {
    EmptyInput,
    InvalidToken,
    UnexpectedEndOfInput,
    MismatchedParentheses,
    UnknownSegment,
}

#[cfg(test)]
mod tests {
    use super::*;

    use serde_yaml_ng::Value;

    #[test]
    fn test_segment_node_as_record_empty() {
        let node = Node::Segment {
            segment_class: "StatementSegment".to_string(),
            segment_type: Some("statement".to_string()),
            pos_marker: None,
            children: vec![],
        };
        let record = node.as_record(false, true, false).unwrap();
        let expected = Value::Mapping({
            let mut m = serde_yaml_ng::Mapping::new();
            m.insert(Value::String("statement".to_string()), Value::Null);
            m
        });
        assert_eq!(record, expected);
    }

    #[test]
    fn test_segment_node_as_record_merge() {
        let node = Node::Segment {
            segment_class: "StatementSegment".to_string(),
            segment_type: Some("statement".to_string()),
            pos_marker: None,
            children: vec![
                Node::new_raw(
                    "KeywordSegment".to_string(),
                    "keyword".to_string(),
                    "SELECT".to_string(),
                    None,
                    vec!["keyword".to_string()],
                    RawSegmentKwargs::default(),
                ),
                Node::new_raw(
                    "IdentifierSegment".to_string(),
                    "naked_identifier".to_string(),
                    "foo".to_string(),
                    None,
                    vec!["identifier".to_string()],
                    RawSegmentKwargs::default(),
                ),
            ],
        };
        let record = node.as_record(false, true, false).unwrap();
        let mut merged = serde_yaml_ng::Mapping::new();
        merged.insert(
            Value::String("keyword".to_string()),
            Value::String("SELECT".to_string()),
        );
        merged.insert(
            Value::String("naked_identifier".to_string()),
            Value::String("foo".to_string()),
        );
        let expected = Value::Mapping({
            let mut m = serde_yaml_ng::Mapping::new();
            m.insert(
                Value::String("statement".to_string()),
                Value::Mapping(merged),
            );
            m
        });
        assert_eq!(record, expected);
    }

    #[test]
    fn test_meta_node_as_record() {
        let node = Node::Meta {
            meta_type: MetaType::Indent { is_implicit: false },
            pos_marker: None,
        };
        let record = node.as_record(false, true, false).unwrap();
        let expected = Value::Mapping({
            let mut m = serde_yaml_ng::Mapping::new();
            m.insert(Value::String("indent".to_string()), Value::Null);
            m
        });
        assert_eq!(record, expected);
    }

    #[test]
    fn test_unparsable_node_as_record() {
        let node = Node::Unparsable {
            expected: "expected foo".to_string(),
            pos_marker: None,
            children: vec![
                Node::new_raw(
                    "KeywordSegment".to_string(),
                    "keyword".to_string(),
                    "SELECT".to_string(),
                    None,
                    vec!["keyword".to_string()],
                    RawSegmentKwargs::default(),
                ),
                Node::new_raw(
                    "IdentifierSegment".to_string(),
                    "naked_identifier".to_string(),
                    "foo".to_string(),
                    None,
                    vec!["identifier".to_string()],
                    RawSegmentKwargs::default(),
                ),
            ],
        };
        let record = node.as_record(false, true, false).unwrap();
        let mut expected_inner = serde_yaml_ng::Mapping::new();
        expected_inner.insert(
            Value::String("keyword".to_string()),
            Value::String("SELECT".to_string()),
        );
        expected_inner.insert(
            Value::String("naked_identifier".to_string()),
            Value::String("foo".to_string()),
        );
        let expected = Value::Mapping({
            let mut m = serde_yaml_ng::Mapping::new();
            m.insert(
                Value::String("unparsable".to_string()),
                Value::Mapping(expected_inner),
            );
            m
        });
        assert_eq!(record, expected);
    }

    #[test]
    fn test_raw_node_to_tuple_show_raw() {
        let node = Node::new_raw(
            "KeywordSegment".to_string(),
            "keyword".to_string(),
            "SELECT".to_string(),
            None,
            vec!["keyword".to_string()],
            RawSegmentKwargs::default(),
        );
        let val = node.to_tuple(false, true, false);
        assert_eq!(
            val,
            NodeTupleValue::Raw("keyword".to_string(), "SELECT".to_string())
        );
    }

    #[test]
    fn test_raw_node_to_tuple_no_raw() {
        let node = Node::new_raw(
            "KeywordSegment".to_string(),
            "keyword".to_string(),
            "SELECT".to_string(),
            None,
            vec!["keyword".to_string()],
            RawSegmentKwargs::default(),
        );
        let val = node.to_tuple(false, false, false);
        assert_eq!(val, NodeTupleValue::Tuple("keyword".to_string(), vec![]));
    }

    #[test]
    fn test_segment_node_to_tuple() {
        let child1 = Node::new_raw(
            "KeywordSegment".to_string(),
            "keyword".to_string(),
            "SELECT".to_string(),
            None,
            vec!["keyword".to_string()],
            RawSegmentKwargs::default(),
        );
        let child2 = Node::new_raw(
            "KeywordSegment".to_string(),
            "keyword".to_string(),
            "FROM".to_string(),
            None,
            vec!["keyword".to_string()],
            RawSegmentKwargs::default(),
        );
        let node = Node::Segment {
            segment_class: "StatementSegment".to_string(),
            segment_type: Some("statement".to_string()),
            pos_marker: None,
            children: vec![child1, child2],
        };
        let val = node.to_tuple(false, true, false);
        assert_eq!(
            val,
            NodeTupleValue::Tuple(
                "statement".to_string(),
                vec![
                    NodeTupleValue::Raw("keyword".to_string(), "SELECT".to_string()),
                    NodeTupleValue::Raw("keyword".to_string(), "FROM".to_string()),
                ]
            )
        );
    }

    #[test]
    fn test_meta_node_to_tuple_include_meta() {
        let node = Node::Meta {
            meta_type: MetaType::Indent { is_implicit: false },
            pos_marker: None,
        };
        let val = node.to_tuple(false, false, true);
        assert_eq!(
            val,
            NodeTupleValue::Raw("indent".to_string(), "".to_string())
        );
    }

    #[test]
    fn test_meta_node_to_tuple_exclude_meta() {
        let node = Node::Meta {
            meta_type: MetaType::Indent { is_implicit: false },
            pos_marker: None,
        };
        let val = node.to_tuple(false, false, false);
        assert_eq!(val, NodeTupleValue::Tuple("indent".to_string(), vec![]));
    }

    #[test]
    fn test_empty_node_to_tuple() {
        let node = Node::Empty;
        let val = node.to_tuple(false, false, false);
        assert_eq!(val, NodeTupleValue::Tuple("empty".to_string(), vec![]));
    }
}
