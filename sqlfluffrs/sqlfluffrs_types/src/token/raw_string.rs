use std::sync::OnceLock;

use crate::regex::RegexModeGroup;

use super::Token;

/// A raw token string together with the forms derived from it: its uppercase
/// version (always), and its normalized version (lazily, per the transform
/// spec). Co-locating them keeps the derived forms in sync with `raw` and keeps
/// the eager work out of the hot path.
#[derive(Debug, Clone)]
pub struct RawString {
    raw: String,
    raw_upper: String,
    /// Spec for normalizing `raw`: extract the quoted value / replace escapes.
    quoted_value: Option<(String, RegexModeGroup)>,
    escape_replacement: Option<(String, String)>,
    /// Lazily computed, config-dependent normalized form. Empty until the first
    /// `normalized()` call (typically only during linting), so construction and
    /// parsing pay nothing.
    normalized: OnceLock<String>,
}

impl RawString {
    pub fn new(
        raw: String,
        quoted_value: Option<(String, RegexModeGroup)>,
        escape_replacement: Option<(String, String)>,
    ) -> Self {
        let raw_upper = raw.to_uppercase();
        Self {
            raw,
            raw_upper,
            quoted_value,
            escape_replacement,
            normalized: OnceLock::new(),
        }
    }

    pub fn as_str(&self) -> &str {
        &self.raw
    }

    pub fn upper(&self) -> &str {
        &self.raw_upper
    }

    /// Get the quoted_value transform spec (if any).
    pub fn quoted_value(&self) -> Option<&(String, RegexModeGroup)> {
        self.quoted_value.as_ref()
    }

    /// Get the escape_replacement transform spec (if any).
    pub fn escape_replacement(&self) -> Option<&(String, String)> {
        self.escape_replacement.as_ref()
    }

    /// The normalized form of `raw`, computed at most once. When there is no
    /// transform spec the result is `raw` itself, so no regex work is done.
    pub fn normalized(&self) -> &str {
        self.normalized.get_or_init(|| {
            if self.quoted_value.is_none() && self.escape_replacement.is_none() {
                self.raw.clone()
            } else {
                Token::normalize(
                    &self.raw,
                    self.quoted_value.as_ref(),
                    self.escape_replacement.as_ref(),
                )
            }
        })
    }
}
