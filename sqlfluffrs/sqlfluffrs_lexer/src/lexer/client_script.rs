//! Lexing scripts that are run through a command-line client.
//!
//! A command-line client reads a script line by line, splits it into
//! statements itself and handles some of the text before anything reaches the
//! server: commands that change the statement delimiter, commands that take
//! raw text arguments, and comment forms that depend on where they appear.
//! [`ClientScriptScanner`] lexes with the same state the client keeps, as
//! described by a dialect's [`ClientCommandRules`]. Nothing here is specific to
//! one client except what the rules say.
//!
//! This is the same scanner as `sqlfluff.core.parser.client_commands` in
//! Python, method for method. The two must emit identical tokens.

use std::sync::LazyLock;

use sqlfluffrs_types::{
    matcher::{LexMatcher, LexedElement},
    ClientCommand, ClientCommandRules, CommandEffect, Token,
};

use super::Lexer;

/// The active delimiter, when it isn't the default one.
static CLIENT_DELIMITER: LazyLock<LexMatcher> =
    LazyLock::new(|| LexMatcher::emitted("client_delimiter", Token::client_text_token));
/// The short form of a command, such as `\d`, `\.` or `\g`.
static CLIENT_COMMAND_SHORTHAND: LazyLock<LexMatcher> =
    LazyLock::new(|| LexMatcher::emitted("client_command_shorthand", Token::code_token));
/// The new delimiter in `DELIMITER $$`, as written.
static DELIMITER_ARGUMENT: LazyLock<LexMatcher> =
    LazyLock::new(|| LexMatcher::emitted("delimiter_argument", Token::client_text_token));
/// The file name in `SOURCE file.sql`, as the client reads it.
static SOURCE_FILE_NAME: LazyLock<LexMatcher> =
    LazyLock::new(|| LexMatcher::emitted("source_file_name", Token::client_text_token));
/// Text on a command's line that the client reads past without using.
static CLIENT_COMMAND_IGNORED: LazyLock<LexMatcher> =
    LazyLock::new(|| LexMatcher::emitted("client_command_ignored", Token::client_text_token));
/// Command text the client doesn't read the way it looks. No grammar accepts
/// it, so it is reported as a parse error.
static CLIENT_COMMAND_MISREAD: LazyLock<LexMatcher> =
    LazyLock::new(|| LexMatcher::emitted("client_command_misread", Token::client_text_token));

// Standard matcher names, which every dialect has.
const WORD: &str = "word";
const WHITESPACE: &str = "whitespace";
const NEWLINE: &str = "newline";
const INLINE_COMMENT: &str = "inline_comment";
const BLOCK_COMMENT: &str = "block_comment";

/// What the client's `my_isspace` accepts within a line.
const SPACE: &[char] = &[' ', '\t', '\u{b}', '\u{c}', '\r'];

/// A long-form command name at the start of a line.
struct CommandWord<'t> {
    command: &'static ClientCommand,
    /// The name as written.
    word: &'t str,
}

/// A command argument: its text as written, and the value the client reads.
struct Argument<'t> {
    raw: &'t str,
    value: String,
}

/// Where a text next appears in the script, found again once lexing passes
/// it.
///
/// Each search runs on from the last place found, so the whole script is
/// searched about once.
struct NextPlace {
    needle: String,
    at: usize,
}

impl NextPlace {
    fn new(needle: &str) -> Self {
        Self {
            needle: needle.to_string(),
            at: 0,
        }
    }

    /// The first place after `pos` where the text appears, or the end of
    /// `text`.
    fn after(&mut self, text: &str, pos: usize) -> usize {
        if self.at <= pos {
            let from = pos + text[pos..].chars().next().map_or(0, char::len_utf8);
            self.at = text[from..]
                .find(self.needle.as_str())
                .map_or(text.len(), |index| from + index);
        }
        self.at
    }
}

/// Lexes a script with the state of the client that runs it.
///
/// The state is the active delimiter, whether the client is at the start of a
/// statement (nothing but whitespace and comments since the last delimiter),
/// and whether it is at the start of a line. Commands are lexed here. All
/// other text is lexed by the dialect's matchers, from the text the server
/// gets: the statement ends where the client finds the delimiter or a short
/// command.
pub(super) struct ClientScriptScanner<'a> {
    rules: &'static ClientCommandRules,
    lexer: &'a Lexer,
    word_matcher: &'a LexMatcher,
    whitespace_matcher: &'a LexMatcher,
    inline_comment_matcher: &'a LexMatcher,
    text: &'a str,
    pos: usize,
    elements: Vec<LexedElement<'a>>,
    delimiter: String,
    delimiter_place: NextPlace,
    shorthand_places: Vec<NextPlace>,
    statement_start: bool,
    line_start: bool,
}

impl<'a> ClientScriptScanner<'a> {
    pub(super) fn new(lexer: &'a Lexer, rules: &'static ClientCommandRules, text: &'a str) -> Self {
        let matcher = |name: &str| {
            lexer
                .matchers
                .iter()
                .find(|matcher| matcher.name == name)
                .unwrap_or_else(|| panic!("Client command lexing needs a `{name}` matcher."))
        };
        Self {
            rules,
            lexer,
            word_matcher: matcher(WORD),
            whitespace_matcher: matcher(WHITESPACE),
            inline_comment_matcher: matcher(INLINE_COMMENT),
            text,
            pos: 0,
            elements: Vec::with_capacity(text.len()),
            delimiter: rules.default_delimiter.to_string(),
            delimiter_place: NextPlace::new(rules.default_delimiter),
            shorthand_places: rules
                .commands
                .iter()
                .filter_map(|command| command.shorthand)
                .map(NextPlace::new)
                .collect(),
            statement_start: true,
            line_start: true,
        }
    }

    /// Lex the whole text into elements.
    pub(super) fn lex(mut self) -> Vec<LexedElement<'a>> {
        while self.pos < self.text.len() {
            if self.statement_start && self.line_start && self.line_command() {
                continue;
            }
            if self.active_delimiter() {
                continue;
            }
            if self.shorthand_command() {
                continue;
            }
            if self.statement_start && self.statement_command() {
                continue;
            }
            if self.statement_start && self.statement_start_comment() {
                continue;
            }
            self.ordinary_token();
        }
        self.elements
    }

    /// A long-form command at the start of a line, which takes the line.
    ///
    /// `DELIMITER` is taken whatever else is on the line. Other commands are
    /// taken here only if the line holds neither the delimiter nor `\g`.
    /// Otherwise the client collects them as a statement first (see
    /// [`Self::statement_command`]).
    fn line_command(&mut self) -> bool {
        let line = self.rest_of_line();
        let Some(CommandWord { command, word }) = self.long_command(line) else {
            return false;
        };
        let argument = &line[word.len()..];
        match command.effect {
            CommandEffect::SetDelimiter => {
                self.emit(word, self.word_matcher);
                let rest = self.delimiter_argument(argument);
                self.emit_ignored(rest);
            }
            CommandEffect::ReadFile => {
                if line.contains(self.delimiter.as_str()) || line.contains("\\g") {
                    return false;
                }
                self.emit(word, self.word_matcher);
                self.file_name(argument);
            }
            CommandEffect::EndStatement => return false,
        }
        // The command took its line, and added nothing to the statement the
        // client is collecting.
        self.statement_start = true;
        true
    }

    /// `SOURCE` that the client collects as a statement before reading it.
    ///
    /// That happens when its line holds the delimiter or `\g`, or when it
    /// follows a delimiter earlier on the line. The statement runs to the
    /// delimiter, and any backslash in it runs as a client command first.
    fn statement_command(&mut self) -> bool {
        let line = self.rest_of_line();
        let Some(CommandWord { command, word }) = self.long_command(line) else {
            return false;
        };
        if command.effect != CommandEffect::ReadFile {
            return false;
        }
        self.emit(word, self.word_matcher);
        let argument = &line[word.len()..];
        match argument.find(self.delimiter.as_str()) {
            Some(end) if !argument[..end].contains('\\') => self.file_name(&argument[..end]),
            // A backslash in the statement ran as a command: the client
            // doesn't open the file this names.
            Some(end) => self.emit_misread(&argument[..end]),
            // The statement runs on past this line.
            None => self.emit_misread(argument),
        }
        true
    }

    /// A short-form command, which counts anywhere outside comments and strings.
    fn shorthand_command(&mut self) -> bool {
        let Some(command) = self.rules.command_starting(&self.text[self.pos..]) else {
            return false;
        };
        let Some(shorthand) = command.shorthand else {
            return false;
        };
        let line = self.rest_of_line();
        self.emit(shorthand, &CLIENT_COMMAND_SHORTHAND);
        let argument = &line[shorthand.len()..];

        let mut statement_start = self.statement_start;
        match command.effect {
            CommandEffect::EndStatement => statement_start = true,
            CommandEffect::SetDelimiter => self.shorthand_delimiter_argument(argument),
            // `\.` reads the rest of its line as the file name, delimiter and
            // all.
            CommandEffect::ReadFile => self.file_name(argument),
        }
        // Other than `\g` and `\G`, the command adds nothing to the statement
        // the client is collecting, so leaves it where it was.
        self.statement_start = statement_start;
        true
    }

    /// The active delimiter, which ends the statement.
    fn active_delimiter(&mut self) -> bool {
        if !self.text[self.pos..].starts_with(self.delimiter.as_str()) {
            return false;
        }
        if self.delimiter == self.rules.default_delimiter {
            // The default delimiter keeps the dialect's own token for it.
            self.ordinary_token();
        } else {
            let delimiter = &self.text[self.pos..self.pos + self.delimiter.len()];
            self.emit(delimiter, &CLIENT_DELIMITER);
        }
        self.statement_start = true;
        true
    }

    /// `--` with no whitespace after it, where the client takes it as a comment.
    fn statement_start_comment(&mut self) -> bool {
        if !self.rules.dash_dash_comment_at_statement_start {
            return false;
        }
        let rest = &self.text[self.pos..];
        if !rest.starts_with("--") {
            return false;
        }
        // Up to the newline, as the comment matcher's `[^\n]*` would take it.
        let end = rest.find('\n').unwrap_or(rest.len());
        self.emit(&rest[..end], self.inline_comment_matcher);
        true
    }

    /// One token, lexed by the dialect's matchers.
    ///
    /// The client looks for the delimiter and short commands everywhere but
    /// in the tokens it scans through (strings and comments). Any other
    /// token is lexed again from the text the server gets, which ends at the
    /// next one of those. So `1.go` with `go` active is `1.`, and `--$$`
    /// with `$$` active is a comment, as `--` at the end of the server's
    /// input is.
    fn ordinary_token(&mut self) {
        let rest = &self.text[self.pos..];
        let mut elements = self.match_text(rest);
        if !self.rules.is_opaque(&elements[0].matcher.name) {
            let end = self.statement_end() - self.pos;
            if end < rest.len() {
                elements = self.match_text(&rest[..end]);
            }
        }
        for element in elements {
            self.emit(element.raw, element.matcher);
        }
    }

    fn match_text(&self, text: &'a str) -> Vec<LexedElement<'a>> {
        let Some((elements, _)) = self
            .lexer
            .lex_match(text)
            .or_else(|| self.lexer.last_resort_lexer.scan_match(text))
        else {
            panic!("Fatal. Unable to lex characters: {text}");
        };
        elements
    }

    /// Where the client next finds the delimiter or a short command, after
    /// here.
    fn statement_end(&mut self) -> usize {
        let delimiter_end = self.delimiter_place.after(self.text, self.pos);
        self.shorthand_places
            .iter_mut()
            .map(|place| place.after(self.text, self.pos))
            .fold(delimiter_end, usize::min)
    }

    /// Lex the argument of `DELIMITER` and set the delimiter from it.
    ///
    /// This follows the client's `get_arg`: whitespace, then either a word
    /// ending at the next space, in which a backslash escapes the next
    /// character, or a word in quotes, with no escapes. An empty argument, or
    /// one with a backslash left in it, is refused and the delimiter kept.
    /// Returns the text after the argument.
    fn delimiter_argument(&mut self, argument: &'a str) -> &'a str {
        let trimmed = argument.trim_start_matches(SPACE);
        self.emit(
            &argument[..argument.len() - trimmed.len()],
            self.whitespace_matcher,
        );
        if trimmed.is_empty() {
            return "";
        }

        let argument = parse_argument(trimmed);
        match self.accepted_delimiter(&argument.value) {
            Some(delimiter) => {
                self.emit(argument.raw, &DELIMITER_ARGUMENT);
                self.delimiter_place = NextPlace::new(&delimiter);
                self.delimiter = delimiter;
            }
            None => self.emit(argument.raw, &CLIENT_COMMAND_MISREAD),
        }
        &trimmed[argument.raw.len()..]
    }

    /// Lex the argument of `\d`.
    ///
    /// Once the delimiter is set, the client skips everything after `\d` up to
    /// and including the first copy of the (new) delimiter, or to the end of
    /// the line, and goes on lexing from there.
    fn shorthand_delimiter_argument(&mut self, argument: &'a str) {
        let new_delimiter =
            self.accepted_delimiter(&parse_argument(argument.trim_start_matches(SPACE)).value);
        let skip_end = argument.find(new_delimiter.as_deref().unwrap_or(&self.delimiter));
        let rest = self.delimiter_argument(argument);
        let argument_end = argument.len() - rest.len();
        let Some(skip_end) = skip_end else {
            self.emit_ignored(rest);
            return;
        };
        let skip_end = skip_end + self.delimiter.len();
        if skip_end < argument_end {
            // The client goes on lexing from inside the argument (a quoted
            // delimiter). Nothing sensible follows, so the remainder of the
            // line is misread.
            self.emit_misread(rest);
            return;
        }
        self.emit_ignored(&rest[..skip_end - argument_end]);
    }

    /// The delimiter the client sets from an argument's value, or `None` if
    /// it refuses the value: empty, or with a backslash left in it.
    fn accepted_delimiter(&self, value: &str) -> Option<String> {
        if value.is_empty() || value.contains('\\') {
            return None;
        }
        Some(cut_to_bytes(value, self.rules.max_delimiter_bytes).to_string())
    }

    /// Lex the argument of `SOURCE` or `\.`, as the client's `com_source`.
    ///
    /// A space must follow the command. The file name is the rest, from the
    /// first character that isn't whitespace, with trailing whitespace and
    /// control characters dropped.
    fn file_name(&mut self, argument: &'a str) {
        if !argument.starts_with(' ') {
            self.emit_misread(argument);
            return;
        }
        let trimmed = argument.trim_start_matches(SPACE);
        let gap = argument.len() - trimmed.len();
        self.emit(&argument[..gap], self.whitespace_matcher);
        let name = trimmed.trim_end_matches(|c: char| SPACE.contains(&c) || c < '\u{20}');
        self.emit(name, &SOURCE_FILE_NAME);
        self.emit_ignored(&trimmed[name.len()..]);
    }

    /// The long-form command that starts `line`.
    ///
    /// The name must be followed by whitespace or the end of the line.
    fn long_command(&self, line: &'a str) -> Option<CommandWord<'a>> {
        let length = line
            .find(|c: char| !c.is_ascii_alphabetic())
            .unwrap_or(line.len());
        if length == 0 || !matches!(line[length..].chars().next(), None | Some(' ' | '\t')) {
            return None;
        }
        let word = &line[..length];
        let command = self.rules.command_named(word)?;
        Some(CommandWord { command, word })
    }

    /// Add an element and update the client's state for it.
    fn emit(&mut self, raw: &'a str, matcher: &'a LexMatcher) {
        if raw.is_empty() {
            return;
        }
        self.elements.push(LexedElement::new(raw, matcher));
        self.pos += raw.len();
        match matcher.name.as_str() {
            NEWLINE => self.line_start = true,
            BLOCK_COMMENT => {
                if !self.rules.command_after_block_comment {
                    self.line_start = false;
                }
            }
            WHITESPACE | INLINE_COMMENT => {}
            _ => {
                self.statement_start = false;
                self.line_start = false;
            }
        }
    }

    /// Text the client reads past, between any whitespace around it.
    fn emit_ignored(&mut self, text: &'a str) {
        let content = text.trim_matches(SPACE);
        if content.is_empty() {
            self.emit(text, self.whitespace_matcher);
            return;
        }
        let start = text.len() - text.trim_start_matches(SPACE).len();
        self.emit(&text[..start], self.whitespace_matcher);
        self.emit(content, &CLIENT_COMMAND_IGNORED);
        self.emit(&text[start + content.len()..], self.whitespace_matcher);
    }

    /// Text the client misreads, after any whitespace before it.
    fn emit_misread(&mut self, text: &'a str) {
        let trimmed = text.trim_start_matches(SPACE);
        self.emit(&text[..text.len() - trimmed.len()], self.whitespace_matcher);
        self.emit(trimmed, &CLIENT_COMMAND_MISREAD);
    }

    /// The text from here to the end of the line, without the line break.
    fn rest_of_line(&self) -> &'a str {
        let rest = &self.text[self.pos..];
        let line = rest.find('\n').map_or(rest, |end| &rest[..end]);
        line.strip_suffix('\r').unwrap_or(line)
    }
}

/// The command argument that starts `text`, as the client's `get_arg` reads it.
///
/// A quoted argument runs to the matching quote, or the end of the text, with
/// no escapes. An unquoted one ends at a space, and a backslash in it escapes
/// the character after it, which is kept in the value without the backslash,
/// so `a\ b` is one argument. A backslash at the very end stays in the value.
fn parse_argument(text: &str) -> Argument<'_> {
    if let Some(quote @ ('\'' | '"' | '`')) = text.chars().next() {
        let inner = &text[1..];
        return match inner.find(quote) {
            Some(close) => Argument {
                raw: &text[..close + 2],
                value: inner[..close].to_string(),
            },
            None => Argument {
                raw: text,
                value: inner.to_string(),
            },
        };
    }

    let mut value = String::new();
    let mut chars = text.char_indices().peekable();
    let mut end = text.len();
    while let Some((index, c)) = chars.next() {
        match c {
            ' ' => {
                end = index;
                break;
            }
            '\\' if chars.peek().is_some() => {
                let (_, escaped) = chars.next().expect("peeked");
                value.push(escaped);
            }
            _ => value.push(c),
        }
    }
    Argument {
        raw: &text[..end],
        value,
    }
}

/// `value` cut to `limit` bytes, at a character boundary.
///
/// The client cuts at the byte limit even inside a multi-byte character. A
/// delimiter ending in part of a character can't match text made of whole
/// characters, so the boundary before that character is the nearest
/// equivalent.
fn cut_to_bytes(value: &str, limit: usize) -> &str {
    if value.len() <= limit {
        return value;
    }
    let mut end = limit;
    while !value.is_char_boundary(end) {
        end -= 1;
    }
    &value[..end]
}
