use pyo3::prelude::*;
use pyo3::types::PySlice as PySliceType;

use sqlfluffrs_types::slice::Slice as RsSlice;

#[derive(Clone, Copy, Debug)]
pub struct PySlice(pub RsSlice);

impl From<PySlice> for RsSlice {
    fn from(value: PySlice) -> Self {
        value.0
    }
}

impl From<RsSlice> for PySlice {
    fn from(value: RsSlice) -> Self {
        PySlice(value)
    }
}

impl<'py> FromPyObject<'py> for PySlice {
    fn extract_bound(obj: &pyo3::Bound<'py, pyo3::PyAny>) -> PyResult<Self> {
        let start = obj.getattr("start")?.extract::<usize>()?;
        let stop = obj.getattr("stop")?.extract::<usize>()?;
        Ok(PySlice(RsSlice { start, stop }))
    }
}

impl<'py> IntoPyObject<'py> for PySlice {
    type Target = PySliceType;
    type Output = Bound<'py, Self::Target>;
    type Error = PyErr;

    fn into_pyobject(self, py: Python<'py>) -> Result<Self::Output, Self::Error> {
        Ok(PySliceType::new(
            py,
            self.0.start.try_into()?,
            self.0.stop.try_into()?,
            1,
        ))
    }
}

impl std::fmt::Display for PySlice {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "slice({}, {}, None)", self.0.start, self.0.stop)
    }
}
