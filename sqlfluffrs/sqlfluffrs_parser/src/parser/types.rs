//! Core types for the parser: Grammar, Node, ParseMode

use std::collections::HashSet;
use std::sync::Arc;

use serde_yaml_ng::{Mapping, Value};
use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_types::{Grammar, Token};

/// Helper enum for tuple serialization, similar to Python's TupleSerialisedSegment.
#[derive(Debug, Clone, PartialEq)]
pub enum NodeTupleValue {
    Raw(String, String),
    Tuple(String, Vec<NodeTupleValue>),
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
    /// bracket_persists: if true, output as "bracketed:" wrapper in YAML
    ///                   if false, output children inline (for square/curly brackets)
    Bracketed {
        children: Vec<Node>,
        bracket_persists: bool,
    },

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
    /// Merge or list logic matching Python's structural_simplify.
    fn merge_or_list(key: String, contents: Vec<serde_yaml_ng::Value>) -> serde_yaml_ng::Value {
        use std::collections::HashSet;
        let mut all_keys = HashSet::new();
        let mut has_duplicates = false;
        for child in &contents {
            if let Value::Mapping(map) = child {
                for k in map.keys() {
                    if !all_keys.insert(k.clone()) {
                        has_duplicates = true;
                    }
                }
            }
        }
        if has_duplicates {
            // Return as a list of dicts
            let seq = contents;
            let mut map = Mapping::new();
            map.insert(Value::String(key), Value::Sequence(seq));
            Value::Mapping(map)
        } else {
            // Merge all dicts into one
            let mut merged = Mapping::new();
            for child in contents {
                if let Value::Mapping(map) = child {
                    for (k, v) in map {
                        merged.insert(k, v);
                    }
                }
            }
            let mut map = Mapping::new();
            map.insert(Value::String(key), Value::Mapping(merged));
            Value::Mapping(map)
        }
    }

    /// Return a tuple structure from this node, similar to Python BaseSegment::to_tuple.
    /// This is useful for serialization to YAML/JSON and for parity with Python tests.
    pub fn to_tuple(&self, code_only: bool, show_raw: bool, include_meta: bool) -> NodeTupleValue {
        match self {
            Node::Token {
                token_type, raw, ..
            } => {
                if show_raw {
                    NodeTupleValue::Raw(token_type.clone(), raw.clone())
                } else {
                    NodeTupleValue::Tuple(token_type.clone(), vec![])
                }
            }
            Node::Whitespace { raw, .. }
            | Node::Newline { raw, .. }
            | Node::EndOfFile { raw, .. } => {
                // These are filtered in code_only mode
                if code_only {
                    NodeTupleValue::Tuple(self.get_type().unwrap(), vec![])
                } else {
                    NodeTupleValue::Raw(self.get_type().unwrap(), raw.to_string())
                }
            }
            Node::Meta {
                token_type: meta_type,
                ..
            } => {
                if include_meta {
                    NodeTupleValue::Raw(meta_type.to_string(), "".to_string())
                } else {
                    NodeTupleValue::Tuple(meta_type.to_string(), vec![])
                }
            }
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
            Node::Bracketed {
                children: items, ..
            } => {
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

    /// Get the last (end) token index from this node
    /// For leaf nodes, returns the same as get_token_idx()
    /// For container nodes, recursively finds the last token in children
    pub fn get_end_token_idx(&self) -> Option<usize> {
        match self {
            // Leaf nodes - return their token index
            Node::Token { token_idx: idx, .. }
            | Node::Whitespace { token_idx: idx, .. }
            | Node::Newline { token_idx: idx, .. }
            | Node::EndOfFile { token_idx: idx, .. } => Some(*idx),

            // Container nodes - find last token in children
            Node::Sequence { children }
            | Node::DelimitedList { children }
            | Node::Bracketed { children, .. }
            | Node::Unparsable { children, .. } => children
                .iter()
                .rev()
                .find_map(|child| child.get_end_token_idx()),

            Node::Ref { child, .. } => child.get_end_token_idx(),

            // Empty and Meta nodes have no tokens
            Node::Empty | Node::Meta { .. } => None,
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
            | Node::Bracketed { children, .. } => {
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
            | Node::Bracketed { children, .. }
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
            // Empty is not code
            Node::Whitespace { .. }
            | Node::Newline { .. }
            | Node::EndOfFile { .. }
            | Node::Meta { .. }
            | Node::Empty => false,

            // Token: treat comments as non-code
            Node::Token { token_type, .. } => !matches!(
                token_type.as_str(),
                "whitespace" | "newline" | "inline_comment" | "comment"
            ),

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
    pub fn get_type(&self) -> Option<String> {
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
            Node::Bracketed { .. } => Some("bracketed".to_string()),
            Node::Meta {
                token_type: name, ..
            } => Some(name.to_string()),
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
        if let Some(node_type) = self.get_type() {
            if node_type == type_name {
                return true;
            }
        }

        // Also check class types
        self.get_class_types(tokens)
            .contains(&type_name.to_string())
    }

    /// Deduplicate whitespace and newline nodes in the AST.
    /// This removes duplicate token positions recursively throughout the tree.
    /// Returns a new Node with duplicates removed.
    pub fn deduplicate(self) -> Node {
        let mut seen = HashSet::new();
        self.deduplicate_impl(&mut seen)
    }

    /// Internal implementation of deduplicate that uses a shared HashSet
    fn deduplicate_impl(self, seen: &mut HashSet<usize>) -> Node {
        match self {
            Node::Sequence { children } => {
                let deduped = children
                    .into_iter()
                    .filter_map(|child| {
                        match &child {
                            Node::Whitespace { token_idx: pos, .. }
                            | Node::Newline { token_idx: pos, .. } => {
                                if seen.insert(*pos) {
                                    Some(child.deduplicate_impl(seen))
                                } else {
                                    None // Skip duplicate
                                }
                            }
                            _ => Some(child.deduplicate_impl(seen)),
                        }
                    })
                    .collect();
                Node::Sequence { children: deduped }
            }
            Node::DelimitedList { children } => {
                let deduped = children
                    .into_iter()
                    .filter_map(|child| match &child {
                        Node::Whitespace { token_idx: pos, .. }
                        | Node::Newline { token_idx: pos, .. } => {
                            if seen.insert(*pos) {
                                Some(child.deduplicate_impl(seen))
                            } else {
                                None
                            }
                        }
                        _ => Some(child.deduplicate_impl(seen)),
                    })
                    .collect();
                Node::DelimitedList { children: deduped }
            }
            Node::Bracketed {
                children,
                bracket_persists,
            } => {
                let deduped = children
                    .into_iter()
                    .filter_map(|child| match &child {
                        Node::Whitespace { token_idx: pos, .. }
                        | Node::Newline { token_idx: pos, .. } => {
                            if seen.insert(*pos) {
                                Some(child.deduplicate_impl(seen))
                            } else {
                                None
                            }
                        }
                        _ => Some(child.deduplicate_impl(seen)),
                    })
                    .collect();
                Node::Bracketed {
                    children: deduped,
                    bracket_persists,
                }
            }
            Node::Ref {
                name,
                segment_type,
                child,
            } => Node::Ref {
                name,
                segment_type,
                child: Box::new(child.deduplicate_impl(seen)),
            },
            Node::Unparsable {
                expected_message,
                children,
            } => {
                let deduped = children
                    .into_iter()
                    .filter_map(|child| match &child {
                        Node::Whitespace { token_idx: pos, .. }
                        | Node::Newline { token_idx: pos, .. } => {
                            if seen.insert(*pos) {
                                Some(child.deduplicate_impl(seen))
                            } else {
                                None
                            }
                        }
                        _ => Some(child.deduplicate_impl(seen)),
                    })
                    .collect();
                Node::Unparsable {
                    expected_message,
                    children: deduped,
                }
            }
            // Leaf nodes - just return as-is
            other => other,
        }
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
    pub pos: Option<usize>,
    pub grammar: Option<Arc<Grammar>>,
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

    pub fn with_context(
        message: String,
        pos: Option<usize>,
        grammar: Option<Arc<Grammar>>,
    ) -> Self {
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

    use serde_yaml_ng::Value;
    use sqlfluffrs_types::SimpleHint;

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

    #[test]
    fn test_meta_node_as_record() {
        let node = Node::Meta {
            token_type: "indent",
            token_idx: None,
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
    fn test_token_node_to_tuple_show_raw() {
        let node = Node::Token {
            token_type: "keyword".to_string(),
            raw: "SELECT".to_string(),
            token_idx: 0,
        };
        let val = node.to_tuple(false, true, false);
        assert_eq!(
            val,
            NodeTupleValue::Raw("keyword".to_string(), "SELECT".to_string())
        );
    }

    #[test]
    fn test_token_node_to_tuple_no_raw() {
        let node = Node::Token {
            token_type: "keyword".to_string(),
            raw: "SELECT".to_string(),
            token_idx: 0,
        };
        let val = node.to_tuple(false, false, false);
        assert_eq!(val, NodeTupleValue::Tuple("keyword".to_string(), vec![]));
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
        let val = node.to_tuple(false, true, false);
        assert_eq!(
            val,
            NodeTupleValue::Tuple(
                "sequence".to_string(),
                vec![
                    NodeTupleValue::Raw("keyword".to_string(), "SELECT".to_string()),
                    NodeTupleValue::Raw("keyword".to_string(), "FROM".to_string()),
                ]
            )
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
        let val = node.to_tuple(false, true, false);
        assert_eq!(
            val,
            NodeTupleValue::Raw("keyword".to_string(), "SELECT".to_string())
        );
    }

    #[test]
    fn test_meta_node_to_tuple_include_meta() {
        let node = Node::Meta {
            token_type: "indent",
            token_idx: None,
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
            token_type: "indent",
            token_idx: None,
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

    #[test]
    fn test_simple_hint_with_dialect_ref_comma_segment() {
        use hashbrown::HashSet;
        use serde_yaml_ng::{Mapping, Value};
        use sqlfluffrs_dialects::dialect::ansi::parser::COMMA_SEGMENT;

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
