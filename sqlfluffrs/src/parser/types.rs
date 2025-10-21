//! Core types for the parser: Grammar, Node, ParseMode

use std::fmt::Display;
use std::hash::{Hash, Hasher};

use crate::token::Token;
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
            token_types: self.token_types.union(&other.token_types).cloned().collect(),
        }
    }

    /// Check if this hint can match the given token
    /// Returns true if the token's raw value OR type matches, or if hint is empty (can't determine)
    pub fn can_match_token(&self, raw_upper: &str, token_type: &str) -> bool {
        // Empty hint means "complex - can't determine", so return true (must try it)
        if self.raw_values.is_empty() && self.token_types.is_empty() {
            return true;
        }

        // Check raw value match
        if !self.raw_values.is_empty() && self.raw_values.contains(raw_upper) {
            return true;
        }

        // Check type match
        if !self.token_types.is_empty() && self.token_types.contains(token_type) {
            return true;
        }

        false
    }

    /// Check if this hint can match the given token (using a set of types)
    /// This matches Python's behavior where it checks intersection of hint types with token's class_types
    /// Returns true if the token's raw value OR any type matches, or if hint is empty (can't determine)
    pub fn can_match_token_types(&self, raw_upper: &str, token_types: &std::collections::HashSet<String>) -> bool {
        // Empty hint means "complex - can't determine", so return true (must try it)
        if self.raw_values.is_empty() && self.token_types.is_empty() {
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
    pub fn is_empty(&self) -> bool {
        self.raw_values.is_empty() && self.token_types.is_empty()
    }
}

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
        exclude: Option<Box<Grammar>>,
        optional: bool,
        terminators: Vec<Grammar>,
        reset_terminators: bool,
        allow_gaps: bool,
        parse_mode: ParseMode,
    },
    OneOf {
        elements: Vec<Grammar>,
        exclude: Option<Box<Grammar>>,
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
        exclude: Option<Box<Grammar>>,
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
    StringParser {
        template: &'static str,
        token_type: &'static str,
        raw_class: &'static str,
        optional: bool,
    },
    MultiStringParser {
        templates: Vec<&'static str>,
        token_type: &'static str,
        raw_class: &'static str,
        optional: bool,
    },
    TypedParser {
        template: &'static str,
        token_type: &'static str,
        raw_class: &'static str,
        optional: bool,
    },
    RegexParser {
        template: &'static str,
        token_type: &'static str,
        raw_class: &'static str,
        optional: bool,
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
            _ => ParseMode::Strict,
        }
    }

    /// Check if this grammar is optional.
    pub fn is_optional(&self) -> bool {
        match self {
            Grammar::AnyNumberOf {
                optional,
                min_times,
                ..
            } => *optional || *min_times == 0,
            Grammar::OneOf { optional, .. } => *optional,
            Grammar::AnySetOf {
                optional,
                min_times,
                ..
            } => *optional || *min_times == 0,
            Grammar::Sequence { optional, .. } => *optional,
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

    /// Get a SimpleHint for this grammar to enable fast pruning of OneOf alternatives.
    /// Returns None if the grammar is too complex to analyze.
    /// Based on Python SQLFluff's simple() method.
    ///
    /// The dialect parameter is needed to resolve Ref grammars.
    /// The crumbs parameter tracks visited Refs to prevent infinite recursion.
    pub fn simple_hint_with_dialect(
        &self,
        dialect: Option<&crate::dialect::Dialect>,
        crumbs: &std::collections::HashSet<String>,
    ) -> Option<SimpleHint> {
        match self {
            // Direct token matchers - can hint by type
            Grammar::Token { token_type } => Some(SimpleHint::from_type(token_type)),

            Grammar::TypedParser { template, .. } => Some(SimpleHint::from_type(template)),

            // RegexParser: Python returns None (doesn't support simple hints)
            // This is because regex matching is too complex to represent as simple raw/type hints
            Grammar::RegexParser { .. } => None,

            // String matchers - can hint by raw value
            Grammar::StringParser { template, .. } => Some(SimpleHint::from_raw(template)),

            Grammar::MultiStringParser { templates, .. } => {
                let raws: Vec<&str> = templates.iter().map(|s| s.as_ref()).collect();
                Some(SimpleHint::from_raws(&raws))
            }

            // Ref: Resolve to referenced grammar (with recursion protection)
            Grammar::Ref { name, .. } => {
                // Check for self-reference
                if crumbs.contains(*name) {
                    log::debug!("Self-referential Ref detected: {}", name);
                    return None;
                }

                // Try to resolve using dialect
                if let Some(d) = dialect {
                    if let Some(grammar) = d.get_segment_grammar(name) {
                        // Add this ref to crumbs and recurse
                        let mut new_crumbs = crumbs.clone();
                        new_crumbs.insert(name.to_string());
                        return grammar.simple_hint_with_dialect(Some(d), &new_crumbs);
                    }
                }

                // No dialect or couldn't resolve
                None
            }

            // Meta: Invisible to matching - return empty hint so it doesn't block pruning
            // Grammar::Meta(_) => Some(SimpleHint::empty()),

            // Sequence: accumulate hints from optional elements until first non-optional
            // Python logic: union all optional elements, then return when hitting first required
            Grammar::Sequence { elements, .. } => {
                let mut combined = SimpleHint::empty();
                for elem in elements {
                    // Skip Meta elements - they're invisible
                    if matches!(elem, Grammar::Meta(_)) {
                        continue;
                    }

                    match elem.simple_hint_with_dialect(dialect, crumbs) {
                        None => return None, // Complex element = whole sequence is complex
                        Some(hint) => {
                            combined = combined.union(&hint);
                            if !elem.is_optional() {
                                // Found first required element, return accumulated hints
                                return Some(combined);
                            }
                        }
                    }
                }
                // All elements are optional (or no elements)
                Some(combined)
            }

            // OneOf: union of all alternatives' hints
            // Python logic: if ANY element returns None, the whole OneOf returns None
            Grammar::OneOf { elements, .. } => {
                let mut combined = SimpleHint::empty();
                for elem in elements {
                    match elem.simple_hint_with_dialect(dialect, crumbs) {
                        Some(hint) => combined = combined.union(&hint),
                        None => return None, // One complex element = whole OneOf is complex
                    }
                }
                Some(combined)
            }

            // AnyNumberOf: union of all elements (like OneOf)
            // Python logic: ALL elements must be simple, or return None
            Grammar::AnyNumberOf { elements, .. } => {
                let mut combined = SimpleHint::empty();
                for elem in elements {
                    match elem.simple_hint_with_dialect(dialect, crumbs) {
                        Some(hint) => combined = combined.union(&hint),
                        None => return None, // One complex element = whole AnyNumberOf is complex
                    }
                }
                Some(combined)
            }

            // AnySetOf: union of all elements (same as AnyNumberOf)
            Grammar::AnySetOf { elements, .. } => {
                let mut combined = SimpleHint::empty();
                for elem in elements {
                    match elem.simple_hint_with_dialect(dialect, crumbs) {
                        Some(hint) => combined = combined.union(&hint),
                        None => return None,
                    }
                }
                Some(combined)
            }

            // Delimited: union of all element alternatives
            // Note: Delimiter is NOT part of the simple hint (it terminates, doesn't start)
            Grammar::Delimited { elements, .. } => {
                let mut combined = SimpleHint::empty();
                for elem in elements {
                    match elem.simple_hint_with_dialect(dialect, crumbs) {
                        Some(hint) => combined = combined.union(&hint),
                        None => return None,
                    }
                }
                Some(combined)
            }

            // Bracketed: starts with opening bracket
            Grammar::Bracketed { bracket_pairs, .. } => {
                bracket_pairs.0.simple_hint_with_dialect(dialect, crumbs)
            }

            // Nothing/Empty: matches nothing, so empty hint is correct
            Grammar::Nothing() | Grammar::Empty => Some(SimpleHint::empty()),

            // Anything, Missing, Indent, Dedent: Can't determine
            _ => None,
        }
    }

    /// Convenience method that calls simple_hint_with_dialect with empty crumbs
    pub fn simple_hint(&self) -> Option<SimpleHint> {
        self.simple_hint_with_dialect(None, &std::collections::HashSet::new())
    }
}

// Implement Hash for Grammar
impl Hash for Grammar {
    fn hash<H: Hasher>(&self, state: &mut H) {
        std::mem::discriminant(self).hash(state);
        match self {
            Grammar::Ref {
                name,
                optional,
                allow_gaps,
                ..
            } => {
                name.hash(state);
                optional.hash(state);
                allow_gaps.hash(state);
            }
            Grammar::StringParser { template, .. } => template.hash(state),
            Grammar::MultiStringParser { templates, .. } => templates.hash(state),
            Grammar::TypedParser { template, .. } => template.hash(state),
            Grammar::RegexParser { template, .. } => template.hash(state),
            Grammar::Sequence {
                elements,
                optional,
                allow_gaps,
                parse_mode,
                ..
            } => {
                elements.hash(state);
                optional.hash(state);
                allow_gaps.hash(state);
                parse_mode.hash(state);
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
                parse_mode.hash(state);
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
                parse_mode.hash(state);
            }
            Grammar::AnySetOf {
                elements,
                optional,
                allow_gaps,
                parse_mode,
                ..
            } => {
                elements.hash(state);
                optional.hash(state);
                allow_gaps.hash(state);
                parse_mode.hash(state);
            }
            Grammar::Delimited {
                elements,
                optional,
                allow_gaps,
                delimiter,
                allow_trailing,
                terminators,
                min_delimiters,
                parse_mode,
                ..
            } => {
                elements.hash(state);
                optional.hash(state);
                allow_gaps.hash(state);
                delimiter.hash(state);
                allow_trailing.hash(state);
                terminators.hash(state);
                min_delimiters.hash(state);
                parse_mode.hash(state);
            }
            Grammar::Bracketed {
                elements,
                optional,
                allow_gaps,
                parse_mode,
                ..
            } => {
                elements.hash(state);
                optional.hash(state);
                allow_gaps.hash(state);
                parse_mode.hash(state);
            }
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
impl PartialEq for Grammar {
    fn eq(&self, other: &Self) -> bool {
        match (self, other) {
            (
                Grammar::Sequence {
                    elements: e1,
                    optional: o1,
                    allow_gaps: g1,
                    parse_mode: pm1,
                    ..
                },
                Grammar::Sequence {
                    elements: e2,
                    optional: o2,
                    allow_gaps: g2,
                    parse_mode: pm2,
                    ..
                },
            ) => e1 == e2 && o1 == o2 && g1 == g2 && pm1 == pm2,
            (
                Grammar::AnyNumberOf {
                    elements: e1,
                    optional: o1,
                    allow_gaps: g1,
                    parse_mode: pm1,
                    ..
                },
                Grammar::AnyNumberOf {
                    elements: e2,
                    optional: o2,
                    allow_gaps: g2,
                    parse_mode: pm2,
                    ..
                },
            ) => e1 == e2 && o1 == o2 && g1 == g2 && pm1 == pm2,
            (
                Grammar::OneOf {
                    elements: e1,
                    optional: o1,
                    allow_gaps: g1,
                    parse_mode: pm1,
                    ..
                },
                Grammar::OneOf {
                    elements: e2,
                    optional: o2,
                    allow_gaps: g2,
                    parse_mode: pm2,
                    ..
                },
            ) => e1 == e2 && o1 == o2 && g1 == g2 && pm1 == pm2,
            (
                Grammar::AnySetOf {
                    elements: e1,
                    optional: o1,
                    allow_gaps: g1,
                    parse_mode: pm1,
                    ..
                },
                Grammar::AnySetOf {
                    elements: e2,
                    optional: o2,
                    allow_gaps: g2,
                    parse_mode: pm2,
                    ..
                },
            ) => e1 == e2 && o1 == o2 && g1 == g2 && pm1 == pm2,
            (
                Grammar::Delimited {
                    elements: e1,
                    optional: o1,
                    allow_gaps: g1,
                    delimiter: d1,
                    allow_trailing: at1,
                    terminators: t1,
                    min_delimiters: md1,
                    parse_mode: pm1,
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
                    parse_mode: pm2,
                    ..
                },
            ) => {
                e1 == e2
                    && o1 == o2
                    && g1 == g2
                    && d1 == d2
                    && at1 == at2
                    && t1 == t2
                    && md1 == md2
                    && pm1 == pm2
            }
            (
                Grammar::Bracketed {
                    elements: e1,
                    optional: o1,
                    allow_gaps: g1,
                    parse_mode: pm1,
                    ..
                },
                Grammar::Bracketed {
                    elements: e2,
                    optional: o2,
                    allow_gaps: g2,
                    parse_mode: pm2,
                    ..
                },
            ) => e1 == e2 && o1 == o2 && g1 == g2 && pm1 == pm2,
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
                    ..
                },
                Grammar::StringParser {
                    template: t2,
                    token_type: tt2,
                    optional: o2,
                    ..
                },
            ) => template == t2 && token_type == tt2 && optional == o2,
            (
                Grammar::MultiStringParser {
                    templates,
                    token_type,
                    optional,
                    ..
                },
                Grammar::MultiStringParser {
                    templates: t2,
                    token_type: tt2,
                    optional: o2,
                    ..
                },
            ) => templates == t2 && token_type == tt2 && optional == o2,
            (
                Grammar::TypedParser {
                    template,
                    token_type,
                    optional,
                    ..
                },
                Grammar::TypedParser {
                    template: t2,
                    token_type: tt2,
                    optional: o2,
                    ..
                },
            ) => template == t2 && token_type == tt2 && optional == o2,
            (
                Grammar::RegexParser {
                    template,
                    token_type,
                    optional,
                    anti_template,
                    ..
                },
                Grammar::RegexParser {
                    template: t2,
                    token_type: tt2,
                    optional: o2,
                    anti_template: at2,
                    ..
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
    /// Whitespace tokens (spaces, tabs)
    Whitespace(String, usize),

    /// Newline tokens
    Newline(String, usize),

    /// End of file marker
    EndOfFile(String, usize),

    /// Generic token
    Token(String, String, usize), // (type, raw, position)

    /// Unparsable segment (in GREEDY mode when tokens don't match)
    Unparsable(String, Vec<Node>), // (expected message, children)

    /// A sequence of child nodes (used for Grammar::Sequence)
    Sequence(Vec<Node>),

    /// A list of elements separated by commas
    DelimitedList(Vec<Node>),

    /// A bracketed section (content between brackets)
    Bracketed(Vec<Node>),

    /// A reference to another segment (wraps its AST)
    Ref {
        name: String,
        segment_type: Option<String>,
        child: Box<Node>,
    },

    /// Used when an optional part didn't match
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
            Node::Bracketed(items) => {
                items.is_empty()
                    || items
                        .iter()
                        .all(|n| matches!(n, Node::Empty | Node::Meta(_)))
            }
            _ => false,
        }
    }

    /// Get the token index from this node if it's a Token/Whitespace/Newline/EndOfFile.
    /// Returns None for complex nodes like Sequence, Ref, etc.
    pub fn get_token_idx(&self) -> Option<usize> {
        match self {
            Node::Token(_, _, idx)
            | Node::Whitespace(_, idx)
            | Node::Newline(_, idx)
            | Node::EndOfFile(_, idx) => Some(*idx),
            _ => None,
        }
    }

    /// Format the AST to mirror Python SQLFluff's parse output format.
    pub fn format_tree(&self, tokens: &[Token]) -> String {
        let mut output = String::new();
        let mut eof_nodes = Vec::new();

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
        eof_nodes: &mut Vec<(usize, usize)>,
    ) -> usize {
        let indent = "    ".repeat(depth);

        match self {
            Node::Whitespace(_, idx) | Node::Newline(_, idx) | Node::Token(_, _, idx) => {
                if let Some(token) = tokens.get(*idx) {
                    output.push_str(&token.stringify(depth, 4, false));
                }
                *idx + 1
            }

            Node::EndOfFile(_, idx) => {
                eof_nodes.push((depth, *idx));
                *idx + 1
            }

            Node::Unparsable(expected, children) => {
                output.push_str(&format!("{}[unparsable] expected: {}\n", indent, expected));
                let mut last_idx = token_idx;
                for child in children {
                    last_idx =
                        child.format_tree_impl(tokens, output, depth + 1, last_idx, eof_nodes);
                }
                last_idx
            }

            Node::Meta(name) => {
                let (line, pos) = if let Some(token) = tokens.get(token_idx) {
                    if let Some(pos_marker) = &token.pos_marker {
                        pos_marker.source_position()
                    } else {
                        (0, 0)
                    }
                } else if token_idx > 0 && token_idx <= tokens.len() {
                    if let Some(token) = tokens.get(token_idx - 1) {
                        if let Some(pos_marker) = &token.pos_marker {
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
                    (0, 0)
                };

                output.push_str(&format!(
                    "[L:{:3}, P:{:3}]      |{}[META] {}:\n",
                    line, pos, indent, name,
                ));
                token_idx
            }

            Node::Ref {
                name,
                segment_type,
                child,
            } => {
                let is_grammar_rule = name.ends_with("Grammar");
                let is_single_token = matches!(
                    child.as_ref(),
                    Node::Whitespace(_, _) | Node::Newline(_, _) | Node::EndOfFile(_, _)
                );
                let is_transparent = is_grammar_rule || is_single_token;

                let mut current_idx = token_idx;

                if is_transparent {
                    current_idx =
                        child.format_tree_impl(tokens, output, depth, current_idx, eof_nodes);
                } else {
                    let display_name = if let Some(ref seg_type) = segment_type {
                        seg_type.clone()
                    } else {
                        simplify_segment_name(name)
                    };

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

                    current_idx =
                        child.format_tree_impl(tokens, output, depth + 1, current_idx, eof_nodes);
                }
                current_idx
            }

            Node::Sequence(children)
            | Node::DelimitedList(children)
            | Node::Bracketed(children) => {
                let mut current_idx = token_idx;
                let mut eof_indices = Vec::new();

                for (i, child) in children.iter().enumerate() {
                    if matches!(child, Node::EndOfFile(_, _)) {
                        eof_indices.push(i);
                    } else if !child.is_empty() {
                        current_idx =
                            child.format_tree_impl(tokens, output, depth, current_idx, eof_nodes);
                    }
                }

                for &i in &eof_indices {
                    current_idx =
                        children[i].format_tree_impl(tokens, output, depth, current_idx, eof_nodes);
                }

                current_idx
            }
            Node::Empty => token_idx,
        }
    }

    fn find_first_token_idx(&self) -> Option<usize> {
        match self {
            Node::Whitespace(_, idx)
            | Node::Newline(_, idx)
            | Node::EndOfFile(_, idx)
            | Node::Token(_, _, idx) => Some(*idx),

            Node::Ref { child, .. } => child.find_first_token_idx(),

            Node::Sequence(children)
            | Node::DelimitedList(children)
            | Node::Bracketed(children)
            | Node::Unparsable(_, children) => {
                children.iter().find_map(|c| c.find_first_token_idx())
            }

            Node::Meta(_) | Node::Empty => None,
        }
    }

    /// Check if this node represents code (not whitespace or meta)
    pub fn is_code(&self) -> bool {
        match self {
            // Whitespace and newlines are not code
            Node::Whitespace(_, _) | Node::Newline(_, _) => false,

            // EndOfFile and Meta are not code
            Node::EndOfFile(_, _) | Node::Meta(_) => false,

            // Empty is not code
            Node::Empty => false,

            // Token depends on its type
            Node::Token(token_type, _, _) => {
                !matches!(token_type.as_str(), "whitespace" | "newline")
            }

            // Unparsable segments contain code
            Node::Unparsable(_, _) => true,

            // Container nodes: check if they contain any code
            Node::Sequence(children)
            | Node::DelimitedList(children)
            | Node::Bracketed(children) => children.iter().any(|child| child.is_code()),

            // Ref nodes: delegate to child
            Node::Ref { child, .. } => child.is_code(),
        }
    }

    /// Check if this node is whitespace (spaces, tabs, newlines)
    pub fn is_whitespace(&self) -> bool {
        match self {
            Node::Whitespace(_, _) | Node::Newline(_, _) => true,
            Node::Token(token_type, _, _) => {
                matches!(token_type.as_str(), "whitespace" | "newline")
            }
            _ => false,
        }
    }

    /// Check if this node is a meta node (indent, dedent, etc.)
    pub fn is_meta(&self) -> bool {
        matches!(self, Node::Meta(_))
    }

    /// Check if this node should be included in code-only serialization
    /// This matches Python's behavior for `code_only=True`
    pub fn should_include_in_code_only(&self) -> bool {
        self.is_code() && !self.is_meta()
    }

    /// Get the type of this node based on its variant and token information
    /// This helps determine what kind of segment it represents
    pub fn get_type(&self, tokens: &[Token]) -> Option<String> {
        match self {
            Node::Whitespace(_, _) => Some("whitespace".to_string()),
            Node::Newline(_, _) => Some("newline".to_string()),
            Node::EndOfFile(_, _) => Some("end_of_file".to_string()),
            Node::Token(token_type, _, _) => Some(token_type.clone()),
            Node::Unparsable(_, _) => Some("unparsable".to_string()),
            Node::Ref { segment_type, .. } => segment_type.clone(),
            Node::Sequence(_) => Some("sequence".to_string()),
            Node::DelimitedList(_) => Some("delimited_list".to_string()),
            Node::Bracketed(_) => Some("bracketed".to_string()),
            Node::Meta(name) => Some(format!("meta_{}", name)),
            Node::Empty => None,
        }
    }

    /// Get all class types from the token, if this node references a token
    pub fn get_class_types(&self, tokens: &[Token]) -> Vec<String> {
        match self {
            Node::Token(token_type, _, idx) => {
                if let Some(token) = tokens.get(*idx) {
                    let mut v = vec![token_type.clone()];
                    v.extend(token.class_types.iter().cloned());
                    v
                } else {
                    Vec::new()
                }
            }
            Node::Ref { child, .. } => child.get_class_types(tokens),
            _ => Vec::new(),
        }
    }

    /// Check if this node or its token has a specific type
    pub fn has_type(&self, type_name: &str, tokens: &[Token]) -> bool {
        if let Some(node_type) = self.get_type(tokens) {
            if node_type == type_name {
                return true;
            }
        }

        // Also check class types
        self.get_class_types(tokens)
            .contains(&type_name.to_string())
    }
}

fn simplify_segment_name(name: &str) -> String {
    let name = name
        .strip_suffix("Segment")
        .or_else(|| name.strip_suffix("Grammar"))
        .unwrap_or(name);

    camel_to_snake(name)
}

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

#[derive(Debug, Clone)]
pub struct ParseError {
    pub message: String,
}

impl ParseError {
    pub fn new(message: String) -> Self {
        ParseError { message }
    }

    pub fn unknown_segment(name: String) -> ParseError {
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

/// Context for parsing operations
pub struct ParseContext {
    dialect: crate::dialect::Dialect,
    uuid: uuid::Uuid,
    match_segment: String,
}

impl ParseContext {
    pub fn new(dialect: crate::dialect::Dialect) -> Self {
        let uuid = uuid::Uuid::new_v4();
        ParseContext {
            dialect,
            uuid,
            match_segment: String::from("File"),
        }
    }
}
