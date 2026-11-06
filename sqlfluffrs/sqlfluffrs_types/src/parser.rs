use std::hash::Hash;

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
