use std::fmt::Display;

use fancy_regex::{Regex as FancyRegex, RegexBuilder as FancyRegexBuilder};
#[cfg(feature = "python")]
use pyo3::pyclass;
use regex::{Regex, RegexBuilder};

#[cfg_attr(feature = "python", pyclass)]
#[derive(Debug, Clone)]
pub enum RegexModeGroup {
    Index(usize),
    Name(String),
}

impl From<usize> for RegexModeGroup {
    fn from(idx: usize) -> Self {
        RegexModeGroup::Index(idx)
    }
}

impl From<&str> for RegexModeGroup {
    fn from(name: &str) -> Self {
        RegexModeGroup::Name(name.to_string())
    }
}

impl From<String> for RegexModeGroup {
    fn from(name: String) -> Self {
        RegexModeGroup::Name(name)
    }
}

#[derive(Debug, Clone)]
pub enum RegexMode {
    Regex(Regex),           // Match using a regex
    FancyRegex(FancyRegex), // Match using a regex
}

impl RegexMode {
    pub fn new(pattern: &str) -> Self {
        // Try to compile with the standard regex first
        if let Ok(re) = RegexBuilder::new(pattern).build() {
            RegexMode::Regex(re)
        } else if let Ok(re) = FancyRegexBuilder::new(pattern).build() {
            RegexMode::FancyRegex(re)
        } else {
            panic!("Invalid regex pattern: {}", pattern);
        }
    }

    pub fn capture(&self, group: impl Into<RegexModeGroup>, text: &str) -> Option<String> {
        match self {
            RegexMode::Regex(re) => {
                let caps = re.captures(text)?;
                match group.into() {
                    RegexModeGroup::Index(idx) => caps.get(idx).map(|m| m.as_str().to_string()),
                    RegexModeGroup::Name(name) => caps.name(&name).map(|m| m.as_str().to_string()),
                }
            }
            RegexMode::FancyRegex(re) => {
                let caps = re.captures(text).ok()??;
                match group.into() {
                    RegexModeGroup::Index(idx) => caps.get(idx).map(|m| m.as_str().to_string()),
                    RegexModeGroup::Name(name) => caps.name(&name).map(|m| m.as_str().to_string()),
                }
            }
        }
    }

    pub fn replace_all(&self, text: &str, replacement: &str) -> String {
        match self {
            RegexMode::Regex(re) => re.replace_all(text, replacement).to_string(),
            RegexMode::FancyRegex(re) => re.replace_all(text, replacement).to_string(),
        }
    }
}

impl Display for RegexMode {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match *self {
            RegexMode::Regex(_) => write!(f, "Regex"),
            RegexMode::FancyRegex(_) => write!(f, "FancyRegex"),
        }
    }
}
