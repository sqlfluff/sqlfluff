use std::sync::{Arc, OnceLock};

use crate::regex::RegexModeGroup;

use super::{CaseFold, Token};

/// Spec for normalizing `raw` (extract the quoted value, replace escapes,
/// casefold), plus the lazily-computed result. Boxed and only present for the
/// minority of tokens that actually carry a transform (string literals, quoted
/// identifiers, the rare casefolded grammar), so the common token pays a single
/// pointer instead of carrying these fields inline.
#[derive(Debug, Clone)]
struct NormalizeSpec {
    quoted_value: Option<(String, RegexModeGroup)>,
    escape_replacements: Option<Arc<Vec<(String, String)>>>,
    casefold: CaseFold,
    /// Config-dependent normalized form, computed at most once. Empty until the
    /// first `normalized()` call (typically only during linting).
    normalized: OnceLock<String>,
}

/// A raw token string together with the forms derived from it: its uppercase
/// version, and its normalized version. Co-locating them keeps the derived
/// forms in sync with `raw` and keeps the eager work out of the hot path.
#[derive(Debug, Clone)]
pub struct RawString {
    raw: String,
    /// Uppercase form. `None` when it is identical to `raw` (whitespace,
    /// punctuation, numbers, already-uppercase text), avoiding a duplicate
    /// allocation for the many tokens with no lowercase letters.
    raw_upper: Option<String>,
    spec: Option<Box<NormalizeSpec>>,
}

impl RawString {
    pub fn new(
        raw: String,
        quoted_value: Option<(String, RegexModeGroup)>,
        escape_replacements: Option<Arc<Vec<(String, String)>>>,
        casefold: CaseFold,
    ) -> Self {
        // Only allocate an uppercase copy when it actually differs from `raw`.
        let raw_upper = if raw.is_ascii() && !raw.bytes().any(|b| b.is_ascii_lowercase()) {
            None
        } else {
            Some(raw.to_uppercase())
        };
        let spec = if quoted_value.is_some()
            || escape_replacements.is_some()
            || casefold != CaseFold::None
        {
            Some(Box::new(NormalizeSpec {
                quoted_value,
                escape_replacements,
                casefold,
                normalized: OnceLock::new(),
            }))
        } else {
            None
        };
        Self {
            raw,
            raw_upper,
            spec,
        }
    }

    pub fn as_str(&self) -> &str {
        &self.raw
    }

    pub fn upper(&self) -> &str {
        self.raw_upper.as_deref().unwrap_or(&self.raw)
    }

    /// Get the quoted_value transform spec (if any).
    pub fn quoted_value(&self) -> Option<&(String, RegexModeGroup)> {
        self.spec.as_ref().and_then(|s| s.quoted_value.as_ref())
    }

    /// Get the escape_replacements transform spec (if any).
    pub fn escape_replacements(&self) -> Option<&Vec<(String, String)>> {
        self.spec
            .as_ref()
            .and_then(|s| s.escape_replacements.as_deref())
    }

    /// Get a cheap (refcount-bumping) clone of the shared escape_replacements
    /// spec, for handing the pairs to a freshly-built token/segment without a
    /// deep copy.
    pub fn escape_replacements_arc(&self) -> Option<Arc<Vec<(String, String)>>> {
        self.spec
            .as_ref()
            .and_then(|s| s.escape_replacements.clone())
    }

    /// Get the casefold mode (`CaseFold::None` when there is no spec).
    pub fn casefold(&self) -> CaseFold {
        self.spec.as_ref().map_or(CaseFold::None, |s| s.casefold)
    }

    /// The normalized form of `raw`, computed at most once. With no transform
    /// spec the result is `raw` itself, so no work or storage is needed.
    pub fn normalized(&self) -> &str {
        match &self.spec {
            None => &self.raw,
            Some(spec) => spec.normalized.get_or_init(|| {
                Token::normalize(
                    &self.raw,
                    spec.quoted_value.as_ref(),
                    spec.escape_replacements.as_deref(),
                )
            }),
        }
    }
}
