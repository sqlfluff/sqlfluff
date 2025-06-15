use crate::slice::Slice;

#[derive(Debug, PartialEq, Clone, Hash)]
pub struct RawFileSlice {
    pub raw: String, // Source string
    pub slice_type: String,
    pub source_idx: usize, // Offset from beginning of source string
    // Block index, incremented on start or end block tags, e.g. "if", "for".
    // This is used in `BaseRule.discard_unsafe_fixes()` to reject any fixes
    // which span multiple templated blocks.
    pub block_idx: usize,
    // The command of a templated tag, e.g. "if", "for"
    // This is used in template tracing as a kind of cache to identify the kind
    // of template element this is without having to re-extract it each time.
    pub tag: Option<String>,
}

impl RawFileSlice {
    pub fn new(
        raw: String,
        slice_type: String,
        source_idx: usize,
        block_idx: Option<usize>,
        tag: Option<String>,
    ) -> Self {
        RawFileSlice {
            raw,
            slice_type,
            source_idx,
            block_idx: block_idx.unwrap_or_default(),
            tag,
        }
    }

    pub fn end_source_idx(&self) -> usize {
        // Return the closing index of this slice.
        let len: usize = self.raw.chars().count().try_into().unwrap();
        self.source_idx + len
    }

    pub fn source_slice(&self) -> Slice {
        Slice::from(self.source_idx..self.end_source_idx())
    }

    pub fn is_source_only_slice(&self) -> bool {
        // Based on its slice_type, does it only appear in the *source*?
        // There are some slice types which are automatically source only.
        // There are *also* some which are source only because they render
        // to an empty string.
        // TODO: should any new logic go here?
        match self.slice_type.as_str() {
            "comment" | "block_end" | "block_start" | "block_mid" => true,
            _ => false,
        }
    }
}

#[derive(Debug, PartialEq, Clone, Hash)]
pub struct TemplatedFileSlice {
    pub slice_type: String,
    pub source_codepoint_slice: Slice,
    pub templated_codepoint_slice: Slice,
}

impl TemplatedFileSlice {
    pub fn new(
        slice_type: String,
        source_codepoint_slice: Slice,
        templated_codepoint_slice: Slice,
    ) -> Self {
        TemplatedFileSlice {
            slice_type,
            source_codepoint_slice,
            templated_codepoint_slice,
        }
    }
}

#[cfg(feature = "python")]
pub mod python {
    use pyo3::prelude::*;

    use crate::slice::Slice;

    use super::{RawFileSlice, TemplatedFileSlice};

    #[pyclass(name = "RsRawFileSlice")]
    #[repr(transparent)]
    #[derive(Clone, Debug, PartialEq, Hash)]
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

    impl Into<RawFileSlice> for PyRawFileSlice {
        fn into(self) -> RawFileSlice {
            self.0
        }
    }

    impl From<RawFileSlice> for PyRawFileSlice {
        fn from(value: RawFileSlice) -> Self {
            Self(value)
        }
    }

    #[pyclass(name = "RsTemplatedFileSlice")]
    #[repr(transparent)]
    #[derive(Clone, Debug, PartialEq, Hash)]
    pub struct PyTemplatedFileSlice(pub(crate) TemplatedFileSlice);

    #[pymethods]
    impl PyTemplatedFileSlice {
        #[new]
        fn new(
            slice_type: String,
            source_codepoint_slice: Slice,
            templated_codepoint_slice: Slice,
        ) -> Self {
            Self(TemplatedFileSlice::new(
                slice_type,
                source_codepoint_slice,
                templated_codepoint_slice,
            ))
        }

        #[getter]
        fn slice_type(&self) -> PyResult<String> {
            Ok(self.0.slice_type.clone())
        }

        #[getter]
        fn source_slice(&self) -> PyResult<Slice> {
            Ok(self.0.source_codepoint_slice.clone())
        }

        #[getter]
        fn templated_slice(&self) -> PyResult<Slice> {
            Ok(self.0.templated_codepoint_slice.clone())
        }
    }

    impl Into<TemplatedFileSlice> for PyTemplatedFileSlice {
        fn into(self) -> TemplatedFileSlice {
            self.0
        }
    }

    impl From<TemplatedFileSlice> for PyTemplatedFileSlice {
        fn from(value: TemplatedFileSlice) -> Self {
            Self(value)
        }
    }

    pub mod sqlfluff {
        use pyo3::prelude::*;

        use crate::{
            slice::Slice,
            templater::fileslice::{RawFileSlice, TemplatedFileSlice},
        };

        use super::{PyRawFileSlice, PyTemplatedFileSlice};

        #[derive(Clone, IntoPyObject)]
        pub struct PySqlFluffTemplatedFileSlice(pub PyTemplatedFileSlice);

        impl<'py> FromPyObject<'py> for PySqlFluffTemplatedFileSlice {
            fn extract_bound(obj: &pyo3::Bound<'py, pyo3::PyAny>) -> PyResult<Self> {
                let slice_type = obj.getattr("slice_type")?.extract::<String>()?;
                let source_slice = obj.getattr("source_slice")?.extract::<Slice>()?;
                let templated_slice = obj.getattr("templated_slice")?.extract::<Slice>()?;

                Ok(Self(PyTemplatedFileSlice(TemplatedFileSlice::new(
                    slice_type,
                    source_slice,
                    templated_slice,
                ))))
            }
        }

        impl Into<PyTemplatedFileSlice> for PySqlFluffTemplatedFileSlice {
            fn into(self) -> PyTemplatedFileSlice {
                PyTemplatedFileSlice(self.0 .0)
            }
        }

        impl Into<TemplatedFileSlice> for PySqlFluffTemplatedFileSlice {
            fn into(self) -> TemplatedFileSlice {
                self.0 .0
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
                    source_idx.unwrap_or_else(|| raw.len()),
                    block_idx,
                    tag,
                ))))
            }
        }

        impl Into<PyRawFileSlice> for PySqlFluffRawFileSlice {
            fn into(self) -> PyRawFileSlice {
                PyRawFileSlice(self.0 .0)
            }
        }

        impl Into<RawFileSlice> for PySqlFluffRawFileSlice {
            fn into(self) -> RawFileSlice {
                self.0 .0
            }
        }
    }
}
