pub mod config;
pub mod dialect;
pub mod lexer;
pub mod marker;
pub mod matcher;
pub mod slice;
pub mod templater;
pub mod token;
// include!(concat!(env!("OUT_DIR"), "/dialect_matcher.rs"));

use dialect::matcher::*;
#[cfg(feature = "python")]
use lexer::python::{PyLexer, PySQLLexError};
#[cfg(feature = "python")]
use marker::python::PyPositionMarker;
#[cfg(feature = "python")]
use pyo3::prelude::*;
#[cfg(feature = "python")]
use templater::{
    fileslice::python::{PyRawFileSlice, PyTemplatedFileSlice},
    templatefile::python::PyTemplatedFile,
};
#[cfg(feature = "python")]
use token::python::PyToken;

#[cfg(feature = "python")]
/// A Python module implemented in Rust.
#[pymodule(name = "rsqlfluff")]
fn rsqlfluff(m: &Bound<'_, PyModule>) -> PyResult<()> {
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
