use std::{fmt::Display, ops::Range};

#[derive(Debug, PartialEq, Hash, Eq, Clone, Copy)]
pub struct Slice {
    pub start: usize,
    pub stop: usize,
}

impl From<Range<usize>> for Slice {
    fn from(value: Range<usize>) -> Self {
        Self {
            start: value.start,
            stop: value.end,
        }
    }
}

impl Slice {
    pub fn slice_is_point(test_slice: &Range<usize>) -> bool {
        test_slice.start == test_slice.end
    }

    pub fn len(&self) -> usize {
        self.stop - self.start
    }
}

impl Display for Slice {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "slice({}, {}, None)", self.start, self.stop)
    }
}

pub mod python {
    use super::Slice;
    use pyo3::{prelude::*, types::PySlice};

    impl<'py> FromPyObject<'py> for Slice {
        fn extract_bound(obj: &pyo3::Bound<'py, pyo3::PyAny>) -> PyResult<Self> {
            let start = obj.getattr("start")?.extract::<usize>()?;
            let stop = obj.getattr("stop")?.extract::<usize>()?;
            Ok(Slice { start, stop })
        }
    }

    impl<'py> IntoPyObject<'py> for Slice {
        type Target = PySlice; // the Python type
        type Output = Bound<'py, Self::Target>; // in most cases this will be `Bound`
        type Error = PyErr; // the conversion error type, has to be convertible to `PyErr`

        fn into_pyobject(self, py: Python<'py>) -> Result<Self::Output, Self::Error> {
            Ok(PySlice::new(
                py,
                self.start.try_into()?,
                self.stop.try_into()?,
                1,
            ))
        }
    }
}
