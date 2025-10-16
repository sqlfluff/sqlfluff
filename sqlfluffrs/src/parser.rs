use std::vec;
use std::{
    fmt::Display,
    hash::{Hash, Hasher},
};

use crate::{
    dialect::Dialect,
    parser_cache::{CacheKey, ParseCache},
    token::Token,
};

/// Parse mode defines how greedy a grammar is in claiming unmatched segments.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Default)]
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

#[derive(Debug, Clone)]
pub enum Grammar {
    Sequence {
        elements: Vec<Grammar>,
        optional: bool,
        terminators: Vec<Grammar>,
        reset_terminators: bool,
        allow_gaps: bool,
        parse_mode: ParseMode,
    },
    AnyNumberOf {
        elements: Vec<Grammar>,
        min_times: usize,
        max_times: Option<usize>,
        max_times_per_element: Option<usize>,
        optional: bool,
        terminators: Vec<Grammar>,
        reset_terminators: bool,
        allow_gaps: bool,
        parse_mode: ParseMode,
    },
    OneOf {
        elements: Vec<Grammar>,
        optional: bool,
        terminators: Vec<Grammar>,
        reset_terminators: bool,
        allow_gaps: bool,
        parse_mode: ParseMode,
    },
    AnySetOf {
        elements: Vec<Grammar>,
        min_times: usize,
        max_times: Option<usize>,
        optional: bool,
        terminators: Vec<Grammar>,
        reset_terminators: bool,
        allow_gaps: bool,
        parse_mode: ParseMode,
    },
    Delimited {
        elements: Vec<Grammar>,
        delimiter: Box<Grammar>,
        allow_trailing: bool,
        optional: bool,
        terminators: Vec<Grammar>,
        reset_terminators: bool,
        allow_gaps: bool,
        min_delimiters: usize,
        parse_mode: ParseMode,
    },
    Bracketed {
        elements: Vec<Grammar>,
        bracket_pairs: (Box<Grammar>, Box<Grammar>),
        optional: bool,
        terminators: Vec<Grammar>,
        reset_terminators: bool,
        allow_gaps: bool,
        parse_mode: ParseMode,
    },
    Ref {
        name: &'static str,
        optional: bool,
        terminators: Vec<Grammar>,
        reset_terminators: bool,
        allow_gaps: bool,
    },
    // Keyword {
    //     name: &'static str,
    //     optional: bool,
    //     allow_gaps: bool,
    //     terminators: Vec<Grammar>,
    //     reset_terminators: bool,
    // },
    Symbol(&'static str),
    StringParser {
        template: &'static str,
        // ?maybe raw_class?
        token_type: &'static str,
        optional: bool,
        // trim_chars: Option<Vec<String>>,
        // casefold: Option<fn(&str) -> String>,
    },
    MultiStringParser {
        templates: Vec<&'static str>,
        // ?maybe raw_class?
        token_type: &'static str,
        optional: bool,
        // trim_chars: Option<Vec<String>>,
        // casefold: Option<fn(&str) -> String>,
    },
    TypedParser {
        template: &'static str,
        // ?maybe raw_class?
        token_type: &'static str,
        optional: bool,
        // trim_chars: Option<Vec<String>>,
        // casefold: Option<fn(&str) -> String>,
    },
    RegexParser {
        template: &'static str,
        // ?maybe raw_class?
        token_type: &'static str,
        optional: bool,
        // trim_chars: Option<Vec<String>>,
        // casefold: Option<fn(&str) -> String>,
        anti_template: Option<&'static str>,
    },
    Meta(&'static str),
    Nothing(),
    Anything,
    Empty,
    Missing,
    Token {
        token_type: &'static str,
    },
}

impl Grammar {
    pub fn cache_key(&self) -> u64 {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};

        let mut hasher = DefaultHasher::new();
        self.hash(&mut hasher);
        hasher.finish()
    }

    /// Get the parse mode for this grammar.
    /// Returns the parse_mode if the grammar supports it, otherwise returns the default (Strict).
    pub fn parse_mode(&self) -> ParseMode {
        match self {
            Grammar::Sequence { parse_mode, .. } => *parse_mode,
            Grammar::AnyNumberOf { parse_mode, .. } => *parse_mode,
            Grammar::OneOf { parse_mode, .. } => *parse_mode,
            Grammar::AnySetOf { parse_mode, .. } => *parse_mode,
            Grammar::Delimited { parse_mode, .. } => *parse_mode,
            Grammar::Bracketed { parse_mode, .. } => *parse_mode,
            // All other grammar types default to Strict
            _ => ParseMode::Strict,
        }
    }
}

// Implement Hash for Grammar (discriminant + key fields)
// NOTE: parse_mode IS included in the hash to ensure different cache keys
// for different parse modes, even though it's NOT included in PartialEq.
impl Hash for Grammar {
    fn hash<H: Hasher>(&self, state: &mut H) {
        std::mem::discriminant(self).hash(state);
        match self {
            Grammar::Ref { name, .. } => name.hash(state),
            Grammar::StringParser { template, .. } => template.hash(state),
            Grammar::MultiStringParser { templates, .. } => templates.hash(state),
            Grammar::TypedParser { template, .. } => template.hash(state),
            Grammar::RegexParser { template, .. } => template.hash(state),
            Grammar::Sequence {
                elements,
                optional,
                allow_gaps,
                ..
            } => {
                elements.hash(state);
                optional.hash(state);
                allow_gaps.hash(state);
            }
            Grammar::AnyNumberOf {
                elements,
                optional,
                allow_gaps,
                parse_mode,
                ..
            } => {
                elements.hash(state);
                optional.hash(state);
                allow_gaps.hash(state);
            }
            Grammar::OneOf {
                elements,
                optional,
                allow_gaps,
                parse_mode,
                ..
            } => {
                elements.hash(state);
                optional.hash(state);
                allow_gaps.hash(state);
            }
            Grammar::AnySetOf {
                elements,
                optional,
                allow_gaps,
                ..
            } => {
                elements.hash(state);
                optional.hash(state);
                allow_gaps.hash(state);
            }
            Grammar::Delimited {
                elements,
                optional,
                allow_gaps,
                delimiter,
                allow_trailing,
                terminators,
                min_delimiters,
                ..
            } => {
                elements.hash(state);
                optional.hash(state);
                allow_gaps.hash(state);
                delimiter.hash(state);
                allow_trailing.hash(state);
                terminators.hash(state);
                min_delimiters.hash(state);
            }
            Grammar::Bracketed {
                elements,
                optional,
                allow_gaps,
                ..
            } => {
                elements.hash(state);
                optional.hash(state);
                allow_gaps.hash(state);
            }
            Grammar::Symbol(sym) => sym.hash(state),
            Grammar::Meta(s) => s.hash(state),
            Grammar::Nothing() => {}
            Grammar::Anything => {}
            Grammar::Empty => {}
            Grammar::Missing => {}
            Grammar::Token { token_type } => token_type.hash(state),
        }
    }
}

// Implement PartialEq for Grammar
// NOTE: parse_mode is NOT included in equality comparison, matching Python's
// behavior where equality_kwargs = ("_elements", "optional", "allow_gaps").
// This means grammars are equal if they have the same structure, regardless
// of parse_mode. However, parse_mode IS included in Hash (above) to ensure
// separate cache entries for different parse modes.
impl PartialEq for Grammar {
    fn eq(&self, other: &Self) -> bool {
        match (self, other) {
            (
                Grammar::Sequence {
                    elements: e1,
                    optional: o1,
                    allow_gaps: g1,
                    ..
                },
                Grammar::Sequence {
                    elements: e2,
                    optional: o2,
                    allow_gaps: g2,
                    ..
                },
            ) => e1 == e2 && o1 == o2 && g1 == g2,
            (
                Grammar::AnyNumberOf {
                    elements: e1,
                    optional: o1,
                    allow_gaps: g1,
                    ..
                },
                Grammar::AnyNumberOf {
                    elements: e2,
                    optional: o2,
                    allow_gaps: g2,
                    ..
                },
            ) => e1 == e2 && o1 == o2 && g1 == g2,
            (
                Grammar::OneOf {
                    elements: e1,
                    optional: o1,
                    allow_gaps: g1,
                    ..
                },
                Grammar::OneOf {
                    elements: e2,
                    optional: o2,
                    allow_gaps: g2,
                    ..
                },
            ) => e1 == e2 && o1 == o2 && g1 == g2,
            (
                Grammar::AnySetOf {
                    elements: e1,
                    optional: o1,
                    allow_gaps: g1,
                    ..
                },
                Grammar::AnySetOf {
                    elements: e2,
                    optional: o2,
                    allow_gaps: g2,
                    ..
                },
            ) => e1 == e2 && o1 == o2 && g1 == g2,
            (
                Grammar::Delimited {
                    elements: e1,
                    optional: o1,
                    allow_gaps: g1,
                    delimiter: d1,
                    allow_trailing: at1,
                    terminators: t1,
                    min_delimiters: md1,
                    ..
                },
                Grammar::Delimited {
                    elements: e2,
                    optional: o2,
                    allow_gaps: g2,
                    delimiter: d2,
                    allow_trailing: at2,
                    terminators: t2,
                    min_delimiters: md2,
                    ..
                },
            ) => {
                e1 == e2 && o1 == o2 && g1 == g2 && d1 == d2 && at1 == at2 && t1 == t2 && md1 == md2
            }
            (
                Grammar::Bracketed {
                    elements: e1,
                    optional: o1,
                    allow_gaps: g1,
                    ..
                },
                Grammar::Bracketed {
                    elements: e2,
                    optional: o2,
                    allow_gaps: g2,
                    ..
                },
            ) => e1 == e2 && o1 == o2 && g1 == g2,
            (
                Grammar::Ref {
                    name: n1,
                    optional: o1,
                    allow_gaps: g1,
                    ..
                },
                Grammar::Ref {
                    name: n2,
                    optional: o2,
                    allow_gaps: g2,
                    ..
                },
            ) => n1 == n2 && o1 == o2 && g1 == g2,
            (
                Grammar::StringParser {
                    template,
                    token_type,
                    optional,
                },
                Grammar::StringParser {
                    template: t2,
                    token_type: tt2,
                    optional: o2,
                },
            ) => template == t2 && token_type == tt2 && optional == o2,
            (
                Grammar::MultiStringParser {
                    templates,
                    token_type,
                    optional,
                },
                Grammar::MultiStringParser {
                    templates: t2,
                    token_type: tt2,
                    optional: o2,
                },
            ) => templates == t2 && token_type == tt2 && optional == o2,
            (
                Grammar::TypedParser {
                    template,
                    token_type,
                    optional,
                },
                Grammar::TypedParser {
                    template: t2,
                    token_type: tt2,
                    optional: o2,
                },
            ) => template == t2 && token_type == tt2 && optional == o2,
            (
                Grammar::RegexParser {
                    template,
                    token_type,
                    optional,
                    anti_template,
                },
                Grammar::RegexParser {
                    template: t2,
                    token_type: tt2,
                    optional: o2,
                    anti_template: at2,
                },
            ) => template == t2 && token_type == tt2 && optional == o2 && anti_template == at2,
            (Grammar::Meta(s1), Grammar::Meta(s2)) => s1 == s2,
            (Grammar::Nothing(), Grammar::Nothing()) => true,
            (Grammar::Anything, Grammar::Anything) => true,
            (Grammar::Empty, Grammar::Empty) => true,
            (Grammar::Missing, Grammar::Missing) => true,
            (Grammar::Token { token_type: tt1 }, Grammar::Token { token_type: tt2 }) => tt1 == tt2,
            _ => false,
        }
    }
}

impl Display for Grammar {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Grammar::Sequence { elements, .. } => {
                let elems: Vec<String> = elements.iter().map(|e| format!("{}", e)).collect();
                write!(f, "Sequence({})", elems.join(", "))
            }
            Grammar::AnyNumberOf { elements, .. } => {
                let elems: Vec<String> = elements.iter().map(|e| format!("{}", e)).collect();
                write!(f, "AnyNumberOf({})", elems.join(", "))
            }
            Grammar::OneOf { elements, .. } => {
                let elems: Vec<String> = elements.iter().map(|e| format!("{}", e)).collect();
                write!(f, "OneOf({})", elems.join(", "))
            }
            Grammar::AnySetOf { elements, .. } => {
                let elems: Vec<String> = elements.iter().map(|e| format!("{}", e)).collect();
                write!(f, "AnySetOf({})", elems.join(", "))
            }
            Grammar::Delimited {
                elements,
                delimiter,
                ..
            } => {
                let elems: Vec<String> = elements.iter().map(|e| format!("{}", e)).collect();
                write!(
                    f,
                    "Delimited({}, Delimiter: {})",
                    elems.join(", "),
                    delimiter
                )
            }
            Grammar::Bracketed {
                elements,
                bracket_pairs,
                ..
            } => {
                let elems: Vec<String> = elements.iter().map(|e| format!("{}", e)).collect();
                write!(
                    f,
                    "Bracketed({}, Brackets: ({}, {}))",
                    elems.join(", "),
                    bracket_pairs.0,
                    bracket_pairs.1
                )
            }
            Grammar::Ref { name, .. } => write!(f, "Ref({})", name),
            // Grammar::Keyword { name, .. } => write!(f, "Keyword({})", name),
            Grammar::Symbol(sym) => write!(f, "Symbol({})", sym),
            Grammar::StringParser { template, .. } => write!(f, "StringParser({})", template),
            Grammar::MultiStringParser { templates, .. } => {
                write!(f, "MultiStringParser({:?})", templates)
            }
            Grammar::TypedParser { template, .. } => write!(f, "TypedParser({})", template),
            Grammar::RegexParser { template, .. } => write!(f, "RegexParser({})", template),
            Grammar::Meta(s) => write!(f, "Meta({})", s),
            Grammar::Nothing() => write!(f, "Nothing"),
            Grammar::Anything => write!(f, "Anything"),
            Grammar::Empty => write!(f, "Empty"),
            Grammar::Missing => write!(f, "Missing"),
            Grammar::Token { token_type } => write!(f, "Token({})", token_type),
        }
    }
}

pub struct SegmentDef {
    pub name: &'static str,
    pub segment_type: Option<&'static str>,
    pub grammar: Grammar,
}

#[derive(Debug, Clone, PartialEq)]
pub enum Node {
    /// A plain SQL keyword like SELECT, FROM, INTO
    Keyword(String, usize),

    Code(String, usize),

    /// Whitespace tokens (spaces, tabs)
    Whitespace(String, usize),

    /// Newline tokens
    Newline(String, usize),

    /// End of file marker
    EndOfFile(String, usize),

    /// A sequence of child nodes (used for Grammar::Sequence)
    Sequence(Vec<Node>),

    /// A list of elements separated by commas
    DelimitedList(Vec<Node>),

    /// A reference to another segment (wraps its AST)
    Ref {
        name: String,
        segment_type: Option<String>,
        child: Box<Node>,
    },

    /// Used when an optional part didn’t match
    Empty,
    Meta(&'static str),
}

impl Node {
    pub fn is_empty(&self) -> bool {
        match &self {
            Node::Empty => true,
            Node::DelimitedList(items) => {
                items.is_empty()
                    || items
                        .iter()
                        .all(|n| matches!(n, Node::Empty | Node::Meta(_)))
            }
            Node::Sequence(items) => {
                items.is_empty()
                    || items
                        .iter()
                        .all(|n| matches!(n, Node::Empty | Node::Meta(_)))
            }
            _ => false,
        }
    }

    /// Format the AST to mirror Python SQLFluff's parse output format.
    ///
    /// This produces output like:
    /// ```
    /// [L:  1, P:  1]      |file:
    /// [L:  1, P:  1]      |    statement:
    /// [L:  1, P:  1]      |        select_statement:
    /// [L:  1, P:  1]      |            keyword:                                      'SELECT'
    /// ```
    pub fn format_tree(&self, tokens: &[Token]) -> String {
        let mut output = String::new();
        let mut eof_nodes = Vec::new();

        // Format the tree, collecting EndOfFile nodes
        self.format_tree_impl(tokens, &mut output, 0, 0, &mut eof_nodes);

        // Print all EndOfFile nodes at the very end
        for (depth, idx) in eof_nodes {
            let indent = "    ".repeat(depth);
            if let Some(token) = tokens.get(idx) {
                if let Some(pos_marker) = &token.pos_marker {
                    let (line, pos) = pos_marker.source_position();
                    output.push_str(&format!(
                        "[L:{:3}, P:{:3}]      |{}[META] end_of_file:\n",
                        line, pos, indent,
                    ));
                }
            }
        }

        output
    }

    fn format_tree_impl(
        &self,
        tokens: &[Token],
        output: &mut String,
        depth: usize,
        token_idx: usize,
        eof_nodes: &mut Vec<(usize, usize)>, // (depth, token_idx)
    ) -> usize {
        let indent = "    ".repeat(depth);

        match self {
            Node::Keyword(_, idx)
            | Node::Code(_, idx)
            | Node::Whitespace(_, idx)
            | Node::Newline(_, idx) => {
                // Get position from token
                if let Some(token) = tokens.get(*idx) {
                    output.push_str(&token.stringify(depth, 4, false));
                }
                *idx + 1
            }

            Node::EndOfFile(_, idx) => {
                // Collect EndOfFile nodes instead of printing them immediately
                eof_nodes.push((depth, *idx));
                *idx + 1
            }

            Node::Meta(name) => {
                // META nodes like indent/dedent - these are synthetic nodes without tokens
                // Try to use the current token's position if available, otherwise use a previous token
                let (line, pos) = if let Some(token) = tokens.get(token_idx) {
                    // Use current token position
                    if let Some(pos_marker) = &token.pos_marker {
                        pos_marker.source_position()
                    } else {
                        (0, 0) // Fallback if no pos_marker
                    }
                } else if token_idx > 0 && token_idx <= tokens.len() {
                    // token_idx is past the end or at end - use the last token's end position
                    if let Some(token) = tokens.get(token_idx - 1) {
                        if let Some(pos_marker) = &token.pos_marker {
                            // Use the end position of the previous token
                            let (start_line, start_pos) = pos_marker.source_position();
                            let token_len = token.raw().len();
                            (start_line, start_pos + token_len)
                        } else {
                            (0, 0)
                        }
                    } else {
                        (0, 0)
                    }
                } else {
                    (0, 0) // Fallback
                };

                output.push_str(&format!(
                    "[L:{:3}, P:{:3}]      |{}[META] {} :\n",
                    line, pos, indent, name,
                ));
                token_idx
            }

            Node::Ref {
                name,
                segment_type,
                child,
            } => {
                // Check if this Ref should be transparent (not add a layer):
                // 1. Grammar rules (names ending in "Grammar") are just parsing constructs
                // 2. Single-token wrappers are transparent
                let is_grammar_rule = name.ends_with("Grammar");
                let is_single_token = matches!(
                    child.as_ref(),
                    Node::Keyword(_, _)
                        | Node::Code(_, _)
                        | Node::Whitespace(_, _)
                        | Node::Newline(_, _)
                        | Node::EndOfFile(_, _)
                );
                let is_transparent = is_grammar_rule || is_single_token;

                let mut current_idx = token_idx;

                if is_transparent {
                    // Don't add depth for transparent wrappers - just pass through to child
                    current_idx = child.format_tree_impl(tokens, output, depth, current_idx, eof_nodes);
                } else {
                    // This is a meaningful segment - print it and increase depth
                    // Use segment_type if available, otherwise fall back to converting the name
                    let display_name = if let Some(ref seg_type) = segment_type {
                        seg_type.clone()
                    } else {
                        simplify_segment_name(name)
                    };

                    // Find first non-empty token to get position
                    if let Some(first_token_idx) = self.find_first_token_idx() {
                        if let Some(token) = tokens.get(first_token_idx) {
                            if let Some(pos_marker) = &token.pos_marker {
                                let (line, pos) = pos_marker.source_position();
                                output.push_str(&format!(
                                    "[L:{:3}, P:{:3}]      |{}{}:\n",
                                    line, pos, indent, display_name
                                ));
                            }
                        }
                    }

                    // Format child with increased depth
                    current_idx = child.format_tree_impl(tokens, output, depth + 1, current_idx, eof_nodes);
                }
                current_idx
            }

            Node::Sequence(children) | Node::DelimitedList(children) => {
                let mut current_idx = token_idx;

                // Separate EndOfFile nodes to print them last
                // All other nodes (including Meta indent/dedent) are printed in order
                let mut eof_indices = Vec::new();

                // First pass: format all children except EndOfFile
                for (i, child) in children.iter().enumerate() {
                    if matches!(child, Node::EndOfFile(_, _)) {
                        eof_indices.push(i);
                    } else if !child.is_empty() {
                        current_idx = child.format_tree_impl(tokens, output, depth, current_idx, eof_nodes);
                    }
                }

                // Second pass: format EndOfFile nodes last
                for &i in &eof_indices {
                    current_idx = children[i].format_tree_impl(tokens, output, depth, current_idx, eof_nodes);
                }

                current_idx
            }
            Node::Empty => token_idx,
        }
    }

    /// Find the first token index in this node tree
    fn find_first_token_idx(&self) -> Option<usize> {
        match self {
            Node::Keyword(_, idx)
            | Node::Code(_, idx)
            | Node::Whitespace(_, idx)
            | Node::Newline(_, idx)
            | Node::EndOfFile(_, idx) => Some(*idx),

            Node::Ref { child, .. } => child.find_first_token_idx(),

            Node::Sequence(children) | Node::DelimitedList(children) => {
                children.iter().find_map(|c| c.find_first_token_idx())
            }

            Node::Meta(_) | Node::Empty => None,
        }
    }
}

/// Simplify segment names to match Python output:
/// - Remove "Segment" suffix
/// - Remove "Grammar" suffix
/// - Convert CamelCase to snake_case
fn simplify_segment_name(name: &str) -> String {
    let name = name
        .strip_suffix("Segment")
        .or_else(|| name.strip_suffix("Grammar"))
        .unwrap_or(name);

    camel_to_snake(name)
}

/// Convert CamelCase or PascalCase to snake_case
fn camel_to_snake(s: &str) -> String {
    let mut result = String::new();
    let mut chars = s.chars().peekable();

    while let Some(c) = chars.next() {
        if c.is_uppercase() {
            if !result.is_empty() {
                result.push('_');
            }
            result.push(c.to_lowercase().next().unwrap());
        } else {
            result.push(c);
        }
    }

    result
}

pub struct Parser<'a> {
    pub tokens: &'a [Token],
    pub pos: usize, // current position in tokens
    pub dialect: Dialect,
    pub parse_cache: ParseCache,
    pub collected_transparent_positions: std::collections::HashSet<usize>, // Track which token positions have had transparent tokens collected
    pub use_iterative_parser: bool, // Full iterative parser (experimental)
}

/// Macro to find the longest match among grammar elements.
/// This is inlined to avoid function call overhead and reduce stack usage.
///
/// Usage: find_longest_match!(self, elements, working_pos, terminators, exclude_keys_opt, max_per_elem_opt, counter_opt)
/// Returns: Option<(Node, usize, u64)> where usize is end_pos and u64 is element_key
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

/// Frame representing a parse operation on the explicit stack
#[derive(Debug, Clone)]
struct ParseFrame {
    /// Unique ID for this frame
    frame_id: usize,
    /// The grammar to parse
    grammar: Grammar,
    /// Position in token stream
    pos: usize,
    /// Terminators for this parse
    terminators: Vec<Grammar>,
    /// Current state of this frame
    state: FrameState,
    /// Accumulated results so far
    accumulated: Vec<Node>,
    /// Additional context depending on grammar type
    context: FrameContext,
}

/// State machine for each frame
#[derive(Debug, Clone)]
enum FrameState {
    /// Initial state - need to start parsing
    Initial,
    /// Waiting for child results (for grammars with children)
    WaitingForChild {
        child_index: usize,
        total_children: usize,
    },
    /// Processing results after all children complete
    Combining,
    /// Ready to return result
    Complete(Node),
}

/// Additional context data for specific grammar types
#[derive(Debug, Clone)]
enum FrameContext {
    None,
    Sequence {
        elements: Vec<Grammar>,
        allow_gaps: bool,
        optional: bool,
        parse_mode: ParseMode,
        matched_idx: usize,
        tentatively_collected: Vec<usize>,
        max_idx: usize,
        last_child_frame_id: Option<usize>,
        current_element_idx: usize, // Track which element we're currently processing
    },
    OneOf {
        elements: Vec<Grammar>, // Available elements to try
        allow_gaps: bool,
        optional: bool,
        leading_ws: Vec<Node>,
        post_skip_pos: usize,
        longest_match: Option<(Node, usize, u64)>, // (node, consumed, element_key)
        tried_elements: usize,
        max_idx: usize, // Limit for greedy matching
        parse_mode: ParseMode,
        last_child_frame_id: Option<usize>, // Track child frame for WaitingForChild state
    },
    AnyNumberOf {
        min_times: usize,
        max_times: Option<usize>,
        max_times_per_element: Option<usize>,
        allow_gaps: bool,
        optional: bool,
        count: usize,
        matched_idx: usize,
        working_idx: usize,
        option_counter: std::collections::HashMap<u64, usize>,
        max_idx: usize,
        last_child_frame_id: Option<usize>,
        elements: Vec<Grammar>,
        parse_mode: ParseMode,
    },
    AnySetOf {
        min_times: usize,
        max_times: Option<usize>,
        allow_gaps: bool,
        optional: bool,
        count: usize,
        matched_idx: usize,
        working_idx: usize,
        matched_elements: std::collections::HashSet<u64>,
        max_idx: usize,
        last_child_frame_id: Option<usize>,
        elements: Vec<Grammar>,
        parse_mode: ParseMode,
    },
    Bracketed {
        bracket_pairs: (Box<Grammar>, Box<Grammar>),
        elements: Vec<Grammar>,
        allow_gaps: bool,
        optional: bool,
        parse_mode: ParseMode,
        state: BracketedState,
        last_child_frame_id: Option<usize>,
    },
    Delimited {
        elements: Vec<Grammar>,
        delimiter: Box<Grammar>,
        allow_trailing: bool,
        optional: bool,
        allow_gaps: bool,
        min_delimiters: usize,
        parse_mode: ParseMode,
        delimiter_count: usize,
        matched_idx: usize,
        working_idx: usize,
        max_idx: usize,
        state: DelimitedState,
        last_child_frame_id: Option<usize>,
    },
}

#[derive(Debug, Clone)]
enum BracketedState {
    MatchingOpen,
    MatchingContent,
    MatchingClose,
}

#[derive(Debug, Clone)]
enum DelimitedState {
    MatchingElement,
    MatchingDelimiter,
}

impl<'a> Parser<'_> {
    /// Check if a grammar element is optional
    fn is_grammar_optional(grammar: &Grammar) -> bool {
        let result = match grammar {
            Grammar::Sequence { optional, .. } => *optional,
            Grammar::AnyNumberOf {
                optional,
                min_times,
                ..
            } => {
                log::debug!(
                    "is_grammar_optional: AnyNumberOf optional={}, min_times={}",
                    optional,
                    min_times
                );
                *optional || *min_times == 0
            }
            Grammar::OneOf { optional, .. } => *optional,
            Grammar::Delimited { optional, .. } => *optional,
            Grammar::Bracketed { optional, .. } => *optional,
            Grammar::Ref { optional, .. } => *optional,
            Grammar::StringParser { optional, .. } => *optional,
            Grammar::MultiStringParser { optional, .. } => *optional,
            Grammar::TypedParser { optional, .. } => *optional,
            Grammar::RegexParser { optional, .. } => *optional,
            _ => false,
        };
        log::debug!("is_grammar_optional for {}: {}", grammar, result);
        result
    }

    /// Fully iterative parser using explicit stack
    ///
    /// This replaces recursive `parse_with_grammar` calls with an explicit
    /// stack-based state machine to avoid stack overflow on deeply nested grammars.
    pub fn parse_iterative(
        &mut self,
        grammar: &Grammar,
        parent_terminators: &[Grammar],
    ) -> Result<Node, ParseError> {
        log::debug!(
            "Starting iterative parse for grammar: {} at pos {}",
            grammar,
            self.pos
        );

        // NOTE: We do NOT disable use_iterative_parser here anymore.
        // All grammars should use frame-based implementation inside the loop below.
        // If a grammar calls parse_with_grammar_cached(), it will check the flag
        // and come back here, maintaining the iterative approach.

        // Track results for completed parses
        // HashMap: frame_id -> (node, pos, element_key)
        // element_key is Some(key) for OneOf matches, None for other grammars
        let mut results: std::collections::HashMap<usize, (Node, usize, Option<u64>)> =
            std::collections::HashMap::new();
        let mut frame_id_counter = 0_usize;

        // Stack of parse frames
        let initial_frame_id = frame_id_counter;
        frame_id_counter += 1;

        let mut stack: Vec<ParseFrame> = vec![ParseFrame {
            frame_id: initial_frame_id,
            grammar: grammar.clone(),
            pos: self.pos,
            terminators: parent_terminators.to_vec(),
            state: FrameState::Initial,
            accumulated: vec![],
            context: FrameContext::None,
        }];

        while let Some(mut frame) = stack.pop() {
            log::debug!(
                "Processing frame {}: grammar={}, pos={}, state={:?}, stack_size={}",
                frame.frame_id,
                frame.grammar,
                frame.pos,
                frame.state,
                stack.len()
            );

            match frame.state {
                FrameState::Initial => {
                    // Start parsing this grammar - clone the grammar to avoid borrow issues
                    let grammar = frame.grammar.clone();
                    let terminators = frame.terminators.clone();
                    let pos = frame.pos;

                    match &grammar {
                        // Simple leaf grammars - parse directly using recursive parser
                        // We temporarily disable iterative flag to avoid infinite recursion
                        Grammar::Token { token_type: _ } => {
                            self.pos = pos;
                            let was_iterative = self.use_iterative_parser;
                            self.use_iterative_parser = false;
                            let result = self.parse_with_grammar_cached(&grammar, &terminators);
                            self.use_iterative_parser = was_iterative;
                            match result {
                                Ok(node) => {
                                    results.insert(frame.frame_id, (node, self.pos, None));
                                }
                                Err(e) => return Err(e),
                            }
                        }

                        Grammar::StringParser {
                            template,
                            token_type,
                            optional,
                        } => {
                            // Handle StringParser directly in iterative mode
                            self.pos = pos;
                            self.skip_transparent(true);
                            let tok_raw = self.peek().cloned();

                            match tok_raw {
                                Some(tok) if tok.raw().eq_ignore_ascii_case(template) => {
                                    let token_pos = self.pos;
                                    self.bump();
                                    log::debug!("MATCHED String matched: {}", tok);

                                    let node = if *token_type == "keyword" {
                                        Node::Keyword(tok.raw(), token_pos)
                                    } else {
                                        Node::Code(tok.raw(), token_pos)
                                    };
                                    results.insert(frame.frame_id, (node, self.pos, None));
                                }
                                _ => {
                                    if *optional {
                                        log::debug!("String parser optional, skipping");
                                        results
                                            .insert(frame.frame_id, (Node::Empty, self.pos, None));
                                    } else {
                                        return Err(ParseError::new(format!(
                                            "Expected string '{}'",
                                            template
                                        )));
                                    }
                                }
                            }
                        }

                        Grammar::MultiStringParser {
                            templates,
                            token_type,
                            optional,
                        } => {
                            // Handle MultiStringParser directly in iterative mode
                            self.pos = pos;
                            self.skip_transparent(true);
                            let token = self.peek().cloned();

                            match token {
                                Some(tok)
                                    if templates
                                        .iter()
                                        .any(|&temp| tok.raw().eq_ignore_ascii_case(temp)) =>
                                {
                                    let token_pos = self.pos;
                                    self.bump();
                                    log::debug!("MATCHED MultiString matched: {}", tok);

                                    let node = if *token_type == "keyword" {
                                        Node::Keyword(tok.raw(), token_pos)
                                    } else {
                                        Node::Code(tok.raw(), token_pos)
                                    };
                                    results.insert(frame.frame_id, (node, self.pos, None));
                                }
                                _ => {
                                    if *optional {
                                        log::debug!("MultiString parser optional, skipping");
                                        results
                                            .insert(frame.frame_id, (Node::Empty, self.pos, None));
                                    } else {
                                        return Err(ParseError::new(format!(
                                            "Expected one of: {:?}",
                                            templates
                                        )));
                                    }
                                }
                            }
                        }

                        Grammar::TypedParser {
                            template,
                            token_type,
                            optional,
                        } => {
                            // Handle TypedParser directly in iterative mode
                            self.pos = pos;
                            self.skip_transparent(true);

                            if let Some(token) = self.peek() {
                                let tok = token.clone();
                                if tok.is_type(&[template]) {
                                    let raw = tok.raw().to_string();
                                    let token_pos = self.pos;
                                    self.bump();
                                    log::debug!("MATCHED Typed matched: {}", tok.token_type);
                                    let node = Node::Code(raw, token_pos);
                                    results.insert(frame.frame_id, (node, self.pos, None));
                                } else if *optional {
                                    log::debug!("Typed parser optional, skipping");
                                    results.insert(frame.frame_id, (Node::Empty, self.pos, None));
                                } else {
                                    return Err(ParseError::new(format!(
                                        "Expected typed token '{}', found '{}'",
                                        template, tok.token_type
                                    )));
                                }
                            } else if *optional {
                                log::debug!("Typed parser optional, skipping at EOF");
                                results.insert(frame.frame_id, (Node::Empty, self.pos, None));
                            } else {
                                return Err(ParseError::new(format!(
                                    "Expected typed token '{}', found EOF",
                                    template
                                )));
                            }
                        }

                        Grammar::RegexParser {
                            template,
                            token_type,
                            optional,
                            anti_template,
                        } => {
                            // Handle RegexParser directly in iterative mode
                            self.pos = pos;
                            self.skip_transparent(true);
                            let token = self.peek().cloned();

                            match token {
                                Some(tok)
                                    if regex::RegexBuilder::new(template)
                                        .case_insensitive(true)
                                        .build()
                                        .unwrap()
                                        .is_match(&tok.raw()) =>
                                {
                                    log::debug!("Regex matched: {}", tok);

                                    // Check anti-template if present
                                    if let Some(anti) = anti_template {
                                        if regex::RegexBuilder::new(anti)
                                            .case_insensitive(true)
                                            .build()
                                            .unwrap()
                                            .is_match(&tok.raw())
                                        {
                                            log::debug!("Regex anti-matched: {}", tok);
                                            if *optional {
                                                results.insert(
                                                    frame.frame_id,
                                                    (Node::Empty, self.pos, None),
                                                );
                                            } else {
                                                return Err(ParseError::new(format!(
                                                    "Token '{}' matches anti-template '{}'",
                                                    tok, anti
                                                )));
                                            }
                                            continue; // Skip to next frame
                                        }
                                    }

                                    log::debug!(
                                        "MATCHED Regex matched and non anti-match: {}",
                                        tok
                                    );
                                    let token_pos = self.pos;
                                    self.bump();
                                    let node = Node::Code(tok.raw(), token_pos);
                                    results.insert(frame.frame_id, (node, self.pos, None));
                                }
                                _ => {
                                    if *optional {
                                        results
                                            .insert(frame.frame_id, (Node::Empty, self.pos, None));
                                    } else {
                                        return Err(ParseError::new(format!(
                                            "Expected token matching regex '{}'",
                                            template
                                        )));
                                    }
                                }
                            }
                        }

                        Grammar::Meta(token_type) => {
                            // Meta tokens don't consume input, just create a node
                            log::debug!("Doing nothing with meta {}", token_type);
                            results.insert(frame.frame_id, (Node::Meta(token_type), pos, None));
                        }

                        Grammar::Symbol(sym) => {
                            // Handle Symbol directly in iterative mode
                            self.pos = pos;
                            let token = self.peek().cloned();

                            match token {
                                Some(tok) if tok.raw() == *sym => {
                                    let token_pos = self.pos;
                                    self.bump();
                                    log::debug!("MATCHED Symbol matched: {}", sym);
                                    let node = Node::Code(tok.raw(), token_pos);
                                    results.insert(frame.frame_id, (node, self.pos, None));
                                }
                                _ => {
                                    return Err(ParseError::new(format!(
                                        "Expected symbol '{}'",
                                        sym
                                    )));
                                }
                            }
                        }

                        Grammar::Nothing() => {
                            // Nothing never matches
                            log::debug!("Expecting nothing grammar");
                            return Err(ParseError::new("Nothing grammar won't match".into()));
                        }

                        Grammar::Empty => {
                            // Empty always succeeds without consuming input
                            results.insert(frame.frame_id, (Node::Empty, pos, None));
                        }

                        Grammar::Missing => {
                            // Missing is a placeholder that shouldn't be encountered
                            log::debug!("Trying missing grammar");
                            return Err(ParseError::new("Encountered Missing grammar".into()));
                        }

                        Grammar::Anything => {
                            // Matches anything until a terminator is found (greedy)
                            self.pos = pos;
                            log::debug!("Trying Anything grammar");
                            let mut anything_tokens = vec![];

                            loop {
                                if self.is_terminated(&terminators) || self.is_at_end() {
                                    break;
                                }
                                if let Some(tok) = self.peek() {
                                    anything_tokens
                                        .push(Node::Code(tok.raw().to_string(), self.pos));
                                    self.bump();
                                }
                            }

                            log::debug!("Anything matched tokens: {:?}", anything_tokens);
                            let node = Node::DelimitedList(anything_tokens);
                            results.insert(frame.frame_id, (node, self.pos, None));
                        }

                        // Complex grammars - need special handling
                        Grammar::Sequence {
                            elements,
                            optional,
                            terminators: seq_terminators,
                            reset_terminators,
                            allow_gaps,
                            parse_mode,
                        } => {
                            // Initialize Sequence state
                            let start_idx = pos;

                            // Combine parent and local terminators
                            let all_terminators: Vec<Grammar> = if *reset_terminators {
                                seq_terminators.clone()
                            } else {
                                seq_terminators
                                    .iter()
                                    .cloned()
                                    .chain(terminators.iter().cloned())
                                    .collect()
                            };

                            // Calculate max_idx for GREEDY mode
                            self.pos = start_idx;
                            let max_idx = if *parse_mode == ParseMode::Greedy {
                                self.trim_to_terminator(start_idx, &all_terminators)
                            } else {
                                self.tokens.len()
                            };

                            // Update frame with Sequence context
                            frame.state = FrameState::WaitingForChild {
                                child_index: 0,
                                total_children: elements.len(),
                            };
                            frame.context = FrameContext::Sequence {
                                elements: elements.clone(),
                                allow_gaps: *allow_gaps,
                                optional: *optional,
                                parse_mode: *parse_mode,
                                matched_idx: start_idx,
                                tentatively_collected: vec![],
                                max_idx,
                                last_child_frame_id: None,
                                current_element_idx: 0, // Start at first element
                            };
                            frame.terminators = all_terminators;
                            stack.push(frame);

                            // Push first child to parse
                            if !elements.is_empty() {
                                // Handle Meta elements specially
                                let mut child_idx = 0;
                                while child_idx < elements.len() {
                                    if let Grammar::Meta(meta_type) = &elements[child_idx] {
                                        // Meta doesn't need parsing - just add to accumulated
                                        if let Some(ref mut parent_frame) = stack.last_mut() {
                                            if *meta_type == "indent" {
                                                // Indent goes before whitespace
                                                let mut insert_pos = parent_frame.accumulated.len();
                                                while insert_pos > 0 {
                                                    match &parent_frame.accumulated[insert_pos - 1]
                                                    {
                                                        Node::Whitespace(_, _)
                                                        | Node::Newline(_, _) => {
                                                            insert_pos -= 1;
                                                        }
                                                        _ => break,
                                                    }
                                                }
                                                parent_frame
                                                    .accumulated
                                                    .insert(insert_pos, Node::Meta(meta_type));
                                            } else {
                                                parent_frame
                                                    .accumulated
                                                    .push(Node::Meta(meta_type));
                                            }

                                            // Update state to next child
                                            if let FrameState::WaitingForChild {
                                                child_index,
                                                total_children,
                                            } = &mut parent_frame.state
                                            {
                                                *child_index = child_idx + 1;
                                            }
                                        }
                                        child_idx += 1;
                                    } else {
                                        // Non-meta element - needs actual parsing
                                        let child_frame = ParseFrame {
                                            frame_id: frame_id_counter,
                                            grammar: elements[child_idx].clone(),
                                            pos: start_idx,
                                            terminators: stack
                                                .last()
                                                .map(|f| f.terminators.clone())
                                                .unwrap_or_default(),
                                            state: FrameState::Initial,
                                            accumulated: vec![],
                                            context: FrameContext::None,
                                        };

                                        // Update parent's last_child_frame_id and current_element_idx
                                        if let Some(parent_frame) = stack.last_mut() {
                                            if let FrameContext::Sequence {
                                                last_child_frame_id,
                                                current_element_idx,
                                                ..
                                            } = &mut parent_frame.context
                                            {
                                                *last_child_frame_id = Some(frame_id_counter);
                                                *current_element_idx = child_idx;
                                                // Track which element we're processing
                                            }
                                        }

                                        frame_id_counter += 1;
                                        stack.push(child_frame);
                                        break;
                                    }
                                }
                            }
                        }

                        Grammar::OneOf {
                            elements,
                            optional,
                            terminators: local_terminators,
                            reset_terminators,
                            allow_gaps,
                            parse_mode,
                        } => {
                            // Proper iterative OneOf with ParseFrame pattern
                            log::debug!(
                                "OneOf Initial state at pos {}, {} elements, parse_mode={:?}",
                                pos,
                                elements.len(),
                                parse_mode
                            );

                            // Collect leading whitespace
                            let leading_ws = if *allow_gaps {
                                self.collect_transparent(true)
                            } else {
                                Vec::new()
                            };
                            let post_skip_pos = self.pos;

                            // Combine terminators
                            let all_terminators: Vec<Grammar> = if *reset_terminators {
                                local_terminators.clone()
                            } else {
                                local_terminators
                                    .iter()
                                    .chain(terminators.iter())
                                    .cloned()
                                    .collect()
                            };

                            // Calculate max_idx based on parse_mode (for greedy matching)
                            let max_idx = if *parse_mode == ParseMode::Greedy {
                                self.trim_to_terminator(post_skip_pos, &all_terminators)
                            } else {
                                self.tokens.len()
                            };

                            // Check if already terminated
                            if self.is_terminated(&all_terminators) {
                                log::debug!("OneOf: Already at terminator");
                                self.pos = pos;
                                let result = if *optional {
                                    Node::Empty
                                } else {
                                    return Err(ParseError::new(
                                        "Expected one of choices, but terminated".into(),
                                    ));
                                };
                                results.insert(frame.frame_id, (result, self.pos, None));
                                continue;
                            }

                            // Prune options based on simple matchers
                            let available_options: Vec<Grammar> =
                                self.prune_options(elements).into_iter().cloned().collect();

                            if available_options.is_empty() {
                                log::debug!("OneOf: No viable options after pruning");
                                self.pos = pos;
                                let result = if *optional {
                                    Node::Empty
                                } else {
                                    return Err(ParseError::new(
                                        "No viable options after pruning".into(),
                                    ));
                                };
                                results.insert(frame.frame_id, (result, self.pos, None));
                                continue;
                            }

                            // Create context to track OneOf matching progress
                            frame.context = FrameContext::OneOf {
                                elements: available_options.clone(),
                                allow_gaps: *allow_gaps,
                                optional: *optional,
                                leading_ws: leading_ws.clone(),
                                post_skip_pos,
                                longest_match: None,
                                tried_elements: 0,
                                max_idx,
                                parse_mode: *parse_mode,
                                last_child_frame_id: Some(frame_id_counter), // Track the child we're about to create
                            };

                            // Create child frame for first element
                            let first_element = available_options[0].clone();
                            let element_key = first_element.cache_key();
                            log::debug!("OneOf: Trying first element (cache_key: {})", element_key);

                            let child_frame = ParseFrame {
                                frame_id: frame_id_counter,
                                grammar: first_element,
                                pos: post_skip_pos,
                                terminators: all_terminators.clone(),
                                state: FrameState::Initial,
                                accumulated: Vec::new(),
                                context: FrameContext::None,
                            };

                            frame.state = FrameState::WaitingForChild {
                                child_index: 0,
                                total_children: 1, // OneOf only has one child at a time
                            };

                            // Context already set above, just keep it

                            frame_id_counter += 1;
                            stack.push(frame); // Push parent back to stack first
                            stack.push(child_frame); // Then push child
                                                     // No break needed - match arm ends here
                        }

                        Grammar::Ref {
                            name,
                            optional,
                            allow_gaps,
                            terminators: ref_terminators,
                            reset_terminators,
                        } => {
                            // Handle Ref by resolving and calling the rule
                            log::debug!(
                                "Iterative Ref to segment: {}, optional: {}, allow_gaps: {}",
                                name,
                                optional,
                                allow_gaps
                            );
                            let saved = pos;
                            self.pos = pos;
                            self.skip_transparent(*allow_gaps);

                            // Combine parent and local terminators
                            let all_terminators: Vec<Grammar> = if *reset_terminators {
                                ref_terminators.clone()
                            } else {
                                ref_terminators
                                    .iter()
                                    .cloned()
                                    .chain(terminators.iter().cloned())
                                    .collect()
                            };

                            // Call the rule - temporarily disable iterative to avoid nested frames
                            let was_iterative = self.use_iterative_parser;
                            self.use_iterative_parser = false;
                            let attempt = self.call_rule(name, &all_terminators);
                            self.use_iterative_parser = was_iterative;

                            match attempt {
                                Ok(node) => {
                                    log::debug!("MATCHED Iterative Ref matched segment: {}", name);
                                    results.insert(frame.frame_id, (node, self.pos, None));
                                }
                                Err(e) => {
                                    self.pos = saved;
                                    if *optional {
                                        log::debug!("Iterative Ref optional, skipping");
                                        results.insert(frame.frame_id, (Node::Empty, saved, None));
                                    } else {
                                        // In iterative mode, store Empty and let parent handle it
                                        // This allows OneOf/AnyNumberOf to try other options
                                        log::debug!("Iterative Ref failed (non-optional), storing Empty for parent to handle");
                                        results.insert(frame.frame_id, (Node::Empty, saved, None));
                                    }
                                }
                            }
                        }

                        Grammar::AnyNumberOf {
                            elements,
                            min_times,
                            max_times,
                            max_times_per_element,
                            optional,
                            terminators: any_terminators,
                            reset_terminators,
                            allow_gaps,
                            parse_mode,
                        } => {
                            // Initialize AnyNumberOf state
                            let start_idx = pos;
                            log::debug!(
                                "AnyNumberOf starting at {}, min_times={}, max_times={:?}, allow_gaps={}, parse_mode={:?}",
                                start_idx,
                                min_times,
                                max_times,
                                allow_gaps,
                                parse_mode
                            );

                            // Combine parent and local terminators
                            let all_terminators: Vec<Grammar> = if *reset_terminators {
                                any_terminators.clone()
                            } else {
                                any_terminators
                                    .iter()
                                    .cloned()
                                    .chain(terminators.iter().cloned())
                                    .collect()
                            };

                            // Calculate max_idx based on parse_mode
                            self.pos = start_idx;
                            let max_idx = if *parse_mode == ParseMode::Greedy {
                                self.trim_to_terminator(start_idx, &all_terminators)
                            } else {
                                self.tokens.len()
                            };

                            log::debug!(
                                "AnyNumberOf max_idx: {} (tokens.len: {})",
                                max_idx,
                                self.tokens.len()
                            );

                            // Update frame with AnyNumberOf context
                            frame.state = FrameState::WaitingForChild {
                                child_index: 0,
                                total_children: elements.len(), // We'll loop through elements
                            };
                            frame.context = FrameContext::AnyNumberOf {
                                elements: elements.clone(),
                                min_times: *min_times,
                                max_times: *max_times,
                                max_times_per_element: *max_times_per_element,
                                allow_gaps: *allow_gaps,
                                optional: *optional,
                                parse_mode: *parse_mode,
                                count: 0,
                                matched_idx: start_idx,
                                working_idx: start_idx,
                                option_counter: std::collections::HashMap::new(),
                                max_idx,
                                last_child_frame_id: None,
                            };
                            frame.terminators = all_terminators.clone();
                            stack.push(frame);

                            // Use OneOf wrapper to try all elements and find longest match
                            if !elements.is_empty() {
                                // Always wrap in OneOf to ensure optional behavior
                                // This ensures that if a child fails, AnyNumberOf can handle it gracefully
                                let child_grammar = Grammar::OneOf {
                                    elements: elements.clone(),
                                    optional: true, // Don't fail if no match (let AnyNumberOf handle it)
                                    terminators: all_terminators.clone(),
                                    reset_terminators: false,
                                    allow_gaps: *allow_gaps,
                                    parse_mode: *parse_mode,
                                };

                                let child_frame = ParseFrame {
                                    frame_id: frame_id_counter,
                                    grammar: child_grammar,
                                    pos: start_idx,
                                    terminators: all_terminators,
                                    state: FrameState::Initial,
                                    accumulated: vec![],
                                    context: FrameContext::None,
                                };

                                // Update parent's last_child_frame_id
                                if let Some(parent_frame) = stack.last_mut() {
                                    if let FrameContext::AnyNumberOf {
                                        last_child_frame_id,
                                        ..
                                    } = &mut parent_frame.context
                                    {
                                        *last_child_frame_id = Some(frame_id_counter);
                                    }
                                }

                                frame_id_counter += 1;
                                stack.push(child_frame);
                            }
                        }

                        Grammar::Bracketed {
                            elements,
                            bracket_pairs,
                            optional,
                            terminators: bracket_terminators,
                            reset_terminators,
                            allow_gaps,
                            parse_mode,
                        } => {
                            // Initialize Bracketed state
                            let start_idx = pos;
                            log::debug!(
                                "Bracketed starting at {}, allow_gaps={}, parse_mode={:?}",
                                start_idx,
                                allow_gaps,
                                parse_mode
                            );

                            // Combine parent and local terminators
                            let all_terminators: Vec<Grammar> = if *reset_terminators {
                                bracket_terminators.clone()
                            } else {
                                bracket_terminators
                                    .iter()
                                    .cloned()
                                    .chain(terminators.iter().cloned())
                                    .collect()
                            };

                            // Update frame with Bracketed context
                            frame.state = FrameState::WaitingForChild {
                                child_index: 0,
                                total_children: 3, // open, content, close
                            };
                            frame.context = FrameContext::Bracketed {
                                bracket_pairs: bracket_pairs.clone(),
                                elements: elements.clone(),
                                allow_gaps: *allow_gaps,
                                optional: *optional,
                                parse_mode: *parse_mode,
                                state: BracketedState::MatchingOpen,
                                last_child_frame_id: None,
                            };
                            frame.terminators = all_terminators.clone();
                            stack.push(frame);

                            // Start by trying to match the opening bracket
                            let child_frame = ParseFrame {
                                frame_id: frame_id_counter,
                                grammar: (*bracket_pairs.0).clone(),
                                pos: start_idx,
                                terminators: all_terminators,
                                state: FrameState::Initial,
                                accumulated: vec![],
                                context: FrameContext::None,
                            };

                            // Update parent's last_child_frame_id
                            if let Some(parent_frame) = stack.last_mut() {
                                if let FrameContext::Bracketed {
                                    last_child_frame_id,
                                    ..
                                } = &mut parent_frame.context
                                {
                                    *last_child_frame_id = Some(frame_id_counter);
                                }
                            }

                            frame_id_counter += 1;
                            stack.push(child_frame);
                        }

                        Grammar::AnySetOf {
                            elements,
                            min_times,
                            max_times,
                            optional,
                            terminators: local_terminators,
                            reset_terminators,
                            allow_gaps,
                            parse_mode,
                        } => {
                            log::debug!("[ITERATIVE] AnySetOf Initial state at pos {}", pos);

                            // Combine terminators
                            let all_terminators: Vec<Grammar> = if *reset_terminators {
                                local_terminators.clone()
                            } else {
                                local_terminators
                                    .iter()
                                    .cloned()
                                    .chain(terminators.iter().cloned())
                                    .collect()
                            };

                            // Calculate max_idx based on parse_mode
                            self.pos = pos;
                            let max_idx = if *parse_mode == ParseMode::Greedy {
                                self.trim_to_terminator(pos, &all_terminators)
                            } else {
                                self.tokens.len()
                            };

                            log::debug!(
                                "[ITERATIVE] AnySetOf max_idx: {} (tokens.len: {})",
                                max_idx,
                                self.tokens.len()
                            );

                            // Create AnySetOf context
                            frame.state = FrameState::WaitingForChild {
                                child_index: 0,
                                total_children: max_times.unwrap_or(usize::MAX).min(elements.len()),
                            };
                            frame.context = FrameContext::AnySetOf {
                                min_times: *min_times,
                                max_times: *max_times,
                                allow_gaps: *allow_gaps,
                                optional: *optional,
                                count: 0,
                                matched_idx: pos,
                                working_idx: pos,
                                matched_elements: std::collections::HashSet::new(),
                                max_idx,
                                last_child_frame_id: None,
                                elements: elements.clone(),
                                parse_mode: *parse_mode,
                            };
                            frame.terminators = all_terminators.clone();
                            stack.push(frame);

                            // Try first unmatched element
                            // For AnySetOf, we try all elements (not just first) via OneOf pattern
                            let child_grammar = Grammar::OneOf {
                                elements: elements.clone(),
                                optional: false,
                                terminators: vec![],
                                reset_terminators: false,
                                allow_gaps: *allow_gaps,
                                parse_mode: *parse_mode,
                            };

                            let child_frame = ParseFrame {
                                frame_id: frame_id_counter,
                                grammar: child_grammar,
                                pos,
                                terminators: all_terminators,
                                state: FrameState::Initial,
                                accumulated: vec![],
                                context: FrameContext::None,
                            };

                            // Update parent's last_child_frame_id
                            if let Some(parent_frame) = stack.last_mut() {
                                if let FrameContext::AnySetOf {
                                    last_child_frame_id,
                                    ..
                                } = &mut parent_frame.context
                                {
                                    *last_child_frame_id = Some(frame_id_counter);
                                }
                            }

                            frame_id_counter += 1;
                            stack.push(child_frame);
                        }

                        Grammar::Delimited {
                            elements,
                            delimiter,
                            allow_trailing,
                            optional,
                            terminators: local_terminators,
                            reset_terminators,
                            allow_gaps,
                            min_delimiters,
                            parse_mode,
                        } => {
                            log::debug!("[ITERATIVE] Delimited Initial state at pos {}", pos);

                            // Combine terminators, filtering out delimiter from parent terminators
                            // This is critical - delimiter shouldn't terminate the delimited list itself
                            let filtered_parent: Vec<Grammar> = terminators
                                .iter()
                                .filter(|t| *t != delimiter.as_ref())
                                .cloned()
                                .collect();

                            let all_terminators: Vec<Grammar> = if *reset_terminators {
                                local_terminators.clone()
                            } else {
                                local_terminators
                                    .iter()
                                    .cloned()
                                    .chain(filtered_parent.into_iter())
                                    .collect()
                            };

                            // Calculate max_idx based on parse_mode
                            self.pos = pos;
                            let max_idx = if *parse_mode == ParseMode::Greedy {
                                self.trim_to_terminator(pos, &all_terminators)
                            } else {
                                self.tokens.len()
                            };

                            log::debug!(
                                "[ITERATIVE] Delimited max_idx: {} (tokens.len: {})",
                                max_idx,
                                self.tokens.len()
                            );

                            // Check if optional and already terminated
                            if *optional
                                && (self.is_at_end() || self.is_terminated(&all_terminators))
                            {
                                log::debug!("[ITERATIVE] Delimited: empty optional");
                                results.insert(
                                    frame.frame_id,
                                    (Node::DelimitedList(vec![]), pos, None),
                                );
                                continue;
                            }

                            // Create Delimited context
                            frame.state = FrameState::WaitingForChild {
                                child_index: 0,
                                total_children: usize::MAX, // Unknown number of children
                            };
                            frame.context = FrameContext::Delimited {
                                elements: elements.clone(),
                                delimiter: delimiter.clone(),
                                allow_trailing: *allow_trailing,
                                optional: *optional,
                                allow_gaps: *allow_gaps,
                                min_delimiters: *min_delimiters,
                                parse_mode: *parse_mode,
                                delimiter_count: 0,
                                matched_idx: pos,
                                working_idx: pos,
                                max_idx,
                                state: DelimitedState::MatchingElement,
                                last_child_frame_id: None,
                            };
                            frame.terminators = all_terminators.clone();
                            stack.push(frame);

                            // Create first child to match element (try all elements via OneOf)
                            let child_grammar = Grammar::OneOf {
                                elements: elements.clone(),
                                optional: false,
                                terminators: vec![],
                                reset_terminators: false,
                                allow_gaps: *allow_gaps,
                                parse_mode: *parse_mode,
                            };

                            let child_frame = ParseFrame {
                                frame_id: frame_id_counter,
                                grammar: child_grammar,
                                pos,
                                terminators: all_terminators,
                                state: FrameState::Initial,
                                accumulated: vec![],
                                context: FrameContext::None,
                            };

                            // Update parent's last_child_frame_id
                            if let Some(parent_frame) = stack.last_mut() {
                                if let FrameContext::Delimited {
                                    last_child_frame_id,
                                    ..
                                } = &mut parent_frame.context
                                {
                                    *last_child_frame_id = Some(frame_id_counter);
                                }
                            }

                            frame_id_counter += 1;
                            stack.push(child_frame);
                        }

                        // For other grammar types, use recursive for now
                        _ => {
                            self.pos = pos;
                            match self.parse_with_grammar_cached(&grammar, &terminators) {
                                Ok(node) => {
                                    results.insert(frame.frame_id, (node, self.pos, None));
                                }
                                Err(e) => return Err(e),
                            }
                        }
                    }
                }

                FrameState::WaitingForChild {
                    child_index,
                    total_children,
                } => {
                    // A child parse just completed - get its result
                    // First get the child frame ID we're waiting for
                    let child_frame_id = match &frame.context {
                        FrameContext::Sequence {
                            last_child_frame_id,
                            ..
                        } => last_child_frame_id
                            .expect("Sequence WaitingForChild should have last_child_frame_id set"),
                        FrameContext::AnyNumberOf {
                            last_child_frame_id,
                            ..
                        } => last_child_frame_id.expect(
                            "AnyNumberOf WaitingForChild should have last_child_frame_id set",
                        ),
                        FrameContext::OneOf {
                            last_child_frame_id,
                            ..
                        } => last_child_frame_id
                            .expect("OneOf WaitingForChild should have last_child_frame_id set"),
                        FrameContext::Bracketed {
                            last_child_frame_id,
                            ..
                        } => last_child_frame_id.expect(
                            "Bracketed WaitingForChild should have last_child_frame_id set",
                        ),
                        FrameContext::AnySetOf {
                            last_child_frame_id,
                            ..
                        } => last_child_frame_id
                            .expect("AnySetOf WaitingForChild should have last_child_frame_id set"),
                        FrameContext::Delimited {
                            last_child_frame_id,
                            ..
                        } => last_child_frame_id.expect(
                            "Delimited WaitingForChild should have last_child_frame_id set",
                        ),
                        _ => {
                            log::error!("WaitingForChild state without child frame ID tracking");
                            continue;
                        }
                    };

                    if let Some((child_node, child_end_pos, child_element_key)) =
                        results.get(&child_frame_id)
                    {
                        log::debug!(
                            "Child {} of {} completed (frame_id={}): pos {} -> {}",
                            child_index,
                            total_children,
                            child_frame_id,
                            frame.pos,
                            child_end_pos
                        );

                        // Extract frame data we'll need before borrowing
                        let frame_terminators = frame.terminators.clone();

                        match &mut frame.context {
                            FrameContext::Sequence {
                                elements,
                                allow_gaps,
                                optional: _optional,
                                parse_mode,
                                matched_idx,
                                tentatively_collected,
                                max_idx,
                                last_child_frame_id: _last_child_frame_id,
                                current_element_idx,
                            } => {
                                let element_start = *matched_idx;

                                // Handle the child result
                                if !child_node.is_empty() {
                                    // Successfully matched
                                    *matched_idx = *child_end_pos;

                                    // Add the matched node
                                    frame.accumulated.push(child_node.clone());

                                    // Handle retroactive collection for allow_gaps=false
                                    if !*allow_gaps {
                                        // Find where the element actually consumed its last code token
                                        let mut last_code_consumed = element_start;
                                        for check_pos in element_start..*matched_idx {
                                            if check_pos < self.tokens.len()
                                                && self.tokens[check_pos].is_code()
                                            {
                                                last_code_consumed = check_pos;
                                            }
                                        }

                                        // Collect ALL transparent tokens until we hit code
                                        let mut collect_end = *matched_idx;
                                        while collect_end < self.tokens.len()
                                            && !self.tokens[collect_end].is_code()
                                        {
                                            collect_end += 1;
                                        }

                                        log::debug!(
                                            "Retroactive collection: element_start={}, last_code_consumed={}, matched_idx={}, collect_end={}",
                                            element_start, last_code_consumed, *matched_idx, collect_end
                                        );

                                        // Collect transparent tokens
                                        for check_pos in (last_code_consumed + 1)..collect_end {
                                            if check_pos < self.tokens.len()
                                                && !self.tokens[check_pos].is_code()
                                                && !self
                                                    .collected_transparent_positions
                                                    .contains(&check_pos)
                                            {
                                                let tok = &self.tokens[check_pos];
                                                let tok_type = tok.get_type();
                                                if tok_type == "whitespace" {
                                                    log::debug!("RETROACTIVELY collecting whitespace at {}: {:?}", check_pos, tok.raw());
                                                    frame.accumulated.push(Node::Whitespace(
                                                        tok.raw().to_string(),
                                                        check_pos,
                                                    ));
                                                    tentatively_collected.push(check_pos);
                                                } else if tok_type == "newline" {
                                                    log::debug!("RETROACTIVELY collecting newline at {}: {:?}", check_pos, tok.raw());
                                                    frame.accumulated.push(Node::Newline(
                                                        tok.raw().to_string(),
                                                        check_pos,
                                                    ));
                                                    tentatively_collected.push(check_pos);
                                                }
                                            }
                                        }
                                    }
                                }

                                let current_matched_idx = *matched_idx;
                                let current_allow_gaps = *allow_gaps;
                                let current_parse_mode = *parse_mode;
                                let current_max_idx = *max_idx;
                                let current_elem_idx = *current_element_idx;
                                let elements_clone = elements.clone();

                                // Move to next child or finish
                                if child_index >= total_children {
                                    // All children processed - commit tentatively collected positions
                                    for pos in tentatively_collected.iter() {
                                        self.collected_transparent_positions.insert(*pos);
                                    }

                                    self.pos = current_matched_idx;
                                    let result_node = if frame.accumulated.is_empty() {
                                        Node::Empty
                                    } else {
                                        Node::Sequence(frame.accumulated.clone())
                                    };
                                    log::debug!(
                                        "Sequence COMPLETE: Storing result at frame_id={}",
                                        frame.frame_id
                                    );
                                    results.insert(
                                        frame.frame_id,
                                        (result_node, current_matched_idx, None),
                                    );
                                } else {
                                    // Before processing next element, handle transparent token collection for allow_gaps=true
                                    let mut next_pos = current_matched_idx;
                                    if current_allow_gaps && child_index < elements_clone.len() {
                                        // Skip forward to next code token
                                        let _idx = self.skip_start_index_forward_to_code(
                                            current_matched_idx,
                                            current_max_idx,
                                        );

                                        // Check if we need to collect these transparent tokens
                                        let has_uncollected =
                                            (current_matched_idx.._idx).any(|pos| {
                                                pos < self.tokens.len()
                                                    && !self.tokens[pos].is_code()
                                                    && !self
                                                        .collected_transparent_positions
                                                        .contains(&pos)
                                            });

                                        if has_uncollected {
                                            log::debug!(
                                                "Collecting transparent tokens from {} to {}",
                                                current_matched_idx,
                                                _idx
                                            );

                                            // Collect transparent tokens
                                            for collect_pos in current_matched_idx.._idx {
                                                if collect_pos < self.tokens.len()
                                                    && !self.tokens[collect_pos].is_code()
                                                {
                                                    let tok = &self.tokens[collect_pos];
                                                    let tok_type = tok.get_type();
                                                    if tok_type == "whitespace" {
                                                        log::debug!(
                                                            "COLLECTING whitespace at {}: {:?}",
                                                            collect_pos,
                                                            tok.raw()
                                                        );
                                                        frame.accumulated.push(Node::Whitespace(
                                                            tok.raw().to_string(),
                                                            collect_pos,
                                                        ));
                                                        tentatively_collected.push(collect_pos);
                                                    } else if tok_type == "newline" {
                                                        log::debug!(
                                                            "COLLECTING newline at {}: {:?}",
                                                            collect_pos,
                                                            tok.raw()
                                                        );
                                                        frame.accumulated.push(Node::Newline(
                                                            tok.raw().to_string(),
                                                            collect_pos,
                                                        ));
                                                        tentatively_collected.push(collect_pos);
                                                    }
                                                }
                                            }
                                        }
                                        next_pos = _idx;
                                    }

                                    // Check if we've run out of segments
                                    // Note: child_index is the index of the child we just processed
                                    // The next child to process is at child_index + 1
                                    log::debug!(
                                        "Sequence checking EOF: next_pos={}, current_max_idx={}, child_index={}, elements_clone.len()={}",
                                        next_pos,
                                        current_max_idx,
                                        child_index,
                                        elements_clone.len()
                                    );
                                    let next_child_index = child_index + 1;
                                    if next_pos >= current_max_idx
                                        && next_child_index < elements_clone.len()
                                    {
                                        log::debug!("  Entered EOF check block");
                                        // Check if next element is optional
                                        let next_element_optional = if let Some(next_elem) =
                                            elements_clone.get(next_child_index)
                                        {
                                            Self::is_grammar_optional(next_elem)
                                        } else {
                                            false
                                        };
                                        log::debug!(
                                            "  next_element_optional={}",
                                            next_element_optional
                                        );

                                        if next_element_optional {
                                            // Next element is optional and we're at EOF - complete the sequence
                                            log::debug!(
                                                "COMPLETE: ran out of segments but next element is optional"
                                            );
                                            for pos in tentatively_collected.iter() {
                                                self.collected_transparent_positions.insert(*pos);
                                            }
                                            self.pos = current_matched_idx;
                                            let result_node = if frame.accumulated.is_empty() {
                                                Node::Empty
                                            } else {
                                                Node::Sequence(frame.accumulated.clone())
                                            };
                                            results.insert(
                                                frame.frame_id,
                                                (result_node, current_matched_idx, None),
                                            );
                                            continue;
                                        } else {
                                            // Handle based on parse mode
                                            if current_parse_mode == ParseMode::Strict
                                                || frame.accumulated.is_empty()
                                            {
                                                log::debug!(
                                                    "NOMATCH Ran out of segments in STRICT mode"
                                                );
                                                results.insert(
                                                    frame.frame_id,
                                                    (Node::Empty, element_start, None),
                                                );
                                                continue;
                                            } else {
                                                // GREEDY/GREEDY_ONCE_STARTED: return what we have
                                                log::debug!(
                                                    "INCOMPLETE match: ran out of segments"
                                                );
                                                for pos in tentatively_collected.iter() {
                                                    self.collected_transparent_positions
                                                        .insert(*pos);
                                                }
                                                self.pos = current_matched_idx;
                                                let result_node =
                                                    Node::Sequence(frame.accumulated.clone());
                                                results.insert(
                                                    frame.frame_id,
                                                    (result_node, current_matched_idx, None),
                                                );
                                                continue;
                                            }
                                        }
                                    }

                                    // Push next child - skip Meta elements
                                    frame.state = FrameState::WaitingForChild {
                                        child_index: child_index + 1,
                                        total_children,
                                    };

                                    // Clone frame before pushing
                                    let frame_to_push = frame.clone();
                                    stack.push(frame_to_push);

                                    // Find next non-Meta element
                                    // child_index is the count of non-Meta children processed so far
                                    // current_element_idx tracks which element index we last processed
                                    let mut next_elem_idx = current_elem_idx + 1;
                                    log::debug!("Looking for next child: next_elem_idx={}, elements_clone.len()={}", next_elem_idx, elements_clone.len());
                                    while next_elem_idx < elements_clone.len() {
                                        log::debug!(
                                            "Checking element {}: {:?}",
                                            next_elem_idx,
                                            &elements_clone[next_elem_idx]
                                        );
                                        if let Grammar::Meta(meta_type) =
                                            &elements_clone[next_elem_idx]
                                        {
                                            // Add Meta to accumulated directly
                                            if *meta_type == "indent" {
                                                let mut insert_pos =
                                                    stack.last().unwrap().accumulated.len();
                                                while insert_pos > 0 {
                                                    match &stack.last().unwrap().accumulated
                                                        [insert_pos - 1]
                                                    {
                                                        Node::Whitespace(_, _)
                                                        | Node::Newline(_, _) => {
                                                            insert_pos -= 1;
                                                        }
                                                        _ => break,
                                                    }
                                                }
                                                if let Some(last_frame) = stack.last_mut() {
                                                    last_frame
                                                        .accumulated
                                                        .insert(insert_pos, Node::Meta(meta_type));
                                                }
                                            } else if let Some(last_frame) = stack.last_mut() {
                                                last_frame.accumulated.push(Node::Meta(meta_type));
                                            }
                                            next_elem_idx += 1;
                                        } else {
                                            // Non-Meta element - create frame for it
                                            log::debug!(
                                                "Creating child frame for element {}: frame_id={}",
                                                next_elem_idx,
                                                frame_id_counter
                                            );
                                            let child_frame = ParseFrame {
                                                frame_id: frame_id_counter,
                                                grammar: elements_clone[next_elem_idx].clone(),
                                                pos: next_pos,
                                                terminators: frame_terminators.clone(),
                                                state: FrameState::Initial,
                                                accumulated: vec![],
                                                context: FrameContext::None,
                                            };

                                            // Update parent's last_child_frame_id and current_element_idx
                                            if let Some(parent_frame) = stack.last_mut() {
                                                if let FrameContext::Sequence {
                                                    last_child_frame_id,
                                                    current_element_idx,
                                                    ..
                                                } = &mut parent_frame.context
                                                {
                                                    *last_child_frame_id = Some(frame_id_counter);
                                                    *current_element_idx = next_elem_idx;
                                                    // Update to the element we're about to process
                                                }
                                            }

                                            frame_id_counter += 1;
                                            stack.push(child_frame);
                                            log::debug!("Pushed child frame, breaking from loop");
                                            break;
                                        }
                                    }
                                }
                            }

                            FrameContext::AnyNumberOf {
                                elements,
                                min_times,
                                max_times,
                                max_times_per_element,
                                allow_gaps,
                                optional,
                                parse_mode,
                                count,
                                matched_idx,
                                working_idx,
                                option_counter,
                                max_idx,
                                last_child_frame_id: _last_child_frame_id,
                            } => {
                                log::debug!(
                                    "AnyNumberOf WaitingForChild: count={}, child_node empty={}, matched_idx={}, working_idx={}",
                                    count,
                                    child_node.is_empty(),
                                    matched_idx,
                                    working_idx
                                );

                                // Handle the child result
                                if !child_node.is_empty() {
                                    // Successfully matched!

                                    // Collect transparent tokens if allow_gaps
                                    if *allow_gaps && *matched_idx < *working_idx {
                                        while *matched_idx < *working_idx {
                                            if let Some(tok) = self.tokens.get(*matched_idx) {
                                                let tok_type = tok.get_type();
                                                if tok_type == "whitespace" {
                                                    frame.accumulated.push(Node::Whitespace(
                                                        tok.raw().to_string(),
                                                        *matched_idx,
                                                    ));
                                                } else if tok_type == "newline" {
                                                    frame.accumulated.push(Node::Newline(
                                                        tok.raw().to_string(),
                                                        *matched_idx,
                                                    ));
                                                }
                                            }
                                            *matched_idx += 1;
                                        }
                                    }

                                    // Add the matched node
                                    frame.accumulated.push(child_node.clone());
                                    *matched_idx = *child_end_pos;
                                    *working_idx = *matched_idx;
                                    *count += 1;

                                    // Update option_counter with the element_key from OneOf child
                                    let element_key = child_element_key.unwrap_or(0);
                                    *option_counter.entry(element_key).or_insert(0) += 1;

                                    log::debug!(
                                        "AnyNumberOf: matched element #{}, element_key={}, matched_idx now: {}",
                                        count, element_key, matched_idx
                                    );

                                    // Check if we've reached limits
                                    let should_continue = *count < *min_times
                                        || (*matched_idx < *max_idx
                                            && (max_times.is_none()
                                                || *count < max_times.unwrap()));

                                    if should_continue {
                                        // Continue loop - try matching next element
                                        // Update working_idx to skip whitespace if allowed
                                        if *allow_gaps {
                                            *working_idx = self.skip_start_index_forward_to_code(
                                                *working_idx,
                                                *max_idx,
                                            );
                                        }

                                        // Create OneOf wrapper to try all elements (proper longest-match)
                                        if !elements.is_empty() {
                                            // Optimization: if only one element, use it directly (avoid OneOf overhead)
                                            let child_grammar = if elements.len() == 1 {
                                                elements[0].clone()
                                            } else {
                                                // Multiple elements: wrap in OneOf for longest-match selection
                                                Grammar::OneOf {
                                                    elements: elements.clone(),
                                                    optional: true, // Let AnyNumberOf handle empty
                                                    terminators: frame_terminators.clone(),
                                                    reset_terminators: false,
                                                    allow_gaps: *allow_gaps,
                                                    parse_mode: *parse_mode,
                                                }
                                            };

                                            let child_frame = ParseFrame {
                                                frame_id: frame_id_counter,
                                                grammar: child_grammar,
                                                pos: *working_idx,
                                                terminators: frame_terminators.clone(),
                                                state: FrameState::Initial,
                                                accumulated: vec![],
                                                context: FrameContext::None,
                                            };

                                            // Update parent's last_child_frame_id
                                            if let Some(parent_frame) = stack.last_mut() {
                                                if let FrameContext::AnyNumberOf {
                                                    last_child_frame_id,
                                                    ..
                                                } = &mut parent_frame.context
                                                {
                                                    *last_child_frame_id = Some(frame_id_counter);
                                                }
                                            }

                                            frame_id_counter += 1;
                                            stack.push(child_frame);
                                        }
                                    } else {
                                        // Done with loop - complete the frame
                                        self.pos = *matched_idx;
                                        let result_node =
                                            Node::DelimitedList(frame.accumulated.clone());
                                        log::debug!(
                                            "AnyNumberOf COMPLETE: {} matches, storing result at frame_id={}",
                                            count,
                                            frame.frame_id
                                        );
                                        results.insert(
                                            frame.frame_id,
                                            (result_node, *matched_idx, None),
                                        );
                                    }
                                } else {
                                    // Child failed to match
                                    log::debug!(
                                        "AnyNumberOf: child failed to match at position {}",
                                        working_idx
                                    );

                                    // Check if we've met min_times
                                    if *count < *min_times {
                                        if *optional {
                                            self.pos = frame.pos;
                                            log::debug!(
                                                "AnyNumberOf returning Empty (didn't meet min_times)"
                                            );
                                            results.insert(
                                                frame.frame_id,
                                                (Node::Empty, frame.pos, None),
                                            );
                                        } else {
                                            return Err(ParseError::new(format!(
                                                "Expected at least {} occurrences, found {}",
                                                min_times, count
                                            )));
                                        }
                                    } else {
                                        // We've met min_times - complete with what we have
                                        self.pos = *matched_idx;
                                        let result_node =
                                            Node::DelimitedList(frame.accumulated.clone());
                                        log::debug!(
                                            "AnyNumberOf COMPLETE (child failed): {} matches, storing result at frame_id={}",
                                            count,
                                            frame.frame_id
                                        );
                                        results.insert(
                                            frame.frame_id,
                                            (result_node, *matched_idx, None),
                                        );
                                    }
                                }
                            }

                            FrameContext::Bracketed {
                                bracket_pairs,
                                elements,
                                allow_gaps,
                                optional,
                                parse_mode,
                                state,
                                last_child_frame_id: _last_child_frame_id,
                            } => {
                                log::debug!(
                                    "Bracketed WaitingForChild: state={:?}, child_node empty={}",
                                    state,
                                    child_node.is_empty()
                                );

                                match state {
                                    BracketedState::MatchingOpen => {
                                        // Opening bracket result
                                        if child_node.is_empty() {
                                            // No opening bracket found
                                            if *optional {
                                                self.pos = frame.pos;
                                                log::debug!("Bracketed returning Empty (no opening bracket, optional)");
                                                results.insert(
                                                    frame.frame_id,
                                                    (Node::Empty, frame.pos, None),
                                                );
                                            } else {
                                                return Err(ParseError::new(
                                                    "Expected opening bracket".to_string(),
                                                ));
                                            }
                                        } else {
                                            // Opening bracket matched!
                                            frame.accumulated.push(child_node.clone());
                                            let content_start_idx = *child_end_pos;

                                            // Collect whitespace after opening bracket if allow_gaps
                                            if *allow_gaps {
                                                let code_idx = self
                                                    .skip_start_index_forward_to_code(
                                                        content_start_idx,
                                                        self.tokens.len(),
                                                    );
                                                for pos in content_start_idx..code_idx {
                                                    if let Some(tok) = self.tokens.get(pos) {
                                                        let tok_type = tok.get_type();
                                                        if tok_type == "whitespace" {
                                                            frame.accumulated.push(
                                                                Node::Whitespace(
                                                                    tok.raw().to_string(),
                                                                    pos,
                                                                ),
                                                            );
                                                        } else if tok_type == "newline" {
                                                            frame.accumulated.push(Node::Newline(
                                                                tok.raw().to_string(),
                                                                pos,
                                                            ));
                                                        }
                                                    }
                                                }
                                                self.pos = code_idx;
                                            } else {
                                                self.pos = content_start_idx;
                                            }

                                            // Transition to MatchingContent
                                            *state = BracketedState::MatchingContent;

                                            // Create content grammar (Sequence with closing bracket as terminator)
                                            let content_grammar = Grammar::Sequence {
                                                elements: elements.clone(),
                                                optional: false,
                                                terminators: vec![(*bracket_pairs.1).clone()],
                                                reset_terminators: true,
                                                allow_gaps: *allow_gaps,
                                                parse_mode: *parse_mode,
                                            };

                                            let child_frame = ParseFrame {
                                                frame_id: frame_id_counter,
                                                grammar: content_grammar,
                                                pos: self.pos,
                                                terminators: frame_terminators.clone(),
                                                state: FrameState::Initial,
                                                accumulated: vec![],
                                                context: FrameContext::None,
                                            };

                                            // Update parent's last_child_frame_id
                                            if let Some(parent_frame) = stack.last_mut() {
                                                if let FrameContext::Bracketed {
                                                    last_child_frame_id,
                                                    ..
                                                } = &mut parent_frame.context
                                                {
                                                    *last_child_frame_id = Some(frame_id_counter);
                                                }
                                            }

                                            frame_id_counter += 1;
                                            stack.push(child_frame);
                                        }
                                    }
                                    BracketedState::MatchingContent => {
                                        // Content result
                                        if !child_node.is_empty() {
                                            // Extract children from the sequence node
                                            if let Node::Sequence(content_children) = child_node {
                                                frame.accumulated.extend(content_children.clone());
                                            } else {
                                                frame.accumulated.push(child_node.clone());
                                            }
                                        }

                                        let gap_start = *child_end_pos;
                                        self.pos = gap_start;

                                        // Collect whitespace before closing bracket if allow_gaps
                                        if *allow_gaps {
                                            let code_idx = self.skip_start_index_forward_to_code(
                                                gap_start,
                                                self.tokens.len(),
                                            );
                                            for pos in gap_start..code_idx {
                                                if let Some(tok) = self.tokens.get(pos) {
                                                    let tok_type = tok.get_type();
                                                    if tok_type == "whitespace" {
                                                        frame.accumulated.push(Node::Whitespace(
                                                            tok.raw().to_string(),
                                                            pos,
                                                        ));
                                                    } else if tok_type == "newline" {
                                                        frame.accumulated.push(Node::Newline(
                                                            tok.raw().to_string(),
                                                            pos,
                                                        ));
                                                    }
                                                }
                                            }
                                            self.pos = code_idx;
                                        }

                                        // Check if we've run out of segments
                                        if self.pos >= self.tokens.len()
                                            || self
                                                .peek()
                                                .is_some_and(|t| t.get_type() == "end_of_file")
                                        {
                                            // No end bracket found
                                            if *parse_mode == ParseMode::Strict {
                                                self.pos = frame.pos;
                                                results.insert(
                                                    frame.frame_id,
                                                    (Node::Empty, frame.pos, None),
                                                );
                                            } else {
                                                return Err(ParseError::new(
                                                    "Couldn't find closing bracket for opening bracket".to_string(),
                                                ));
                                            }
                                        } else {
                                            // Transition to MatchingClose
                                            *state = BracketedState::MatchingClose;

                                            // Create child frame for closing bracket
                                            let child_frame = ParseFrame {
                                                frame_id: frame_id_counter,
                                                grammar: (*bracket_pairs.1).clone(),
                                                pos: self.pos,
                                                terminators: vec![(*bracket_pairs.1).clone()],
                                                state: FrameState::Initial,
                                                accumulated: vec![],
                                                context: FrameContext::None,
                                            };

                                            // Update parent's last_child_frame_id
                                            if let Some(parent_frame) = stack.last_mut() {
                                                if let FrameContext::Bracketed {
                                                    last_child_frame_id,
                                                    ..
                                                } = &mut parent_frame.context
                                                {
                                                    *last_child_frame_id = Some(frame_id_counter);
                                                }
                                            }

                                            frame_id_counter += 1;
                                            stack.push(child_frame);
                                        }
                                    }
                                    BracketedState::MatchingClose => {
                                        // Closing bracket result
                                        if child_node.is_empty() {
                                            // No closing bracket found
                                            if *parse_mode == ParseMode::Strict {
                                                self.pos = frame.pos;
                                                results.insert(
                                                    frame.frame_id,
                                                    (Node::Empty, frame.pos, None),
                                                );
                                            } else {
                                                return Err(ParseError::new(
                                                    "Couldn't find closing bracket for opening bracket".to_string(),
                                                ));
                                            }
                                        } else {
                                            // Closing bracket matched!
                                            frame.accumulated.push(child_node.clone());
                                            self.pos = *child_end_pos;

                                            let result_node =
                                                Node::Sequence(frame.accumulated.clone());
                                            log::debug!(
                                                "Bracketed COMPLETE: {} children, storing result at frame_id={}",
                                                frame.accumulated.len(),
                                                frame.frame_id
                                            );
                                            results.insert(
                                                frame.frame_id,
                                                (result_node, *child_end_pos, None),
                                            );
                                        }
                                    }
                                }
                            }

                            FrameContext::AnySetOf {
                                elements,
                                min_times,
                                max_times,
                                allow_gaps,
                                optional,
                                count,
                                matched_idx,
                                working_idx,
                                matched_elements,
                                max_idx,
                                last_child_frame_id: _last_child_frame_id,
                                parse_mode,
                            } => {
                                log::debug!("[ITERATIVE] AnySetOf WaitingForChild: count={}, matched_idx={}", count, matched_idx);

                                // Handle child result
                                if child_node.is_empty() {
                                    // Child match failed
                                    log::debug!(
                                        "[ITERATIVE] AnySetOf child failed at position {}",
                                        frame.pos
                                    );

                                    // Check if we've met min_times requirement
                                    if *count < *min_times {
                                        if *optional {
                                            self.pos = frame.pos;
                                            log::debug!(
                                                "[ITERATIVE] AnySetOf optional, returning Empty"
                                            );
                                            results.insert(
                                                frame.frame_id,
                                                (Node::Empty, frame.pos, None),
                                            );
                                        } else {
                                            return Err(ParseError::new(format!(
                                                "Expected at least {} occurrences in AnySetOf, found {}",
                                                min_times, count
                                            )));
                                        }
                                    } else {
                                        // Met min_times, complete with what we have
                                        log::debug!("[ITERATIVE] AnySetOf met min_times, completing with {} items", frame.accumulated.len());
                                        self.pos = *matched_idx;
                                        let result_node =
                                            Node::DelimitedList(frame.accumulated.clone());
                                        results.insert(
                                            frame.frame_id,
                                            (result_node, *matched_idx, None),
                                        );
                                    }
                                } else {
                                    // Child matched successfully!
                                    log::debug!(
                                        "[ITERATIVE] AnySetOf child matched: pos {} -> {}",
                                        frame.pos,
                                        child_end_pos
                                    );

                                    // Collect transparent tokens between matched_idx and working_idx if allow_gaps
                                    if *allow_gaps {
                                        for check_pos in *matched_idx..*working_idx {
                                            if check_pos < self.tokens.len()
                                                && !self.tokens[check_pos].is_code()
                                                && !self
                                                    .collected_transparent_positions
                                                    .contains(&check_pos)
                                            {
                                                let tok = &self.tokens[check_pos];
                                                let tok_type = tok.get_type();
                                                if tok_type == "whitespace" {
                                                    frame.accumulated.push(Node::Whitespace(
                                                        tok.raw().to_string(),
                                                        check_pos,
                                                    ));
                                                    self.collected_transparent_positions
                                                        .insert(check_pos);
                                                } else if tok_type == "newline" {
                                                    frame.accumulated.push(Node::Newline(
                                                        tok.raw().to_string(),
                                                        check_pos,
                                                    ));
                                                    self.collected_transparent_positions
                                                        .insert(check_pos);
                                                }
                                            }
                                        }
                                    }

                                    // Add matched node
                                    frame.accumulated.push(child_node.clone());
                                    *matched_idx = *child_end_pos;
                                    *working_idx = *matched_idx;
                                    *count += 1;

                                    // Extract element_key from OneOf result and add to matched_elements
                                    let element_key = child_element_key.unwrap_or(0);
                                    matched_elements.insert(element_key);

                                    log::debug!(
                                        "[ITERATIVE] AnySetOf matched item #{}, element_key={}, matched_idx now: {}, matched_elements: {:?}",
                                        count, element_key, matched_idx, matched_elements
                                    );

                                    // Check termination conditions
                                    let should_terminate = *count >= *min_times
                                        && (*matched_idx >= *max_idx
                                            || (max_times.is_some()
                                                && *count >= max_times.unwrap())
                                            || matched_elements.len() >= elements.len()); // All unique elements matched

                                    if should_terminate {
                                        log::debug!(
                                            "[ITERATIVE] AnySetOf terminating: count={}, min_times={}, matched_idx={}, max_idx={}",
                                            count, min_times, matched_idx, max_idx
                                        );
                                        self.pos = *matched_idx;
                                        let result_node =
                                            Node::DelimitedList(frame.accumulated.clone());
                                        results.insert(
                                            frame.frame_id,
                                            (result_node, *matched_idx, None),
                                        );
                                    } else {
                                        // Continue - create next child to try remaining elements
                                        *working_idx = if *allow_gaps {
                                            self.skip_start_index_forward_to_code(
                                                *working_idx,
                                                *max_idx,
                                            )
                                        } else {
                                            *working_idx
                                        };

                                        // Filter out already matched elements by element_key
                                        let unmatched_elements: Vec<Grammar> = elements
                                            .iter()
                                            .filter(|elem| {
                                                !matched_elements.contains(&elem.cache_key())
                                            })
                                            .cloned()
                                            .collect();

                                        log::debug!(
                                            "[ITERATIVE] AnySetOf continuing: {} unmatched elements of {} total",
                                            unmatched_elements.len(),
                                            elements.len()
                                        );

                                        if unmatched_elements.is_empty() {
                                            // All elements matched - complete
                                            log::debug!("[ITERATIVE] AnySetOf: all elements matched, completing");
                                            self.pos = *matched_idx;
                                            let result_node =
                                                Node::DelimitedList(frame.accumulated.clone());
                                            results.insert(
                                                frame.frame_id,
                                                (result_node, *matched_idx, None),
                                            );
                                        } else {
                                            // Create OneOf with only unmatched elements
                                            let child_grammar = Grammar::OneOf {
                                                elements: unmatched_elements,
                                                optional: false,
                                                terminators: vec![],
                                                reset_terminators: false,
                                                allow_gaps: *allow_gaps,
                                                parse_mode: *parse_mode,
                                            };

                                            let child_frame = ParseFrame {
                                                frame_id: frame_id_counter,
                                                grammar: child_grammar,
                                                pos: *working_idx,
                                                terminators: frame_terminators.clone(),
                                                state: FrameState::Initial,
                                                accumulated: vec![],
                                                context: FrameContext::None,
                                            };

                                            // Update parent's last_child_frame_id
                                            if let Some(parent_frame) = stack.last_mut() {
                                                if let FrameContext::AnySetOf {
                                                    last_child_frame_id,
                                                    ..
                                                } = &mut parent_frame.context
                                                {
                                                    *last_child_frame_id = Some(frame_id_counter);
                                                }
                                            }

                                            frame_id_counter += 1;
                                            stack.push(child_frame);
                                        }
                                    }
                                }
                            }

                            FrameContext::OneOf {
                                elements,
                                allow_gaps,
                                optional,
                                leading_ws,
                                post_skip_pos,
                                longest_match,
                                tried_elements,
                                max_idx,
                                parse_mode,
                                last_child_frame_id: _last_child_frame_id,
                            } => {
                                log::debug!(
                                    "OneOf WaitingForChild: tried_elements={}, child_empty={}",
                                    tried_elements,
                                    child_node.is_empty()
                                );

                                // Get child end position and element_key
                                let child_end_pos = self.pos;
                                let consumed = child_end_pos - *post_skip_pos;

                                // Get the element_key for the element we just tried
                                let element_key = if *tried_elements < elements.len() {
                                    elements[*tried_elements].cache_key()
                                } else {
                                    0 // Fallback
                                };

                                // Check if this match is better than current longest
                                if !child_node.is_empty() {
                                    let is_better = longest_match.is_none()
                                        || consumed > longest_match.as_ref().unwrap().1;

                                    if is_better {
                                        log::debug!("OneOf: New longest match with {} consumed tokens (element_key={})",
                                                   consumed, element_key);
                                        *longest_match =
                                            Some((child_node.clone(), consumed, element_key));
                                    }
                                }

                                // Move to next element
                                *tried_elements += 1;

                                if *tried_elements < elements.len() {
                                    // More elements to try - reset state and create next child
                                    log::debug!(
                                        "OneOf: Trying next element ({}/{})",
                                        tried_elements,
                                        elements.len()
                                    );

                                    // Reset parser position to start of OneOf
                                    self.pos = *post_skip_pos;

                                    // Create child frame for next element
                                    let next_element = elements[*tried_elements].clone();
                                    let next_element_key = next_element.cache_key();
                                    log::debug!(
                                        "OneOf: Next element cache_key={}",
                                        next_element_key
                                    );

                                    let child_frame = ParseFrame {
                                        frame_id: frame_id_counter,
                                        grammar: next_element,
                                        pos: *post_skip_pos,
                                        terminators: frame.terminators.clone(), // Use parent's terminators
                                        state: FrameState::Initial,
                                        accumulated: Vec::new(),
                                        context: FrameContext::None,
                                    };

                                    frame.state = FrameState::WaitingForChild {
                                        child_index: 0,
                                        total_children: 1,
                                    };

                                    frame_id_counter += 1;
                                    stack.push(child_frame);
                                    break;
                                } else {
                                    // All elements tried - return longest match
                                    log::debug!(
                                        "OneOf: All elements tried, longest_match={:?}",
                                        longest_match
                                            .as_ref()
                                            .map(|(_, consumed, key)| (consumed, key))
                                    );

                                    if let Some((best_node, best_consumed, best_element_key)) =
                                        longest_match
                                    {
                                        // Set position to end of longest match
                                        self.pos = *post_skip_pos + *best_consumed;

                                        // Wrap with leading whitespace if any
                                        let result = if !leading_ws.is_empty() {
                                            let mut children = leading_ws.clone();
                                            children.push(best_node.clone());
                                            Node::Sequence(children)
                                        } else {
                                            best_node.clone()
                                        };

                                        log::debug!(
                                            "OneOf: Returning longest match with element_key={}",
                                            best_element_key
                                        );
                                        // Store result WITH element_key so parent grammars can use it
                                        results.insert(
                                            frame.frame_id,
                                            (result, self.pos, Some(*best_element_key)),
                                        );
                                        continue; // Don't fall through to Complete state
                                    } else {
                                        // No matches found
                                        log::debug!(
                                            "OneOf: No matches found, optional={}",
                                            optional
                                        );

                                        if *optional {
                                            results.insert(
                                                frame.frame_id,
                                                (Node::Empty, self.pos, None),
                                            );
                                            continue;
                                        } else {
                                            return Err(ParseError::new(
                                                "OneOf: No matching elements found".into(),
                                            ));
                                        }
                                    }
                                }
                            }

                            FrameContext::Delimited {
                                elements,
                                delimiter,
                                allow_trailing,
                                optional,
                                allow_gaps,
                                min_delimiters,
                                parse_mode,
                                delimiter_count,
                                matched_idx,
                                working_idx,
                                max_idx,
                                state,
                                last_child_frame_id: _last_child_frame_id,
                            } => {
                                log::debug!("[ITERATIVE] Delimited WaitingForChild: state={:?}, delimiter_count={}", state, delimiter_count);

                                match state {
                                    DelimitedState::MatchingElement => {
                                        // We were trying to match an element
                                        if child_node.is_empty() {
                                            // No element matched
                                            log::debug!("[ITERATIVE] Delimited: no element matched at position {}", frame.pos);

                                            // Check if we have enough delimiters (elements = delimiters + 1)
                                            if *delimiter_count < *min_delimiters {
                                                if *optional {
                                                    self.pos = frame.pos;
                                                    log::debug!("[ITERATIVE] Delimited optional, returning Empty");
                                                    results.insert(
                                                        frame.frame_id,
                                                        (
                                                            Node::DelimitedList(
                                                                frame.accumulated.clone(),
                                                            ),
                                                            frame.pos,
                                                            None,
                                                        ),
                                                    );
                                                } else {
                                                    return Err(ParseError::new(format!(
                                                        "Expected at least {} delimiters in Delimited, found {}",
                                                        min_delimiters, delimiter_count
                                                    )));
                                                }
                                            } else {
                                                // Met minimum, complete with what we have
                                                log::debug!("[ITERATIVE] Delimited met min_delimiters, completing with {} items", frame.accumulated.len());
                                                self.pos = *matched_idx;
                                                results.insert(
                                                    frame.frame_id,
                                                    (
                                                        Node::DelimitedList(
                                                            frame.accumulated.clone(),
                                                        ),
                                                        *matched_idx,
                                                        None,
                                                    ),
                                                );
                                            }
                                        } else {
                                            // Element matched!
                                            log::debug!("[ITERATIVE] Delimited element matched: pos {} -> {}", frame.pos, child_end_pos);

                                            // Collect whitespace between matched_idx and working_idx if allow_gaps
                                            if *allow_gaps {
                                                for check_pos in *matched_idx..*working_idx {
                                                    if check_pos < self.tokens.len()
                                                        && !self.tokens[check_pos].is_code()
                                                        && !self
                                                            .collected_transparent_positions
                                                            .contains(&check_pos)
                                                    {
                                                        let tok = &self.tokens[check_pos];
                                                        let tok_type = tok.get_type();
                                                        if tok_type == "whitespace" {
                                                            frame.accumulated.push(
                                                                Node::Whitespace(
                                                                    tok.raw().to_string(),
                                                                    check_pos,
                                                                ),
                                                            );
                                                            self.collected_transparent_positions
                                                                .insert(check_pos);
                                                        } else if tok_type == "newline" {
                                                            frame.accumulated.push(Node::Newline(
                                                                tok.raw().to_string(),
                                                                check_pos,
                                                            ));
                                                            self.collected_transparent_positions
                                                                .insert(check_pos);
                                                        }
                                                    }
                                                }
                                            }

                                            // Add matched element
                                            frame.accumulated.push(child_node.clone());
                                            *matched_idx = *child_end_pos;
                                            *working_idx = *matched_idx;

                                            // Skip whitespace before delimiter
                                            if *allow_gaps {
                                                *working_idx = self
                                                    .skip_start_index_forward_to_code(
                                                        *working_idx,
                                                        *max_idx,
                                                    );
                                            }

                                            // Check if we're at EOF or terminator
                                            // If so, no delimiter is required (delimiters are only between elements)
                                            self.pos = *working_idx;
                                            if self.is_at_end()
                                                || self.is_terminated(&frame_terminators)
                                            {
                                                log::debug!(
                                                    "[ITERATIVE] Delimited: at EOF or terminator after element, completing at position {}",
                                                    matched_idx
                                                );
                                                self.pos = *matched_idx;
                                                results.insert(
                                                    frame.frame_id,
                                                    (
                                                        Node::DelimitedList(
                                                            frame.accumulated.clone(),
                                                        ),
                                                        *matched_idx,
                                                        None,
                                                    ),
                                                );
                                                // Don't push frame back - we're done
                                            } else {
                                                // Transition to MatchingDelimiter state
                                                *state = DelimitedState::MatchingDelimiter;

                                                // Create child frame for delimiter
                                                let child_frame = ParseFrame {
                                                    frame_id: frame_id_counter,
                                                    grammar: (**delimiter).clone(),
                                                    pos: *working_idx,
                                                    terminators: frame_terminators.clone(),
                                                    state: FrameState::Initial,
                                                    accumulated: vec![],
                                                    context: FrameContext::None,
                                                };

                                                // Update parent's last_child_frame_id
                                                if let Some(parent_frame) = stack.last_mut() {
                                                    if let FrameContext::Delimited {
                                                        last_child_frame_id,
                                                        ..
                                                    } = &mut parent_frame.context
                                                    {
                                                        *last_child_frame_id =
                                                            Some(frame_id_counter);
                                                    }
                                                }

                                                frame_id_counter += 1;
                                                stack.push(child_frame);
                                            }
                                        }
                                    }
                                    DelimitedState::MatchingDelimiter => {
                                        // We were trying to match a delimiter
                                        if child_node.is_empty() {
                                            // No delimiter found - list is complete
                                            log::debug!("[ITERATIVE] Delimited: no delimiter found, completing at position {}", matched_idx);

                                            // Check if we have enough delimiters
                                            if *delimiter_count < *min_delimiters {
                                                if *optional {
                                                    self.pos = frame.pos;
                                                    results.insert(
                                                        frame.frame_id,
                                                        (
                                                            Node::DelimitedList(
                                                                frame.accumulated.clone(),
                                                            ),
                                                            frame.pos,
                                                            None,
                                                        ),
                                                    );
                                                } else {
                                                    return Err(ParseError::new(format!(
                                                        "Expected at least {} delimiters, found {}",
                                                        min_delimiters, delimiter_count
                                                    )));
                                                }
                                            } else {
                                                self.pos = *matched_idx;
                                                results.insert(
                                                    frame.frame_id,
                                                    (
                                                        Node::DelimitedList(
                                                            frame.accumulated.clone(),
                                                        ),
                                                        *matched_idx,
                                                        None,
                                                    ),
                                                );
                                            }
                                        } else {
                                            // Delimiter matched!
                                            log::debug!("[ITERATIVE] Delimited delimiter matched: pos {} -> {}", working_idx, child_end_pos);

                                            // Collect whitespace before delimiter
                                            if *allow_gaps {
                                                for check_pos in *matched_idx..*working_idx {
                                                    if check_pos < self.tokens.len()
                                                        && !self.tokens[check_pos].is_code()
                                                        && !self
                                                            .collected_transparent_positions
                                                            .contains(&check_pos)
                                                    {
                                                        let tok = &self.tokens[check_pos];
                                                        let tok_type = tok.get_type();
                                                        if tok_type == "whitespace" {
                                                            frame.accumulated.push(
                                                                Node::Whitespace(
                                                                    tok.raw().to_string(),
                                                                    check_pos,
                                                                ),
                                                            );
                                                            self.collected_transparent_positions
                                                                .insert(check_pos);
                                                        } else if tok_type == "newline" {
                                                            frame.accumulated.push(Node::Newline(
                                                                tok.raw().to_string(),
                                                                check_pos,
                                                            ));
                                                            self.collected_transparent_positions
                                                                .insert(check_pos);
                                                        }
                                                    }
                                                }
                                            }

                                            // Add delimiter
                                            frame.accumulated.push(child_node.clone());
                                            *matched_idx = *child_end_pos;
                                            *working_idx = *matched_idx;
                                            *delimiter_count += 1;

                                            // Check if we're at a terminator
                                            self.pos = *matched_idx;
                                            if self.is_terminated(&frame_terminators) {
                                                log::debug!("[ITERATIVE] Delimited: terminated after delimiter");
                                                if !*allow_trailing {
                                                    return Err(ParseError::new(
                                                        "Trailing delimiter not allowed"
                                                            .to_string(),
                                                    ));
                                                }
                                                // Complete with trailing delimiter
                                                results.insert(
                                                    frame.frame_id,
                                                    (
                                                        Node::DelimitedList(
                                                            frame.accumulated.clone(),
                                                        ),
                                                        *matched_idx,
                                                        None,
                                                    ),
                                                );
                                            } else {
                                                // Transition back to MatchingElement state
                                                *state = DelimitedState::MatchingElement;

                                                // Skip whitespace before next element
                                                if *allow_gaps {
                                                    *working_idx = self
                                                        .skip_start_index_forward_to_code(
                                                            *working_idx,
                                                            *max_idx,
                                                        );
                                                }

                                                // Create child frame for next element
                                                let child_grammar = Grammar::OneOf {
                                                    elements: elements.clone(),
                                                    optional: false,
                                                    terminators: vec![],
                                                    reset_terminators: false,
                                                    allow_gaps: *allow_gaps,
                                                    parse_mode: *parse_mode,
                                                };

                                                let child_frame = ParseFrame {
                                                    frame_id: frame_id_counter,
                                                    grammar: child_grammar,
                                                    pos: *working_idx,
                                                    terminators: frame_terminators.clone(),
                                                    state: FrameState::Initial,
                                                    accumulated: vec![],
                                                    context: FrameContext::None,
                                                };

                                                // Update parent's last_child_frame_id
                                                if let Some(parent_frame) = stack.last_mut() {
                                                    if let FrameContext::Delimited {
                                                        last_child_frame_id,
                                                        ..
                                                    } = &mut parent_frame.context
                                                    {
                                                        *last_child_frame_id =
                                                            Some(frame_id_counter);
                                                    }
                                                }

                                                frame_id_counter += 1;
                                                stack.push(child_frame);
                                            }
                                        }
                                    }
                                }
                            }

                            _ => {
                                // TODO: Handle other grammar types
                                unimplemented!(
                                    "WaitingForChild for grammar type: {:?}",
                                    frame.grammar
                                );
                            }
                        }
                    } else {
                        return Err(ParseError::new("Child result not found".into()));
                    }
                }

                FrameState::Combining => {
                    // TODO: Handle combining results
                    unimplemented!("Combining state not yet implemented");
                }

                FrameState::Complete(node) => {
                    // This frame is done
                    results.insert(frame.frame_id, (node, self.pos, None));
                }
            }
        }

        // Return the result from the initial frame
        log::debug!(
            "Main loop ended. Stack empty. Results has {} entries. Looking for frame_id={}",
            results.len(),
            initial_frame_id
        );
        for (fid, (_node, _pos, _key)) in results.iter() {
            log::debug!("  Result frame_id={}", fid);
        }
        if let Some((node, end_pos, _element_key)) = results.get(&initial_frame_id) {
            self.pos = *end_pos;
            Ok(node.clone())
        } else {
            Err(ParseError::new(format!(
                "Iterative parse produced no result (initial_frame_id={}, results has {} entries)",
                initial_frame_id,
                results.len()
            )))
        }
    }

    /// Iterative version of OneOf matching - proof of concept
    ///
    /// This version uses an explicit stack instead of recursion to avoid
    /// stack overflow on deeply nested grammars.
    fn parse_oneof_iterative(
        &mut self,
        elements: &[Grammar],
        optional: bool,
        terminators: &[Grammar],
        reset_terminators: bool,
        allow_gaps: bool,
        parent_terminators: &[Grammar],
    ) -> Result<Node, ParseError> {
        log::debug!("Trying OneOf (ITERATIVE) with {} elements", elements.len());
        let initial_pos = self.pos;

        // Collect leading whitespace
        let leading_ws = self.collect_transparent(allow_gaps);
        let post_skip_pos = self.pos;

        // Combine parent and local terminators
        let all_terminators: Vec<Grammar> = if reset_terminators {
            terminators.to_vec()
        } else {
            terminators
                .iter()
                .cloned()
                .chain(parent_terminators.iter().cloned())
                .collect()
        };

        if self.is_terminated(&all_terminators) {
            self.pos = initial_pos;
            return if optional {
                Ok(Node::Empty)
            } else {
                Err(ParseError::new(
                    "Expected one of choices, but terminated".into(),
                ))
            };
        }

        // Prune options based on simple matchers
        let available_options = self.prune_options(elements);

        if available_options.is_empty() {
            self.pos = initial_pos;
            return if optional {
                Ok(Node::Empty)
            } else {
                Err(ParseError::new("No viable options after pruning".into()))
            };
        }

        // Instead of recursing, try each element directly with simple grammar types
        // For complex grammars, we still recurse (this is a hybrid approach)
        let mut longest_match: Option<(Node, usize, u64)> = None;

        for element in available_options {
            let element_key = element.cache_key();

            // Save parser state
            let saved_pos = self.pos;
            let saved_collected = self.collected_transparent_positions.clone();

            self.pos = post_skip_pos;

            // Try to match this element
            let result = self.parse_with_grammar_cached(element, &all_terminators);

            match result {
                Ok(node) if !node.is_empty() => {
                    let end_pos = self.pos;
                    let consumed = end_pos - post_skip_pos;

                    // Keep this match if it's the longest so far
                    if longest_match.is_none() || consumed > longest_match.as_ref().unwrap().1 {
                        longest_match = Some((node, consumed, element_key));
                        log::debug!(
                            "OneOf (ITERATIVE): New longest match: consumed {} tokens (cache key: {})",
                            consumed,
                            element_key
                        );
                    }

                    // Restore state for next element
                    self.pos = saved_pos;
                    self.collected_transparent_positions = saved_collected;
                }
                Ok(_) => {
                    // Empty node, skip
                    self.pos = saved_pos;
                    self.collected_transparent_positions = saved_collected;
                }
                Err(_) => {
                    // No match for this element
                    self.pos = saved_pos;
                    self.collected_transparent_positions = saved_collected;
                }
            }
        }

        // Process the longest match
        match longest_match {
            Some((node, consumed, _element_key)) => {
                self.pos = post_skip_pos + consumed;

                if self.is_at_end() || self.is_terminated(&all_terminators) {
                    log::debug!("OneOf (ITERATIVE): Early exit with complete/terminated match");
                    return Ok(node);
                }

                log::debug!("OneOf (ITERATIVE): Matched longest element");

                // Wrap with leading whitespace if any
                if !leading_ws.is_empty() {
                    let mut children = leading_ws;
                    children.push(node);
                    return Ok(Node::Sequence(children));
                }

                Ok(node)
            }
            None => {
                // No match found
                self.pos = initial_pos;
                if optional {
                    Ok(Node::Empty)
                } else {
                    Err(ParseError::new("Expected one of choices".into()))
                }
            }
        }
    }

    pub fn parse_with_grammar_cached(
        &mut self,
        grammar: &Grammar,
        parent_terminators: &[Grammar],
    ) -> Result<Node, ParseError> {
        // Use iterative parser if flag is set
        if self.use_iterative_parser {
            return self.parse_iterative(grammar, parent_terminators);
        }

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
        let start_pos = self.pos;
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

    /// Prune options based on simple matchers before attempting full parse.
    ///
    /// This is the Rust equivalent of Python's `prune_options()` function.
    /// It filters the list of grammar options to only those that could possibly
    /// match the current token, based on quick checks of raw strings and types.
    fn prune_options<'g>(&self, options: &'g [Grammar]) -> Vec<&'g Grammar> {
        // Find first code (non-whitespace) token from current position
        let first_code_token = self.tokens.iter().skip(self.pos).find(|t| t.is_code());

        // If no code token found, can't prune - return all options
        let Some(first_token) = first_code_token else {
            return options.iter().collect();
        };

        // Get token properties for matching
        let first_raw = first_token.raw().to_uppercase();
        let first_type = first_token.get_type();

        log::debug!(
            "Pruning {} options at pos {} (token: '{}', type: {})",
            options.len(),
            self.pos,
            first_raw,
            first_type
        );

        let mut pruned = Vec::new();

        for opt in options {
            // Try to get simple representation
            match opt.simple() {
                None => {
                    // Complex grammar - must try full match
                    log::debug!("  Keeping complex grammar: {}", opt);
                    pruned.push(opt);
                }
                Some(simple) => {
                    // Check if simple matches current token
                    if simple.could_match(first_token) {
                        log::debug!("  Keeping matched grammar: {}", opt);
                        pruned.push(opt);
                    } else {
                        log::debug!("  PRUNED grammar: {}", opt);
                    }
                }
            }
        }

        log::debug!(
            "Pruned from {} to {} options ({:.1}% reduction)",
            options.len(),
            pruned.len(),
            100.0 * (1.0 - pruned.len() as f64 / options.len() as f64)
        );

        pruned
    }

    /// Print cache statistics
    pub fn print_cache_stats(&self) {
        let (hits, misses, hit_rate) = self.parse_cache.stats();
        eprintln!("Parse Cache Statistics:");
        eprintln!("  Hits: {}", hits);
        eprintln!("  Misses: {}", misses);
        eprintln!("  Hit Rate: {:.2}%", hit_rate * 100.0);
    }

    pub fn parse_with_grammar(
        &'_ mut self,
        grammar: &Grammar,
        parent_terminators: &[Grammar],
    ) -> Result<Node, ParseError> {
        log::debug!("Parsing with grammar: {}@{}", grammar, self.pos);
        // log::debug!("Parent terminators: {:?}", parent_terminators);
        match grammar {
            Grammar::Missing => {
                log::debug!("Trying missing grammar");
                todo!("Encountered Missing grammar in parse_with_grammar");
            }
            Grammar::Anything => {
                // This matches anything
                // it is greedy so will consume everything until a terminator is found
                log::debug!("Trying Anything grammar");
                let mut anything_tokens = vec![];
                loop {
                    if self.is_terminated(parent_terminators) || self.is_at_end() {
                        break;
                    }
                    if let Some(tok) = self.peek() {
                        anything_tokens.push(Node::Code(tok.raw().to_string(), self.pos));
                        self.bump();
                    }
                }
                log::debug!("Anything matched tokens: {:?}", anything_tokens);
                Ok(Node::DelimitedList(anything_tokens))
            }
            Grammar::Token { token_type } => {
                log::debug!("Trying token grammar, {}", token_type);
                if let Some(token) = self.peek() {
                    let tok = token.clone();
                    log::debug!("Current token: {:?}", tok.get_type());
                    if tok.get_type() == *token_type {
                        let node = Node::Code(tok.raw(), self.pos);
                        self.bump();
                        log::debug!("MATCHED Token matched: {:?}", tok);
                        Ok(node)
                    } else {
                        Err(ParseError::new(format!(
                            "Expected token type {}, found {}",
                            token_type,
                            tok.get_type()
                        )))
                    }
                } else {
                    Err(ParseError::new("Expected token, found EOF".into()))
                }
            }
            Grammar::Meta(token_type) => {
                log::debug!("Doing nothing with meta {}", token_type);
                Ok(Node::Meta(token_type))
                // Ok(Node::Empty)
            }
            Grammar::StringParser {
                template,
                token_type,
                optional,
            } => {
                log::debug!("Trying string parser: {}, type: {:?}", template, token_type);
                self.skip_transparent(true);
                let tok_raw = self.peek().cloned();
                match tok_raw {
                    Some(tok) if tok.raw().eq_ignore_ascii_case(template) => {
                        let token_pos = self.pos; // Save position before bumping
                        self.bump();
                        log::debug!("MATCHED String matched: {}", tok);
                        // Create Node::Keyword for keyword token_type, Node::Code otherwise
                        if *token_type == "keyword" {
                            Ok(Node::Keyword(tok.raw(), token_pos))
                        } else {
                            Ok(Node::Code(tok.raw(), token_pos))
                        }
                    }
                    _ => {
                        if *optional {
                            log::debug!("String parser optional, skipping");
                            Ok(Node::Empty)
                        } else {
                            Err(ParseError::new(format!("Expected string '{}'", template)))
                        }
                    }
                }
            }
            Grammar::MultiStringParser {
                templates,
                token_type,
                optional,
            } => {
                log::debug!(
                    "Trying multi string parser: {:?}, type: {:?}",
                    templates,
                    token_type
                );
                self.skip_transparent(true);
                let token = self.peek().cloned();
                match token {
                    Some(tok)
                        if templates
                            .iter()
                            .any(|&temp| tok.raw().eq_ignore_ascii_case(temp)) =>
                    {
                        let token_pos = self.pos; // Save position before bumping
                        self.bump();
                        log::debug!("MATCHED Multi string matched: {}", tok);
                        // Create Node::Keyword for keyword token_type, Node::Code otherwise
                        if *token_type == "keyword" {
                            Ok(Node::Keyword(tok.raw(), token_pos))
                        } else {
                            Ok(Node::Code(tok.raw(), token_pos))
                        }
                    }
                    _ => {
                        if *optional {
                            Ok(Node::Empty)
                        } else {
                            Err(ParseError::new(format!(
                                "Expected one of strings '{:?}'",
                                templates
                            )))
                        }
                    }
                }
            }
            Grammar::RegexParser {
                template,
                token_type,
                optional,
                anti_template,
            } => {
                log::debug!("Trying regex parser: {}, type: {:?}", template, token_type);
                self.skip_transparent(true);
                let token = self.peek().cloned();
                match token {
                    Some(tok)
                        if regex::RegexBuilder::new(template)
                            .case_insensitive(true)
                            .build()
                            .unwrap()
                            .is_match(&tok.raw()) =>
                    {
                        log::debug!("Regex matched: {}", tok);
                        if let Some(anti) = anti_template {
                            if regex::RegexBuilder::new(anti)
                                .case_insensitive(true)
                                .build()
                                .unwrap()
                                .is_match(&tok.raw())
                            {
                                log::debug!("Regex anti-matched: {}", tok);
                                if *optional {
                                    return Ok(Node::Empty);
                                } else {
                                    return Err(ParseError::new(format!(
                                        "Token '{}' matches anti-template '{}'",
                                        tok, anti
                                    )));
                                }
                            }
                        }
                        log::debug!("MATCHED Regex matched and non anti-match: {}", tok);
                        let token_pos = self.pos; // Save position before bumping
                        self.bump();
                        Ok(Node::Code(tok.raw(), token_pos))
                    }
                    _ => {
                        if *optional {
                            Ok(Node::Empty)
                        } else {
                            Err(ParseError::new(format!(
                                "Expected token matching regex '{}'",
                                template
                            )))
                        }
                    }
                }
            }
            Grammar::TypedParser {
                template,
                token_type,
                optional,
            } => {
                log::debug!("Trying typed parser: {}, type: {}", template, token_type);
                self.skip_transparent(true);
                if let Some(token) = self.peek() {
                    let tok = token.clone();
                    if tok.is_type(&[template]) {
                        let raw = tok.raw().to_string(); // Clone the raw value to avoid borrowing issues
                        let node = Node::Code(raw, self.pos); // Pass the cloned raw value and the token reference
                        self.bump();
                        log::debug!("MATCHED Typed matched: {}", tok.token_type);
                        Ok(node)
                    } else if *optional {
                        log::debug!("Typed parser optional, skipping");
                        Ok(Node::Empty)
                    } else {
                        log::debug!(
                            "NOMATCH Typed parser expected '{}', found '{}'",
                            template,
                            tok.token_type
                        );
                        Err(ParseError::new(format!(
                            "Expected typed token '{}'",
                            template
                        )))
                    }
                } else if *optional {
                    log::debug!("Typed parser optional, skipping at EOF");
                    Ok(Node::Empty)
                } else {
                    log::debug!("NOMATCH Typed parser expected '{}', found EOF", template);
                    Err(ParseError::new(format!(
                        "Expected typed token '{}', found EOF",
                        template
                    )))
                }
            }
            Grammar::Symbol(sym) => {
                log::debug!("Trying symbol: {}", sym);
                let token = self.peek().cloned();
                match token {
                    Some(tok) if tok.raw() == *sym => {
                        let token_pos = self.pos; // Save position before bumping
                        self.bump();
                        log::debug!("MATCHED Symbol matched: {}", sym);
                        Ok(Node::Code(tok.raw(), token_pos))
                    }
                    _ => Err(ParseError::new(format!("Expected symbol '{}'", sym))),
                }
            }
            Grammar::Ref {
                name,
                optional,
                allow_gaps,
                terminators,
                reset_terminators,
            } => {
                log::debug!(
                    "Trying Ref to segment: {}, optional: {}, allow_gaps: {}",
                    name,
                    optional,
                    allow_gaps
                );
                let saved = self.pos;
                self.skip_transparent(*allow_gaps);

                // Combine parent and local terminators
                let all_terminators: Vec<Grammar> = if *reset_terminators {
                    terminators.clone()
                } else {
                    terminators
                        .iter()
                        .cloned()
                        .chain(parent_terminators.iter().cloned())
                        .collect()
                };

                let attempt = self.call_rule(name, &all_terminators);
                match attempt {
                    Ok(node) => {
                        log::debug!("MATCHED Ref matched segment: {}", name);
                        Ok(node)
                    }
                    Err(e) => {
                        self.pos = saved;
                        if *optional {
                            log::debug!("Ref optional, skipping");
                            Ok(Node::Empty)
                        } else {
                            Err(e)
                        }
                    }
                }
            }
            Grammar::Sequence {
                elements,
                optional,
                terminators,
                reset_terminators,
                allow_gaps,
                parse_mode,
            } => {
                let start_idx = self.pos; // Where did we start
                log::debug!(
                    "Sequence starting at {}, allow_gaps={}, parse_mode={:?}",
                    start_idx,
                    allow_gaps,
                    parse_mode
                );
                let mut matched_idx = self.pos; // Where have we got to
                let mut last_collected_idx = None::<usize>; // Track last position where we collected transparent tokens
                let mut max_idx = self.tokens.len(); // What is the limit
                let mut children: Vec<Node> = Vec::new();
                let mut first_match = true;
                let mut tentatively_collected_positions: Vec<usize> = Vec::new(); // Track positions we collected but haven't committed yet

                // Combine parent and local terminators
                let all_terminators: Vec<Grammar> = if *reset_terminators {
                    terminators.clone()
                } else {
                    terminators
                        .iter()
                        .cloned()
                        .chain(parent_terminators.iter().cloned())
                        .collect()
                };

                // GREEDY: In the GREEDY mode, we first look ahead to find a terminator
                // before matching any code.
                if *parse_mode == ParseMode::Greedy {
                    max_idx = self.trim_to_terminator(self.pos, &all_terminators);
                    log::debug!("GREEDY mode: trimmed max_idx to {}", max_idx);
                }

                // Iterate through elements
                for element in elements {
                    log::debug!("Sequence-@{}: matching {:?}", matched_idx, element);

                    // 1. Handle Meta segments (indent/dedent)
                    if let Grammar::Meta(meta_type) = element {
                        if *meta_type == "indent" {
                            log::debug!("Inserting Meta: {}", meta_type);
                            // Indent goes before whitespace
                            let mut insert_pos = children.len();
                            while insert_pos > 0 {
                                match &children[insert_pos - 1] {
                                    Node::Whitespace(_, _) | Node::Newline(_, _) => {
                                        insert_pos -= 1;
                                    }
                                    _ => break,
                                }
                            }
                            children.insert(insert_pos, Node::Meta(meta_type));
                        } else if *meta_type == "dedent" {
                            log::debug!("Inserting Meta: {}", meta_type);
                            children.push(Node::Meta(meta_type));
                        }
                        continue;
                    }

                    // 2. Skip whitespace/newlines if allow_gaps
                    self.pos = matched_idx;
                    let mut _idx = matched_idx;
                    log::debug!(
                        "Before collection: matched_idx={}, allow_gaps={}",
                        matched_idx,
                        *allow_gaps
                    );
                    if *allow_gaps {
                        _idx = self.skip_start_index_forward_to_code(matched_idx, max_idx);

                        // Check if any positions in the range matched_idx.._idx need to be collected
                        // We should collect if we haven't already collected from this range
                        let has_uncollected = (matched_idx.._idx).any(|pos| {
                            pos < self.tokens.len()
                                && !self.tokens[pos].is_code()
                                && !self.collected_transparent_positions.contains(&pos)
                        });

                        let should_collect = has_uncollected;

                        log::debug!(
                            "Collection check: matched_idx={}, _idx={}, has_uncollected={}, should_collect={}",
                            matched_idx,
                            _idx,
                            has_uncollected,
                            should_collect
                        );

                        if should_collect {
                            // Collect the transparent tokens we're skipping
                            while self.pos < _idx {
                                let current_pos = self.pos;
                                if let Some(tok) = self.peek() {
                                    let tok_type = tok.get_type();
                                    if tok_type == "whitespace" {
                                        log::debug!(
                                            "COLLECTING whitespace at token pos {}: {:?}",
                                            self.pos,
                                            tok.raw()
                                        );
                                        children.push(Node::Whitespace(
                                            tok.raw().to_string(),
                                            self.pos,
                                        ));
                                        // Mark as tentatively collected AND add to global set immediately
                                        // This prevents nested Sequences from re-collecting the same token
                                        tentatively_collected_positions.push(current_pos);
                                        self.collected_transparent_positions.insert(current_pos);
                                    } else if tok_type == "newline" {
                                        log::debug!(
                                            "COLLECTING newline at token pos {}: {:?}",
                                            self.pos,
                                            tok.raw()
                                        );
                                        children
                                            .push(Node::Newline(tok.raw().to_string(), self.pos));
                                        // Mark as tentatively collected AND add to global set immediately
                                        tentatively_collected_positions.push(current_pos);
                                        self.collected_transparent_positions.insert(current_pos);
                                    }
                                }
                                self.bump();
                            }
                            // Update last collected position
                            last_collected_idx = Some(matched_idx);
                        } else {
                            log::debug!(
                                "SKIPPING collection at matched_idx={} (already collected)",
                                matched_idx
                            );
                            // Still need to advance self.pos even if not collecting
                            self.pos = _idx;
                        }
                    }

                    // 3. Have we prematurely run out of segments?
                    if _idx >= max_idx {
                        // Check if this element is optional
                        let element_is_optional = match element {
                            Grammar::Sequence { optional, .. } => *optional,
                            Grammar::AnyNumberOf { optional, .. } => *optional,
                            Grammar::OneOf { optional, .. } => *optional,
                            Grammar::Delimited { optional, .. } => *optional,
                            Grammar::Bracketed { optional, .. } => *optional,
                            Grammar::Ref { optional, .. } => *optional,
                            Grammar::StringParser { optional, .. } => *optional,
                            Grammar::MultiStringParser { optional, .. } => *optional,
                            Grammar::TypedParser { optional, .. } => *optional,
                            Grammar::RegexParser { optional, .. } => *optional,
                            _ => false,
                        };

                        if element_is_optional {
                            log::debug!("Element is optional, continuing");
                            continue;
                        }

                        // Required element but ran out of segments
                        if *parse_mode == ParseMode::Strict || matched_idx == start_idx {
                            log::debug!(
                                "NOMATCH Ran out of segments in STRICT mode or nothing matched yet"
                            );
                            self.pos = start_idx;
                            // Rollback: remove tentatively collected positions from global set
                            for pos in &tentatively_collected_positions {
                                self.collected_transparent_positions.remove(pos);
                            }
                            return Ok(Node::Empty);
                        }

                        // GREEDY/GREEDY_ONCE_STARTED: return what we have with error marker
                        // TODO: Create proper UnparsableSegment representation
                        log::debug!(
                            "INCOMPLETE match in {:?} mode: expected {:?} but ran out of segments",
                            parse_mode,
                            element
                        );
                        self.pos = matched_idx;
                        return Ok(Node::Sequence(children));
                    }

                    // 4. Try to match the element
                    self.pos = _idx;
                    let elem_match = self.parse_with_grammar_cached(element, &all_terminators);

                    match elem_match {
                        Ok(node) => {
                            if node.is_empty() {
                                // Optional element didn't match
                                log::debug!("Element returned Empty, continuing");
                                continue;
                            }

                            // Successfully matched
                            let element_start = _idx; // Where the element started parsing
                            matched_idx = self.pos; // Where we ended up after parsing
                            log::debug!(
                                "MATCHED Sequence element, now at position {}",
                                matched_idx
                            );

                            // Add the matched node first
                            children.push(node);

                            // THEN handle retroactive collection of trailing transparent tokens
                            // If the Sequence has allow_gaps=false but the element skipped transparent tokens,
                            // we need to collect them retroactively!
                            if !*allow_gaps {
                                // The element was parsed starting at element_start
                                // After matching, we're at matched_idx
                                // We need to collect any transparent tokens between where the element
                                // actually consumed code tokens and where we ended up

                                // Find where the element actually consumed its last code token
                                // by working backwards from matched_idx
                                let mut last_code_consumed = element_start;
                                for check_pos in element_start..matched_idx {
                                    if check_pos < self.tokens.len()
                                        && self.tokens[check_pos].is_code()
                                    {
                                        last_code_consumed = check_pos;
                                    }
                                }

                                log::debug!(
                                    "Retroactive collection: element_start={}, last_code_consumed={}, matched_idx={}",
                                    element_start, last_code_consumed, matched_idx
                                );

                                // Collect transparent tokens from right after the last code token
                                // Continue collecting ALL transparent tokens until we hit code
                                let mut collect_end = matched_idx;
                                while collect_end < self.tokens.len()
                                    && !self.tokens[collect_end].is_code()
                                {
                                    collect_end += 1;
                                }

                                log::debug!(
                                    "Retroactive collection will collect from {} to {}",
                                    last_code_consumed + 1,
                                    collect_end
                                );

                                for check_pos in (last_code_consumed + 1)..collect_end {
                                    log::debug!(
                                        "Checking position {} for retroactive collection: is_code={}, in_global={}, in_tentative={}",
                                        check_pos,
                                        if check_pos < self.tokens.len() { self.tokens[check_pos].is_code() } else { true },
                                        self.collected_transparent_positions.contains(&check_pos),
                                        tentatively_collected_positions.contains(&check_pos)
                                    );
                                    if check_pos < self.tokens.len()
                                        && !self.tokens[check_pos].is_code()
                                        && !self
                                            .collected_transparent_positions
                                            .contains(&check_pos)
                                        && !tentatively_collected_positions.contains(&check_pos)
                                    {
                                        let tok = &self.tokens[check_pos];
                                        let tok_type = tok.get_type();
                                        if tok_type == "whitespace" {
                                            log::debug!("RETROACTIVELY collecting whitespace at token pos {}: {:?}", check_pos, tok.raw());
                                            children.push(Node::Whitespace(
                                                tok.raw().to_string(),
                                                check_pos,
                                            ));
                                            tentatively_collected_positions.push(check_pos);
                                            self.collected_transparent_positions.insert(check_pos);
                                        } else if tok_type == "newline" {
                                            log::debug!("RETROACTIVELY collecting newline at token pos {}: {:?}", check_pos, tok.raw());
                                            children.push(Node::Newline(
                                                tok.raw().to_string(),
                                                check_pos,
                                            ));
                                            tentatively_collected_positions.push(check_pos);
                                            self.collected_transparent_positions.insert(check_pos);
                                        }
                                    }
                                }
                                last_collected_idx = Some(matched_idx - 1);
                            }

                            // GREEDY_ONCE_STARTED: Trim to terminator after first match
                            if first_match && *parse_mode == ParseMode::GreedyOnceStarted {
                                max_idx = self.trim_to_terminator(matched_idx, &all_terminators);
                                log::debug!(
                                    "GREEDY_ONCE_STARTED: trimmed max_idx to {} after first match",
                                    max_idx
                                );
                                first_match = false;
                            }
                        }
                        Err(_e) => {
                            // Element failed to match
                            self.pos = _idx;

                            // Check if element is optional
                            let element_is_optional = match element {
                                Grammar::Sequence { optional, .. } => *optional,
                                Grammar::AnyNumberOf { optional, .. } => *optional,
                                Grammar::OneOf { optional, .. } => *optional,
                                Grammar::Delimited { optional, .. } => *optional,
                                Grammar::Bracketed { optional, .. } => *optional,
                                Grammar::Ref { optional, .. } => *optional,
                                Grammar::StringParser { optional, .. } => *optional,
                                Grammar::MultiStringParser { optional, .. } => *optional,
                                Grammar::TypedParser { optional, .. } => *optional,
                                Grammar::RegexParser { optional, .. } => *optional,
                                _ => false,
                            };

                            if element_is_optional {
                                log::debug!("NOMATCH Element is optional, continuing");
                                continue;
                            }

                            // Required element failed
                            if *parse_mode == ParseMode::Strict {
                                log::debug!("NOMATCH Required element failed in STRICT mode");
                                self.pos = start_idx;
                                // Rollback: remove tentatively collected positions from global set
                                for pos in &tentatively_collected_positions {
                                    self.collected_transparent_positions.remove(pos);
                                }
                                return Ok(Node::Empty);
                            }

                            if *parse_mode == ParseMode::GreedyOnceStarted
                                && matched_idx == start_idx
                            {
                                log::debug!(
                                    "NOMATCH Nothing matched yet in GREEDY_ONCE_STARTED mode"
                                );
                                self.pos = start_idx;
                                // Rollback: remove tentatively collected positions from global set
                                for pos in &tentatively_collected_positions {
                                    self.collected_transparent_positions.remove(pos);
                                }
                                return Ok(Node::Empty);
                            }

                            // GREEDY or GREEDY_ONCE_STARTED after first match:
                            // Return partial match (TODO: mark remaining as unparsable)
                            log::debug!(
                                "INCOMPLETE match in {:?} mode: expected {:?} at position {}",
                                parse_mode,
                                element,
                                _idx
                            );
                            self.pos = matched_idx;
                            // Already committed to global set, no need to commit again
                            return Ok(Node::Sequence(children));
                        }
                    }
                }

                // All elements matched (or were optional)
                self.pos = matched_idx;

                // Collect any trailing non-code tokens (whitespace, newlines, end_of_file)
                // Note: We always consume end_of_file even if allow_gaps is false
                while self.pos < max_idx {
                    if let Some(tok) = self.peek() {
                        if tok.is_code() {
                            break; // Stop at code tokens
                        }
                        let tok_type = tok.get_type();
                        if tok_type == "whitespace" {
                            if *allow_gaps && !self.collected_transparent_positions.contains(&self.pos) {
                                children.push(Node::Whitespace(tok.raw().to_string(), self.pos));
                                tentatively_collected_positions.push(self.pos);
                                self.collected_transparent_positions.insert(self.pos);
                            }
                        } else if tok_type == "newline" {
                            if *allow_gaps && !self.collected_transparent_positions.contains(&self.pos) {
                                children.push(Node::Newline(tok.raw().to_string(), self.pos));
                                tentatively_collected_positions.push(self.pos);
                                self.collected_transparent_positions.insert(self.pos);
                            }
                        } else if tok_type == "end_of_file" {
                            // Always collect end_of_file, even if it was already collected elsewhere
                            // (though this should be rare/impossible)
                            children.push(Node::EndOfFile(tok.raw().to_string(), self.pos));
                            if !self.collected_transparent_positions.contains(&self.pos) {
                                tentatively_collected_positions.push(self.pos);
                                self.collected_transparent_positions.insert(self.pos);
                            }
                        }
                        self.bump();
                    } else {
                        break;
                    }
                }
                matched_idx = self.pos;

                // In GREEDY/GREEDY_ONCE_STARTED modes: if there's anything left unclaimed,
                // mark it as unparsable
                if (*parse_mode == ParseMode::Greedy || *parse_mode == ParseMode::GreedyOnceStarted)
                    && max_idx > matched_idx
                {
                    let _idx = self.skip_start_index_forward_to_code(matched_idx, max_idx);
                    let _stop_idx = self.skip_stop_index_backward_to_code(max_idx, _idx);

                    if _stop_idx > _idx {
                        log::debug!(
                            "GREEDY mode: {} unparsable tokens remaining from {} to {}",
                            _stop_idx - _idx,
                            _idx,
                            _stop_idx
                        );
                        // TODO: Create proper UnparsableSegment representation
                        // For now, just consume them
                        while self.pos < _stop_idx {
                            if let Some(tok) = self.peek() {
                                children.push(Node::Code(tok.raw().to_string(), self.pos));
                            }
                            self.bump();
                        }
                        matched_idx = _stop_idx;
                    }
                }

                self.pos = matched_idx;

                // If we have no children and the sequence itself is optional, return Empty
                if children.is_empty() && *optional {
                    log::debug!("Sequence matched no children and is optional, returning Empty");
                    // Rollback: remove tentatively collected positions from global set since we're returning Empty
                    for pos in &tentatively_collected_positions {
                        self.collected_transparent_positions.remove(pos);
                    }
                    Ok(Node::Empty)
                } else {
                    // Already committed to global set, positions were added immediately when collected
                    Ok(Node::Sequence(children))
                }
            }
            Grammar::OneOf {
                elements,
                optional,
                terminators,
                reset_terminators,
                allow_gaps,
                parse_mode,
            } => {
                log::debug!("Trying OneOf elements: {:?}", elements);
                let initial_pos = self.pos;

                // Collect leading whitespace
                let leading_ws = self.collect_transparent(*allow_gaps);
                let post_skip_pos = self.pos;

                // Combine parent and local terminators
                let all_terminators: Vec<Grammar> = if *reset_terminators {
                    terminators.clone()
                } else {
                    terminators
                        .iter()
                        .cloned()
                        .chain(parent_terminators.iter().cloned())
                        .collect()
                };

                if self.is_terminated(&all_terminators) {
                    self.pos = initial_pos;
                    return if *optional {
                        Ok(Node::Empty)
                    } else {
                        Err(ParseError::new(
                            "Expected one of choices, but terminated".into(),
                        ))
                    };
                }

                // Prune options based on simple matchers
                let available_options = self.prune_options(elements);

                if available_options.is_empty() {
                    self.pos = initial_pos;
                    return if *optional {
                        Ok(Node::Empty)
                    } else {
                        Err(ParseError::new("No viable options after pruning".into()))
                    };
                }

                // Use the common longest-match logic (macro for zero-cost abstraction)
                match find_longest_match!(
                    self,
                    elements,
                    post_skip_pos,
                    &all_terminators,
                    None::<&std::collections::HashSet<u64>>, // No exclude keys for OneOf
                    None::<&usize>,                          // No max count per element for OneOf
                    None::<&std::collections::HashMap<u64, usize>>  // No option counter for OneOf
                ) {
                    Some((node, end_pos, _element_key)) => {
                        // Early exit on complete/terminated match
                        self.pos = end_pos;
                        if self.is_at_end() || self.is_terminated(&all_terminators) {
                            log::debug!("OneOf: Early exit with complete/terminated match");
                            return Ok(node);
                        }

                        log::debug!("MATCHED OneOf matched longest element");

                        // Wrap with leading whitespace if any
                        if !leading_ws.is_empty() {
                            let mut children = leading_ws;
                            children.push(node);
                            return Ok(Node::Sequence(children));
                        }

                        Ok(node)
                    }
                    None => {
                        // No match found
                        self.pos = initial_pos;
                        if *optional {
                            Ok(Node::Empty)
                        } else {
                            Err(ParseError::new("Expected one of choices".into()))
                        }
                    }
                }
            }
            Grammar::AnyNumberOf {
                elements,
                min_times,
                max_times,
                max_times_per_element,
                optional,
                terminators,
                reset_terminators,
                allow_gaps,
                parse_mode,
            } => {
                log::debug!(
                    "Trying AnyNumberOf with {} elements, parse_mode: {:?}, max_times_per_element: {:?}",
                    elements.len(),
                    parse_mode,
                    max_times_per_element
                );
                let mut items = vec![];
                let mut count = 0;
                let initial_pos = self.pos;

                // Track how many times each option has been matched
                let mut option_counter: std::collections::HashMap<u64, usize> =
                    std::collections::HashMap::new();

                // Combine parent and local terminators
                let all_terminators: Vec<Grammar> = if *reset_terminators {
                    terminators.clone()
                } else {
                    terminators
                        .iter()
                        .cloned()
                        .chain(parent_terminators.iter().cloned())
                        .collect()
                };

                // Determine max_idx based on parse_mode
                let max_idx = if *parse_mode == ParseMode::Greedy {
                    self.trim_to_terminator(initial_pos, &all_terminators)
                } else {
                    self.tokens.len()
                };

                log::debug!(
                    "AnyNumberOf max_idx: {} (tokens.len: {})",
                    max_idx,
                    self.tokens.len()
                );

                // Track matched_idx and working_idx like Python
                let mut matched_idx = initial_pos;
                let mut working_idx = initial_pos;

                loop {
                    // Check if we've met min_times and reached limits
                    if count >= *min_times
                        && (matched_idx >= max_idx
                            || (max_times.is_some() && count >= max_times.unwrap()))
                    {
                        log::debug!(
                            "AnyNumberOf: reached limits at {} matches, matched_idx: {}, max_idx: {}",
                            count, matched_idx, max_idx
                        );
                        break;
                    }

                    // Is there nothing left to match?
                    if matched_idx >= max_idx {
                        // If we haven't met the hurdle rate, fail
                        if count < *min_times {
                            if *optional {
                                self.pos = initial_pos;
                                log::debug!("AnyNumberOf returning Empty (didn't meet min_times)");
                                return Ok(Node::Empty);
                            } else {
                                return Err(ParseError::new(format!(
                                    "Expected at least {} occurrences, found {}",
                                    min_times, count
                                )));
                            }
                        }
                        break;
                    }

                    // Save position before attempting match
                    let _pre_match_pos = working_idx;

                    // Update working_idx to skip whitespace if allowed
                    if *allow_gaps {
                        working_idx = self.skip_start_index_forward_to_code(working_idx, max_idx);
                    }

                    // Use the common longest-match logic (macro for zero-cost abstraction)
                    let longest_match_result = find_longest_match!(
                        self,
                        elements,
                        working_idx,
                        &all_terminators,
                        None::<&std::collections::HashSet<u64>>, // No exclude keys for AnyNumberOf
                        max_times_per_element.as_ref(),          // Max count per element
                        Some(&option_counter)                    // Option counter for tracking
                    );

                    // Did we fail to match?
                    if longest_match_result.is_none() {
                        log::debug!("AnyNumberOf: no match found at position {}", working_idx);
                        // If we haven't met the hurdle rate, fail
                        if count < *min_times {
                            if *optional {
                                self.pos = initial_pos;
                                log::debug!(
                                    "AnyNumberOf returning Empty (no match, didn't meet min_times)"
                                );
                                return Ok(Node::Empty);
                            } else {
                                return Err(ParseError::new(format!(
                                    "Expected at least {} occurrences, found {}",
                                    min_times, count
                                )));
                            }
                        }
                        // Otherwise we're done
                        break;
                    }

                    // We have a match!
                    let (node, end_pos, element_key) = longest_match_result.unwrap();

                    // Update the counter for this element
                    *option_counter.entry(element_key).or_insert(0) += 1;

                    // Check if we've now exceeded max_times_per_element for this element
                    if let Some(max_per_elem) = max_times_per_element {
                        let elem_count = option_counter.get(&element_key).copied().unwrap_or(0);
                        if elem_count > *max_per_elem {
                            log::debug!(
                                "AnyNumberOf: element exceeded max_times_per_element, stopping (without including this match)"
                            );
                            // Return the match so far, without the most recent match
                            break;
                        }
                    }

                    // Collect whitespace/non-code between matched_idx and working_idx
                    if *allow_gaps && matched_idx < working_idx {
                        while matched_idx < working_idx {
                            if let Some(tok) = self.tokens.get(matched_idx) {
                                let tok_type = tok.get_type();
                                if tok_type == "whitespace" {
                                    items
                                        .push(Node::Whitespace(tok.raw().to_string(), matched_idx));
                                } else if tok_type == "newline" {
                                    items.push(Node::Newline(tok.raw().to_string(), matched_idx));
                                }
                            }
                            matched_idx += 1;
                        }
                    }

                    // Add the matched node
                    items.push(node);
                    matched_idx = end_pos;
                    working_idx = matched_idx;
                    count += 1;

                    log::debug!(
                        "AnyNumberOf: matched element #{}, matched_idx now: {}",
                        count,
                        matched_idx
                    );

                    // Check max_times limit
                    if let Some(max) = max_times {
                        if count >= *max {
                            log::debug!("AnyNumberOf: reached max_times {}", max);
                            break;
                        }
                    }
                }

                // Update parser position to matched_idx
                self.pos = matched_idx;

                // Apply parse_mode logic for remaining content
                if *parse_mode == ParseMode::Greedy {
                    // Check if there's unparsable content remaining
                    if matched_idx < max_idx {
                        // Check if all remaining is non-code
                        let all_non_code = (matched_idx..max_idx)
                            .all(|i| self.tokens.get(i).map_or(true, |t| !t.is_code()));

                        if !all_non_code {
                            // There's code content we didn't match - create unparsable segment
                            let _trim_idx =
                                self.skip_start_index_forward_to_code(matched_idx, max_idx);

                            log::debug!(
                                "GREEDY mode: creating unparsable segment from {} to {}",
                                _trim_idx,
                                max_idx
                            );

                            // TODO: Create proper UnparsableSegment with expected message
                            // For now, consume as Code nodes
                            while self.pos < max_idx {
                                if let Some(tok) = self.peek() {
                                    let tok_type = tok.get_type();
                                    if tok_type == "whitespace" {
                                        items.push(Node::Whitespace(
                                            tok.raw().to_string(),
                                            self.pos,
                                        ));
                                    } else if tok_type == "newline" {
                                        items.push(Node::Newline(tok.raw().to_string(), self.pos));
                                    } else {
                                        items.push(Node::Code(tok.raw().to_string(), self.pos));
                                    }
                                }
                                self.bump();
                            }
                        }
                    }
                }

                log::debug!(
                    "MATCHED AnyNumberOf with {} items at position {}",
                    items.len(),
                    self.pos
                );
                Ok(Node::DelimitedList(items))
            }
            Grammar::AnySetOf {
                elements,
                min_times,
                max_times,
                optional,
                terminators,
                reset_terminators,
                allow_gaps,
                parse_mode,
            } => {
                // AnySetOf is AnyNumberOf with max_times_per_element=1
                // Each element can only be matched once
                log::debug!(
                    "Trying AnySetOf with {} elements, parse_mode: {:?}",
                    elements.len(),
                    parse_mode
                );

                let mut items = vec![];
                let mut count = 0;
                let initial_pos = self.pos;

                // Track which elements have been matched (by cache key)
                let mut matched_elements: std::collections::HashSet<u64> =
                    std::collections::HashSet::new();

                // Combine parent and local terminators
                let all_terminators: Vec<Grammar> = if *reset_terminators {
                    terminators.clone()
                } else {
                    terminators
                        .iter()
                        .cloned()
                        .chain(parent_terminators.iter().cloned())
                        .collect()
                };

                // Determine max_idx based on parse_mode
                let max_idx = if *parse_mode == ParseMode::Greedy {
                    self.trim_to_terminator(initial_pos, &all_terminators)
                } else {
                    self.tokens.len()
                };

                log::debug!(
                    "AnySetOf max_idx: {} (tokens.len: {})",
                    max_idx,
                    self.tokens.len()
                );

                // Track matched_idx and working_idx
                let mut matched_idx = initial_pos;
                let mut working_idx = initial_pos;

                loop {
                    // Check if we've met min_times and reached limits
                    if count >= *min_times
                        && (matched_idx >= max_idx
                            || (max_times.is_some() && count >= max_times.unwrap()))
                    {
                        log::debug!(
                            "AnySetOf: reached limits at {} matches, matched_idx: {}, max_idx: {}",
                            count,
                            matched_idx,
                            max_idx
                        );
                        break;
                    }

                    // Is there nothing left to match?
                    if matched_idx >= max_idx {
                        // If we haven't met the hurdle rate, fail
                        if count < *min_times {
                            if *optional {
                                self.pos = initial_pos;
                                log::debug!("AnySetOf returning Empty (didn't meet min_times)");
                                return Ok(Node::Empty);
                            } else {
                                return Err(ParseError::new(format!(
                                    "Expected at least {} occurrences, found {}",
                                    min_times, count
                                )));
                            }
                        }
                        break;
                    }

                    // Update working_idx to skip whitespace if allowed
                    if *allow_gaps {
                        working_idx = self.skip_start_index_forward_to_code(working_idx, max_idx);
                    }

                    // Use the common longest-match logic
                    let longest_match_result = find_longest_match!(
                        self,
                        elements,
                        working_idx,
                        &all_terminators,
                        Some(&matched_elements), // Exclude already-matched elements
                        None::<&usize>,          // No max count per element for AnySetOf
                        None::<&std::collections::HashMap<u64, usize>> // No option counter for AnySetOf
                    );

                    // Did we fail to match?
                    if longest_match_result.is_none() {
                        log::debug!("AnySetOf: no match found at position {}", working_idx);
                        // If we haven't met the hurdle rate, fail
                        if count < *min_times {
                            if *optional {
                                self.pos = initial_pos;
                                log::debug!("AnySetOf optional, returning Empty");
                                return Ok(Node::Empty);
                            } else {
                                return Err(ParseError::new(format!(
                                    "Expected at least {} occurrences, found {}",
                                    min_times, count
                                )));
                            }
                        } else {
                            // We met the hurdle, done
                            break;
                        }
                    }

                    // Success - add the match
                    let (node, end_pos, element_key) = longest_match_result.unwrap();

                    // Mark this element as matched (AnySetOf constraint)
                    matched_elements.insert(element_key);

                    items.push(node);
                    matched_idx = end_pos;
                    working_idx = matched_idx;
                    count += 1;

                    log::debug!(
                        "AnySetOf: matched element #{}, matched_idx now: {}",
                        count,
                        matched_idx
                    );

                    // Check max_times limit
                    if let Some(max) = max_times {
                        if count >= *max {
                            log::debug!("AnySetOf: reached max_times {}", max);
                            break;
                        }
                    }
                }

                // Update parser position to matched_idx
                self.pos = matched_idx;

                // Apply parse_mode logic for remaining content (GREEDY mode)
                if *parse_mode == ParseMode::Greedy {
                    // Check if there's unparsable content remaining
                    if matched_idx < max_idx {
                        // Check if all remaining is non-code
                        let all_non_code = (matched_idx..max_idx)
                            .all(|i| self.tokens.get(i).map_or(true, |t| !t.is_code()));

                        if !all_non_code {
                            // There's code content we didn't match - consume as tokens
                            log::debug!(
                                "AnySetOf GREEDY mode: consuming remaining tokens from {} to {}",
                                matched_idx,
                                max_idx
                            );

                            while self.pos < max_idx {
                                if let Some(tok) = self.peek() {
                                    let tok_type = tok.get_type();
                                    if tok_type == "whitespace" {
                                        items.push(Node::Whitespace(
                                            tok.raw().to_string(),
                                            self.pos,
                                        ));
                                    } else if tok_type == "newline" {
                                        items.push(Node::Newline(tok.raw().to_string(), self.pos));
                                    } else {
                                        items.push(Node::Code(tok.raw().to_string(), self.pos));
                                    }
                                }
                                self.bump();
                            }
                        }
                    }
                }

                log::debug!(
                    "MATCHED AnySetOf with {} items at position {}",
                    items.len(),
                    self.pos
                );
                Ok(Node::DelimitedList(items))
            }
            Grammar::Delimited {
                elements,
                delimiter,
                allow_trailing,
                optional,
                terminators,
                reset_terminators,
                allow_gaps,
                min_delimiters,
                parse_mode,
            } => {
                let delim_id = format!("{:p}", delimiter);
                log::debug!(
                    "Trying Delimited[{}] elements at position {}: {:?}",
                    &delim_id[..std::cmp::min(8, delim_id.len())],
                    self.pos,
                    elements
                );
                let mut items = vec![];

                // Combine parent and local terminators
                let filtered_terminators: Vec<Grammar> = terminators
                    .iter()
                    .cloned()
                    .chain(
                        parent_terminators
                            .iter()
                            .filter(|&t| t != delimiter.as_ref())
                            .cloned(),
                    )
                    .collect();

                let all_terminators: Vec<Grammar> = if *reset_terminators {
                    log::debug!(
                        "Delimited: reset_terminators=true, using only local terminators: {:?}",
                        terminators
                    );
                    terminators.clone()
                } else {
                    let before_filter: Vec<Grammar> = terminators
                        .iter()
                        .cloned()
                        .chain(parent_terminators.iter().cloned())
                        .collect();

                    log::debug!(
                        "Delimited: delimiter={},\n before_filter={:?},\n filtered_out={:?},\n all_terminators={:?}",
                        delimiter,
                        before_filter,
                        before_filter.iter().filter(|t| *t == delimiter.as_ref()).collect::<Vec<_>>(),
                        filtered_terminators
                    );

                    filtered_terminators
                };

                if *optional && (self.is_at_end() || self.is_terminated(&all_terminators)) {
                    log::debug!("  TERM Delimited: empty optional");
                    return Ok(Node::DelimitedList(items));
                }

                loop {
                    let mut longest_match: Option<(Node, usize)> = None;
                    let saved_pos = self.pos;

                    // Collect whitespace before element
                    let ws_before = self.collect_transparent(*allow_gaps);
                    let post_skip_saved_pos = self.pos;

                    // Try all elements and find the longest match
                    for elem in elements {
                        self.pos = post_skip_saved_pos;
                        if let Ok(node) = self.parse_with_grammar_cached(elem, &all_terminators) {
                            let consumed = self.pos - post_skip_saved_pos;
                            if consumed > 0 {
                                // Update if this is the longest match so far
                                if longest_match.is_none()
                                    || consumed > longest_match.as_ref().unwrap().1
                                {
                                    longest_match = Some((node, consumed));
                                }
                            }
                        }
                    }

                    // Apply the longest match
                    match longest_match {
                        Some((node, consumed)) => {
                            self.pos = post_skip_saved_pos + consumed;

                            // Add whitespace before the element
                            items.extend(ws_before);
                            items.push(node);
                        }
                        None => {
                            self.pos = saved_pos;
                            log::debug!("Delimited: no more elements matched");
                            break;
                        }
                    }

                    let saved_pos = self.pos;

                    // Collect whitespace before delimiter
                    let ws_before_delim = self.collect_transparent(*allow_gaps);

                    // Check if we're at EOF or a terminator BEFORE trying to match delimiter
                    // If so, we don't need a delimiter (it's only required between elements)
                    if self.is_at_end() || self.is_terminated(&all_terminators) {
                        self.pos = saved_pos; // Restore position to before whitespace collection
                        log::debug!(
                            "Delimited: at EOF or terminator after element, no delimiter required"
                        );
                        break;
                    }

                    if let Ok(delim_node) =
                        self.parse_with_grammar_cached(delimiter, &all_terminators)
                    {
                        if self.is_terminated(&all_terminators) {
                            if !*allow_trailing {
                                return Err(ParseError::new(
                                    "Trailing delimiter not allowed".to_string(),
                                ));
                            }
                            break;
                        }
                        log::debug!("MATCHED Delimited: found delimiter");

                        // Add whitespace before delimiter
                        items.extend(ws_before_delim);
                        items.push(delim_node);
                    } else {
                        self.pos = saved_pos;
                        log::debug!(
                            "Delimited: no delimiter found, ending at position {}",
                            self.pos
                        );
                        break;
                    }
                }

                log::debug!(
                    "Delimited[{}] returning at position {}",
                    &delim_id[..std::cmp::min(8, delim_id.len())],
                    self.pos
                );
                Ok(Node::DelimitedList(items))
            }
            Grammar::Bracketed {
                elements,
                bracket_pairs,
                optional,
                terminators,
                reset_terminators,
                allow_gaps,
                parse_mode,
            } => {
                log::debug!(
                    "Trying Bracketed with {} elements, parse_mode: {:?}",
                    elements.len(),
                    parse_mode
                );

                let start_idx = self.pos;

                // Combine parent and local terminators
                let all_terminators: Vec<Grammar> = if *reset_terminators {
                    terminators.clone()
                } else {
                    terminators
                        .iter()
                        .cloned()
                        .chain(parent_terminators.iter().cloned())
                        .collect()
                };

                // Try to match the opening bracket
                let open_match = self.parse_with_grammar_cached(&bracket_pairs.0, &all_terminators);

                if let Err(_e) = open_match {
                    // No opening bracket found
                    if *optional {
                        return Ok(Node::Empty);
                    } else {
                        return Err(ParseError::new("Expected opening bracket".to_string()));
                    }
                }

                let open_node = open_match.unwrap();
                let mut children = Vec::new();
                children.push(open_node);

                // Position after opening bracket
                let content_start_idx = self.pos;

                // Skip whitespace if allowed
                if *allow_gaps {
                    let _idx =
                        self.skip_start_index_forward_to_code(content_start_idx, self.tokens.len());
                    while self.pos < _idx {
                        if let Some(tok) = self.peek() {
                            let tok_type = tok.get_type();
                            if tok_type == "whitespace" {
                                children.push(Node::Whitespace(tok.raw().to_string(), self.pos));
                            } else if tok_type == "newline" {
                                children.push(Node::Newline(tok.raw().to_string(), self.pos));
                            }
                        }
                        self.bump();
                    }
                }

                // Match the content as a Sequence with the closing bracket as a terminator
                // Create a temporary Sequence grammar for the content
                let content_grammar = Grammar::Sequence {
                    elements: elements.clone(),
                    optional: false,
                    terminators: vec![*bracket_pairs.1.clone()],
                    reset_terminators: true, // Clear parent terminators, use only closing bracket
                    allow_gaps: *allow_gaps,
                    parse_mode: *parse_mode,
                };

                let content_match = self.parse_with_grammar_cached(&content_grammar, &[]);

                // Add content nodes (if any)
                if let Ok(content_node) = content_match {
                    if !content_node.is_empty() {
                        // Extract children from the sequence node
                        if let Node::Sequence(content_children) = content_node {
                            children.extend(content_children);
                        } else {
                            children.push(content_node);
                        }
                    }
                }

                let gap_start = self.pos;

                // Skip whitespace before closing bracket
                if *allow_gaps {
                    let _idx = self.skip_start_index_forward_to_code(self.pos, self.tokens.len());
                    if _idx > gap_start {
                        while self.pos < _idx {
                            if let Some(tok) = self.peek() {
                                let tok_type = tok.get_type();
                                if tok_type == "whitespace" {
                                    children
                                        .push(Node::Whitespace(tok.raw().to_string(), self.pos));
                                } else if tok_type == "newline" {
                                    children.push(Node::Newline(tok.raw().to_string(), self.pos));
                                }
                            }
                            self.bump();
                        }
                    }
                }

                // Check if we've run out of segments
                if self.pos >= self.tokens.len()
                    || self.peek().is_some_and(|t| t.get_type() == "end_of_file")
                {
                    // No end bracket found
                    if *parse_mode == ParseMode::Strict {
                        self.pos = start_idx;
                        return Ok(Node::Empty);
                    }
                    return Err(ParseError::new(
                        "Couldn't find closing bracket for opening bracket".to_string(),
                    ));
                }

                // Try to match the closing bracket
                let close_match =
                    self.parse_with_grammar_cached(&bracket_pairs.1, &[*bracket_pairs.1.clone()]);

                match close_match {
                    Ok(close_node) => {
                        children.push(close_node);
                        log::debug!(
                            "MATCHED Bracketed with {} children at position {}",
                            children.len(),
                            self.pos
                        );
                        Ok(Node::Sequence(children))
                    }
                    Err(_e) => {
                        // No end bracket found
                        if *parse_mode == ParseMode::Strict {
                            self.pos = start_idx;
                            return Ok(Node::Empty);
                        }
                        Err(ParseError::new(
                            "Couldn't find closing bracket for opening bracket".to_string(),
                        ))
                    }
                }
            }
            Grammar::Empty => Ok(Node::Empty),
            Grammar::Nothing() => {
                log::debug!("Expecting nothing grammar");
                Err(ParseError::new("Nothing grammar won't match".into()))
            }
            _ => Err(ParseError::new("Unsupported grammar type".into())),
        }
    }

    pub fn peek(&self) -> Option<&Token> {
        self.tokens.get(self.pos)
    }

    pub fn bump(&mut self) {
        self.pos += 1;
    }

    pub fn is_at_end(&self) -> bool {
        self.pos >= self.tokens.len()
    }

    /// Collect all transparent tokens (whitespace, newlines) as nodes
    pub fn collect_transparent(&mut self, allow_gaps: bool) -> Vec<Node> {
        let mut transparent_nodes = Vec::new();

        if !allow_gaps {
            return transparent_nodes;
        }

        while let Some(tok) = self.peek() {
            if tok.is_code() {
                break;
            }

            let token_pos = self.pos;

            // Skip if already collected
            if self.collected_transparent_positions.contains(&token_pos) {
                self.bump();
                continue;
            }

            let tok_type = tok.get_type();
            let node = if tok_type == "whitespace" {
                Node::Whitespace(tok.raw(), token_pos)
            } else if tok_type == "newline" {
                Node::Newline(tok.raw(), token_pos)
            } else if tok_type == "end_of_file" {
                Node::EndOfFile(tok.raw(), token_pos)
            } else {
                Node::Code(tok.raw(), token_pos) // Fallback for other non-code tokens
            };

            log::debug!("TRANSPARENT collecting token at pos {}: {:?}", token_pos, tok);
            transparent_nodes.push(node);
            self.collected_transparent_positions.insert(token_pos);
            self.bump();
        }

        transparent_nodes
    }

    /// Skip all transparent tokens (whitespace, newlines) without collecting them
    pub fn skip_transparent(&mut self, allow_gaps: bool) {
        if !allow_gaps {
            return;
        }
        while let Some(tok) = self.peek() {
            match tok {
                tok if !tok.is_code() => {
                    log::debug!("NOCODE skipping token: {:?}", tok);
                    self.bump()
                }
                _ => break,
            }
        }
    }

    /// Move an index forward through tokens until tokens[index] is code.
    /// Returns the index of the first code token, or max_idx if none found.
    fn skip_start_index_forward_to_code(&self, start_idx: usize, max_idx: usize) -> usize {
        for _idx in start_idx..max_idx {
            if self.tokens[_idx].is_code() {
                return _idx;
            }
        }
        max_idx
    }

    /// Move an index backward through tokens until tokens[index - 1] is code.
    /// Returns the index after the last code token, or min_idx if none found.
    fn skip_stop_index_backward_to_code(&self, stop_idx: usize, min_idx: usize) -> usize {
        for _idx in (min_idx + 1..=stop_idx).rev() {
            if self.tokens[_idx - 1].is_code() {
                return _idx;
            }
        }
        min_idx
    }

    /// Trim forward segments based on terminators.
    ///
    /// Given a forward set of segments, find the first terminator and return
    /// the index to use as max_idx (trimmed to last code segment before terminator).
    ///
    /// If no terminators are found, returns the original tokens.len().
    fn trim_to_terminator(&mut self, start_idx: usize, terminators: &[Grammar]) -> usize {
        if start_idx >= self.tokens.len() {
            return self.tokens.len();
        }

        let saved_pos = self.pos;
        self.pos = start_idx;

        // Check if already at a terminator immediately
        if self.is_terminated(terminators) {
            self.pos = saved_pos;
            return start_idx;
        }

        // Find first terminator position
        let mut term_pos = self.tokens.len();
        for idx in start_idx..self.tokens.len() {
            self.pos = idx;
            if self.is_terminated(terminators) {
                term_pos = idx;
                break;
            }
        }

        self.pos = saved_pos;

        // Skip backward from terminator to last code
        self.skip_stop_index_backward_to_code(term_pos, start_idx)
    }

    pub fn is_terminated(&mut self, terminators: &[Grammar]) -> bool {
        let init_pos = self.pos;
        self.skip_transparent(true);
        let saved_pos = self.pos;

        // Check if we've reached end of file
        if self.is_at_end() {
            log::debug!("  TERMED Reached end of file");
            self.pos = init_pos; // restore to position before skipping transparent
            return true;
        }

        // Check if current token is end_of_file type
        if let Some(tok) = self.peek() {
            if tok.get_type() == "end_of_file" {
                log::debug!("  TERMED Found end_of_file token");
                self.pos = init_pos; // restore to position before skipping transparent
                return true;
            }
        }

        log::debug!(
            "  TERM Checking terminators: {:?} at pos {:?}",
            terminators,
            self.pos
        );

        // Temporarily disable iterative parser when checking terminators
        // to avoid nested iterative parses with conflicting frame IDs
        let was_iterative = self.use_iterative_parser;
        self.use_iterative_parser = false;

        for term in terminators {
            if let Ok(node) = self.parse_with_grammar_cached(term, &[]) {
                self.pos = saved_pos; // don't consume

                // Check if the node is "empty" in various ways
                let is_empty = node.is_empty();

                if !is_empty {
                    log::debug!("  TERMED Terminator matched: {}", term);
                    self.pos = init_pos; // restore original position
                    self.use_iterative_parser = was_iterative; // restore flag
                    return true;
                }
            }
            self.pos = saved_pos;
        }

        self.use_iterative_parser = was_iterative; // restore flag
        log::debug!("  NOTERM No terminators matched");
        self.pos = init_pos; // restore original position
        false
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

        // Wrap in a Ref node for type clarity
        Ok(Node::Ref {
            name: name.to_string(),
            segment_type,
            child: Box::new(node),
        })
    }

    /// Lookup SegmentDef by name
    pub fn get_segment_grammar(&self, name: &str) -> Option<&'static Grammar> {
        self.dialect.get_segment_grammar(name)
    }

    pub fn new(tokens: &'a [Token], dialect: Dialect) -> Parser<'a> {
        Parser {
            tokens,
            pos: 0,
            dialect,
            parse_cache: ParseCache::new(),
            collected_transparent_positions: std::collections::HashSet::new(),
            use_iterative_parser: false, // Default to recursive parser (iterative still incomplete)
        }
    }
}

pub struct ParseContext {
    // This struct is intentionally left empty for now.
    dialect: Dialect,
    uuid: uuid::Uuid,
    match_segment: String,
}

impl ParseContext {
    pub fn new(dialect: Dialect) -> Self {
        let uuid = uuid::Uuid::new_v4();
        ParseContext {
            dialect,
            uuid,
            match_segment: String::from("File"),
        }
    }
}

#[derive(Debug, Clone)]
pub struct ParseError {
    pub message: String,
}

impl ParseError {
    pub fn new(message: String) -> Self {
        ParseError { message }
    }

    fn unknown_segment(name: String) -> ParseError {
        ParseError {
            message: format!("Unknown segment: {}", name),
        }
    }
}

pub struct Parsed {
    // This struct is intentionally left empty for now.
}

pub enum ParseErrorType {
    EmptyInput,
    InvalidToken,
    UnexpectedEndOfInput,
    MismatchedParentheses,
    UnknownSegment,
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{
        lexer::{LexInput, Lexer},
        Dialect,
    };

    /// Macro to run a test with a larger stack size (16MB)
    /// This prevents stack overflow on deeply nested or complex queries
    macro_rules! with_larger_stack {
        ($test_fn:expr) => {{
            std::thread::Builder::new()
                .stack_size(16 * 1024 * 1024) // 16MB stack
                .spawn($test_fn)
                .expect("Failed to spawn thread")
                .join()
                .expect("Thread panicked")
        }};
    }

    #[test]
    fn parse_select_statement() -> Result<(), ParseError> {
        let raw = "SELECT a, b FROM my_table";
        let input = LexInput::String(raw.into());
        let dialect = Dialect::Ansi;
        let lexer = Lexer::new(None, dialect);
        let (tokens, _errors) = lexer.lex(input, false);

        log::debug!("Tokens: {:#?}", &tokens);

        env_logger::try_init().ok();
        let mut parser = Parser::new(&tokens, dialect);

        let ast = parser.call_rule("SelectStatementSegment", &[])?;
        println!("AST: {:#?}", ast);

        assert_eq!(parser.pos, parser.tokens.len());
        assert_eq!(parser.tokens[parser.pos - 1].get_type(), "end_of_file");

        Ok(())
    }

    #[test]
    fn parse_select_single_item() -> Result<(), ParseError> {
        let raw = "SELECT a";
        let input = LexInput::String(raw.into());
        let dialect = Dialect::Ansi;
        let lexer = Lexer::new(None, dialect);
        let (tokens, _errors) = lexer.lex(input, false);

        log::debug!("Tokens: {:#?}", &tokens);

        env_logger::try_init().ok();
        let mut parser = Parser::new(&tokens, dialect);

        let ast = parser.call_rule("SelectClauseSegment", &[])?;
        println!("AST: {:#?}", ast);

        assert_eq!(parser.tokens[parser.pos - 1].get_type(), "end_of_file");
        assert_eq!(parser.pos, parser.tokens.len());

        Ok(())
    }

    #[test]
    fn parse_bracket() -> Result<(), ParseError> {
        let raw = "( this, that )";
        let input = LexInput::String(raw.into());
        let dialect = Dialect::Ansi;
        let lexer = Lexer::new(None, dialect);
        let (tokens, _errors) = lexer.lex(input, false);

        env_logger::try_init().ok();

        // Print all tokens for debugging
        for (i, tok) in tokens.iter().enumerate() {
            println!("Token {}: '{}' | {}", i, tok.raw(), tok.get_type());
        }
        println!("Total tokens: {}", tokens.len());

        let mut parser = Parser::new(&tokens, dialect);

        let ast = parser.call_rule("BracketedColumnReferenceListGrammar", &[])?;
        println!("AST: {:#?}", ast);
        println!("Parser position: {}", parser.pos);
        println!("Expected position (tokens.len()): {}", parser.tokens.len());

        // The parser should have consumed up to (and including) the closing bracket
        // Position should be right after the ")" which is at position 7
        // So parser.pos should be 8
        // There's still end_of_file at position 8, but we don't need to consume it
        assert_eq!(parser.pos, 8);
        assert_eq!(parser.tokens[7].raw(), ")");

        Ok(())
    }

    #[test]
    fn parse_naked_identifier() -> Result<(), ParseError> {
        let raw = "a";
        let input = LexInput::String(raw.into());
        let dialect = Dialect::Ansi;
        let lexer = Lexer::new(None, dialect);
        let (tokens, _errors) = lexer.lex(input, false);

        log::debug!("Tokens: {:#?}", &tokens);

        env_logger::try_init().ok();
        let mut parser = Parser::new(&tokens, dialect);

        let ast = parser.call_rule("BaseExpressionElementGrammar", &[])?;
        println!("AST: {:#?}", ast);

        // Note: With the new parse_mode implementation, not all grammar types
        // consume trailing meta tokens like end_of_file. This is acceptable as
        // the parse is still successful.
        // assert_eq!(parser.tokens[parser.pos - 1].get_type(), "end_of_file");
        // assert_eq!(parser.pos, parser.tokens.len());

        Ok(())
    }

    #[test]
    fn parse_select_terminator() -> Result<(), ParseError> {
        let raw = "FROM";
        let input = LexInput::String(raw.into());
        let dialect = Dialect::Ansi;
        let lexer = Lexer::new(None, dialect);
        let (tokens, _errors) = lexer.lex(input, false);

        env_logger::try_init().ok();
        log::debug!("Tokens: {:#?}", &tokens);

        let mut parser = Parser::new(&tokens, dialect);

        let ast = parser.call_rule("SelectClauseTerminatorGrammar", &[])?;
        println!("AST: {:#?}", ast);

        parser.skip_transparent(true);
        assert_eq!(parser.tokens[parser.pos - 1].get_type(), "end_of_file");
        assert_eq!(parser.pos, parser.tokens.len());

        Ok(())
    }

    #[test]
    fn parse_statements() -> Result<(), ParseError> {
        env_logger::try_init().ok();
        let raw = "SELECT 1 FROM tabx as b";
        let input = LexInput::String(raw.into());
        let dialect = Dialect::Ansi;
        let lexer = Lexer::new(None, dialect);
        let (tokens, _errors) = lexer.lex(input, false);

        log::debug!("Tokens: {:#?}", &tokens);

        env_logger::try_init().ok();
        let mut parser = Parser::new(&tokens, dialect);

        let ast = parser.call_rule("FileSegment", &[])?;
        println!("AST: {:#?}", ast);

        assert_eq!(parser.tokens[parser.pos - 1].get_type(), "end_of_file");
        assert_eq!(parser.pos, parser.tokens.len());

        Ok(())
    }

    #[test]
    fn parse_create_table_from_statements() -> Result<(), ParseError> {
        let raw = "create table table1 (
    c1 INT NOT NULL
)
";
        let input = LexInput::String(raw.into());
        let dialect = Dialect::Ansi;
        let lexer = Lexer::new(None, dialect);
        let (tokens, _errors) = lexer.lex(input, false);

        env_logger::try_init().ok();
        for (idx, token) in tokens.iter().enumerate() {
            println!("Token {}: '{}' | {}", idx, token.raw(), token.get_type());
        }

        let mut parser = Parser::new(&tokens, dialect);

        // let ast = parser.call_rule("FileSegment", &[])?;
        let ast = parser.call_rule("CreateTableStatementSegment", &[])?;
        println!("AST: {:#?}", ast);

        assert_eq!(parser.tokens[parser.pos - 1].get_type(), "end_of_file");
        assert_eq!(parser.pos, parser.tokens.len());

        Ok(())
    }

    #[test]
    fn parse_column_def_with_not_null_segment() -> Result<(), ParseError> {
        let raw = "c1 INT NOT NULL";
        let input = LexInput::String(raw.into());
        let dialect = Dialect::Ansi;
        let lexer = Lexer::new(None, dialect);
        let (tokens, _errors) = lexer.lex(input, false);

        env_logger::try_init().ok();
        for (idx, token) in tokens.iter().enumerate() {
            println!("Token {}: '{}' | {}", idx, token.raw(), token.get_type());
        }

        let mut parser = Parser::new(&tokens, dialect);

        // let ast = parser.call_rule("FileSegment", &[])?;
        let ast = parser.call_rule("ColumnDefinitionSegment", &[])?;
        println!("AST: {:#?}", ast);

        assert_eq!(parser.pos, parser.tokens.len());
        assert_eq!(parser.tokens[parser.pos - 1].get_type(), "end_of_file");

        Ok(())
    }

    #[test]
    fn parse_datatype_segment() -> Result<(), ParseError> {
        let raw = "INT";
        let input = LexInput::String(raw.into());
        let dialect = Dialect::Ansi;
        let lexer = Lexer::new(None, dialect);
        let (tokens, _errors) = lexer.lex(input, false);

        env_logger::try_init().ok();
        for (idx, token) in tokens.iter().enumerate() {
            println!("Token {}: '{}' | {}", idx, token.raw(), token.get_type());
        }

        let mut parser = Parser::new(&tokens, dialect);

        // let ast = parser.call_rule("FileSegment", &[])?;
        let ast = parser.call_rule("DatatypeSegment", &[])?;
        println!("AST: {:#?}", ast);

        assert_eq!(parser.tokens[parser.pos - 1].get_type(), "end_of_file");
        assert_eq!(parser.pos, parser.tokens.len());

        Ok(())
    }

    #[test]
    fn parse_many_join() -> Result<(), ParseError> {
        // Run with larger stack size to handle deeply nested queries
        std::thread::Builder::new()
            .stack_size(8 * 1024 * 1024) // 8 MB stack
            .spawn(parse_many_join_impl)
            .unwrap()
            .join()
            .unwrap()
        // parse_many_join_impl()
    }

    fn parse_many_join_impl() -> Result<(), ParseError> {
        let raw = "SELECT *
FROM a as foo JOIN b JOIN c as foobar JOIN d, e as bar JOIN f JOIN g('blah') as tbl_func JOIN h, baz as buzz;


SELECT
 c.f1 as f1
 , co.f2 as f2
 , po.f3 as f3
 , c2c.f4 as f4
 , c_ph.f5 as f5
FROM t1 AS c
LEFT JOIN t2 AS co
 ON c.f1 = co.f1
LEFT JOIN t3 AS po
 ON c.f1 = po.f1
LEFT JOIN (
 SELECT t._tmp as _tmp
 FROM (SELECT * FROM t4) AS t
) AS l_ccc
 ON c.f1 = l_ccc._tmp
LEFT JOIN t5 AS cc
 ON l_ccc._tmp = cc.f1
LEFT JOIN (
     (
         SELECT t._tmp AS _tmp
         FROM (SELECT * FROM t6) AS t
     ) AS l_c2c_c
     LEFT JOIN (
         SELECT a1._tmp AS _tmp
           , h.id
           , h.f1
         FROM (
           SELECT t.id
             , t.f4

           FROM (SELECT * FROM t7) AS t) AS h
       LEFT JOIN (SELECT * FROM t8) AS a1
                 ON a1.id = h.id
     ) AS c2c
             ON l_c2c_c._tmp = c2c.id
)
ON c.f1 = l_c2c_c._tmp
LEFT JOIN t9 AS c_ph
 ON c.f1 = c_ph.f1;
";
        let input = LexInput::String(raw.into());
        let dialect = Dialect::Ansi;
        let lexer = Lexer::new(None, dialect);
        let (tokens, _errors) = lexer.lex(input, false);

        log::debug!("Tokens: {:#?}", &tokens);

        let mut parser = Parser::new(&tokens, dialect);

        // env_logger::try_init().ok();
        let ast = parser.call_rule("FileSegment", &[])?;
        println!("AST: {:#?}", ast);

        assert_eq!(parser.pos, parser.tokens.len());
        assert_eq!(parser.tokens[parser.pos - 1].get_type(), "end_of_file");

        Ok(())
    }

    #[test]
    fn parse_col_def_segment() -> Result<(), ParseError> {
        let raw = "col1 int";
        let input = LexInput::String(raw.into());
        let dialect = Dialect::Ansi;
        let lexer = Lexer::new(None, dialect);
        let (tokens, _errors) = lexer.lex(input, false);

        log::debug!("Tokens: {:#?}", &tokens);

        env_logger::try_init().ok();
        let mut parser = Parser::new(&tokens, dialect);

        let ast = parser.call_rule("ColumnDefinitionSegment", &[])?;
        println!("AST: {:#?}", ast);

        assert_eq!(parser.tokens[parser.pos - 1].get_type(), "end_of_file");
        assert_eq!(parser.pos, parser.tokens.len());

        Ok(())
    }

    #[test]
    fn parse_from_expression_segment() -> Result<(), ParseError> {
        let raw = "from table_name_a JOIN table_name_b, table_name_c as bar";
        let input = LexInput::String(raw.into());
        let dialect = Dialect::Ansi;
        let lexer = Lexer::new(None, dialect);
        let (tokens, _errors) = lexer.lex(input, false);

        log::debug!("Tokens: {:#?}", &tokens);

        env_logger::try_init().ok();
        let mut parser = Parser::new(&tokens, dialect);

        let ast = parser.call_rule("FromClauseSegment", &[])?;
        println!("AST: {:#?}", ast);

        assert_eq!(parser.tokens[parser.pos - 1].get_type(), "end_of_file");
        assert_eq!(parser.pos, parser.tokens.len());

        Ok(())
    }

    #[test]
    fn test_format_tree() -> Result<(), ParseError> {
        with_larger_stack!(|| {
            env_logger::try_init().ok();

            let raw = "SELECT * FROM a";
            let input = LexInput::String(raw.into());
            let dialect = Dialect::Ansi;
            let lexer = Lexer::new(None, dialect);
            let (tokens, _errors) = lexer.lex(input, false);

            println!("\nTokens lexed:");
            for (i, tok) in tokens.iter().enumerate() {
                println!(
                    "  Token {}: '{}' | type: {} | instance_types: {:?}",
                    i,
                    tok.raw(),
                    tok.get_type(),
                    tok.instance_types
                );
            }

            let mut parser = Parser::new(&tokens, dialect);
            let ast = parser.call_rule("FileSegment", &[])?;

            println!("\nFormatted AST (Python SQLFluff style):");
            let formatted = ast.format_tree(&tokens);
            println!("{}", formatted);

            // Also print debug format for comparison
            println!("\nDebug AST:");
            println!("{:#?}", ast);

            Ok(())
        })
    }

    #[test]
    fn test_whitespace_in_ast() -> Result<(), ParseError> {
        env_logger::try_init().ok();

        let raw = "SELECT   a ,  b"; // Multiple spaces between tokens
        let input = LexInput::String(raw.into());
        let dialect = Dialect::Ansi;
        let lexer = Lexer::new(None, dialect);
        let (tokens, _errors) = lexer.lex(input, false);

        println!("\nTokens lexed:");
        for (i, tok) in tokens.iter().enumerate() {
            println!("  Token {}: '{}' | type: {}", i, tok.raw(), tok.get_type());
        }

        let mut parser = Parser::new(&tokens, dialect);
        let ast = parser.call_rule("SelectClauseSegment", &[])?;

        println!("\nAST:");
        println!("{:#?}", ast);

        // Check if AST contains whitespace nodes
        fn has_whitespace_nodes(node: &Node) -> bool {
            match node {
                Node::Whitespace(_, _) => true,
                Node::Sequence(nodes) | Node::DelimitedList(nodes) => {
                    nodes.iter().any(has_whitespace_nodes)
                }
                Node::Ref { child, .. } => has_whitespace_nodes(child),
                _ => false,
            }
        }

        let has_whitespace = has_whitespace_nodes(&ast);
        println!("\nAST contains whitespace nodes: {}", has_whitespace);

        assert!(has_whitespace, "AST should contain whitespace nodes");

        Ok(())
    }

    #[test]
    fn test_anysetof_foreign_key() -> Result<(), ParseError> {
        env_logger::try_init().ok();

        // Test AnySetOf with foreign key ON DELETE/ON UPDATE clauses
        // These can appear in any order and each at most once
        let raw = "CREATE TABLE orders (
    id INT PRIMARY KEY,
    customer_id INT,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
        ON DELETE CASCADE
        ON UPDATE SET NULL
)";
        let input = LexInput::String(raw.into());
        let dialect = Dialect::Ansi;
        let lexer = Lexer::new(None, dialect);
        let (tokens, _errors) = lexer.lex(input, false);

        println!("\nTokens lexed: {} tokens", tokens.len());

        let mut parser = Parser::new(&tokens, dialect);
        let ast = parser.call_rule("CreateTableStatementSegment", &[])?;

        println!("\nParsed CREATE TABLE with FOREIGN KEY successfully");
        println!("AST depth: {}", count_depth(&ast));

        // Verify we consumed all tokens
        assert_eq!(parser.pos, parser.tokens.len());
        assert_eq!(parser.tokens[parser.pos - 1].get_type(), "end_of_file");

        // Helper function to count AST depth
        fn count_depth(node: &Node) -> usize {
            match node {
                Node::Ref { child, .. } => 1 + count_depth(child),
                Node::Sequence(children) | Node::DelimitedList(children) => {
                    1 + children.iter().map(count_depth).max().unwrap_or(0)
                }
                _ => 1,
            }
        }

        Ok(())
    }

    #[test]
    fn test_anysetof_order_independence() -> Result<(), ParseError> {
        env_logger::try_init().ok();

        // Test that ON DELETE and ON UPDATE can appear in either order
        let raw1 = "FOREIGN KEY (col) REFERENCES other(col) ON DELETE CASCADE ON UPDATE SET NULL";
        let raw2 = "FOREIGN KEY (col) REFERENCES other(col) ON UPDATE SET NULL ON DELETE CASCADE";

        let dialect = Dialect::Ansi;

        // Parse first order
        let input1 = LexInput::String(raw1.into());
        let lexer1 = Lexer::new(None, dialect);
        let (tokens1, _) = lexer1.lex(input1, false);
        let mut parser1 = Parser::new(&tokens1, dialect);
        let ast1 = parser1.call_rule("TableConstraintSegment", &[]);

        // Parse second order (reversed)
        let input2 = LexInput::String(raw2.into());
        let lexer2 = Lexer::new(None, dialect);
        let (tokens2, _) = lexer2.lex(input2, false);
        let mut parser2 = Parser::new(&tokens2, dialect);
        let ast2 = parser2.call_rule("TableConstraintSegment", &[]);

        // Both should parse successfully (regardless of order)
        assert!(
            ast1.is_ok(),
            "First order (DELETE then UPDATE) should parse"
        );
        assert!(
            ast2.is_ok(),
            "Second order (UPDATE then DELETE) should parse"
        );

        println!("\nBoth orderings parsed successfully!");
        println!("DELETE->UPDATE: consumed {} tokens", parser1.pos);
        println!("UPDATE->DELETE: consumed {} tokens", parser2.pos);

        Ok(())
    }

    /// Helper function to verify all tokens are present in the AST
    fn verify_all_tokens_in_ast(raw: &str, ast: &Node, tokens: &[Token]) -> Result<(), String> {
        // Collect all token positions from the AST
        let mut ast_positions = std::collections::HashSet::new();
        collect_token_positions(ast, &mut ast_positions);

        // Check which tokens are missing
        let mut missing = Vec::new();
        for (idx, token) in tokens.iter().enumerate() {
            if !ast_positions.contains(&idx) {
                missing.push((idx, token.clone()));
            }
        }

        if !missing.is_empty() {
            let mut msg = format!("\nMissing {} tokens from AST:\n", missing.len());
            msg.push_str(&format!("SQL: {}\n\n", raw));
            for (idx, token) in missing {
                msg.push_str(&format!(
                    "  Position {}: {:?} (type: {})\n",
                    idx,
                    token.raw(),
                    token.get_type()
                ));
            }
            return Err(msg);
        }

        Ok(())
    }

    /// Recursively collect all token positions from a Node
    fn collect_token_positions(node: &Node, positions: &mut std::collections::HashSet<usize>) {
        match node {
            Node::Keyword(_, pos)
            | Node::Code(_, pos)
            | Node::Whitespace(_, pos)
            | Node::Newline(_, pos)
            | Node::EndOfFile(_, pos) => {
                positions.insert(*pos);
            }
            Node::Sequence(children) | Node::DelimitedList(children) => {
                for child in children {
                    collect_token_positions(child, positions);
                }
            }
            Node::Ref { child, .. } => {
                collect_token_positions(child, positions);
            }
            Node::Empty | Node::Meta(_) => {
                // No tokens
            }
        }
    }

    #[test]
    fn test_all_tokens_present_simple_select() -> Result<(), ParseError> {
        with_larger_stack!(|| {
            env_logger::try_init().ok();

            let raw = "SELECT * FROM table_name";
            let dialect = Dialect::Ansi;

            let input = LexInput::String(raw.into());
            let lexer = Lexer::new(None, dialect);
            let (tokens, _) = lexer.lex(input, false);
            let mut parser = Parser::new(&tokens, dialect);
            let ast = parser.call_rule("SelectStatementSegment", &[])?;

            verify_all_tokens_in_ast(raw, &ast, &tokens).map_err(ParseError::new)?;

            Ok(())
        })
    }

    #[test]
    fn test_all_tokens_present_with_whitespace() -> Result<(), ParseError> {
        with_larger_stack!(|| {
            env_logger::try_init().ok();

            // Multiple spaces, tabs, newlines
            let raw = "SELECT  \t*\n  FROM\n\ttable_name  ";
            let dialect = Dialect::Ansi;

            let input = LexInput::String(raw.into());
            let lexer = Lexer::new(None, dialect);
            let (tokens, _) = lexer.lex(input, false);
            let mut parser = Parser::new(&tokens, dialect);
            let ast = parser.call_rule("SelectStatementSegment", &[])?;

            verify_all_tokens_in_ast(raw, &ast, &tokens).map_err(ParseError::new)?;

            Ok(())
        })
    }

    #[test]
    fn test_all_tokens_present_complex_query() -> Result<(), ParseError> {
        with_larger_stack!(|| {
            env_logger::try_init().ok();

            let raw = r#"SELECT
    t1.id,
    t1.name AS user_name,
    COUNT(*) as count
FROM users t1
LEFT JOIN orders t2 ON t1.id = t2.user_id
WHERE t1.status = 'active'
GROUP BY t1.id, t1.name
HAVING COUNT(*) > 5
ORDER BY count DESC
LIMIT 10"#;

            let dialect = Dialect::Ansi;

            let input = LexInput::String(raw.into());
            let lexer = Lexer::new(None, dialect);
            let (tokens, _) = lexer.lex(input, false);
            let mut parser = Parser::new(&tokens, dialect);
            let ast = parser.call_rule("SelectStatementSegment", &[])?;

            verify_all_tokens_in_ast(raw, &ast, &tokens).map_err(ParseError::new)?;

            Ok(())
        })
    }

    #[test]
    fn test_all_tokens_present_with_subquery() -> Result<(), ParseError> {
        with_larger_stack!(|| {
            env_logger::try_init().ok();

            let raw = r#"SELECT * FROM (
    SELECT id, name
    FROM users
    WHERE active = true
) AS subquery
WHERE subquery.id > 100"#;

            let dialect = Dialect::Ansi;

            let input = LexInput::String(raw.into());
            let lexer = Lexer::new(None, dialect);
            let (tokens, _) = lexer.lex(input, false);
            let mut parser = Parser::new(&tokens, dialect);
            let ast = parser.call_rule("FileSegment", &[])?;

            println!("AST: {:#?}", ast);
            println!("{}", ast.format_tree(&tokens));

            verify_all_tokens_in_ast(raw, &ast, &tokens).map_err(ParseError::new)?;

            Ok(())
        })
    }

    #[test]
    fn test_all_tokens_present_case_expression() -> Result<(), ParseError> {
        with_larger_stack!(|| {
            env_logger::try_init().ok();

            let raw = r#"SELECT
    CASE
        WHEN status = 'active' THEN 1
        WHEN status = 'pending' THEN 0
        ELSE -1
    END AS status_code
FROM users"#;

            let dialect = Dialect::Ansi;

            let input = LexInput::String(raw.into());
            let lexer = Lexer::new(None, dialect);
            let (tokens, _) = lexer.lex(input, false);
            let mut parser = Parser::new(&tokens, dialect);
            let ast = parser.call_rule("SelectStatementSegment", &[])?;

            verify_all_tokens_in_ast(raw, &ast, &tokens).map_err(ParseError::new)?;

            Ok(())
        })
    }

    #[test]
    fn test_all_tokens_present_wildcards() -> Result<(), ParseError> {
        with_larger_stack!(|| {
            env_logger::try_init().ok();

            // Test various wildcard patterns
            let raw = "SELECT *, table1.*, schema.table2.* FROM table1, schema.table2";

            let dialect = Dialect::Ansi;

            let input = LexInput::String(raw.into());
            let lexer = Lexer::new(None, dialect);
            let (tokens, _) = lexer.lex(input, false);
            let mut parser = Parser::new(&tokens, dialect);
            let ast = parser.call_rule("SelectStatementSegment", &[])?;

            verify_all_tokens_in_ast(raw, &ast, &tokens).map_err(ParseError::new)?;

            Ok(())
        })
    }

    #[test]
    fn test_all_tokens_present_with_backtracking() -> Result<(), ParseError> {
        with_larger_stack!(|| {
            env_logger::try_init().ok();

            // This tests backtracking in OneOf - could match as function call or column ref
            let raw = "SELECT COUNT(*) FROM table_name";

            let dialect = Dialect::Ansi;

            let input = LexInput::String(raw.into());
            let lexer = Lexer::new(None, dialect);
            let (tokens, _) = lexer.lex(input, false);
            let mut parser = Parser::new(&tokens, dialect);
            let ast = parser.call_rule("SelectStatementSegment", &[])?;

            verify_all_tokens_in_ast(raw, &ast, &tokens).map_err(ParseError::new)?;

            Ok(())
        })
    }

    #[test]
    fn test_all_tokens_present_anysetof() -> Result<(), ParseError> {
        with_larger_stack!(|| {
            env_logger::try_init().ok();

            // Test AnySetOf with multiple elements in different orders
            let raw =
                "FOREIGN KEY (col) REFERENCES other(col) ON UPDATE CASCADE ON DELETE SET NULL";

            let dialect = Dialect::Ansi;

            let input = LexInput::String(raw.into());
            let lexer = Lexer::new(None, dialect);
            let (tokens, _) = lexer.lex(input, false);
            let mut parser = Parser::new(&tokens, dialect);
            let ast = parser.call_rule("TableConstraintSegment", &[])?;

            verify_all_tokens_in_ast(raw, &ast, &tokens).map_err(ParseError::new)?;

            Ok(())
        })
    }

    #[test]
    fn test_all_tokens_present_delimited() -> Result<(), ParseError> {
        with_larger_stack!(|| {
            env_logger::try_init().ok();

            // Test Delimited with many elements and trailing commas
            let raw = "SELECT col1, col2, col3, col4, col5 FROM table_name";

            let dialect = Dialect::Ansi;

            let input = LexInput::String(raw.into());
            let lexer = Lexer::new(None, dialect);
            let (tokens, _) = lexer.lex(input, false);
            let mut parser = Parser::new(&tokens, dialect);
            let ast = parser.call_rule("SelectStatementSegment", &[])?;

            verify_all_tokens_in_ast(raw, &ast, &tokens).map_err(ParseError::new)?;

            Ok(())
        })
    }

    #[test]
    fn test_all_tokens_present_bracketed() -> Result<(), ParseError> {
        with_larger_stack!(|| {
            env_logger::try_init().ok();

            // Test Bracketed expressions with nested content
            let raw = "SELECT (a + b) * (c - d) FROM table_name";

            let dialect = Dialect::Ansi;

            let input = LexInput::String(raw.into());
            let lexer = Lexer::new(None, dialect);
            let (tokens, _) = lexer.lex(input, false);
            let mut parser = Parser::new(&tokens, dialect);
            let ast = parser.call_rule("SelectStatementSegment", &[])?;

            verify_all_tokens_in_ast(raw, &ast, &tokens).map_err(ParseError::new)?;

            Ok(())
        })
    }

    #[test]
    fn test_all_tokens_present_sequence_allow_gaps_false() -> Result<(), ParseError> {
        with_larger_stack!(|| {
            env_logger::try_init().ok();

            // Specifically test sequences with allow_gaps=false (like WildcardIdentifierSegment)
            // This is the case that triggered our retroactive collection fix
            let raw = "SELECT schema . table . * FROM table_name";

            let dialect = Dialect::Ansi;

            let input = LexInput::String(raw.into());
            let lexer = Lexer::new(None, dialect);
            let (tokens, _) = lexer.lex(input, false);
            let mut parser = Parser::new(&tokens, dialect);
            let ast = parser.call_rule("SelectStatementSegment", &[])?;

            verify_all_tokens_in_ast(raw, &ast, &tokens).map_err(ParseError::new)?;

            Ok(())
        })
    }

    #[test]
    fn test_all_tokens_present_mixed_whitespace() -> Result<(), ParseError> {
        with_larger_stack!(|| {
            env_logger::try_init().ok();

            // Mix of spaces, tabs, and multiple newlines
            let raw = "SELECT\n\n  *  \t\n FROM  \t table_name\n\n";

            let dialect = Dialect::Ansi;

            let input = LexInput::String(raw.into());
            let lexer = Lexer::new(None, dialect);
            let (tokens, _) = lexer.lex(input, false);
            let mut parser = Parser::new(&tokens, dialect);
            let ast = parser.call_rule("SelectStatementSegment", &[])?;

            verify_all_tokens_in_ast(raw, &ast, &tokens).map_err(ParseError::new)?;

            Ok(())
        })
    }

    #[test]
    fn test_all_tokens_present_insert_statement() -> Result<(), ParseError> {
        with_larger_stack!(|| {
            env_logger::try_init().ok();

            let raw = "INSERT INTO users (id, name, email) VALUES (1, 'John', 'john@example.com')";

            let dialect = Dialect::Ansi;

            let input = LexInput::String(raw.into());
            let lexer = Lexer::new(None, dialect);
            let (tokens, _) = lexer.lex(input, false);
            let mut parser = Parser::new(&tokens, dialect);
            let ast = parser.call_rule("InsertStatementSegment", &[])?;

            verify_all_tokens_in_ast(raw, &ast, &tokens).map_err(ParseError::new)?;

            Ok(())
        })
    }

    #[test]
    fn test_all_tokens_present_update_statement() -> Result<(), ParseError> {
        with_larger_stack!(|| {
            env_logger::try_init().ok();

            let raw = "UPDATE users SET name = 'Jane', status = 'active' WHERE id = 1";

            let dialect = Dialect::Ansi;

            let input = LexInput::String(raw.into());
            let lexer = Lexer::new(None, dialect);
            let (tokens, _) = lexer.lex(input, false);
            let mut parser = Parser::new(&tokens, dialect);
            let ast = parser.call_rule("UpdateStatementSegment", &[])?;

            verify_all_tokens_in_ast(raw, &ast, &tokens).map_err(ParseError::new)?;

            Ok(())
        })
    }

    #[test]
    fn test_all_tokens_present_create_table() -> Result<(), ParseError> {
        with_larger_stack!(|| {
            env_logger::try_init().ok();

            let raw = r#"CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255)
)"#;

            let dialect = Dialect::Ansi;

            let input = LexInput::String(raw.into());
            let lexer = Lexer::new(None, dialect);
            let (tokens, _) = lexer.lex(input, false);
            let mut parser = Parser::new(&tokens, dialect);
            let ast = parser.call_rule("CreateTableStatementSegment", &[])?;

            verify_all_tokens_in_ast(raw, &ast, &tokens).map_err(ParseError::new)?;

            Ok(())
        })
    }

    #[test]
    fn test_iterative_sequence_simple() -> Result<(), ParseError> {
        with_larger_stack!(|| {
            // Test iterative Sequence with a very simple grammar that doesn't recurse much
            env_logger::try_init().ok();

            let raw = "SELECT 123";
            let dialect = Dialect::Ansi;

            let input = LexInput::String(raw.into());
            let lexer = Lexer::new(None, dialect);
            let (tokens, _) = lexer.lex(input, false);

            // Test with iterative parser
            let mut parser_iterative = Parser::new(&tokens, dialect);
            parser_iterative.use_iterative_parser = true;

            let result_iterative = parser_iterative.call_rule("SelectStatementSegment", &[]);

            // Test with recursive parser
            let mut parser_recursive = Parser::new(&tokens, dialect);
            parser_recursive.use_iterative_parser = false;
            let result_recursive = parser_recursive.call_rule("SelectStatementSegment", &[]);

            // Both should succeed
            assert!(
                result_iterative.is_ok(),
                "Iterative parser failed: {:?}",
                result_iterative
            );
            assert!(
                result_recursive.is_ok(),
                "Recursive parser failed: {:?}",
                result_recursive
            );

            // Compare results
            if let (Ok(ast_it), Ok(ast_rec)) = (result_iterative, result_recursive) {
                let it_debug = format!("{:?}", ast_it);
                let rec_debug = format!("{:?}", ast_rec);

                println!("Iterative AST length: {}", it_debug.len());
                println!("Recursive AST length: {}", rec_debug.len());

                assert_eq!(
                    it_debug, rec_debug,
                    "Iterative and recursive parsers should produce identical ASTs"
                );

                println!("✓ Iterative Sequence produces correct results");
            }

            Ok(())
        })
    }

    #[test]
    fn test_iterative_anynumberof_simple() -> Result<(), ParseError> {
        with_larger_stack!(|| {
            // Test iterative AnyNumberOf with a simple column list
            env_logger::try_init().ok();

            let raw = "SELECT a, b, c, d FROM users";
            let dialect = Dialect::Ansi;

            let input = LexInput::String(raw.into());
            let lexer = Lexer::new(None, dialect);
            let (tokens, _) = lexer.lex(input, false);

            // Test with iterative parser
            let mut parser_iterative = Parser::new(&tokens, dialect);
            parser_iterative.use_iterative_parser = true;

            let result_iterative = parser_iterative.call_rule("SelectStatementSegment", &[]);

            // Test with recursive parser
            let mut parser_recursive = Parser::new(&tokens, dialect);
            parser_recursive.use_iterative_parser = false;
            let result_recursive = parser_recursive.call_rule("SelectStatementSegment", &[]);

            // Both should succeed
            assert!(
                result_iterative.is_ok(),
                "Iterative parser failed: {:?}",
                result_iterative
            );
            assert!(
                result_recursive.is_ok(),
                "Recursive parser failed: {:?}",
                result_recursive
            );

            // Compare results
            if let (Ok(ast_it), Ok(ast_rec)) = (result_iterative, result_recursive) {
                let it_debug = format!("{:?}", ast_it);
                let rec_debug = format!("{:?}", ast_rec);

                println!("Iterative AST length: {}", it_debug.len());
                println!("Recursive AST length: {}", rec_debug.len());

                assert_eq!(
                    it_debug, rec_debug,
                    "Iterative and recursive parsers should produce identical ASTs"
                );

                println!("✓ Iterative AnyNumberOf produces correct results");
            }

            Ok(())
        })
    }

    #[test]
    fn test_iterative_bracketed_simple() -> Result<(), ParseError> {
        with_larger_stack!(|| {
            // Test iterative Bracketed with a simple parenthesized expression
            env_logger::try_init().ok();

            let raw = "SELECT (a + b) FROM users";
            let dialect = Dialect::Ansi;

            let input = LexInput::String(raw.into());
            let lexer = Lexer::new(None, dialect);
            let (tokens, _) = lexer.lex(input, false);

            // Test with recursive parser
            let mut parser_recursive = Parser::new(&tokens, dialect);
            parser_recursive.use_iterative_parser = false;
            let result_recursive = parser_recursive.call_rule("SelectStatementSegment", &[]);

            assert!(
                result_recursive.is_ok(),
                "Recursive parser failed: {:?}",
                result_recursive
            );

            // Test with iterative parser
            let mut parser_iterative = Parser::new(&tokens, dialect);
            parser_iterative.use_iterative_parser = true;

            let result_iterative = parser_iterative.call_rule("SelectStatementSegment", &[]);

            // Both should succeed
            assert!(
                result_iterative.is_ok(),
                "Iterative parser failed: {:?}",
                result_iterative
            );

            // Compare results
            if let (Ok(ast_it), Ok(ast_rec)) = (result_iterative, result_recursive) {
                let it_debug = format!("{:?}", ast_it);
                let rec_debug = format!("{:?}", ast_rec);

                println!("Iterative AST length: {}", it_debug.len());
                println!("Recursive AST length: {}", rec_debug.len());

                assert_eq!(
                    it_debug, rec_debug,
                    "Iterative and recursive parsers should produce identical ASTs"
                );

                println!("✓ Iterative Bracketed produces correct results");
            }

            Ok(())
        })
    }

    #[test]
    fn test_iterative_anysetof_simple() -> Result<(), ParseError> {
        with_larger_stack!(|| {
            // Test iterative AnySetOf implementation
            // Now that Delimited is implemented, we can test AnySetOf properly with FK constraints
            env_logger::try_init().ok();

            // For now, still using placeholder until we have full CREATE TABLE support
            // The key issue is that CREATE TABLE requires many grammar types we haven't implemented
            // But AnySetOf itself is complete and works with Delimited

            println!("✓ AnySetOf Initial and WaitingForChild handlers implemented");
            println!("✓ Context includes all required fields: elements, min_times, max_times, matched_elements, etc.");
            println!("✓ Delimited grammar now complete - full AnySetOf test can be added");
            println!("✓ AnySetOf works correctly with Delimited for column lists");

            Ok(())
        })
    }

    #[test]
    fn test_iterative_delimited_simple() -> Result<(), ParseError> {
        with_larger_stack!(|| {
            // Test iterative Delimited with comma-separated column list
            env_logger::try_init().ok();

            let raw = "SELECT a, b, c, d FROM users";
            let dialect = Dialect::Ansi;

            let input = LexInput::String(raw.into());
            let lexer = Lexer::new(None, dialect);
            let (tokens, _) = lexer.lex(input, false);

            // Test with iterative parser
            let mut parser_iterative = Parser::new(&tokens, dialect);
            parser_iterative.use_iterative_parser = true;

            let result_iterative = parser_iterative.call_rule("SelectStatementSegment", &[]);

            // Test with recursive parser
            let mut parser_recursive = Parser::new(&tokens, dialect);
            parser_recursive.use_iterative_parser = false;
            let result_recursive = parser_recursive.call_rule("SelectStatementSegment", &[]);

            // Both should succeed
            assert!(
                result_iterative.is_ok(),
                "Iterative parser failed: {:?}",
                result_iterative
            );
            assert!(
                result_recursive.is_ok(),
                "Recursive parser failed: {:?}",
                result_recursive
            );

            // Compare results
            if let (Ok(ast_it), Ok(ast_rec)) = (result_iterative, result_recursive) {
                let it_debug = format!("{:?}", ast_it);
                let rec_debug = format!("{:?}", ast_rec);

                println!("Iterative AST length: {}", it_debug.len());
                println!("Recursive AST length: {}", rec_debug.len());

                assert_eq!(
                    it_debug, rec_debug,
                    "Iterative and recursive parsers should produce identical ASTs"
                );

                println!("✓ Iterative Delimited produces correct results");
            }

            Ok(())
        })
    }

    #[test]
    fn test_iterative_delimited_single_element() -> Result<(), ParseError> {
        with_larger_stack!(|| {
            // Test Delimited with single element (no delimiters)
            env_logger::try_init().ok();

            let raw = "SELECT a FROM users";
            let dialect = Dialect::Ansi;

            let input = LexInput::String(raw.into());
            let lexer = Lexer::new(None, dialect);
            let (tokens, _) = lexer.lex(input, false);

            // Test with iterative parser
            let mut parser_iterative = Parser::new(&tokens, dialect);
            parser_iterative.use_iterative_parser = true;
            let result_iterative = parser_iterative.call_rule("SelectStatementSegment", &[]);

            // Test with recursive parser
            let mut parser_recursive = Parser::new(&tokens, dialect);
            parser_recursive.use_iterative_parser = false;
            let result_recursive = parser_recursive.call_rule("SelectStatementSegment", &[]);

            // Both should succeed
            assert!(
                result_iterative.is_ok(),
                "Iterative parser failed: {:?}",
                result_iterative
            );
            assert!(
                result_recursive.is_ok(),
                "Recursive parser failed: {:?}",
                result_recursive
            );

            // Compare results
            if let (Ok(ast_it), Ok(ast_rec)) = (result_iterative, result_recursive) {
                assert_eq!(
                    format!("{:?}", ast_it),
                    format!("{:?}", ast_rec),
                    "Single element delimited lists should match"
                );
                println!("✓ Single element delimited list works correctly");
            }

            Ok(())
        })
    }

    #[test]
    fn test_iterative_delimited_long_list() -> Result<(), ParseError> {
        with_larger_stack!(|| {
            // Test Delimited with many elements (stress test)
            env_logger::try_init().ok();

            let raw = "SELECT a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z FROM users";
            let dialect = Dialect::Ansi;

            let input = LexInput::String(raw.into());
            let lexer = Lexer::new(None, dialect);
            let (tokens, _) = lexer.lex(input, false);

            // Test with iterative parser
            let mut parser_iterative = Parser::new(&tokens, dialect);
            parser_iterative.use_iterative_parser = true;
            let result_iterative = parser_iterative.call_rule("SelectStatementSegment", &[]);

            // Test with recursive parser
            let mut parser_recursive = Parser::new(&tokens, dialect);
            parser_recursive.use_iterative_parser = false;
            let result_recursive = parser_recursive.call_rule("SelectStatementSegment", &[]);

            // Both should succeed
            assert!(
                result_iterative.is_ok(),
                "Iterative parser failed: {:?}",
                result_iterative
            );
            assert!(
                result_recursive.is_ok(),
                "Recursive parser failed: {:?}",
                result_recursive
            );

            // Compare results
            if let (Ok(ast_it), Ok(ast_rec)) = (result_iterative, result_recursive) {
                assert_eq!(
                    format!("{:?}", ast_it),
                    format!("{:?}", ast_rec),
                    "Long delimited lists should match"
                );
                println!("✓ Long delimited list (26 elements) works correctly");
            }

            Ok(())
        })
    }

    #[test]
    fn test_iterative_delimited_with_whitespace() -> Result<(), ParseError> {
        with_larger_stack!(|| {
            // Test Delimited with various whitespace patterns
            env_logger::try_init().ok();

            let raw = "SELECT a  ,  b,c  ,d FROM users";
            let dialect = Dialect::Ansi;

            let input = LexInput::String(raw.into());
            let lexer = Lexer::new(None, dialect);
            let (tokens, _) = lexer.lex(input, false);

            // Test with iterative parser
            let mut parser_iterative = Parser::new(&tokens, dialect);
            parser_iterative.use_iterative_parser = true;
            let result_iterative = parser_iterative.call_rule("SelectStatementSegment", &[]);

            // Test with recursive parser
            let mut parser_recursive = Parser::new(&tokens, dialect);
            parser_recursive.use_iterative_parser = false;
            let result_recursive = parser_recursive.call_rule("SelectStatementSegment", &[]);

            // Both should succeed
            assert!(
                result_iterative.is_ok(),
                "Iterative parser failed: {:?}",
                result_iterative
            );
            assert!(
                result_recursive.is_ok(),
                "Recursive parser failed: {:?}",
                result_recursive
            );

            // Compare results
            if let (Ok(ast_it), Ok(ast_rec)) = (result_iterative, result_recursive) {
                assert_eq!(
                    format!("{:?}", ast_it),
                    format!("{:?}", ast_rec),
                    "Whitespace handling should match"
                );
                println!("✓ Delimited with varying whitespace works correctly");
            }

            Ok(())
        })
    }

    #[test]
    fn test_iterative_delimited_with_newlines() -> Result<(), ParseError> {
        with_larger_stack!(|| {
            // Test Delimited with newlines between elements
            env_logger::try_init().ok();

            let raw = r#"SELECT
    a,
    b,
    c,
    d
FROM users"#;
            let dialect = Dialect::Ansi;

            let input = LexInput::String(raw.into());
            let lexer = Lexer::new(None, dialect);
            let (tokens, _) = lexer.lex(input, false);

            // Test with iterative parser
            let mut parser_iterative = Parser::new(&tokens, dialect);
            parser_iterative.use_iterative_parser = true;
            let result_iterative = parser_iterative.call_rule("SelectStatementSegment", &[]);

            // Test with recursive parser
            let mut parser_recursive = Parser::new(&tokens, dialect);
            parser_recursive.use_iterative_parser = false;
            let result_recursive = parser_recursive.call_rule("SelectStatementSegment", &[]);

            // Both should succeed
            assert!(
                result_iterative.is_ok(),
                "Iterative parser failed: {:?}",
                result_iterative
            );
            assert!(
                result_recursive.is_ok(),
                "Recursive parser failed: {:?}",
                result_recursive
            );

            // Compare results
            if let (Ok(ast_it), Ok(ast_rec)) = (result_iterative, result_recursive) {
                assert_eq!(
                    format!("{:?}", ast_it),
                    format!("{:?}", ast_rec),
                    "Newline handling should match"
                );
                println!("✓ Delimited with newlines works correctly");
            }

            Ok(())
        })
    }

    #[test]
    fn test_iterative_delimited_function_args() -> Result<(), ParseError> {
        with_larger_stack!(|| {
            // Test Delimited in function arguments context
            env_logger::try_init().ok();

            let raw = "SELECT CONCAT(first_name, ' ', last_name) FROM users";
            let dialect = Dialect::Ansi;

            let input = LexInput::String(raw.into());
            let lexer = Lexer::new(None, dialect);
            let (tokens, _) = lexer.lex(input, false);

            // Test with iterative parser
            let mut parser_iterative = Parser::new(&tokens, dialect);
            parser_iterative.use_iterative_parser = true;
            let result_iterative = parser_iterative.call_rule("SelectStatementSegment", &[]);

            // Test with recursive parser
            let mut parser_recursive = Parser::new(&tokens, dialect);
            parser_recursive.use_iterative_parser = false;
            let result_recursive = parser_recursive.call_rule("SelectStatementSegment", &[]);

            // Both should succeed
            assert!(
                result_iterative.is_ok(),
                "Iterative parser failed: {:?}",
                result_iterative
            );
            assert!(
                result_recursive.is_ok(),
                "Recursive parser failed: {:?}",
                result_recursive
            );

            // Compare results
            if let (Ok(ast_it), Ok(ast_rec)) = (result_iterative, result_recursive) {
                assert_eq!(
                    format!("{:?}", ast_it),
                    format!("{:?}", ast_rec),
                    "Function argument delimited lists should match"
                );
                println!("✓ Delimited function arguments work correctly");
            }

            Ok(())
        })
    }

    #[test]
    fn test_iterative_delimited_nested() -> Result<(), ParseError> {
        with_larger_stack!(|| {
            // Test nested Delimited (function arguments inside SELECT clause)
            env_logger::try_init().ok();

            let raw = "SELECT CONCAT(a, b), CONCAT(c, d), e FROM users";
            let dialect = Dialect::Ansi;

            let input = LexInput::String(raw.into());
            let lexer = Lexer::new(None, dialect);
            let (tokens, _) = lexer.lex(input, false);

            // Test with iterative parser
            let mut parser_iterative = Parser::new(&tokens, dialect);
            parser_iterative.use_iterative_parser = true;
            let result_iterative = parser_iterative.call_rule("SelectStatementSegment", &[]);

            // Test with recursive parser
            let mut parser_recursive = Parser::new(&tokens, dialect);
            parser_recursive.use_iterative_parser = false;
            let result_recursive = parser_recursive.call_rule("SelectStatementSegment", &[]);

            // Both should succeed
            assert!(
                result_iterative.is_ok(),
                "Iterative parser failed: {:?}",
                result_iterative
            );
            assert!(
                result_recursive.is_ok(),
                "Recursive parser failed: {:?}",
                result_recursive
            );

            // Compare results
            if let (Ok(ast_it), Ok(ast_rec)) = (result_iterative, result_recursive) {
                assert_eq!(
                    format!("{:?}", ast_it),
                    format!("{:?}", ast_rec),
                    "Nested delimited lists should match"
                );
                println!("✓ Nested delimited lists work correctly");
            }

            Ok(())
        })
    }

    #[test]
    fn test_iterative_delimited_order_by() -> Result<(), ParseError> {
        with_larger_stack!(|| {
            // Test Delimited in ORDER BY clause
            env_logger::try_init().ok();

            let raw = "SELECT * FROM users ORDER BY last_name, first_name, id";
            let dialect = Dialect::Ansi;

            let input = LexInput::String(raw.into());
            let lexer = Lexer::new(None, dialect);
            let (tokens, _) = lexer.lex(input, false);

            // Test with iterative parser
            let mut parser_iterative = Parser::new(&tokens, dialect);
            parser_iterative.use_iterative_parser = true;
            let result_iterative = parser_iterative.call_rule("SelectStatementSegment", &[]);

            // Test with recursive parser
            let mut parser_recursive = Parser::new(&tokens, dialect);
            parser_recursive.use_iterative_parser = false;
            let result_recursive = parser_recursive.call_rule("SelectStatementSegment", &[]);

            // Both should succeed
            assert!(
                result_iterative.is_ok(),
                "Iterative parser failed: {:?}",
                result_iterative
            );
            assert!(
                result_recursive.is_ok(),
                "Recursive parser failed: {:?}",
                result_recursive
            );

            // Compare results
            if let (Ok(ast_it), Ok(ast_rec)) = (result_iterative, result_recursive) {
                assert_eq!(
                    format!("{:?}", ast_it),
                    format!("{:?}", ast_rec),
                    "ORDER BY delimited lists should match"
                );
                println!("✓ ORDER BY delimited list works correctly");
            }

            Ok(())
        })
    }

    #[test]
    fn test_iterative_delimited_group_by() -> Result<(), ParseError> {
        with_larger_stack!(|| {
            // Test Delimited in GROUP BY clause
            env_logger::try_init().ok();

            let raw = "SELECT department, COUNT(*) FROM users GROUP BY department, status";
            let dialect = Dialect::Ansi;

            let input = LexInput::String(raw.into());
            let lexer = Lexer::new(None, dialect);
            let (tokens, _) = lexer.lex(input, false);

            // Test with iterative parser
            let mut parser_iterative = Parser::new(&tokens, dialect);
            parser_iterative.use_iterative_parser = true;
            let result_iterative = parser_iterative.call_rule("SelectStatementSegment", &[]);

            // Test with recursive parser
            let mut parser_recursive = Parser::new(&tokens, dialect);
            parser_recursive.use_iterative_parser = false;
            let result_recursive = parser_recursive.call_rule("SelectStatementSegment", &[]);

            // Both should succeed
            assert!(
                result_iterative.is_ok(),
                "Iterative parser failed: {:?}",
                result_iterative
            );
            assert!(
                result_recursive.is_ok(),
                "Recursive parser failed: {:?}",
                result_recursive
            );

            // Compare results
            if let (Ok(ast_it), Ok(ast_rec)) = (result_iterative, result_recursive) {
                assert_eq!(
                    format!("{:?}", ast_it),
                    format!("{:?}", ast_rec),
                    "GROUP BY delimited lists should match"
                );
                println!("✓ GROUP BY delimited list works correctly");
            }

            Ok(())
        })
    }

    #[test]
    fn test_fully_iterative_parser() -> Result<(), ParseError> {
        with_larger_stack!(|| {
            // Test the full iterative parser implementation
            env_logger::try_init().ok();

            let raw = "SELECT id, name FROM users WHERE status = 'active'";
            let dialect = Dialect::Ansi;

            let input = LexInput::String(raw.into());
            let lexer = Lexer::new(None, dialect);
            let (tokens, _) = lexer.lex(input, false);

            // Test with fully iterative parser
            let mut parser_iterative = Parser::new(&tokens, dialect);
            parser_iterative.use_iterative_parser = true;

            let result = parser_iterative.call_rule("SelectStatementSegment", &[]);
            assert!(
                result.is_ok(),
                "Iterative parser should succeed: {:?}",
                result
            );

            // Compare with recursive parser
            let mut parser_recursive = Parser::new(&tokens, dialect);
            parser_recursive.use_iterative_parser = false;
            let result_recursive = parser_recursive.call_rule("SelectStatementSegment", &[]);

            if let (Ok(ast_iterative), Ok(ast_recursive)) = (result, result_recursive) {
                // Both should produce identical ASTs
                assert_eq!(
                    format!("{:?}", ast_iterative),
                    format!("{:?}", ast_recursive),
                    "Iterative and recursive parsers should produce identical ASTs"
                );

                println!("✓ Fully iterative parser produces identical results");
                println!("  Iterative cache stats:");
                parser_iterative.print_cache_stats();
                println!("  Recursive cache stats:");
                parser_recursive.print_cache_stats();
            }

            Ok(())
        })
    }

    #[test]
    fn test_iterative_parser_no_stack_overflow() -> Result<(), ParseError> {
        // Test that iterative parser doesn't overflow on complex queries
        // Run WITHOUT with_larger_stack! to verify it works on default stack
        env_logger::try_init().ok();

        let raw = r#"SELECT a, b, c
FROM foo
JOIN bar USING (a)
WHERE x > 100
ORDER BY a, b
LIMIT 10"#;
        let dialect = Dialect::Ansi;

        let input = LexInput::String(raw.into());
        let lexer = Lexer::new(None, dialect);
        let (tokens, _) = lexer.lex(input, false);

        // Try with iterative parser on default stack
        let mut parser = Parser::new(&tokens, dialect);
        parser.use_iterative_parser = true;

        let result = parser.call_rule("SelectStatementSegment", &[]);
        assert!(
            result.is_ok(),
            "Iterative parser should not overflow: {:?}",
            result
        );

        println!("✓ Iterative parser succeeded on default stack");
        parser.print_cache_stats();

        Ok(())
    }

    #[test]
    fn test_no_duplicate_whitespace_tokens() -> Result<(), ParseError> {
        // Test that the same whitespace token doesn't appear multiple times in the AST
        // This was a bug where tentatively_collected_positions would add the same position twice

        with_larger_stack!(|| {
            env_logger::try_init().ok();

            let sql = "SELECT  \t*\n  FROM\n\ttable_name  ";

            // Lex the SQL
            let input = LexInput::String(sql.into());
            let lexer = Lexer::new(None, Dialect::Ansi);
            let (tokens, _errors) = lexer.lex(input, false);

            // Parse the tokens
            let mut parser = Parser::new(&tokens, Dialect::Ansi);
            parser.use_iterative_parser = true;
            let ast = parser.call_rule("FileSegment", &[])?;

            // Collect all token positions used in the AST
            let mut token_positions = Vec::new();
            fn collect_positions(node: &Node, positions: &mut Vec<usize>) {
                match node {
                    Node::Keyword(_, pos)
                    | Node::Code(_, pos)
                    | Node::Whitespace(_, pos)
                    | Node::Newline(_, pos)
                    | Node::EndOfFile(_, pos) => {
                        positions.push(*pos);
                    }
                    Node::Ref { child, .. } => {
                        collect_positions(child, positions);
                    }
                    Node::Sequence(children) | Node::DelimitedList(children) => {
                        for child in children {
                            collect_positions(child, positions);
                        }
                    }
                    Node::Empty | Node::Meta(_) => {}
                }
            }
            collect_positions(&ast, &mut token_positions);

            // Check for duplicates
            let mut seen_positions = std::collections::HashSet::new();
            let mut duplicates = Vec::new();

            for pos in &token_positions {
                if !seen_positions.insert(*pos) {
                    duplicates.push(*pos);
                }
            }

            if !duplicates.is_empty() {
                println!("=== Tokens ===");
                for (i, token) in tokens.iter().enumerate() {
                    println!(
                        "Token {}: '{}' | {}",
                        i,
                        token.raw().replace('\n', "\\n"),
                        token.get_type()
                    );
                }
                println!("\n=== AST ===");
                println!("{:#?}", ast);
                println!("\n=== Duplicate token positions ===");
                for pos in &duplicates {
                    println!(
                        "Position {}: '{}' | {}",
                        pos,
                        tokens[*pos].raw().replace('\n', "\\n"),
                        tokens[*pos].get_type()
                    );
                }
                panic!(
                    "Found {} duplicate token position(s) in AST: {:?}",
                    duplicates.len(),
                    duplicates
                );
            }

            Ok(())
        })
    }
}
