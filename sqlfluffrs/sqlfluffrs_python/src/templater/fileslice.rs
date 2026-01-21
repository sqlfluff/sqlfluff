use pyo3::{prelude::*, types::PyBytes};
use serde::{Deserialize, Serialize};

use crate::slice::PySlice;
use sqlfluffrs_types::templater::fileslice::{RawFileSlice, TemplatedFileSlice};

#[pyclass(name = "RsRawFileSlice", module = "sqlfluffrs")]
#[repr(transparent)]
#[derive(Clone, Debug, PartialEq, Hash, Serialize, Deserialize)]
pub struct PyRawFileSlice(pub(crate) RawFileSlice);

#[pymethods]
impl PyRawFileSlice {
    #[new]
    #[pyo3(signature = (raw, slice_type, source_idx, block_idx=0, tag=None))]
    pub fn new(
        raw: String,
        slice_type: String,
        source_idx: usize,
        block_idx: Option<usize>,
        tag: Option<String>,
    ) -> Self {
        Self(RawFileSlice::new(
            raw, slice_type, source_idx, block_idx, tag,
        ))
    }

    pub fn __setstate__(&mut self, state: Bound<'_, PyBytes>) -> PyResult<()> {
        *self = bincode::deserialize(state.as_bytes()).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyException, _>(format!("Deserialization error: {}", e))
        })?;
        Ok(())
    }

    pub fn __getstate__<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyBytes>> {
        let bytes = bincode::serialize(&self.0).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyException, _>(format!("Serialization error: {}", e))
        })?;
        Ok(PyBytes::new(py, &bytes))
    }

    pub fn __getnewargs__(&self) -> PyResult<(String, String, usize, usize, Option<String>)> {
        Ok((
            self.raw(),
            self.slice_type(),
            self.source_idx(),
            self.block_idx(),
            self.tag(),
        ))
    }

    #[getter]
    pub fn raw(&self) -> String {
        self.0.raw.clone()
    }
    #[getter]
    pub fn slice_type(&self) -> String {
        self.0.slice_type.clone()
    }
    #[getter]
    pub fn source_idx(&self) -> usize {
        self.0.source_idx
    }
    #[getter]
    pub fn block_idx(&self) -> usize {
        self.0.block_idx
    }
    #[getter]
    pub fn tag(&self) -> Option<String> {
        self.0.tag.clone()
    }
}

impl From<PyRawFileSlice> for RawFileSlice {
    fn from(value: PyRawFileSlice) -> Self {
        value.0
    }
}

impl From<RawFileSlice> for PyRawFileSlice {
    fn from(value: RawFileSlice) -> Self {
        Self(value)
    }
}

#[pyclass(name = "RsTemplatedFileSlice", module = "sqlfluffrs")]
#[repr(transparent)]
#[derive(Clone, Debug, PartialEq, Hash, Serialize, Deserialize)]
pub struct PyTemplatedFileSlice(pub(crate) TemplatedFileSlice);

#[pymethods]
impl PyTemplatedFileSlice {
    #[new]
    fn new(
        slice_type: String,
        source_codepoint_slice: PySlice,
        templated_codepoint_slice: PySlice,
    ) -> Self {
        Self(TemplatedFileSlice::new(
            slice_type,
            source_codepoint_slice.0,
            templated_codepoint_slice.0,
        ))
    }
    pub fn __setstate__(&mut self, state: Bound<'_, PyBytes>) -> PyResult<()> {
        *self = bincode::deserialize(state.as_bytes()).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyException, _>(format!("Deserialization error: {}", e))
        })?;
        Ok(())
    }

    pub fn __getstate__<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyBytes>> {
        let bytes = bincode::serialize(&self.0).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyException, _>(format!("Serialization error: {}", e))
        })?;
        Ok(PyBytes::new(py, &bytes))
    }

    pub fn __getnewargs__(&self) -> PyResult<(String, PySlice, PySlice)> {
        Ok((
            self.0.slice_type.clone(),
            PySlice(self.0.source_codepoint_slice),
            PySlice(self.0.templated_codepoint_slice),
        ))
    }

    #[getter]
    fn slice_type(&self) -> PyResult<String> {
        Ok(self.0.slice_type.clone())
    }

    #[getter]
    fn source_slice(&self) -> PyResult<PySlice> {
        Ok(PySlice(self.0.source_codepoint_slice))
    }

    #[getter]
    fn templated_slice(&self) -> PyResult<PySlice> {
        Ok(PySlice(self.0.templated_codepoint_slice))
    }
}

impl From<PyTemplatedFileSlice> for TemplatedFileSlice {
    fn from(value: PyTemplatedFileSlice) -> Self {
        value.0
    }
}

impl From<TemplatedFileSlice> for PyTemplatedFileSlice {
    fn from(value: TemplatedFileSlice) -> Self {
        Self(value)
    }
}

pub mod sqlfluff {
    use pyo3::prelude::*;

    use sqlfluffrs_types::templater::fileslice::{RawFileSlice, TemplatedFileSlice};

    use super::{PyRawFileSlice, PyTemplatedFileSlice};

    #[derive(Clone, IntoPyObject)]
    pub struct PySqlFluffTemplatedFileSlice(pub PyTemplatedFileSlice);

    impl<'py> FromPyObject<'py> for PySqlFluffTemplatedFileSlice {
        fn extract_bound(obj: &pyo3::Bound<'py, pyo3::PyAny>) -> PyResult<Self> {
            let slice_type = obj.getattr("slice_type")?.extract::<String>()?;
            let source_slice = obj
                .getattr("source_slice")?
                .extract::<crate::slice::PySlice>()?;
            let templated_slice = obj
                .getattr("templated_slice")?
                .extract::<crate::slice::PySlice>()?;

            Ok(Self(PyTemplatedFileSlice(TemplatedFileSlice::new(
                slice_type,
                source_slice.0,
                templated_slice.0,
            ))))
        }
    }

    impl From<PySqlFluffTemplatedFileSlice> for PyTemplatedFileSlice {
        fn from(value: PySqlFluffTemplatedFileSlice) -> Self {
            value.0
        }
    }

    impl From<PySqlFluffTemplatedFileSlice> for TemplatedFileSlice {
        fn from(value: PySqlFluffTemplatedFileSlice) -> Self {
            value.0 .0
        }
    }

    #[derive(Clone)]
    pub struct PySqlFluffRawFileSlice(pub PyRawFileSlice);

    impl<'py> FromPyObject<'py> for PySqlFluffRawFileSlice {
        fn extract_bound(obj: &pyo3::Bound<'py, pyo3::PyAny>) -> PyResult<Self> {
            let raw = obj.getattr("raw")?.extract::<String>()?;
            let slice_type = obj.getattr("slice_type")?.extract::<String>()?;
            let source_idx = obj.getattr("source_idx")?.extract::<usize>().ok();
            let block_idx = obj.getattr("block_idx")?.extract::<usize>().ok();
            let tag = obj.getattr("tag")?.extract::<Option<String>>()?;

            Ok(Self(PyRawFileSlice(RawFileSlice::new(
                raw.clone(),
                slice_type,
                source_idx.unwrap_or(raw.len()),
                block_idx,
                tag,
            ))))
        }
    }

    impl From<PySqlFluffRawFileSlice> for PyRawFileSlice {
        fn from(value: PySqlFluffRawFileSlice) -> Self {
            value.0
        }
    }

    impl From<PySqlFluffRawFileSlice> for RawFileSlice {
        fn from(value: PySqlFluffRawFileSlice) -> Self {
            value.0 .0
        }
    }
}
