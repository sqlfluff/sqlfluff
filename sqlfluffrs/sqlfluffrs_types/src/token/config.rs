use crate::{regex::RegexModeGroup, token::CaseFold};
use hashbrown::HashSet;
use std::sync::Arc;

/// Configuration for token construction, grouping optional parameters
#[derive(Debug, Clone, Default)]
pub struct TokenConfig {
    pub class_types: HashSet<String>,
    pub instance_types: Vec<String>,
    pub trim_start: Option<Vec<String>>,
    pub trim_chars: Option<Vec<String>>,
    pub quoted_value: Option<(String, RegexModeGroup)>,
    pub escape_replacements: Option<Arc<Vec<(String, String)>>>,
    pub casefold: CaseFold,
}

impl TokenConfig {
    /// Create a new TokenConfig with default values (all empty/None)
    pub fn new() -> Self {
        Self::default()
    }

    /// Create TokenConfig with only instance_types set
    pub fn with_instance_types(instance_types: Vec<String>) -> Self {
        Self {
            instance_types,
            ..Default::default()
        }
    }

    /// Create TokenConfig with class_types and instance_types
    pub fn with_types(class_types: HashSet<String>, instance_types: Vec<String>) -> Self {
        Self {
            class_types,
            instance_types,
            ..Default::default()
        }
    }

    /// Builder method to add trim_start
    pub fn trim_start(mut self, chars: Vec<String>) -> Self {
        self.trim_start = Some(chars);
        self
    }

    /// Builder method to add trim_chars
    pub fn trim_chars(mut self, chars: Vec<String>) -> Self {
        self.trim_chars = Some(chars);
        self
    }

    /// Builder method to add quoted_value
    pub fn quoted_value(mut self, value: String, mode: RegexModeGroup) -> Self {
        self.quoted_value = Some((value, mode));
        self
    }

    /// Builder method to add escape_replacements
    pub fn escape_replacements(mut self, replacements: Vec<(String, String)>) -> Self {
        self.escape_replacements = Some(Arc::new(replacements));
        self
    }

    /// Builder method to add casefold function
    pub fn casefold(mut self, func: CaseFold) -> Self {
        self.casefold = func;
        self
    }
}
