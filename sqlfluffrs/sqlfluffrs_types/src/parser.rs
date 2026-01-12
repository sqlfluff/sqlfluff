use std::hash::Hash;

use hashbrown::HashSet;

/// SimpleHint is used for fast pruning of OneOf alternatives.
/// It represents what raw values and token types a grammar can start with.
/// Based on Python SQLFluff's SimpleHintType.
#[derive(Debug, Clone, PartialEq)]
pub struct SimpleHint {
    /// Uppercase raw strings that this grammar can start with (e.g., {"SELECT", "INSERT"})
    pub raw_values: HashSet<String>,
    /// Token types that this grammar can start with (e.g., {"naked_identifier", "keyword"})
    pub token_types: HashSet<String>,
}

impl SimpleHint {
    /// Create an empty hint (means "complex - can't determine")
    pub fn empty() -> Self {
        Self {
            raw_values: HashSet::new(),
            token_types: HashSet::new(),
        }
    }

    /// Create a hint from a raw string value
    #[inline]
    pub fn from_raw(raw: &str) -> Self {
        let mut set = HashSet::new();
        set.insert(raw.to_uppercase());
        Self {
            raw_values: set,
            token_types: HashSet::new(),
        }
    }

    /// Create a hint from multiple raw string values
    pub fn from_raws(raws: &[&str]) -> Self {
        let raw_values = raws.iter().map(|s| s.to_uppercase()).collect();
        Self {
            raw_values,
            token_types: HashSet::new(),
        }
    }

    /// Create a hint from a token type
    pub fn from_type(type_name: &str) -> Self {
        let mut set = HashSet::new();
        set.insert(type_name.to_string());
        Self {
            raw_values: HashSet::new(),
            token_types: set,
        }
    }

    /// Create a hint from multiple token types
    pub fn from_types(types: &[&str]) -> Self {
        let token_types = types.iter().map(|s| s.to_string()).collect();
        Self {
            raw_values: HashSet::new(),
            token_types,
        }
    }

    /// Union two hints together
    pub fn union(&self, other: &SimpleHint) -> Self {
        Self {
            raw_values: self.raw_values.union(&other.raw_values).cloned().collect(),
            token_types: self
                .token_types
                .union(&other.token_types)
                .cloned()
                .collect(),
        }
    }

    /// Check if this hint can match the given token (using a set of types)
    /// This matches Python's behavior where it checks intersection of hint types with token's class_types
    /// Returns true if the token's raw value OR any type matches, or if hint is empty (can't determine)
    pub fn can_match_token(&self, raw_upper: &str, token_types: &HashSet<String>) -> bool {
        // Empty hint means "complex - can't determine", so return true (must try it)
        if self.is_empty() {
            return true;
        }

        // Check raw value match
        if !self.raw_values.is_empty() && self.raw_values.contains(raw_upper) {
            return true;
        }

        // Check type intersection (Python: first_types.intersection(simple_types))
        if !self.token_types.is_empty() {
            for hint_type in &self.token_types {
                if token_types.contains(hint_type) {
                    return true;
                }
            }
        }

        false
    }

    /// Check if this hint is empty (meaning grammar is too complex to analyze)
    #[inline]
    pub fn is_empty(&self) -> bool {
        self.raw_values.is_empty() && self.token_types.is_empty()
    }
}

/// Parse mode defines how greedy a grammar is in claiming unmatched segments.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Default)]
#[repr(u8)]
pub enum ParseMode {
    /// Strict only returns a match if the full content matches.
    /// If it's not a successful match, don't return any match and never raise unparsable sections.
    /// This is the default for all grammars.
    #[default]
    Strict,
    /// Greedy will always return a match, providing there is at least one code element before
    /// a terminator. Terminators are not included in the match, but are searched for before
    /// matching any content. Segments which are part of any terminator (or beyond) are not
    /// available for matching by any content.
    /// This replicates the `GreedyUntil` semantics.
    Greedy,
    /// A variant on "Greedy" that behaves like "Strict" if nothing matches, but behaves like
    /// "Greedy" once something has matched.
    /// This replicates the `StartsWith` semantics.
    GreedyOnceStarted,
}

/// Root grammar reference containing a GrammarId and GrammarTables.
/// Used for table-driven parsing throughout the codebase.
#[derive(Debug, Clone)]
pub struct RootGrammar {
    pub grammar_id: crate::GrammarId,
    pub tables: &'static crate::GrammarTables,
}

impl RootGrammar {
    /// Create a new RootGrammar from GrammarId and GrammarTables
    pub fn new(grammar_id: crate::GrammarId, tables: &'static crate::GrammarTables) -> Self {
        RootGrammar { grammar_id, tables }
    }
}
