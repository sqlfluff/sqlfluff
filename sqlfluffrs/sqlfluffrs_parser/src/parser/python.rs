use pyo3::exceptions::PyException;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};

use super::match_result::MatchResult;
use super::types::NodeTupleValue;
use super::{Node, ParseError, Parser};
use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_lexer::Lexer;
use sqlfluffrs_types::token::python::PyToken;
use sqlfluffrs_types::Token;
use std::str::FromStr;

/// Python-wrapped Node for AST representation
#[pyclass(name = "RsNode", module = "sqlfluffrs")]
#[derive(Clone)]
pub struct PyNode(pub Node);

#[pymethods]
impl PyNode {
    /// Get the node type as a string
    #[getter]
    fn node_type(&self) -> String {
        match &self.0 {
            Node::Token { .. } => "token".to_string(),
            Node::Ref { .. } => "ref".to_string(),
            Node::Sequence { .. } => "sequence".to_string(),
            Node::DelimitedList { .. } => "delimited_list".to_string(),
            Node::Bracketed { .. } => "bracketed".to_string(),
            Node::Meta { .. } => "meta".to_string(),
            Node::Empty => "empty".to_string(),
            Node::Whitespace { .. } => "whitespace".to_string(),
            Node::Newline { .. } => "newline".to_string(),
            Node::Comment { .. } => "comment".to_string(),
            Node::EndOfFile { .. } => "end_of_file".to_string(),
            Node::Unparsable { .. } => "unparsable".to_string(),
        }
    }

    /// Check if node is empty
    fn is_empty(&self) -> bool {
        self.0.is_empty()
    }

    /// Get children nodes (if applicable)
    fn children(&self) -> Option<Vec<PyNode>> {
        match &self.0 {
            Node::Sequence { children } | Node::DelimitedList { children } => {
                Some(children.iter().map(|n| PyNode(n.clone())).collect())
            }
            Node::Bracketed {
                children,
                bracket_persists: _,
            } => Some(children.iter().map(|n| PyNode(n.clone())).collect()),
            Node::Ref { child, .. } => Some(vec![PyNode((**child).clone())]),
            Node::Unparsable { children, .. } => {
                Some(children.iter().map(|n| PyNode(n.clone())).collect())
            }
            _ => None,
        }
    }

    /// Get token information (for Token nodes)
    /// Returns (token_type, segment_type, raw, token_idx)
    fn token_info(&self) -> Option<(String, String, String, usize)> {
        match &self.0 {
            Node::Token {
                token_type,
                segment_type,
                raw,
                token_idx,
            } => Some((
                token_type.clone(),
                segment_type.clone(),
                raw.clone(),
                *token_idx,
            )),
            Node::Whitespace { raw, token_idx } => Some((
                "whitespace".to_string(),
                "whitespace".to_string(),
                raw.clone(),
                *token_idx,
            )),
            Node::Newline { raw, token_idx } => Some((
                "newline".to_string(),
                "newline".to_string(),
                raw.clone(),
                *token_idx,
            )),
            Node::Comment { raw, token_idx } => Some((
                "comment".to_string(),
                "comment".to_string(),
                raw.clone(),
                *token_idx,
            )),
            Node::EndOfFile { raw, token_idx } => Some((
                "end_of_file".to_string(),
                "end_of_file".to_string(),
                raw.clone(),
                *token_idx,
            )),
            _ => None,
        }
    }

    /// Get ref information (for Ref nodes)
    fn ref_info(&self) -> Option<(String, Option<String>, Option<String>)> {
        match &self.0 {
            Node::Ref {
                name,
                segment_type,
                segment_class_name,
                ..
            } => Some((
                name.clone(),
                segment_type.clone(),
                segment_class_name.clone(),
            )),
            _ => None,
        }
    }

    /// Get bracket information (for Bracketed nodes)
    fn bracket_persists(&self) -> Option<bool> {
        match &self.0 {
            Node::Bracketed {
                bracket_persists, ..
            } => Some(*bracket_persists),
            _ => None,
        }
    }

    /// Convert to Python dict representation (for debugging/inspection)
    fn to_dict(&self, py: Python) -> PyResult<Py<PyAny>> {
        self.to_dict_recursive(py, 0, 100)
    }

    /// Convert to tuple representation (mirrors Python's to_tuple)
    #[pyo3(signature = (code_only=false, show_raw=false, include_meta=false))]
    fn to_tuple(
        &self,
        py: Python,
        code_only: bool,
        show_raw: bool,
        include_meta: bool,
    ) -> PyResult<Py<PyAny>> {
        let tuple_val = self.0.to_tuple(code_only, show_raw, include_meta);
        self.tuple_value_to_python(py, &tuple_val)
    }

    /// Get record representation (for YAML serialization)
    #[pyo3(signature = (code_only=false, show_raw=false, include_meta=false))]
    fn as_record(
        &self,
        py: Python,
        code_only: bool,
        show_raw: bool,
        include_meta: bool,
    ) -> PyResult<Option<Py<PyAny>>> {
        match self.0.as_record(code_only, show_raw, include_meta) {
            Some(yaml_val) => {
                // Convert serde_yaml::Value to Python object
                let py_obj = Self::yaml_to_python(py, &yaml_val)?;
                Ok(Some(py_obj))
            }
            None => Ok(None),
        }
    }

    /// Represent node as string
    fn __repr__(&self) -> String {
        match &self.0 {
            Node::Token {
                token_type, raw, ..
            } => {
                format!("RsNode(Token(type='{}', raw='{}'))", token_type, raw)
            }
            Node::Ref { name, .. } => {
                format!("RsNode(Ref(name='{}'))", name)
            }
            Node::Sequence { children } => {
                format!("RsNode(Sequence({} children))", children.len())
            }
            Node::Empty => "RsNode(Empty)".to_string(),
            _ => format!("RsNode({})", self.node_type()),
        }
    }

    /// String representation
    fn __str__(&self) -> String {
        self.__repr__()
    }
}

impl PyNode {
    fn to_dict_recursive(&self, py: Python, depth: usize, max_depth: usize) -> PyResult<Py<PyAny>> {
        if depth > max_depth {
            return Ok("...".into_pyobject(py)?.into());
        }

        let dict = PyDict::new(py);
        dict.set_item("node_type", self.node_type())?;

        match &self.0 {
            Node::Token {
                token_type,
                segment_type,
                raw,
                token_idx,
            } => {
                dict.set_item("token_type", token_type)?;
                dict.set_item("segment_type", segment_type)?;
                dict.set_item("raw", raw)?;
                dict.set_item("token_idx", token_idx)?;
            }
            Node::Whitespace { raw, token_idx }
            | Node::Newline { raw, token_idx }
            | Node::Comment { raw, token_idx }
            | Node::EndOfFile { raw, token_idx } => {
                dict.set_item("raw", raw)?;
                dict.set_item("token_idx", token_idx)?;
            }
            Node::Ref {
                name,
                segment_type,
                segment_class_name,
                child,
            } => {
                dict.set_item("name", name)?;
                dict.set_item("segment_type", segment_type)?;
                dict.set_item("segment_class_name", segment_class_name)?;
                let child_node = PyNode((**child).clone());
                dict.set_item(
                    "child",
                    child_node.to_dict_recursive(py, depth + 1, max_depth)?,
                )?;
            }
            Node::Sequence { children } | Node::DelimitedList { children } => {
                let py_children = PyList::empty(py);
                for child in children {
                    let child_node = PyNode(child.clone());
                    py_children.append(child_node.to_dict_recursive(
                        py,
                        depth + 1,
                        max_depth,
                    )?)?;
                }
                dict.set_item("children", py_children)?;
            }
            Node::Bracketed {
                children,
                bracket_persists,
            } => {
                let py_children = PyList::empty(py);
                for child in children {
                    let child_node = PyNode(child.clone());
                    py_children.append(child_node.to_dict_recursive(
                        py,
                        depth + 1,
                        max_depth,
                    )?)?;
                }
                dict.set_item("children", py_children)?;
                dict.set_item("bracket_persists", bracket_persists)?;
            }
            Node::Unparsable {
                expected_message,
                children,
            } => {
                dict.set_item("expected_message", expected_message)?;
                let py_children = PyList::empty(py);
                for child in children {
                    let child_node = PyNode(child.clone());
                    py_children.append(child_node.to_dict_recursive(
                        py,
                        depth + 1,
                        max_depth,
                    )?)?;
                }
                dict.set_item("children", py_children)?;
            }
            Node::Meta {
                token_type,
                token_idx,
            } => {
                dict.set_item("token_type", token_type)?;
                dict.set_item("token_idx", token_idx)?;
            }
            Node::Empty => {}
        }

        Ok(dict.into())
    }

    fn tuple_value_to_python(&self, py: Python, val: &NodeTupleValue) -> PyResult<Py<PyAny>> {
        match val {
            NodeTupleValue::Raw(key, s) => Ok((key, s).into_pyobject(py)?.into()),
            NodeTupleValue::Tuple(key, children) => {
                let py_children = PyList::empty(py);
                for child in children {
                    py_children.append(self.tuple_value_to_python(py, child)?)?;
                }
                Ok((key, py_children).into_pyobject(py)?.into())
            }
        }
    }

    fn yaml_to_python(py: Python, val: &serde_yaml_ng::Value) -> PyResult<Py<PyAny>> {
        use serde_yaml_ng::Value;
        match val {
            Value::Null => Ok(py.None()),
            Value::Bool(b) => Ok(b.into_pyobject(py)?.as_any().clone().unbind()),
            Value::Number(n) => {
                if let Some(i) = n.as_i64() {
                    Ok(i.into_pyobject(py)?.as_any().clone().unbind())
                } else if let Some(f) = n.as_f64() {
                    Ok(f.into_pyobject(py)?.as_any().clone().unbind())
                } else {
                    Ok(py.None())
                }
            }
            Value::String(s) => Ok(s.into_pyobject(py)?.as_any().clone().unbind()),
            Value::Sequence(seq) => {
                let py_list = PyList::empty(py);
                for item in seq {
                    py_list.append(Self::yaml_to_python(py, item)?)?;
                }
                Ok(py_list.into())
            }
            Value::Mapping(map) => {
                let py_dict = PyDict::new(py);
                for (k, v) in map {
                    let key = Self::yaml_to_python(py, k)?;
                    let value = Self::yaml_to_python(py, v)?;
                    py_dict.set_item(key, value)?;
                }
                Ok(py_dict.into())
            }
            Value::Tagged(tagged) => Self::yaml_to_python(py, &tagged.value),
        }
    }
}

impl From<Node> for PyNode {
    fn from(node: Node) -> Self {
        PyNode(node)
    }
}

/// Python-wrapped ParseError
#[pyclass(name = "RsParseError", module = "sqlfluffrs", extends=PyException)]
#[derive(Clone)]
pub struct PyParseError {
    #[pyo3(get)]
    message: String,
}

#[pymethods]
impl PyParseError {
    #[new]
    fn new(message: String) -> Self {
        PyParseError { message }
    }

    fn __str__(&self) -> String {
        self.message.clone()
    }

    fn __repr__(&self) -> String {
        format!("RsParseError('{}')", self.message)
    }
}

impl From<ParseError> for PyParseError {
    fn from(err: ParseError) -> Self {
        PyParseError {
            message: err.message,
        }
    }
}

/// Python-wrapped MatchResult for deferred AST construction
///
/// This allows Python code to receive match results and apply them using
/// Python's existing apply() logic, avoiding double-counting issues in Rust.
///
/// frozen=true makes this immutable (matches Python's @dataclass(frozen=True))
#[pyclass(name = "RsMatchResult", module = "sqlfluffrs", frozen)]
#[derive(Clone)]
pub struct PyMatchResult(pub MatchResult);

#[pymethods]
impl PyMatchResult {
    /// Get the matched slice as a Python tuple (start, stop)
    #[getter]
    fn matched_slice(&self) -> (usize, usize) {
        (self.0.matched_slice.start, self.0.matched_slice.end)
    }

    /// Get the matched class type as a string (or None)
    #[getter]
    fn matched_class(&self) -> Option<String> {
        self.0.matched_class.clone()
    }

    /// Get child matches as a list of PyMatchResult objects
    #[getter]
    fn child_matches(&self) -> Vec<PyMatchResult> {
        self.0
            .child_matches
            .iter()
            .map(|m| PyMatchResult((**m).clone()))
            .collect()
    }

    /// Get instance_types (semantic type markers like "keyword", "star")
    #[getter]
    fn instance_types(&self) -> Option<Vec<String>> {
        self.0.instance_types.clone()
    }

    /// Get trim_chars for the segment
    #[getter]
    fn trim_chars(&self) -> Option<Vec<String>> {
        self.0.trim_chars.clone()
    }

    /// Get casefold mode (for case-insensitive matching)
    #[getter]
    fn casefold(&self) -> Option<String> {
        match self.0.casefold {
            sqlfluffrs_types::token::CaseFold::None => None,
            sqlfluffrs_types::token::CaseFold::Upper => Some("upper".to_string()),
            sqlfluffrs_types::token::CaseFold::Lower => Some("lower".to_string()),
        }
    }

    /// Get quoted_value for identifier normalization
    #[getter]
    fn quoted_value(&self, py: Python<'_>) -> Option<(String, Py<PyAny>)> {
        self.0.quoted_value.as_ref().map(|(pattern, group)| {
            let py_group: Py<PyAny> = match group {
                sqlfluffrs_types::regex::RegexModeGroup::Index(idx) => {
                    idx.into_pyobject(py).unwrap().into()
                }
                sqlfluffrs_types::regex::RegexModeGroup::Name(name) => {
                    name.clone().into_pyobject(py).unwrap().into()
                }
            };
            (pattern.clone(), py_group)
        })
    }

    /// Get escape_replacement for escape sequence handling
    #[getter]
    fn escape_replacement(&self) -> Option<(String, String)> {
        self.0.escape_replacement.clone()
    }

    /// Get insert_segments (meta segments like Indent/Dedent to insert)
    #[getter]
    fn insert_segments(&self) -> Vec<(usize, String, bool)> {
        self.0
            .insert_segments
            .iter()
            .map(|(idx, seg_type, is_implicit)| {
                let type_name = match seg_type {
                    crate::parser::MetaSegmentType::Indent => "indent",
                    crate::parser::MetaSegmentType::Dedent => "dedent",
                };
                (*idx, type_name.to_string(), *is_implicit)
            })
            .collect()
    }

    /// Get parse_error (error message and token position) if present
    #[getter]
    fn parse_error(&self) -> Option<(String, usize)> {
        self.0.parse_error.clone()
    }

    /// Get segment_kwargs dictionary (e.g., "expected" for UnparsableSegment)
    #[getter]
    fn segment_kwargs(&self) -> std::collections::HashMap<String, String> {
        self.0
            .segment_kwargs
            .iter()
            .map(|(k, v)| (k.clone(), v.clone()))
            .collect()
    }

    /// Check if this is an empty match
    fn is_empty(&self) -> bool {
        self.0.matched_slice.is_empty()
    }

    /// Get length of matched slice
    fn __len__(&self) -> usize {
        self.0.matched_slice.end - self.0.matched_slice.start
    }

    /// Boolean conversion - truthy if has length
    fn __bool__(&self) -> bool {
        !self.0.matched_slice.is_empty() || !self.0.insert_segments.is_empty()
    }

    /// String representation for debugging
    fn __repr__(&self) -> String {
        format!(
            "RsMatchResult(slice={}..{}, class={:?}, {} children)",
            self.0.matched_slice.start,
            self.0.matched_slice.end,
            self.0.matched_class,
            self.0.child_matches.len()
        )
    }
}

/// Python-wrapped Parser
#[pyclass(name = "RsParser", module = "sqlfluffrs")]
pub struct PyParser {
    dialect: Dialect,
    indent_config: hashbrown::HashMap<&'static str, bool>,
}

#[pymethods]
impl PyParser {
    #[new]
    #[pyo3(signature = (dialect=None, indent_config=None))]
    pub fn new(
        dialect: Option<&str>,
        indent_config: Option<std::collections::HashMap<String, bool>>,
    ) -> PyResult<Self> {
        let dialect = dialect
            .and_then(|d| Dialect::from_str(d).ok())
            .unwrap_or(Dialect::Ansi);

        // Convert Python HashMap<String, bool> to Rust HashMap<&'static str, bool>
        // by leaking the strings to get 'static references
        let indent_config = if let Some(config) = indent_config {
            config
                .into_iter()
                .map(|(k, v)| {
                    let static_key: &'static str = Box::leak(k.into_boxed_str());
                    (static_key, v)
                })
                .collect()
        } else {
            hashbrown::HashMap::new()
        };

        Ok(PyParser {
            dialect,
            indent_config,
        })
    }

    /// Parse SQL from tokens (standalone mode)
    ///
    /// Takes a list of RsToken objects and returns the parsed AST as RsNode.
    pub fn parse_from_tokens(&self, tokens: Vec<PyToken>) -> PyResult<PyNode> {
        // Convert PyToken to internal Token
        let mut rust_tokens: Vec<Token> = tokens.into_iter().map(|t| t.into()).collect();

        // Compute bracket pairs for the tokens.
        // When tokens come from Python (lexed by Python lexer), matching_bracket_idx is None.
        // We need to compute it for the Bracketed grammar to work correctly.
        compute_bracket_pairs(&mut rust_tokens);

        // Create parser
        let mut parser = Parser::new(&rust_tokens, self.dialect, self.indent_config.clone());

        // Parse and convert result
        let node = parser
            .call_rule_as_root()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.message))?;

        Ok(PyNode(node))
    }

    /// Parse SQL string directly (convenience method)
    ///
    /// This is less efficient as it lexes internally. For best performance,
    /// use parse_from_tokens with tokens from RsLexer.
    pub fn parse(&self, sql: &str) -> PyResult<PyNode> {
        // Lex the SQL
        let lexer = Lexer::new(None, self.dialect.get_lexers().to_vec());
        let (tokens, violations) =
            lexer.lex(sqlfluffrs_lexer::LexInput::String(sql.to_string()), true);

        // Check for lex errors
        if !violations.is_empty() {
            let error_msg = format!(
                "Lexing failed with {} errors: {}",
                violations.len(),
                violations
                    .first()
                    .map(|v| v.description.clone().unwrap_or_default())
                    .unwrap_or_default()
            );
            return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(error_msg));
        }

        // Parse
        let mut parser = Parser::new(&tokens, self.dialect, self.indent_config.clone());
        let node = parser
            .call_rule_as_root()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.message))?;

        Ok(PyNode(node))
    }

    /// Get dialect name
    #[getter]
    fn dialect(&self) -> String {
        format!("{:?}", self.dialect).to_lowercase()
    }

    /// Parse SQL from tokens and return MatchResult (deferred AST construction)
    ///
    /// This returns a MatchResult that Python can apply using its own apply() logic,
    /// avoiding double-counting issues and allowing Python to maintain control over
    /// the AST construction process.
    pub fn parse_match_result_from_tokens(&self, tokens: Vec<PyToken>) -> PyResult<PyMatchResult> {
        // Convert PyToken to internal Token
        let mut rust_tokens: Vec<Token> = tokens.into_iter().map(|t| t.into()).collect();

        // Compute bracket pairs for the tokens.
        // When tokens come from Python (lexed by Python lexer), matching_bracket_idx is None.
        // We need to compute it for the Bracketed grammar to work correctly.
        compute_bracket_pairs(&mut rust_tokens);

        // Create parser
        let mut parser = Parser::new(&rust_tokens, self.dialect, self.indent_config.clone());

        // Parse and get the MatchResult directly
        let match_result = parser
            .call_rule_as_root_match_result()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.message))?;

        Ok(PyMatchResult(match_result))
    }

    /// Parse SQL from tokens and return MatchResult along with parser statistics.
    ///
    /// This is used for comparing Python and Rust parser behavior to verify
    /// that both parsers are doing equivalent work (pruning, caching, etc.)
    ///
    /// Returns a tuple: (PyMatchResult, stats_dict)
    /// where stats_dict contains:
    /// - cache_hits: number of cache hits
    /// - cache_misses: number of cache misses
    /// - cache_entries: number of cache entries
    /// - pruning_calls: number of prune_options calls
    /// - pruning_total: total options considered
    /// - pruning_kept: options kept after pruning
    /// - pruning_hinted: options that had hints
    /// - pruning_complex: options that returned None (complex)
    pub fn parse_match_result_with_stats(
        &self,
        tokens: Vec<PyToken>,
    ) -> PyResult<(PyMatchResult, std::collections::HashMap<String, usize>)> {
        // Convert PyToken to internal Token
        let mut rust_tokens: Vec<Token> = tokens.into_iter().map(|t| t.into()).collect();

        // Compute bracket pairs for the tokens.
        compute_bracket_pairs(&mut rust_tokens);

        // Create parser
        let mut parser = Parser::new(&rust_tokens, self.dialect, self.indent_config.clone());

        // Parse and get the MatchResult directly
        let match_result = parser
            .call_rule_as_root_match_result()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.message))?;

        // Collect statistics
        let (cache_hits, cache_misses, _) = parser.table_cache.stats();
        let cache_entries = parser.table_cache.len();

        let mut stats = std::collections::HashMap::new();
        stats.insert("cache_hits".to_string(), cache_hits);
        stats.insert("cache_misses".to_string(), cache_misses);
        stats.insert("cache_entries".to_string(), cache_entries);
        stats.insert("pruning_calls".to_string(), parser.pruning_calls.get());
        stats.insert("pruning_total".to_string(), parser.pruning_total.get());
        stats.insert("pruning_kept".to_string(), parser.pruning_kept.get());
        stats.insert("pruning_hinted".to_string(), parser.pruning_hinted.get());
        stats.insert("pruning_complex".to_string(), parser.pruning_complex.get());
        stats.insert("match_attempts".to_string(), parser.match_attempts.get());
        stats.insert("match_successes".to_string(), parser.match_successes.get());
        stats.insert(
            "complete_match_early_exits".to_string(),
            parser.complete_match_early_exits.get(),
        );
        stats.insert(
            "terminator_checks".to_string(),
            parser.terminator_checks.get(),
        );
        stats.insert("terminator_hits".to_string(), parser.terminator_hits.get());

        Ok((PyMatchResult(match_result), stats))
    }

    /// Parse SQL from tokens and return grammar call counts for debugging.
    ///
    /// Returns a tuple: (PyMatchResult, grammar_counts_dict)
    /// where grammar_counts_dict maps grammar names to call counts.
    ///
    /// This is used to identify which grammars are called most frequently,
    /// helping debug performance differences between Python and Rust parsers.
    pub fn parse_match_result_with_grammar_counts(
        &self,
        tokens: Vec<PyToken>,
    ) -> PyResult<(PyMatchResult, std::collections::HashMap<String, usize>)> {
        // Convert PyToken to internal Token
        let mut rust_tokens: Vec<Token> = tokens.into_iter().map(|t| t.into()).collect();

        // Compute bracket pairs for the tokens.
        compute_bracket_pairs(&mut rust_tokens);

        // Create parser with grammar counting enabled
        let mut parser = Parser::new(&rust_tokens, self.dialect, self.indent_config.clone());

        // Track grammar calls using cache misses as a proxy
        // Each unique (grammar_id, pos) pair in the cache represents one grammar call
        let match_result = parser
            .call_rule_as_root_match_result()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.message))?;

        // Count calls per grammar by iterating cache entries
        let mut grammar_counts = std::collections::HashMap::new();

        for (key, _result) in parser.table_cache.iter() {
            let grammar_id = sqlfluffrs_types::GrammarId(key.grammar_id);

            // Skip invalid grammar IDs (can happen during failed parse attempts)
            if grammar_id.get() as usize >= parser.grammar_ctx.len() {
                continue;
            }

            // Use grammar_id_name which handles all variants (Ref, StringParser, etc.)
            let grammar_name = parser.grammar_ctx.grammar_id_name(grammar_id);
            *grammar_counts.entry(grammar_name).or_insert(0) += 1;
        }

        Ok((PyMatchResult(match_result), grammar_counts))
    }
}

/// Compute matching bracket indices for all bracket tokens.
///
/// This function sets `matching_bracket_idx` on each opening and closing bracket
/// to point to its matching counterpart. This is used by the parser's
/// `find_matching_bracket` function for O(1) bracket pair lookup.
///
/// This is necessary when tokens come from Python (via PyToken -> Token conversion)
/// because the Python lexer doesn't compute these indices.
fn compute_bracket_pairs(tokens: &mut [Token]) {
    // Stack to track opening brackets: (index, bracket_char)
    let mut bracket_stack: Vec<(usize, char)> = Vec::new();

    for idx in 0..tokens.len() {
        let raw = tokens[idx].raw();

        // Check if this is an opening bracket
        if let Some(open_char) = match raw.as_str() {
            "(" => Some('('),
            "[" => Some('['),
            "{" => Some('{'),
            _ => None,
        } {
            bracket_stack.push((idx, open_char));
        }
        // Check if this is a closing bracket
        else if let Some(expected_open) = match raw.as_str() {
            ")" => Some('('),
            "]" => Some('['),
            "}" => Some('{'),
            _ => None,
        } {
            // Try to match with the most recent opening bracket of the same type
            if let Some(pos) = bracket_stack.iter().rposition(|(_, c)| *c == expected_open) {
                let (open_idx, _) = bracket_stack.remove(pos);
                // Set bidirectional pointers
                tokens[open_idx].matching_bracket_idx = Some(idx);
                tokens[idx].matching_bracket_idx = Some(open_idx);
            }
            // If no matching opening bracket, leave as None (syntax error)
        }
    }
    // Any remaining opening brackets on the stack are unmatched - leave as None
}
