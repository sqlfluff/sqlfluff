use std::fmt::Display;
use std::vec;

use crate::{dialect::Dialect, token::Token};

#[derive(Debug, Clone)]
pub struct RegexParserConfig {
    pattern: String,
    segment_type: String,
    parser_type: String,
    anti_template: Option<String>,
    casefold: Option<fn(&str) -> String>,
}

pub struct IdentifierSegmentGenerator {
    reserved_keywords: Vec<String>,
}

impl IdentifierSegmentGenerator {
    pub fn new(dialect: &Dialect) -> Self {
        Self {
            reserved_keywords: dialect.get_reserved_keywords().clone(),
        }
    }

    pub fn generate(&self) -> RegexParserConfig {
        let anti_template = format!("^({})$", self.reserved_keywords.join("|"));

        RegexParserConfig {
            pattern: String::from(r"[A-Z0-9_]*[A-Z][A-Z0-9_]*"),
            segment_type: String::from("identifier"),
            parser_type: String::from("naked_identifier"),
            anti_template: Some(anti_template),
            casefold: Some(|s: &str| s.to_uppercase()),
        }
    }
}

#[derive(Debug, Clone, PartialEq)]
pub enum Grammar {
    Sequence {
        elements: Vec<Grammar>,
        optional: bool,
        terminators: Vec<Grammar>,
        allow_gaps: bool,
    },
    AnyNumberOf {
        elements: Vec<Grammar>,
        min_times: usize,
        max_times: Option<usize>,
        optional: bool,
        terminators: Vec<Grammar>,
        allow_gaps: bool,
    },
    OneOf {
        elements: Vec<Grammar>,
        optional: bool,
        terminators: Vec<Grammar>,
        allow_gaps: bool,
    },
    Delimited {
        elements: Vec<Grammar>,
        delimiter: Box<Grammar>,
        allow_trailing: bool,
        optional: bool,
        terminators: Vec<Grammar>,
        allow_gaps: bool,
    },
    Bracketed {
        elements: Vec<Grammar>,
        bracket_pairs: (Box<Grammar>, Box<Grammar>),
        optional: bool,
        terminators: Vec<Grammar>,
        allow_gaps: bool,
    },
    Ref {
        name: &'static str,
        optional: bool,
        terminators: Vec<Grammar>,
        allow_gaps: bool,
    },
    Keyword {
        name: &'static str,
        optional: bool,
        allow_gaps: bool,
        terminators: Vec<Grammar>,
    },
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
    Meta,
    Nothing(),
    Anything,
    OptionallyBracketed(),
    Empty,
    Missing,
    Token {
        token_type: &'static str,
    },
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
            Grammar::Keyword { name, .. } => write!(f, "Keyword({})", name),
            Grammar::Symbol(sym) => write!(f, "Symbol({})", sym),
            Grammar::StringParser { template, .. } => write!(f, "StringParser({})", template),
            Grammar::MultiStringParser { templates, .. } => {
                write!(f, "MultiStringParser({:?})", templates)
            }
            Grammar::TypedParser { template, .. } => write!(f, "TypedParser({})", template),
            Grammar::RegexParser { template, .. } => write!(f, "RegexParser({})", template),
            Grammar::Meta => write!(f, "Meta"),
            Grammar::Nothing() => write!(f, "Nothing"),
            Grammar::Anything => write!(f, "Anything"),
            Grammar::OptionallyBracketed() => write!(f, "OptionallyBracketed"),
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
    Keyword(String),

    Code(String),

    /// A sequence of child nodes (used for Grammar::Sequence)
    Sequence(Vec<Node>),

    OneOf(Box<Node>),

    /// A list of elements separated by commas
    DelimitedList(Vec<Node>),

    /// A reference to another segment (wraps its AST)
    Ref {
        name: String,
        child: Box<Node>,
    },

    /// Used when an optional part didn’t match
    Empty,
    Meta,
}

pub struct Parser<'a> {
    tokens: &'a [Token],
    pos: usize, // current position in tokens
    dialect: Dialect,
}

impl Parser<'_> {
    fn parse_with_grammar(
        &mut self,
        grammar: &Grammar,
        parent_terminators: &[Grammar],
    ) -> Result<Node, ParseError> {
        // println!("Parsing with grammar: {}@{}", grammar, self.pos);
        // println!("Parent terminators: {:?}", parent_terminators);
        match grammar {
            Grammar::Missing => {
                // println!("Expecting missing grammar");
                todo!("Encountered Missing grammar in parse_with_grammar");
            }
            Grammar::Anything => {
                // This matches anything
                // it is greedy so will consume everything until a terminator is found
                // println!("Expecting anything grammar");
                let mut anything_tokens = vec![];
                loop {
                    if self.is_terminated(parent_terminators) || self.is_at_end() {
                        break;
                    }
                    if let Some(tok) = self.peek() {
                        anything_tokens.push(Node::Code(tok.raw().to_string()));
                        self.bump();
                    }
                }
                println!("Anything matched tokens: {:?}", anything_tokens);
                Ok(Node::DelimitedList(anything_tokens))
            }
            Grammar::Token { token_type } => {
                // println!("Expecting token, {}", token_type);
                if let Some(tok) = self.peek() {
                    let tok = tok.clone();
                    // println!("Current token: {:?}", tok.get_type());
                    if tok.get_type() == *token_type {
                        self.bump();
                        println!("Token matched: {:?}", tok);
                        Ok(Node::Code(tok.raw()))
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
            Grammar::Keyword {
                name,
                optional,
                terminators,
                allow_gaps,
            } => {
                // println!("Expecting keyword: {}", name);
                self.expect_keyword(name, *allow_gaps)
            }
            Grammar::Meta => {
                println!("Expecting meta");
                Ok(Node::Meta)
            }
            Grammar::StringParser {
                template,
                token_type,
                optional,
            } => {
                // println!(
                //     "Expecting string parser: {}, type: {:?}",
                //     template, token_type
                // );
                self.skip_transparent(true);
                let tok_raw = self.peek().map(|t| t.raw().to_string());
                match tok_raw {
                    Some(tok) if tok.eq_ignore_ascii_case(template) => {
                        self.bump();
                        println!("String matched: {}", tok);
                        Ok(Node::Code(tok))
                    }
                    _ => {
                        if *optional {
                            // println!("String parser optional, skipping");
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
                // println!(
                //     "Expecting multi string parser: {:?}, type: {:?}",
                //     templates, token_type
                // );
                self.skip_transparent(true);
                let token_raw = self.peek().map(|t| t.raw().to_string());
                match token_raw {
                    Some(raw) if templates.iter().any(|&temp| raw.eq_ignore_ascii_case(temp)) => {
                        self.bump();
                        println!("Multi string matched: {}", raw);
                        Ok(Node::Code(raw))
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
                // println!(
                //     "Expecting regex parser: {}, type: {:?}",
                //     template, token_type
                // );
                self.skip_transparent(true);
                let tok_raw = self.peek().map(|t| t.raw().to_string());
                match tok_raw {
                    Some(raw)
                        if regex::RegexBuilder::new(template)
                            .case_insensitive(true)
                            .build()
                            .unwrap()
                            .is_match(&raw) =>
                    {
                        println!("Regex matched: {}", raw);
                        if let Some(anti) = anti_template {
                            if regex::RegexBuilder::new(anti)
                                .case_insensitive(true)
                                .build()
                                .unwrap()
                                .is_match(&raw)
                            {
                                if *optional {
                                    return Ok(Node::Empty);
                                } else {
                                    return Err(ParseError::new(format!(
                                        "Token '{}' matches anti-template '{}'",
                                        raw, anti
                                    )));
                                }
                            }
                        }
                        println!("Regex matched and non anti-match: {}", raw);
                        self.bump();
                        Ok(Node::Code(raw))
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
                // println!("Expecting typed parser: {}, type: {}", template, token_type);
                self.skip_transparent(true);
                if let Some(tok) = self.peek() {
                    let tok = tok.clone();
                    if tok.is_type(&[template]) {
                        self.bump();
                        println!("Typed matched: {}", tok.token_type);
                        Ok(Node::Code(tok.raw()))
                    } else if *optional {
                        Ok(Node::Empty)
                    } else {
                        Err(ParseError::new(format!(
                            "Expected typed token '{}'",
                            template
                        )))
                    }
                } else if *optional {
                    Ok(Node::Empty)
                } else {
                    Err(ParseError::new(format!(
                        "Expected typed token '{}', found EOF",
                        template
                    )))
                }
            }
            Grammar::Symbol(sym) => {
                println!("Expecting symbol: {}", sym);
                match self.peek() {
                    Some(t) if t.raw() == *sym => {
                        self.bump();
                        println!("Symbol matched: {}", sym);
                        Ok(Node::Code(sym.to_string()))
                    }
                    _ => Err(ParseError::new(format!("Expected symbol '{}'", sym))),
                }
            }
            Grammar::Ref {
                name,
                optional,
                allow_gaps,
                terminators,
            } => {
                // println!("Ref to segment: {}, optional: {}", name, optional);
                let saved = self.pos;
                self.skip_transparent(*allow_gaps);

                // Combine parent and local terminators
                let all_terminators: Vec<Grammar> = terminators
                    .iter()
                    .cloned()
                    .chain(parent_terminators.iter().cloned())
                    .collect();

                let attempt = self.call_rule(name, &all_terminators);
                match attempt {
                    Ok(node) => {
                        println!("Ref matched segment: {}", name);
                        Ok(node)
                    }
                    Err(e) => {
                        self.pos = saved;
                        if *optional {
                            // println!("Ref optional, skipping");
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
                allow_gaps,
            } => {
                // println!("Sequence elements: {:?}", elements);
                let saved = self.pos;
                self.skip_transparent(*allow_gaps);
                let mut children = vec![];

                // Combine parent and local terminators
                let all_terminators: Vec<Grammar> = terminators
                    .iter()
                    .cloned()
                    .chain(parent_terminators.iter().cloned())
                    .collect();

                for element in elements {
                    // println!("Sequence element: {:?}", element);
                    if self.is_terminated(&all_terminators) {
                        // println!("Sequence terminated!");
                        break;
                    }
                    match self.parse_with_grammar(element, &all_terminators) {
                        Ok(node) => {
                            println!("Sequence element matched: {:?}", node);
                            children.push(node)
                        }
                        Err(e) => {
                            self.pos = saved;
                            if *optional {
                                // println!("Sequence element optional, skipping");
                                return Ok(Node::Empty);
                            } else {
                                return Err(e);
                            }
                        }
                    }
                }
                println!("Sequence children: {:?}", &children);
                Ok(Node::Sequence(children))
            }
            Grammar::OneOf {
                elements,
                optional,
                terminators,
                allow_gaps,
            } => {
                // println!("OneOf elements: {:?}", elements);
                let initial_pos = self.pos;
                self.skip_transparent(*allow_gaps);

                // Combine parent and local terminators
                let all_terminators: Vec<Grammar> = terminators
                    .iter()
                    .cloned()
                    .chain(parent_terminators.iter().cloned())
                    .collect();

                for element in elements {
                    if self.is_terminated(&all_terminators) {
                        break;
                    }
                    let element_start = self.pos;
                    match self.parse_with_grammar(element, &all_terminators) {
                        Ok(node) => {
                            println!("OneOf matched element: {:?}", node);
                            return Ok(Node::OneOf(Box::new(node)));
                        }
                        Err(_) => {
                            self.pos = element_start;
                        }
                    }
                }

                if *optional {
                    self.pos = initial_pos;
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
                allow_gaps,
            } => {
                // println!("AnyNumberOf elements: {:?}", elements);
                let mut items = vec![];
                let mut count = 0;
                let saved_pos = self.pos;

                // Combine parent and local terminators
                let all_terminators: Vec<Grammar> = terminators
                    .iter()
                    .cloned()
                    .chain(parent_terminators.iter().cloned())
                    .collect();

                loop {
                    if self.is_terminated(&all_terminators) {
                        break;
                    }

                    let mut matched = false;
                    self.skip_transparent(*allow_gaps);
                    let post_skip_saved_pos = self.pos;

                    for element in elements {
                        match self.parse_with_grammar(element, &all_terminators) {
                            Ok(node) if node != Node::Empty => {
                                items.push(node);
                                count += 1;
                                matched = true;
                                break;
                            }
                            Ok(_) => {
                                // if self.pos > post_skip_saved_pos {
                                //     // items.push(node);
                                // }
                                // If position didn't advance, treat as no match
                                // self.pos = post_skip_saved_pos;
                                // panic!("Parser did not advance position, possible infinite loop");
                            }
                            Err(_) => self.pos = saved_pos,
                        }
                    }

                    if !matched {
                        // If no elements matched, restore to initial position
                        self.pos = saved_pos;
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
                        Ok(Node::Empty)
                    } else {
                        Err(ParseError::new(format!(
                            "Expected at least {} occurrences, found {}",
                            min_times, count
                        )))
                    }
                } else {
                    println!("AnyNumberOf matched items: {:?}", items);
                    Ok(Node::DelimitedList(items))
                }
            }
            Grammar::Delimited {
                elements,
                delimiter,
                allow_trailing,
                optional,
                terminators,
                allow_gaps,
            } => {
                // println!("Delimited elements: {:?}", elements);
                let mut items = vec![];

                // Combine parent and local terminators
                let all_terminators: Vec<Grammar> = terminators
                    .iter()
                    .cloned()
                    .chain(parent_terminators.iter().cloned())
                    .collect();

                if *optional && (self.is_at_end() || self.is_terminated(&all_terminators)) {
                    println!("Delimited: empty optional");
                    return Ok(Node::DelimitedList(items));
                }

                loop {
                    if self.is_terminated(&all_terminators) {
                        break;
                    }

                    let mut matched = false;
                    let saved_pos = self.pos;
                    self.skip_transparent(*allow_gaps);
                    let post_skip_saved_pos = self.pos;
                    for elem in elements {
                        match self.parse_with_grammar(elem, &all_terminators) {
                            Ok(node) => {
                                if self.pos > post_skip_saved_pos {
                                    items.push(node);
                                    matched = true;
                                    break;
                                }
                                // If position didn't advance, treat as no match
                                // self.pos = post_skip_saved_pos;
                                panic!("Parser did not advance position, possible infinite loop");
                            }
                            Err(_) => self.pos = saved_pos,
                        }
                    }

                    if !matched {
                        // println!("Delimited: no more elements matched");
                        break;
                    }

                    let saved_pos = self.pos;
                    self.skip_transparent(*allow_gaps);
                    if let Ok(delim_node) = self.parse_with_grammar(delimiter, &all_terminators) {
                        if self.is_terminated(&all_terminators) {
                            if !*allow_trailing {
                                return Err(ParseError::new(
                                    "Trailing delimiter not allowed".to_string(),
                                ));
                            }
                            break;
                        }
                        println!("Delimited: found delimiter");
                        items.push(delim_node);
                    } else {
                        self.pos = saved_pos;
                        println!("Delimited: no delimiter found, ending");
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
                allow_gaps,
            } => {
                println!("Bracketed elements: {:?}", elements);
                let saved_pos = self.pos;
                self.skip_transparent(*allow_gaps);

                // Combine parent and local terminators
                // let all_terminators: Vec<Grammar> = terminators
                //     .iter()
                //     .cloned()
                //     .chain(parent_terminators.iter().cloned())
                //     .collect();

                match self.parse_with_grammar(&bracket_pairs.0, &[]) {
                    Ok(open_node) => {
                        let mut children = vec![open_node];

                        let mut last_successful_pos = self.pos;
                        loop {
                            if self.is_terminated(&[*bracket_pairs.1.clone()]) {
                                break;
                            }

                            let mut matched = false;
                            let saved_inner_pos = self.pos;
                            self.skip_transparent(*allow_gaps);

                            for elem in elements {
                                match self.parse_with_grammar(elem, &[*bracket_pairs.1.clone()]) {
                                    Ok(node) => {
                                        children.push(node);
                                        matched = true;
                                        last_successful_pos = self.pos;
                                        break;
                                    }
                                    Err(_) => self.pos = saved_inner_pos,
                                }
                            }

                            if !matched || self.pos <= last_successful_pos {
                                self.pos = last_successful_pos;
                                break;
                            }
                        }
                        self.skip_transparent(*allow_gaps);
                        match self.parse_with_grammar(&bracket_pairs.1, &[*bracket_pairs.1.clone()])
                        {
                            Ok(close_node) => {
                                children.push(close_node);
                                println!("Bracketed matched children: {:?}", &children);
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
                    println!("skipping token: {:?}", tok);
                    self.bump()
                }
                _ => break,
            }
        }
    }

    fn is_terminated(&mut self, terminators: &[Grammar]) -> bool {
        self.skip_transparent(true);
        let saved_pos = self.pos;
        // println!(
        //     "Checking terminators: {:?} at pos {:?}",
        //     terminators, self.pos
        // );
        for term in terminators {
            if self.parse_with_grammar(term, &[]).is_ok() {
                self.pos = saved_pos; // don’t consume
                return true;
            }
            self.pos = saved_pos;
        }
        false
    }

    /// Peek after skipping transparent tokens
    pub fn peek_non_transparent(&mut self) -> Option<&Token> {
        let mut pos = self.pos;
        while let Some(tok) = self.tokens.get(pos) {
            match tok {
                tok if !tok.is_code() => pos += 1,
                _ => return Some(tok),
            }
        }
        None
    }

    pub fn expect_keyword(&mut self, kw: &str, allow_gaps: bool) -> Result<Node, ParseError> {
        self.skip_transparent(allow_gaps);
        match self.peek() {
            Some(tok) if tok.is_type(&["word"]) && tok.raw().eq_ignore_ascii_case(kw) => {
                let keyword = tok.raw().to_string();
                self.bump(); // consume the keyword
                println!("Keyword matched: {}", keyword);
                Ok(Node::Keyword(keyword))
            }
            Some(tok) => Err(ParseError::new(format!(
                "Expected keyword '{}', found {:?}",
                kw, tok
            ))),
            None => Err(ParseError::new(format!(
                "Expected keyword '{}', found end of input",
                kw
            ))),
        }
    }

    pub fn consume_keyword(&mut self, kw: &str) -> bool {
        match self.peek() {
            Some(tok) if tok.is_type(&["word"]) && tok.raw().eq_ignore_ascii_case(kw) => {
                self.bump();
                true
            }
            _ => false,
        }
    }

    fn parse_naked_identifier(&mut self) -> Result<Node, ParseError> {
        let config = IdentifierSegmentGenerator::new(&self.dialect).generate();

        // Use the config to parse
        if let Some(token) = self.peek() {
            let raw = token.raw();

            // Check against pattern
            if !regex::Regex::new(&config.pattern).unwrap().is_match(&raw) {
                return Err(ParseError::new("Does not match identifier pattern".into()));
            }

            // Check against anti_template if present
            if let Some(anti) = &config.anti_template {
                if regex::Regex::new(anti).unwrap().is_match(&raw) {
                    return Err(ParseError::new("Matches reserved keyword".into()));
                }
            }

            // Apply casefold if needed
            let final_value = if let Some(casefold) = config.casefold {
                casefold(&raw)
            } else {
                raw
            };

            self.bump();
            Ok(Node::Ref {
                name: config.segment_type,
                child: Box::new(Node::Keyword(final_value)),
            })
        } else {
            Err(ParseError::new("Expected identifier".into()))
        }
    }

    pub fn parse_identifier(&mut self) -> Result<Node, ParseError> {
        match self.peek() {
            Some(token) if token.is_type(&["word"]) => {
                // Check it's not a keyword
                let upper = token.raw().to_uppercase();
                if ["SELECT", "FROM", "WHERE", "INTO"].contains(&upper.as_str()) {
                    return Err(ParseError::new(format!(
                        "Expected identifier, got keyword '{}'",
                        &token.raw()
                    )));
                }
                let token_raw = token.raw().clone();
                self.bump();
                Ok(Node::Ref {
                    name: "Identifier".into(),
                    child: Box::new(Node::Keyword(token_raw)), // or Node::Identifier(s.clone())
                })
            }
            Some(tok) => Err(ParseError::new(format!(
                "Expected identifier, got {:?}",
                tok
            ))),
            None => Err(ParseError::new("Expected identifier, got EOF".into())),
        }
    }

    /// Tries to parse a segment by name.
    /// Returns Some(Node) if it succeeds, None if it cannot be parsed (optional).
    // pub fn can_parse(&mut self, name: &str) -> Result<bool, ParseError> {
    //     // Look up the grammar for the segment
    //     let grammar = match self.get_segment_grammar(name) {
    //         Some(g) => g,
    //         None => return Err(ParseError::unknown_segment(name.to_string())),
    //     };

    //     // Save parser state in case we fail
    //     let saved_pos = self.pos;

    //     // Try parsing
    //     match self.parse_with_grammar(grammar) {
    //         Ok(_node) => {
    //             // Reset parser back; caller decides whether to consume
    //             self.pos = saved_pos;
    //             Ok(true)
    //         }
    //         Err(_) => {
    //             // Restore parser state
    //             self.pos = saved_pos;
    //             Ok(false)
    //         }
    //     }
    // }

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
        let node = self.parse_with_grammar(grammar, parent_terminators)?;

        // Wrap in a Ref node for type clarity (optional)
        Ok(Node::Ref {
            name: name.to_string(),
            child: Box::new(node),
        })
    }

    /// Lookup SegmentDef by name
    pub fn get_segment_grammar(&self, name: &str) -> Option<&'static Grammar> {
        self.dialect.get_segment_grammar(name)
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

#[derive(Debug)]
pub struct ParseError {
    message: String,
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

// pub struct Segment {
//     segment_type: String,
//     can_start_end_non_code: bool,
//     allow_empty: bool,
//     file_path: Option<String>,
//     tokens: Vec<Token>,
//     pos_marker: Option<PositionMarker>,
// }

// impl Segment {
//     pub fn root_parse(
//         &self,
//         tokens: Vec<Token>,
//         ctx: &ParseContext,
//         fname: Option<&str>,
//     ) -> Result<Segment, ParseError> {
//         let start_idx = tokens.iter().position(|t| t.is_code()).unwrap_or(0);
//         let end_idx = tokens
//             .iter()
//             .rposition(|t| t.is_code())
//             .unwrap_or(tokens.len() - 1);

//         if start_idx == end_idx {
//             return Ok(Segment {
//                 segment_type: String::from("file"),
//                 can_start_end_non_code: true,
//                 allow_empty: true,
//                 file_path: fname.map(String::from),
//                 tokens,
//                 pos_marker: None,
//             });
//         }

//         let matched = ();

//         Ok(Segment {
//             segment_type: String::from("file"),
//             can_start_end_non_code: true,
//             allow_empty: false,
//             file_path: fname.map(String::from),
//         })
//     }
// }

// pub struct Parser {
//     dialect: Dialect,
//     root_segment: Segment,
// }

// impl Parser {
//     pub fn new(dialect: Dialect) -> Self {
//         dialect.
//         Parser { dialect: dialect.clone(), }
//     }

//     pub fn parse(&self, tokens: Vec<Token>, fname: Option<&str>) -> Result<Parsed, ParseError> {
//         if tokens.is_empty() {
//             return Err(ParseError::EmptyInput);
//         }

//         let ctx = ParseContext::new(self.dialect.clone());

//         let root = self.root_segment.root_parse(tokens, &ctx)?;

//         // Parsing logic would go here.
//         Ok(Parsed {})
//     }
// }

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{
        lexer::{LexInput, Lexer},
        Dialect,
    };

    #[test]
    fn parse_select_statement() -> Result<(), ParseError> {
        let raw = "SELECT a, b FROM my_table;";
        let input = LexInput::String(raw.into());
        let dialect = Dialect::Ansi;
        let lexer = Lexer::new(None, dialect);
        let (tokens, _errors) = lexer.lex(input, false);

        println!("Tokens: {:#?}", &tokens);

        let mut parser = Parser {
            tokens: &tokens,
            pos: 0,
            dialect,
        };

        let ast = parser.call_rule("SelectStatementSegment", &[])?;
        println!("AST: {:#?}", ast);

        Ok(())
    }

    #[test]
    fn parse_select_single_item() -> Result<(), ParseError> {
        let raw = "SELECT a;";
        let input = LexInput::String(raw.into());
        let dialect = Dialect::Ansi;
        let lexer = Lexer::new(None, dialect);
        let (tokens, _errors) = lexer.lex(input, false);

        println!("Tokens: {:#?}", &tokens);

        let mut parser = Parser {
            tokens: &tokens,
            pos: 0,
            dialect,
        };

        let ast = parser.call_rule("SelectClauseSegment", &[])?;
        println!("AST: {:#?}", ast);

        Ok(())
    }

    #[test]
    fn parse_bracket() -> Result<(), ParseError> {
        let raw = "( this, that )";
        let input = LexInput::String(raw.into());
        let dialect = Dialect::Ansi;
        let lexer = Lexer::new(None, dialect);
        let (tokens, _errors) = lexer.lex(input, false);

        println!("Tokens: {:#?}", &tokens);

        let mut parser = Parser {
            tokens: &tokens,
            pos: 0,
            dialect,
        };

        let ast = parser.call_rule("BracketedColumnReferenceListGrammar", &[])?;
        println!("AST: {:#?}", ast);

        Ok(())
    }

    #[test]
    fn parse_naked_identifier() -> Result<(), ParseError> {
        let raw = "a";
        let input = LexInput::String(raw.into());
        let dialect = Dialect::Ansi;
        let lexer = Lexer::new(None, dialect);
        let (tokens, _errors) = lexer.lex(input, false);

        println!("Tokens: {:#?}", &tokens);

        let mut parser = Parser {
            tokens: &tokens,
            pos: 0,
            dialect,
        };

        let ast = parser.call_rule("BaseExpressionElementGrammar", &[])?;
        println!("AST: {:#?}", ast);

        Ok(())
    }

    #[test]
    fn parse_select_terminator() -> Result<(), ParseError> {
        let raw = "FROM";
        let input = LexInput::String(raw.into());
        let dialect = Dialect::Ansi;
        let lexer = Lexer::new(None, dialect);
        let (tokens, _errors) = lexer.lex(input, false);

        println!("Tokens: {:#?}", &tokens);

        let mut parser = Parser {
            tokens: &tokens,
            pos: 0,
            dialect,
        };

        let ast = parser.call_rule("SelectClauseTerminatorGrammar", &[])?;
        println!("AST: {:#?}", ast);

        Ok(())
    }

    #[test]
    fn parse_statements() -> Result<(), ParseError> {
        let raw = "SELECT 1; SELECT 2;";
        let input = LexInput::String(raw.into());
        let dialect = Dialect::Ansi;
        let lexer = Lexer::new(None, dialect);
        let (tokens, _errors) = lexer.lex(input, false);

        println!("Tokens: {:#?}", &tokens);

        let mut parser = Parser {
            tokens: &tokens,
            pos: 0,
            dialect,
        };

        let ast = parser.call_rule("FileSegment", &[])?;
        println!("AST: {:#?}", ast);

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

        println!("Tokens: {:#?}", &tokens);

        let mut parser = Parser {
            tokens: &tokens,
            pos: 0,
            dialect,
        };

        let ast = parser.call_rule("CreateTableStatementSegment", &[])?;
        println!("AST: {:#?}", ast);

        Ok(())
    }

    #[test]
    fn parse_datatype_segment() -> Result<(), ParseError> {
        let raw = "col1 int";
        let input = LexInput::String(raw.into());
        let dialect = Dialect::Ansi;
        let lexer = Lexer::new(None, dialect);
        let (tokens, _errors) = lexer.lex(input, false);

        println!("Tokens: {:#?}", &tokens);

        let mut parser = Parser {
            tokens: &tokens,
            pos: 0,
            dialect,
        };

        let ast = parser.call_rule("ColumnDefinitionSegment", &[])?;
        println!("AST: {:#?}", ast);

        Ok(())
    }
}
