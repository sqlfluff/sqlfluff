/// Parse caching module for performance optimization
///
/// This module implements a memoization cache for parse results to avoid
/// redundant parsing operations. It's based on the Python implementation's
/// parse cache which provides 30-50% speedup on complex queries.
use hashbrown::HashMap;
use std::hash::Hash;

use crate::parser::MatchResult;

// ============================================================================
// Table-Driven Parse Cache
// ============================================================================

use sqlfluffrs_types::GrammarId;

/// Cache key for table-driven parser memoization
///
/// Components:
/// - pos: Current position in token stream
/// - grammar_id: The GrammarId being matched (simple u32)
/// - max_idx: Maximum index to parse up to (accounts for terminators)
/// - terminators_hash: Optional hash of terminators (only when non-empty)
///
/// Optimization: We only include terminators_hash when terminators are non-empty.
/// This provides a middle ground between:
/// 1. Always including terminators (cache pollution, slower)
/// 2. Never including terminators (incorrect results in some cases)
///
/// Empty terminators are very common and don't affect parsing behavior beyond
/// max_idx calculation, so omitting the hash in that case dramatically improves
/// cache hit rates.
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct TableCacheKey {
    pub pos: usize,
    pub grammar_id: u32,
    pub max_idx: usize,
    pub terminators_hash: Option<u64>,
}

impl TableCacheKey {
    pub fn new(
        pos: usize,
        grammar_id: GrammarId,
        max_idx: usize,
        terminators: &[GrammarId],
    ) -> Self {
        // Only include terminators_hash when terminators are non-empty
        let terminators_hash = if terminators.is_empty() {
            None
        } else {
            Some(hash_table_terminators(terminators))
        };

        TableCacheKey {
            pos,
            grammar_id: grammar_id.0,
            max_idx,
            terminators_hash,
        }
    }
}

/// Hash terminators for table cache key
/// Sorted to be order-insensitive (terminators semantically form a set)
fn hash_table_terminators(terminators: &[GrammarId]) -> u64 {
    use std::collections::hash_map::DefaultHasher;
    use std::hash::{Hash, Hasher};

    // Collect and sort grammar IDs for order-insensitive hashing
    let mut ids: Vec<u32> = terminators.iter().map(|g| g.0).collect();
    ids.sort_unstable();

    let mut hasher = DefaultHasher::new();
    ids.len().hash(&mut hasher);
    for id in ids {
        id.hash(&mut hasher);
    }
    hasher.finish()
}

/// Cache value for table-driven parser
/// - MatchResult: The lazy parse result (can be converted to Node via apply())
/// - usize: End position after parsing
/// - Option<Vec<usize>>: Transparent token positions collected during parse
pub type TableCacheValue = (MatchResult, usize, Option<Vec<usize>>);

/// Parse result cache for table-driven parser
///
/// This cache is optimized for the table-driven parser which uses GrammarId
/// instead of Arc<Grammar>. The key is much simpler and faster to compute.
pub struct TableParseCache {
    cache: HashMap<TableCacheKey, TableCacheValue>,
    hits: usize,
    misses: usize,
}

impl TableParseCache {
    pub fn new() -> Self {
        TableParseCache {
            cache: HashMap::new(),
            hits: 0,
            misses: 0,
        }
    }

    /// Check cache for a result
    pub fn get(&mut self, key: &TableCacheKey) -> Option<&TableCacheValue> {
        match self.cache.get(key) {
            Some(result) => {
                self.hits += 1;
                log::debug!(
                    "TableCache HIT at pos {} (grammar_id: {}, max_idx: {}, terminators: {})",
                    key.pos,
                    key.grammar_id,
                    key.max_idx,
                    if key.terminators_hash.is_some() {
                        "yes"
                    } else {
                        "no"
                    }
                );
                Some(result)
            }
            None => {
                self.misses += 1;
                log::debug!(
                    "TableCache MISS at pos {} (grammar_id: {}, max_idx: {}, terminators: {})",
                    key.pos,
                    key.grammar_id,
                    key.max_idx,
                    if key.terminators_hash.is_some() {
                        "yes"
                    } else {
                        "no"
                    }
                );
                None
            }
        }
    }

    /// Store a result in cache
    pub fn put(&mut self, key: TableCacheKey, result: TableCacheValue) {
        log::debug!(
            "TableCache INSERT at pos {} (grammar_id: {}, max_idx: {}, terminators: {})",
            key.pos,
            key.grammar_id,
            key.max_idx,
            if key.terminators_hash.is_some() {
                "yes"
            } else {
                "no"
            }
        );
        self.cache.insert(key, result);
    }

    pub fn hit_rate(&self) -> f64 {
        let total = self.hits + self.misses;
        if total == 0 {
            0.0
        } else {
            self.hits as f64 / total as f64
        }
    }

    pub fn stats(&self) -> (usize, usize, f64) {
        (self.hits, self.misses, self.hit_rate())
    }

    pub fn clear(&mut self) {
        self.cache.clear();
        self.hits = 0;
        self.misses = 0;
    }

    pub fn len(&self) -> usize {
        self.cache.len()
    }

    pub fn is_empty(&self) -> bool {
        self.cache.is_empty()
    }

    /// Iterate over cache entries (for analysis/debugging)
    pub fn iter(&self) -> impl Iterator<Item = (&TableCacheKey, &TableCacheValue)> {
        self.cache.iter()
    }
}

impl Default for TableParseCache {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use sqlfluffrs_dialects::Dialect;
    use sqlfluffrs_lexer::{LexInput, Lexer};

    use crate::parser::Parser;

    #[test]
    fn test_cache_functionality() {
        let _ = env_logger::builder().is_test(true).try_init();

        // Parse a simple SELECT statement twice
        let sql = "SELECT a FROM b";
        let input = LexInput::String(sql.to_string());
        let dialect = Dialect::Ansi;

        use sqlfluffrs_dialects::dialect::ansi::matcher::ANSI_LEXERS;
        let lexer = Lexer::new(None, ANSI_LEXERS.to_vec());
        let (tokens, _errors) = lexer.lex(input, false);

        let mut parser = Parser::new(&tokens, dialect, hashbrown::HashMap::new());

        // First parse - should populate cache
        println!("\n=== First Parse (should populate cache) ===");
        match parser.call_rule("SelectStatementSegment", &[]) {
            Ok(_ast) => {
                println!("✓ Parse successful");
                parser.print_cache_stats();
                println!("{:#?}", parser.table_cache.cache)
            }
            Err(e) => {
                panic!("✗ Parse failed: {:?}", e);
            }
        }

        // Reset position
        parser.pos = 0;

        // Second parse - should hit cache heavily
        println!("\n=== Second Parse (should hit cache) ===");
        match parser.call_rule("SelectStatementSegment", &[]) {
            Ok(_ast) => {
                println!("✓ Parse successful");
                parser.print_cache_stats();
                println!("{:#?}", parser.table_cache.cache)
            }
            Err(e) => {
                panic!("✗ Parse failed: {:?}", e);
            }
        }
    }
}
