use std::{fmt::Display, sync::Arc};

use hashbrown::HashMap;
use pyo3::{prelude::*, types::PyType};

use crate::slice::PySlice;
use crate::templater::templatefile::{PySqlFluffTemplatedFile, PyTemplatedFile};

use sqlfluffrs_types::marker::PositionMarker as RsPositionMarker;
use sqlfluffrs_types::templater::templatefile::TemplatedFile as RsTemplatedFile;

#[pyclass(name = "RsPositionMarker", str, eq, ord, frozen, module = "sqlfluffrs")]
#[repr(transparent)]
#[derive(Debug, Clone)]
pub struct PyPositionMarker(pub RsPositionMarker);

#[pymethods]
impl PyPositionMarker {
    #[getter]
    pub fn source_slice(&self) -> PySlice {
        PySlice(self.0.source_slice)
    }

    #[getter]
    pub fn templated_slice(&self) -> PySlice {
        PySlice(self.0.templated_slice)
    }

    #[getter]
    pub fn templated_file(&self) -> PyTemplatedFile {
        PyTemplatedFile(self.0.templated_file.clone())
    }

    #[getter]
    pub fn working_line_no(&self) -> usize {
        self.0.working_line_no
    }

    #[getter]
    pub fn working_line_pos(&self) -> usize {
        self.0.working_line_pos
    }

    #[getter]
    pub fn working_loc(&self) -> (usize, usize) {
        (self.0.working_line_no, self.0.working_line_pos)
    }

    pub fn start_point_marker(&self) -> Self {
        Self(self.0.start_point_marker())
    }

    pub fn end_point_marker(&self) -> Self {
        Self(self.0.end_point_marker())
    }

    pub fn source_position(&self) -> (usize, usize) {
        self.0.source_position()
    }

    pub fn templated_position(&self) -> (usize, usize) {
        self.0.templated_position()
    }

    pub fn is_literal(&self) -> bool {
        self.0.is_literal()
    }

    pub fn with_working_position(&self, line_no: usize, line_pos: usize) -> Self {
        Self(self.0.with_working_position(line_no, line_pos))
    }

    pub fn infer_next_position(
        &self,
        raw: &str,
        line_no: usize,
        line_pos: usize,
    ) -> (usize, usize) {
        self.0.infer_next_position(raw, line_no, line_pos)
    }

    pub fn line_no(&self) -> usize {
        self.0.line_no()
    }

    pub fn line_pos(&self) -> usize {
        self.0.line_pos()
    }

    pub fn source_str(&self) -> String {
        self.0.source_str()
    }

    pub fn to_source_dict(&self) -> HashMap<String, usize> {
        self.0.to_source_dict()
    }

    #[classmethod]
    #[pyo3(signature = (markers))]
    pub fn from_child_markers(
        _cls: &Bound<'_, PyType>,
        markers: Vec<Option<PyPositionMarker>>,
    ) -> PyResult<Self> {
        let rust_markers: Vec<Option<RsPositionMarker>> =
            markers.into_iter().map(|m| m.map(Into::into)).collect();
        Ok(Self(RsPositionMarker::from_child_markers(&rust_markers)))
    }

    #[classmethod]
    pub fn from_point(
        _cls: &Bound<'_, PyType>,
        source_point: usize,
        templated_point: usize,
        templated_file: PySqlFluffTemplatedFile,
        working_line_no: Option<usize>,
        working_line_pos: Option<usize>,
    ) -> Self {
        let templated_file: Arc<RsTemplatedFile> = templated_file.into();
        Self(RsPositionMarker::from_point(
            source_point,
            templated_point,
            &templated_file,
            working_line_no,
            working_line_pos,
        ))
    }

    #[classmethod]
    pub fn from_points(
        _cls: &Bound<'_, PyType>,
        start_marker: &PyPositionMarker,
        end_marker: &PyPositionMarker,
    ) -> Self {
        Self(RsPositionMarker::from_points(
            &start_marker.0,
            &end_marker.0,
        ))
    }

    pub fn is_point(&self) -> bool {
        self.0.is_point()
    }

    pub fn to_source_string(&self) -> String {
        self.0.to_source_string()
    }
}

impl Display for PyPositionMarker {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.0.to_source_string())
    }
}

impl From<PyPositionMarker> for PySqlFluffTemplatedFile {
    fn from(value: PyPositionMarker) -> Self {
        PySqlFluffTemplatedFile(PyTemplatedFile::from(value.0.templated_file.clone()))
    }
}

impl From<PyPositionMarker> for RsPositionMarker {
    fn from(value: PyPositionMarker) -> Self {
        value.0
    }
}

impl From<RsPositionMarker> for PyPositionMarker {
    fn from(value: RsPositionMarker) -> Self {
        Self(value)
    }
}

impl PartialEq for PyPositionMarker {
    fn eq(&self, other: &Self) -> bool {
        self.0.eq(&other.0)
    }
}

impl PartialOrd for PyPositionMarker {
    fn partial_cmp(&self, other: &Self) -> Option<std::cmp::Ordering> {
        self.0.partial_cmp(&other.0)
    }
}

#[derive(Clone, IntoPyObject, Debug)]
pub struct PySqlFluffPositionMarker(pub PyPositionMarker);

impl<'py> FromPyObject<'py> for PySqlFluffPositionMarker {
    fn extract_bound(obj: &pyo3::Bound<'py, pyo3::PyAny>) -> PyResult<Self> {
        let source_slice = obj.getattr("source_slice")?.extract::<PySlice>()?.0;
        let templated_slice = obj.getattr("templated_slice")?.extract::<PySlice>()?.0;
        let templated_file: Arc<RsTemplatedFile> = obj
            .getattr("templated_file")?
            .extract::<PySqlFluffTemplatedFile>()?
            .into();

        Ok(Self(PyPositionMarker(RsPositionMarker::new(
            source_slice,
            templated_slice,
            &templated_file,
            None,
            None,
        ))))
    }
}

impl From<PySqlFluffPositionMarker> for PyPositionMarker {
    fn from(value: PySqlFluffPositionMarker) -> Self {
        value.0
    }
}

impl From<PySqlFluffPositionMarker> for RsPositionMarker {
    fn from(value: PySqlFluffPositionMarker) -> Self {
        value.0 .0
    }
}
