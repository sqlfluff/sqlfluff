//! Core types for the parser: Grammar, Node, ParseMode

use std::collections::HashSet;

use serde_yaml_ng::{Mapping, Value};
use sqlfluffrs_types::{GrammarId, Token};

/// Helper enum for tuple serialization, similar to Python's TupleSerialisedSegment.
#[derive(Debug, Clone, PartialEq)]
pub enum NodeTupleValue {
    Raw(String, String),
    Tuple(String, Vec<NodeTupleValue>),
}

#[derive(Debug, Clone, PartialEq)]
pub enum Node {
    /// Generic token
    /// - token: The token object from the lexer
    /// - instance_types: The instance types for this token from the parser
    Raw {
        token: Token,
        instance_types: Vec<String>,
    },

    /// Unparsable segment (in GREEDY mode when tokens don't match)
    Unparsable {
        expected_message: String,
        children: Vec<Node>,
    }, // (expected message, children)

    /// A sequence of child nodes (used for Sequence grammars)
    Sequence { children: Vec<Node> },

    /// A list of elements separated by commas
    #[deprecated(note = "Use Sequence instead")]
    DelimitedList { children: Vec<Node> },

    /// A bracketed section (content between brackets)
    /// bracket_persists: if true, output as "bracketed:" wrapper in YAML
    ///                   if false, output children inline (for square/curly brackets)
    Bracketed {
        children: Vec<Node>,
        bracket_persists: bool,
    },

    /// A reference to another segment (wraps its AST)
    /// - name: The grammar/segment name from the dialect (e.g., "SelectStatementSegment" or "SelectableGrammar")
    /// - segment_type: The segment's type attribute (e.g., "select_statement")
    /// - segment_class: The segment's class name (e.g., "SelectStatementSegment")
    /// - child: The wrapped AST node
    Ref {
        name: String,
        segment_type: Option<String>,
        segment_class: Option<String>,
        child: Box<Node>,
    },

    /// Used when an optional part didn't match
    Empty,
}

impl Node {
    /// Create a Token node.
    ///
    /// Python will map token_type to the appropriate segment class via
    /// the segment_types dictionary.
    #[deprecated(note = "Use from_token instead")]
    pub fn new_token(token_type: String, raw: String, token_idx: usize) -> Self {
        panic!("Use from_token instead");
    }

    pub fn from_token(token: Token) -> Self {
        Self::from_token_types(token, vec![])
    }

    pub fn from_token_types(token: Token, instance_types: Vec<String>) -> Self {
        Node::Raw {
            token,
            instance_types,
        }
    }

    /// Create a Ref node.
    pub fn new_ref(
        name: String,
        segment_type: Option<String>,
        segment_class: Option<String>,
        child: Node,
    ) -> Self {
        Node::Ref {
            name,
            segment_type,
            segment_class,
            child: Box::new(child),
        }
    }

    /// Return a tuple structure from this node, similar to Python BaseSegment::to_tuple.
    /// This is useful for serialization to YAML/JSON and for parity with Python tests.
    pub fn to_tuple(&self, code_only: bool, show_raw: bool, include_meta: bool) -> NodeTupleValue {
        match self {
            Node::Raw {
                token,
                instance_types,
                ..
            } => {
                // Use token.token_type (semantic type) for tuple output
                if show_raw {
                    NodeTupleValue::Raw(token.token_type.clone(), token.raw.clone())
                } else {
                    NodeTupleValue::Tuple(token.token_type.clone(), vec![])
                }
            }
            Node::Raw {
                token,
                instance_types,
                ..
            } if token.is_whitespace() => {
                // These are filtered in code_only mode (except comments which stay)
                if code_only {
                    NodeTupleValue::Tuple(token.token_type.clone(), vec![])
                } else {
                    NodeTupleValue::Raw(token.token_type.clone(), token.raw.to_string())
                }
            }
            // Node::Meta {
            //     token,
            //     instance_types,
            //     ..
            // } => {
            //     if include_meta {
            //         NodeTupleValue::Raw(token.token_type.clone(), "".to_string())
            //     } else {
            //         NodeTupleValue::Tuple(token.token_type.clone(), vec![])
            //     }
            // }
            Node::Ref {
                segment_type,
                child,
                ..
            } => {
                // Recursively flatten only 'sequence' nodes
                fn flatten_sequence(node: NodeTupleValue) -> NodeTupleValue {
                    match node {
                        NodeTupleValue::Tuple(t, v) if t == "sequence" => {
                            let mut flat = Vec::new();
                            for c in v {
                                match flatten_sequence(c) {
                                    NodeTupleValue::Tuple(inner_t, inner_v)
                                        if inner_t == "sequence" =>
                                    {
                                        flat.extend(inner_v);
                                    }
                                    other => flat.push(other),
                                }
                            }
                            NodeTupleValue::Tuple("sequence".to_string(), flat)
                        }
                        other => other,
                    }
                }

                let child_node =
                    flatten_sequence(child.to_tuple(code_only, show_raw, include_meta));
                if let Some(ref_type) = segment_type {
                    match &child_node {
                        NodeTupleValue::Raw(t, s) if t == "sequence" => {
                            NodeTupleValue::Raw(ref_type.clone(), s.clone())
                        }
                        NodeTupleValue::Tuple(t, v) if t == "sequence" => {
                            NodeTupleValue::Tuple(ref_type.clone(), v.to_vec())
                        }
                        _ => NodeTupleValue::Tuple(ref_type.clone(), vec![child_node]),
                    }
                } else {
                    child_node
                }
            }
            Node::Sequence { children } | Node::DelimitedList { children } => {
                let mut tupled = vec![];
                for child in children {
                    if code_only && !child.is_code() {
                        continue;
                    }
                    let val = child.to_tuple(code_only, show_raw, include_meta);
                    tupled.push(val);
                }
                NodeTupleValue::Tuple("sequence".to_string(), tupled)
            }
            Node::Bracketed {
                children,
                bracket_persists,
            } => {
                // Use the same flatten_sequence logic as in Ref
                fn flatten_sequence(node: NodeTupleValue) -> Vec<NodeTupleValue> {
                    match node {
                        NodeTupleValue::Tuple(t, v) if t == "sequence" => {
                            let mut flat = Vec::new();
                            for c in v {
                                for item in flatten_sequence(c) {
                                    match item {
                                        NodeTupleValue::Tuple(inner_t, inner_v)
                                            if inner_t == "sequence" =>
                                        {
                                            flat.extend(inner_v);
                                        }
                                        other => flat.push(other),
                                    }
                                }
                            }
                            flat
                        }
                        other => vec![other],
                    }
                }

                let mut tupled = vec![];
                for child in children {
                    if code_only && !child.is_code() {
                        continue;
                    }
                    let val = flatten_sequence(child.to_tuple(code_only, show_raw, include_meta));
                    tupled.extend(val);
                }

                // Python parity: If bracket_persists is false (square/curly brackets),
                // output as "sequence" instead of "bracketed" so children are inlined
                let tuple_type = if *bracket_persists {
                    "bracketed".to_string()
                } else {
                    log::debug!("Bracketed with bracket_persists=false, returning as sequence");
                    "sequence".to_string()
                };
                NodeTupleValue::Tuple(tuple_type, tupled)
            }
            Node::Unparsable {
                expected_message: _,
                children,
            } => {
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
            Node::DelimitedList { children: items }
            | Node::Sequence { children: items }
            | Node::Bracketed {
                children: items, ..
            } => items.is_empty() || items.iter().all(|n| matches!(n, Node::Empty)),
            _ => false,
        }
    }

    /// Get the token index from this node if it's a Token/Whitespace/Newline/EndOfFile.
    /// Returns None for complex nodes like Sequence, Ref, etc.
    #[deprecated(note = "To remove")]
    pub fn get_token_idx(&self) -> Option<usize> {
        panic!("don't use get_token_idx!");
        // match self {
        //     Node::Token { token, .. } => token.pos_marker.as_ref().map(|pm| pm.start_index),
        //     _ => None,
        // }
    }

    /// Check if this node represents code (not whitespace or meta)
    pub fn is_code(&self) -> bool {
        match self {
            // Empty is not code
            Node::Empty => false,

            // Raw: check `is_code`
            Node::Raw { token, .. } => token.is_code(),

            // Unparsable segments contain code
            Node::Unparsable { .. } => true,

            // Container nodes: check if they contain any code
            Node::Sequence { children }
            | Node::DelimitedList { children }
            | Node::Bracketed { children, .. } => children.iter().any(|child| child.is_code()),

            // Ref nodes: delegate to child
            Node::Ref { child, .. } => child.is_code(),
        }
    }

    /// Check if this node is whitespace (spaces, tabs, newlines)
    pub fn is_whitespace(&self) -> bool {
        match self {
            Node::Raw { token, .. } => token.is_whitespace(),
            _ => false,
        }
    }

    /// Check if this node is a meta node (indent, dedent, etc.)
    pub fn is_meta(&self) -> bool {
        match self {
            Node::Raw { token, .. } => token.is_meta,
            _ => false,
        }
    }

    /// Check if this node should be included in code-only serialization
    /// This matches Python's behavior for `code_only=True`
    pub fn should_include_in_code_only(&self) -> bool {
        self.is_code() && !self.is_meta()
    }

    /// Get the type of this node based on its variant and token information
    /// This helps determine what kind of segment it represents
    pub fn get_type(&self) -> Option<String> {
        match self {
            // Node::Whitespace {
            //     raw: _,
            //     token_idx: _,
            // } => Some("whitespace".to_string()),
            // Node::Newline {
            //     raw: _,
            //     token_idx: _,
            // } => Some("newline".to_string()),
            // Node::Comment {
            //     raw: _,
            //     token_idx: _,
            // } => Some("comment".to_string()),
            // Node::EndOfFile {
            //     raw: _,
            //     token_idx: _,
            // } => Some("end_of_file".to_string()),
            Node::Raw { token, .. } => Some(token.token_type.clone()),
            Node::Unparsable {
                expected_message: _,
                children: _,
            } => Some("unparsable".to_string()),
            Node::Ref { segment_type, .. } => segment_type.clone(),
            Node::Sequence { children: _ } => Some("sequence".to_string()),
            Node::DelimitedList { children: _ } => Some("delimited".to_string()),
            Node::Bracketed { .. } => Some("bracketed".to_string()),
            Node::Empty => None,
        }
    }

    /// Get all class types from the token, if this node references a token
    pub fn get_class_types(&self, tokens: &[Token]) -> Vec<String> {
        match self {
            Node::Raw { token, .. } => {
                let mut v = vec![token.token_type.clone()];
                v.extend(token.class_types.iter().cloned());
                v
            }
            Node::Ref { child, .. } => child.get_class_types(tokens),
            _ => Vec::new(),
        }
    }

    /// Check if this node or its token has a specific type
    pub fn has_type(&self, type_name: &str, tokens: &[Token]) -> bool {
        if let Some(node_type) = self.get_type() {
            if node_type == type_name {
                return true;
            }
        }

        // Also check class types
        self.get_class_types(tokens)
            .contains(&type_name.to_string())
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
    fn test_sequence_node_as_record_empty() {
        let node = Node::Sequence { children: vec![] };
        let record = node.as_record(false, true, false).unwrap();
        let expected = Value::Mapping({
            let mut m = serde_yaml_ng::Mapping::new();
            m.insert(Value::String("sequence".to_string()), Value::Null);
            m
        });
        assert_eq!(record, expected);
    }

    #[test]
    fn test_sequence_node_as_record_merge() {
        let node = Node::Sequence {
            children: vec![
                Node::new_token("keyword".to_string(), "SELECT".to_string(), 0),
                Node::new_token("naked_identifier".to_string(), "foo".to_string(), 1),
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
                Value::String("sequence".to_string()),
                Value::Mapping(merged),
            );
            m
        });
        assert_eq!(record, expected);
    }

    #[test]
    fn test_ref_node_as_record() {
        let child = Node::new_token("keyword".to_string(), "SELECT".to_string(), 0);
        let node = Node::Ref {
            name: "SelectKeywordSegment".to_string(),
            segment_type: Some("keyword".to_string()),
            segment_class: Some("SelectKeywordSegment".to_string()),
            child: Box::new(child),
        };
        let record = node.as_record(false, true, false).unwrap();
        let expected = Value::Mapping({
            let mut m = serde_yaml_ng::Mapping::new();
            m.insert(
                Value::String("keyword".to_string()),
                Value::Mapping({
                    let mut inner = serde_yaml_ng::Mapping::new();
                    inner.insert(
                        Value::String("keyword".to_string()),
                        Value::String("SELECT".to_string()),
                    );
                    inner
                }),
            );
            m
        });
        assert_eq!(record, expected);
    }

    // #[test]
    // fn test_meta_node_as_record() {
    //     let node = Node::Meta {
    //         token_type: "indent".to_string(),
    //         token_idx: None,
    //     };
    //     let record = node.as_record(false, true, false).unwrap();
    //     let expected = Value::Mapping({
    //         let mut m = serde_yaml_ng::Mapping::new();
    //         m.insert(Value::String("indent".to_string()), Value::Null);
    //         m
    //     });
    //     assert_eq!(record, expected);
    // }

    // #[test]
    // fn test_unparsable_node_as_record() {
    //     let node = Node::Unparsable {
    //         expected_message: "expected foo".to_string(),
    //         children: vec![
    //             Node::Raw {
    //                 token_type: "keyword".to_string(),
    //                 raw: "SELECT".to_string(),
    //                 token_idx: 0,
    //             },
    //             Node::Raw {
    //                 token_type: "naked_identifier".to_string(),
    //                 raw: "foo".to_string(),
    //                 token_idx: 1,
    //             },
    //         ],
    //     };
    //     let record = node.as_record(false, true, false).unwrap();
    //     let mut expected_inner = serde_yaml_ng::Mapping::new();
    //     expected_inner.insert(
    //         Value::String("keyword".to_string()),
    //         Value::String("SELECT".to_string()),
    //     );
    //     expected_inner.insert(
    //         Value::String("naked_identifier".to_string()),
    //         Value::String("foo".to_string()),
    //     );
    //     let expected = Value::Mapping({
    //         let mut m = serde_yaml_ng::Mapping::new();
    //         m.insert(
    //             Value::String("unparsable".to_string()),
    //             Value::Mapping(expected_inner),
    //         );
    //         m
    //     });
    //     assert_eq!(record, expected);
    // }

    // #[test]
    // fn test_token_node_to_tuple_show_raw() {
    //     let node = Node::Raw {
    //         token_type: "keyword".to_string(),
    //         raw: "SELECT".to_string(),
    //         token_idx: 0,
    //     };
    //     let val = node.to_tuple(false, true, false);
    //     assert_eq!(
    //         val,
    //         NodeTupleValue::Raw("keyword".to_string(), "SELECT".to_string())
    //     );
    // }

    // #[test]
    // fn test_token_node_to_tuple_no_raw() {
    //     let node = Node::Raw {
    //         token_type: "keyword".to_string(),
    //         raw: "SELECT".to_string(),
    //         token_idx: 0,
    //     };
    //     let val = node.to_tuple(false, false, false);
    //     assert_eq!(val, NodeTupleValue::Tuple("keyword".to_string(), vec![]));
    // }

    // #[test]
    // fn test_sequence_node_to_tuple() {
    //     let child1 = Node::Raw {
    //         token_type: "keyword".to_string(),
    //         raw: "SELECT".to_string(),
    //         token_idx: 0,
    //     };
    //     let child2 = Node::Raw {
    //         token_type: "keyword".to_string(),
    //         raw: "FROM".to_string(),
    //         token_idx: 1,
    //     };
    //     let node = Node::Sequence {
    //         children: vec![child1, child2],
    //     };
    //     let val = node.to_tuple(false, true, false);
    //     assert_eq!(
    //         val,
    //         NodeTupleValue::Tuple(
    //             "sequence".to_string(),
    //             vec![
    //                 NodeTupleValue::Raw("keyword".to_string(), "SELECT".to_string()),
    //                 NodeTupleValue::Raw("keyword".to_string(), "FROM".to_string()),
    //             ]
    //         )
    //     );
    // }

    // #[test]
    // fn test_ref_node_to_tuple() {
    //     let child = Node::Raw {
    //         token_type: "keyword".to_string(),
    //         raw: "SELECT".to_string(),
    //         token_idx: 0,
    //     };
    //     let node = Node::Ref {
    //         name: "SelectKeywordSegment".to_string(),
    //         segment_type: None,
    //         segment_class: None,
    //         child: Box::new(child),
    //     };
    //     let val = node.to_tuple(false, true, false);
    //     assert_eq!(
    //         val,
    //         NodeTupleValue::Raw("keyword".to_string(), "SELECT".to_string())
    //     );
    // }

    // #[test]
    // fn test_meta_node_to_tuple_include_meta() {
    //     let node = Node::Meta {
    //         token_type: "indent".to_string(),
    //         token_idx: None,
    //     };
    //     let val = node.to_tuple(false, false, true);
    //     assert_eq!(
    //         val,
    //         NodeTupleValue::Raw("indent".to_string(), "".to_string())
    //     );
    // }

    // #[test]
    // fn test_meta_node_to_tuple_exclude_meta() {
    //     let node = Node::Meta {
    //         token_type: "indent".to_string(),
    //         token_idx: None,
    //     };
    //     let val = node.to_tuple(false, false, false);
    //     assert_eq!(val, NodeTupleValue::Tuple("indent".to_string(), vec![]));
    // }

    // #[test]
    // fn test_empty_node_to_tuple() {
    //     let node = Node::Empty;
    //     let val = node.to_tuple(false, false, false);
    //     assert_eq!(val, NodeTupleValue::Tuple("empty".to_string(), vec![]));
    // }
}
