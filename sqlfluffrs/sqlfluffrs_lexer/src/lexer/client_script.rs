//! Lexing scripts that are run through a command-line client.
//!
//! A command-line client reads a script line by line, splits it into
//! statements itself and handles some of the text before anything reaches the
//! server: commands that change the statement delimiter, commands that take
//! raw text arguments, and comment forms that depend on where they appear.
//! [`ClientScriptLexer`] lexes with the same state the client keeps, as
//! described by a dialect's [`ClientCommandRules`]. Nothing here is specific to
//! one client except what the rules say.
//!
//! This is the same lexer as `sqlfluff.core.parser.client_commands` in
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
    LazyLock::new(|| LexMatcher::emitted(CLIENT_COMMAND_SHORTHAND_NAME, Token::code_token));
/// The new delimiter in `DELIMITER $$`, as written.
static DELIMITER_ARGUMENT: LazyLock<LexMatcher> =
    LazyLock::new(|| LexMatcher::emitted(DELIMITER_ARGUMENT_NAME, Token::client_text_token));
/// The file name in `SOURCE file.sql`, as the client reads it.
static SOURCE_FILE_NAME: LazyLock<LexMatcher> =
    LazyLock::new(|| LexMatcher::emitted(SOURCE_FILE_NAME_NAME, Token::client_text_token));
/// Text on a command's line that the client reads past without using.
static CLIENT_COMMAND_IGNORED: LazyLock<LexMatcher> =
    LazyLock::new(|| LexMatcher::emitted(CLIENT_COMMAND_IGNORED_NAME, Token::client_text_token));
/// Command text the client doesn't read the way it looks. No grammar accepts
/// it, so it is reported as a parse error.
static CLIENT_COMMAND_MISREAD: LazyLock<LexMatcher> =
    LazyLock::new(|| LexMatcher::emitted("client_command_misread", Token::client_text_token));

// Tokens the client reads itself, which add nothing to the statement it is
// collecting: a command at the start of a statement leaves it at the start.
const CLIENT_COMMAND_SHORTHAND_NAME: &str = "client_command_shorthand";
const DELIMITER_ARGUMENT_NAME: &str = "delimiter_argument";
const SOURCE_FILE_NAME_NAME: &str = "source_file_name";
const CLIENT_COMMAND_IGNORED_NAME: &str = "client_command_ignored";

// Standard matcher names, which every dialect has.
const WORD: &str = "word";
const WHITESPACE: &str = "whitespace";
const NEWLINE: &str = "newline";
const INLINE_COMMENT: &str = "inline_comment";
const BLOCK_COMMENT: &str = "block_comment";

/// What the client's `my_isspace` accepts within a line.
const SPACE: &[char] = &[' ', '\t', '\u{b}', '\u{c}', '\r'];

/// A command, and its name or short form as written.
#[derive(Clone, Copy)]
struct CommandWord<'a> {
    command: &'static ClientCommand,
    word: &'a str,
}

/// What comes next in the script, as the client reads it.
enum Next<'a> {
    /// A command that sets the delimiter (`DELIMITER`), at the start of a
    /// line. It takes the line.
    DelimiterCommand(CommandWord<'a>),
    /// A command that reads a file (`SOURCE`), at the start of a line that
    /// holds neither the delimiter nor `\g`. The rest of the line is the file
    /// name.
    SourceLine(CommandWord<'a>),
    /// A command that reads a file, which the client collects as a statement
    /// before reading it.
    SourceStatement(CommandWord<'a>),
    /// The short form of a command, such as `\d`, `\.` or `\g`.
    Shorthand(CommandWord<'a>),
    /// The active delimiter, which ends the statement.
    ActiveDelimiter,
    /// `--` with no whitespace after it, at the start of a statement, where
    /// the client takes it as a comment.
    StatementStartComment,
    /// Anything else, for the dialect's matchers.
    Token,
}

/// A command argument: its text as written, and the value the client reads.
struct Argument<'a> {
    raw: &'a str,
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
pub(super) struct ClientScriptLexer<'a> {
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

impl<'a> ClientScriptLexer<'a> {
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
            match self.peek() {
                Next::DelimiterCommand(found) => self.lex_delimiter_command(found),
                Next::SourceLine(found) => self.lex_source_line(found),
                Next::SourceStatement(found) => self.lex_source_statement(found),
                Next::Shorthand(found) => self.lex_shorthand(found),
                Next::ActiveDelimiter => self.lex_active_delimiter(),
                Next::StatementStartComment => self.lex_statement_start_comment(),
                Next::Token => self.lex_token(),
            }
        }
        self.elements
    }

    /// What comes next, checked in the order the client checks.
    ///
    /// Long-form commands count only at the start of a statement, and take
    /// their line unless the client collects it as a statement first (see
    /// [`Self::line_is_collected`]). Short forms count anywhere outside
    /// comments and strings.
    fn peek(&self) -> Next<'a> {
        let long = if self.statement_start {
            self.long_command(self.rest_of_line())
        } else {
            None
        };
        if let Some(found) = long.filter(|found| self.line_start && !self.line_is_collected(found))
        {
            match found.command.effect {
                CommandEffect::SetDelimiter => return Next::DelimiterCommand(found),
                CommandEffect::ReadFile => return Next::SourceLine(found),
                // `ClientCommandRules` refuses a long form that ends a statement.
                CommandEffect::EndStatement => {}
            }
        }
        if self.text[self.pos..].starts_with(self.delimiter.as_str()) {
            return Next::ActiveDelimiter;
        }
        let shorthand = self
            .rules
            .command_starting(&self.text[self.pos..])
            .and_then(|command| command.shorthand.map(|word| CommandWord { command, word }));
        if let Some(found) = shorthand {
            return Next::Shorthand(found);
        }
        if let Some(found) = long.filter(|found| found.command.effect == CommandEffect::ReadFile) {
            return Next::SourceStatement(found);
        }
        if self.statement_start
            && self.rules.dash_dash_comment_at_statement_start
            && self.text[self.pos..].starts_with("--")
        {
            return Next::StatementStartComment;
        }
        Next::Token
    }

    /// Whether the client collects this line as a statement, not as `found`.
    ///
    /// As the client's `find_command`, it does when the line holds the
    /// collected-line marker, or holds the delimiter and `found` doesn't set
    /// the delimiter (`DELIMITER ;` holds the delimiter it replaces).
    fn line_is_collected(&self, found: &CommandWord<'a>) -> bool {
        let line = self.rest_of_line();
        if self
            .rules
            .collected_line_marker
            .is_some_and(|marker| line.contains(marker))
        {
            return true;
        }
        let sets_delimiter = found.command.effect == CommandEffect::SetDelimiter;
        !sets_delimiter && line.contains(self.delimiter.as_str())
    }

    /// `DELIMITER` and its argument. The rest of the line is ignored.
    fn lex_delimiter_command(&mut self, found: CommandWord<'a>) {
        let argument = &self.rest_of_line()[found.word.len()..];
        self.emit(found.word, self.word_matcher);
        let rest = self.delimiter_argument(argument);
        self.emit_ignored(rest);
        // The command took its line, and added nothing to the statement the
        // client is collecting.
        self.statement_start = true;
    }

    /// `SOURCE` and the file name that is the rest of its line.
    fn lex_source_line(&mut self, found: CommandWord<'a>) {
        let argument = &self.rest_of_line()[found.word.len()..];
        self.emit(found.word, self.word_matcher);
        self.file_name(argument);
        // The command took its line, and added nothing to the statement the
        // client is collecting.
        self.statement_start = true;
    }

    /// `SOURCE` that the client collects as a statement before reading it.
    ///
    /// That happens when its line holds the delimiter or `\g`, or when it
    /// follows a delimiter earlier on the line. The statement runs to the
    /// delimiter. A short command in it runs as the client reaches it, so it
    /// is lexed as a command after the text before it: `SOURCE a.sql \g`
    /// sends `SOURCE a.sql` to the server, and the statement ends there.
    fn lex_source_statement(&mut self, found: CommandWord<'a>) {
        let argument = &self.rest_of_line()[found.word.len()..];
        self.emit(found.word, self.word_matcher);
        match self.first_break(argument) {
            // The statement runs on past this line, so the client doesn't
            // open the file this names.
            None => self.emit_misread(argument),
            Some(end)
                if argument[end..].starts_with(self.delimiter.as_str())
                    && !argument[..end].contains('\\') =>
            {
                self.file_name(&argument[..end]);
            }
            // A short command comes first, or a backslash before the
            // delimiter ran as a command: the client doesn't open the file
            // this names.
            Some(end) => self.emit_misread(&argument[..end]),
        }
    }

    /// A short-form command and its argument.
    fn lex_shorthand(&mut self, found: CommandWord<'a>) {
        let argument = &self.rest_of_line()[found.word.len()..];
        self.emit(found.word, &CLIENT_COMMAND_SHORTHAND);
        match found.command.effect {
            CommandEffect::EndStatement => self.statement_start = true,
            CommandEffect::SetDelimiter => self.shorthand_delimiter_argument(argument),
            // `\.` reads the rest of its line as the file name, delimiter and
            // all.
            CommandEffect::ReadFile => self.file_name(argument),
        }
    }

    /// The active delimiter, which ends the statement.
    fn lex_active_delimiter(&mut self) {
        if self.delimiter == self.rules.default_delimiter {
            // The default delimiter keeps the dialect's own token for it.
            self.lex_token();
        } else {
            let delimiter = &self.text[self.pos..self.pos + self.delimiter.len()];
            self.emit(delimiter, &CLIENT_DELIMITER);
        }
        self.statement_start = true;
    }

    /// `--` with no whitespace after it, as a comment.
    fn lex_statement_start_comment(&mut self) {
        // Up to the newline, as the comment matcher's `[^\n]*` would take it.
        let rest = &self.text[self.pos..];
        let end = rest.find('\n').unwrap_or(rest.len());
        self.emit(&rest[..end], self.inline_comment_matcher);
    }

    /// One token, lexed by the dialect's matchers.
    ///
    /// The client looks for the delimiter and short commands everywhere but
    /// in the tokens it scans through (strings and comments). Any other
    /// token is lexed again from the text the server gets, which ends at the
    /// next one of those. So `1.go` with `go` active is `1.`, and `--$$`
    /// with `$$` active is a comment, as `--` at the end of the server's
    /// input is.
    fn lex_token(&mut self) {
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
                if !self.rules.line_command_after_block_comment {
                    self.line_start = false;
                }
            }
            WHITESPACE | INLINE_COMMENT => {}
            CLIENT_COMMAND_SHORTHAND_NAME
            | DELIMITER_ARGUMENT_NAME
            | SOURCE_FILE_NAME_NAME
            | CLIENT_COMMAND_IGNORED_NAME => self.line_start = false,
            // The client adds this to the statement it is collecting.
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

    /// Text the client misreads, between any whitespace around it.
    fn emit_misread(&mut self, text: &'a str) {
        let content = text.trim_matches(SPACE);
        if content.is_empty() {
            self.emit(text, self.whitespace_matcher);
            return;
        }
        let start = text.len() - text.trim_start_matches(SPACE).len();
        self.emit(&text[..start], self.whitespace_matcher);
        self.emit(content, &CLIENT_COMMAND_MISREAD);
        self.emit(&text[start + content.len()..], self.whitespace_matcher);
    }

    /// Where the client finds the delimiter or a short command in `text`.
    fn first_break(&self, text: &str) -> Option<usize> {
        let shorthands = self
            .rules
            .commands
            .iter()
            .filter_map(|command| command.shorthand);
        std::iter::once(self.delimiter.as_str())
            .chain(shorthands)
            .filter_map(|needle| text.find(needle))
            .min()
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
