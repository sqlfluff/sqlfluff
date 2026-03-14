use std::hash::{DefaultHasher, Hash, Hasher};
use std::sync::{Arc, Mutex};

use hashbrown::HashMap;
use pyo3::IntoPyObject;
use pyo3::{prelude::*, types::PyType};

use crate::slice::PySlice;
use crate::templater::fileslice::sqlfluff::{PySqlFluffRawFileSlice, PySqlFluffTemplatedFileSlice};
use crate::templater::fileslice::{PyRawFileSlice, PyTemplatedFileSlice};
use sqlfluffrs_types::templater::fileslice::{RawFileSlice, TemplatedFileSlice};

use once_cell::sync::Lazy;
use sqlfluffrs_types::templater::templatefile::TemplatedFile;

static PY_TEMPLATED_FILE_CACHE: Lazy<Mutex<HashMap<String, Arc<TemplatedFile>>>> =
    Lazy::new(|| Mutex::new(HashMap::new()));

#[pyclass(name = "RsTemplatedFile", frozen, module = "sqlfluffrs")]
#[repr(transparent)]
#[derive(Clone, PartialEq, Hash)]
pub struct PyTemplatedFile(pub Arc<TemplatedFile>);

#[pymethods]
impl PyTemplatedFile {
    #[new]
    #[pyo3(signature = (source_str, fname, templated_str=None, sliced_file=None, raw_sliced=None))]
    pub fn new(
        source_str: String,
        fname: String,
        templated_str: Option<String>,
        sliced_file: Option<Vec<PyTemplatedFileSlice>>,
        raw_sliced: Option<Vec<PyRawFileSlice>>,
    ) -> Self {
        log::debug!("PyTemplatedFile::new");
        let tf = Arc::new(TemplatedFile::new(
            source_str,
            fname,
            templated_str,
            sliced_file.map(|x| x.into_iter().map(Into::into).collect()),
            raw_sliced.map(|x| x.into_iter().map(Into::into).collect()),
        ));
        Self(tf)
    }

    #[classmethod]
    pub fn from_string(_cls: &Bound<'_, PyType>, raw: String) -> Self {
        log::debug!("PyTemplatedFile::from_string");
        let tf = Arc::new(TemplatedFile::from(raw));
        Self(tf)
    }

    #[getter]
    fn source_str(&self) -> PyResult<String> {
        Ok(self.0.source_str.clone())
    }

    #[getter]
    fn fname(&self) -> PyResult<String> {
        Ok(self.0.fname.clone())
    }

    #[getter]
    fn templated_str(&self) -> PyResult<String> {
        Ok(self.0.templated_str.clone())
    }

    #[getter]
    fn sliced_file(&self) -> Vec<PyTemplatedFileSlice> {
        self.0
            .sliced_file
            .clone()
            .into_iter()
            .map(Into::into)
            .collect()
    }

    #[getter]
    fn raw_sliced(&self) -> Vec<PyRawFileSlice> {
        self.0
            .raw_sliced
            .clone()
            .into_iter()
            .map(Into::into)
            .collect()
    }

    #[getter("_source_newlines")]
    fn source_newlines(&self) -> PyResult<Vec<usize>> {
        Ok(self
            .0
            .source_str
            .char_indices()
            .filter(|(_i, c)| *c == '\n')
            .map(|(i, _)| i)
            .collect())
    }

    #[getter("_templated_newlines")]
    fn templated_newlines(&self) -> PyResult<Vec<usize>> {
        Ok(self
            .0
            .templated_str
            .char_indices()
            .filter(|(_i, c)| *c == '\n')
            .map(|(i, _)| i)
            .collect())
    }

    fn __str__(&self) -> PyResult<String> {
        Ok(self.0.templated_str.clone())
    }

    fn __repr__(&self) -> PyResult<String> {
        Ok(String::from("<TemplatedFile>"))
    }

    fn __eq__(&self, other: &Self) -> bool {
        self.0 == other.0
    }

    fn __hash__(&self) -> u64 {
        let mut hasher = DefaultHasher::new();
        self.0.hash(&mut hasher);
        hasher.finish()
    }

    fn get_line_pos_of_char_pos(&self, char_pos: usize, source: bool) -> PyResult<(usize, usize)> {
        Ok(self.0.get_line_pos_of_char_pos(char_pos, source))
    }

    pub fn is_source_slice_literal(&self, source_slice: PySlice) -> bool {
        self.0.is_source_slice_literal(&source_slice.0)
    }

    pub fn source_position_dict_from_slice(&self, source_slice: PySlice) -> HashMap<String, usize> {
        self.0.source_position_dict_from_slice(&source_slice.0)
    }
}

impl PyTemplatedFile {
    fn from_python(
        source_str: String,
        fname: String,
        templated_str: String,
        sliced_file: Vec<TemplatedFileSlice>,
        raw_sliced: Vec<RawFileSlice>,
        source_newlines: Vec<usize>,
        templated_newlines: Vec<usize>,
    ) -> Self {
        log::debug!("PyTemplatedFile::from_python: {}", fname);
        let tf = Arc::new(TemplatedFile::copy(
            source_str,
            fname,
            templated_str,
            sliced_file,
            raw_sliced,
            source_newlines,
            templated_newlines,
        ));
        Self(tf)
    }

    fn py_raw_slices(raw_sliced: &[PyRawFileSlice]) -> Vec<RawFileSlice> {
        if raw_sliced.len() == 1 {
            return raw_sliced.iter().map(|s| s.0.clone()).collect::<Vec<_>>();
        }
        let mut idx = 0;
        raw_sliced
            .iter()
            .map(|rs| {
                let mut slice = rs.0.clone();
                slice.source_idx = idx;
                idx += slice.raw.chars().count();
                slice
            })
            .collect()
    }

    fn unicode_to_utf8_slices(
        source_str: &str,
        templated_str: &str,
        sliced_file: &[PyTemplatedFileSlice],
    ) -> Vec<TemplatedFileSlice> {
        if source_str.len()
            == sliced_file
                .last()
                .map_or(0, |s| s.0.source_codepoint_slice.stop)
            && source_str.len()
                == sliced_file
                    .last()
                    .map_or(0, |s| s.0.templated_codepoint_slice.stop)
        {
            return sliced_file.iter().map(|ts| ts.0.clone()).collect();
        }
        let char_source_vec = source_str.char_indices().enumerate().collect::<Vec<_>>();
        let char_templated_vec = templated_str.char_indices().enumerate().collect::<Vec<_>>();

        sliced_file
            .iter()
            .map(|py_slice| {
                let mut new_slice = py_slice.0.clone(); // Extract TemplatedFileSlice and clone it

                new_slice.source_codepoint_slice.start = char_source_vec
                    .get(new_slice.source_codepoint_slice.start)
                    .map_or_else(|| char_source_vec.len(), |c| c.0);
                new_slice.source_codepoint_slice.stop = char_source_vec
                    .get(new_slice.source_codepoint_slice.stop)
                    .map_or_else(|| char_source_vec.len(), |c| c.0);
                new_slice.templated_codepoint_slice.start = char_templated_vec
                    .get(new_slice.templated_codepoint_slice.start)
                    .map_or_else(|| char_templated_vec.len(), |c| c.0);
                new_slice.templated_codepoint_slice.stop = char_templated_vec
                    .get(new_slice.templated_codepoint_slice.stop)
                    .map_or_else(|| char_templated_vec.len(), |c| c.0);

                new_slice
            })
            .collect()
    }
}

impl From<Arc<TemplatedFile>> for PyTemplatedFile {
    fn from(value: Arc<TemplatedFile>) -> Self {
        log::debug!("PyTemplatedFile::from<ArcTemplated> {}", value.fname);
        Self(value)
    }
}

impl From<PyTemplatedFile> for Arc<TemplatedFile> {
    fn from(value: PyTemplatedFile) -> Self {
        log::debug!("PyTemplatedFile::from<ArcTemplated> {}", value.0.fname);
        value.0
    }
}

#[derive(Clone, IntoPyObject)]
pub struct PySqlFluffTemplatedFile(pub PyTemplatedFile);

impl<'py> FromPyObject<'py> for PySqlFluffTemplatedFile {
    fn extract_bound(obj: &pyo3::Bound<'py, pyo3::PyAny>) -> PyResult<Self> {
        let source_str = obj.getattr("source_str")?.extract::<String>()?;
        let fname = obj.getattr("fname")?.extract::<String>()?;
        let templated_str = obj.getattr("templated_str")?.extract::<String>()?;

        let key = format!("{}:{}:{}", fname, &source_str, &templated_str);
        let mut cache = PY_TEMPLATED_FILE_CACHE.lock().unwrap();

        if let Some(cached) = cache.get(&key) {
            return Ok(Self(PyTemplatedFile(cached.clone())));
        }

        let py_sliced_file = obj
            .getattr("sliced_file")?
            .extract::<Vec<PySqlFluffTemplatedFileSlice>>()?
            .into_iter()
            .map(Into::into)
            .collect::<Vec<_>>();
        let sliced_file =
            PyTemplatedFile::unicode_to_utf8_slices(&source_str, &templated_str, &py_sliced_file);

        let py_raw_sliced = obj
            .getattr("raw_sliced")?
            .extract::<Vec<PySqlFluffRawFileSlice>>()?
            .into_iter()
            .map(Into::into)
            .collect::<Vec<_>>();
        let raw_sliced = PyTemplatedFile::py_raw_slices(&py_raw_sliced);

        let py_source_newlines = obj.getattr("_source_newlines")?.extract::<Vec<usize>>()?;
        let py_templated_newlines = obj
            .getattr("_templated_newlines")?
            .extract::<Vec<usize>>()?;

        let tf = Self(PyTemplatedFile::from_python(
            source_str,
            fname,
            templated_str,
            sliced_file,
            raw_sliced,
            py_source_newlines,
            py_templated_newlines,
        ));

        cache.insert(key, tf.0 .0.clone());
        Ok(tf)
    }
}

impl From<PySqlFluffTemplatedFile> for PyTemplatedFile {
    fn from(value: PySqlFluffTemplatedFile) -> Self {
        value.0
    }
}

impl From<PySqlFluffTemplatedFile> for Arc<TemplatedFile> {
    fn from(value: PySqlFluffTemplatedFile) -> Self {
        value.0 .0
    }
}
