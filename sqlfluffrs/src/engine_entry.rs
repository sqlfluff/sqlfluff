//! Python-callable engine entrypoints — Rust drives the per-file orchestration
//! (discover → render → lex → parse) for the `parse` and `render` CLI commands,
//! calling back into the Python templaters over the GIL.
//!
//! Gated behind the `python` feature (registered in [`crate::python`]). The
//! discovery + lex + parse leaf ops come from the pyo3-free `sqlfluffrs_engine`;
//! the render step reverse-dispatches to the Python templater exactly as
//! `Linter.render_string` does. Config is read from the *already-resolved*
//! Python `FluffConfig` passed in — single source of truth, no native
//! re-resolution. Results are returned as records + pass-through Python objects
//! so the existing `commands.py` output/exit-code code stays byte-identical.

use std::collections::BTreeMap;
use std::sync::Arc;

use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};

use sqlfluffrs_engine::pipeline::ParseLimits;
use sqlfluffrs_engine::{discovery, pipeline};
use sqlfluffrs_parser::PyNode;
use sqlfluffrs_python::templater::templatefile::PySqlFluffTemplatedFile;
use sqlfluffrs_types::TemplatedFile;

/// Read a `core.<key>` config value that may be a comma-separated string or a
/// sequence, as a `Vec<String>`.
fn read_str_list(config: &Bound<'_, PyAny>, key: &str) -> Vec<String> {
    let Ok(v) = config.call_method1("get", (key,)) else {
        return Vec::new();
    };
    if v.is_none() {
        return Vec::new();
    }
    if let Ok(list) = v.extract::<Vec<String>>() {
        return list;
    }
    if let Ok(s) = v.extract::<String>() {
        return s
            .split(',')
            .map(|x| x.trim().to_string())
            .filter(|x| !x.is_empty())
            .collect();
    }
    Vec::new()
}

/// `child.get(val, section=..)`, returned as an owned `String` when scalar.
fn get_str<'py>(config: &Bound<'py, PyAny>, val: &str, section: Option<&str>) -> Option<String> {
    let kwargs = PyDict::new(config.py());
    if let Some(sec) = section {
        kwargs.set_item("section", sec).ok()?;
    }
    let v = config.call_method("get", (val,), Some(&kwargs)).ok()?;
    if v.is_none() {
        return None;
    }
    v.extract::<String>().ok()
}

/// Whether template blocks emit indent metas (default true), mirroring the
/// `[sqlfluff:indentation] template_blocks_indent` flag.
fn template_blocks_indent(config: &Bound<'_, PyAny>) -> bool {
    indent_config(config)
        .get("template_blocks_indent")
        .copied()
        .unwrap_or(true)
}

/// The boolean entries of the `[sqlfluff:indentation]` section, for the parser's
/// `indent_config` (mirrors `ResolvedConfig::indentation_bools`).
fn indent_config(config: &Bound<'_, PyAny>) -> BTreeMap<String, bool> {
    let mut out = BTreeMap::new();
    let Ok(section) = config.call_method1("get_section", ("indentation",)) else {
        return out;
    };
    let Ok(dict) = section.cast::<PyDict>() else {
        return out;
    };
    for (k, v) in dict.iter() {
        if let (Ok(key), Ok(b)) = (k.extract::<String>(), v.extract::<bool>()) {
            out.insert(key, b);
        }
    }
    out
}

/// Read the parser resource limits from `core.*`, mirroring what `RustParser`
/// threads in (falling back to the `default_config.cfg` values).
fn parse_limits(config: &Bound<'_, PyAny>) -> ParseLimits {
    let d = ParseLimits::default();
    let get = |key: &str, dflt: usize| -> usize {
        config
            .call_method1("get", (key,))
            .ok()
            .and_then(|v| v.extract::<usize>().ok())
            .unwrap_or(dflt)
    };
    ParseLimits {
        max_parser_iterations: get("rust_parser_max_iterations", d.max_parser_iterations),
        parser_warn_threshold: get("rust_parser_warn_threshold", d.parser_warn_threshold),
        max_parse_depth: get("max_parse_depth", d.max_parse_depth),
        max_parse_nodes: get("max_parse_nodes", d.max_parse_nodes),
    }
}

/// The per-file config: `make_child_from_path` for a real file (re-resolves
/// per-directory config, matching `load_raw_file_and_config`), or the passed
/// root config for stdin. Then apply inline `-- sqlfluff:` directives.
fn child_config<'py>(
    config: &Bound<'py, PyAny>,
    fname: &str,
    is_stdin: bool,
    raw: &str,
) -> PyResult<Bound<'py, PyAny>> {
    let child = if is_stdin {
        config.clone()
    } else {
        let kwargs = PyDict::new(config.py());
        kwargs.set_item("require_dialect", false)?;
        config.call_method("make_child_from_path", (fname,), Some(&kwargs))?
    };
    child.call_method1("process_raw_file_for_config", (raw, fname))?;
    Ok(child)
}

/// Reverse-dispatch templating to the Python templater, exactly as
/// `Linter.render_string`. Returns the (unchanged) Python `TemplatedFile`
/// variant objects and the templater-violation objects.
fn render_via_python<'py>(
    py: Python<'py>,
    child: &Bound<'py, PyAny>,
    raw: &str,
    fname: &str,
    formatter: Option<&Bound<'py, PyAny>>,
) -> PyResult<(Vec<Bound<'py, PyAny>>, Bound<'py, PyList>)> {
    let templater = child.call_method0("get_templater")?;
    let kwargs = PyDict::new(py);
    kwargs.set_item("in_str", raw)?;
    kwargs.set_item("fname", fname)?;
    kwargs.set_item("config", child)?;
    kwargs.set_item("formatter", formatter.map(|f| f.clone()))?;

    let violations = PyList::empty(py);
    let mut variants = Vec::new();

    // Iterate templater variants. A raised `SQLTemplaterError` is a fatal
    // templating error captured as a violation (mirrors `Linter.render_string`);
    // any other exception propagates.
    let result = (|| -> PyResult<()> {
        let iter = templater.call_method("process_with_variants", (), Some(&kwargs))?;
        for item in iter.try_iter()? {
            let tup = item?;
            let tf_obj = tup.get_item(0)?;
            let errs_obj = tup.get_item(1)?;
            if !tf_obj.is_none() {
                variants.push(tf_obj);
            }
            if !errs_obj.is_none() {
                for e in errs_obj.try_iter()? {
                    violations.append(e?)?;
                }
            }
        }
        Ok(())
    })();
    if let Err(err) = result {
        let errors_mod = py.import("sqlfluff.core.errors")?;
        let templater_err_cls = errors_mod.getattr("SQLTemplaterError")?;
        let value = err.value(py).clone().into_any();
        if value.is_instance(&templater_err_cls)? {
            violations.append(value)?;
        } else {
            return Err(err);
        }
    }
    Ok((variants, violations))
}

/// Build the `segments` record from a templated variant by lexing + parsing it
/// natively and calling `PyNode::as_record` (the parity-verified path Python's
/// `parse` uses). Returns the record object (or `None`) plus lex-error strings.
fn parse_variant_to_record<'py>(
    py: Python<'py>,
    child: &Bound<'py, PyAny>,
    tf_obj: &Bound<'py, PyAny>,
    code_only: bool,
    include_meta: bool,
) -> PyResult<(Option<Py<PyAny>>, Vec<String>, Vec<String>)> {
    let pf: PySqlFluffTemplatedFile = tf_obj.extract()?;
    let templated: Arc<TemplatedFile> = pf.into();

    // Raise the same `SQLFluffUserError` Python does when no dialect is set
    // (the CLI's PathAndUserErrorHandler turns this into a clean "User Error").
    child.call_method0("verify_dialect_specified")?;
    let dialect = pipeline::resolve_dialect_by_name(get_str(child, "dialect", None).as_deref())
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))?;

    let tbi = template_blocks_indent(child);
    let indent = indent_config(child);
    let limits = parse_limits(child);

    // Pure-Rust lex+parse. `catch_unwind` guards the parser's hard iteration-limit
    // `panic!` so a pathological/huge file degrades to null segments (like the
    // Python path) instead of crashing the interpreter. Recoverable parse errors
    // (depth/node limits, unmatched input) come back as `Err` and are handled the
    // same way. No Python objects are touched inside the closure.
    let parsed = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
        let (tokens, lex_errors) = pipeline::lex_variant(&templated, dialect, tbi);
        let node = pipeline::parse_tokens(&tokens, dialect, indent, limits);
        (lex_errors, node)
    }));

    match parsed {
        Ok((lex_errors, Ok(node))) => {
            // `show_raw=true` matches the CLI `parse` record shape (leaves scalar).
            let pynode = Py::new(py, PyNode::from(node))?;
            let record = pynode.call_method1(py, "as_record", (code_only, true, include_meta))?;
            Ok((Some(record), lex_errors, Vec::new()))
        }
        Ok((lex_errors, Err(e))) => Ok((None, lex_errors, vec![e.to_string()])),
        Err(_) => Ok((
            None,
            Vec::new(),
            vec!["parser exceeded its resource limits (iteration/depth/node)".to_string()],
        )),
    }
}

/// Rust-driven discover→render→lex→parse for `sqlfluff parse` (non-human output).
///
/// Returns one dict per discovered file (in discovery order):
/// `{fname, segments, templater_violations, lex_errors, parse_errors}`.
#[pyfunction]
#[pyo3(signature = (paths, config, formatter=None, *, stdin_content=None,
        stdin_filename=None, code_only=false, include_meta=false,
        parse_statistics=false))]
#[allow(clippy::too_many_arguments)]
pub fn engine_parse_paths<'py>(
    py: Python<'py>,
    paths: Vec<String>,
    config: Bound<'py, PyAny>,
    formatter: Option<Bound<'py, PyAny>>,
    stdin_content: Option<String>,
    stdin_filename: Option<String>,
    code_only: bool,
    include_meta: bool,
    parse_statistics: bool,
) -> PyResult<Vec<Py<PyDict>>> {
    let _ = parse_statistics; // reserved (timing/stats not surfaced yet)
    let is_stdin = paths.iter().any(|p| p == "-");

    // (fname, raw) work-list — Rust drives discovery / file reading.
    let mut files: Vec<(String, String)> = Vec::new();
    if is_stdin {
        files.push((
            stdin_filename.unwrap_or_else(|| "stdin".to_string()),
            stdin_content.unwrap_or_default(),
        ));
    } else {
        let exts: Vec<String> = read_str_list(&config, "sql_file_exts")
            .iter()
            .map(|e| e.to_ascii_lowercase())
            .collect();
        let exts = if exts.is_empty() {
            vec![".sql".to_string()]
        } else {
            exts
        };
        let ignore_paths = read_str_list(&config, "ignore_paths");
        let cwd = std::env::current_dir()
            .map_err(|e| pyo3::exceptions::PyOSError::new_err(e.to_string()))?;
        let discovered = discovery::discover_files(&paths, &exts, &ignore_paths, &cwd)
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))?;
        for path in discovered {
            let raw = std::fs::read_to_string(&path)
                .map_err(|e| pyo3::exceptions::PyOSError::new_err(e.to_string()))?;
            files.push((path.to_string_lossy().to_string(), raw));
        }
    }

    let formatter_ref = formatter.as_ref();
    let mut out = Vec::with_capacity(files.len());
    for (fname, raw) in files {
        let child = child_config(&config, &fname, is_stdin, &raw)?;
        let (variants, templater_violations) =
            render_via_python(py, &child, &raw, &fname, formatter_ref)?;

        let dict = PyDict::new(py);
        dict.set_item("fname", &fname)?;
        dict.set_item("templater_violations", &templater_violations)?;

        if let Some(root) = variants.first() {
            let (record, lex_errors, parse_errors) =
                parse_variant_to_record(py, &child, root, code_only, include_meta)?;
            dict.set_item("segments", record)?;
            dict.set_item("lex_errors", lex_errors)?;
            dict.set_item("parse_errors", parse_errors)?;
        } else {
            dict.set_item("segments", py.None())?;
            dict.set_item("lex_errors", Vec::<String>::new())?;
            dict.set_item("parse_errors", Vec::<String>::new())?;
        }
        out.push(dict.unbind());
    }
    Ok(out)
}

/// Rust-driven render for `sqlfluff render` (single file or stdin). Returns
/// `{templated_variants, templater_violations}` — the templated variants are the
/// unchanged Python `TemplatedFile` objects, so the existing print path applies.
#[pyfunction]
#[pyo3(signature = (raw_sql, fname, config, formatter=None))]
pub fn engine_render_string<'py>(
    py: Python<'py>,
    raw_sql: String,
    fname: String,
    config: Bound<'py, PyAny>,
    formatter: Option<Bound<'py, PyAny>>,
) -> PyResult<Bound<'py, PyDict>> {
    // `render` resolves per-file config Python-side and passes it in already; we
    // apply inline directives here to match `process_raw_file_for_config`.
    config.call_method1("process_raw_file_for_config", (&raw_sql, &fname))?;
    // `render_string` requires a dialect (raises SQLFluffUserError otherwise).
    config.call_method0("verify_dialect_specified")?;
    let (variants, violations) =
        render_via_python(py, &config, &raw_sql, &fname, formatter.as_ref())?;

    let variant_list = PyList::empty(py);
    for v in variants {
        variant_list.append(v)?;
    }
    let dict = PyDict::new(py);
    dict.set_item("templated_variants", variant_list)?;
    dict.set_item("templater_violations", violations)?;
    Ok(dict)
}
