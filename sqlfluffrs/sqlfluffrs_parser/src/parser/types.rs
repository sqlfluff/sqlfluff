//! Core types for the parser: Grammar, Node, ParseMode

use std::default;

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
                let mut tupled = vec![];
                for child in children {
                    if code_only && !child.is_code() {
                        continue;
                    }
                    let val = child.to_tuple(code_only, show_raw, include_meta);
                    tupled.push(val);
                }
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

    // /// Format the AST to mirror Python SQLFluff's parse output format.
    // pub fn format_tree(&self, tokens: &[Token]) -> String {
    //     let mut output = String::new();
    //     let mut eof_nodes = Vec::new();

    //     self.format_tree_impl(tokens, &mut output, 0, 0, &mut eof_nodes);

    //     // Print all EndOfFile nodes at the very end
    //     for (depth, idx) in eof_nodes {
    //         let indent = "    ".repeat(depth);
    //         if let Some(token) = tokens.get(idx) {
    //             if let Some(pos_marker) = &token.pos_marker {
    //                 let (line, pos) = pos_marker.source_position();
    //                 output.push_str(&format!(
    //                     "[L:{:3}, P:{:3}]      |{}[META] end_of_file:\n",
    //                     line, pos, indent,
    //                 ));
    //             }
    //         }
    //     }

    //     output
    // }

    // fn format_tree_impl(
    //     &self,
    //     tokens: &[Token],
    //     output: &mut String,
    //     depth: usize,
    //     token_idx: usize,
    //     eof_nodes: &mut Vec<(usize, usize)>,
    // ) -> usize {
    //     let indent = "    ".repeat(depth);

    //     match self {
    //         Node::Whitespace {
    //             raw: _,
    //             token_idx: idx,
    //         }
    //         | Node::Newline {
    //             raw: _,
    //             token_idx: idx,
    //         }
    //         | Node::Comment {
    //             raw: _,
    //             token_idx: idx,
    //         }
    //         | Node::Token { token_idx: idx, .. } => {
    //             if let Some(token) = tokens.get(*idx) {
    //                 output.push_str(&token.stringify(depth, 4, false));
    //             }
    //             *idx + 1
    //         }

    //         Node::EndOfFile {
    //             raw: _,
    //             token_idx: idx,
    //         } => {
    //             eof_nodes.push((depth, *idx));
    //             *idx + 1
    //         }

    //         Node::Unparsable {
    //             expected_message: expected,
    //             children,
    //         } => {
    //             output.push_str(&format!("{}[unparsable] expected: {}\n", indent, expected));
    //             let mut last_idx = token_idx;
    //             for child in children {
    //                 last_idx =
    //                     child.format_tree_impl(tokens, output, depth + 1, last_idx, eof_nodes);
    //             }
    //             last_idx
    //         }

    //         Node::Meta {
    //             token_type: name, ..
    //         } => {
    //             let (line, pos) = if let Some(token) = tokens.get(token_idx) {
    //                 if let Some(pos_marker) = &token.pos_marker {
    //                     pos_marker.source_position()
    //                 } else {
    //                     (0, 0)
    //                 }
    //             } else if token_idx > 0 && token_idx <= tokens.len() {
    //                 if let Some(token) = tokens.get(token_idx - 1) {
    //                     if let Some(pos_marker) = &token.pos_marker {
    //                         let (start_line, start_pos) = pos_marker.source_position();
    //                         let token_len = token.raw().len();
    //                         (start_line, start_pos + token_len)
    //                     } else {
    //                         (0, 0)
    //                     }
    //                 } else {
    //                     (0, 0)
    //                 }
    //             } else {
    //                 (0, 0)
    //             };

    //             output.push_str(&format!(
    //                 "[L:{:3}, P:{:3}]      |{}[META] {}:\n",
    //                 line, pos, indent, name,
    //             ));
    //             token_idx
    //         }

    //         Node::Ref {
    //             name,
    //             segment_type,
    //             children: child,
    //         } => {
    //             let is_grammar_rule = name.ends_with("Grammar");
    //             let is_single_token = matches!(
    //                 child.as_ref(),
    //                 Node::Whitespace { .. } | Node::Newline { .. } | Node::EndOfFile { .. }
    //             );
    //             let is_transparent = is_grammar_rule || is_single_token;

    //             let mut current_idx = token_idx;

    //             if is_transparent {
    //                 current_idx =
    //                     child.format_tree_impl(tokens, output, depth, current_idx, eof_nodes);
    //             } else {
    //                 let display_name = if let Some(ref seg_type) = segment_type {
    //                     seg_type.clone()
    //                 } else {
    //                     simplify_segment_name(name)
    //                 };

    //                 if let Some(first_token_idx) = self.find_first_token_idx() {
    //                     if let Some(token) = tokens.get(first_token_idx) {
    //                         if let Some(pos_marker) = &token.pos_marker {
    //                             let (line, pos) = pos_marker.source_position();
    //                             output.push_str(&format!(
    //                                 "[L:{:3}, P:{:3}]      |{}{}:\n",
    //                                 line, pos, indent, display_name
    //                             ));
    //                         }
    //                     }
    //                 }

    //                 current_idx =
    //                     child.format_tree_impl(tokens, output, depth + 1, current_idx, eof_nodes);
    //             }
    //             current_idx
    //         }

    //         Node::Sequence { children }
    //         | Node::DelimitedList { children }
    //         | Node::Bracketed { children, .. } => {
    //             let mut current_idx = token_idx;
    //             let mut eof_indices = Vec::new();

    //             for (i, child) in children.iter().enumerate() {
    //                 if matches!(
    //                     child,
    //                     Node::EndOfFile {
    //                         raw: _,
    //                         token_idx: _
    //                     }
    //                 ) {
    //                     eof_indices.push(i);
    //                 } else if !child.is_empty() {
    //                     current_idx =
    //                         child.format_tree_impl(tokens, output, depth, current_idx, eof_nodes);
    //                 }
    //             }

    //             for &i in &eof_indices {
    //                 current_idx =
    //                     children[i].format_tree_impl(tokens, output, depth, current_idx, eof_nodes);
    //             }

    //             current_idx
    //         }
    //         Node::Empty => token_idx,
    //     }
    // }

    // fn find_first_token_idx(&self) -> Option<usize> {
    //     match self {
    //         Node::Ref {
    //             children: child, ..
    //         } => child.find_first_token_idx(),

    //         Node::Sequence { children }
    //         | Node::DelimitedList { children }
    //         | Node::Bracketed { children, .. }
    //         | Node::Unparsable {
    //             expected_message: _,
    //             children,
    //         } => children.iter().find_map(|c| c.find_first_token_idx()),

    //         _ => self.get_token_idx(),
    //     }
    // }

    /// Check if this node represents code (not whitespace or meta)
    pub fn is_code(&self) -> bool {
        match self {
            Node::Meta { .. } | Node::Empty => false,
            Node::Raw { instance_types, .. } => !instance_types
                .iter()
                .any(|t| matches!(t.as_str(), "whitespace" | "newline" | "comment")),
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

    /// Check if this node is of a specific type (including instance_types for Raw nodes)
    pub fn is_type(&self, target: &str) -> bool {
        match self {
            Node::Raw {
                segment_type,
                instance_types,
                ..
            } => segment_type == target || instance_types.iter().any(|t| t == target),
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
                Node::Raw {
                    segment_class: "KeywordSegment".to_string(),
                    segment_type: "keyword".to_string(),
                    raw: "SELECT".to_string(),
                    pos_marker: None,
                    instance_types: vec!["keyword".to_string()],
                    segment_kwargs: RawSegmentKwargs::default(),
                },
                Node::Raw {
                    segment_class: "IdentifierSegment".to_string(),
                    segment_type: "naked_identifier".to_string(),
                    raw: "foo".to_string(),
                    pos_marker: None,
                    instance_types: vec!["identifier".to_string()],
                    segment_kwargs: RawSegmentKwargs::default(),
                },
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
                Node::Raw {
                    segment_class: "KeywordSegment".to_string(),
                    segment_type: "keyword".to_string(),
                    raw: "SELECT".to_string(),
                    pos_marker: None,
                    instance_types: vec!["keyword".to_string()],
                    segment_kwargs: RawSegmentKwargs::default(),
                },
                Node::Raw {
                    segment_class: "IdentifierSegment".to_string(),
                    segment_type: "naked_identifier".to_string(),
                    raw: "foo".to_string(),
                    pos_marker: None,
                    instance_types: vec!["identifier".to_string()],
                    segment_kwargs: RawSegmentKwargs::default(),
                },
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
        let node = Node::Raw {
            segment_class: "KeywordSegment".to_string(),
            segment_type: "keyword".to_string(),
            raw: "SELECT".to_string(),
            pos_marker: None,
            instance_types: vec!["keyword".to_string()],
            segment_kwargs: RawSegmentKwargs::default(),
        };
        let val = node.to_tuple(false, true, false);
        assert_eq!(
            val,
            NodeTupleValue::Raw("keyword".to_string(), "SELECT".to_string())
        );
    }

    #[test]
    fn test_raw_node_to_tuple_no_raw() {
        let node = Node::Raw {
            segment_class: "KeywordSegment".to_string(),
            segment_type: "keyword".to_string(),
            raw: "SELECT".to_string(),
            pos_marker: None,
            instance_types: vec!["keyword".to_string()],
            segment_kwargs: RawSegmentKwargs::default(),
        };
        let val = node.to_tuple(false, false, false);
        assert_eq!(val, NodeTupleValue::Tuple("keyword".to_string(), vec![]));
    }

    #[test]
    fn test_segment_node_to_tuple() {
        let child1 = Node::Raw {
            segment_class: "KeywordSegment".to_string(),
            segment_type: "keyword".to_string(),
            raw: "SELECT".to_string(),
            pos_marker: None,
            instance_types: vec!["keyword".to_string()],
            segment_kwargs: RawSegmentKwargs::default(),
        };
        let child2 = Node::Raw {
            segment_class: "KeywordSegment".to_string(),
            segment_type: "keyword".to_string(),
            raw: "FROM".to_string(),
            pos_marker: None,
            instance_types: vec!["keyword".to_string()],
            segment_kwargs: RawSegmentKwargs::default(),
        };
        let node = Node::Segment {
            segment_class: "StatementSegment".to_string(),
            segment_type: "statement".to_string(),
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
