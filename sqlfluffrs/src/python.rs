use pyo3::prelude::*;
use sqlfluffrs_lexer::{PyLexer, PySQLLexError};
use sqlfluffrs_types::templater::{
    fileslice::python::{PyRawFileSlice, PyTemplatedFileSlice},
    templatefile::python::PyTemplatedFile,
};
use sqlfluffrs_types::PyPositionMarker;
use sqlfluffrs_types::PyToken;

/// A Python module implemented in Rust.
#[pymodule(name = "sqlfluffrs", module = "sqlfluffrs")]
fn sqlfluffrs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    let env = env_logger::Env::default().filter_or("RUST_LOG", "warn");
    env_logger::Builder::from_env(env)
        .try_init()
        .unwrap_or_else(|_| log::warn!("env_logger already initialized!"));
    m.add_class::<PyToken>()?;
    m.add_class::<PyTemplatedFile>()?;
    m.add_class::<PyTemplatedFileSlice>()?;
    m.add_class::<PyRawFileSlice>()?;
    m.add_class::<PySQLLexError>()?;
    m.add_class::<PyLexer>()?;
    m.add_class::<PyPositionMarker>()?;
    Ok(())
}
