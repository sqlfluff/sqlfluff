use std::fmt::Display;

use fancy_regex::{Regex as FancyRegex, RegexBuilder as FancyRegexBuilder};
use hashbrown::HashSet;
use regex::{Regex, RegexBuilder};

use crate::{
    dialect::Dialect,
    marker::PositionMarker,
    regex::RegexModeGroup,
    token::Token,
};

/// Legacy function pointer type for token generation (maintains backward compatibility)
/// This signature accepts individual parameters and constructs a TokenConfig internally
pub type TokenGenerator = fn(
    String,                                    // raw
    PositionMarker,                            // pos_marker
    HashSet<String>,                           // class_types
    Vec<String>,                               // instance_types
    Option<Vec<String>>,                       // trim_start
    Option<Vec<String>>,                       // trim_chars
    Option<(String, RegexModeGroup)>,          // quoted_value
    Option<(String, String)>,                  // escape_replacement
    Option<fn(&str) -> str>,                   // casefold
) -> Token;

#[derive(Debug, Clone)]
pub enum LexerMode {
    String(String),                           // Match a literal string
    Regex(Regex, fn(&str) -> bool),           // Match using a regex
    FancyRegex(FancyRegex, fn(&str) -> bool), // Match using a regex
    Function(fn(&str, Dialect) -> Option<&str>),
}

impl Display for LexerMode {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match *self {
            LexerMode::Regex(_, _) => write!(f, "RegexMatcher"),
            LexerMode::FancyRegex(_, _) => write!(f, "FancyRegexMatcher"),
            LexerMode::String(_) => write!(f, "StringMatcher"),
            LexerMode::Function(_) => write!(f, "FunctionMatcher"),
        }
    }
}

pub struct LexedElement<'a> {
    pub raw: &'a str,
    pub matcher: &'a LexMatcher,
}

impl<'a> LexedElement<'a> {
    pub fn new(raw: &'a str, matcher: &'a LexMatcher) -> Self {
        Self { raw, matcher }
    }
}

#[derive(Debug, Clone)]
pub struct LexMatcher {
    pub dialect: Dialect,
    pub name: String,
    pub mode: LexerMode,
    pub token_class_func: TokenGenerator,
    pub subdivider: Option<Box<LexMatcher>>,
    pub trim_post_subdivide: Option<Box<LexMatcher>>,
    pub trim_start: Option<Vec<String>>,
    pub trim_chars: Option<Vec<String>>,
    pub quoted_value: Option<(String, RegexModeGroup)>,
    pub escape_replacements: Option<(String, String)>,
    pub casefold: Option<fn(&str) -> str>,
    pub kwarg_type: Option<String>,
}

impl Display for LexMatcher {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "<{}: {}>", self.mode, self.name)
    }
}

impl LexMatcher {
    pub fn string_lexer(
        dialect: Dialect,
        name: &str,
        template: &str,
        token_class_func: TokenGenerator,
        subdivider: Option<Box<LexMatcher>>,
        trim_post_subdivide: Option<Box<LexMatcher>>,
        trim_start: Option<Vec<String>>,
        trim_chars: Option<Vec<String>>,
        quoted_value: Option<(String, RegexModeGroup)>,
        escape_replacements: Option<(String, String)>,
        casefold: Option<fn(&str) -> str>,
        kwarg_type: Option<String>,
    ) -> Self {
        Self {
            dialect,
            name: name.to_string(),
            mode: LexerMode::String(template.to_string()),
            token_class_func,
            subdivider,
            trim_post_subdivide,
            trim_start,
            trim_chars,
            quoted_value,
            escape_replacements,
            casefold,
            kwarg_type,
        }
    }

    fn base_regex_lexer(
        dialect: Dialect,
        name: &str,
        pattern: &str,
        token_class_func: TokenGenerator,
        subdivider: Option<Box<LexMatcher>>,
        trim_post_subdivide: Option<Box<LexMatcher>>,
        trim_start: Option<Vec<String>>,
        trim_chars: Option<Vec<String>>,
        quoted_value: Option<(String, RegexModeGroup)>,
        escape_replacements: Option<(String, String)>,
        casefold: Option<fn(&str) -> str>,
        fallback_lexer: Option<fn(&str, Dialect) -> Option<&str>>,
        precheck: fn(&str) -> bool,
        kwarg_type: Option<String>,
    ) -> Self {
        let mode = match RegexBuilder::new(&pattern).build() {
            Ok(regex) => LexerMode::Regex(regex, precheck),
            Err(_) => match FancyRegexBuilder::new(&pattern).build() {
                Ok(regex) => LexerMode::FancyRegex(regex, precheck),
                Err(_) => {
                    if let Some(fallback) = fallback_lexer {
                        LexerMode::Function(fallback)
                    } else {
                        panic!(
                            "Unable to compile regex {} and no fallback function provided",
                            pattern
                        )
                    }
                }
            },
        };

        Self {
            dialect,
            name: name.to_string(),
            mode,
            token_class_func,
            subdivider,
            trim_post_subdivide,
            trim_start,
            trim_chars,
            quoted_value,
            escape_replacements,
            casefold,
            kwarg_type,
        }
    }

    pub fn regex_lexer(
        dialect: Dialect,
        name: &str,
        template: &str,
        token_class_func: TokenGenerator,
        subdivider: Option<Box<LexMatcher>>,
        trim_post_subdivide: Option<Box<LexMatcher>>,
        trim_start: Option<Vec<String>>,
        trim_chars: Option<Vec<String>>,
        quoted_value: Option<(String, RegexModeGroup)>,
        escape_replacements: Option<(String, String)>,
        casefold: Option<fn(&str) -> str>,
        fallback_lexer: Option<fn(&str, Dialect) -> Option<&str>>,
        precheck: fn(&str) -> bool,
        kwarg_type: Option<String>,
    ) -> Self {
        let pattern = format!(r"(?s)\A(?:{})", template);
        Self::base_regex_lexer(
            dialect,
            name,
            &pattern,
            token_class_func,
            subdivider,
            trim_post_subdivide,
            trim_start,
            trim_chars,
            quoted_value,
            escape_replacements,
            casefold,
            fallback_lexer,
            precheck,
            kwarg_type,
        )
    }

    pub fn regex_subdivider(
        dialect: Dialect,
        name: &str,
        template: &str,
        token_class_func: TokenGenerator,
        subdivider: Option<Box<LexMatcher>>,
        trim_post_subdivide: Option<Box<LexMatcher>>,
        trim_start: Option<Vec<String>>,
        trim_chars: Option<Vec<String>>,
        quoted_value: Option<(String, RegexModeGroup)>,
        escape_replacements: Option<(String, String)>,
        casefold: Option<fn(&str) -> str>,
        fallback_lexer: Option<fn(&str, Dialect) -> Option<&str>>,
        precheck: fn(&str) -> bool,
        kwarg_type: Option<String>,
    ) -> Self {
        let pattern = format!(r"(?:{})", template);
        Self::base_regex_lexer(
            dialect,
            name,
            &pattern,
            token_class_func,
            subdivider,
            trim_post_subdivide,
            trim_start,
            trim_chars,
            quoted_value,
            escape_replacements,
            casefold,
            fallback_lexer,
            precheck,
            kwarg_type,
        )
    }

    pub fn scan_match<'a>(&'a self, input: &'a str) -> Option<(Vec<LexedElement<'a>>, usize)> {
        // let t = Instant::now();
        if input.is_empty() {
            panic!("Unexpected empty string!");
        }

        // Match based on the mode
        let matched = match &self.mode {
            LexerMode::String(template) => input
                .starts_with(template)
                .then(|| LexedElement::new(template, self)),
            LexerMode::Regex(regex, is_match_valid) => {
                if !(is_match_valid)(input) {
                    // println!("{},{}", self.name, t.elapsed().as_nanos());
                    return None;
                }
                regex
                    .find(input)
                    .map(|mat| LexedElement::new(mat.as_str(), self))
            }
            LexerMode::FancyRegex(regex, is_match_valid) => {
                if !(is_match_valid)(input) {
                    // println!("{},{}", self.name, t.elapsed().as_nanos());
                    return None;
                }
                regex
                    .find(input)
                    .ok()
                    .flatten()
                    .map(|mat| LexedElement::new(mat.as_str(), self))
            }
            LexerMode::Function(function) => {
                (function)(input, self.dialect).map(|s| LexedElement::new(s, self))
            }
        };
        // println!("{},{}", self.name, t.elapsed().as_nanos());

        // Handle subdivision and trimming
        if let Some(matched) = matched {
            let len = matched.raw.len();
            let elements = self.subdivide(matched);
            Some((elements, len))
        } else {
            None
        }
    }

    fn search(&self, input: &str) -> Option<(usize, usize)> {
        match &self.mode {
            LexerMode::String(template) => input.find(template).map(|start| {
                let end = start + template.len();
                (start, end)
            }),
            LexerMode::Regex(regex, _) => regex.find(input).map(|mat| (mat.start(), mat.end())),
            LexerMode::FancyRegex(regex, _) => regex
                .find(input)
                .ok()
                .flatten()
                .map(|mat| (mat.start(), mat.end())),
            _ => todo!(),
        }
    }

    fn subdivide<'a>(&'a self, matched: LexedElement<'a>) -> Vec<LexedElement<'a>> {
        if let Some(subdivider) = &self.subdivider {
            let mut elements = Vec::new();
            let mut buffer = matched.raw;
            while !buffer.is_empty() {
                if let Some((start, end)) = subdivider.search(buffer) {
                    let trimmed_elems = self.trim_match(&buffer[..start]);
                    elements.extend(trimmed_elems);
                    elements.push(LexedElement {
                        raw: &buffer[start..end],
                        matcher: subdivider,
                    });
                    buffer = &buffer[end..];
                } else {
                    let trimmed_elems = self.trim_match(buffer);
                    elements.extend(trimmed_elems);
                    break;
                }
            }
            elements
        } else {
            vec![matched]
        }
    }

    fn trim_match<'a>(&'a self, raw: &'a str) -> Vec<LexedElement<'a>> {
        let mut elements = Vec::new();
        let mut buffer = raw;
        let mut content_buffer = 0..0;

        if let Some(trim_post_subdivide) = &self.trim_post_subdivide {
            while !buffer.is_empty() {
                if let Some((start, end)) = trim_post_subdivide.search(buffer) {
                    if start == 0 {
                        // Starting match
                        elements.push(LexedElement {
                            raw: &buffer[..end],
                            matcher: trim_post_subdivide,
                        });
                        buffer = &buffer[end..];
                        content_buffer = end..end;
                    } else if end == buffer.len() {
                        elements.push(LexedElement {
                            raw: &raw[content_buffer.start..content_buffer.end + start],
                            matcher: self,
                        });
                        elements.push(LexedElement {
                            raw: &buffer[start..end],
                            matcher: trim_post_subdivide,
                        });
                        return elements;
                    } else {
                        content_buffer.end += end;
                        buffer = &buffer[end..];
                    }
                } else {
                    break;
                }
            }
        }
        if !content_buffer.is_empty() || !buffer.is_empty() {
            elements.push(LexedElement::new(&raw[content_buffer.start..], self));
        }
        elements
    }

    pub fn construct_token(&self, raw: &str, pos_marker: PositionMarker) -> Token {
        let instance_types = match self.kwarg_type.clone() {
            Some(t) => vec![t],
            None => vec![self.name.clone()],
        };

        (self.token_class_func)(
            raw.to_string(),
            pos_marker,
            HashSet::new(),
            instance_types,
            self.trim_start.clone(),
            self.trim_chars.clone(),
            self.quoted_value.clone(),
            self.escape_replacements.clone(),
            self.casefold,
        )
    }
}

pub fn extract_nested_block_comment(input: &str, dialect: Dialect) -> Option<&str> {
    let mut chars = input.chars().peekable();
    let mut comment = String::new();

    // Ensure the input starts with "/*"
    if chars.next() != Some('/') || chars.next() != Some('*') {
        return None;
    }

    comment.push_str("/*"); // Add the opening delimiter
    let mut depth = 1; // Track nesting level

    while let Some(c) = chars.next() {
        comment.push(c);

        if c == '/' && chars.peek() == Some(&'*') {
            chars.next(); // Consume '*'
            comment.push('*');
            depth += 1;
        } else if c == '*' && chars.peek() == Some(&'/') {
            chars.next(); // Consume '/'
            comment.push('/');
            depth -= 1;

            if depth == 0 {
                return Some(&input[..comment.len()]);
            }
        }
    }

    // If we reach here, the comment wasn't properly closed
    match &dialect {
        Dialect::Sqlite => Some(&input[..comment.len()]),
        _ => None,
    }
}

// TODO: implement python passthroughs
#[cfg(feature = "python")]
pub mod python {}

#[cfg(test)]
mod test {
    use crate::{dialect::Dialect, token::Token};

    use super::{extract_nested_block_comment, LexMatcher};

    #[test]
    fn test_subdivide() {
        let block_comment_matcher = LexMatcher::regex_lexer(
            Dialect::Ansi,
            "block_comment",
            r#"\/\*([^\*]|\*(?!\/))*\*\/"#,
            Token::comment_token_compat,
            Some(Box::new(LexMatcher::regex_subdivider(
                Dialect::Ansi,
                "newline",
                r#"\r\n|\n"#,
                Token::newline_token_compat,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                |_| true,
                None,
            ))),
            Some(Box::new(LexMatcher::regex_subdivider(
                Dialect::Ansi,
                "whitespace",
                r#"[^\S\r\n]+"#,
                Token::whitespace_token_compat,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                |_| true,
                None,
            ))),
            None,
            None,
            None,
            None,
            None,
            Some(extract_nested_block_comment),
            |input| input.starts_with("/"),
            None,
        );

        let (elems, _) = block_comment_matcher
            .scan_match("/*\n)\n*/")
            .expect("should match");
        for elem in elems {
            println!("{}: {}", elem.matcher.name, elem.raw);
        }
    }
}
