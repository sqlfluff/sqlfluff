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
    Regex(Regex, String),           // Match using a regex, with pattern string
    FancyRegex(FancyRegex, String), // Match using a regex, with pattern string
}

impl RegexMode {
    pub fn new(pattern: &str) -> Self {
        Self::new_with_flags(pattern, true)
    }

    pub fn new_with_flags(pattern: &str, case_insensitive: bool) -> Self {
        // Try to compile with the standard regex first
        if let Ok(re) = RegexBuilder::new(pattern)
            .case_insensitive(case_insensitive)
            .build()
        {
            RegexMode::Regex(re, pattern.to_string())
        } else if let Ok(re) = FancyRegexBuilder::new(pattern)
            .case_insensitive(case_insensitive)
            .build()
        {
            RegexMode::FancyRegex(re, pattern.to_string())
        } else {
            panic!("Invalid regex pattern: {}", pattern);
        }
    }

    pub fn as_str(&self) -> &str {
        match self {
            RegexMode::Regex(_, pattern) => pattern,
            RegexMode::FancyRegex(_, pattern) => pattern,
        }
    }

    pub fn is_match(&self, text: &str) -> bool {
        match self {
            RegexMode::Regex(re, _) => re.is_match(text),
            RegexMode::FancyRegex(re, _) => re.is_match(text).unwrap_or(false),
        }
    }

    pub fn capture(&self, group: impl Into<RegexModeGroup>, text: &str) -> Option<String> {
        match self {
            RegexMode::Regex(re, _) => {
                let caps = re.captures(text)?;
                match group.into() {
                    RegexModeGroup::Index(idx) => caps.get(idx).map(|m| m.as_str().to_string()),
                    RegexModeGroup::Name(name) => caps.name(&name).map(|m| m.as_str().to_string()),
                }
            }
            RegexMode::FancyRegex(re, _) => {
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
            RegexMode::Regex(re, _) => re.replace_all(text, replacement).to_string(),
            RegexMode::FancyRegex(re, _) => re.replace_all(text, replacement).to_string(),
        }
    }
}

impl Display for RegexMode {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match *self {
            RegexMode::Regex(_, _) => write!(f, "Regex"),
            RegexMode::FancyRegex(_, _) => write!(f, "FancyRegex"),
        }
    }
}
