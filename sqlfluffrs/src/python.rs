use std::collections::HashSet;

use pyo3::prelude::*;
use sqlfluffrs_lexer::{PyLexer, PySQLLexError};
use sqlfluffrs_parser::{PyHandle, PyMatchResult, PyNode, PyParser, PyTree, RsParseError};
use sqlfluffrs_python::marker::PyPositionMarker;
use sqlfluffrs_python::templater::{
    fileslice::{PyRawFileSlice, PyTemplatedFileSlice},
    templatefile::PyTemplatedFile,
};
use sqlfluffrs_python::token::{PyCaseFold, PyToken};

/// Experimental: detect CP01 (keyword capitalisation) violations natively.
///
/// Runs CP01's detection loop entirely in Rust over the arena read API and
/// returns `(leaf_index, fixed_raw)` for each keyword/operator node needing a
/// fix — `leaf_index` is the position in the depth-first leaf order, 1:1 with
/// Python's `raw_segments`. One FFI crossing for the whole result; the caller
/// anchors via `raw_segments[leaf_index]`. Read-only (no arena mutation).
///
/// Lives here, not on `RsTree`, because the rule logic is in `sqlfluffrs_rules`,
/// which depends on `sqlfluffrs_parser` — so the binding belongs in the root
/// crate that depends on both.
#[pyfunction]
#[pyo3(signature = (tree, policy, ignore_words=vec![], ignore_templated=false))]
fn cp01_violations(
    tree: &PyTree,
    policy: &str,
    ignore_words: Vec<String>,
    ignore_templated: bool,
) -> Vec<(usize, String)> {
    let ignore: HashSet<String> = ignore_words.into_iter().collect();
    tree.with_arena(|arena| {
        sqlfluffrs_rules::cp01::cp01_violations(arena, policy, &ignore, ignore_templated)
    })
}

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
    // Experimental Rust-native lint rule detection
    m.add_function(wrap_pyfunction!(cp01_violations, m)?)?;
    // Add custom exception
    m.add("RsParseError", m.py().get_type::<RsParseError>())?;
    Ok(())
}
