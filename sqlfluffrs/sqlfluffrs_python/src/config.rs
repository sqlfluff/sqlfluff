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

        Ok(Self(RsFluffConfig::new(dialect, true)))
    }
}

impl From<PyFluffConfig> for RsFluffConfig {
    fn from(value: PyFluffConfig) -> Self {
        value.0
    }
}
