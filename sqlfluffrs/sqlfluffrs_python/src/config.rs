use pyo3::{prelude::*, types::PyDict};

use sqlfluffrs_types::config::fluffconfig::FluffConfig as RsFluffConfig;

#[derive(Clone)]
pub struct PyFluffConfig(pub RsFluffConfig);

impl<'py> FromPyObject<'py> for PyFluffConfig {
    fn extract_bound(ob: &pyo3::Bound<'py, PyAny>) -> PyResult<Self> {
        let configs = ob.getattr("_configs")?;
        let configs_dict = configs.downcast::<PyDict>()?;
        let core = configs_dict.get_item("core").ok().flatten().unwrap();
        let core_dict = core.downcast::<PyDict>()?;
        let dialect = core_dict
            .get_item("dialect")
            .ok()
            .flatten()
            .and_then(|x| x.extract::<String>().ok());

        let max_parser_iterations = core_dict
            .get_item("rust_parser_max_iterations")
            .ok()
            .flatten()
            .and_then(|x| x.extract::<usize>().ok());

        let parser_warn_threshold = core_dict
            .get_item("rust_parser_warn_threshold")
            .ok()
            .flatten()
            .and_then(|x| x.extract::<usize>().ok());

        Ok(Self(RsFluffConfig::new(dialect, true).with_parser_limits(
            max_parser_iterations,
            parser_warn_threshold,
        )))
    }
}

impl From<PyFluffConfig> for RsFluffConfig {
    fn from(value: PyFluffConfig) -> Self {
        value.0
    }
}
