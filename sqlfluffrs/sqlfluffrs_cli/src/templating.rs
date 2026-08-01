//! Templating. The `raw` templater is handled natively in Rust; every other
//! templater (`jinja`, `python`, `placeholder`, `dbt`, ...) is reverse-dispatched
//! to the existing Python implementation through an embedded interpreter (the
//! `embed-python` feature). This reuses Python's battle-tested Jinja tracer and
//! the dbt plugin without re-deriving source-mapping logic in Rust.

use std::sync::Arc;

use anyhow::Result;
use sqlfluffrs_types::templater::templatefile::TemplatedFile;

use sqlfluffrs_engine::config::ResolvedConfig;

/// The result of templating a single file: one or more templated variants plus
/// any templater error messages.
pub struct TemplateOutcome {
    pub variants: Vec<Arc<TemplatedFile>>,
    pub errors: Vec<String>,
}

/// Template `raw_sql` using the configured templater.
pub fn template(
    raw_sql: &str,
    fname: &str,
    templater_name: &str,
    config: &ResolvedConfig,
) -> Result<TemplateOutcome> {
    if templater_name == "raw" {
        let tf = TemplatedFile::new(raw_sql.to_string(), fname.to_string(), None, None, None);
        return Ok(TemplateOutcome {
            variants: vec![Arc::new(tf)],
            errors: Vec::new(),
        });
    }

    #[cfg(feature = "embed-python")]
    {
        bridge::template_via_python(raw_sql, fname, config)
    }

    #[cfg(not(feature = "embed-python"))]
    {
        let _ = config;
        anyhow::bail!(
            "templater '{}' requires the embedded Python templater bridge; \
             rebuild with `--features embed-python` (only the 'raw' templater \
             is available in the pure-Rust build)",
            templater_name
        )
    }
}

#[cfg(feature = "embed-python")]
mod bridge {
    use super::*;
    use pyo3::prelude::*;
    use pyo3::types::PyDict;
    use sqlfluffrs_engine::config::{ConfigMap, ConfigValue};
    use sqlfluffrs_python::templater::templatefile::PySqlFluffTemplatedFile;

    /// Reverse-dispatch templating to Python's templaters.
    pub fn template_via_python(
        raw_sql: &str,
        fname: &str,
        config: &ResolvedConfig,
    ) -> Result<TemplateOutcome> {
        Python::attach(|py| {
            ensure_python_paths(py)?;
            let configs = config_to_pydict(py, &config.map)?;

            // Build a FluffConfig from the Rust-resolved config map.
            let fluff_config_cls = py
                .import("sqlfluff.core")
                .map_err(py_err)?
                .getattr("FluffConfig")
                .map_err(py_err)?;
            let kwargs = PyDict::new(py);
            kwargs.set_item("configs", configs).map_err(py_err)?;
            kwargs.set_item("require_dialect", false).map_err(py_err)?;
            let fluff_config = fluff_config_cls.call((), Some(&kwargs)).map_err(py_err)?;

            // Select the templater generically — this is what makes dbt work.
            let templater = fluff_config.call_method0("get_templater").map_err(py_err)?;

            let call_kwargs = PyDict::new(py);
            call_kwargs.set_item("in_str", raw_sql).map_err(py_err)?;
            call_kwargs.set_item("fname", fname).map_err(py_err)?;
            call_kwargs
                .set_item("config", &fluff_config)
                .map_err(py_err)?;
            call_kwargs
                .set_item("formatter", py.None())
                .map_err(py_err)?;
            // Run the templating itself. A raised `SQLTemplaterError` is a
            // *templating failure* driven by the input (e.g. a Jinja syntax
            // error), which Python surfaces as a violation (exit FAIL) — not an
            // internal error — so it is downgraded to a templater error. Any
            // other exception (e.g. a bridge/conversion bug) propagates as a
            // hard failure, mirroring `Linter.render_string`.
            let mut variants = Vec::new();
            let mut errors = Vec::new();
            let mut run = || -> PyResult<()> {
                let variants_iter =
                    templater.call_method("process_with_variants", (), Some(&call_kwargs))?;
                for item in variants_iter.try_iter()? {
                    let tup = item?;
                    let tf_obj = tup.get_item(0)?;
                    let errs_obj = tup.get_item(1)?;
                    if !tf_obj.is_none() {
                        let pf: PySqlFluffTemplatedFile = tf_obj.extract()?;
                        let arc: Arc<TemplatedFile> = pf.into();
                        variants.push(arc);
                    }
                    if !errs_obj.is_none() {
                        for e in errs_obj.try_iter()? {
                            errors.push(e?.str()?.to_string());
                        }
                    }
                }
                Ok(())
            };
            if let Err(e) = run() {
                let templater_err_cls = py
                    .import("sqlfluff.core.errors")
                    .and_then(|m| m.getattr("SQLTemplaterError"))
                    .map_err(py_err)?;
                if e.value(py)
                    .is_instance(&templater_err_cls)
                    .map_err(py_err)?
                {
                    errors.push(e.to_string());
                } else {
                    return Err(py_err(e));
                }
            }
            Ok(TemplateOutcome { variants, errors })
        })
    }

    fn py_err(e: PyErr) -> anyhow::Error {
        anyhow::anyhow!("Python templater error: {e}")
    }

    /// The embedded interpreter is initialized from its build-time config and so
    /// does not automatically pick up an activated virtualenv. When `VIRTUAL_ENV`
    /// is set we add its `site-packages` (running `.pth` files, which also covers
    /// editable installs) so `sqlfluff` and its templater deps resolve. Users of
    /// a non-activated environment can instead set `PYTHONPATH`.
    fn ensure_python_paths(py: Python<'_>) -> Result<()> {
        use std::sync::OnceLock;
        // Store the first run's outcome so every caller observes the same
        // result (a plain `Once` would return fresh `Ok(())`s after a failed
        // initialization).
        static RESULT: OnceLock<std::result::Result<(), String>> = OnceLock::new();
        RESULT
            .get_or_init(|| {
                let code = c"
import os, site, glob
ve = os.environ.get('VIRTUAL_ENV')
if ve:
    for sp in glob.glob(os.path.join(ve, 'lib', 'python*', 'site-packages')):
        site.addsitedir(sp)
    win = os.path.join(ve, 'Lib', 'site-packages')
    if os.path.isdir(win):
        site.addsitedir(win)
";
                py.run(code, None, None).map_err(|e| py_err(e).to_string())
            })
            .clone()
            .map_err(|e| anyhow::anyhow!("{e}"))
    }

    /// Convert a Rust [`ConfigMap`] into a nested Python dict suitable for
    /// `FluffConfig(configs=...)`.
    fn config_to_pydict<'py>(py: Python<'py>, map: &ConfigMap) -> PyResult<Bound<'py, PyDict>> {
        let dict = PyDict::new(py);
        for (key, value) in map {
            match value {
                ConfigValue::Str(s) => dict.set_item(key, s)?,
                ConfigValue::Int(i) => dict.set_item(key, i)?,
                ConfigValue::Bool(b) => dict.set_item(key, b)?,
                ConfigValue::None => dict.set_item(key, py.None())?,
                ConfigValue::Section(sub) => dict.set_item(key, config_to_pydict(py, sub)?)?,
            }
        }
        Ok(dict)
    }
}
