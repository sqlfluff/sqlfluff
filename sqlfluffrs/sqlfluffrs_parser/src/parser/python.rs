use pyo3::exceptions::PyException;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList, PyTuple};

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
    fn to_dict(&self, py: Python) -> PyResult<PyObject> {
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
    ) -> PyResult<PyObject> {
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
    ) -> PyResult<Option<PyObject>> {
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
    fn to_dict_recursive(&self, py: Python, depth: usize, max_depth: usize) -> PyResult<PyObject> {
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

    fn tuple_value_to_python(&self, py: Python, val: &NodeTupleValue) -> PyResult<PyObject> {
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

    fn yaml_to_python(py: Python, val: &serde_yaml_ng::Value) -> PyResult<PyObject> {
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

/// Python-wrapped Parser
#[pyclass(name = "RsParser", module = "sqlfluffrs")]
pub struct PyParser {
    dialect: Dialect,
}

#[pymethods]
impl PyParser {
    #[new]
    #[pyo3(signature = (dialect=None))]
    pub fn new(dialect: Option<&str>) -> PyResult<Self> {
        let dialect = dialect
            .and_then(|d| Dialect::from_str(d).ok())
            .unwrap_or(Dialect::Ansi);

        Ok(PyParser { dialect })
    }

    /// Parse SQL from tokens (standalone mode)
    ///
    /// Takes a list of RsToken objects and returns the parsed AST as RsNode.
    pub fn parse_from_tokens(&self, tokens: Vec<PyToken>) -> PyResult<PyNode> {
        // Convert PyToken to internal Token
        let rust_tokens: Vec<Token> = tokens.into_iter().map(|t| t.into()).collect();

        // Create parser
        let mut parser = Parser::new(&rust_tokens, self.dialect);

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
        let mut parser = Parser::new(&tokens, self.dialect);
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
}
