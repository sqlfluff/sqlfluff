/// Parse caching module for performance optimization
///
/// This module implements a memoization cache for parse results to avoid
/// redundant parsing operations. It's based on the Python implementation's
/// parse cache which provides 30-50% speedup on complex queries.
use hashbrown::HashMap;
use std::hash::{Hash, Hasher};

use crate::parser::{Grammar, Node, ParseError};
use crate::token::Token;

// /// A simple match hint that allows quick filtering of grammar options
// /// without performing a full parse. This is the Rust equivalent of the
// /// Python parser's `simple()` method.
// #[derive(Debug, Clone, Default)]
// pub struct SimpleMatch {
//     /// Raw uppercase strings this grammar could match (e.g., "SELECT", "FROM")
//     pub raw_strings: Vec<&'static str>,
//     /// Token types this grammar could match (e.g., "word", "number")
//     pub token_types: Vec<&'static str>,
// }

// impl SimpleMatch {
//     pub fn new(raw_strings: Vec<&'static str>, token_types: Vec<&'static str>) -> Self {
//         SimpleMatch {
//             raw_strings,
//             token_types,
//         }
//     }

//     pub fn from_raws(raws: Vec<&'static str>) -> Self {
//         SimpleMatch {
//             raw_strings: raws,
//             token_types: vec![],
//         }
//     }

//     pub fn from_types(types: Vec<&'static str>) -> Self {
//         SimpleMatch {
//             raw_strings: vec![],
//             token_types: types,
//         }
//     }

//     /// Check if this simple match could match the given token
//     pub fn could_match(&self, token: &Token) -> bool {
//         let raw_upper = token.raw().to_uppercase();

//         // Check raw strings
//         if !self.raw_strings.is_empty()
//             && self
//                 .raw_strings
//                 .iter()
//                 .any(|r| r.eq_ignore_ascii_case(&raw_upper))
//         {
//             return true;
//         }

//         // Check token types
//         if !self.token_types.is_empty() {
//             let token_type = token.get_type();
//             if self.token_types.iter().any(|t| *t == token_type) {
//                 return true;
//             }
//         }

//         // If both are empty, it's a complex matcher - assume it could match
//         self.raw_strings.is_empty() && self.token_types.is_empty()
//     }

//     /// Combine multiple simple matches (used for OneOf)
//     pub fn combine(matches: Vec<SimpleMatch>) -> SimpleMatch {
//         let mut raw_strings = Vec::new();
//         let mut token_types = Vec::new();

//         for m in matches {
//             raw_strings.extend(m.raw_strings);
//             token_types.extend(m.token_types);
//         }

//         // Deduplicate
//         raw_strings.sort_unstable();
//         raw_strings.dedup();
//         token_types.sort_unstable();
//         token_types.dedup();

//         SimpleMatch {
//             raw_strings,
//             token_types,
//         }
//     }
// }

impl Grammar {
    // /// Extract a simple representation of this grammar for fast pruning.
    // ///
    // /// Returns None if the grammar is too complex to simplify.
    // /// Returns Some(SimpleMatch) with the possible raw strings and token types.
    // pub fn simple(&self) -> Option<SimpleMatch> {
    //     match self {
    //         Grammar::StringParser { template, .. } => Some(SimpleMatch::from_raws(vec![template])),
    //         Grammar::MultiStringParser { templates, .. } => {
    //             Some(SimpleMatch::from_raws(templates.to_vec()))
    //         }
    //         Grammar::TypedParser { template, .. } => Some(SimpleMatch::from_types(vec![template])),
    //         Grammar::RegexParser {
    //             template,
    //             token_type,
    //             ..
    //         } => {
    //             // Regex is complex, but we can hint with the token type
    //             Some(SimpleMatch::from_types(vec![token_type]))
    //         }
    //         Grammar::Token { token_type } => Some(SimpleMatch::from_types(vec![token_type])),
    //         Grammar::Sequence { elements, .. } => {
    //             // Return the simple of the first non-optional element
    //             for elem in elements {
    //                 if !is_optional(elem) {
    //                     return elem.simple();
    //                 }
    //             }
    //             // All elements are optional - too complex
    //             None
    //         }
    //         Grammar::OneOf { elements, .. } => {
    //             // Try to combine all element simples
    //             let mut simples = Vec::new();
    //             for elem in elements {
    //                 match elem.simple() {
    //                     Some(s) => simples.push(s),
    //                     None => return None, // If any element is complex, give up
    //                 }
    //             }
    //             Some(SimpleMatch::combine(simples))
    //         }
    //         Grammar::Ref { .. } => {
    //             // References are tricky - would need dialect lookup
    //             // For now, mark as complex
    //             None
    //         }
    //         // Complex grammars that can't be simplified
    //         Grammar::AnyNumberOf { .. }
    //         | Grammar::AnySetOf { .. }
    //         | Grammar::Delimited { .. }
    //         | Grammar::Bracketed { .. }
    //         | Grammar::Anything
    //         | Grammar::Meta(_)
    //         | Grammar::Empty
    //         | Grammar::Nothing()
    //         | Grammar::Missing => None,
    //     }
    // }
}

fn is_optional(grammar: &Grammar) -> bool {
    match grammar {
        Grammar::Sequence { optional, .. } => *optional,
        Grammar::AnyNumberOf { optional, .. } => *optional,
        Grammar::OneOf { optional, .. } => *optional,
        Grammar::AnySetOf { optional, .. } => *optional,
        Grammar::Delimited { optional, .. } => *optional,
        Grammar::Bracketed { optional, .. } => *optional,
        Grammar::Ref { optional, .. } => *optional,
        Grammar::StringParser { optional, .. } => *optional,
        Grammar::MultiStringParser { optional, .. } => *optional,
        Grammar::TypedParser { optional, .. } => *optional,
        Grammar::RegexParser { optional, .. } => *optional,
        _ => false,
    }
}

/// Cache key for memoizing parse results
///
/// Components:
/// - pos: Current position in token stream
/// - grammar_hash: Hash of the grammar being matched
/// - raw: Raw string of token at position (for disambiguation)
/// - max_idx: Length of token stream (accounts for trimming)
/// - terminators_hash: Hash of the terminators (critical for correct caching!)
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct CacheKey {
    pos: usize,
    grammar_hash: u64,
    raw: String,
    max_idx: usize,
    terminators_hash: u64,
}

impl CacheKey {
    pub fn new(pos: usize, grammar: &Grammar, tokens: &[Token], terminators: &[Grammar]) -> Self {
        let grammar_hash = grammar_hash(grammar);
        let raw = tokens
            .get(pos)
            .map(|t| t.raw().to_string())
            .unwrap_or_default();
        let max_idx = tokens.len();

        // Hash the terminators - critical for cache correctness!
        // Same grammar at same position with different terminators should be different cache entries
        let terminators_hash = hash_terminators(terminators);

        CacheKey {
            pos,
            grammar_hash,
            raw,
            max_idx,
            terminators_hash,
        }
    }
}

/// Hash terminators for cache key
fn hash_terminators(terminators: &[Grammar]) -> u64 {
    use std::collections::hash_map::DefaultHasher;
    use std::hash::{Hash, Hasher};

    let mut hasher = DefaultHasher::new();
    terminators.len().hash(&mut hasher);
    for term in terminators {
        grammar_hash(term).hash(&mut hasher);
    }
    hasher.finish()
}

/// Cache value includes:
/// - Node: The parsed result
/// - usize: End position after parsing
/// - Vec<usize>: Transparent token positions collected during this parse
type CacheValue = Result<(Node, usize, Vec<usize>), ParseError>;

/// Compute a stable hash for a grammar
fn grammar_hash(grammar: &Grammar) -> u64 {
    use std::collections::hash_map::DefaultHasher;

    let mut hasher = DefaultHasher::new();
    grammar_discriminant(grammar).hash(&mut hasher);

    // Hash key identifying fields
    match grammar {
        Grammar::StringParser {
            template,
            token_type,
            ..
        } => {
            template.hash(&mut hasher);
            token_type.hash(&mut hasher);
        }
        Grammar::MultiStringParser {
            templates,
            token_type,
            ..
        } => {
            templates.hash(&mut hasher);
            token_type.hash(&mut hasher);
        }
        Grammar::TypedParser {
            template,
            token_type,
            ..
        } => {
            template.hash(&mut hasher);
            token_type.hash(&mut hasher);
        }
        Grammar::RegexParser {
            template,
            token_type,
            ..
        } => {
            template.as_str().hash(&mut hasher);
            token_type.hash(&mut hasher);
        }
        Grammar::Ref { name, .. } => {
            name.hash(&mut hasher);
        }
        Grammar::Token { token_type } => {
            token_type.hash(&mut hasher);
        }
        Grammar::Meta(m) => {
            m.hash(&mut hasher);
        }
        // For compound grammars, hash recursively (expensive but necessary)
        Grammar::Sequence { elements, .. } => {
            for elem in elements {
                grammar_hash(elem).hash(&mut hasher);
            }
        }
        Grammar::OneOf { elements, .. } => {
            for elem in elements {
                grammar_hash(elem).hash(&mut hasher);
            }
        }
        Grammar::AnyNumberOf {
            elements,
            min_times,
            max_times,
            ..
        } => {
            for elem in elements {
                grammar_hash(elem).hash(&mut hasher);
            }
            min_times.hash(&mut hasher);
            max_times.hash(&mut hasher);
        }
        Grammar::Delimited {
            elements,
            delimiter,
            ..
        } => {
            for elem in elements {
                grammar_hash(elem).hash(&mut hasher);
            }
            grammar_hash(delimiter).hash(&mut hasher);
        }
        Grammar::Bracketed {
            elements,
            bracket_pairs,
            ..
        } => {
            for elem in elements {
                grammar_hash(elem).hash(&mut hasher);
            }
            grammar_hash(&bracket_pairs.0).hash(&mut hasher);
            grammar_hash(&bracket_pairs.1).hash(&mut hasher);
        }
        _ => {}
    }

    hasher.finish()
}

fn grammar_discriminant(grammar: &Grammar) -> usize {
    // Rust doesn't expose discriminant directly for custom enums,
    // so we use a match to get a unique number per variant
    match grammar {
        Grammar::Sequence { .. } => 0,
        Grammar::AnyNumberOf { .. } => 1,
        Grammar::OneOf { .. } => 2,
        Grammar::AnySetOf { .. } => 3,
        Grammar::Delimited { .. } => 4,
        Grammar::Bracketed { .. } => 5,
        Grammar::Ref { .. } => 6,
        Grammar::StringParser { .. } => 8,
        Grammar::MultiStringParser { .. } => 9,
        Grammar::TypedParser { .. } => 10,
        Grammar::RegexParser { .. } => 11,
        Grammar::Meta(_) => 12,
        Grammar::Nothing() => 13,
        Grammar::Anything => 14,
        Grammar::Empty => 15,
        Grammar::Missing => 16,
        Grammar::Token { .. } => 17,
    }
}

/// Parse result cache
pub struct ParseCache {
    cache: HashMap<CacheKey, CacheValue>,
    hits: usize,
    misses: usize,
}

impl ParseCache {
    pub fn new() -> Self {
        ParseCache {
            cache: HashMap::new(),
            hits: 0,
            misses: 0,
        }
    }

    pub fn get(&mut self, key: &CacheKey) -> Option<CacheValue> {
        match self.cache.get(key) {
            Some(result) => {
                self.hits += 1;
                log::debug!("Cache HIT at pos {} (hash: {})", key.pos, key.grammar_hash);
                Some(
                    result
                        .clone()
                        .map_err(|msg| ParseError::new(msg.message.clone())),
                )
            }
            None => {
                self.misses += 1;
                log::debug!("Cache MISS at pos {} (hash: {})", key.pos, key.grammar_hash);
                None
            }
        }
    }

    pub fn put(&mut self, key: CacheKey, result: CacheValue) {
        let serialized = result.map_err(|e| ParseError::new(e.message.clone()));
        self.cache.insert(key, serialized);
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
}

impl Default for ParseCache {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use hashbrown::HashSet;

    use super::*;
    use crate::lexer::{LexInput, Lexer};
    use crate::parser::Parser;
    use crate::Dialect;

    #[test]
    fn test_simple_match_string_parser() {
        let grammar = Grammar::StringParser {
            template: "SELECT",
            raw_class: "KeywordSegment",
            token_type: "keyword",
            optional: false,
        };

        let simple_hint = grammar
            .simple_hint_with_dialect(Some(&Dialect::Ansi), &HashSet::new())
            .unwrap();
        assert!(simple_hint.raw_values.contains("SELECT"));
        assert!(simple_hint.token_types.is_empty());
    }

    #[test]
    fn test_simple_match_typed_parser() {
        let grammar = Grammar::TypedParser {
            template: "word",
            raw_class: "IdentifierSegment",
            token_type: "identifier",
            optional: false,
        };

        let simple = grammar
            .simple_hint_with_dialect(Some(&Dialect::Ansi), &HashSet::new())
            .unwrap();
        assert!(simple.raw_values.is_empty());
        assert!(simple.token_types.contains("word"));
    }

    #[test]
    fn test_simple_match_multi_string() {
        let grammar = Grammar::MultiStringParser {
            templates: vec!["SELECT", "INSERT", "UPDATE"],
            raw_class: "KeywordSegment",
            token_type: "keyword",
            optional: false,
        };

        let simple_hint = grammar
            .simple_hint_with_dialect(Some(&Dialect::Ansi), &HashSet::new())
            .unwrap();
        assert_eq!(simple_hint.raw_values.len(), 3);
        assert!(simple_hint.raw_values.contains("SELECT"));
    }

    // #[test]
    // fn test_cache_key_generation() {
    //     use crate::token::Token;

    //     let tokens = vec![
    //         Token::new("SELECT", "keyword", None),
    //         Token::new("*", "star", None),
    //     ];

    //     let grammar = Grammar::StringParser {
    //         template: "SELECT",
    //         token_type: "keyword",
    //         optional: false,
    //     };

    //     let key = CacheKey::new(0, &grammar, &tokens);
    //     assert_eq!(key.pos, 0);
    //     assert_eq!(key.raw, "SELECT");
    //     assert_eq!(key.max_idx, 2);
    // }

    #[test]
    fn test_cache_functionality() {
        // Initialize logger for test runs (safe to call multiple times).
        let _ = env_logger::builder().is_test(true).try_init();

        // Parse a simple SELECT statement twice
        let sql = "SELECT a FROM b";
        let input = LexInput::String(sql.to_string());
        let dialect = Dialect::Ansi;

        let lexer = Lexer::new(None, dialect);
        let (tokens, _errors) = lexer.lex(input, false);

        let mut parser = Parser::new(&tokens, dialect);

        // First parse - should populate cache
        println!("\n=== First Parse (should populate cache) ===");
        match parser.call_rule("SelectStatementSegment", &[]) {
            Ok(_ast) => {
                println!("✓ Parse successful");
                parser.print_cache_stats();
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
            }
            Err(e) => {
                panic!("✗ Parse failed: {:?}", e);
            }
        }
    }
}
