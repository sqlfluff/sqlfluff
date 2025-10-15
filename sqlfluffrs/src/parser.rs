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

#[derive(Debug, Clone)]
pub enum Grammar {
    Sequence {
        elements: Vec<Grammar>,
        optional: bool,
        terminators: Vec<Grammar>,
        reset_terminators: bool,
        allow_gaps: bool,
    },
    AnyNumberOf {
        elements: Vec<Grammar>,
        min_times: usize,
        max_times: Option<usize>,
        optional: bool,
        terminators: Vec<Grammar>,
        reset_terminators: bool,
        allow_gaps: bool,
    },
    OneOf {
        elements: Vec<Grammar>,
        optional: bool,
        terminators: Vec<Grammar>,
        reset_terminators: bool,
        allow_gaps: bool,
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
    },
    Bracketed {
        elements: Vec<Grammar>,
        bracket_pairs: (Box<Grammar>, Box<Grammar>),
        optional: bool,
        terminators: Vec<Grammar>,
        reset_terminators: bool,
        allow_gaps: bool,
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
}

// Implement Hash for Grammar (discriminant + key fields)
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
            },
            Grammar::AnyNumberOf {
                elements,
                optional,
                allow_gaps,
                ..
            } => {
                elements.hash(state);
                optional.hash(state);
                allow_gaps.hash(state);
            },
            Grammar::OneOf {
                elements,
                optional,
                allow_gaps,
                ..
            } => {
                elements.hash(state);
                optional.hash(state);
                allow_gaps.hash(state);
            },
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
            },
            Grammar::Bracketed {
                elements,
                optional,
                allow_gaps,
                ..
            } => {
                elements.hash(state);
                optional.hash(state);
                allow_gaps.hash(state);
            },
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
    pub grammar: Grammar,
}

#[derive(Debug, Clone, PartialEq)]
pub enum Node {
    /// A plain SQL keyword like SELECT, FROM, INTO
    Keyword(String, usize),

    Code(String, usize),

    /// A sequence of child nodes (used for Grammar::Sequence)
    Sequence(Vec<Node>),

    /// A list of elements separated by commas
    DelimitedList(Vec<Node>),

    /// A reference to another segment (wraps its AST)
    Ref {
        name: String,
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
}

pub struct Parser<'a> {
    pub tokens: &'a [Token],
    pub pos: usize, // current position in tokens
    pub dialect: Dialect,
    pub parse_cache: ParseCache,
}

impl<'a> Parser<'_> {
    pub fn parse_with_grammar_cached(
        &mut self,
        grammar: &Grammar,
        parent_terminators: &[Grammar],
    ) -> Result<Node, ParseError> {
        // Create cache key
        let cache_key = CacheKey::new(self.pos, grammar, self.tokens);

        // Check cache first
        if let Some(Ok((node, end_pos))) = self.parse_cache.get(&cache_key) {
            self.pos = end_pos; // Directly set to cached end position
            return Ok(node);
        }

        // Cache miss - parse fresh
        let start_pos = self.pos;
        let result = self.parse_with_grammar(grammar, parent_terminators);

        // Store in cache
        if let Ok(ref node) = result {
            self.parse_cache
                .put(cache_key, Ok((node.clone(), self.pos)));
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
                log::debug!("Trying meta");
                Ok(Node::Meta(token_type))
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
                        Ok(Node::Code(tok.raw(), token_pos))
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
                        Ok(Node::Code(tok.raw(), token_pos))
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
                log::debug!("Trying Ref to segment: {}, optional: {}", name, optional);
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
            } => {
                log::debug!("Trying Sequence with {} elements", elements.len());

                // Save start position for backtracking if the whole sequence fails
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

                let mut children: Vec<Node> = Vec::new();

                for element in elements {
                    log::debug!("Sequence-@{}: {:?}", self.pos, element);

                    self.skip_transparent(*allow_gaps);

                    // Check if we hit a terminator
                    if self.is_terminated(&all_terminators) {
                        log::debug!("Sequence terminated!");
                        break;
                    }

                    let element_start = self.pos;

                    match self.parse_with_grammar_cached(element, &all_terminators) {
                        Ok(node) => {
                            let consumed = self.pos - element_start;
                            if !node.is_empty() {
                                log::debug!(
                                    "MATCHED Sequence element matched: {:?}, consumed: {}",
                                    node,
                                    consumed
                                );
                                children.push(node);
                            } else {
                                // Empty node (from optional element that didn't match)
                                log::debug!("Sequence element returned Empty, continuing");
                            }
                        }
                        Err(e) => {
                            // Element failed to match
                            self.pos = element_start;

                            // Check if this specific element is optional
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
                                // This element is optional, continue with next element
                                log::debug!("NOMATCH Sequence element is optional, continuing");
                                continue;
                            } else if *optional {
                                // The whole sequence is optional, so we can return empty
                                log::debug!("NOMATCH Sequence is optional, returning empty");
                                self.pos = start_idx;
                                return Ok(Node::Empty);
                            } else {
                                // Required element failed, fail the whole sequence
                                log::debug!("NOMATCH Required element failed, sequence fails");
                                return Err(e);
                            }
                        }
                    }
                }

                log::debug!("MATCHED Sequence children: {:?}", &children);

                // If we have no children and the sequence itself is optional, return Empty
                // This prevents infinite loops in AnyNumberOf when all elements are optional
                if children.is_empty() && *optional {
                    log::debug!("Sequence matched no children and is optional, returning Empty");
                    Ok(Node::Empty)
                } else {
                    Ok(Node::Sequence(children))
                }
            }
            Grammar::OneOf {
                elements,
                optional,
                terminators,
                reset_terminators,
                allow_gaps,
            } => {
                log::debug!("Trying OneOf elements: {:?}", elements);
                let initial_pos = self.pos;
                self.skip_transparent(*allow_gaps);
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

                let mut longest_match: Option<(Node, usize)> = None;
                let mut best_pos = post_skip_pos;

                for element in elements {
                    self.pos = post_skip_pos;

                    match self.parse_with_grammar_cached(element, &all_terminators) {
                        Ok(node) if !node.is_empty() => {
                            let consumed = self.pos - post_skip_pos;

                            // Early exit on complete/terminated match
                            if self.is_at_end() || self.is_terminated(&all_terminators) {
                                log::debug!("OneOf: Early exit with complete/terminated match");
                                return Ok(node);
                            }

                            if longest_match.is_none()
                                || consumed > longest_match.as_ref().unwrap().1
                            {
                                longest_match = Some((node, consumed));
                                best_pos = self.pos;
                                log::debug!(
                                    "PARTMATCHED OneOf element matched, consumed: {}",
                                    consumed
                                );
                            }
                        }
                        Ok(_) => {
                            // Empty node, continue trying other elements
                        }
                        Err(_) => {
                            // No match for this element, continue
                        }
                    }
                }

                if let Some((node, _)) = longest_match {
                    self.pos = best_pos;
                    log::debug!("MATCHED OneOf matched longest element: {:?}", node);
                    return Ok(node);
                }

                self.pos = initial_pos;
                if *optional {
                    Ok(Node::Empty)
                } else {
                    Err(ParseError::new("Expected one of choices".into()))
                }
            }
            Grammar::AnyNumberOf {
                elements,
                min_times,
                max_times,
                optional,
                terminators,
                reset_terminators,
                allow_gaps,
            } => {
                log::debug!("Trying AnyNumberOf elements: {:?}", elements);
                let mut items = vec![];
                let mut count = 0;
                let initial_pos = self.pos;

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

                // Check for termination BEFORE starting
                if self.is_terminated(&all_terminators) {
                    if *optional || *min_times == 0 {
                        log::debug!("AnyNumberOf: empty optional or min_times=0");
                        return Ok(Node::DelimitedList(items));
                    } else {
                        return Err(ParseError::new(format!(
                            "Expected at least {} occurrences, found 0",
                            min_times
                        )));
                    }
                }

                loop {
                    let mut matched = false;
                    self.skip_transparent(*allow_gaps);
                    let post_skip_saved_pos = self.pos;

                    // Prune options before trying
                    let available_options = self.prune_options(elements);

                    if available_options.is_empty() {
                        // No options could match - stop loop
                        self.pos = post_skip_saved_pos;
                        break;
                    }

                    let mut longest_match: Option<(Node, usize)> = None;
                    let mut best_pos = post_skip_saved_pos;

                    for element in elements {
                        self.pos = post_skip_saved_pos;
                        match self.parse_with_grammar_cached(element, &all_terminators) {
                            Ok(node) if !node.is_empty() => {
                                let consumed = self.pos - post_skip_saved_pos;
                                if longest_match.is_none()
                                    || consumed > longest_match.as_ref().unwrap().1
                                {
                                    longest_match = Some((node, consumed));
                                    best_pos = self.pos;
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

                    if let Some((node, _)) = longest_match {
                        self.pos = best_pos;
                        items.push(node);
                        count += 1;
                        matched = true;
                    }

                    if !matched {
                        // If no elements matched, restore to position BEFORE this iteration
                        self.pos = post_skip_saved_pos;
                        break;
                    }

                    // Check for termination AFTER a successful match
                    if self.is_terminated(&all_terminators) {
                        log::debug!("AnyNumberOf: terminated after {} matches", count);
                        break;
                    }

                    if let Some(max) = max_times {
                        if count >= *max {
                            break;
                        }
                    }
                }

                if count < *min_times {
                    if *optional {
                        self.pos = initial_pos;
                        Ok(Node::Empty)
                    } else {
                        Err(ParseError::new(format!(
                            "Expected at least {} occurrences, found {}",
                            min_times, count
                        )))
                    }
                } else {
                    log::debug!("MATCHED AnyNumberOf matched items: {:?}", items);
                    Ok(Node::DelimitedList(items))
                }
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
            } => {
                log::debug!("Trying Delimited elements: {:?}", elements);
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
                    self.skip_transparent(*allow_gaps);
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
                            items.push(node);
                        }
                        None => {
                            self.pos = saved_pos;
                            log::debug!("Delimited: no more elements matched");
                            break;
                        }
                    }

                    let saved_pos = self.pos;
                    self.skip_transparent(*allow_gaps);
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
                        items.push(delim_node);
                    } else {
                        self.pos = saved_pos;
                        log::debug!("Delimited: no delimiter found, ending");
                        break;
                    }
                }

                Ok(Node::DelimitedList(items))
            }
            Grammar::Bracketed {
                elements,
                bracket_pairs,
                optional,
                terminators,
                reset_terminators,
                allow_gaps,
            } => {
                log::debug!("Trying Bracketed elements: {:?}", elements);
                let saved_pos = self.pos;
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

                match self.parse_with_grammar_cached(&bracket_pairs.0, &all_terminators) {
                    Ok(open_node) => {
                        let mut children = vec![open_node];

                        let mut last_successful_pos = self.pos;
                        loop {
                            if self.is_terminated(&[*bracket_pairs.1.clone()]) {
                                log::debug!("  TERM Bracketed: found closing bracket terminator");
                                break;
                            }

                            let mut matched = false;
                            let saved_inner_pos = self.pos;
                            self.skip_transparent(*allow_gaps);

                            let mut longest_match: Option<(Node, usize)> = None;
                            let mut best_pos = self.pos;

                            for elem in elements {
                                self.pos = saved_inner_pos;
                                if let Ok(node) = self
                                    .parse_with_grammar_cached(elem, &[*bracket_pairs.1.clone()])
                                {
                                    let consumed = self.pos - saved_inner_pos;
                                    if longest_match.is_none()
                                        || consumed > longest_match.as_ref().unwrap().1
                                    {
                                        longest_match = Some((node, consumed));
                                        best_pos = self.pos;
                                    }
                                }
                            }

                            if let Some((node, _)) = longest_match {
                                self.pos = best_pos;
                                children.push(node);
                                matched = true;
                                last_successful_pos = self.pos;
                            }

                            if !matched || self.pos <= last_successful_pos {
                                self.pos = last_successful_pos;
                                break;
                            }
                        }
                        self.skip_transparent(*allow_gaps);
                        match self.parse_with_grammar_cached(
                            &bracket_pairs.1,
                            &[*bracket_pairs.1.clone()],
                        ) {
                            Ok(close_node) => {
                                children.push(close_node);
                                log::debug!(
                                    "PARTMATCHED Bracketed matched children: {:?}, final pos: {}",
                                    &children,
                                    self.pos
                                );
                                Ok(Node::Sequence(children))
                            }
                            Err(e) => Err(ParseError::new(format!(
                                "Expected closing bracket: {}",
                                e.message
                            ))),
                        }
                    }
                    Err(e) => {
                        self.pos = saved_pos;
                        if *optional {
                            Ok(Node::Empty)
                        } else {
                            Err(ParseError::new(format!(
                                "Expected opening bracket: {}",
                                e.message
                            )))
                        }
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

    /// Skip all transparent tokens (whitespace, newlines)
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

    pub fn is_terminated(&mut self, terminators: &[Grammar]) -> bool {
        let init_pos = self.pos;
        self.skip_transparent(true);
        let saved_pos = self.pos;

        // Check if we've reached end of file
        if self.is_at_end() {
            log::debug!("  TERMED Reached end of file");
            return true;
        }

        // Check if current token is end_of_file type
        if let Some(tok) = self.peek() {
            if tok.get_type() == "end_of_file" {
                log::debug!("  TERMED Found end_of_file token");
                return true;
            }
        }

        log::debug!(
            "  TERM Checking terminators: {:?} at pos {:?}",
            terminators,
            self.pos
        );
        for term in terminators {
            if let Ok(node) = self.parse_with_grammar_cached(term, &[]) {
                self.pos = saved_pos; // don't consume

                // Check if the node is "empty" in various ways
                let is_empty = node.is_empty();

                if !is_empty {
                    log::debug!("  TERMED Terminator matched: {}", term);
                    self.pos = init_pos; // restore original position
                    return true;
                }
            }
            self.pos = saved_pos;
        }
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

        // Wrap in a Ref node for type clarity
        Ok(Node::Ref {
            name: name.to_string(),
            child: Box::new(node),
        })
    }

    /// Lookup SegmentDef by name
    pub fn get_segment_grammar(&self, name: &str) -> Option<&'static Grammar> {
        self.dialect.get_segment_grammar(name)
    }

    fn new(tokens: &'a [Token], dialect: Dialect) -> Parser<'a> {
        Parser {
            tokens,
            pos: 0,
            dialect,
            parse_cache: ParseCache::new(),
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

        assert_eq!(parser.tokens[parser.pos - 1].get_type(), "end_of_file");
        assert_eq!(parser.pos, parser.tokens.len());

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
    fn parse_column_def_segment() -> Result<(), ParseError> {
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

        assert_eq!(parser.tokens[parser.pos - 1].get_type(), "end_of_file");
        assert_eq!(parser.pos, parser.tokens.len());

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
            .spawn(|| parse_many_join_impl())
            .unwrap()
            .join()
            .unwrap()
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
}
