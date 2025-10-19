//! Macros for parser operations

/// Find the longest matching element from a list of grammar options.
///
/// This macro tries to match each grammar element and returns the one that consumes
/// the most tokens. It supports:
/// - Excluding certain elements (for AnySetOf)
/// - Per-element limits (for AnyNumberOf)
///
/// # Arguments
/// - `$self`: The parser instance
/// - `$elements`: Slice of grammar elements to try
/// - `$working_pos`: Starting position in token stream
/// - `$terminators`: Parent terminators to pass to child parses
/// - `$exclude_keys`: Optional set of cache keys to exclude
/// - `$max_per_elem`: Optional maximum matches per element
/// - `$counter`: Optional counter tracking matches per element
///
/// # Returns
/// `Option<(Node, usize, u64)>` where:
/// - `Node`: The matched parse node
/// - `usize`: End position after match
/// - `u64`: Cache key of matched element
#[macro_export]
macro_rules! find_longest_match {
    ($self:expr, $elements:expr, $working_pos:expr, $terminators:expr, $exclude_keys:expr, $max_per_elem:expr, $counter:expr) => {{
        let mut longest_match: Option<(Node, usize, u64)> = None;

        for element in $elements {
            let element_key = element.cache_key();

            // Skip if this element is in the exclude set (for AnySetOf)
            if let Some(exclude) = $exclude_keys {
                if exclude.contains(&element_key) {
                    log::debug!(
                        "Skipping already-matched element (cache key: {})",
                        element_key
                    );
                    continue;
                }
            }

            // Check if this element has hit its per-element limit (for AnyNumberOf)
            if let (Some(max_per_elem), Some(counter)) = ($max_per_elem, $counter) {
                let elem_count = counter.get(&element_key).copied().unwrap_or(0);
                if elem_count >= *max_per_elem {
                    log::debug!(
                        "Skipping element (cache key: {}) - already matched {} times (max: {})",
                        element_key,
                        elem_count,
                        max_per_elem
                    );
                    continue;
                }
            }

            // Try to match this element
            $self.pos = $working_pos;
            match $self.parse_with_grammar_cached(element, $terminators) {
                Ok(node) if !node.is_empty() => {
                    let end_pos = $self.pos;
                    let consumed = end_pos - $working_pos;

                    // Keep this match if it's the longest so far
                    if longest_match.is_none() || consumed > longest_match.as_ref().unwrap().1 {
                        longest_match = Some((node, consumed, element_key));
                        log::debug!(
                            "New longest match: consumed {} tokens (cache key: {})",
                            consumed,
                            element_key
                        );
                    }
                }
                Ok(_) => {
                    // Empty node, skip
                }
                Err(_) => {
                    // No match for this element
                }
            }
        }

        // Convert to return format: (node, end_pos, element_key)
        longest_match.map(|(node, consumed, key)| (node, $working_pos + consumed, key))
    }};
}
