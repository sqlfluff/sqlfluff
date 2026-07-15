//! PyO3 bindings for the Rust-native rules.
//!
//! Each rule's binding sits next to its detection logic; the root crate just
//! calls [`register`]. Bindings are read-only over the arena and return compact
//! results the Python side anchors fixes from.

use std::collections::HashSet;

use pyo3::prelude::*;
use sqlfluffrs_parser::PyTree;

/// Experimental: detect CP01 (keyword capitalisation) violations natively.
///
/// Runs CP01's detection loop entirely in Rust over the arena read API and
/// returns `(leaf_index, fixed_raw)` for each keyword/operator node needing a
/// fix — `leaf_index` is the position in the depth-first leaf order, 1:1 with
/// Python's `raw_segments`. One FFI crossing for the whole result; the caller
/// anchors via `raw_segments[leaf_index]`. Read-only (no arena mutation).
#[pyfunction]
#[pyo3(signature = (tree, policy, ignore_words=vec![], ignore_templated=false))]
fn cp01_violations(
    tree: &PyTree,
    policy: &str,
    ignore_words: Vec<String>,
    ignore_templated: bool,
) -> Vec<(usize, String)> {
    let ignore: HashSet<String> = ignore_words.into_iter().collect();
    tree.with_arena(|arena| crate::cp01::cp01_violations(arena, policy, &ignore, ignore_templated))
}

/// Experimental: detect CP03 (function-name capitalisation) violations
/// natively. Same contract as [`cp01_violations`]; `policy` additionally
/// accepts `pascal`/`camel`/`snake` (CP03 reads `extended_capitalisation_policy`).
#[pyfunction]
#[pyo3(signature = (tree, policy, ignore_words=vec![], ignore_templated=false))]
fn cp03_violations(
    tree: &PyTree,
    policy: &str,
    ignore_words: Vec<String>,
    ignore_templated: bool,
) -> Vec<(usize, String)> {
    let ignore: HashSet<String> = ignore_words.into_iter().collect();
    tree.with_arena(|arena| crate::cp03::cp03_violations(arena, policy, &ignore, ignore_templated))
}

/// Experimental: detect CP04 (boolean/null literal capitalisation) violations
/// natively. Same contract as [`cp01_violations`].
#[pyfunction]
#[pyo3(signature = (tree, policy, ignore_words=vec![], ignore_templated=false))]
fn cp04_violations(
    tree: &PyTree,
    policy: &str,
    ignore_words: Vec<String>,
    ignore_templated: bool,
) -> Vec<(usize, String)> {
    let ignore: HashSet<String> = ignore_words.into_iter().collect();
    tree.with_arena(|arena| crate::cp04::cp04_violations(arena, policy, &ignore, ignore_templated))
}

/// Register this crate's rule bindings on the extension module.
pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(cp01_violations, m)?)?;
    m.add_function(wrap_pyfunction!(cp03_violations, m)?)?;
    m.add_function(wrap_pyfunction!(cp04_violations, m)?)?;
    Ok(())
}
