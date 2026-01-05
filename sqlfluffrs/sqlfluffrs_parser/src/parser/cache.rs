/// Parse caching module for performance optimization
///
/// This module implements a memoization cache for parse results to avoid
/// redundant parsing operations. It's based on the Python implementation's
/// parse cache which provides 30-50% speedup on complex queries.
///
/// IMPORTANT: Only frame-level caching is used:
/// - Frame-level cache (TableParseCache): Caches complete grammar results
///
/// Element-level caching was removed because after Rc/Arc optimization,
/// the cache overhead (HashMap lookups, key construction) outweighed the
/// benefits (Arc::clone is just an atomic increment, very cheap).
/// Element cache had 0.1% hit rate and added 2% overhead.
use hashbrown::HashMap;
use sqlfluffrs_types::GrammarId;
use std::hash::Hash;
use std::sync::Arc;

use crate::parser::MatchResult;

// ============================================================================
// Element-Level Parse Cache - REMOVED
// ============================================================================
//
// Element-level caching was removed after analysis showed:
// - 0.1% hit rate (2 hits out of 1515 operations)
// - 2% performance overhead
// - After Arc optimization, cache hits only save Arc::clone() (5-10ns)
// - HashMap operations cost more than the savings
//
// See bench_element_cache.rs example for measurement details.
// ============================================================================

// ============================================================================
// Table-Driven Parse Cache (Frame-Level)
// ============================================================================

/// Cache key for table-driven parser memoization
///
/// Components:
/// - pos: Current position in token stream
/// - grammar_id: The GrammarId being matched (simple u32)
/// - max_idx: Maximum index to parse up to (encodes terminator effects)
///
/// PYTHON PARITY: Python's cache key is (raw, loc, type, max_idx).
/// Terminators are NOT in the cache key! Instead, terminators affect max_idx
/// calculation via trim_to_terminator(), so their effect is already captured.
/// This dramatically improves cache hit rates.
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct TableCacheKey {
    pub pos: usize,
    pub grammar_id: u32,
    pub max_idx: usize,
}

impl TableCacheKey {
    /// Create a new cache key.
    ///
    /// PYTHON PARITY: terminators and terminator_hash_cache parameters are now
    /// ignored - we only use (pos, grammar_id, max_idx) just like Python uses
    /// (raw, loc, type, max_idx). The max_idx already encodes terminator effects.
    pub fn new_with_cache(
        pos: usize,
        grammar_id: GrammarId,
        max_idx: usize,
        _terminators: &[GrammarId],
        _terminator_hash_cache: Option<&std::cell::RefCell<hashbrown::HashMap<Vec<u32>, u64>>>,
    ) -> Self {
        TableCacheKey {
            pos,
            grammar_id: grammar_id.0,
            max_idx,
        }
    }

    /// Create a new cache key without hash caching (for backward compatibility).
    pub fn new(
        pos: usize,
        grammar_id: GrammarId,
        max_idx: usize,
        _terminators: &[GrammarId],
    ) -> Self {
        Self::new_with_cache(pos, grammar_id, max_idx, _terminators, None)
    }
}

/// Hash terminators with optional caching.
/// This is the optimized version that uses a cache to avoid recomputing
/// the same hash for frequently-used terminator sets.
fn hash_table_terminators_cached(
    terminators: &[GrammarId],
    cache: Option<&std::cell::RefCell<hashbrown::HashMap<Vec<u32>, u64>>>,
) -> u64 {
    // Collect and sort grammar IDs for order-insensitive hashing
    let mut ids: Vec<u32> = terminators.iter().map(|g| g.0).collect();
    ids.sort_unstable();

    // Check cache if available
    if let Some(cache_ref) = cache {
        if let Some(&cached_hash) = cache_ref.borrow().get(&ids) {
            return cached_hash;
        }
    }

    // Compute hash
    use std::collections::hash_map::DefaultHasher;
    use std::hash::{Hash, Hasher};

    let mut hasher = DefaultHasher::new();
    ids.len().hash(&mut hasher);
    for id in &ids {
        id.hash(&mut hasher);
    }
    let hash = hasher.finish();

    // Store in cache if available
    if let Some(cache_ref) = cache {
        cache_ref.borrow_mut().insert(ids, hash);
    }

    hash
}

/// Hash terminators for table cache key (legacy version without caching).
/// Sorted to be order-insensitive (terminators semantically form a set).
#[allow(dead_code)]
fn hash_table_terminators(terminators: &[GrammarId]) -> u64 {
    hash_table_terminators_cached(terminators, None)
}

/// Cache value for table-driven parser
/// - MatchResult: The lazy parse result (can be converted to Node via apply())
/// - usize: End position after parsing
/// - Option<Vec<usize>>: Transparent token positions collected during parse
pub type TableCacheValue = (Arc<MatchResult>, usize, Option<Vec<usize>>);

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
                    "TableCache HIT at pos {} (grammar_id: {}, max_idx: {})",
                    key.pos,
                    key.grammar_id,
                    key.max_idx,
                );
                Some(result)
            }
            None => {
                self.misses += 1;
                log::debug!(
                    "TableCache MISS at pos {} (grammar_id: {}, max_idx: {})",
                    key.pos,
                    key.grammar_id,
                    key.max_idx,
                );
                None
            }
        }
    }

    /// Store a result in cache
    pub fn put(&mut self, key: TableCacheKey, result: TableCacheValue) {
        log::debug!(
            "TableCache INSERT at pos {} (grammar_id: {}, max_idx: {})",
            key.pos,
            key.grammar_id,
            key.max_idx,
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
