//! Core Parser struct and implementation
//!
//! This module contains the Parser struct definition and its core methods
//! including the main entry point for parsing with grammar.

use crate::{
    dialect::Dialect,
    parser_cache::{CacheKey, ParseCache},
    token::Token,
};

use super::utils::tag_keyword_if_word;
use super::{Grammar, Node, ParseError};

/// The main parser struct that holds parsing state and provides parsing methods.
pub struct Parser<'a> {
    pub tokens: &'a [Token],
    pub pos: usize, // current position in tokens
    pub dialect: Dialect,
    pub parse_cache: ParseCache,
    pub collected_transparent_positions: std::collections::HashSet<usize>, // Track which token positions have had transparent tokens collected
    pub use_iterative_parser: bool, // Full iterative parser (experimental)
}

impl<'a> Parser<'a> {
    /// Create a new Parser instance
    pub fn new(tokens: &'a [Token], dialect: Dialect) -> Parser<'a> {
        Parser {
            tokens,
            pos: 0,
            dialect,
            parse_cache: ParseCache::new(),
            collected_transparent_positions: std::collections::HashSet::new(),
            use_iterative_parser: true, // Default to iterative parser
        }
    }

    /// Main entry point for parsing with grammar and caching.
    /// Dispatches to either iterative or recursive implementation based on flag.
    pub fn parse_with_grammar_cached(
        &mut self,
        grammar: &Grammar,
        parent_terminators: &[Grammar],
    ) -> Result<Node, ParseError> {
        self.parse_with_grammar_cached_iterative(grammar, parent_terminators)
    }

    /// Iterative (frame-based) parser with caching.
    /// Uses a stack-based approach to avoid deep recursion.
    fn parse_with_grammar_cached_iterative(
        &mut self,
        grammar: &Grammar,
        parent_terminators: &[Grammar],
    ) -> Result<Node, ParseError> {
        self.parse_iterative(grammar, parent_terminators)
    }

    /// Recursive parser with caching.
    /// Uses traditional recursive descent with memoization for performance.
    fn parse_with_grammar_cached_recursive(
        &mut self,
        grammar: &Grammar,
        parent_terminators: &[Grammar],
    ) -> Result<Node, ParseError> {
        // Create cache key
        let cache_key = CacheKey::new(self.pos, grammar, self.tokens);

        // Check cache first
        if let Some(Ok((node, end_pos, collected_positions))) = self.parse_cache.get(&cache_key) {
            self.pos = end_pos; // Directly set to cached end position
                                // Restore collected transparent positions
            let num_positions = collected_positions.len();
            for pos in collected_positions {
                self.collected_transparent_positions.insert(pos);
            }
            log::debug!("Cache HIT restored {} collected positions", num_positions);
            return Ok(node);
        }

        // Cache miss - parse fresh
        let positions_before = self.collected_transparent_positions.clone();
        let result = self.parse_with_grammar(grammar, parent_terminators);

        // Store in cache with collected positions
        if let Ok(ref node) = result {
            // Collect positions that were added during this parse
            let new_positions: Vec<usize> = self
                .collected_transparent_positions
                .difference(&positions_before)
                .copied()
                .collect();

            self.parse_cache
                .put(cache_key, Ok((node.clone(), self.pos, new_positions)));
        }

        result
    }

    /// Get the grammar for a rule by name.
    /// This is used by the iterative parser to expand Ref nodes into their grammars.
    pub fn get_rule_grammar(&self, name: &str) -> Result<Grammar, ParseError> {
        // Look up the grammar for the segment
        match self.get_segment_grammar(name) {
            Some(g) => Ok(g.clone()),
            None => Err(ParseError::unknown_segment(name.to_string())),
        }
    }

    /// Call a grammar rule by name, producing a Node.
    pub fn call_rule(
        &mut self,
        name: &str,
        parent_terminators: &[Grammar],
    ) -> Result<Node, ParseError> {
        // Look up the grammar for the segment
        let grammar = match self.get_segment_grammar(name) {
            Some(g) => g,
            None => return Err(ParseError::unknown_segment(name.to_string())),
        };

        // Parse using the grammar
        let node = self.parse_with_grammar_cached(grammar, parent_terminators)?;

        // If the node is empty, return it as-is without wrapping
        // This prevents infinite loops when optional segments match nothing
        if node.is_empty() {
            return Ok(node);
        }

        // Get the segment type from the dialect
        let segment_type = self.dialect.get_segment_type(name).map(|s| s.to_string());

        // Check if this is a KeywordSegment and the child is a word token
        // If so, convert Node::Code to Node::Keyword
        let processed_node = if name.ends_with("KeywordSegment") {
            tag_keyword_if_word(&node, &self.tokens)
        } else {
            node
        };

        // Wrap in a Ref node for type clarity
        Ok(Node::Ref {
            name: name.to_string(),
            segment_type,
            child: Box::new(processed_node),
        })
    }

    /// Lookup SegmentDef by name
    pub fn get_segment_grammar(&self, name: &str) -> Option<&'static Grammar> {
        self.dialect.get_segment_grammar(name)
    }
}
