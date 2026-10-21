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
    BufferAction, ClientCommandRules, CommandArgument, LongClientCommand, ShortClientCommand,
    Token,
};

use super::Lexer;

/// The active delimiter, when it isn't the default one.
static CLIENT_DELIMITER: LazyLock<LexMatcher> =
    LazyLock::new(|| LexMatcher::emitted("client_delimiter", Token::client_text_token));
/// A short command, such as `\d`, `\.` or `\g`.
static CLIENT_SHORT_COMMAND: LazyLock<LexMatcher> =
    LazyLock::new(|| LexMatcher::emitted("client_short_command", Token::code_token));
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

/// Matchers whose tokens are non-code: whitespace, newlines and comments.
/// They don't change the statement the client is collecting.
const NON_CODE_MATCHERS: &[&str] = &[WHITESPACE, NEWLINE, INLINE_COMMENT, BLOCK_COMMENT];

/// What the client's `my_isspace` accepts within a line.
const SPACE: &[char] = &[' ', '\t', '\u{b}', '\u{c}', '\r'];

/// A long command, and its name as written.
#[derive(Clone, Copy)]
struct CommandWord<'a> {
    command: &'static LongClientCommand,
    word: &'a str,
}

/// What a piece of text does to the statement the client is collecting.
#[derive(Clone, Copy, PartialEq, Eq)]
enum Buffer {
    /// It goes into the statement: SQL.
    Append,
    /// The statement stays as it is: whitespace, comments, and the client
    /// commands the client takes out and runs.
    Keep,
    /// The statement is sent and a new one starts: the delimiter, `\g`.
    End,
    /// The statement is thrown away and a new one starts: `\.`.
    Discard,
}

impl From<BufferAction> for Buffer {
    fn from(action: BufferAction) -> Self {
        match action {
            BufferAction::Keep => Buffer::Keep,
            BufferAction::End => Buffer::End,
            BufferAction::Discard => Buffer::Discard,
        }
    }
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
    /// A short command, such as `\d`, `\.` or `\g`.
    ShortCommand(&'static ShortClientCommand),
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
    /// `None` for a quote with no closing quote, which is refused.
    value: Option<String>,
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
    short_command_places: Vec<NextPlace>,
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
            short_command_places: rules
                .short_commands
                .iter()
                .map(|command| NextPlace::new(command.text))
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
                Next::ShortCommand(command) => self.lex_short_command(command),
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
    /// [`Self::line_is_collected`]). Short commands count anywhere outside
    /// comments and strings.
    fn peek(&self) -> Next<'a> {
        let long = if self.statement_start {
            self.long_command(self.rest_of_line())
        } else {
            None
        };
        if let Some(found) = long.filter(|found| self.line_start && !self.line_is_collected(found))
        {
            return match found.command.argument {
                CommandArgument::Delimiter => Next::DelimiterCommand(found),
                CommandArgument::FileName => Next::SourceLine(found),
            };
        }
        if self.text[self.pos..].starts_with(self.delimiter.as_str()) {
            return Next::ActiveDelimiter;
        }
        if let Some(command) = self.rules.command_starting(&self.text[self.pos..]) {
            return Next::ShortCommand(command);
        }
        if let Some(found) =
            long.filter(|found| found.command.argument == CommandArgument::FileName)
        {
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
        let sets_delimiter = found.command.argument == CommandArgument::Delimiter;
        !sets_delimiter && line.contains(self.delimiter.as_str())
    }

    /// `DELIMITER` and its argument. The rest of the line is ignored.
    fn lex_delimiter_command(&mut self, found: CommandWord<'a>) {
        let argument = &self.rest_of_line()[found.word.len()..];
        self.emit(found.word, self.word_matcher, Buffer::Keep);
        let rest = self.delimiter_argument(argument);
        self.emit_ignored(rest);
    }

    /// `SOURCE` and the file name that is the rest of its line.
    fn lex_source_line(&mut self, found: CommandWord<'a>) {
        let argument = &self.rest_of_line()[found.word.len()..];
        self.emit(found.word, self.word_matcher, Buffer::Keep);
        self.file_name(argument, Buffer::Keep);
    }

    /// `SOURCE` that the client collects as a statement before reading it.
    ///
    /// That happens when its line holds the delimiter or `\g`, or when it
    /// follows a delimiter earlier on the line. The client then treats it
    /// almost like SQL, with results that are probably client bugs:
    /// - `SOURCE a.sql;` still runs the file: at the delimiter the client sees
    ///   the statement starts with `SOURCE` and runs it.
    /// - `SOURCE a.sql \g` sends `SOURCE a.sql` to the server as SQL, which
    ///   fails: `\g` sends the statement without that check.
    fn lex_source_statement(&mut self, found: CommandWord<'a>) {
        let argument = &self.rest_of_line()[found.word.len()..];
        self.emit(found.word, self.word_matcher, Buffer::Append);
        match self.first_break(argument) {
            // The statement runs on past this line, so the client doesn't
            // open the file this names.
            None => self.emit_misread(argument, Buffer::Append),
            Some(end)
                if argument[end..].starts_with(self.delimiter.as_str())
                    && !argument[..end].contains('\\') =>
            {
                self.file_name(&argument[..end], Buffer::Append);
            }
            // A short command comes first, or a backslash before the
            // delimiter ran as a command: the client doesn't open the file
            // this names.
            Some(end) => self.emit_misread(&argument[..end], Buffer::Append),
        }
    }

    /// A short command and its argument.
    fn lex_short_command(&mut self, command: &'static ShortClientCommand) {
        let argument = &self.rest_of_line()[command.text.len()..];
        self.emit(
            command.text,
            &CLIENT_SHORT_COMMAND,
            Buffer::from(command.buffer_action),
        );
        match command.argument {
            Some(CommandArgument::Delimiter) => self.short_command_delimiter_argument(argument),
            // `\.` reads the rest of its line as the file name, delimiter and
            // all.
            Some(CommandArgument::FileName) => self.file_name(argument, Buffer::Keep),
            None => {}
        }
    }

    /// The active delimiter, which ends the statement.
    fn lex_active_delimiter(&mut self) {
        let delimiter = &self.text[self.pos..self.pos + self.delimiter.len()];
        if self.delimiter == self.rules.default_delimiter {
            // The default delimiter keeps the dialect's own token for it.
            for element in self.match_text(delimiter) {
                self.emit(element.raw, element.matcher, Buffer::End);
            }
        } else {
            self.emit(delimiter, &CLIENT_DELIMITER, Buffer::End);
        }
    }

    /// `--` with no whitespace after it, as a comment.
    fn lex_statement_start_comment(&mut self) {
        // Up to the newline, as the comment matcher's `[^\n]*` would take it.
        let rest = &self.text[self.pos..];
        let end = rest.find('\n').unwrap_or(rest.len());
        self.emit(&rest[..end], self.inline_comment_matcher, Buffer::Keep);
    }

    /// One token, lexed by the dialect's matchers.
    ///
    /// The client cuts the statement at the delimiter or a short command before
    /// the server sees it, so a token that isn't a string or comment is lexed
    /// again from the text up to there. With `go` as the delimiter, `1.go` is the
    /// number `1.`. And, absurdly, with `$$` as the delimiter `--$$` is a
    /// comment: the client doesn't treat `--` without a space as a comment, but
    /// the server does at the end of a statement.
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
            let buffer = if NON_CODE_MATCHERS.contains(&element.matcher.name.as_str()) {
                Buffer::Keep
            } else {
                Buffer::Append
            };
            self.emit(element.raw, element.matcher, buffer);
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
        self.short_command_places
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
            Buffer::Keep,
        );
        if trimmed.is_empty() {
            return "";
        }

        let argument = parse_argument(trimmed);
        let delimiter = self.accepted_delimiter(argument.value.as_deref());
        self.set_delimiter(argument.raw, delimiter);
        &trimmed[argument.raw.len()..]
    }

    /// Emit an argument as written, and set the delimiter it gives.
    ///
    /// `None` if the client refused the argument: it is misread, and the
    /// delimiter kept.
    fn set_delimiter(&mut self, raw: &'a str, delimiter: Option<String>) {
        let Some(delimiter) = delimiter else {
            self.emit(raw, &CLIENT_COMMAND_MISREAD, Buffer::Keep);
            return;
        };
        self.emit(raw, &DELIMITER_ARGUMENT, Buffer::Keep);
        self.delimiter_place = NextPlace::new(&delimiter);
        self.delimiter = delimiter;
    }

    /// Lex the argument of `\d`.
    ///
    /// The mysql and mariadb clients handle this bizarrely, probably a client
    /// bug, but both do the same thing: after setting the delimiter, the client carries on
    /// reading right after the new delimiter's text on the line. Normally that's
    /// just after the argument: `\d $$ SELECT 1 $$` runs `SELECT 1`. But when
    /// the argument as typed isn't exactly the delimiter, ridiculous stuff
    /// happens:
    /// - `\d '$$'` sets `$$` and carries on inside the quotes, so the closing
    ///   quote is read as SQL.
    /// - An argument over 15 bytes sets only its first 15 and carries on after
    ///   those, so the rest is read as SQL.
    /// - `\d a\ b` sets `a b`, which isn't on the line as typed, so it carries
    ///   on after the next `a b` on the line, or discards the rest of the line
    ///   if there's none.
    ///
    /// Text the client skips belongs to the command: the server never sees it,
    /// even if it looks like SQL. SQL before the `\d` stays in the statement.
    fn short_command_delimiter_argument(&mut self, argument: &'a str) {
        let trimmed = argument.trim_start_matches(SPACE);
        let gap = argument.len() - trimmed.len();
        let parsed = parse_argument(trimmed);
        let delimiter = self.accepted_delimiter(parsed.value.as_deref());
        let needle = delimiter.as_deref().unwrap_or(&self.delimiter);
        let resume = trimmed.find(needle).map(|found| gap + found + needle.len());
        let argument_end = gap + parsed.raw.len();
        if let Some(resume) = resume.filter(|&resume| resume < argument_end) {
            // The client goes on from inside the argument. The whole argument
            // still decides the delimiter, but only the text before that point
            // is the command's.
            self.emit(&argument[..gap], self.whitespace_matcher, Buffer::Keep);
            self.set_delimiter(&argument[gap..resume], delimiter);
            return;
        }
        let rest = self.delimiter_argument(argument);
        match resume {
            None => self.emit_ignored(rest),
            Some(resume) => self.emit_ignored(&rest[..resume - argument_end]),
        }
    }

    /// The delimiter the client sets from an argument's value.
    ///
    /// `None` if it refuses the value: empty, with a backslash left in it, or
    /// from a quote with no closing quote. The client checks these before it
    /// cuts the value to the byte limit. A delimiter that starts or ends with
    /// whitespace (from quotes or an escaped space, as in `\d \ x`, or from a
    /// cut that ends at a space) is refused too: the client takes it, but
    /// then splits statements at every such space, or only where the
    /// invisible space follows, so it is only ever a mistake. That is checked
    /// after the cut, on the delimiter the client would set.
    fn accepted_delimiter(&self, value: Option<&str>) -> Option<String> {
        let value = value?;
        if value.is_empty() || value.contains('\\') {
            return None;
        }
        let value = match self.rules.max_delimiter_bytes {
            Some(limit) => cut_to_bytes(value, limit),
            None => value,
        };
        if value.starts_with(SPACE) || value.ends_with(SPACE) {
            return None;
        }
        Some(value.to_string())
    }

    /// Lex the argument of `SOURCE` or `\.`, as the client's `com_source`.
    ///
    /// A space must follow the command. The file name is the rest, from the
    /// first character that isn't whitespace, with trailing whitespace and
    /// control characters dropped. `buffer` says what the name does to the
    /// statement: nothing on a command's own line, but a collected `SOURCE`
    /// is part of the statement until the delimiter.
    fn file_name(&mut self, argument: &'a str, buffer: Buffer) {
        if !argument.starts_with(' ') {
            self.emit_misread(argument, buffer);
            return;
        }
        let trimmed = argument.trim_start_matches(SPACE);
        let gap = argument.len() - trimmed.len();
        self.emit(&argument[..gap], self.whitespace_matcher, Buffer::Keep);
        let name = trimmed.trim_end_matches(|c: char| SPACE.contains(&c) || c < '\u{20}');
        self.emit(name, &SOURCE_FILE_NAME, buffer);
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
    fn emit(&mut self, raw: &'a str, matcher: &'a LexMatcher, buffer: Buffer) {
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
            _ => self.line_start = false,
        }
        match buffer {
            Buffer::Append => self.statement_start = false,
            Buffer::Keep => {}
            Buffer::End | Buffer::Discard => self.statement_start = true,
        }
    }

    /// Text the client reads past, between any whitespace around it.
    fn emit_ignored(&mut self, text: &'a str) {
        self.emit_between_spaces(text, &CLIENT_COMMAND_IGNORED, Buffer::Keep);
    }

    /// Text the client misreads, between any whitespace around it.
    ///
    /// `buffer` says whether the client puts it into the statement.
    fn emit_misread(&mut self, text: &'a str, buffer: Buffer) {
        self.emit_between_spaces(text, &CLIENT_COMMAND_MISREAD, buffer);
    }

    /// `text` as one `matcher` token, with any whitespace around it apart.
    fn emit_between_spaces(&mut self, text: &'a str, matcher: &'a LexMatcher, buffer: Buffer) {
        let content = text.trim_matches(SPACE);
        if content.is_empty() {
            self.emit(text, self.whitespace_matcher, Buffer::Keep);
            return;
        }
        let start = text.len() - text.trim_start_matches(SPACE).len();
        self.emit(&text[..start], self.whitespace_matcher, Buffer::Keep);
        self.emit(content, matcher, buffer);
        self.emit(
            &text[start + content.len()..],
            self.whitespace_matcher,
            Buffer::Keep,
        );
    }

    /// Where the client finds the delimiter or a short command in `text`.
    fn first_break(&self, text: &str) -> Option<usize> {
        let short_commands = self.rules.short_commands.iter().map(|command| command.text);
        std::iter::once(self.delimiter.as_str())
            .chain(short_commands)
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
/// A quoted argument runs to the matching quote, with no escapes. With no
/// closing quote it has no value: the mysql client reads to the end of the
/// line, but that only ever comes from a typo such as `DELIMITER '$$`, and the
/// mariadb client refuses it, so it is refused here. An unquoted argument ends
/// at a space, and a backslash in it escapes the character after it, which is
/// kept in the value without the backslash, so `a\ b` is one argument. A
/// backslash at the very end stays in the value.
fn parse_argument(text: &str) -> Argument<'_> {
    if let Some(quote @ ('\'' | '"' | '`')) = text.chars().next() {
        let inner = &text[1..];
        return match inner.find(quote) {
            Some(close) => Argument {
                raw: &text[..close + 2],
                value: Some(inner[..close].to_string()),
            },
            None => Argument {
                raw: text,
                value: None,
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
        value: Some(value),
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
