use hashbrown::HashMap;
use pyo3::exceptions::PyException;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};

use crate::parser::MetaSegment;

use super::match_result::MatchResult;
use super::types::NodeTupleValue;
use super::{Node, ParseError, Parser};
use sqlfluffrs_dialects::Dialect;
use sqlfluffrs_python::token::PyToken;
use sqlfluffrs_types::Token;
use std::str::FromStr;

// Create a custom Python exception for parse errors with position info
pyo3::create_exception!(
    sqlfluffrs,
    RsParseError,
    PyException,
    "Rust parser error with position information"
);

/// Helper to convert ParseError to Python exception with position attribute
fn parse_error_to_pyerr(e: ParseError) -> PyErr {
    Python::attach(|py| {
        // Create the exception
        let exc = RsParseError::new_err(e.message.clone());

        // If we have position info, set it as an attribute
        if let Some(pos) = e.pos {
            let _ = exc.value(py).setattr("pos", pos);
        }

        exc
    })
}

/// Python-wrapped Node for AST representation
#[pyclass(name = "RsNode", module = "sqlfluffrs", from_py_object)]
#[derive(Clone)]
pub struct PyNode(pub Node);

#[pymethods]
impl PyNode {
    /// Get the node type as a string
    #[getter]
    fn node_type(&self) -> String {
        match &self.0 {
            Node::Raw { .. } => "raw".to_string(),
            Node::Segment { .. } => "segment".to_string(),
            Node::Meta { .. } => "meta".to_string(),
            Node::Unparsable { .. } => "unparsable".to_string(),
            Node::Empty => "empty".to_string(),
        }
    }

    /// Get the segment type (semantic type like "keyword", "select_statement", etc.)
    #[getter]
    fn segment_type(&self) -> Option<String> {
        self.0.segment_type().map(|s| s.to_string())
    }

    /// Get the segment class name (e.g., "KeywordSegment", "SelectStatementSegment")
    #[getter]
    fn segment_class(&self) -> Option<String> {
        match &self.0 {
            Node::Raw { segment_class, .. } | Node::Segment { segment_class, .. } => {
                Some(segment_class.clone())
            }
            _ => None,
        }
    }

    /// Get raw text of this node (recursively joins children for containers)
    #[getter]
    fn raw(&self) -> String {
        self.0.raw()
    }

    /// Check if node is empty
    fn is_empty(&self) -> bool {
        self.0.is_empty()
    }

    /// Check if node is code (not whitespace/meta)
    fn is_code(&self) -> bool {
        self.0.is_code()
    }

    /// Get children nodes (for Segment and Unparsable nodes)
    fn children(&self) -> Option<Vec<PyNode>> {
        match &self.0 {
            Node::Segment { children, .. } | Node::Unparsable { children, .. } => {
                Some(children.iter().map(|n| PyNode(n.clone())).collect())
            }
            _ => None,
        }
    }

    /// Get instance_types (for Raw nodes)
    fn instance_types(&self) -> Option<Vec<String>> {
        match &self.0 {
            Node::Raw { instance_types, .. } => Some(instance_types.clone()),
            _ => None,
        }
    }

    /// Get class_types — mirrors Python's class_types property.
    fn class_types(&self) -> Option<Vec<String>> {
        match &self.0 {
            Node::Raw { class_types, .. } => Some(class_types.clone()),
            Node::Segment { class_types, .. } => {
                if class_types.is_empty() {
                    None
                } else {
                    Some(class_types.clone())
                }
            }
            _ => None,
        }
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
        Self::tuple_value_to_python(py, &tuple_val)
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
                let py_obj = Self::yaml_to_python(py, &yaml_val)?;
                Ok(Some(py_obj))
            }
            None => Ok(None),
        }
    }

    /// Represent node as string
    fn __repr__(&self) -> String {
        match &self.0 {
            Node::Raw {
                segment_type, raw, ..
            } => {
                format!("RsNode(Raw(type='{}', raw='{}'))", segment_type, raw)
            }
            Node::Segment {
                segment_class,
                children,
                ..
            } => {
                format!(
                    "RsNode(Segment(class='{}', {} children))",
                    segment_class,
                    children.len()
                )
            }
            Node::Meta { meta_type, .. } => {
                format!("RsNode(Meta({:?}))", meta_type)
            }
            Node::Unparsable {
                expected, children, ..
            } => {
                format!(
                    "RsNode(Unparsable(expected='{}', {} children))",
                    expected,
                    children.len()
                )
            }
            Node::Empty => "RsNode(Empty)".to_string(),
        }
    }

    /// String representation
    fn __str__(&self) -> String {
        self.__repr__()
    }
}

impl PyNode {
    fn tuple_value_to_python(py: Python, val: &NodeTupleValue) -> PyResult<Py<PyAny>> {
        match val {
            NodeTupleValue::Raw(key, s) => Ok((key, s).into_pyobject(py)?.into()),
            NodeTupleValue::Tuple(key, children) => {
                let py_children = PyList::empty(py);
                for child in children {
                    py_children.append(Self::tuple_value_to_python(py, child)?)?;
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
#[pyclass(name = "RsParseError", module = "sqlfluffrs", extends=PyException, from_py_object)]
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
#[pyclass(name = "RsMatchResult", module = "sqlfluffrs", frozen, from_py_object)]
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
        self.0.matched_class.as_ref().map(|s| s.class_name.clone())
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
        self.0
            .matched_class
            .as_ref()
            .and_then(|s| s.segment_kwargs.instance_types.clone())
    }

    /// Get trim_chars for the segment
    #[getter]
    fn trim_chars(&self) -> Option<Vec<String>> {
        self.0
            .matched_class
            .as_ref()
            .and_then(|s| s.segment_kwargs.trim_chars.clone())
    }

    /// Get casefold mode (for case-insensitive matching)
    #[getter]
    fn casefold(&self) -> Option<String> {
        match self
            .0
            .matched_class
            .as_ref()
            .map(|s| s.segment_kwargs.casefold.clone())
            .unwrap_or_default()
        {
            sqlfluffrs_types::token::CaseFold::None => None,
            sqlfluffrs_types::token::CaseFold::Upper => Some("upper".to_string()),
            sqlfluffrs_types::token::CaseFold::Lower => Some("lower".to_string()),
        }
    }

    /// Get quoted_value for identifier normalization
    #[getter]
    fn quoted_value(&self, py: Python<'_>) -> Option<(String, Py<PyAny>)> {
        self.0
            .matched_class
            .as_ref()
            .and_then(|s| s.segment_kwargs.quoted_value.clone())
            .as_ref()
            .map(|(pattern, group)| {
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
        self.0
            .matched_class
            .as_ref()
            .and_then(|s| s.segment_kwargs.escape_replacement.clone())
    }

    /// Get insert_segments (meta segments like Indent/Dedent to insert)
    #[getter]
    fn insert_segments(&self) -> Vec<(usize, String, bool)> {
        self.0
            .insert_segments
            .iter()
            .map(|(idx, seg_type)| {
                let (type_name, is_implicit) = match seg_type {
                    MetaSegment::Indent { is_implicit } => ("indent", is_implicit),
                    MetaSegment::Dedent { is_implicit } => ("dedent", is_implicit),
                };
                (*idx, type_name.to_string(), *is_implicit)
            })
            .collect()
    }

    /// Get parse_error (error message and token position) if present
    #[getter]
    fn parse_error(&self) -> Option<(String, usize)> {
        self.0
            .matched_class
            .as_ref()
            .and_then(|s| s.segment_kwargs.parse_error.clone())
    }

    /// Get segment_kwargs dictionary (e.g., parsed properties for segments)
    #[getter]
    fn segment_kwargs(&self, py: Python) -> PyResult<Py<PyAny>> {
        let dict = PyDict::new(py);

        if let Some(matched_class) = self.0.matched_class.as_ref() {
            let sk = &matched_class.segment_kwargs;

            if let Some((ref msg, _pos)) = sk.parse_error.as_ref() {
                dict.set_item("expected", msg.clone())?;
            }
        }

        Ok(dict.into())
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

    /// Build the full AST as an `RsNode` from this MatchResult and tokens.
    ///
    /// Applies the match result against the provided tokens to construct the
    /// complete Rust-side AST which can be used by Rust linting rules
    /// (e.g., respace/LT01) without round-tripping through Python's segment
    /// tree. Optionally prepend `leading` and append `trailing` non-code
    /// tokens to the root.
    ///
    /// This is the single PyO3 entry-point for node construction.
    #[pyo3(signature = (tokens, leading=vec![], trailing=vec![]))]
    fn apply_as_node(
        &self,
        tokens: Vec<PyToken>,
        leading: Vec<PyToken>,
        trailing: Vec<PyToken>,
    ) -> PyNode {
        let rust_leading: Vec<Token> = leading.into_iter().map(|t| t.into()).collect();
        let rust_tokens: Vec<Token> = tokens.into_iter().map(|t| t.into()).collect();
        let rust_trailing: Vec<Token> = trailing.into_iter().map(|t| t.into()).collect();
        let node = self
            .0
            .clone()
            .apply_as_root(&rust_tokens, &rust_leading, &rust_trailing);
        PyNode(node)
    }
}

/// Python-wrapped Parser
#[pyclass(name = "RsParser", module = "sqlfluffrs")]
pub struct PyParser {
    dialect: Dialect,
    indent_config: hashbrown::HashMap<&'static str, bool>,
    max_parser_iterations: usize,
    parser_warn_threshold: usize,
    max_parse_depth: usize,
    max_parse_nodes: usize,
}

#[pymethods]
impl PyParser {
    #[new]
    #[pyo3(signature = (dialect=None, indent_config=None, max_parser_iterations=None, parser_warn_threshold=None, max_parse_depth=0, max_parse_nodes=0))]
    pub fn new(
        dialect: Option<&str>,
        indent_config: Option<HashMap<String, bool>>,
        max_parser_iterations: Option<usize>,
        parser_warn_threshold: Option<usize>,
        max_parse_depth: usize,
        max_parse_nodes: usize,
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
            max_parser_iterations: max_parser_iterations.unwrap_or(3_000_000),
            parser_warn_threshold: parser_warn_threshold.unwrap_or(2_000_000),
            max_parse_depth,
            max_parse_nodes,
        })
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
        let mut parser = Parser::new_with_max_parse_depth(
            &rust_tokens,
            self.dialect,
            self.indent_config.clone(),
            self.max_parse_depth,
        )
        .with_parser_limits(self.max_parser_iterations, self.parser_warn_threshold)
        .with_node_limit(self.max_parse_nodes);

        // Parse and get the MatchResult directly
        let match_result = parser.call_rule_as_root().map_err(parse_error_to_pyerr)?;

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
    ) -> PyResult<(PyMatchResult, HashMap<String, usize>)> {
        // Convert PyToken to internal Token
        let mut rust_tokens: Vec<Token> = tokens.into_iter().map(|t| t.into()).collect();

        // Compute bracket pairs for the tokens.
        compute_bracket_pairs(&mut rust_tokens);

        // Create parser
        let mut parser = Parser::new_with_max_parse_depth(
            &rust_tokens,
            self.dialect,
            self.indent_config.clone(),
            self.max_parse_depth,
        )
        .with_parser_limits(self.max_parser_iterations, self.parser_warn_threshold)
        .with_node_limit(self.max_parse_nodes);

        // Parse and get the MatchResult directly
        let match_result = parser
            .call_rule_as_root()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.message))?;

        // Collect statistics
        let (cache_hits, cache_misses, _) = parser.table_cache.stats();
        let cache_entries = parser.table_cache.len();

        let mut stats = HashMap::new();
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
    ) -> PyResult<(PyMatchResult, HashMap<String, usize>)> {
        // Convert PyToken to internal Token
        let mut rust_tokens: Vec<Token> = tokens.into_iter().map(|t| t.into()).collect();

        // Compute bracket pairs for the tokens.
        compute_bracket_pairs(&mut rust_tokens);

        // Create parser with grammar counting enabled
        let mut parser = Parser::new_with_max_parse_depth(
            &rust_tokens,
            self.dialect,
            self.indent_config.clone(),
            self.max_parse_depth,
        )
        .with_parser_limits(self.max_parser_iterations, self.parser_warn_threshold)
        .with_node_limit(self.max_parse_nodes);

        // Track grammar calls using cache misses as a proxy
        // Each unique (grammar_id, pos) pair in the cache represents one grammar call
        let match_result = parser
            .call_rule_as_root()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.message))?;

        // Count calls per grammar by iterating cache entries
        let mut grammar_counts = HashMap::new();

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
