//! Core types for the parser: Grammar, Node, ParseMode

use serde_yaml::Mapping;
use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_types::{Token, Grammar};

/// Helper enum for tuple serialization, similar to Python's TupleSerialisedSegment.
#[derive(Debug, Clone, PartialEq)]
pub enum NodeTupleValue {
    Raw(String),
    Tuple(Vec<NodeTupleValue>),
}

pub struct SegmentDef {
    pub name: &'static str,
    pub segment_type: Option<&'static str>,
    pub grammar: Grammar,
}

#[derive(Debug, Clone, PartialEq)]
pub enum Node {
    /// Whitespace tokens (spaces, tabs)
    Whitespace { raw: String, token_idx: usize },

    /// Newline tokens
    Newline { raw: String, token_idx: usize },

    /// End of file marker
    EndOfFile { raw: String, token_idx: usize },

    /// Generic token
    Token {
        token_type: String,
        raw: String,
        token_idx: usize,
    }, // (type, raw, position)

    /// Unparsable segment (in GREEDY mode when tokens don't match)
    Unparsable {
        expected_message: String,
        children: Vec<Node>,
    }, // (expected message, children)

    /// A sequence of child nodes (used for Grammar::Sequence)
    Sequence { children: Vec<Node> },

    /// A list of elements separated by commas
    DelimitedList { children: Vec<Node> },

    /// A bracketed section (content between brackets)
    Bracketed { children: Vec<Node> },

    /// A reference to another segment (wraps its AST)
    Ref {
        name: String,
        segment_type: Option<String>,
        child: Box<Node>,
    },

    /// Used when an optional part didn't match
    Empty,
    Meta {
        token_type: &'static str,
        token_idx: Option<usize>,
    },
}

impl Node {
    /// Return a tuple structure from this node, similar to Python BaseSegment::to_tuple.
    /// This is useful for serialization to YAML/JSON and for parity with Python tests.
    pub fn to_tuple(
        &self,
        tokens: &[Token],
        code_only: bool,
        show_raw: bool,
        include_meta: bool,
    ) -> (String, NodeTupleValue) {
        match self {
            Node::Token {
                token_type,
                raw,
                token_idx: _pos,
            } => {
                if show_raw {
                    (token_type.clone(), NodeTupleValue::Raw(raw.clone()))
                } else {
                    (token_type.clone(), NodeTupleValue::Tuple(vec![]))
                }
            }
            Node::Whitespace { raw, token_idx }
            | Node::Newline { raw, token_idx }
            | Node::EndOfFile { raw, token_idx } => {
                // These are filtered in code_only mode
                if code_only {
                    (
                        tokens[*token_idx].token_type.to_string(),
                        NodeTupleValue::Tuple(vec![]),
                    )
                } else {
                    (
                        tokens[*token_idx].token_type.to_string(),
                        NodeTupleValue::Raw(raw.to_string()),
                    )
                }
            }
            Node::Meta {
                token_type: meta_type,
                ..
            } => {
                if include_meta {
                    (meta_type.to_string(), NodeTupleValue::Raw("".to_string()))
                } else {
                    ("".to_string(), NodeTupleValue::Tuple(vec![]))
                }
            }
            Node::Ref {
                segment_type,
                child,
                ..
            } => {
                let (_typ, val) = child.to_tuple(tokens, code_only, show_raw, include_meta);
                if let Some(segment_type) = segment_type {
                    (segment_type.clone(), val)
                } else {
                    ("".to_string(), val)
                }
            }
            Node::Sequence { children }
            | Node::DelimitedList { children }
            | Node::Bracketed { children }
            | Node::Unparsable {
                expected_message: _,
                children,
            } => {
                let mut tupled = vec![];
                for child in children {
                    // Filter out non-code elements if code_only is true
                    if code_only && !child.is_code() {
                        continue;
                    }
                    let (_typ, val) = child.to_tuple(tokens, code_only, show_raw, include_meta);
                    tupled.push(val);
                }
                ("grammar".to_string(), NodeTupleValue::Tuple(tupled))
            }
            Node::Empty => ("empty".to_string(), NodeTupleValue::Tuple(vec![])),
        }
    }

    /// Serialize the Node AST to a simplified record structure for YAML/JSON output.
    /// Mirrors Python's BaseSegment::as_record logic.
    pub fn as_record(&self) -> Option<serde_yaml::Value> {
        use serde_yaml::Value;

        // Helper: merge child mappings if keys are unique, else use a list
        fn merge_or_list(key: String, contents: Vec<Value>) -> Value {
            let mut subkeys = Vec::new();
            let mut dicts = Vec::new();
            for v in &contents {
                if let Value::Mapping(map) = v {
                    for k in map.keys() {
                        if let Some(s) = k.as_str() {
                            subkeys.push(s.to_string());
                        }
                    }
                    dicts.push(map.clone());
                }
            }
            if subkeys.len() == 0 {
                // All children are null or empty
                let mut map = Mapping::new();
                map.insert(Value::String(key.clone()), Value::Null);
                Value::Mapping(map)
            } else if subkeys.len() == dicts.len() {
                // All keys are unique, merge into one dict
                let mut merged = Mapping::new();
                for dict in dicts {
                    for (k, v) in dict {
                        merged.insert(k, v);
                    }
                }
                let mut map = Mapping::new();
                map.insert(Value::String(key.clone()), Value::Mapping(merged));
                Value::Mapping(map)
            } else {
                // Duplicates: use a list
                let mut map = Mapping::new();
                map.insert(Value::String(key.clone()), Value::Sequence(contents));
                Value::Mapping(map)
            }
        }

        match self {
            Node::Token {
                token_type,
                raw,
                token_idx: _,
            } => {
                let mut map = Mapping::new();
                map.insert(
                    Value::String(token_type.clone()),
                    Value::String(raw.clone()),
                );
                Some(Value::Mapping(map))
            }
            Node::Whitespace { raw, token_idx: _ } => {
                let mut map = Mapping::new();
                map.insert(
                    Value::String("whitespace".to_string()),
                    Value::String(raw.clone()),
                );
                Some(Value::Mapping(map))
            }
            Node::Newline { raw, token_idx: _ } => {
                let mut map = Mapping::new();
                map.insert(
                    Value::String("newline".to_string()),
                    Value::String(raw.clone()),
                );
                Some(Value::Mapping(map))
            }
            Node::EndOfFile { raw, token_idx: _ } => {
                let mut map = Mapping::new();
                map.insert(
                    Value::String("end_of_file".to_string()),
                    Value::String(raw.clone()),
                );
                Some(Value::Mapping(map))
            }
            Node::Meta {
                token_type: name, ..
            } => {
                let mut map = Mapping::new();
                map.insert(Value::String(format!("meta_{}", name)), Value::Null);
                Some(Value::Mapping(map))
            }
            Node::Empty => {
                // Represent as None/null
                None
            }
            Node::Unparsable {
                expected_message: expected,
                children,
            } => {
                let contents: Vec<Value> = children.iter().filter_map(|c| c.as_record()).collect();
                let mut map = Mapping::new();
                map.insert(
                    Value::String("unparsable".to_string()),
                    Value::Sequence(contents),
                );
                Some(Value::Mapping(map))
            }
            Node::Ref {
                name,
                segment_type,
                child,
            } => {
                let key = segment_type
                    .clone()
                    .unwrap_or_else(|| simplify_segment_name(name));
                if let Some(child_rec) = child.as_record() {
                    let mut map = Mapping::new();
                    map.insert(Value::String(key), child_rec);
                    Some(Value::Mapping(map))
                } else {
                    let mut map = Mapping::new();
                    map.insert(Value::String(key), Value::Null);
                    Some(Value::Mapping(map))
                }
            }
            Node::Sequence { children }
            | Node::DelimitedList { children }
            | Node::Bracketed { children } => {
                let key = match self {
                    Node::Sequence { children: _ } => "sequence",
                    Node::DelimitedList { children: _ } => "delimited_list",
                    Node::Bracketed { children: _ } => "bracketed",
                    _ => unreachable!(),
                };
                let contents: Vec<Value> = children.iter().filter_map(|c| c.as_record()).collect();
                if contents.is_empty() {
                    let mut map = Mapping::new();
                    map.insert(Value::String(key.to_string()), Value::Null);
                    Some(Value::Mapping(map))
                } else {
                    Some(merge_or_list(key.to_string(), contents))
                }
            }
        }
    }

    pub fn is_empty(&self) -> bool {
        match &self {
            Node::Empty => true,
            Node::DelimitedList { children: items } => {
                items.is_empty()
                    || items
                        .iter()
                        .all(|n| matches!(n, Node::Empty | Node::Meta { .. }))
            }
            Node::Sequence { children: items } => {
                items.is_empty()
                    || items
                        .iter()
                        .all(|n| matches!(n, Node::Empty | Node::Meta { .. }))
            }
            Node::Bracketed { children: items } => {
                items.is_empty()
                    || items
                        .iter()
                        .all(|n| matches!(n, Node::Empty | Node::Meta { .. }))
            }
            _ => false,
        }
    }

    /// Get the token index from this node if it's a Token/Whitespace/Newline/EndOfFile.
    /// Returns None for complex nodes like Sequence, Ref, etc.
    pub fn get_token_idx(&self) -> Option<usize> {
        match self {
            Node::Token {
                token_type: _,
                raw: _,
                token_idx: idx,
            }
            | Node::Whitespace {
                raw: _,
                token_idx: idx,
            }
            | Node::Newline {
                raw: _,
                token_idx: idx,
            }
            | Node::EndOfFile {
                raw: _,
                token_idx: idx,
            } => Some(*idx),
            _ => None,
        }
    }

    /// Format the AST to mirror Python SQLFluff's parse output format.
    pub fn format_tree(&self, tokens: &[Token]) -> String {
        let mut output = String::new();
        let mut eof_nodes = Vec::new();

        self.format_tree_impl(tokens, &mut output, 0, 0, &mut eof_nodes);

        // Print all EndOfFile nodes at the very end
        for (depth, idx) in eof_nodes {
            let indent = "    ".repeat(depth);
            if let Some(token) = tokens.get(idx) {
                if let Some(pos_marker) = &token.pos_marker {
                    let (line, pos) = pos_marker.source_position();
                    output.push_str(&format!(
                        "[L:{:3}, P:{:3}]      |{}[META] end_of_file:\n",
                        line, pos, indent,
                    ));
                }
            }
        }

        output
    }

    fn format_tree_impl(
        &self,
        tokens: &[Token],
        output: &mut String,
        depth: usize,
        token_idx: usize,
        eof_nodes: &mut Vec<(usize, usize)>,
    ) -> usize {
        let indent = "    ".repeat(depth);

        match self {
            Node::Whitespace {
                raw: _,
                token_idx: idx,
            }
            | Node::Newline {
                raw: _,
                token_idx: idx,
            }
            | Node::Token {
                token_type: _,
                raw: _,
                token_idx: idx,
            } => {
                if let Some(token) = tokens.get(*idx) {
                    output.push_str(&token.stringify(depth, 4, false));
                }
                *idx + 1
            }

            Node::EndOfFile {
                raw: _,
                token_idx: idx,
            } => {
                eof_nodes.push((depth, *idx));
                *idx + 1
            }

            Node::Unparsable {
                expected_message: expected,
                children,
            } => {
                output.push_str(&format!("{}[unparsable] expected: {}\n", indent, expected));
                let mut last_idx = token_idx;
                for child in children {
                    last_idx =
                        child.format_tree_impl(tokens, output, depth + 1, last_idx, eof_nodes);
                }
                last_idx
            }

            Node::Meta {
                token_type: name, ..
            } => {
                let (line, pos) = if let Some(token) = tokens.get(token_idx) {
                    if let Some(pos_marker) = &token.pos_marker {
                        pos_marker.source_position()
                    } else {
                        (0, 0)
                    }
                } else if token_idx > 0 && token_idx <= tokens.len() {
                    if let Some(token) = tokens.get(token_idx - 1) {
                        if let Some(pos_marker) = &token.pos_marker {
                            let (start_line, start_pos) = pos_marker.source_position();
                            let token_len = token.raw().len();
                            (start_line, start_pos + token_len)
                        } else {
                            (0, 0)
                        }
                    } else {
                        (0, 0)
                    }
                } else {
                    (0, 0)
                };

                output.push_str(&format!(
                    "[L:{:3}, P:{:3}]      |{}[META] {}:\n",
                    line, pos, indent, name,
                ));
                token_idx
            }

            Node::Ref {
                name,
                segment_type,
                child,
            } => {
                let is_grammar_rule = name.ends_with("Grammar");
                let is_single_token = matches!(
                    child.as_ref(),
                    Node::Whitespace {
                        raw: _,
                        token_idx: _
                    } | Node::Newline {
                        raw: _,
                        token_idx: _
                    } | Node::EndOfFile {
                        raw: _,
                        token_idx: _
                    }
                );
                let is_transparent = is_grammar_rule || is_single_token;

                let mut current_idx = token_idx;

                if is_transparent {
                    current_idx =
                        child.format_tree_impl(tokens, output, depth, current_idx, eof_nodes);
                } else {
                    let display_name = if let Some(ref seg_type) = segment_type {
                        seg_type.clone()
                    } else {
                        simplify_segment_name(name)
                    };

                    if let Some(first_token_idx) = self.find_first_token_idx() {
                        if let Some(token) = tokens.get(first_token_idx) {
                            if let Some(pos_marker) = &token.pos_marker {
                                let (line, pos) = pos_marker.source_position();
                                output.push_str(&format!(
                                    "[L:{:3}, P:{:3}]      |{}{}:\n",
                                    line, pos, indent, display_name
                                ));
                            }
                        }
                    }

                    current_idx =
                        child.format_tree_impl(tokens, output, depth + 1, current_idx, eof_nodes);
                }
                current_idx
            }

            Node::Sequence { children }
            | Node::DelimitedList { children }
            | Node::Bracketed { children } => {
                let mut current_idx = token_idx;
                let mut eof_indices = Vec::new();

                for (i, child) in children.iter().enumerate() {
                    if matches!(
                        child,
                        Node::EndOfFile {
                            raw: _,
                            token_idx: _
                        }
                    ) {
                        eof_indices.push(i);
                    } else if !child.is_empty() {
                        current_idx =
                            child.format_tree_impl(tokens, output, depth, current_idx, eof_nodes);
                    }
                }

                for &i in &eof_indices {
                    current_idx =
                        children[i].format_tree_impl(tokens, output, depth, current_idx, eof_nodes);
                }

                current_idx
            }
            Node::Empty => token_idx,
        }
    }

    fn find_first_token_idx(&self) -> Option<usize> {
        match self {
            Node::Whitespace {
                raw: _,
                token_idx: idx,
            }
            | Node::Newline {
                raw: _,
                token_idx: idx,
            }
            | Node::EndOfFile {
                raw: _,
                token_idx: idx,
            }
            | Node::Token {
                token_type: _,
                raw: _,
                token_idx: idx,
            } => Some(*idx),

            Node::Ref { child, .. } => child.find_first_token_idx(),

            Node::Sequence { children }
            | Node::DelimitedList { children }
            | Node::Bracketed { children }
            | Node::Unparsable {
                expected_message: _,
                children,
            } => children.iter().find_map(|c| c.find_first_token_idx()),

            Node::Meta { .. } | Node::Empty => None,
        }
    }

    /// Check if this node represents code (not whitespace or meta)
    pub fn is_code(&self) -> bool {
        match self {
            // Whitespace and newlines are not code
            Node::Whitespace {
                raw: _,
                token_idx: _,
            }
            | Node::Newline {
                raw: _,
                token_idx: _,
            } => false,

            // EndOfFile and Meta are not code
            Node::EndOfFile {
                raw: _,
                token_idx: _,
            }
            | Node::Meta { .. } => false,

            // Empty is not code
            Node::Empty => false,

            // Token depends on its type
            Node::Token {
                token_type,
                raw: _,
                token_idx: _,
            } => !matches!(token_type.as_str(), "whitespace" | "newline"),

            // Unparsable segments contain code
            Node::Unparsable {
                expected_message: _,
                children: _,
            } => true,

            // Container nodes: check if they contain any code
            Node::Sequence { children }
            | Node::DelimitedList { children }
            | Node::Bracketed { children } => children.iter().any(|child| child.is_code()),

            // Ref nodes: delegate to child
            Node::Ref { child, .. } => child.is_code(),
        }
    }

    /// Check if this node is whitespace (spaces, tabs, newlines)
    pub fn is_whitespace(&self) -> bool {
        match self {
            Node::Whitespace {
                raw: _,
                token_idx: _,
            }
            | Node::Newline {
                raw: _,
                token_idx: _,
            } => true,
            Node::Token {
                token_type,
                raw: _,
                token_idx: _,
            } => {
                matches!(token_type.as_str(), "whitespace" | "newline")
            }
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

    /// Get the type of this node based on its variant and token information
    /// This helps determine what kind of segment it represents
    pub fn get_type(&self, tokens: &[Token]) -> Option<String> {
        match self {
            Node::Whitespace {
                raw: _,
                token_idx: _,
            } => Some("whitespace".to_string()),
            Node::Newline {
                raw: _,
                token_idx: _,
            } => Some("newline".to_string()),
            Node::EndOfFile {
                raw: _,
                token_idx: _,
            } => Some("end_of_file".to_string()),
            Node::Token {
                token_type,
                raw: _,
                token_idx: _,
            } => Some(token_type.clone()),
            Node::Unparsable {
                expected_message: _,
                children: _,
            } => Some("unparsable".to_string()),
            Node::Ref { segment_type, .. } => segment_type.clone(),
            Node::Sequence { children: _ } => Some("sequence".to_string()),
            Node::DelimitedList { children: _ } => Some("delimited_list".to_string()),
            Node::Bracketed { children: _ } => Some("bracketed".to_string()),
            Node::Meta {
                token_type: name, ..
            } => Some(format!("meta_{}", name)),
            Node::Empty => None,
        }
    }

    /// Get all class types from the token, if this node references a token
    pub fn get_class_types(&self, tokens: &[Token]) -> Vec<String> {
        match self {
            Node::Token {
                token_type,
                raw: _,
                token_idx: idx,
            } => {
                if let Some(token) = tokens.get(*idx) {
                    let mut v = vec![token_type.clone()];
                    v.extend(token.class_types.iter().cloned());
                    v
                } else {
                    Vec::new()
                }
            }
            Node::Ref { child, .. } => child.get_class_types(tokens),
            _ => Vec::new(),
        }
    }

    /// Check if this node or its token has a specific type
    pub fn has_type(&self, type_name: &str, tokens: &[Token]) -> bool {
        if let Some(node_type) = self.get_type(tokens) {
            if node_type == type_name {
                return true;
            }
        }

        // Also check class types
        self.get_class_types(tokens)
            .contains(&type_name.to_string())
    }
}

fn simplify_segment_name(name: &str) -> String {
    let name = name
        .strip_suffix("Segment")
        .or_else(|| name.strip_suffix("Grammar"))
        .unwrap_or(name);

    camel_to_snake(name)
}

fn camel_to_snake(s: &str) -> String {
    let mut result = String::new();
    let mut chars = s.chars().peekable();

    while let Some(c) = chars.next() {
        if c.is_uppercase() {
            if !result.is_empty() {
                result.push('_');
            }
            result.push(c.to_lowercase().next().unwrap());
        } else {
            result.push(c);
        }
    }

    result
}

#[derive(Debug, Clone)]
pub struct ParseError {
    pub message: String,
}

impl ParseError {
    pub fn new(message: String) -> Self {
        ParseError { message }
    }

    pub fn unknown_segment(name: String) -> ParseError {
        ParseError {
            message: format!("Unknown segment: {}", name),
        }
    }
}

pub struct Parsed {
    // This struct is intentionally left empty for now.
}

pub enum ParseErrorType {
    EmptyInput,
    InvalidToken,
    UnexpectedEndOfInput,
    MismatchedParentheses,
    UnknownSegment,
}

/// Context for parsing operations
pub struct ParseContext {
    dialect: Dialect,
    uuid: uuid::Uuid,
    match_segment: String,
}

impl ParseContext {
    pub fn new(dialect: Dialect) -> Self {
        let uuid = uuid::Uuid::new_v4();
        ParseContext {
            dialect,
            uuid,
            match_segment: String::from("File"),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    use serde_yaml::Value;
    use sqlfluffrs_types::SimpleHint;

    #[test]
    fn test_token_node_as_record() {
        let node = Node::Token {
            token_type: "keyword".to_string(),
            raw: "SELECT".to_string(),
            token_idx: 0,
        };
        let record = node.as_record().unwrap();
        let expected = Value::Mapping({
            let mut m = serde_yaml::Mapping::new();
            m.insert(
                Value::String("keyword".to_string()),
                Value::String("SELECT".to_string()),
            );
            m
        });
        assert_eq!(record, expected);
    }

    #[test]
    fn test_sequence_node_as_record_empty() {
        let node = Node::Sequence { children: vec![] };
        let record = node.as_record().unwrap();
        let expected = Value::Mapping({
            let mut m = serde_yaml::Mapping::new();
            m.insert(Value::String("sequence".to_string()), Value::Null);
            m
        });
        assert_eq!(record, expected);
    }

    #[test]
    fn test_sequence_node_as_record_merge() {
        let node = Node::Sequence {
            children: vec![
                Node::Token {
                    token_type: "keyword".to_string(),
                    raw: "SELECT".to_string(),
                    token_idx: 0,
                },
                Node::Token {
                    token_type: "naked_identifier".to_string(),
                    raw: "foo".to_string(),
                    token_idx: 1,
                },
            ],
        };
        let record = node.as_record().unwrap();
        let mut merged = serde_yaml::Mapping::new();
        merged.insert(
            Value::String("keyword".to_string()),
            Value::String("SELECT".to_string()),
        );
        merged.insert(
            Value::String("naked_identifier".to_string()),
            Value::String("foo".to_string()),
        );
        let expected = Value::Mapping({
            let mut m = serde_yaml::Mapping::new();
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
        let child = Node::Token {
            token_type: "keyword".to_string(),
            raw: "SELECT".to_string(),
            token_idx: 0,
        };
        let node = Node::Ref {
            name: "SelectKeywordSegment".to_string(),
            segment_type: Some("keyword".to_string()),
            child: Box::new(child),
        };
        let record = node.as_record().unwrap();
        let expected = Value::Mapping({
            let mut m = serde_yaml::Mapping::new();
            m.insert(
                Value::String("keyword".to_string()),
                Value::Mapping({
                    let mut inner = serde_yaml::Mapping::new();
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

    #[test]
    fn test_meta_node_as_record() {
        let node = Node::Meta {
            token_type: "indent",
            token_idx: None,
        };
        let record = node.as_record().unwrap();
        let expected = Value::Mapping({
            let mut m = serde_yaml::Mapping::new();
            m.insert(Value::String("meta_indent".to_string()), Value::Null);
            m
        });
        assert_eq!(record, expected);
    }

    #[test]
    fn test_unparsable_node_as_record() {
        let node = Node::Unparsable {
            expected_message: "expected foo".to_string(),
            children: vec![
                Node::Token {
                    token_type: "keyword".to_string(),
                    raw: "SELECT".to_string(),
                    token_idx: 0,
                },
                Node::Token {
                    token_type: "naked_identifier".to_string(),
                    raw: "foo".to_string(),
                    token_idx: 1,
                },
            ],
        };
        let record = node.as_record().unwrap();
        let expected = Value::Mapping({
            let mut m = serde_yaml::Mapping::new();
            let mut seq = Vec::new();
            seq.push(Value::Mapping({
                let mut inner = serde_yaml::Mapping::new();
                inner.insert(
                    Value::String("keyword".to_string()),
                    Value::String("SELECT".to_string()),
                );
                inner
            }));
            seq.push(Value::Mapping({
                let mut inner = serde_yaml::Mapping::new();
                inner.insert(
                    Value::String("naked_identifier".to_string()),
                    Value::String("foo".to_string()),
                );
                inner
            }));
            m.insert(
                Value::String("unparsable".to_string()),
                Value::Sequence(seq),
            );
            m
        });
        assert_eq!(record, expected);
    }

    #[test]
    fn test_token_node_to_tuple_show_raw() {
        let node = Node::Token {
            token_type: "keyword".to_string(),
            raw: "SELECT".to_string(),
            token_idx: 0,
        };
        let (typ, val) = node.to_tuple(&[], false, true, false);
        assert_eq!(typ, "keyword");
        assert_eq!(val, NodeTupleValue::Raw("SELECT".to_string()));
    }

    #[test]
    fn test_token_node_to_tuple_no_raw() {
        let node = Node::Token {
            token_type: "keyword".to_string(),
            raw: "SELECT".to_string(),
            token_idx: 0,
        };
        let (typ, val) = node.to_tuple(&[], false, false, false);
        assert_eq!(typ, "keyword");
        assert_eq!(val, NodeTupleValue::Tuple(vec![]));
    }

    #[test]
    fn test_sequence_node_to_tuple() {
        let child1 = Node::Token {
            token_type: "keyword".to_string(),
            raw: "SELECT".to_string(),
            token_idx: 0,
        };
        let child2 = Node::Token {
            token_type: "keyword".to_string(),
            raw: "FROM".to_string(),
            token_idx: 1,
        };
        let node = Node::Sequence {
            children: vec![child1, child2],
        };
        let (typ, val) = node.to_tuple(&[], false, true, false);
        assert_eq!(typ, "sequence");
        assert_eq!(
            val,
            NodeTupleValue::Tuple(vec![
                NodeTupleValue::Raw("SELECT".to_string()),
                NodeTupleValue::Raw("FROM".to_string()),
            ])
        );
    }

    #[test]
    fn test_ref_node_to_tuple() {
        let child = Node::Token {
            token_type: "keyword".to_string(),
            raw: "SELECT".to_string(),
            token_idx: 0,
        };
        let node = Node::Ref {
            name: "SelectKeywordSegment".to_string(),
            segment_type: None,
            child: Box::new(child),
        };
        let (typ, val) = node.to_tuple(&[], false, true, false);
        assert_eq!(typ, "");
        assert_eq!(val, NodeTupleValue::Raw("SELECT".to_string()));
    }

    #[test]
    fn test_meta_node_to_tuple_include_meta() {
        let node = Node::Meta {
            token_type: "indent",
            token_idx: None,
        };
        let (typ, val) = node.to_tuple(&[], false, false, true);
        assert_eq!(typ, "indent");
        assert_eq!(val, NodeTupleValue::Raw("".to_string()));
    }

    #[test]
    fn test_meta_node_to_tuple_exclude_meta() {
        let node = Node::Meta {
            token_type: "indent",
            token_idx: None,
        };
        let (typ, val) = node.to_tuple(&[], false, false, false);
        assert_eq!(typ, "indent");
        assert_eq!(val, NodeTupleValue::Tuple(vec![]));
    }

    #[test]
    fn test_empty_node_to_tuple() {
        let node = Node::Empty;
        let (typ, val) = node.to_tuple(&[], false, false, false);
        assert_eq!(typ, "empty");
        assert_eq!(val, NodeTupleValue::Tuple(vec![]));
    }

    #[test]
    fn test_simple_hint_with_dialect_ref_comma_segment() {
    use sqlfluffrs_dialects::dialect::ansi::parser::COMMA_SEGMENT;
        use hashbrown::HashSet;

        // Create a Ref grammar for CommaSegment
        let grammar = COMMA_SEGMENT.clone();
        // Get the Ansi dialect
        let mut cache: hashbrown::HashMap<u64, Option<SimpleHint>> = hashbrown::HashMap::new();
        // Get the hint
        let hint = grammar
            .simple_hint(&mut cache)
            .expect("Should return a hint");
        // Should match raw value ","
        assert!(hint.raw_values.contains(&" ,".trim().to_uppercase()));
        // Should match can_match_token for ","
        let mut token_types = HashSet::new();
        token_types.insert("comma".to_string());
        assert!(hint.can_match_token(&" ,".trim().to_uppercase(), &token_types));
    }
}
