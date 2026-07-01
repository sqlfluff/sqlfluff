use pyo3::prelude::*;
use sqlfluffrs_lexer::{PyLexer, PySQLLexError};
use sqlfluffrs_parser::{PyHandle, PyMatchResult, PyNode, PyParser, PyTree, RsParseError};
use sqlfluffrs_python::marker::PyPositionMarker;
use sqlfluffrs_python::templater::{
    fileslice::{PyRawFileSlice, PyTemplatedFileSlice},
    templatefile::PyTemplatedFile,
};
use sqlfluffrs_python::token::{PyCaseFold, PyToken};

/// A Python module implemented in Rust.
#[pymodule(name = "sqlfluffrs", module = "sqlfluffrs")]
fn sqlfluffrs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    let env = env_logger::Env::default().filter_or("RUST_LOG", "warn");
    env_logger::Builder::from_env(env)
        .try_init()
        .unwrap_or_else(|_| log::warn!("env_logger already initialized!"));
    m.add_class::<PyCaseFold>()?;
    m.add_class::<PyToken>()?;
    m.add_class::<PyTemplatedFile>()?;
    m.add_class::<PyTemplatedFileSlice>()?;
    m.add_class::<PyRawFileSlice>()?;
    m.add_class::<PySQLLexError>()?;
    m.add_class::<PyLexer>()?;
    m.add_class::<PyPositionMarker>()?;
    // Parser classes
    m.add_class::<PyNode>()?;
    m.add_class::<PyMatchResult>()?;
    m.add_class::<PyParser>()?;
    // Arena tree (Rust-backed segment façade)
    m.add_class::<PyTree>()?;
    m.add_class::<PyHandle>()?;
    // Add custom exception
    m.add("RsParseError", m.py().get_type::<RsParseError>())?;
    // Rust-driven orchestration entrypoints (discover → render → lex → parse).
    m.add_function(wrap_pyfunction!(
        crate::engine_entry::engine_parse_paths,
        m
    )?)?;
    m.add_function(wrap_pyfunction!(
        crate::engine_entry::engine_render_string,
        m
    )?)?;
    Ok(())
}
