#[derive(Clone)]
pub struct FluffConfig {
    pub dialect: Option<String>,
    pub template_blocks_indent: bool,
}

impl FluffConfig {
    pub fn new(dialect: Option<String>, template_blocks_indent: bool) -> Self {
        Self {
            dialect,
            template_blocks_indent,
        }
    }
}

#[cfg(feature = "python")]
pub mod python {
    use pyo3::{
        prelude::*,
        types::{PyDict, PyDictMethods},
    };

    use super::FluffConfig;

    #[derive(Clone)]
    pub struct PyFluffConfig(pub FluffConfig);

    impl<'py> FromPyObject<'py> for PyFluffConfig {
        fn extract_bound(ob: &Bound<'py, PyAny>) -> PyResult<Self> {
            let configs = ob.getattr("_configs")?;
            let configs_dict = configs.downcast::<PyDict>()?;
            let core = configs_dict.get_item("core").ok().flatten().unwrap();
            let core_dict = core.downcast::<PyDict>()?;
            let dialect = core_dict
                .get_item("dialect")
                .ok()
                .flatten()
                .and_then(|x| x.extract::<String>().ok());

            Ok(Self(FluffConfig::new(dialect, true)))
        }
    }
}
