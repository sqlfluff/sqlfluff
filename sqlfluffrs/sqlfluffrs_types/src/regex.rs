use std::fmt::Display;
use std::sync::RwLock;

use fancy_regex::{Regex as FancyRegex, RegexBuilder as FancyRegexBuilder};
use hashbrown::HashMap;
use once_cell::sync::Lazy;
use regex::{Regex, RegexBuilder};

/// Process-global cache of compiled `RegexMode`s, keyed by `(pattern, case_insensitive)`.
///
/// Compiling a regex is orders of magnitude more expensive than matching one, and
/// the same handful of dialect patterns (quoted-value / escape-replacement) are
/// reused across thousands of tokens. Cache the compiled form so each distinct
/// pattern is built at most once.
///
/// Note: the parser keeps its own instance-scoped cache for grammar patterns.
static REGEX_CACHE: Lazy<RwLock<HashMap<(String, bool), RegexMode>>> =
    Lazy::new(|| RwLock::new(HashMap::new()));

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

    /// Like [`RegexMode::new`], but returns a cached compiled regex, only
    /// compiling on the first request for a given pattern.
    pub fn cached(pattern: &str) -> Self {
        Self::cached_with_flags(pattern, true)
    }

    /// Like [`RegexMode::new_with_flags`], but returns a cached compiled regex,
    /// only compiling on the first request for a given `(pattern, flags)`.
    pub fn cached_with_flags(pattern: &str, case_insensitive: bool) -> Self {
        let key = (pattern.to_string(), case_insensitive);
        // Fast path: shared read lock for the common (already-cached) case.
        if let Some(re) = REGEX_CACHE
            .read()
            .unwrap_or_else(|p| p.into_inner())
            .get(&key)
        {
            return re.clone();
        }
        // Slow path: compile under the write lock so each pattern is built at
        // most once even under concurrent first use.
        REGEX_CACHE
            .write()
            .unwrap_or_else(|p| p.into_inner())
            .entry(key)
            .or_insert_with(|| Self::new_with_flags(pattern, case_insensitive))
            .clone()
    }

    pub fn new_with_flags(pattern: &str, case_insensitive: bool) -> Self {
        let pattern = format!("^(?:{})$", pattern);
        // Try to compile with the standard regex first
        if let Ok(re) = RegexBuilder::new(&pattern)
            .case_insensitive(case_insensitive)
            .build()
        {
            RegexMode::Regex(re, pattern.to_string())
        } else if let Ok(re) = FancyRegexBuilder::new(&pattern)
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
