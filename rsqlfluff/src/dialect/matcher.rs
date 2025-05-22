/* This is a generated file! */
use once_cell::sync::Lazy;
use uuid::Uuid;
use crate::matcher::{LexMatcher, extract_nested_block_comment};
use std::str::FromStr;
use crate::token::Token;

pub static ANSI_LEXERS: Lazy<Vec<LexMatcher>> = Lazy::new(|| { vec![

    LexMatcher::regex_lexer(
        Dialect::Ansi,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Ansi,
        "inline_comment",
        r#"(--|#)[^\n]*"#,
        Token::comment_token,
        None,
        None,
        Some(vec![String::from("--"), String::from("#")]),
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['#','-','/']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Ansi,
        "block_comment",
        r#"\/\*([^\*]|\*(?!\/))*\*\/"#,
        Token::comment_token,
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Ansi,
        "newline",
        r#"\r\n|\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Ansi,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        None,
        None,
        Uuid::new_v4().to_string(),
        Some(extract_nested_block_comment),
        |input| input.starts_with("/"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Ansi,
        "single_quote",
        r#"'([^'\\]|\\.|'')*'"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'\'', ..] => true,                     // Single quote case
        [b'R' | b'r', b'\'', ..] => true,        // r' or R'
        [b'B' | b'b', b'\'', ..] => true,        // b' or B'
        [b'R' | b'r', b'B' | b'b', b'\'', ..] => true, // rb', RB', etc.
        [b'B' | b'b', b'R' | b'r', b'\'', ..] => true, // br', Br', etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Ansi,
        "double_quote",
        r#""(""|[^"\\]|\\.)*""#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'"', ..] => true,                     // Just a double quote
        [b'R' | b'r', b'"', ..] => true,        // r" or R"
        [b'B' | b'b', b'"', ..] => true,        // b" or B"
        [b'R' | b'r', b'B' | b'b', b'"', ..] => true, // rb", RB", etc.
        [b'B' | b'b', b'R' | b'r', b'"', ..] => true, // br", Br", etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Ansi,
        "back_quote",
        r#"`(?:[^`\\]|\\.)*`"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Ansi,
        "dollar_quote",
        r#"\$(\w*)\$(.*?)\$\1\$"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with("$"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Ansi,
        "numeric_literal",
        r#"(?>\d+\.\d+|\d+\.(?![\.\w])|\.\d+|\d+)(\.?[eE][+-]?\d+)?((?<=\.)|(?=\b))"#,
        Token::literal_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['.','0','1','2','3','4','5','6','7','8','9']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Ansi,
        "like_operator",
        r#"!?~~?\*?"#,
        Token::comparison_operator_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Ansi,
        "newline",
        r#"\r?\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::string_lexer(
        Dialect::Ansi,
        "casting_operator",
        "::",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Ansi,
        "equals",
        "=",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Ansi,
        "greater_than",
        ">",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Ansi,
        "less_than",
        "<",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Ansi,
        "not",
        "!",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Ansi,
        "dot",
        ".",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Ansi,
        "comma",
        ",",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Ansi,
        "plus",
        "+",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Ansi,
        "minus",
        "-",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Ansi,
        "divide",
        "/",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Ansi,
        "percent",
        "%",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Ansi,
        "question",
        "?",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Ansi,
        "ampersand",
        "&",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Ansi,
        "vertical_bar",
        "|",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Ansi,
        "caret",
        "^",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Ansi,
        "star",
        "*",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Ansi,
        "start_bracket",
        "(",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Ansi,
        "end_bracket",
        ")",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Ansi,
        "start_square_bracket",
        "[",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Ansi,
        "end_square_bracket",
        "]",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Ansi,
        "start_curly_bracket",
        "{",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Ansi,
        "end_curly_bracket",
        "}",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Ansi,
        "colon",
        ":",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Ansi,
        "semicolon",
        ";",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Ansi,
        "word",
        r#"[0-9a-zA-Z_]+"#,
        Token::word_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),
]});
pub static ATHENA_LEXERS: Lazy<Vec<LexMatcher>> = Lazy::new(|| { vec![

    LexMatcher::regex_lexer(
        Dialect::Athena,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Athena,
        "inline_comment",
        r#"(--|#)[^\n]*"#,
        Token::comment_token,
        None,
        None,
        Some(vec![String::from("--"), String::from("#")]),
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['#','-','/']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Athena,
        "block_comment",
        r#"\/\*([^\*]|\*(?!\/))*\*\/"#,
        Token::comment_token,
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Athena,
        "newline",
        r#"\r\n|\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Athena,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        None,
        None,
        Uuid::new_v4().to_string(),
        Some(extract_nested_block_comment),
        |input| input.starts_with("/"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Athena,
        "single_quote",
        r#"'([^'\\]|\\.|'')*'"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'\'', ..] => true,                     // Single quote case
        [b'R' | b'r', b'\'', ..] => true,        // r' or R'
        [b'B' | b'b', b'\'', ..] => true,        // b' or B'
        [b'R' | b'r', b'B' | b'b', b'\'', ..] => true, // rb', RB', etc.
        [b'B' | b'b', b'R' | b'r', b'\'', ..] => true, // br', Br', etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Athena,
        "double_quote",
        r#""(""|[^"\\]|\\.)*""#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'"', ..] => true,                     // Just a double quote
        [b'R' | b'r', b'"', ..] => true,        // r" or R"
        [b'B' | b'b', b'"', ..] => true,        // b" or B"
        [b'R' | b'r', b'B' | b'b', b'"', ..] => true, // rb", RB", etc.
        [b'B' | b'b', b'R' | b'r', b'"', ..] => true, // br", Br", etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Athena,
        "back_quote",
        r#"`(?:[^`\\]|\\.)*`"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Athena,
        "dollar_quote",
        r#"\$(\w*)\$(.*?)\$\1\$"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with("$"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Athena,
        "numeric_literal",
        r#"(?>\d+\.\d+|\d+\.(?![\.\w])|\.\d+|\d+)(\.?[eE][+-]?\d+)?((?<=\.)|(?=\b))"#,
        Token::literal_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['.','0','1','2','3','4','5','6','7','8','9']),
    ),

    LexMatcher::string_lexer(
        Dialect::Athena,
        "right_arrow",
        "->",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Athena,
        "like_operator",
        r#"!?~~?\*?"#,
        Token::comparison_operator_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Athena,
        "newline",
        r#"\r?\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::string_lexer(
        Dialect::Athena,
        "casting_operator",
        "::",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Athena,
        "equals",
        "=",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Athena,
        "greater_than",
        ">",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Athena,
        "less_than",
        "<",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Athena,
        "not",
        "!",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Athena,
        "dot",
        ".",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Athena,
        "comma",
        ",",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Athena,
        "plus",
        "+",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Athena,
        "minus",
        "-",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Athena,
        "divide",
        "/",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Athena,
        "percent",
        "%",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Athena,
        "question",
        "?",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Athena,
        "ampersand",
        "&",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Athena,
        "vertical_bar",
        "|",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Athena,
        "caret",
        "^",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Athena,
        "star",
        "*",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Athena,
        "start_bracket",
        "(",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Athena,
        "end_bracket",
        ")",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Athena,
        "start_square_bracket",
        "[",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Athena,
        "end_square_bracket",
        "]",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Athena,
        "start_curly_bracket",
        "{",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Athena,
        "end_curly_bracket",
        "}",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Athena,
        "colon",
        ":",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Athena,
        "semicolon",
        ";",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Athena,
        "word",
        r#"[0-9a-zA-Z_]+"#,
        Token::word_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),
]});
pub static BIGQUERY_LEXERS: Lazy<Vec<LexMatcher>> = Lazy::new(|| { vec![

    LexMatcher::regex_lexer(
        Dialect::Bigquery,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Bigquery,
        "inline_comment",
        r#"(--|#)[^\n]*"#,
        Token::comment_token,
        None,
        None,
        Some(vec![String::from("--"), String::from("#")]),
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['#','-','/']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Bigquery,
        "block_comment",
        r#"\/\*([^\*]|\*(?!\/))*\*\/"#,
        Token::comment_token,
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Bigquery,
        "newline",
        r#"\r\n|\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Bigquery,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        None,
        None,
        Uuid::new_v4().to_string(),
        Some(extract_nested_block_comment),
        |input| input.starts_with("/"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Bigquery,
        "single_quote",
        r#"([rR]?[bB]?|[bB]?[rR]?)?('''((?<!\\)(\\{2})*\\'|'{,2}(?!')|[^'])*(?<!\\)(\\{2})*'''|'((?<!\\)(\\{2})*\\'|[^'])*(?<!\\)(\\{2})*')"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'\'', ..] => true,                     // Single quote case
        [b'R' | b'r', b'\'', ..] => true,        // r' or R'
        [b'B' | b'b', b'\'', ..] => true,        // b' or B'
        [b'R' | b'r', b'B' | b'b', b'\'', ..] => true, // rb', RB', etc.
        [b'B' | b'b', b'R' | b'r', b'\'', ..] => true, // br', Br', etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Bigquery,
        "double_quote",
        r#"([rR]?[bB]?|[bB]?[rR]?)?(\"\"\"((?<!\\)(\\{2})*\\\"|\"{,2}(?!\")|[^\"])*(?<!\\)(\\{2})*\"\"\"|"((?<!\\)(\\{2})*\\"|[^"])*(?<!\\)(\\{2})*")"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'"', ..] => true,                     // Just a double quote
        [b'R' | b'r', b'"', ..] => true,        // r" or R"
        [b'B' | b'b', b'"', ..] => true,        // b" or B"
        [b'R' | b'r', b'B' | b'b', b'"', ..] => true, // rb", RB", etc.
        [b'B' | b'b', b'R' | b'r', b'"', ..] => true, // br", Br", etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Bigquery,
        "back_quote",
        r#"`(?:[^`\\]|\\.)*`"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Bigquery,
        "dollar_quote",
        r#"\$(\w*)\$(.*?)\$\1\$"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with("$"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Bigquery,
        "numeric_literal",
        r#"(?>\d+\.\d+|\d+\.(?![\.\w])|\.\d+|\d+)(\.?[eE][+-]?\d+)?((?<=\.)|(?=\b))"#,
        Token::literal_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['.','0','1','2','3','4','5','6','7','8','9']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Bigquery,
        "like_operator",
        r#"!?~~?\*?"#,
        Token::comparison_operator_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Bigquery,
        "newline",
        r#"\r?\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::string_lexer(
        Dialect::Bigquery,
        "casting_operator",
        "::",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Bigquery,
        "right_arrow",
        "=>",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Bigquery,
        "question_mark",
        "?",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Bigquery,
        "at_sign_literal",
        r#"@[a-zA-Z_][\w]*"#,
        Token::literal_token,
        None,
        None,
        None,
        Some(vec![String::from("@")]),
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Bigquery,
        "double_at_sign_literal",
        r#"@@[a-zA-Z_][\w\.]*"#,
        Token::literal_token,
        None,
        None,
        None,
        Some(vec![String::from("@@")]),
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::string_lexer(
        Dialect::Bigquery,
        "equals",
        "=",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Bigquery,
        "greater_than",
        ">",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Bigquery,
        "less_than",
        "<",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Bigquery,
        "not",
        "!",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Bigquery,
        "dot",
        ".",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Bigquery,
        "comma",
        ",",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Bigquery,
        "plus",
        "+",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Bigquery,
        "minus",
        "-",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Bigquery,
        "divide",
        "/",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Bigquery,
        "percent",
        "%",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Bigquery,
        "question",
        "?",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Bigquery,
        "ampersand",
        "&",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Bigquery,
        "vertical_bar",
        "|",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Bigquery,
        "caret",
        "^",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Bigquery,
        "star",
        "*",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Bigquery,
        "start_bracket",
        "(",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Bigquery,
        "end_bracket",
        ")",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Bigquery,
        "start_square_bracket",
        "[",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Bigquery,
        "end_square_bracket",
        "]",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Bigquery,
        "start_curly_bracket",
        "{",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Bigquery,
        "end_curly_bracket",
        "}",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Bigquery,
        "colon",
        ":",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Bigquery,
        "semicolon",
        ";",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Bigquery,
        "word",
        r#"[0-9a-zA-Z_]+"#,
        Token::word_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),
]});
pub static CLICKHOUSE_LEXERS: Lazy<Vec<LexMatcher>> = Lazy::new(|| { vec![

    LexMatcher::regex_lexer(
        Dialect::Clickhouse,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Clickhouse,
        "inline_comment",
        r#"(--|#)[^\n]*"#,
        Token::comment_token,
        None,
        None,
        Some(vec![String::from("--"), String::from("#")]),
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['#','-','/']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Clickhouse,
        "block_comment",
        r#"\/\*([^\*]|\*(?!\/))*\*\/"#,
        Token::comment_token,
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Clickhouse,
        "newline",
        r#"\r\n|\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Clickhouse,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        None,
        None,
        Uuid::new_v4().to_string(),
        Some(extract_nested_block_comment),
        |input| input.starts_with("/"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Clickhouse,
        "single_quote",
        r#"'([^'\\]|\\.|'')*'"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'\'', ..] => true,                     // Single quote case
        [b'R' | b'r', b'\'', ..] => true,        // r' or R'
        [b'B' | b'b', b'\'', ..] => true,        // b' or B'
        [b'R' | b'r', b'B' | b'b', b'\'', ..] => true, // rb', RB', etc.
        [b'B' | b'b', b'R' | b'r', b'\'', ..] => true, // br', Br', etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Clickhouse,
        "double_quote",
        r#""([^"\\]|""|\\.)*""#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'"', ..] => true,                     // Just a double quote
        [b'R' | b'r', b'"', ..] => true,        // r" or R"
        [b'B' | b'b', b'"', ..] => true,        // b" or B"
        [b'R' | b'r', b'B' | b'b', b'"', ..] => true, // rb", RB", etc.
        [b'B' | b'b', b'R' | b'r', b'"', ..] => true, // br", Br", etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Clickhouse,
        "back_quote",
        r#"`(?:[^`\\]|``|\\.)*`"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Clickhouse,
        "dollar_quote",
        r#"\$(\w*)\$(.*?)\$\1\$"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with("$"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Clickhouse,
        "numeric_literal",
        r#"(?>\d+\.\d+|\d+\.(?![\.\w])|\.\d+|\d+)(\.?[eE][+-]?\d+)?((?<=\.)|(?=\b))"#,
        Token::literal_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['.','0','1','2','3','4','5','6','7','8','9']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Clickhouse,
        "like_operator",
        r#"!?~~?\*?"#,
        Token::comparison_operator_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::string_lexer(
        Dialect::Clickhouse,
        "lambda",
        "->",
        Token::symbol_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Clickhouse,
        "newline",
        r#"\r?\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::string_lexer(
        Dialect::Clickhouse,
        "casting_operator",
        "::",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Clickhouse,
        "equals",
        "=",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Clickhouse,
        "greater_than",
        ">",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Clickhouse,
        "less_than",
        "<",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Clickhouse,
        "not",
        "!",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Clickhouse,
        "dot",
        ".",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Clickhouse,
        "comma",
        ",",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Clickhouse,
        "plus",
        "+",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Clickhouse,
        "minus",
        "-",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Clickhouse,
        "divide",
        "/",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Clickhouse,
        "percent",
        "%",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Clickhouse,
        "question",
        "?",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Clickhouse,
        "ampersand",
        "&",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Clickhouse,
        "vertical_bar",
        "|",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Clickhouse,
        "caret",
        "^",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Clickhouse,
        "star",
        "*",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Clickhouse,
        "start_bracket",
        "(",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Clickhouse,
        "end_bracket",
        ")",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Clickhouse,
        "start_square_bracket",
        "[",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Clickhouse,
        "end_square_bracket",
        "]",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Clickhouse,
        "start_curly_bracket",
        "{",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Clickhouse,
        "end_curly_bracket",
        "}",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Clickhouse,
        "colon",
        ":",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Clickhouse,
        "semicolon",
        ";",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Clickhouse,
        "word",
        r#"[0-9a-zA-Z_]+"#,
        Token::word_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),
]});
pub static DATABRICKS_LEXERS: Lazy<Vec<LexMatcher>> = Lazy::new(|| { vec![

    LexMatcher::regex_lexer(
        Dialect::Databricks,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Databricks,
        "notebook_start",
        r#"-- Databricks notebook source(\r?\n){1}"#,
        Token::comment_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Databricks,
        "magic_line",
        r#"(-- MAGIC)( [^%]{1})([^\n]*)"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Databricks,
        "magic_start",
        r#"(-- MAGIC %)([^\n]{2,})(\r?\n)"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Databricks,
        "inline_comment",
        r#"(--)[^\n]*"#,
        Token::comment_token,
        None,
        None,
        Some(vec![String::from("-"), String::from("-")]),
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['#','-','/']),
    ),

    LexMatcher::string_lexer(
        Dialect::Databricks,
        "start_hint",
        "/*+",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Databricks,
        "block_comment",
        r#"\/\*([^\*]|\*(?!\/))*\*\/"#,
        Token::comment_token,
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Databricks,
        "newline",
        r#"\r\n|\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Databricks,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        None,
        None,
        Uuid::new_v4().to_string(),
        Some(extract_nested_block_comment),
        |input| input.starts_with("/"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Databricks,
        "raw_single_quote",
        r#"[rR]'([^'\\]|\\.)*'"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Databricks,
        "raw_double_quote",
        r#"[rR]"([^"\\]|\\.)*""#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Databricks,
        "bytes_single_quote",
        r#"X'([^'\\]|\\.)*'"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Databricks,
        "bytes_double_quote",
        r#"X"([^"\\]|\\.)*""#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::string_lexer(
        Dialect::Databricks,
        "end_hint",
        "*/",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Databricks,
        "single_quote",
        r#"'([^'\\]|\\.|'')*'"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'\'', ..] => true,                     // Single quote case
        [b'R' | b'r', b'\'', ..] => true,        // r' or R'
        [b'B' | b'b', b'\'', ..] => true,        // b' or B'
        [b'R' | b'r', b'B' | b'b', b'\'', ..] => true, // rb', RB', etc.
        [b'B' | b'b', b'R' | b'r', b'\'', ..] => true, // br', Br', etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Databricks,
        "double_quote",
        r#""(""|[^"\\]|\\.)*""#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'"', ..] => true,                     // Just a double quote
        [b'R' | b'r', b'"', ..] => true,        // r" or R"
        [b'B' | b'b', b'"', ..] => true,        // b" or B"
        [b'R' | b'r', b'B' | b'b', b'"', ..] => true, // rb", RB", etc.
        [b'B' | b'b', b'R' | b'r', b'"', ..] => true, // br", Br", etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Databricks,
        "back_quote",
        r#"`([^`]|``)*`"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Databricks,
        "dollar_quote",
        r#"\$(\w*)\$(.*?)\$\1\$"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with("$"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Databricks,
        "numeric_literal",
        r#"(?>(?>\d+\.\d+|\d+\.|\.\d+)([eE][+-]?\d+)?([dDfF]|BD|bd)?|\d+[eE][+-]?\d+([dDfF]|BD|bd)?|\d+([dDfFlLsSyY]|BD|bd)?)((?<=\.)|(?=\b))"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['.','0','1','2','3','4','5','6','7','8','9']),
    ),

    LexMatcher::string_lexer(
        Dialect::Databricks,
        "right_arrow",
        "->",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Databricks,
        "like_operator",
        r#"!?~~?\*?"#,
        Token::comparison_operator_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Databricks,
        "file_literal",
        r#"[a-zA-Z0-9]+:([a-zA-Z0-9\-_\.]*(\/|\\)){2,}((([a-zA-Z0-9\-_\.]*(:|\?|=|&)[a-zA-Z0-9\-_\.]*)+)|([a-zA-Z0-9\-_\.]*\.[a-z]+))"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Databricks,
        "command",
        r#"(\r?\n){2}-- COMMAND ----------(\r?\n)"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Databricks,
        "newline",
        r#"\r?\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::string_lexer(
        Dialect::Databricks,
        "casting_operator",
        "::",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Databricks,
        "right_arrow",
        "=>",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Databricks,
        "equals",
        r#"==|<=>|="#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::string_lexer(
        Dialect::Databricks,
        "greater_than",
        ">",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Databricks,
        "less_than",
        "<",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Databricks,
        "not",
        "!",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Databricks,
        "dot",
        ".",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Databricks,
        "comma",
        ",",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Databricks,
        "plus",
        "+",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Databricks,
        "minus",
        "-",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Databricks,
        "divide",
        "/",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Databricks,
        "percent",
        "%",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Databricks,
        "question",
        "?",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Databricks,
        "ampersand",
        "&",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Databricks,
        "vertical_bar",
        "|",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Databricks,
        "caret",
        "^",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Databricks,
        "star",
        "*",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Databricks,
        "start_bracket",
        "(",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Databricks,
        "end_bracket",
        ")",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Databricks,
        "start_square_bracket",
        "[",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Databricks,
        "end_square_bracket",
        "]",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Databricks,
        "start_curly_bracket",
        "{",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Databricks,
        "end_curly_bracket",
        "}",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Databricks,
        "colon",
        ":",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Databricks,
        "semicolon",
        ";",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Databricks,
        "at_sign_literal",
        r#"@\w*"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Databricks,
        "word",
        r#"[0-9a-zA-Z_]+"#,
        Token::word_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),
]});
pub static DB2_LEXERS: Lazy<Vec<LexMatcher>> = Lazy::new(|| { vec![

    LexMatcher::regex_lexer(
        Dialect::Db2,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Db2,
        "inline_comment",
        r#"(--)[^\n]*"#,
        Token::comment_token,
        None,
        None,
        Some(vec![String::from("-"), String::from("-")]),
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['#','-','/']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Db2,
        "block_comment",
        r#"\/\*([^\*]|\*(?!\/))*\*\/"#,
        Token::comment_token,
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Db2,
        "newline",
        r#"\r\n|\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Db2,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        None,
        None,
        Uuid::new_v4().to_string(),
        Some(extract_nested_block_comment),
        |input| input.starts_with("/"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Db2,
        "single_quote",
        r#"'((?:[^']|'')*)'"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'\'', ..] => true,                     // Single quote case
        [b'R' | b'r', b'\'', ..] => true,        // r' or R'
        [b'B' | b'b', b'\'', ..] => true,        // b' or B'
        [b'R' | b'r', b'B' | b'b', b'\'', ..] => true, // rb', RB', etc.
        [b'B' | b'b', b'R' | b'r', b'\'', ..] => true, // br', Br', etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Db2,
        "double_quote",
        r#""((?:[^"]|"")*)""#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'"', ..] => true,                     // Just a double quote
        [b'R' | b'r', b'"', ..] => true,        // r" or R"
        [b'B' | b'b', b'"', ..] => true,        // b" or B"
        [b'R' | b'r', b'B' | b'b', b'"', ..] => true, // rb", RB", etc.
        [b'B' | b'b', b'R' | b'r', b'"', ..] => true, // br", Br", etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Db2,
        "back_quote",
        r#"`(?:[^`\\]|\\.)*`"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Db2,
        "dollar_quote",
        r#"\$(\w*)\$(.*?)\$\1\$"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with("$"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Db2,
        "numeric_literal",
        r#"(?>\d+\.\d+|\d+\.(?![\.\w])|\.\d+|\d+)(\.?[eE][+-]?\d+)?((?<=\.)|(?=\b))"#,
        Token::literal_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['.','0','1','2','3','4','5','6','7','8','9']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Db2,
        "like_operator",
        r#"!?~~?\*?"#,
        Token::comparison_operator_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Db2,
        "newline",
        r#"\r?\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::string_lexer(
        Dialect::Db2,
        "casting_operator",
        "::",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Db2,
        "right_arrow",
        "=>",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Db2,
        "equals",
        "=",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Db2,
        "greater_than",
        ">",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Db2,
        "less_than",
        "<",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Db2,
        "not",
        "!",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Db2,
        "dot",
        ".",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Db2,
        "comma",
        ",",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Db2,
        "plus",
        "+",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Db2,
        "minus",
        "-",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Db2,
        "divide",
        "/",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Db2,
        "percent",
        "%",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Db2,
        "question",
        "?",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Db2,
        "ampersand",
        "&",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Db2,
        "vertical_bar",
        "|",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Db2,
        "caret",
        "^",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Db2,
        "star",
        "*",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Db2,
        "start_bracket",
        "(",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Db2,
        "end_bracket",
        ")",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Db2,
        "start_square_bracket",
        "[",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Db2,
        "end_square_bracket",
        "]",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Db2,
        "start_curly_bracket",
        "{",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Db2,
        "end_curly_bracket",
        "}",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Db2,
        "colon",
        ":",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Db2,
        "semicolon",
        ";",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Db2,
        "word",
        r#"[0-9a-zA-Z_#]+"#,
        Token::word_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),
]});
pub static DUCKDB_LEXERS: Lazy<Vec<LexMatcher>> = Lazy::new(|| { vec![

    LexMatcher::regex_lexer(
        Dialect::Duckdb,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Duckdb,
        "inline_comment",
        r#"(--)[^\n]*(?=\n|$)"#,
        Token::comment_token,
        None,
        None,
        Some(vec![String::from("-"), String::from("-")]),
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['#','-','/']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Duckdb,
        "block_comment",
        r#"/\*(?>[^*/]+|\*(?!\/)|/[^*])*(?>(?R)(?>[^*/]+|\*(?!\/)|/[^*])*)*\*/"#,
        Token::comment_token,
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Duckdb,
        "newline",
        r#"\r\n|\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Duckdb,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        None,
        None,
        Uuid::new_v4().to_string(),
        Some(extract_nested_block_comment),
        |input| input.starts_with("/"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Duckdb,
        "single_quote",
        r#"'([^']|'')*'"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'\'', ..] => true,                     // Single quote case
        [b'R' | b'r', b'\'', ..] => true,        // r' or R'
        [b'B' | b'b', b'\'', ..] => true,        // b' or B'
        [b'R' | b'r', b'B' | b'b', b'\'', ..] => true, // rb', RB', etc.
        [b'B' | b'b', b'R' | b'r', b'\'', ..] => true, // br', Br', etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Duckdb,
        "double_quote",
        r#""([^"]|"")*""#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'"', ..] => true,                     // Just a double quote
        [b'R' | b'r', b'"', ..] => true,        // r" or R"
        [b'B' | b'b', b'"', ..] => true,        // b" or B"
        [b'R' | b'r', b'B' | b'b', b'"', ..] => true, // rb", RB", etc.
        [b'B' | b'b', b'R' | b'r', b'"', ..] => true, // br", Br", etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Duckdb,
        "back_quote",
        r#"`(?:[^`\\]|\\.)*`"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Duckdb,
        "dollar_quote",
        r#"\$(\w*)\$(.*?)\$\1\$"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with("$"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Duckdb,
        "numeric_literal",
        r#"(?>\d+\.\d+|\d+\.(?![\.\w])|\.\d+|\d+)(\.?[eE][+-]?\d+)?((?<=\.)|(?=\b))"#,
        Token::literal_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['.','0','1','2','3','4','5','6','7','8','9']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Duckdb,
        "unicode_single_quote",
        r#"(?si)U&'([^']|'')*'(\s*UESCAPE\s*'[^0-9A-Fa-f'+\-\s)]')?"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Duckdb,
        "escaped_single_quote",
        r#"(?si)E(('')+?(?!')|'.*?((?<!\\)(?:\\\\)*(?<!')(?:'')*|(?<!\\)(?:\\\\)*\\(?<!')(?:'')*')'(?!'))"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['E', 'e']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Duckdb,
        "unicode_double_quote",
        r#"(?si)U&".+?"(\s*UESCAPE\s*\'[^0-9A-Fa-f\'+\-\s)]\')?"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Duckdb,
        "json_operator",
        r#"->>?|#>>?|@[>@?]|<@|\?[|&]?|#-"#,
        Token::symbol_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Duckdb,
        "postgis_operator",
        r#"\&\&\&|\&<\||<<\||@|\|\&>|\|>>|\~=|<\->|\|=\||<\#>|<<\->>|<<\#>>"#,
        Token::symbol_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::string_lexer(
        Dialect::Duckdb,
        "at",
        "@",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Duckdb,
        "bit_string_literal",
        r#"[bBxX]'[0-9a-fA-F]*'"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::string_lexer(
        Dialect::Duckdb,
        "full_text_search_operator",
        "!!",
        Token::symbol_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Duckdb,
        "like_operator",
        r#"!?~~?\*?"#,
        Token::comparison_operator_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Duckdb,
        "newline",
        r#"\r?\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::string_lexer(
        Dialect::Duckdb,
        "casting_operator",
        "::",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Duckdb,
        "right_arrow",
        "=>",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Duckdb,
        "walrus_operator",
        ":=",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Duckdb,
        "equals",
        "=",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Duckdb,
        "greater_than",
        ">",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Duckdb,
        "less_than",
        "<",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Duckdb,
        "not",
        "!",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Duckdb,
        "dot",
        ".",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Duckdb,
        "comma",
        ",",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Duckdb,
        "plus",
        "+",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Duckdb,
        "minus",
        "-",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Duckdb,
        "double_divide",
        "//",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Duckdb,
        "divide",
        "/",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Duckdb,
        "percent",
        "%",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Duckdb,
        "question",
        "?",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Duckdb,
        "ampersand",
        "&",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Duckdb,
        "vertical_bar",
        "|",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Duckdb,
        "caret",
        "^",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Duckdb,
        "star",
        "*",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Duckdb,
        "start_bracket",
        "(",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Duckdb,
        "end_bracket",
        ")",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Duckdb,
        "start_square_bracket",
        "[",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Duckdb,
        "end_square_bracket",
        "]",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Duckdb,
        "start_curly_bracket",
        "{",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Duckdb,
        "end_curly_bracket",
        "}",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Duckdb,
        "colon",
        ":",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Duckdb,
        "semicolon",
        ";",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Duckdb,
        "meta_command",
        r#"\\(?!gset|gexec)([^\\\r\n])+((\\\\)|(?=\n)|(?=\r\n))?"#,
        Token::comment_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['\\']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Duckdb,
        "dollar_numeric_literal",
        r#"\$\d+"#,
        Token::literal_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Duckdb,
        "meta_command_query_buffer",
        r#"\\([^\\\r\n])+((\\g(set|exec))|(?=\n)|(?=\r\n))?"#,
        Token::symbol_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['\\']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Duckdb,
        "word",
        r#"[a-zA-Z_][0-9a-zA-Z_$]*"#,
        Token::word_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),
]});
pub static EXASOL_LEXERS: Lazy<Vec<LexMatcher>> = Lazy::new(|| { vec![

    LexMatcher::regex_lexer(
        Dialect::Exasol,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Exasol,
        "inline_comment",
        r#"--[^\n]*"#,
        Token::comment_token,
        None,
        None,
        Some(vec![String::from("-"), String::from("-")]),
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['#','-','/']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Exasol,
        "block_comment",
        r#"\/\*([^\*]|\*(?!\/))*\*\/"#,
        Token::comment_token,
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Exasol,
        "newline",
        r#"\r\n|\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Exasol,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        None,
        None,
        Uuid::new_v4().to_string(),
        Some(extract_nested_block_comment),
        |input| input.starts_with("/"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Exasol,
        "single_quote",
        r#"'([^']|'')*'"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'\'', ..] => true,                     // Single quote case
        [b'R' | b'r', b'\'', ..] => true,        // r' or R'
        [b'B' | b'b', b'\'', ..] => true,        // b' or B'
        [b'R' | b'r', b'B' | b'b', b'\'', ..] => true, // rb', RB', etc.
        [b'B' | b'b', b'R' | b'r', b'\'', ..] => true, // br', Br', etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Exasol,
        "double_quote",
        r#""([^"]|"")*""#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'"', ..] => true,                     // Just a double quote
        [b'R' | b'r', b'"', ..] => true,        // r" or R"
        [b'B' | b'b', b'"', ..] => true,        // b" or B"
        [b'R' | b'r', b'B' | b'b', b'"', ..] => true, // rb", RB", etc.
        [b'B' | b'b', b'R' | b'r', b'"', ..] => true, // br", Br", etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Exasol,
        "back_quote",
        r#"`(?:[^`\\]|\\.)*`"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Exasol,
        "dollar_quote",
        r#"\$(\w*)\$(.*?)\$\1\$"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with("$"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Exasol,
        "numeric_literal",
        r#"(?>\d+\.\d+|\d+\.(?![\.\w])|\.\d+|\d+)(\.?[eE][+-]?\d+)?((?<=\.)|(?=\b))"#,
        Token::literal_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['.','0','1','2','3','4','5','6','7','8','9']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Exasol,
        "lua_nested_quotes",
        r#"\[={1,3}\[.*\]={1,3}\]"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Exasol,
        "lua_multiline_quotes",
        r#"\[{2}([^\[\\]|\\.)*\]{2}"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Exasol,
        "escaped_identifier",
        r#"\[\w+\]"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Exasol,
        "udf_param_dot_syntax",
        r#"\.{3}"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Exasol,
        "range_operator",
        r#"\.{2}"#,
        Token::symbol_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::string_lexer(
        Dialect::Exasol,
        "hash",
        "#",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Exasol,
        "walrus_operator",
        ":=",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Exasol,
        "function_script_terminator",
        r#"\n/\n|\n/$"#,
        Token::symbol_token,
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Exasol,
        "newline",
        r#"(\n|\r\n)+"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Exasol,
        "at_sign_literal",
        r#"@[a-zA-Z_][\w]*"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Exasol,
        "dollar_literal",
        r#"[$][a-zA-Z0-9_.]*"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Exasol,
        "like_operator",
        r#"!?~~?\*?"#,
        Token::comparison_operator_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Exasol,
        "newline",
        r#"\r?\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::string_lexer(
        Dialect::Exasol,
        "casting_operator",
        "::",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Exasol,
        "equals",
        "=",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Exasol,
        "greater_than",
        ">",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Exasol,
        "less_than",
        "<",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Exasol,
        "not",
        "!",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Exasol,
        "dot",
        ".",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Exasol,
        "comma",
        ",",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Exasol,
        "plus",
        "+",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Exasol,
        "minus",
        "-",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Exasol,
        "divide",
        "/",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Exasol,
        "percent",
        "%",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Exasol,
        "question",
        "?",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Exasol,
        "ampersand",
        "&",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Exasol,
        "vertical_bar",
        "|",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Exasol,
        "caret",
        "^",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Exasol,
        "star",
        "*",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Exasol,
        "start_bracket",
        "(",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Exasol,
        "end_bracket",
        ")",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Exasol,
        "start_square_bracket",
        "[",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Exasol,
        "end_square_bracket",
        "]",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Exasol,
        "start_curly_bracket",
        "{",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Exasol,
        "end_curly_bracket",
        "}",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Exasol,
        "colon",
        ":",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Exasol,
        "semicolon",
        ";",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Exasol,
        "word",
        r#"[0-9a-zA-Z_]+"#,
        Token::word_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),
]});
pub static GREENPLUM_LEXERS: Lazy<Vec<LexMatcher>> = Lazy::new(|| { vec![

    LexMatcher::regex_lexer(
        Dialect::Greenplum,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Greenplum,
        "inline_comment",
        r#"(--)[^\n]*(?=\n|$)"#,
        Token::comment_token,
        None,
        None,
        Some(vec![String::from("-"), String::from("-")]),
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['#','-','/']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Greenplum,
        "block_comment",
        r#"/\*(?>[^*/]+|\*(?!\/)|/[^*])*(?>(?R)(?>[^*/]+|\*(?!\/)|/[^*])*)*\*/"#,
        Token::comment_token,
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Greenplum,
        "newline",
        r#"\r\n|\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Greenplum,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        None,
        None,
        Uuid::new_v4().to_string(),
        Some(extract_nested_block_comment),
        |input| input.starts_with("/"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Greenplum,
        "single_quote",
        r#"'([^']|'')*'"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'\'', ..] => true,                     // Single quote case
        [b'R' | b'r', b'\'', ..] => true,        // r' or R'
        [b'B' | b'b', b'\'', ..] => true,        // b' or B'
        [b'R' | b'r', b'B' | b'b', b'\'', ..] => true, // rb', RB', etc.
        [b'B' | b'b', b'R' | b'r', b'\'', ..] => true, // br', Br', etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Greenplum,
        "double_quote",
        r#""([^"]|"")*""#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'"', ..] => true,                     // Just a double quote
        [b'R' | b'r', b'"', ..] => true,        // r" or R"
        [b'B' | b'b', b'"', ..] => true,        // b" or B"
        [b'R' | b'r', b'B' | b'b', b'"', ..] => true, // rb", RB", etc.
        [b'B' | b'b', b'R' | b'r', b'"', ..] => true, // br", Br", etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Greenplum,
        "back_quote",
        r#"`(?:[^`\\]|\\.)*`"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Greenplum,
        "dollar_quote",
        r#"\$(\w*)\$(.*?)\$\1\$"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with("$"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Greenplum,
        "numeric_literal",
        r#"(?>\d+\.\d+|\d+\.(?![\.\w])|\.\d+|\d+)(\.?[eE][+-]?\d+)?((?<=\.)|(?=\b))"#,
        Token::literal_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['.','0','1','2','3','4','5','6','7','8','9']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Greenplum,
        "unicode_single_quote",
        r#"(?si)U&'([^']|'')*'(\s*UESCAPE\s*'[^0-9A-Fa-f'+\-\s)]')?"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Greenplum,
        "escaped_single_quote",
        r#"(?si)E(('')+?(?!')|'.*?((?<!\\)(?:\\\\)*(?<!')(?:'')*|(?<!\\)(?:\\\\)*\\(?<!')(?:'')*')'(?!'))"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['E', 'e']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Greenplum,
        "unicode_double_quote",
        r#"(?si)U&".+?"(\s*UESCAPE\s*\'[^0-9A-Fa-f\'+\-\s)]\')?"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Greenplum,
        "json_operator",
        r#"->>?|#>>?|@[>@?]|<@|\?[|&]?|#-"#,
        Token::symbol_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Greenplum,
        "postgis_operator",
        r#"\&\&\&|\&<\||<<\||@|\|\&>|\|>>|\~=|<\->|\|=\||<\#>|<<\->>|<<\#>>"#,
        Token::symbol_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::string_lexer(
        Dialect::Greenplum,
        "at",
        "@",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Greenplum,
        "bit_string_literal",
        r#"[bBxX]'[0-9a-fA-F]*'"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::string_lexer(
        Dialect::Greenplum,
        "full_text_search_operator",
        "!!",
        Token::symbol_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Greenplum,
        "like_operator",
        r#"!?~~?\*?"#,
        Token::comparison_operator_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Greenplum,
        "newline",
        r#"\r?\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::string_lexer(
        Dialect::Greenplum,
        "casting_operator",
        "::",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Greenplum,
        "right_arrow",
        "=>",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Greenplum,
        "walrus_operator",
        ":=",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Greenplum,
        "equals",
        "=",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Greenplum,
        "greater_than",
        ">",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Greenplum,
        "less_than",
        "<",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Greenplum,
        "not",
        "!",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Greenplum,
        "dot",
        ".",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Greenplum,
        "comma",
        ",",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Greenplum,
        "plus",
        "+",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Greenplum,
        "minus",
        "-",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Greenplum,
        "divide",
        "/",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Greenplum,
        "percent",
        "%",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Greenplum,
        "question",
        "?",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Greenplum,
        "ampersand",
        "&",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Greenplum,
        "vertical_bar",
        "|",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Greenplum,
        "caret",
        "^",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Greenplum,
        "star",
        "*",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Greenplum,
        "start_bracket",
        "(",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Greenplum,
        "end_bracket",
        ")",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Greenplum,
        "start_square_bracket",
        "[",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Greenplum,
        "end_square_bracket",
        "]",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Greenplum,
        "start_curly_bracket",
        "{",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Greenplum,
        "end_curly_bracket",
        "}",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Greenplum,
        "colon",
        ":",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Greenplum,
        "semicolon",
        ";",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Greenplum,
        "meta_command",
        r#"\\(?!gset|gexec)([^\\\r\n])+((\\\\)|(?=\n)|(?=\r\n))?"#,
        Token::comment_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['\\']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Greenplum,
        "dollar_numeric_literal",
        r#"\$\d+"#,
        Token::literal_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Greenplum,
        "meta_command_query_buffer",
        r#"\\([^\\\r\n])+((\\g(set|exec))|(?=\n)|(?=\r\n))?"#,
        Token::symbol_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['\\']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Greenplum,
        "word",
        r#"[a-zA-Z_][0-9a-zA-Z_$]*"#,
        Token::word_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),
]});
pub static HIVE_LEXERS: Lazy<Vec<LexMatcher>> = Lazy::new(|| { vec![

    LexMatcher::regex_lexer(
        Dialect::Hive,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Hive,
        "inline_comment",
        r#"(--|#)[^\n]*"#,
        Token::comment_token,
        None,
        None,
        Some(vec![String::from("--"), String::from("#")]),
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['#','-','/']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Hive,
        "block_comment",
        r#"\/\*([^\*]|\*(?!\/))*\*\/"#,
        Token::comment_token,
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Hive,
        "newline",
        r#"\r\n|\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Hive,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        None,
        None,
        Uuid::new_v4().to_string(),
        Some(extract_nested_block_comment),
        |input| input.starts_with("/"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Hive,
        "single_quote",
        r#"'([^'\\]|\\.|'')*'"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'\'', ..] => true,                     // Single quote case
        [b'R' | b'r', b'\'', ..] => true,        // r' or R'
        [b'B' | b'b', b'\'', ..] => true,        // b' or B'
        [b'R' | b'r', b'B' | b'b', b'\'', ..] => true, // rb', RB', etc.
        [b'B' | b'b', b'R' | b'r', b'\'', ..] => true, // br', Br', etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Hive,
        "double_quote",
        r#""(""|[^"\\]|\\.)*""#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'"', ..] => true,                     // Just a double quote
        [b'R' | b'r', b'"', ..] => true,        // r" or R"
        [b'B' | b'b', b'"', ..] => true,        // b" or B"
        [b'R' | b'r', b'B' | b'b', b'"', ..] => true, // rb", RB", etc.
        [b'B' | b'b', b'R' | b'r', b'"', ..] => true, // br", Br", etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Hive,
        "back_quote",
        r#"`(?:[^`\\]|\\.)*`"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Hive,
        "dollar_quote",
        r#"\$(\w*)\$(.*?)\$\1\$"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with("$"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Hive,
        "numeric_literal",
        r#"(?>\d+\.\d+|\d+\.(?![\.\w])|\.\d+|\d+)(\.?[eE][+-]?\d+)?((?<=\.)|(?=\b))"#,
        Token::literal_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['.','0','1','2','3','4','5','6','7','8','9']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Hive,
        "like_operator",
        r#"!?~~?\*?"#,
        Token::comparison_operator_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Hive,
        "newline",
        r#"\r?\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::string_lexer(
        Dialect::Hive,
        "casting_operator",
        "::",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Hive,
        "equals",
        "=",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Hive,
        "greater_than",
        ">",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Hive,
        "less_than",
        "<",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Hive,
        "not",
        "!",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Hive,
        "dot",
        ".",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Hive,
        "comma",
        ",",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Hive,
        "plus",
        "+",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Hive,
        "minus",
        "-",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Hive,
        "divide",
        "/",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Hive,
        "percent",
        "%",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Hive,
        "question",
        "?",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Hive,
        "ampersand",
        "&",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Hive,
        "vertical_bar",
        "|",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Hive,
        "caret",
        "^",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Hive,
        "star",
        "*",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Hive,
        "start_bracket",
        "(",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Hive,
        "end_bracket",
        ")",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Hive,
        "start_square_bracket",
        "[",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Hive,
        "end_square_bracket",
        "]",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Hive,
        "start_curly_bracket",
        "{",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Hive,
        "end_curly_bracket",
        "}",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Hive,
        "colon",
        ":",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Hive,
        "semicolon",
        ";",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Hive,
        "word",
        r#"[0-9a-zA-Z_]+"#,
        Token::word_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),
]});
pub static IMPALA_LEXERS: Lazy<Vec<LexMatcher>> = Lazy::new(|| { vec![

    LexMatcher::regex_lexer(
        Dialect::Impala,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Impala,
        "inline_comment",
        r#"(--|#)[^\n]*"#,
        Token::comment_token,
        None,
        None,
        Some(vec![String::from("--"), String::from("#")]),
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['#','-','/']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Impala,
        "block_comment",
        r#"\/\*([^\*]|\*(?!\/))*\*\/"#,
        Token::comment_token,
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Impala,
        "newline",
        r#"\r\n|\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Impala,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        None,
        None,
        Uuid::new_v4().to_string(),
        Some(extract_nested_block_comment),
        |input| input.starts_with("/"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Impala,
        "single_quote",
        r#"'([^'\\]|\\.|'')*'"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'\'', ..] => true,                     // Single quote case
        [b'R' | b'r', b'\'', ..] => true,        // r' or R'
        [b'B' | b'b', b'\'', ..] => true,        // b' or B'
        [b'R' | b'r', b'B' | b'b', b'\'', ..] => true, // rb', RB', etc.
        [b'B' | b'b', b'R' | b'r', b'\'', ..] => true, // br', Br', etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Impala,
        "double_quote",
        r#""(""|[^"\\]|\\.)*""#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'"', ..] => true,                     // Just a double quote
        [b'R' | b'r', b'"', ..] => true,        // r" or R"
        [b'B' | b'b', b'"', ..] => true,        // b" or B"
        [b'R' | b'r', b'B' | b'b', b'"', ..] => true, // rb", RB", etc.
        [b'B' | b'b', b'R' | b'r', b'"', ..] => true, // br", Br", etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Impala,
        "back_quote",
        r#"`(?:[^`\\]|\\.)*`"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Impala,
        "dollar_quote",
        r#"\$(\w*)\$(.*?)\$\1\$"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with("$"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Impala,
        "numeric_literal",
        r#"(?>\d+\.\d+|\d+\.(?![\.\w])|\.\d+|\d+)(\.?[eE][+-]?\d+)?((?<=\.)|(?=\b))"#,
        Token::literal_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['.','0','1','2','3','4','5','6','7','8','9']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Impala,
        "like_operator",
        r#"!?~~?\*?"#,
        Token::comparison_operator_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Impala,
        "newline",
        r#"\r?\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::string_lexer(
        Dialect::Impala,
        "casting_operator",
        "::",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Impala,
        "equals",
        "=",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Impala,
        "greater_than",
        ">",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Impala,
        "less_than",
        "<",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Impala,
        "not",
        "!",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Impala,
        "dot",
        ".",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Impala,
        "comma",
        ",",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Impala,
        "plus",
        "+",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Impala,
        "minus",
        "-",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Impala,
        "divide",
        "/",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Impala,
        "percent",
        "%",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Impala,
        "question",
        "?",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Impala,
        "ampersand",
        "&",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Impala,
        "vertical_bar",
        "|",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Impala,
        "caret",
        "^",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Impala,
        "star",
        "*",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Impala,
        "start_bracket",
        "(",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Impala,
        "end_bracket",
        ")",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Impala,
        "start_square_bracket",
        "[",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Impala,
        "end_square_bracket",
        "]",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Impala,
        "start_curly_bracket",
        "{",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Impala,
        "end_curly_bracket",
        "}",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Impala,
        "colon",
        ":",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Impala,
        "semicolon",
        ";",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Impala,
        "word",
        r#"[0-9a-zA-Z_]+"#,
        Token::word_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),
]});
pub static MARIADB_LEXERS: Lazy<Vec<LexMatcher>> = Lazy::new(|| { vec![

    LexMatcher::regex_lexer(
        Dialect::Mariadb,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Mariadb,
        "inline_comment",
        r#"(^--|-- |#)[^\n]*"#,
        Token::comment_token,
        None,
        None,
        Some(vec![String::from("--"), String::from("#")]),
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['#','-','/']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Mariadb,
        "block_comment",
        r#"\/\*([^\*]|\*(?!\/))*\*\/"#,
        Token::comment_token,
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Mariadb,
        "newline",
        r#"\r\n|\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Mariadb,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        None,
        None,
        Uuid::new_v4().to_string(),
        Some(extract_nested_block_comment),
        |input| input.starts_with("/"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Mariadb,
        "single_quote",
        r#"(?s)('(?:\\'|''|\\\\|[^'])*'(?!'))"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'\'', ..] => true,                     // Single quote case
        [b'R' | b'r', b'\'', ..] => true,        // r' or R'
        [b'B' | b'b', b'\'', ..] => true,        // b' or B'
        [b'R' | b'r', b'B' | b'b', b'\'', ..] => true, // rb', RB', etc.
        [b'B' | b'b', b'R' | b'r', b'\'', ..] => true, // br', Br', etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Mariadb,
        "double_quote",
        r#"(?s)("(?:\\"|""|\\\\|[^"])*"(?!"))"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'"', ..] => true,                     // Just a double quote
        [b'R' | b'r', b'"', ..] => true,        // r" or R"
        [b'B' | b'b', b'"', ..] => true,        // b" or B"
        [b'R' | b'r', b'B' | b'b', b'"', ..] => true, // rb", RB", etc.
        [b'B' | b'b', b'R' | b'r', b'"', ..] => true, // br", Br", etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Mariadb,
        "back_quote",
        r#"`(?:[^`\\]|\\.)*`"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Mariadb,
        "dollar_quote",
        r#"\$(\w*)\$(.*?)\$\1\$"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with("$"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Mariadb,
        "hexadecimal_literal",
        r#"([xX]'([\da-fA-F][\da-fA-F])+'|0x[\da-fA-F]+)"#,
        Token::literal_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Mariadb,
        "bit_value_literal",
        r#"([bB]'[01]+'|0b[01]+)"#,
        Token::literal_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Mariadb,
        "numeric_literal",
        r#"(?>\d+\.\d+|\d+\.(?![\.\w])|\.\d+|\d+)(\.?[eE][+-]?\d+)?((?<=\.)|(?=\b))"#,
        Token::literal_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['.','0','1','2','3','4','5','6','7','8','9']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Mariadb,
        "like_operator",
        r#"!?~~?\*?"#,
        Token::comparison_operator_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Mariadb,
        "newline",
        r#"\r?\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::string_lexer(
        Dialect::Mariadb,
        "casting_operator",
        "::",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mariadb,
        "walrus_operator",
        ":=",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mariadb,
        "equals",
        "=",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mariadb,
        "inline_path_operator",
        "->>",
        Token::symbol_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mariadb,
        "column_path_operator",
        "->",
        Token::symbol_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mariadb,
        "greater_than",
        ">",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mariadb,
        "less_than",
        "<",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mariadb,
        "not",
        "!",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mariadb,
        "dot",
        ".",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mariadb,
        "comma",
        ",",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mariadb,
        "plus",
        "+",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mariadb,
        "minus",
        "-",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mariadb,
        "divide",
        "/",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mariadb,
        "percent",
        "%",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mariadb,
        "question",
        "?",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mariadb,
        "double_ampersand",
        "&&",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mariadb,
        "ampersand",
        "&",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mariadb,
        "double_vertical_bar",
        "||",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mariadb,
        "vertical_bar",
        "|",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mariadb,
        "caret",
        "^",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mariadb,
        "star",
        "*",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mariadb,
        "start_bracket",
        "(",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mariadb,
        "end_bracket",
        ")",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mariadb,
        "start_square_bracket",
        "[",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mariadb,
        "end_square_bracket",
        "]",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mariadb,
        "start_curly_bracket",
        "{",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mariadb,
        "end_curly_bracket",
        "}",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mariadb,
        "colon",
        ":",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mariadb,
        "semicolon",
        ";",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Mariadb,
        "at_sign",
        r#"@@?[a-zA-Z0-9_$]*(\.[a-zA-Z0-9_$]+)?"#,
        Token::code_token,
        None,
        None,
        None,
        Some(vec![String::from("@")]),
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Mariadb,
        "word",
        r#"[0-9a-zA-Z_]+"#,
        Token::word_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),
]});
pub static MATERIALIZE_LEXERS: Lazy<Vec<LexMatcher>> = Lazy::new(|| { vec![

    LexMatcher::regex_lexer(
        Dialect::Materialize,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Materialize,
        "inline_comment",
        r#"(--)[^\n]*(?=\n|$)"#,
        Token::comment_token,
        None,
        None,
        Some(vec![String::from("-"), String::from("-")]),
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['#','-','/']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Materialize,
        "block_comment",
        r#"/\*(?>[^*/]+|\*(?!\/)|/[^*])*(?>(?R)(?>[^*/]+|\*(?!\/)|/[^*])*)*\*/"#,
        Token::comment_token,
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Materialize,
        "newline",
        r#"\r\n|\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Materialize,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        None,
        None,
        Uuid::new_v4().to_string(),
        Some(extract_nested_block_comment),
        |input| input.starts_with("/"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Materialize,
        "single_quote",
        r#"'([^']|'')*'"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'\'', ..] => true,                     // Single quote case
        [b'R' | b'r', b'\'', ..] => true,        // r' or R'
        [b'B' | b'b', b'\'', ..] => true,        // b' or B'
        [b'R' | b'r', b'B' | b'b', b'\'', ..] => true, // rb', RB', etc.
        [b'B' | b'b', b'R' | b'r', b'\'', ..] => true, // br', Br', etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Materialize,
        "double_quote",
        r#""([^"]|"")*""#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'"', ..] => true,                     // Just a double quote
        [b'R' | b'r', b'"', ..] => true,        // r" or R"
        [b'B' | b'b', b'"', ..] => true,        // b" or B"
        [b'R' | b'r', b'B' | b'b', b'"', ..] => true, // rb", RB", etc.
        [b'B' | b'b', b'R' | b'r', b'"', ..] => true, // br", Br", etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Materialize,
        "back_quote",
        r#"`(?:[^`\\]|\\.)*`"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Materialize,
        "dollar_quote",
        r#"\$(\w*)\$(.*?)\$\1\$"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with("$"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Materialize,
        "numeric_literal",
        r#"(?>\d+\.\d+|\d+\.(?![\.\w])|\.\d+|\d+)(\.?[eE][+-]?\d+)?((?<=\.)|(?=\b))"#,
        Token::literal_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['.','0','1','2','3','4','5','6','7','8','9']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Materialize,
        "unicode_single_quote",
        r#"(?si)U&'([^']|'')*'(\s*UESCAPE\s*'[^0-9A-Fa-f'+\-\s)]')?"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Materialize,
        "escaped_single_quote",
        r#"(?si)E(('')+?(?!')|'.*?((?<!\\)(?:\\\\)*(?<!')(?:'')*|(?<!\\)(?:\\\\)*\\(?<!')(?:'')*')'(?!'))"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['E', 'e']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Materialize,
        "unicode_double_quote",
        r#"(?si)U&".+?"(\s*UESCAPE\s*\'[^0-9A-Fa-f\'+\-\s)]\')?"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Materialize,
        "json_operator",
        r#"->>?|#>>?|@[>@?]|<@|\?[|&]?|#-"#,
        Token::symbol_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Materialize,
        "postgis_operator",
        r#"\&\&\&|\&<\||<<\||@|\|\&>|\|>>|\~=|<\->|\|=\||<\#>|<<\->>|<<\#>>"#,
        Token::symbol_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::string_lexer(
        Dialect::Materialize,
        "at",
        "@",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Materialize,
        "bit_string_literal",
        r#"[bBxX]'[0-9a-fA-F]*'"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::string_lexer(
        Dialect::Materialize,
        "full_text_search_operator",
        "!!",
        Token::symbol_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Materialize,
        "like_operator",
        r#"!?~~?\*?"#,
        Token::comparison_operator_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Materialize,
        "newline",
        r#"\r?\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::string_lexer(
        Dialect::Materialize,
        "casting_operator",
        "::",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Materialize,
        "right_arrow",
        "=>",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Materialize,
        "walrus_operator",
        ":=",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Materialize,
        "equals",
        "=",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Materialize,
        "greater_than",
        ">",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Materialize,
        "less_than",
        "<",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Materialize,
        "not",
        "!",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Materialize,
        "dot",
        ".",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Materialize,
        "comma",
        ",",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Materialize,
        "plus",
        "+",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Materialize,
        "minus",
        "-",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Materialize,
        "divide",
        "/",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Materialize,
        "percent",
        "%",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Materialize,
        "question",
        "?",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Materialize,
        "ampersand",
        "&",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Materialize,
        "vertical_bar",
        "|",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Materialize,
        "caret",
        "^",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Materialize,
        "star",
        "*",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Materialize,
        "start_bracket",
        "(",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Materialize,
        "end_bracket",
        ")",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Materialize,
        "start_square_bracket",
        "[",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Materialize,
        "end_square_bracket",
        "]",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Materialize,
        "start_curly_bracket",
        "{",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Materialize,
        "end_curly_bracket",
        "}",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Materialize,
        "colon",
        ":",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Materialize,
        "semicolon",
        ";",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Materialize,
        "meta_command",
        r#"\\(?!gset|gexec)([^\\\r\n])+((\\\\)|(?=\n)|(?=\r\n))?"#,
        Token::comment_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['\\']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Materialize,
        "dollar_numeric_literal",
        r#"\$\d+"#,
        Token::literal_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Materialize,
        "meta_command_query_buffer",
        r#"\\([^\\\r\n])+((\\g(set|exec))|(?=\n)|(?=\r\n))?"#,
        Token::symbol_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['\\']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Materialize,
        "word",
        r#"[a-zA-Z_][0-9a-zA-Z_$]*"#,
        Token::word_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),
]});
pub static MYSQL_LEXERS: Lazy<Vec<LexMatcher>> = Lazy::new(|| { vec![

    LexMatcher::regex_lexer(
        Dialect::Mysql,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Mysql,
        "inline_comment",
        r#"(^--|-- |#)[^\n]*"#,
        Token::comment_token,
        None,
        None,
        Some(vec![String::from("--"), String::from("#")]),
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['#','-','/']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Mysql,
        "block_comment",
        r#"\/\*([^\*]|\*(?!\/))*\*\/"#,
        Token::comment_token,
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Mysql,
        "newline",
        r#"\r\n|\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Mysql,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        None,
        None,
        Uuid::new_v4().to_string(),
        Some(extract_nested_block_comment),
        |input| input.starts_with("/"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Mysql,
        "single_quote",
        r#"(?s)('(?:\\'|''|\\\\|[^'])*'(?!'))"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'\'', ..] => true,                     // Single quote case
        [b'R' | b'r', b'\'', ..] => true,        // r' or R'
        [b'B' | b'b', b'\'', ..] => true,        // b' or B'
        [b'R' | b'r', b'B' | b'b', b'\'', ..] => true, // rb', RB', etc.
        [b'B' | b'b', b'R' | b'r', b'\'', ..] => true, // br', Br', etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Mysql,
        "double_quote",
        r#"(?s)("(?:\\"|""|\\\\|[^"])*"(?!"))"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'"', ..] => true,                     // Just a double quote
        [b'R' | b'r', b'"', ..] => true,        // r" or R"
        [b'B' | b'b', b'"', ..] => true,        // b" or B"
        [b'R' | b'r', b'B' | b'b', b'"', ..] => true, // rb", RB", etc.
        [b'B' | b'b', b'R' | b'r', b'"', ..] => true, // br", Br", etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Mysql,
        "back_quote",
        r#"`(?:[^`\\]|\\.)*`"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Mysql,
        "dollar_quote",
        r#"\$(\w*)\$(.*?)\$\1\$"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with("$"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Mysql,
        "hexadecimal_literal",
        r#"([xX]'([\da-fA-F][\da-fA-F])+'|0x[\da-fA-F]+)"#,
        Token::literal_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Mysql,
        "bit_value_literal",
        r#"([bB]'[01]+'|0b[01]+)"#,
        Token::literal_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Mysql,
        "numeric_literal",
        r#"(?>\d+\.\d+|\d+\.(?![\.\w])|\.\d+|\d+)(\.?[eE][+-]?\d+)?((?<=\.)|(?=\b))"#,
        Token::literal_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['.','0','1','2','3','4','5','6','7','8','9']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Mysql,
        "like_operator",
        r#"!?~~?\*?"#,
        Token::comparison_operator_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Mysql,
        "newline",
        r#"\r?\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::string_lexer(
        Dialect::Mysql,
        "casting_operator",
        "::",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mysql,
        "walrus_operator",
        ":=",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mysql,
        "equals",
        "=",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mysql,
        "inline_path_operator",
        "->>",
        Token::symbol_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mysql,
        "column_path_operator",
        "->",
        Token::symbol_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mysql,
        "greater_than",
        ">",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mysql,
        "less_than",
        "<",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mysql,
        "not",
        "!",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mysql,
        "dot",
        ".",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mysql,
        "comma",
        ",",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mysql,
        "plus",
        "+",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mysql,
        "minus",
        "-",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mysql,
        "divide",
        "/",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mysql,
        "percent",
        "%",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mysql,
        "question",
        "?",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mysql,
        "double_ampersand",
        "&&",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mysql,
        "ampersand",
        "&",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mysql,
        "double_vertical_bar",
        "||",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mysql,
        "vertical_bar",
        "|",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mysql,
        "caret",
        "^",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mysql,
        "star",
        "*",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mysql,
        "start_bracket",
        "(",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mysql,
        "end_bracket",
        ")",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mysql,
        "start_square_bracket",
        "[",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mysql,
        "end_square_bracket",
        "]",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mysql,
        "start_curly_bracket",
        "{",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mysql,
        "end_curly_bracket",
        "}",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mysql,
        "colon",
        ":",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Mysql,
        "semicolon",
        ";",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Mysql,
        "at_sign",
        r#"@@?[a-zA-Z0-9_$]*(\.[a-zA-Z0-9_$]+)?"#,
        Token::code_token,
        None,
        None,
        None,
        Some(vec![String::from("@")]),
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Mysql,
        "word",
        r#"[0-9a-zA-Z_]+"#,
        Token::word_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),
]});
pub static ORACLE_LEXERS: Lazy<Vec<LexMatcher>> = Lazy::new(|| { vec![

    LexMatcher::regex_lexer(
        Dialect::Oracle,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Oracle,
        "inline_comment",
        r#"(--|#)[^\n]*"#,
        Token::comment_token,
        None,
        None,
        Some(vec![String::from("--"), String::from("#")]),
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['#','-','/']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Oracle,
        "block_comment",
        r#"\/\*([^\*]|\*(?!\/))*\*\/"#,
        Token::comment_token,
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Oracle,
        "newline",
        r#"\r\n|\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Oracle,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        None,
        None,
        Uuid::new_v4().to_string(),
        Some(extract_nested_block_comment),
        |input| input.starts_with("/"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Oracle,
        "single_quote",
        r#"'([^'\\]|\\|\\.|'')*'"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'\'', ..] => true,                     // Single quote case
        [b'R' | b'r', b'\'', ..] => true,        // r' or R'
        [b'B' | b'b', b'\'', ..] => true,        // b' or B'
        [b'R' | b'r', b'B' | b'b', b'\'', ..] => true, // rb', RB', etc.
        [b'B' | b'b', b'R' | b'r', b'\'', ..] => true, // br', Br', etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Oracle,
        "double_quote",
        r#""([^"]|"")*""#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'"', ..] => true,                     // Just a double quote
        [b'R' | b'r', b'"', ..] => true,        // r" or R"
        [b'B' | b'b', b'"', ..] => true,        // b" or B"
        [b'R' | b'r', b'B' | b'b', b'"', ..] => true, // rb", RB", etc.
        [b'B' | b'b', b'R' | b'r', b'"', ..] => true, // br", Br", etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Oracle,
        "back_quote",
        r#"`(?:[^`\\]|\\.)*`"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Oracle,
        "dollar_quote",
        r#"\$(\w*)\$(.*?)\$\1\$"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with("$"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Oracle,
        "numeric_literal",
        r#"(?>\d+\.\d+|\d+\.(?![\.\w])|\.\d+|\d+)(\.?[eE][+-]?\d+)?((?<=\.)|(?=\b))"#,
        Token::literal_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['.','0','1','2','3','4','5','6','7','8','9']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Oracle,
        "like_operator",
        r#"!?~~?\*?"#,
        Token::comparison_operator_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Oracle,
        "newline",
        r#"\r?\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::string_lexer(
        Dialect::Oracle,
        "casting_operator",
        "::",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Oracle,
        "right_arrow",
        "=>",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Oracle,
        "equals",
        "=",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Oracle,
        "greater_than",
        ">",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Oracle,
        "less_than",
        "<",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Oracle,
        "not",
        "!",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Oracle,
        "dot",
        ".",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Oracle,
        "comma",
        ",",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Oracle,
        "plus",
        "+",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Oracle,
        "minus",
        "-",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Oracle,
        "divide",
        "/",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Oracle,
        "percent",
        "%",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Oracle,
        "question",
        "?",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Oracle,
        "ampersand",
        "&",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Oracle,
        "vertical_bar",
        "|",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Oracle,
        "caret",
        "^",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Oracle,
        "star",
        "*",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Oracle,
        "start_bracket",
        "(",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Oracle,
        "end_bracket",
        ")",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Oracle,
        "start_square_bracket",
        "[",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Oracle,
        "end_square_bracket",
        "]",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Oracle,
        "start_curly_bracket",
        "{",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Oracle,
        "end_curly_bracket",
        "}",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Oracle,
        "colon",
        ":",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Oracle,
        "semicolon",
        ";",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Oracle,
        "prompt_command",
        r#"PROMPT([^(\r\n)])*((?=\n)|(?=\r\n))?"#,
        Token::comment_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with("PROMPT"),
    ),

    LexMatcher::string_lexer(
        Dialect::Oracle,
        "at_sign",
        "@",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Oracle,
        "word",
        r#"[a-zA-Z][0-9a-zA-Z_$#]*"#,
        Token::word_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),
]});
pub static POSTGRES_LEXERS: Lazy<Vec<LexMatcher>> = Lazy::new(|| { vec![

    LexMatcher::regex_lexer(
        Dialect::Postgres,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Postgres,
        "inline_comment",
        r#"(--)[^\n]*(?=\n|$)"#,
        Token::comment_token,
        None,
        None,
        Some(vec![String::from("-"), String::from("-")]),
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['#','-','/']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Postgres,
        "block_comment",
        r#"/\*(?>[^*/]+|\*(?!\/)|/[^*])*(?>(?R)(?>[^*/]+|\*(?!\/)|/[^*])*)*\*/"#,
        Token::comment_token,
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Postgres,
        "newline",
        r#"\r\n|\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Postgres,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        None,
        None,
        Uuid::new_v4().to_string(),
        Some(extract_nested_block_comment),
        |input| input.starts_with("/"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Postgres,
        "single_quote",
        r#"'([^']|'')*'"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'\'', ..] => true,                     // Single quote case
        [b'R' | b'r', b'\'', ..] => true,        // r' or R'
        [b'B' | b'b', b'\'', ..] => true,        // b' or B'
        [b'R' | b'r', b'B' | b'b', b'\'', ..] => true, // rb', RB', etc.
        [b'B' | b'b', b'R' | b'r', b'\'', ..] => true, // br', Br', etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Postgres,
        "double_quote",
        r#""([^"]|"")*""#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'"', ..] => true,                     // Just a double quote
        [b'R' | b'r', b'"', ..] => true,        // r" or R"
        [b'B' | b'b', b'"', ..] => true,        // b" or B"
        [b'R' | b'r', b'B' | b'b', b'"', ..] => true, // rb", RB", etc.
        [b'B' | b'b', b'R' | b'r', b'"', ..] => true, // br", Br", etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Postgres,
        "back_quote",
        r#"`(?:[^`\\]|\\.)*`"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Postgres,
        "dollar_quote",
        r#"\$(\w*)\$(.*?)\$\1\$"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with("$"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Postgres,
        "numeric_literal",
        r#"(?>\d+\.\d+|\d+\.(?![\.\w])|\.\d+|\d+)(\.?[eE][+-]?\d+)?((?<=\.)|(?=\b))"#,
        Token::literal_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['.','0','1','2','3','4','5','6','7','8','9']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Postgres,
        "unicode_single_quote",
        r#"(?si)U&'([^']|'')*'(\s*UESCAPE\s*'[^0-9A-Fa-f'+\-\s)]')?"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Postgres,
        "escaped_single_quote",
        r#"(?si)E(('')+?(?!')|'.*?((?<!\\)(?:\\\\)*(?<!')(?:'')*|(?<!\\)(?:\\\\)*\\(?<!')(?:'')*')'(?!'))"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['E', 'e']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Postgres,
        "unicode_double_quote",
        r#"(?si)U&".+?"(\s*UESCAPE\s*\'[^0-9A-Fa-f\'+\-\s)]\')?"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Postgres,
        "json_operator",
        r#"->>?|#>>?|@[>@?]|<@|\?[|&]?|#-"#,
        Token::symbol_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Postgres,
        "postgis_operator",
        r#"\&\&\&|\&<\||<<\||@|\|\&>|\|>>|\~=|<\->|\|=\||<\#>|<<\->>|<<\#>>"#,
        Token::symbol_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::string_lexer(
        Dialect::Postgres,
        "at",
        "@",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Postgres,
        "bit_string_literal",
        r#"[bBxX]'[0-9a-fA-F]*'"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::string_lexer(
        Dialect::Postgres,
        "full_text_search_operator",
        "!!",
        Token::symbol_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Postgres,
        "like_operator",
        r#"!?~~?\*?"#,
        Token::comparison_operator_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Postgres,
        "newline",
        r#"\r?\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::string_lexer(
        Dialect::Postgres,
        "casting_operator",
        "::",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Postgres,
        "right_arrow",
        "=>",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Postgres,
        "walrus_operator",
        ":=",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Postgres,
        "equals",
        "=",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Postgres,
        "greater_than",
        ">",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Postgres,
        "less_than",
        "<",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Postgres,
        "not",
        "!",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Postgres,
        "dot",
        ".",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Postgres,
        "comma",
        ",",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Postgres,
        "plus",
        "+",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Postgres,
        "minus",
        "-",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Postgres,
        "divide",
        "/",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Postgres,
        "percent",
        "%",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Postgres,
        "question",
        "?",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Postgres,
        "ampersand",
        "&",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Postgres,
        "vertical_bar",
        "|",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Postgres,
        "caret",
        "^",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Postgres,
        "star",
        "*",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Postgres,
        "start_bracket",
        "(",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Postgres,
        "end_bracket",
        ")",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Postgres,
        "start_square_bracket",
        "[",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Postgres,
        "end_square_bracket",
        "]",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Postgres,
        "start_curly_bracket",
        "{",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Postgres,
        "end_curly_bracket",
        "}",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Postgres,
        "colon",
        ":",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Postgres,
        "semicolon",
        ";",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Postgres,
        "meta_command",
        r#"\\(?!gset|gexec)([^\\\r\n])+((\\\\)|(?=\n)|(?=\r\n))?"#,
        Token::comment_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['\\']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Postgres,
        "dollar_numeric_literal",
        r#"\$\d+"#,
        Token::literal_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Postgres,
        "meta_command_query_buffer",
        r#"\\([^\\\r\n])+((\\g(set|exec))|(?=\n)|(?=\r\n))?"#,
        Token::symbol_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['\\']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Postgres,
        "word",
        r#"[a-zA-Z_][0-9a-zA-Z_$]*"#,
        Token::word_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),
]});
pub static REDSHIFT_LEXERS: Lazy<Vec<LexMatcher>> = Lazy::new(|| { vec![

    LexMatcher::regex_lexer(
        Dialect::Redshift,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Redshift,
        "inline_comment",
        r#"(--)[^\n]*(?=\n|$)"#,
        Token::comment_token,
        None,
        None,
        Some(vec![String::from("-"), String::from("-")]),
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['#','-','/']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Redshift,
        "block_comment",
        r#"/\*(?>[^*/]+|\*(?!\/)|/[^*])*(?>(?R)(?>[^*/]+|\*(?!\/)|/[^*])*)*\*/"#,
        Token::comment_token,
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Redshift,
        "newline",
        r#"\r\n|\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Redshift,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        None,
        None,
        Uuid::new_v4().to_string(),
        Some(extract_nested_block_comment),
        |input| input.starts_with("/"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Redshift,
        "single_quote",
        r#"'([^']|'')*'"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'\'', ..] => true,                     // Single quote case
        [b'R' | b'r', b'\'', ..] => true,        // r' or R'
        [b'B' | b'b', b'\'', ..] => true,        // b' or B'
        [b'R' | b'r', b'B' | b'b', b'\'', ..] => true, // rb', RB', etc.
        [b'B' | b'b', b'R' | b'r', b'\'', ..] => true, // br', Br', etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Redshift,
        "double_quote",
        r#""([^"]|"")*""#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'"', ..] => true,                     // Just a double quote
        [b'R' | b'r', b'"', ..] => true,        // r" or R"
        [b'B' | b'b', b'"', ..] => true,        // b" or B"
        [b'R' | b'r', b'B' | b'b', b'"', ..] => true, // rb", RB", etc.
        [b'B' | b'b', b'R' | b'r', b'"', ..] => true, // br", Br", etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Redshift,
        "back_quote",
        r#"`(?:[^`\\]|\\.)*`"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Redshift,
        "dollar_quote",
        r#"\$(\w*)\$(.*?)\$\1\$"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with("$"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Redshift,
        "numeric_literal",
        r#"(?>\d+\.\d+|\d+\.(?![\.\w])|\.\d+|\d+)(\.?[eE][+-]?\d+)?((?<=\.)|(?=\b))"#,
        Token::literal_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['.','0','1','2','3','4','5','6','7','8','9']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Redshift,
        "unicode_single_quote",
        r#"(?si)U&'([^']|'')*'(\s*UESCAPE\s*'[^0-9A-Fa-f'+\-\s)]')?"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Redshift,
        "escaped_single_quote",
        r#"(?si)E(('')+?(?!')|'.*?((?<!\\)(?:\\\\)*(?<!')(?:'')*|(?<!\\)(?:\\\\)*\\(?<!')(?:'')*')'(?!'))"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['E', 'e']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Redshift,
        "unicode_double_quote",
        r#"(?si)U&".+?"(\s*UESCAPE\s*\'[^0-9A-Fa-f\'+\-\s)]\')?"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Redshift,
        "json_operator",
        r#"->>?|#>>?|@[>@?]|<@|\?[|&]?|#-"#,
        Token::symbol_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Redshift,
        "postgis_operator",
        r#"\&\&\&|\&<\||<<\||@|\|\&>|\|>>|\~=|<\->|\|=\||<\#>|<<\->>|<<\#>>"#,
        Token::symbol_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::string_lexer(
        Dialect::Redshift,
        "at",
        "@",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Redshift,
        "bit_string_literal",
        r#"[bBxX]'[0-9a-fA-F]*'"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::string_lexer(
        Dialect::Redshift,
        "full_text_search_operator",
        "!!",
        Token::symbol_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Redshift,
        "like_operator",
        r#"!?~~?\*?"#,
        Token::comparison_operator_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Redshift,
        "newline",
        r#"\r?\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::string_lexer(
        Dialect::Redshift,
        "casting_operator",
        "::",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Redshift,
        "right_arrow",
        "=>",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Redshift,
        "walrus_operator",
        ":=",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Redshift,
        "equals",
        "=",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Redshift,
        "greater_than",
        ">",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Redshift,
        "less_than",
        "<",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Redshift,
        "not",
        "!",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Redshift,
        "dot",
        ".",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Redshift,
        "comma",
        ",",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Redshift,
        "plus",
        "+",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Redshift,
        "minus",
        "-",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Redshift,
        "divide",
        "/",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Redshift,
        "percent",
        "%",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Redshift,
        "question",
        "?",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Redshift,
        "ampersand",
        "&",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Redshift,
        "vertical_bar",
        "|",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Redshift,
        "caret",
        "^",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Redshift,
        "star",
        "*",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Redshift,
        "start_bracket",
        "(",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Redshift,
        "end_bracket",
        ")",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Redshift,
        "start_square_bracket",
        "[",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Redshift,
        "end_square_bracket",
        "]",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Redshift,
        "start_curly_bracket",
        "{",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Redshift,
        "end_curly_bracket",
        "}",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Redshift,
        "colon",
        ":",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Redshift,
        "semicolon",
        ";",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Redshift,
        "meta_command",
        r#"\\(?!gset|gexec)([^\\\r\n])+((\\\\)|(?=\n)|(?=\r\n))?"#,
        Token::comment_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['\\']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Redshift,
        "dollar_numeric_literal",
        r#"\$\d+"#,
        Token::literal_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Redshift,
        "meta_command_query_buffer",
        r#"\\([^\\\r\n])+((\\g(set|exec))|(?=\n)|(?=\r\n))?"#,
        Token::symbol_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['\\']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Redshift,
        "word",
        r#"#?[0-9a-zA-Z_]+[0-9a-zA-Z_$]*"#,
        Token::word_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),
]});
pub static SNOWFLAKE_LEXERS: Lazy<Vec<LexMatcher>> = Lazy::new(|| { vec![

    LexMatcher::regex_lexer(
        Dialect::Snowflake,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Snowflake,
        "inline_comment",
        r#"(--|#|//)[^\n]*"#,
        Token::comment_token,
        None,
        None,
        Some(vec![String::from("--"), String::from("#"), String::from("//")]),
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['#','-','/']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Snowflake,
        "block_comment",
        r#"\/\*([^\*]|\*(?!\/))*\*\/"#,
        Token::comment_token,
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Snowflake,
        "newline",
        r#"\r\n|\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Snowflake,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        None,
        None,
        Uuid::new_v4().to_string(),
        Some(extract_nested_block_comment),
        |input| input.starts_with("/"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Snowflake,
        "single_quote",
        r#"'([^'\\]|\\.|'')*'"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'\'', ..] => true,                     // Single quote case
        [b'R' | b'r', b'\'', ..] => true,        // r' or R'
        [b'B' | b'b', b'\'', ..] => true,        // b' or B'
        [b'R' | b'r', b'B' | b'b', b'\'', ..] => true, // rb', RB', etc.
        [b'B' | b'b', b'R' | b'r', b'\'', ..] => true, // br', Br', etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Snowflake,
        "double_quote",
        r#""(""|[^"\\]|\\.)*""#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'"', ..] => true,                     // Just a double quote
        [b'R' | b'r', b'"', ..] => true,        // r" or R"
        [b'B' | b'b', b'"', ..] => true,        // b" or B"
        [b'R' | b'r', b'B' | b'b', b'"', ..] => true, // rb", RB", etc.
        [b'B' | b'b', b'R' | b'r', b'"', ..] => true, // br", Br", etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Snowflake,
        "back_quote",
        r#"`(?:[^`\\]|\\.)*`"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Snowflake,
        "dollar_quote",
        r#"\$(\w*)\$(.*?)\$\1\$"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with("$"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Snowflake,
        "numeric_literal",
        r#"(?>\d+\.\d+|\d+\.(?![\.\w])|\.\d+|\d+)(\.?[eE][+-]?\d+)?((?<=\.)|(?=\b))"#,
        Token::literal_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['.','0','1','2','3','4','5','6','7','8','9']),
    ),

    LexMatcher::string_lexer(
        Dialect::Snowflake,
        "parameter_assigner",
        "=>",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Snowflake,
        "function_assigner",
        "->",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Snowflake,
        "stage_path",
        r#"(?:@[^\s;)]+|'@[^']+')"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Snowflake,
        "column_selector",
        r#"\$[0-9]+"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Snowflake,
        "dollar_quote",
        r#"\$\$.*\$\$"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with("$"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Snowflake,
        "dollar_literal",
        r#"[$][a-zA-Z0-9_.]*"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Snowflake,
        "inline_dollar_sign",
        r#"[a-zA-Z_][a-zA-Z0-9_$]*\$[a-zA-Z0-9_$]*"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Snowflake,
        "unquoted_file_path",
        r#"file://(?:[a-zA-Z]+:|/)+(?:[0-9a-zA-Z\\/_*?-]+)(?:\.[0-9a-zA-Z]+)?"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::string_lexer(
        Dialect::Snowflake,
        "question_mark",
        "?",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Snowflake,
        "exclude_bracket_open",
        "{-",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Snowflake,
        "exclude_bracket_close",
        "-}",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Snowflake,
        "like_operator",
        r#"!?~~?\*?"#,
        Token::comparison_operator_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Snowflake,
        "newline",
        r#"\r?\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::string_lexer(
        Dialect::Snowflake,
        "casting_operator",
        "::",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Snowflake,
        "walrus_operator",
        ":=",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Snowflake,
        "equals",
        "=",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Snowflake,
        "greater_than",
        ">",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Snowflake,
        "less_than",
        "<",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Snowflake,
        "not",
        "!",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Snowflake,
        "dot",
        ".",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Snowflake,
        "comma",
        ",",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Snowflake,
        "plus",
        "+",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Snowflake,
        "minus",
        "-",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Snowflake,
        "divide",
        "/",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Snowflake,
        "percent",
        "%",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Snowflake,
        "question",
        "?",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Snowflake,
        "ampersand",
        "&",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Snowflake,
        "vertical_bar",
        "|",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Snowflake,
        "caret",
        "^",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Snowflake,
        "star",
        "*",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Snowflake,
        "start_bracket",
        "(",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Snowflake,
        "end_bracket",
        ")",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Snowflake,
        "start_square_bracket",
        "[",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Snowflake,
        "end_square_bracket",
        "]",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Snowflake,
        "start_curly_bracket",
        "{",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Snowflake,
        "end_curly_bracket",
        "}",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Snowflake,
        "colon",
        ":",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Snowflake,
        "semicolon",
        ";",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Snowflake,
        "word",
        r#"[0-9a-zA-Z_]+"#,
        Token::word_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),
]});
pub static SOQL_LEXERS: Lazy<Vec<LexMatcher>> = Lazy::new(|| { vec![

    LexMatcher::regex_lexer(
        Dialect::Soql,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Soql,
        "inline_comment",
        r#"(--|#)[^\n]*"#,
        Token::comment_token,
        None,
        None,
        Some(vec![String::from("--"), String::from("#")]),
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['#','-','/']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Soql,
        "block_comment",
        r#"\/\*([^\*]|\*(?!\/))*\*\/"#,
        Token::comment_token,
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Soql,
        "newline",
        r#"\r\n|\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Soql,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        None,
        None,
        Uuid::new_v4().to_string(),
        Some(extract_nested_block_comment),
        |input| input.starts_with("/"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Soql,
        "single_quote",
        r#"'([^'\\]|\\.|'')*'"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'\'', ..] => true,                     // Single quote case
        [b'R' | b'r', b'\'', ..] => true,        // r' or R'
        [b'B' | b'b', b'\'', ..] => true,        // b' or B'
        [b'R' | b'r', b'B' | b'b', b'\'', ..] => true, // rb', RB', etc.
        [b'B' | b'b', b'R' | b'r', b'\'', ..] => true, // br', Br', etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Soql,
        "double_quote",
        r#""(""|[^"\\]|\\.)*""#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'"', ..] => true,                     // Just a double quote
        [b'R' | b'r', b'"', ..] => true,        // r" or R"
        [b'B' | b'b', b'"', ..] => true,        // b" or B"
        [b'R' | b'r', b'B' | b'b', b'"', ..] => true, // rb", RB", etc.
        [b'B' | b'b', b'R' | b'r', b'"', ..] => true, // br", Br", etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Soql,
        "back_quote",
        r#"`(?:[^`\\]|\\.)*`"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Soql,
        "dollar_quote",
        r#"\$(\w*)\$(.*?)\$\1\$"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with("$"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Soql,
        "datetime_literal",
        r#"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(Z|(\+|\-)[0-9]{2}:[0-9]{2})"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Soql,
        "date_literal",
        r#"[0-9]{4}-[0-9]{2}-[0-9]{2}"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Soql,
        "numeric_literal",
        r#"(?>\d+\.\d+|\d+\.(?![\.\w])|\.\d+|\d+)(\.?[eE][+-]?\d+)?((?<=\.)|(?=\b))"#,
        Token::literal_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['.','0','1','2','3','4','5','6','7','8','9']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Soql,
        "like_operator",
        r#"!?~~?\*?"#,
        Token::comparison_operator_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Soql,
        "newline",
        r#"\r?\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::string_lexer(
        Dialect::Soql,
        "casting_operator",
        "::",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Soql,
        "equals",
        "=",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Soql,
        "greater_than",
        ">",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Soql,
        "less_than",
        "<",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Soql,
        "not",
        "!",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Soql,
        "dot",
        ".",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Soql,
        "comma",
        ",",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Soql,
        "plus",
        "+",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Soql,
        "minus",
        "-",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Soql,
        "divide",
        "/",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Soql,
        "percent",
        "%",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Soql,
        "question",
        "?",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Soql,
        "ampersand",
        "&",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Soql,
        "vertical_bar",
        "|",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Soql,
        "caret",
        "^",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Soql,
        "star",
        "*",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Soql,
        "start_bracket",
        "(",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Soql,
        "end_bracket",
        ")",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Soql,
        "start_square_bracket",
        "[",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Soql,
        "end_square_bracket",
        "]",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Soql,
        "start_curly_bracket",
        "{",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Soql,
        "end_curly_bracket",
        "}",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Soql,
        "colon",
        ":",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Soql,
        "semicolon",
        ";",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Soql,
        "word",
        r#"[0-9a-zA-Z_]+"#,
        Token::word_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),
]});
pub static SPARKSQL_LEXERS: Lazy<Vec<LexMatcher>> = Lazy::new(|| { vec![

    LexMatcher::regex_lexer(
        Dialect::Sparksql,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Sparksql,
        "inline_comment",
        r#"(--)[^\n]*"#,
        Token::comment_token,
        None,
        None,
        Some(vec![String::from("-"), String::from("-")]),
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['#','-','/']),
    ),

    LexMatcher::string_lexer(
        Dialect::Sparksql,
        "start_hint",
        "/*+",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Sparksql,
        "block_comment",
        r#"\/\*([^\*]|\*(?!\/))*\*\/"#,
        Token::comment_token,
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Sparksql,
        "newline",
        r#"\r\n|\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Sparksql,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        None,
        None,
        Uuid::new_v4().to_string(),
        Some(extract_nested_block_comment),
        |input| input.starts_with("/"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Sparksql,
        "raw_single_quote",
        r#"[rR]'([^'\\]|\\.)*'"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Sparksql,
        "raw_double_quote",
        r#"[rR]"([^"\\]|\\.)*""#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Sparksql,
        "bytes_single_quote",
        r#"X'([^'\\]|\\.)*'"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Sparksql,
        "bytes_double_quote",
        r#"X"([^"\\]|\\.)*""#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::string_lexer(
        Dialect::Sparksql,
        "end_hint",
        "*/",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Sparksql,
        "single_quote",
        r#"'([^'\\]|\\.|'')*'"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'\'', ..] => true,                     // Single quote case
        [b'R' | b'r', b'\'', ..] => true,        // r' or R'
        [b'B' | b'b', b'\'', ..] => true,        // b' or B'
        [b'R' | b'r', b'B' | b'b', b'\'', ..] => true, // rb', RB', etc.
        [b'B' | b'b', b'R' | b'r', b'\'', ..] => true, // br', Br', etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Sparksql,
        "double_quote",
        r#""(""|[^"\\]|\\.)*""#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'"', ..] => true,                     // Just a double quote
        [b'R' | b'r', b'"', ..] => true,        // r" or R"
        [b'B' | b'b', b'"', ..] => true,        // b" or B"
        [b'R' | b'r', b'B' | b'b', b'"', ..] => true, // rb", RB", etc.
        [b'B' | b'b', b'R' | b'r', b'"', ..] => true, // br", Br", etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Sparksql,
        "back_quote",
        r#"`([^`]|``)*`"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Sparksql,
        "dollar_quote",
        r#"\$(\w*)\$(.*?)\$\1\$"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with("$"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Sparksql,
        "numeric_literal",
        r#"(?>(?>\d+\.\d+|\d+\.|\.\d+)([eE][+-]?\d+)?([dDfF]|BD|bd)?|\d+[eE][+-]?\d+([dDfF]|BD|bd)?|\d+([dDfFlLsSyY]|BD|bd)?)((?<=\.)|(?=\b))"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['.','0','1','2','3','4','5','6','7','8','9']),
    ),

    LexMatcher::string_lexer(
        Dialect::Sparksql,
        "right_arrow",
        "->",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Sparksql,
        "like_operator",
        r#"!?~~?\*?"#,
        Token::comparison_operator_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Sparksql,
        "file_literal",
        r#"[a-zA-Z0-9]+:([a-zA-Z0-9\-_\.]*(\/|\\)){2,}((([a-zA-Z0-9\-_\.]*(:|\?|=|&)[a-zA-Z0-9\-_\.]*)+)|([a-zA-Z0-9\-_\.]*\.[a-z]+))"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Sparksql,
        "newline",
        r#"\r?\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::string_lexer(
        Dialect::Sparksql,
        "casting_operator",
        "::",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Sparksql,
        "equals",
        r#"==|<=>|="#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::string_lexer(
        Dialect::Sparksql,
        "greater_than",
        ">",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Sparksql,
        "less_than",
        "<",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Sparksql,
        "not",
        "!",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Sparksql,
        "dot",
        ".",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Sparksql,
        "comma",
        ",",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Sparksql,
        "plus",
        "+",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Sparksql,
        "minus",
        "-",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Sparksql,
        "divide",
        "/",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Sparksql,
        "percent",
        "%",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Sparksql,
        "question",
        "?",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Sparksql,
        "ampersand",
        "&",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Sparksql,
        "vertical_bar",
        "|",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Sparksql,
        "caret",
        "^",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Sparksql,
        "star",
        "*",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Sparksql,
        "start_bracket",
        "(",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Sparksql,
        "end_bracket",
        ")",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Sparksql,
        "start_square_bracket",
        "[",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Sparksql,
        "end_square_bracket",
        "]",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Sparksql,
        "start_curly_bracket",
        "{",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Sparksql,
        "end_curly_bracket",
        "}",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Sparksql,
        "colon",
        ":",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Sparksql,
        "semicolon",
        ";",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Sparksql,
        "at_sign_literal",
        r#"@\w*"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Sparksql,
        "word",
        r#"[0-9a-zA-Z_]+"#,
        Token::word_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),
]});
pub static SQLITE_LEXERS: Lazy<Vec<LexMatcher>> = Lazy::new(|| { vec![

    LexMatcher::regex_lexer(
        Dialect::Sqlite,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Sqlite,
        "inline_comment",
        r#"(--|#)[^\n]*"#,
        Token::comment_token,
        None,
        None,
        Some(vec![String::from("--"), String::from("#")]),
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['#','-','/']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Sqlite,
        "block_comment",
        r#"\/\*([^\*]|\*(?!\/))*(\*\/|\Z)"#,
        Token::comment_token,
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Sqlite,
        "newline",
        r#"\r\n|\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Sqlite,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        None,
        None,
        Uuid::new_v4().to_string(),
        Some(extract_nested_block_comment),
        |input| input.starts_with("/"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Sqlite,
        "single_quote",
        r#"'([^']|'')*'"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'\'', ..] => true,                     // Single quote case
        [b'R' | b'r', b'\'', ..] => true,        // r' or R'
        [b'B' | b'b', b'\'', ..] => true,        // b' or B'
        [b'R' | b'r', b'B' | b'b', b'\'', ..] => true, // rb', RB', etc.
        [b'B' | b'b', b'R' | b'r', b'\'', ..] => true, // br', Br', etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Sqlite,
        "double_quote",
        r#""([^"]|"")*""#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'"', ..] => true,                     // Just a double quote
        [b'R' | b'r', b'"', ..] => true,        // r" or R"
        [b'B' | b'b', b'"', ..] => true,        // b" or B"
        [b'R' | b'r', b'B' | b'b', b'"', ..] => true, // rb", RB", etc.
        [b'B' | b'b', b'R' | b'r', b'"', ..] => true, // br", Br", etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Sqlite,
        "back_quote",
        r#"`([^`]|``)*`"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Sqlite,
        "dollar_quote",
        r#"\$(\w*)\$(.*?)\$\1\$"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with("$"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Sqlite,
        "numeric_literal",
        r#"(?>\d+\.\d+|\d+\.(?![\.\w])|\.\d+|\d+)(\.?[eE][+-]?\d+)?((?<=\.)|(?=\b))"#,
        Token::literal_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['.','0','1','2','3','4','5','6','7','8','9']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Sqlite,
        "like_operator",
        r#"!?~~?\*?"#,
        Token::comparison_operator_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Sqlite,
        "newline",
        r#"\r?\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::string_lexer(
        Dialect::Sqlite,
        "casting_operator",
        "::",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Sqlite,
        "equals",
        "=",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Sqlite,
        "inline_path_operator",
        "->>",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Sqlite,
        "column_path_operator",
        "->",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Sqlite,
        "greater_than",
        ">",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Sqlite,
        "less_than",
        "<",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Sqlite,
        "not",
        "!",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Sqlite,
        "dot",
        ".",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Sqlite,
        "comma",
        ",",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Sqlite,
        "plus",
        "+",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Sqlite,
        "minus",
        "-",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Sqlite,
        "divide",
        "/",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Sqlite,
        "percent",
        "%",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Sqlite,
        "at_sign_literal",
        r#"@[a-zA-Z0-9_]+"#,
        Token::literal_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Sqlite,
        "colon_literal",
        r#":[a-zA-Z0-9_]+"#,
        Token::literal_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Sqlite,
        "question_literal",
        r#"\?[0-9]+"#,
        Token::literal_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Sqlite,
        "dollar_literal",
        r#"\$[a-zA-Z0-9_]+"#,
        Token::literal_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::string_lexer(
        Dialect::Sqlite,
        "question",
        "?",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Sqlite,
        "ampersand",
        "&",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Sqlite,
        "vertical_bar",
        "|",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Sqlite,
        "caret",
        "^",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Sqlite,
        "star",
        "*",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Sqlite,
        "start_bracket",
        "(",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Sqlite,
        "end_bracket",
        ")",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Sqlite,
        "start_square_bracket",
        "[",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Sqlite,
        "end_square_bracket",
        "]",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Sqlite,
        "start_curly_bracket",
        "{",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Sqlite,
        "end_curly_bracket",
        "}",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Sqlite,
        "colon",
        ":",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Sqlite,
        "semicolon",
        ";",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Sqlite,
        "word",
        r#"[0-9a-zA-Z_]+"#,
        Token::word_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),
]});
pub static STARROCKS_LEXERS: Lazy<Vec<LexMatcher>> = Lazy::new(|| { vec![

    LexMatcher::regex_lexer(
        Dialect::Starrocks,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Starrocks,
        "inline_comment",
        r#"(^--|-- |#)[^\n]*"#,
        Token::comment_token,
        None,
        None,
        Some(vec![String::from("--"), String::from("#")]),
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['#','-','/']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Starrocks,
        "block_comment",
        r#"\/\*([^\*]|\*(?!\/))*\*\/"#,
        Token::comment_token,
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Starrocks,
        "newline",
        r#"\r\n|\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Starrocks,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        None,
        None,
        Uuid::new_v4().to_string(),
        Some(extract_nested_block_comment),
        |input| input.starts_with("/"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Starrocks,
        "single_quote",
        r#"(?s)('(?:\\'|''|\\\\|[^'])*'(?!'))"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'\'', ..] => true,                     // Single quote case
        [b'R' | b'r', b'\'', ..] => true,        // r' or R'
        [b'B' | b'b', b'\'', ..] => true,        // b' or B'
        [b'R' | b'r', b'B' | b'b', b'\'', ..] => true, // rb', RB', etc.
        [b'B' | b'b', b'R' | b'r', b'\'', ..] => true, // br', Br', etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Starrocks,
        "double_quote",
        r#"(?s)("(?:\\"|""|\\\\|[^"])*"(?!"))"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'"', ..] => true,                     // Just a double quote
        [b'R' | b'r', b'"', ..] => true,        // r" or R"
        [b'B' | b'b', b'"', ..] => true,        // b" or B"
        [b'R' | b'r', b'B' | b'b', b'"', ..] => true, // rb", RB", etc.
        [b'B' | b'b', b'R' | b'r', b'"', ..] => true, // br", Br", etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Starrocks,
        "back_quote",
        r#"`(?:[^`\\]|\\.)*`"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Starrocks,
        "dollar_quote",
        r#"\$(\w*)\$(.*?)\$\1\$"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with("$"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Starrocks,
        "hexadecimal_literal",
        r#"([xX]'([\da-fA-F][\da-fA-F])+'|0x[\da-fA-F]+)"#,
        Token::literal_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Starrocks,
        "bit_value_literal",
        r#"([bB]'[01]+'|0b[01]+)"#,
        Token::literal_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Starrocks,
        "numeric_literal",
        r#"(?>\d+\.\d+|\d+\.(?![\.\w])|\.\d+|\d+)(\.?[eE][+-]?\d+)?((?<=\.)|(?=\b))"#,
        Token::literal_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['.','0','1','2','3','4','5','6','7','8','9']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Starrocks,
        "like_operator",
        r#"!?~~?\*?"#,
        Token::comparison_operator_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Starrocks,
        "newline",
        r#"\r?\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::string_lexer(
        Dialect::Starrocks,
        "casting_operator",
        "::",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Starrocks,
        "walrus_operator",
        ":=",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Starrocks,
        "equals",
        "=",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Starrocks,
        "inline_path_operator",
        "->>",
        Token::symbol_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Starrocks,
        "column_path_operator",
        "->",
        Token::symbol_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Starrocks,
        "greater_than",
        ">",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Starrocks,
        "less_than",
        "<",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Starrocks,
        "not",
        "!",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Starrocks,
        "dot",
        ".",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Starrocks,
        "comma",
        ",",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Starrocks,
        "plus",
        "+",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Starrocks,
        "minus",
        "-",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Starrocks,
        "divide",
        "/",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Starrocks,
        "percent",
        "%",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Starrocks,
        "question",
        "?",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Starrocks,
        "double_ampersand",
        "&&",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Starrocks,
        "ampersand",
        "&",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Starrocks,
        "double_vertical_bar",
        "||",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Starrocks,
        "vertical_bar",
        "|",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Starrocks,
        "caret",
        "^",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Starrocks,
        "star",
        "*",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Starrocks,
        "start_bracket",
        "(",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Starrocks,
        "end_bracket",
        ")",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Starrocks,
        "start_square_bracket",
        "[",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Starrocks,
        "end_square_bracket",
        "]",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Starrocks,
        "start_curly_bracket",
        "{",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Starrocks,
        "end_curly_bracket",
        "}",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Starrocks,
        "colon",
        ":",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Starrocks,
        "semicolon",
        ";",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Starrocks,
        "at_sign",
        r#"@@?[a-zA-Z0-9_$]*(\.[a-zA-Z0-9_$]+)?"#,
        Token::code_token,
        None,
        None,
        None,
        Some(vec![String::from("@")]),
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Starrocks,
        "word",
        r#"[0-9a-zA-Z_]+"#,
        Token::word_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),
]});
pub static TERADATA_LEXERS: Lazy<Vec<LexMatcher>> = Lazy::new(|| { vec![

    LexMatcher::regex_lexer(
        Dialect::Teradata,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Teradata,
        "inline_comment",
        r#"(--|#)[^\n]*"#,
        Token::comment_token,
        None,
        None,
        Some(vec![String::from("--"), String::from("#")]),
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['#','-','/']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Teradata,
        "block_comment",
        r#"\/\*([^\*]|\*(?!\/))*\*\/"#,
        Token::comment_token,
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Teradata,
        "newline",
        r#"\r\n|\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Teradata,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        None,
        None,
        Uuid::new_v4().to_string(),
        Some(extract_nested_block_comment),
        |input| input.starts_with("/"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Teradata,
        "single_quote",
        r#"'([^'\\]|\\.|'')*'"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'\'', ..] => true,                     // Single quote case
        [b'R' | b'r', b'\'', ..] => true,        // r' or R'
        [b'B' | b'b', b'\'', ..] => true,        // b' or B'
        [b'R' | b'r', b'B' | b'b', b'\'', ..] => true, // rb', RB', etc.
        [b'B' | b'b', b'R' | b'r', b'\'', ..] => true, // br', Br', etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Teradata,
        "double_quote",
        r#""(""|[^"\\]|\\.)*""#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'"', ..] => true,                     // Just a double quote
        [b'R' | b'r', b'"', ..] => true,        // r" or R"
        [b'B' | b'b', b'"', ..] => true,        // b" or B"
        [b'R' | b'r', b'B' | b'b', b'"', ..] => true, // rb", RB", etc.
        [b'B' | b'b', b'R' | b'r', b'"', ..] => true, // br", Br", etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Teradata,
        "back_quote",
        r#"`(?:[^`\\]|\\.)*`"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Teradata,
        "dollar_quote",
        r#"\$(\w*)\$(.*?)\$\1\$"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with("$"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Teradata,
        "numeric_literal",
        r#"([0-9]+(\.[0-9]*)?)"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['.','0','1','2','3','4','5','6','7','8','9']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Teradata,
        "like_operator",
        r#"!?~~?\*?"#,
        Token::comparison_operator_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Teradata,
        "newline",
        r#"\r?\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::string_lexer(
        Dialect::Teradata,
        "casting_operator",
        "::",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Teradata,
        "equals",
        "=",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Teradata,
        "greater_than",
        ">",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Teradata,
        "less_than",
        "<",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Teradata,
        "not",
        "!",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Teradata,
        "dot",
        ".",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Teradata,
        "comma",
        ",",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Teradata,
        "plus",
        "+",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Teradata,
        "minus",
        "-",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Teradata,
        "divide",
        "/",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Teradata,
        "percent",
        "%",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Teradata,
        "question",
        "?",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Teradata,
        "ampersand",
        "&",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Teradata,
        "vertical_bar",
        "|",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Teradata,
        "caret",
        "^",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Teradata,
        "star",
        "*",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Teradata,
        "start_bracket",
        "(",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Teradata,
        "end_bracket",
        ")",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Teradata,
        "start_square_bracket",
        "[",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Teradata,
        "end_square_bracket",
        "]",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Teradata,
        "start_curly_bracket",
        "{",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Teradata,
        "end_curly_bracket",
        "}",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Teradata,
        "colon",
        ":",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Teradata,
        "semicolon",
        ";",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Teradata,
        "word",
        r#"[0-9a-zA-Z_]+"#,
        Token::word_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),
]});
pub static TRINO_LEXERS: Lazy<Vec<LexMatcher>> = Lazy::new(|| { vec![

    LexMatcher::regex_lexer(
        Dialect::Trino,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Trino,
        "inline_comment",
        r#"(--|#)[^\n]*"#,
        Token::comment_token,
        None,
        None,
        Some(vec![String::from("--"), String::from("#")]),
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['#','-','/']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Trino,
        "block_comment",
        r#"\/\*([^\*]|\*(?!\/))*\*\/"#,
        Token::comment_token,
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Trino,
        "newline",
        r#"\r\n|\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Trino,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        None,
        None,
        Uuid::new_v4().to_string(),
        Some(extract_nested_block_comment),
        |input| input.starts_with("/"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Trino,
        "single_quote",
        r#"'([^'\\]|\\.|'')*'"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'\'', ..] => true,                     // Single quote case
        [b'R' | b'r', b'\'', ..] => true,        // r' or R'
        [b'B' | b'b', b'\'', ..] => true,        // b' or B'
        [b'R' | b'r', b'B' | b'b', b'\'', ..] => true, // rb', RB', etc.
        [b'B' | b'b', b'R' | b'r', b'\'', ..] => true, // br', Br', etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Trino,
        "double_quote",
        r#""([^"]|"")*""#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'"', ..] => true,                     // Just a double quote
        [b'R' | b'r', b'"', ..] => true,        // r" or R"
        [b'B' | b'b', b'"', ..] => true,        // b" or B"
        [b'R' | b'r', b'B' | b'b', b'"', ..] => true, // rb", RB", etc.
        [b'B' | b'b', b'R' | b'r', b'"', ..] => true, // br", Br", etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Trino,
        "back_quote",
        r#"`(?:[^`\\]|\\.)*`"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Trino,
        "dollar_quote",
        r#"\$(\w*)\$(.*?)\$\1\$"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with("$"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Trino,
        "numeric_literal",
        r#"(?>\d+\.\d+|\d+\.(?![\.\w])|\.\d+|\d+)(\.?[eE][+-]?\d+)?((?<=\.)|(?=\b))"#,
        Token::literal_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['.','0','1','2','3','4','5','6','7','8','9']),
    ),

    LexMatcher::string_lexer(
        Dialect::Trino,
        "right_arrow",
        "->",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Trino,
        "like_operator",
        r#"!?~~?\*?"#,
        Token::comparison_operator_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Trino,
        "newline",
        r#"\r?\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::string_lexer(
        Dialect::Trino,
        "casting_operator",
        "::",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Trino,
        "equals",
        "=",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Trino,
        "greater_than",
        ">",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Trino,
        "less_than",
        "<",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Trino,
        "not",
        "!",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Trino,
        "dot",
        ".",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Trino,
        "comma",
        ",",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Trino,
        "plus",
        "+",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Trino,
        "minus",
        "-",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Trino,
        "divide",
        "/",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Trino,
        "percent",
        "%",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Trino,
        "question",
        "?",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Trino,
        "ampersand",
        "&",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Trino,
        "vertical_bar",
        "|",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Trino,
        "caret",
        "^",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Trino,
        "star",
        "*",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Trino,
        "start_bracket",
        "(",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Trino,
        "end_bracket",
        ")",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Trino,
        "start_square_bracket",
        "[",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Trino,
        "end_square_bracket",
        "]",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Trino,
        "start_curly_bracket",
        "{",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Trino,
        "end_curly_bracket",
        "}",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Trino,
        "colon",
        ":",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Trino,
        "semicolon",
        ";",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Trino,
        "word",
        r#"[0-9a-zA-Z_]+"#,
        Token::word_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),
]});
pub static TSQL_LEXERS: Lazy<Vec<LexMatcher>> = Lazy::new(|| { vec![

    LexMatcher::regex_lexer(
        Dialect::Tsql,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Tsql,
        "inline_comment",
        r#"(--)[^\n]*"#,
        Token::comment_token,
        None,
        None,
        Some(vec![String::from("-"), String::from("-")]),
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['#','-','/']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Tsql,
        "block_comment",
        r#"/\*(?>[^*/]+|\*(?!\/)|/[^*])*(?>(?R)(?>[^*/]+|\*(?!\/)|/[^*])*)*\*/"#,
        Token::comment_token,
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Tsql,
        "newline",
        r#"\r\n|\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Tsql,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        None,
        None,
        Uuid::new_v4().to_string(),
        Some(extract_nested_block_comment),
        |input| input.starts_with("/"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Tsql,
        "single_quote",
        r#"'([^']|'')*'"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'\'', ..] => true,                     // Single quote case
        [b'R' | b'r', b'\'', ..] => true,        // r' or R'
        [b'B' | b'b', b'\'', ..] => true,        // b' or B'
        [b'R' | b'r', b'B' | b'b', b'\'', ..] => true, // rb', RB', etc.
        [b'B' | b'b', b'R' | b'r', b'\'', ..] => true, // br', Br', etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Tsql,
        "double_quote",
        r#""(""|[^"\\]|\\.)*""#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'"', ..] => true,                     // Just a double quote
        [b'R' | b'r', b'"', ..] => true,        // r" or R"
        [b'B' | b'b', b'"', ..] => true,        // b" or B"
        [b'R' | b'r', b'B' | b'b', b'"', ..] => true, // rb", RB", etc.
        [b'B' | b'b', b'R' | b'r', b'"', ..] => true, // br", Br", etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Tsql,
        "atsign",
        r#"[@][a-zA-Z0-9_]+"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Tsql,
        "var_prefix",
        r#"[$][a-zA-Z0-9_]+"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Tsql,
        "square_quote",
        r#"\[([^\[\]]*)*\]"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Tsql,
        "single_quote_with_n",
        r#"N'([^']|'')*'"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Tsql,
        "hash_prefix",
        r#"[#][#]?[a-zA-Z0-9_]+"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Tsql,
        "unquoted_relative_sql_file_path",
        r#"[.\w\\/#-]+\.[sS][qQ][lL]\b"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Tsql,
        "back_quote",
        r#"`(?:[^`\\]|\\.)*`"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Tsql,
        "dollar_quote",
        r#"\$(\w*)\$(.*?)\$\1\$"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with("$"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Tsql,
        "numeric_literal",
        r#"(?>\d+\.\d+|\d+\.(?![\.\w])|\.\d+|\d+)(\.?[eE][+-]?\d+)?((?<=\.)|(?=\b))"#,
        Token::literal_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['.','0','1','2','3','4','5','6','7','8','9']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Tsql,
        "like_operator",
        r#"!?~~?\*?"#,
        Token::comparison_operator_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Tsql,
        "newline",
        r#"\r?\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::string_lexer(
        Dialect::Tsql,
        "casting_operator",
        "::",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Tsql,
        "equals",
        "=",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Tsql,
        "greater_than",
        ">",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Tsql,
        "less_than",
        "<",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Tsql,
        "not",
        "!",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Tsql,
        "dot",
        ".",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Tsql,
        "comma",
        ",",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Tsql,
        "plus",
        "+",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Tsql,
        "minus",
        "-",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Tsql,
        "divide",
        "/",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Tsql,
        "percent",
        "%",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Tsql,
        "question",
        "?",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Tsql,
        "ampersand",
        "&",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Tsql,
        "vertical_bar",
        "|",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Tsql,
        "caret",
        "^",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Tsql,
        "star",
        "*",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Tsql,
        "start_bracket",
        "(",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Tsql,
        "end_bracket",
        ")",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Tsql,
        "start_square_bracket",
        "[",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Tsql,
        "end_square_bracket",
        "]",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Tsql,
        "start_curly_bracket",
        "{",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Tsql,
        "end_curly_bracket",
        "}",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Tsql,
        "colon",
        ":",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Tsql,
        "semicolon",
        ";",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Tsql,
        "word",
        r#"[0-9a-zA-Z_#@]+"#,
        Token::word_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),
]});
pub static VERTICA_LEXERS: Lazy<Vec<LexMatcher>> = Lazy::new(|| { vec![

    LexMatcher::regex_lexer(
        Dialect::Vertica,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Vertica,
        "inline_comment",
        r#"(--|#)[^\n]*"#,
        Token::comment_token,
        None,
        None,
        Some(vec![String::from("--"), String::from("#")]),
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['#','-','/']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Vertica,
        "block_comment",
        r#"\/\*([^\*]|\*(?!\/))*\*\/"#,
        Token::comment_token,
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Vertica,
        "newline",
        r#"\r\n|\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        Some(Box::new(
    LexMatcher::regex_subdivider(
        Dialect::Vertica,
        "whitespace",
        r#"[^\S\r\n]+"#,
        Token::whitespace_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ))),
        None,
        None,
        Uuid::new_v4().to_string(),
        Some(extract_nested_block_comment),
        |input| input.starts_with("/"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Vertica,
        "single_quote",
        r#"'([^'\\]|\\.|'')*'"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'\'', ..] => true,                     // Single quote case
        [b'R' | b'r', b'\'', ..] => true,        // r' or R'
        [b'B' | b'b', b'\'', ..] => true,        // b' or B'
        [b'R' | b'r', b'B' | b'b', b'\'', ..] => true, // rb', RB', etc.
        [b'B' | b'b', b'R' | b'r', b'\'', ..] => true, // br', Br', etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Vertica,
        "double_quote",
        r#""([^"]|"")*""#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| match input.as_bytes() {
        [b'"', ..] => true,                     // Just a double quote
        [b'R' | b'r', b'"', ..] => true,        // r" or R"
        [b'B' | b'b', b'"', ..] => true,        // b" or B"
        [b'R' | b'r', b'B' | b'b', b'"', ..] => true, // rb", RB", etc.
        [b'B' | b'b', b'R' | b'r', b'"', ..] => true, // br", Br", etc.
        _ => false,
    },
    ),

    LexMatcher::regex_lexer(
        Dialect::Vertica,
        "back_quote",
        r#"`(?:[^`\\]|\\.)*`"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Vertica,
        "dollar_quote",
        r#"\$(\w*)\$(.*?)\$\1\$"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with("$"),
    ),

    LexMatcher::regex_lexer(
        Dialect::Vertica,
        "numeric_literal",
        r#"(?>\d+\.\d+|\d+\.(?![\.\w])|\.\d+|\d+)(\.?[eE][+-]?\d+)?((?<=\.)|(?=\b))"#,
        Token::literal_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['.','0','1','2','3','4','5','6','7','8','9']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Vertica,
        "escaped_single_quote",
        r#"(?s)[eE](('')+?(?!')|'.*?((?<!\\)(?:\\\\)*(?<!')(?:'')*|(?<!\\)(?:\\\\)*\\(?<!')(?:'')*')'(?!'))"#,
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |input| input.starts_with(['E', 'e']),
    ),

    LexMatcher::regex_lexer(
        Dialect::Vertica,
        "like_operator",
        r#"!?~~?\*?"#,
        Token::comparison_operator_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::regex_lexer(
        Dialect::Vertica,
        "newline",
        r#"\r?\n"#,
        Token::newline_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),

    LexMatcher::string_lexer(
        Dialect::Vertica,
        "null_casting_operator",
        "::!",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Vertica,
        "casting_operator",
        "::",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Vertica,
        "equals",
        "=",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Vertica,
        "greater_than",
        ">",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Vertica,
        "null_equals_operator",
        "<=>",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Vertica,
        "less_than",
        "<",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Vertica,
        "not",
        "!",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Vertica,
        "dot",
        ".",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Vertica,
        "comma",
        ",",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Vertica,
        "plus",
        "+",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Vertica,
        "minus",
        "-",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Vertica,
        "integer_division",
        "//",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Vertica,
        "divide",
        "/",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Vertica,
        "percent",
        "%",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Vertica,
        "question",
        "?",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Vertica,
        "ampersand",
        "&",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Vertica,
        "vertical_bar",
        "|",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Vertica,
        "caret",
        "^",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Vertica,
        "star",
        "*",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Vertica,
        "start_bracket",
        "(",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Vertica,
        "end_bracket",
        ")",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Vertica,
        "start_square_bracket",
        "[",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Vertica,
        "end_square_bracket",
        "]",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Vertica,
        "start_curly_bracket",
        "{",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Vertica,
        "end_curly_bracket",
        "}",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Vertica,
        "colon",
        ":",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::string_lexer(
        Dialect::Vertica,
        "semicolon",
        ";",
        Token::code_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        
        
    ),

    LexMatcher::regex_lexer(
        Dialect::Vertica,
        "word",
        r#"[\p{L}_][\p{L}\p{N}_$]*"#,
        Token::word_token,
        None,
        None,
        None,
        None,
        Uuid::new_v4().to_string(),
        None,
        |_| true,
    ),
]});

#[derive(Debug, Eq, PartialEq, Hash, Copy, Clone)]
pub enum Dialect {
    Ansi,
Athena,
Bigquery,
Clickhouse,
Databricks,
Db2,
Duckdb,
Exasol,
Greenplum,
Hive,
Impala,
Mariadb,
Materialize,
Mysql,
Oracle,
Postgres,
Redshift,
Snowflake,
Soql,
Sparksql,
Sqlite,
Starrocks,
Teradata,
Trino,
Tsql,
Vertica
}

impl FromStr for Dialect {
    type Err = ();
    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s {
            "ansi" => Ok(Dialect::Ansi),
"athena" => Ok(Dialect::Athena),
"bigquery" => Ok(Dialect::Bigquery),
"clickhouse" => Ok(Dialect::Clickhouse),
"databricks" => Ok(Dialect::Databricks),
"db2" => Ok(Dialect::Db2),
"duckdb" => Ok(Dialect::Duckdb),
"exasol" => Ok(Dialect::Exasol),
"greenplum" => Ok(Dialect::Greenplum),
"hive" => Ok(Dialect::Hive),
"impala" => Ok(Dialect::Impala),
"mariadb" => Ok(Dialect::Mariadb),
"materialize" => Ok(Dialect::Materialize),
"mysql" => Ok(Dialect::Mysql),
"oracle" => Ok(Dialect::Oracle),
"postgres" => Ok(Dialect::Postgres),
"redshift" => Ok(Dialect::Redshift),
"snowflake" => Ok(Dialect::Snowflake),
"soql" => Ok(Dialect::Soql),
"sparksql" => Ok(Dialect::Sparksql),
"sqlite" => Ok(Dialect::Sqlite),
"starrocks" => Ok(Dialect::Starrocks),
"teradata" => Ok(Dialect::Teradata),
"trino" => Ok(Dialect::Trino),
"tsql" => Ok(Dialect::Tsql),
"vertica" => Ok(Dialect::Vertica),
            _ => Err(())
        }
    }
}

pub fn get_lexers(dialect: Dialect) -> &'static Vec<LexMatcher> {
    match dialect {
        Dialect::Ansi => &ANSI_LEXERS,
Dialect::Athena => &ATHENA_LEXERS,
Dialect::Bigquery => &BIGQUERY_LEXERS,
Dialect::Clickhouse => &CLICKHOUSE_LEXERS,
Dialect::Databricks => &DATABRICKS_LEXERS,
Dialect::Db2 => &DB2_LEXERS,
Dialect::Duckdb => &DUCKDB_LEXERS,
Dialect::Exasol => &EXASOL_LEXERS,
Dialect::Greenplum => &GREENPLUM_LEXERS,
Dialect::Hive => &HIVE_LEXERS,
Dialect::Impala => &IMPALA_LEXERS,
Dialect::Mariadb => &MARIADB_LEXERS,
Dialect::Materialize => &MATERIALIZE_LEXERS,
Dialect::Mysql => &MYSQL_LEXERS,
Dialect::Oracle => &ORACLE_LEXERS,
Dialect::Postgres => &POSTGRES_LEXERS,
Dialect::Redshift => &REDSHIFT_LEXERS,
Dialect::Snowflake => &SNOWFLAKE_LEXERS,
Dialect::Soql => &SOQL_LEXERS,
Dialect::Sparksql => &SPARKSQL_LEXERS,
Dialect::Sqlite => &SQLITE_LEXERS,
Dialect::Starrocks => &STARROCKS_LEXERS,
Dialect::Teradata => &TERADATA_LEXERS,
Dialect::Trino => &TRINO_LEXERS,
Dialect::Tsql => &TSQL_LEXERS,
Dialect::Vertica => &VERTICA_LEXERS
    }
}

