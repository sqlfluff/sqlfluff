use std::{
    fmt::{Debug, Display},
    sync::Arc,
};

use hashbrown::HashSet;
use pyo3::{
    prelude::*,
    types::{PyDict, PyString, PyTuple, PyType},
};
use uuid::Uuid;

use crate::{
    marker::python::{PyPositionMarker, PySqlFluffPositionMarker},
    regex::RegexModeGroup,
};

use super::{path::PathStep, CaseFold, SourceFix, Token, TupleSerialisedSegment};

/// Python wrapper for the CaseFold enum
#[pyclass(name = "RsCaseFold", module = "sqlfluffrs")]
#[derive(Debug, Clone, PartialEq)]
pub struct PyCaseFold(pub CaseFold);

#[pymethods]
impl PyCaseFold {
    #[new]
    fn new() -> Self {
        PyCaseFold(CaseFold::None)
    }

    #[staticmethod]
    fn none() -> Self {
        PyCaseFold(CaseFold::None)
    }

    #[staticmethod]
    fn upper() -> Self {
        PyCaseFold(CaseFold::Upper)
    }

    #[staticmethod]
    fn lower() -> Self {
        PyCaseFold(CaseFold::Lower)
    }

    fn __repr__(&self) -> String {
        match self.0 {
            CaseFold::None => "RsCaseFold.None".to_string(),
            CaseFold::Upper => "RsCaseFold.Upper".to_string(),
            CaseFold::Lower => "RsCaseFold.Lower".to_string(),
        }
    }

    fn __str__(&self) -> String {
        self.__repr__()
    }

    fn __eq__(&self, other: &Self) -> bool {
        self.0 == other.0
    }
}

impl From<CaseFold> for PyCaseFold {
    fn from(value: CaseFold) -> Self {
        PyCaseFold(value)
    }
}

impl From<PyCaseFold> for CaseFold {
    fn from(value: PyCaseFold) -> Self {
        value.0
    }
}

#[pyclass(name = "RsSourceFix")]
#[repr(transparent)]
#[derive(Clone)]
pub struct PySourceFix(pub SourceFix);

impl From<PySourceFix> for SourceFix {
    fn from(value: PySourceFix) -> SourceFix {
        value.0
    }
}

impl From<SourceFix> for PySourceFix {
    fn from(value: SourceFix) -> Self {
        Self(value)
    }
}

#[pyclass(name = "RsPathStep")]
#[repr(transparent)]
#[derive(Clone)]
pub struct PyPathStep(pub PathStep);

impl From<PyPathStep> for PathStep {
    fn from(value: PyPathStep) -> Self {
        value.0
    }
}

impl From<PathStep> for PyPathStep {
    fn from(value: PathStep) -> Self {
        Self(value)
    }
}

#[pyclass(name = "RsTupleSerialisedSegment")]
#[repr(transparent)]
#[derive(Clone)]
pub struct PyTupleSerialisedSegment(pub TupleSerialisedSegment);

impl PyTupleSerialisedSegment {
    pub fn to_py_tuple<'py>(&self, py: Python<'py>) -> Result<Bound<'py, PyTuple>, PyErr> {
        match &self.0 {
            TupleSerialisedSegment::Str(segment_type, raw_value) => {
                PyTuple::new(py, [segment_type, raw_value])
            }
            TupleSerialisedSegment::Nested(segment_type, segments) => {
                let py_segment_type = PyString::new(py, segment_type);
                let py_segments: Vec<_> = segments
                    .iter()
                    .map(|s| {
                        PyTupleSerialisedSegment::to_py_tuple(
                            &PyTupleSerialisedSegment(s.clone()),
                            py,
                        )
                    })
                    .collect::<Result<Vec<_>, _>>()?;
                let pt_segments_tuple = PyTuple::new(py, &py_segments)?;

                PyTuple::new(
                    py,
                    &[py_segment_type.into_any(), pt_segments_tuple.into_any()],
                )
            }
        }
    }
}

impl From<PyTupleSerialisedSegment> for TupleSerialisedSegment {
    fn from(value: PyTupleSerialisedSegment) -> Self {
        value.0
    }
}

impl From<TupleSerialisedSegment> for PyTupleSerialisedSegment {
    fn from(value: TupleSerialisedSegment) -> Self {
        Self(value)
    }
}

#[pyclass(name = "RsToken", weakref, module = "sqlfluffrs")]
#[repr(transparent)]
#[derive(Debug, Clone)]
pub struct PyToken(pub Token);

#[pymethods]
impl PyToken {
    #[getter]
    pub fn raw(&self) -> String {
        self.0.raw.to_string()
    }

    pub fn raw_trimmed(&self) -> String {
        self.0.raw_trimmed()
    }

    #[getter]
    pub fn pos_marker(&self) -> Option<PyPositionMarker> {
        self.0.pos_marker.clone().map(PyPositionMarker)
    }

    #[setter]
    pub fn set_pos_marker(&mut self, value: Option<PySqlFluffPositionMarker>) {
        self.0.pos_marker = value.map(Into::into);
    }

    pub fn get_type(&self) -> String {
        self.0.get_type()
    }

    #[getter(r#type)]
    pub fn type_(&self) -> String {
        self.0.get_type()
    }

    #[getter]
    pub fn is_templated(&self) -> bool {
        self.0.is_templated()
    }

    #[getter]
    pub fn is_code(&self) -> bool {
        self.0.is_code
    }

    #[getter]
    pub fn is_meta(&self) -> bool {
        self.0.is_meta
    }

    #[getter]
    pub fn source_str(&self) -> Option<String> {
        self.0.source_str.clone()
    }

    #[getter]
    pub fn block_type(&self) -> Option<String> {
        self.0.block_type()
    }

    #[getter]
    pub fn block_uuid(&self) -> Option<Uuid> {
        self.0.block_uuid
    }

    #[getter]
    pub fn cache_key(&self) -> String {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};

        let mut hasher = DefaultHasher::new();
        self.0.token_type.hash(&mut hasher);
        for t in &self.0.instance_types {
            t.hash(&mut hasher);
        }
        format!("{:016x}", hasher.finish())
    }

    #[getter]
    pub fn trim_start(&self) -> Option<Vec<String>> {
        self.0.trim_start.clone()
    }

    #[getter]
    pub fn trim_chars(&self) -> Option<Vec<String>> {
        self.0.trim_chars.clone()
    }

    #[pyo3(signature = (raw_only = false))]
    pub fn count_segments(&self, raw_only: Option<bool>) -> usize {
        self.0.count_segments(raw_only.unwrap_or_default())
    }

    #[pyo3(signature = (*seg_type))]
    pub fn is_type(&self, seg_type: &Bound<'_, PyTuple>) -> bool {
        let seg_strs = seg_type
            .extract::<Vec<String>>()
            .expect("args should be all strings");
        self.0
            .is_type(&seg_strs.iter().map(String::as_str).collect::<Vec<&str>>())
    }

    #[getter]
    pub fn indent_val(&self) -> i32 {
        self.0.indent_value
    }

    #[getter]
    pub fn is_whitespace(&self) -> bool {
        self.0.is_whitespace
    }

    pub fn is_raw(&self) -> bool {
        self.0.is_raw()
    }

    #[getter]
    pub fn is_comment(&self) -> bool {
        self.0.is_comment
    }

    #[getter]
    pub fn class_types(&self) -> HashSet<String> {
        self.0.class_types()
    }

    #[getter]
    pub fn instance_types(&self) -> Vec<String> {
        self.0.instance_types.clone()
    }

    #[getter]
    pub fn preface_modifier(&self) -> String {
        self.0.preface_modifier.clone()
    }

    #[getter]
    pub fn source_fixes(&self) -> Vec<PySourceFix> {
        self.0.source_fixes().into_iter().map(Into::into).collect()
    }

    #[getter]
    pub fn _source_fixes(&self) -> Option<Vec<PySourceFix>> {
        self.0
            .source_fixes
            .clone()
            .map(|sf| sf.into_iter().map(Into::into).collect())
    }

    #[pyo3(signature = (*seg_type))]
    pub fn class_is_type(&self, seg_type: &Bound<'_, PyTuple>) -> bool {
        let seg_strs = seg_type
            .extract::<Vec<String>>()
            .expect("args should be all strings");
        self.0
            .class_is_type(&seg_strs.iter().map(String::as_str).collect::<Vec<&str>>())
    }

    #[getter]
    pub fn first_non_whitespace_segment_raw_upper(&self) -> Option<String> {
        self.0.first_non_whitespace_segment_raw_upper()
    }

    #[getter]
    pub fn raw_upper(&self) -> String {
        self.0.raw_upper()
    }

    pub fn invalidate_caches(&self) {}

    #[getter]
    pub fn uuid(&self) -> u128 {
        self.0.uuid
    }

    #[getter]
    pub fn descendant_type_set(&self) -> HashSet<String> {
        self.0.descendant_type_set()
    }

    #[pyo3(signature = (*seg_type, recurse_into = true, no_recursive_seg_type = None, allow_self = true))]
    pub fn recursive_crawl(
        &self,
        seg_type: &Bound<'_, PyTuple>,
        recurse_into: bool,
        no_recursive_seg_type: Option<Bound<'_, PyAny>>,
        allow_self: bool,
    ) -> Vec<PyToken> {
        let seg_type = seg_type
            .extract::<Vec<String>>()
            .expect("args should be all strings");
        let temp: Option<Vec<String>> = match no_recursive_seg_type {
            Some(py_any) => {
                if let Ok(single_str) = py_any.extract::<String>() {
                    Some(vec![single_str]) // Convert single string into a Vec<String>
                } else if let Ok(list_of_str) = py_any.extract::<Vec<String>>() {
                    Some(list_of_str) // Already a Vec<String>, return as is
                } else {
                    Some(vec![]) // If it's neither, return an empty vector
                }
            }
            None => None, // If None, return an empty vector
        };
        let no_recursive_seg_type: Option<Vec<&str>> = temp
            .as_ref()
            .map(|vec| vec.iter().map(String::as_str).collect());

        self.0
            .recursive_crawl(
                &seg_type.iter().map(String::as_str).collect::<Vec<&str>>(),
                recurse_into,
                no_recursive_seg_type.as_deref(),
                allow_self,
            )
            .into_iter()
            .map(Into::into)
            .collect()
    }

    pub fn recursive_crawl_all(&self, reverse: bool) -> Vec<PyToken> {
        self.0
            .recursive_crawl_all(reverse)
            .map(|t| t.clone().into())
            .collect()
    }

    #[getter]
    pub fn segments(&self) -> Vec<PyToken> {
        self.0
            .segments
            .clone()
            .into_iter()
            .map(Into::into)
            .collect()
    }

    pub fn path_to(&self, other: PyToken) -> Vec<PyPathStep> {
        self.0
            .clone()
            .path_to(other.into())
            .into_iter()
            .map(Into::into)
            .collect()
    }

    pub fn get_start_loc(&self) -> (usize, usize) {
        self.0.get_start_loc()
    }

    pub fn get_end_loc(&self) -> (usize, usize) {
        self.0.get_end_loc()
    }

    #[getter]
    pub fn raw_segments(&self) -> Vec<PyToken> {
        self.0.raw_segments().into_iter().map(Into::into).collect()
    }

    pub fn _get_raw_segment_kwargs<'py>(&self, py: Python<'py>) -> Bound<'py, PyDict> {
        let dict = PyDict::new(py);
        if let Some(ref quoted_value) = self.0.quoted_value {
            dict.set_item("quoted_value", quoted_value.clone()).unwrap();
        } else {
            dict.set_item("quoted_value", py.None()).unwrap();
        }
        if let Some(ref escape_replacement) = self.0.escape_replacement {
            dict.set_item("escape_replacements", vec![escape_replacement])
                .unwrap();
        } else {
            dict.set_item("escape_replacements", py.None()).unwrap();
        }
        dict
    }

    #[getter]
    pub fn quoted_value(&self, py: Python<'_>) -> Option<(String, Py<PyAny>)> {
        self.0.quoted_value.clone().map(|(s, g)| {
            let py_group: Py<PyAny> = match g {
                RegexModeGroup::Index(idx) => idx.into_pyobject(py).unwrap().into(),
                RegexModeGroup::Name(name) => name.into_pyobject(py).unwrap().into(),
            };
            (s, py_group)
        })
    }

    #[getter]
    pub fn escape_replacements(&self) -> Option<Vec<(String, String)>> {
        if self.0.escape_replacement.is_none() {
            None
        } else {
            Some(vec![self.0.escape_replacement.clone().unwrap()])
        }
    }

    pub fn set_parent(&self, parent: &Bound<'_, PyAny>, idx: usize) -> PyResult<()> {
        let parent: Arc<Token> = parent
            .extract()
            .map(|t: PySqlFluffToken| Arc::new(t.0 .0))?;
        let mut inner = self.0.clone();
        inner.set_parent(parent, idx);
        Ok(())
    }

    pub fn get_parent(&self) -> Option<(PyToken, i32)> {
        None
    }

    pub fn iter_unparsables(&self) -> Vec<PyToken> {
        self.0
            .iter_unparseables()
            .into_iter()
            .map(Into::into)
            .collect()
    }

    #[pyo3(signature = (ident=0, tabsize=4, code_only=false))]
    pub fn stringify(
        &self,
        ident: Option<usize>,
        tabsize: Option<usize>,
        code_only: Option<bool>,
    ) -> String {
        self.0.stringify(
            ident.unwrap_or(0),
            tabsize.unwrap_or(4),
            code_only.unwrap_or_default(),
        )
    }

    #[pyo3(signature = (code_only=None, show_raw=None, include_meta=None))]
    pub fn to_tuple<'py>(
        &self,
        py: Python<'py>,
        code_only: Option<bool>,
        show_raw: Option<bool>,
        include_meta: Option<bool>,
    ) -> Result<Bound<'py, PyTuple>, PyErr> {
        PyTupleSerialisedSegment(self.0.to_tuple(code_only, show_raw, include_meta)).to_py_tuple(py)
    }

    // pub fn structural_simplify(&self) -> HashMap<String, Option<serde_json::Value>> {
    //     self.0
    //         .structural_simplify()
    //         .into_iter()
    //         .map(|(k, v)| (k, v.map(|v| serde_json::to_value(v).unwrap())))
    //         .collect()
    // }

    #[pyo3(signature = (segments=None, parent=None, parent_idx=None))]
    pub fn copy(
        &self,
        segments: Option<Vec<PySqlFluffToken>>,
        parent: Option<PySqlFluffToken>,
        parent_idx: Option<usize>,
    ) -> PyToken {
        PyToken(
            self.0.copy(
                segments.map(|s| s.into_iter().map(Into::into).collect()),
                parent
                    .as_ref()
                    .map(|parent_token| Arc::clone(&parent_token.0 .0.clone().into())),
                parent_idx,
            ),
        )
    }

    #[pyo3(signature = (raw=None, source_fixes=None))]
    pub fn edit(&self, raw: Option<String>, source_fixes: Option<Vec<PySourceFix>>) -> Self {
        Self(self.0.edit(
            raw,
            source_fixes.map(|sf| sf.into_iter().map(Into::into).collect()),
        ))
    }

    #[classmethod]
    pub fn position_segments<'py>(
        _cls: &Bound<'py, PyType>,
        py: Python<'py>,
        segments: Vec<PySqlFluffToken>,
        parent_pos: PySqlFluffPositionMarker,
    ) -> Result<Bound<'py, PyTuple>, PyErr> {
        let tokens = Token::position_segments(
            &segments
                .into_iter()
                .map(|s| s.into())
                .collect::<Vec<Token>>(),
            parent_pos.into(),
        );
        PyTuple::new(
            py,
            tokens.into_iter().map(Into::into).collect::<Vec<PyToken>>(),
        )
    }

    #[staticmethod]
    #[pyo3(signature = (source_slice, templated_slice, block_type, _source_str, block_uuid, templated_file))]
    pub fn template_placeholder_from_slice(
        source_slice: (usize, usize),
        templated_slice: (usize, usize),
        block_type: String,
        _source_str: String, // Currently unused - extracted from templated_file
        block_uuid: Option<String>,
        templated_file: Bound<'_, PyAny>,
    ) -> PyResult<Self> {
        use crate::slice::Slice;
        use crate::templater::templatefile::python::PySqlFluffTemplatedFile;

        // Extract TemplatedFile from Python object
        let tf: PySqlFluffTemplatedFile = templated_file.extract()?;
        let tf_arc: Arc<crate::templater::templatefile::TemplatedFile> = tf.into();

        // Parse UUID if provided (Python passes hex string)
        let uuid = block_uuid.as_ref().and_then(|s| Uuid::parse_str(s).ok());

        // Create template placeholder token using existing constructor
        let token = Token::template_placeholder_token_from_slice(
            Slice {
                start: source_slice.0,
                stop: source_slice.1,
            },
            Slice {
                start: templated_slice.0,
                stop: templated_slice.1,
            },
            block_type,
            &tf_arc,
            uuid,
            HashSet::new(), // class_types - empty for template placeholders
        );

        Ok(PyToken(token))
    }

    pub fn __repr__(&self) -> String {
        format!("{}", self)
    }
}

impl Display for PyToken {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.0)
    }
}

impl From<PyToken> for Token {
    fn from(value: PyToken) -> Token {
        value.0
    }
}

impl From<Token> for PyToken {
    fn from(value: Token) -> Self {
        Self(value)
    }
}

#[derive(IntoPyObject)]
pub struct PySqlFluffToken(pub PyToken);

impl<'py> FromPyObject<'py> for PySqlFluffToken {
    fn extract_bound(ob: &Bound<'py, PyAny>) -> PyResult<Self> {
        let raw = ob.getattr("raw")?.extract::<String>()?;
        let class_types = ob
            .getattr("_class_types")
            .unwrap_or(ob.getattr("class_types")?)
            .extract::<HashSet<String>>()?
            .into_iter()
            .map(|s| s.to_string())
            .collect::<HashSet<String>>();
        let instance_types = ob
            .getattr("instance_types")?
            .extract::<Vec<String>>()?
            .into_iter()
            .map(|s| s.to_string())
            .collect::<Vec<String>>();
        let segments = ob
            .getattr("segments")?
            .extract::<Vec<PySqlFluffToken>>()
            .map(|s| s.into_iter().map(Into::into).collect::<Vec<Token>>())?;
        let pos_marker = ob
            .getattr("pos_marker")?
            .extract::<PySqlFluffPositionMarker>()?;

        use crate::token::config::TokenConfig;
        Ok(Self(PyToken(Token::base_token(
            raw,
            pos_marker.into(),
            TokenConfig {
                class_types,
                instance_types,
                ..TokenConfig::default()
            },
            segments,
        ))))
    }
}

impl From<PySqlFluffToken> for Token {
    fn from(value: PySqlFluffToken) -> Token {
        value.0 .0
    }
}

impl From<Token> for PySqlFluffToken {
    fn from(value: Token) -> Self {
        Self(PyToken(value))
    }
}
