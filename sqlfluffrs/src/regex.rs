use std::fmt::Display;

use fancy_regex::{Regex as FancyRegex, RegexBuilder as FancyRegexBuilder};
use regex::{Regex, RegexBuilder};

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

    pub fn capture(&self, group_idx: usize, text: &str) -> Option<String> {
        match self {
            RegexMode::Regex(re) => {
                if let Some(caps) = re.captures(text) {
                    if let Some(m) = caps.get(group_idx) {
                        return Some(m.as_str().to_string());
                    }
                }
                None
            }
            RegexMode::FancyRegex(re) => {
                if let Some(caps) = re.captures(text).ok()? {
                    if let Some(m) = caps.get(group_idx) {
                        return Some(m.as_str().to_string());
                    }
                }
                None
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
