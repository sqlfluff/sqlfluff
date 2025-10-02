use std::vec;

use crate::{dialect::matcher::Dialect, token::Token};

#[derive(Debug, Clone, PartialEq)]
pub enum Grammar {
    Sequence {
        elements: Vec<Grammar>,
        optional: bool,
        terminators: Vec<Grammar>,
        allow_gaps: bool,
    },
    AnyNumberOf {
        element: Box<Grammar>,
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
        allow_gaps: bool,
    },
    Keyword {
        name: &'static str,
        optional: bool,
        allow_gaps: bool,
    },
    Symbol(&'static str),
    Empty,
}

pub struct SegmentDef {
    pub name: &'static str,
    pub grammar: Grammar,
}

#[derive(Debug, Clone, PartialEq)]
pub enum Node {
    /// A plain SQL keyword like SELECT, FROM, INTO
    Keyword(String),

    Symbol(String),

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
}

pub struct Parser<'a> {
    tokens: &'a [Token],
    pos: usize, // current position in tokens
    dialect: Dialect,
}

impl Parser<'_> {
    fn parse_with_grammar(&mut self, grammar: &Grammar) -> Result<Node, ParseError> {
        dbg!("Parsing with grammar: {:?}", grammar);
        match grammar {
            Grammar::Keyword {
                name,
                optional,
                allow_gaps,
            } => {
                dbg!("Expecting keyword: {}", name);
                self.expect_keyword(name, *allow_gaps)
            }
            Grammar::Symbol(sym) => {
                dbg!("Expecting symbol: {}", sym);
                match self.peek() {
                    Some(t) if t.raw() == *sym => {
                        self.bump();
                        Ok(Node::Symbol(sym.to_string()))
                    }
                    _ => Err(ParseError::new(format!("Expected symbol '{}'", sym))),
                }
            }
            Grammar::Ref {
                name,
                optional,
                allow_gaps,
            } => {
                self.skip_transparent(*allow_gaps);
                dbg!("Ref to segment: {}, optional: {}", name, optional);
                if *name == "Identifier" {
                    self.skip_transparent(*allow_gaps);
                    Ok(self.parse_identifier()?)
                } else if *optional && !self.can_parse(name)? {
                    Ok(Node::Empty)
                } else {
                    self.call_rule(name)
                }
            }
            Grammar::Sequence {
                elements,
                optional,
                terminators,
                allow_gaps,
            } => {
                dbg!("Sequence elements: {:?}", elements);
                let saved = self.pos;
                let mut children = vec![];
                for element in elements {
                    dbg!("Sequence element: {:?}", element);
                    if self.is_terminated(terminators) {
                        dbg!("Sequence terminated!");
                        break;
                    }
                    match self.parse_with_grammar(element) {
                        Ok(node) => children.push(node),
                        Err(e) => {
                            if *optional {
                                dbg!("Sequence element optional, skipping");
                                self.pos = saved; // whole sequence optional → rewind
                                return Ok(Node::Empty);
                            } else {
                                return Err(e);
                            }
                        }
                    }
                }
                dbg!("Sequence children: {:?}", &children);
                Ok(Node::Sequence(children))
            }
            Grammar::OneOf {
                elements,
                optional,
                terminators,
                allow_gaps,
            } => {
                dbg!("OneOf elements: {:?}", elements);
                let saved = self.pos;
                for element in elements {
                    if self.is_terminated(terminators) {
                        break;
                    }
                    let attempt = self.parse_with_grammar(element);
                    if attempt.is_ok() {
                        return Ok(Node::OneOf(Box::new(attempt?)));
                    }
                }

                if *optional {
                    self.pos = saved;
                    Ok(Node::Empty)
                } else {
                    Err(ParseError::new("Expected one of choices".into()))
                }
            }
            Grammar::AnyNumberOf {
                element,
                min_times,
                max_times,
                optional,
                terminators,
                allow_gaps,
            } => {
                dbg!("AnyNumberOf element: {:?}", element);
                let mut items = vec![];
                let mut count = 0;

                loop {
                    if self.is_terminated(terminators) {
                        break;
                    }

                    let saved_pos = self.pos;
                    match self.parse_with_grammar(element) {
                        Ok(node) => {
                            items.push(node);
                            count += 1;
                            if let Some(max) = max_times {
                                if count >= *max {
                                    break;
                                }
                            }
                        }
                        Err(_) => {
                            self.pos = saved_pos; // rewind
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
                dbg!("Delimited elements: {:?}", elements);
                let mut items = vec![];

                if *optional && (self.is_at_end() || self.is_terminated(terminators)) {
                    dbg!("Delimited: empty optional");
                    return Ok(Node::DelimitedList(items));
                }

                loop {
                    if self.is_terminated(terminators) {
                        break;
                    }

                    // match one element
                    self.skip_transparent(*allow_gaps);
                    let mut matched = false;
                    let saved_pos = self.pos;
                    for elem in elements {
                        match self.parse_with_grammar(elem) {
                            Ok(node) => {
                                items.push(node);
                                matched = true;
                                break;
                            }
                            Err(_) => self.pos = saved_pos,
                        }
                    }

                    if !matched {
                        dbg!("Delimited: no more elements matched");
                        break;
                    }

                    // try delimiter
                    self.skip_transparent(*allow_gaps);
                    let saved_pos = self.pos;
                    if let Ok(delim_node) = self.parse_with_grammar(delimiter) {
                        // check if element follows
                        if self.is_terminated(terminators) {
                            if !*allow_trailing {
                                return Err(ParseError::new(
                                    "Trailing delimiter not allowed".to_string(),
                                ));
                            }
                            break;
                        }
                        dbg!("Delimited: found delimiter");
                        items.push(delim_node);
                    } else {
                        self.pos = saved_pos;
                        dbg!("Delimited: no delimiter found, ending");
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
                dbg!("Bracketed elements: {:?}", elements);
                let saved_pos = self.pos;
                self.skip_transparent(*allow_gaps);
                // Expect opening bracket
                match self.parse_with_grammar(&bracket_pairs.0) {
                    Ok(open_node) => {
                        let mut children = vec![open_node];

                        // Try to parse elements until we can't anymore
                        let mut last_successful_pos = self.pos;
                        loop {
                            if self.is_terminated(terminators) {
                                break;
                            }

                            // Skip transparent tokens before each element
                            self.skip_transparent(*allow_gaps);

                            // Try to match each element type
                            let mut matched = false;
                            let saved_inner_pos = self.pos;
                            for elem in elements {
                                match self.parse_with_grammar(elem) {
                                    Ok(node) => {
                                        children.push(node);
                                        matched = true;
                                        last_successful_pos = self.pos;
                                        break;
                                    }
                                    Err(_) => self.pos = saved_inner_pos,
                                }
                            }

                            // If we didn't match any element, or haven't made progress, break
                            if !matched || self.pos <= last_successful_pos {
                                self.pos = last_successful_pos;  // Restore to last good position
                                break;
                            }
                        }
                        // Expect closing bracket
                        self.skip_transparent(*allow_gaps);
                        match self.parse_with_grammar(&bracket_pairs.1) {
                            Ok(close_node) => {
                                children.push(close_node);
                                Ok(Node::Sequence(children))
                            }
                            Err(e) => Err(ParseError::new(format!(
                                "Expected closing bracket: {}",
                                e.message
                            ))),
                        }
                    }
                    Err(e) => {
                        if *optional {
                            self.pos = saved_pos;
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
                tok if !tok.is_code() => self.bump(),
                _ => break,
            }
        }
    }

    fn is_terminated(&mut self, terminators: &[Grammar]) -> bool {
        self.skip_transparent(true);
        let saved_pos = self.pos;
        dbg!(
            "Checking terminators: {:?} at pos {:?}",
            terminators,
            self.pos
        );
        for term in terminators {
            if self.parse_with_grammar(term).is_ok() {
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
    pub fn can_parse(&mut self, name: &str) -> Result<bool, ParseError> {
        // Look up the grammar for the segment
        let grammar = match self.get_segment_grammar(name) {
            Some(g) => g,
            None => return Err(ParseError::unknown_segment(name.to_string())),
        };

        // Save parser state in case we fail
        let saved_pos = self.pos;

        // Try parsing
        match self.parse_with_grammar(grammar) {
            Ok(_node) => {
                // Reset parser back; caller decides whether to consume
                self.pos = saved_pos;
                Ok(true)
            }
            Err(_) => {
                // Restore parser state
                self.pos = saved_pos;
                Ok(false)
            }
        }
    }

    /// Call a grammar rule by name, producing a Node.
    pub fn call_rule(&mut self, name: &str) -> Result<Node, ParseError> {
        // Look up the grammar for the segment
        let grammar = match self.get_segment_grammar(name) {
            Some(g) => g,
            None => return Err(ParseError::unknown_segment(name.to_string())),
        };

        // Parse using the grammar
        let node = self.parse_with_grammar(grammar)?;

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
    fn parse_select_delimited() -> Result<(), ParseError> {
        let raw = "SELECT a, b FROM my_table;";
        let input = LexInput::String(raw.into());
        let dialect = Dialect::Postgres;
        let lexer = Lexer::new(None, dialect);
        let (tokens, _errors) = lexer.lex(input, false);

        dbg!("Tokens: {:#?}", &tokens);

        let mut parser = Parser {
            tokens: &tokens,
            pos: 0,
            dialect,
        };

        let ast = parser.call_rule("SelectClauseSegment")?;
        println!("AST: {:#?}", ast);

        Ok(())
    }

    #[test]
    fn parse_select_single_item() -> Result<(), ParseError> {
        let raw = "SELECT a;";
        let input = LexInput::String(raw.into());
        let dialect = Dialect::Postgres;
        let lexer = Lexer::new(None, dialect);
        let (tokens, _errors) = lexer.lex(input, false);

        dbg!("Tokens: {:#?}", &tokens);

        let mut parser = Parser {
            tokens: &tokens,
            pos: 0,
            dialect,
        };

        let ast = parser.call_rule("SelectClauseSegment")?;
        println!("AST: {:#?}", ast);

        Ok(())
    }

    #[test]
    fn parse_bracket() -> Result<(), ParseError> {
        let raw = "( this, that )";
        let input = LexInput::String(raw.into());
        let dialect = Dialect::Postgres;
        let lexer = Lexer::new(None, dialect);
        let (tokens, _errors) = lexer.lex(input, false);

        dbg!("Tokens: {:#?}", &tokens);

        let mut parser = Parser {
            tokens: &tokens,
            pos: 0,
            dialect,
        };

        let ast = parser.call_rule("BracketedColumnReferenceListGrammar")?;
        println!("AST: {:#?}", ast);

        Ok(())
    }
}
