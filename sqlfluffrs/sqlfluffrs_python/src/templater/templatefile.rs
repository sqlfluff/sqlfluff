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

/// Cache of Python→Rust `TemplatedFile` conversions, keyed by the SOURCE
/// PYTHON OBJECT's address. It exists for two reasons: repeated extraction of
/// the same `TemplatedFile` (every position marker crossing the FFI boundary
/// carries one) would otherwise re-convert the full slice vectors each time,
/// and markers combined in Rust compare their `Arc<TemplatedFile>`s by
/// POINTER first (see `sqlfluffrs_types/src/marker.rs`), so one Python object
/// must normalize to one `Arc`.
///
/// Keying by content (`fname:source:templated`) is UNSOUND — two
/// TemplatedFiles can share all three strings with different SLICINGS (e.g.
/// jinja vs raw templater over the same rendered text), and the second would
/// silently reuse the first's slices. Object identity cannot collide. Each
/// entry holds the `weakref.ref` whose callback evicts the entry when the
/// source object is garbage collected (the ref must be kept alive for the
/// callback to fire) — so the cache is bounded by LIVE TemplatedFiles and a
/// recycled object address can never hit a stale entry.
type TemplatedFileCacheEntry = (Arc<TemplatedFile>, Py<PyAny>);
type TemplatedFileCache = Lazy<Mutex<HashMap<usize, TemplatedFileCacheEntry>>>;

static PY_TEMPLATED_FILE_CACHE: TemplatedFileCache = Lazy::new(|| Mutex::new(HashMap::new()));

/// Weakref callback target: drop one conversion-cache entry. Bound to its key
/// with `functools.partial`; the weakref machinery passes the (dead) ref as a
/// positional arg.
#[pyfunction]
#[pyo3(name = "_evict_templated_file_cache_entry")]
#[pyo3(signature = (key, _r=None))]
pub fn evict_templated_file_cache_entry(key: usize, _r: Option<Py<PyAny>>) {
    PY_TEMPLATED_FILE_CACHE.lock().unwrap().remove(&key);
}

/// The live entry count of the conversion cache (test introspection).
#[pyfunction]
#[pyo3(name = "_templated_file_cache_len")]
pub fn templated_file_cache_len() -> usize {
    PY_TEMPLATED_FILE_CACHE.lock().unwrap().len()
}

#[pyclass(
    name = "RsTemplatedFile",
    frozen,
    module = "sqlfluffrs",
    from_py_object
)]
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

impl<'a, 'py> FromPyObject<'a, 'py> for PySqlFluffTemplatedFile {
    type Error = PyErr;

    fn extract(obj: pyo3::Borrowed<'a, 'py, pyo3::PyAny>) -> Result<Self, Self::Error> {
        // Fast path: an actual RsTemplatedFile — share its Arc directly.
        if let Ok(native) = obj.cast::<PyTemplatedFile>() {
            return Ok(Self(native.get().clone()));
        }

        let key = obj.as_ptr() as usize;
        if let Some((cached, _)) = PY_TEMPLATED_FILE_CACHE.lock().unwrap().get(&key) {
            return Ok(Self(PyTemplatedFile(cached.clone())));
        }

        // NOTE: the lock is NOT held during extraction — the `getattr` calls
        // run arbitrary Python which can trigger GC, whose eviction callbacks
        // take the same (non-reentrant) lock.
        let source_str = obj.getattr("source_str")?.extract::<String>()?;
        let fname = obj.getattr("fname")?.extract::<String>()?;
        let templated_str = obj.getattr("templated_str")?.extract::<String>()?;

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

        // Cache only when eviction-on-GC can be arranged; an object that
        // doesn't support weakrefs stays uncached (correct, just slower).
        let py = obj.py();
        let weakref = (|| -> PyResult<Py<PyAny>> {
            let evict = pyo3::wrap_pyfunction!(evict_templated_file_cache_entry, py)?;
            let callback = py
                .import("functools")?
                .getattr("partial")?
                .call1((evict, key))?;
            Ok(py
                .import("weakref")?
                .getattr("ref")?
                .call1((obj.to_owned(), callback))?
                .unbind())
        })();
        let mut cache = PY_TEMPLATED_FILE_CACHE.lock().unwrap();
        // Re-check under the lock: the extraction above runs arbitrary Python,
        // so a nested/concurrent conversion of the same object may have cached
        // an entry already. Return that Arc rather than overwriting it, so
        // every conversion of one Python object yields the same allocation
        // (markers pointer-compare templated files on the fast path).
        if let Some((cached, _)) = cache.get(&key) {
            return Ok(Self(PyTemplatedFile(cached.clone())));
        }
        if let Ok(weakref) = weakref {
            cache.insert(key, (tf.0 .0.clone(), weakref));
        }
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
