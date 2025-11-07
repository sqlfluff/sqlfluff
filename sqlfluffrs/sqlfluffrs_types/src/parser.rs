use std::fmt::Display;
use std::hash::{Hash, Hasher};
use std::sync::Arc;

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
        elements: Vec<Arc<Grammar>>,
        optional: bool,
        terminators: Vec<Arc<Grammar>>,
        reset_terminators: bool,
        allow_gaps: bool,
        parse_mode: ParseMode,
        simple_hint: Option<SimpleHint>,
    },
    AnyNumberOf {
        elements: Vec<Arc<Grammar>>,
        min_times: usize,
        max_times: Option<usize>,
        max_times_per_element: Option<usize>,
        exclude: Option<Box<Arc<Grammar>>>,
        optional: bool,
        terminators: Vec<Arc<Grammar>>,
        reset_terminators: bool,
        allow_gaps: bool,
        parse_mode: ParseMode,
        simple_hint: Option<SimpleHint>,
    },
    OneOf {
        elements: Vec<Arc<Grammar>>,
        exclude: Option<Box<Arc<Grammar>>>,
        optional: bool,
        terminators: Vec<Arc<Grammar>>,
        reset_terminators: bool,
        allow_gaps: bool,
        parse_mode: ParseMode,
        simple_hint: Option<SimpleHint>,
    },
    AnySetOf {
        elements: Vec<Arc<Grammar>>,
        min_times: usize,
        max_times: Option<usize>,
        exclude: Option<Box<Arc<Grammar>>>,
        optional: bool,
        terminators: Vec<Arc<Grammar>>,
        reset_terminators: bool,
        allow_gaps: bool,
        parse_mode: ParseMode,
        simple_hint: Option<SimpleHint>,
    },
    Delimited {
        elements: Vec<Arc<Grammar>>,
        delimiter: Box<Arc<Grammar>>,
        allow_trailing: bool,
        optional: bool,
        optional_delimiter: bool, // If true, delimiters are optional (OptionallyDelimited)
        terminators: Vec<Arc<Grammar>>,
        reset_terminators: bool,
        allow_gaps: bool,
        min_delimiters: usize,
        parse_mode: ParseMode,
        simple_hint: Option<SimpleHint>,
    },
    Bracketed {
        elements: Vec<Arc<Grammar>>,
        bracket_pairs: (Box<Arc<Grammar>>, Box<Arc<Grammar>>),
        optional: bool,
        terminators: Vec<Arc<Grammar>>,
        reset_terminators: bool,
        allow_gaps: bool,
        parse_mode: ParseMode,
        simple_hint: Option<SimpleHint>,
    },
    Ref {
        name: &'static str,
        optional: bool,
        exclude: Option<Box<Arc<Grammar>>>,
        terminators: Vec<Arc<Grammar>>,
        reset_terminators: bool,
        allow_gaps: bool,
        simple_hint: Option<SimpleHint>,
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
        template: crate::regex::RegexMode,
        token_type: &'static str,
        raw_class: &'static str,
        optional: bool,
        anti_template: Option<crate::regex::RegexMode>,
    },
    Meta(&'static str),
    NonCodeMatcher,
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
    pub fn simple_hint(
        &self,
        cache: &mut hashbrown::HashMap<u64, Option<SimpleHint>>,
    ) -> Option<SimpleHint> {
        let key = self.cache_key();
        if let Some(cached) = cache.get(&key) {
            return cached.as_ref().cloned();
        }

        let result = match self {
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

            // Meta: Invisible to matching - return empty hint so it doesn't block pruning
            Grammar::Meta(s) => match *s {
                "indent" | "dedent" => Some(SimpleHint::empty()),
                _ => None,
            },
            // NonCodeMatcher: matches whitespace/newline, so hint by type
            Grammar::NonCodeMatcher => Some(SimpleHint::from_types(&["whitespace", "newline"])),

            // Ref: Resolve to referenced grammar (with recursion protection)
            Grammar::Ref { simple_hint, .. } => simple_hint.clone(),

            // Sequence: accumulate hints from optional elements until first non-optional
            // Python logic: union all optional elements, then return when hitting first required
            Grammar::Sequence { simple_hint, .. } => simple_hint.clone(),

            // OneOf: union of all alternatives' hints
            // Python logic: if ANY element returns None, the whole OneOf returns None
            Grammar::OneOf { simple_hint, .. } => simple_hint.clone(),

            // AnyNumberOf: union of all elements (like OneOf)
            // Python logic: ALL elements must be simple, or return None
            Grammar::AnyNumberOf { simple_hint, .. } => simple_hint.clone(),

            // AnySetOf: union of all elements (same as AnyNumberOf)
            Grammar::AnySetOf { simple_hint, .. } => simple_hint.clone(),

            // Delimited: union of all element alternatives
            // Note: Delimiter is NOT part of the simple hint (it terminates, doesn't start)
            Grammar::Delimited { simple_hint, .. } => simple_hint.clone(),

            // Bracketed: starts with opening bracket
            Grammar::Bracketed { bracket_pairs, .. } => bracket_pairs.0.simple_hint(cache),

            // Nothing/Empty: matches nothing, so empty hint is correct
            Grammar::Nothing() | Grammar::Empty => Some(SimpleHint::empty()),

            // Anything, Missing, Indent, Dedent: Can't determine
            _ => None,
        };
        cache.insert(key, result.as_ref().cloned());
        result
    }
}

// Implement Hash for Grammar
impl Hash for Grammar {
    fn hash<H: Hasher>(&self, state: &mut H) {
        std::mem::discriminant(self).hash(state);
        match self {
            Grammar::NonCodeMatcher => {}
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
            Grammar::RegexParser { template, .. } => template.as_str().hash(state),
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
            (Grammar::NonCodeMatcher, Grammar::NonCodeMatcher) => true,
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
            ) => {
                template.as_str() == t2.as_str()
                    && token_type == tt2
                    && optional == o2
                    && anti_template.as_ref().map(|at1| at1.as_str())
                        == at2.as_ref().map(|x| x.as_str())
            }
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
            Grammar::RegexParser { template, .. } => {
                write!(f, "RegexParser({})", template.as_str())
            }
            Grammar::Meta(s) => write!(f, "Meta({})", s),
            Grammar::NonCodeMatcher => write!(f, "NonCodeMatcher"),
            Grammar::Nothing() => write!(f, "Nothing"),
            Grammar::Anything => write!(f, "Anything"),
            Grammar::Empty => write!(f, "Empty"),
            Grammar::Missing => write!(f, "Missing"),
            Grammar::Token { token_type } => write!(f, "Token({})", token_type),
        }
    }
}
