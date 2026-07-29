//! Small shared converters for building PyO3 containers from Rust collections.
//!
//! Centralised here so the string-list and escape-pair conversions used across
//! `sqlfluffrs_python::token` and the `sqlfluffrs_parser` PyO3 bindings stay in
//! sync instead of being copy-pasted at each call site.

use pyo3::prelude::*;
use pyo3::types::{PyList, PyTuple};

/// Build a `PyList` of Python strings from a slice of owned `String`s.
pub fn pylist_of_strs<'py>(py: Python<'py>, items: &[String]) -> PyResult<Bound<'py, PyList>> {
    PyList::new(py, items.iter().map(String::as_str))
}

/// Build a `PyTuple` of Python strings from a slice of owned `String`s.
pub fn pytuple_of_strs<'py>(py: Python<'py>, items: &[String]) -> PyResult<Bound<'py, PyTuple>> {
    PyTuple::new(py, items.iter().map(String::as_str))
}

/// Build a `PyList` of `(str, str)` tuples from a slice of string pairs.
pub fn pylist_of_str_pairs<'py>(
    py: Python<'py>,
    pairs: &[(String, String)],
) -> PyResult<Bound<'py, PyList>> {
    PyList::new(
        py,
        pairs
            .iter()
            .map(|(a, b)| PyTuple::new(py, [a.as_str(), b.as_str()]))
            .collect::<PyResult<Vec<_>>>()?,
    )
}
