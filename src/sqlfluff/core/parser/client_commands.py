"""Lexing scripts that are run through a command-line client.

Some SQL is never sent to the server as written. A command-line client reads
the script line by line, splits it into statements itself and handles some of
the text before anything reaches the server: commands that change how the rest
of the script is split (the statement delimiter), commands that take raw text
arguments (a file to read), and comment forms that depend on where they
appear. Lexing such a script correctly needs the same state the client keeps.

`ClientCommandRules` describes a client, and `ClientScriptLexer` lexes with
that state. The MySQL/MariaDB rules live with those dialects. Nothing here is
specific to that client except what the rules say, so another client's
terminator command could reuse the lexer with rules of its own.

The Rust side has the same lexer (`sqlfluffrs_lexer::client_script`), and the
two must emit identical tokens.
"""

from dataclasses import dataclass
from enum import Enum
from typing import NamedTuple, Optional, Union

from sqlfluff.core.errors import SQLLexError
from sqlfluff.core.parser.lexer import LexedElement, LexerType, StringLexer
from sqlfluff.core.parser.segments import ClientTextSegment, CodeSegment, RawSegment


class CommandEffect(Enum):
    """What a client command does, which decides how its text is lexed."""

    SET_DELIMITER = "set_delimiter"
    """Changes the statement delimiter, e.g. `DELIMITER $$`."""

    READ_FILE = "read_file"
    """Runs another script, e.g. `SOURCE file.sql`."""

    END_STATEMENT = "end_statement"
    """Sends the statement so far, as the delimiter does, e.g. `\\g`."""


@dataclass(frozen=True)
class ClientCommand:
    """One row of a client's command table."""

    effect: CommandEffect
    name: Optional[str] = None
    """The long form in lower case, e.g. `delimiter`, matched in any case.

    It is a command only at the start of a statement. `None` for a command
    whose long form can't usefully appear in a script.
    """
    shorthand: Optional[str] = None
    """The short form, e.g. `\\d`, matched in its own case.

    It is a command anywhere outside strings and comments.
    """


@dataclass(frozen=True)
class ClientCommandRules:
    """How a command-line client splits a script into statements."""

    commands: tuple[ClientCommand, ...]
    opaque_token_names: frozenset[str]
    """Lexer matchers whose text the client doesn't scan: strings, quoted
    identifiers and comments. The delimiter isn't found inside these."""
    line_command_after_block_comment: bool
    """Whether a `/* ... */` comment may come before a long-form command that
    takes its line. A command the client collects as a statement may follow a
    comment either way."""
    dash_dash_comment_at_statement_start: bool
    """Whether `--` starts a comment at the start of a statement even with no
    whitespace after it. Elsewhere `--` needs whitespace or the end of the line
    after it, which is the dialect's comment matcher's job."""
    collected_line_marker: Optional[str]
    """A long-form command never takes a line that holds this text: the client
    collects the line as a statement instead. The mysql client's `find_command`
    checks for a lower-case `\\g`, so `\\G` doesn't count."""
    default_delimiter: str = ";"
    max_delimiter_bytes: int = 15
    """Longer delimiters are cut to this many bytes, as the client does."""

    def command_named(self, name: str) -> Optional[ClientCommand]:
        """The command whose long form is `name`, in any case."""
        lowered = name.lower()
        for command in self.commands:
            if command.name == lowered:
                return command
        return None

    def command_starting(self, text: str, pos: int = 0) -> Optional[ClientCommand]:
        """The command whose short form starts at `pos` in `text`."""
        for command in self.commands:
            if command.shorthand and text.startswith(command.shorthand, pos):
                return command
        return None


class EmittedToken(StringLexer):
    """A kind of token the client script lexer emits itself, not a matcher.

    It is never in a dialect's matcher list. It only gives that lexer's tokens
    their type and segment class.
    """

    def __init__(self, name: str, segment_class: type[RawSegment]) -> None:
        super().__init__(name, "", segment_class)

    def _match(self, forward_string: str) -> Optional[LexedElement]:
        raise NotImplementedError(f"{self!r} is emitted, never matched.")

    def search(self, forward_string: str) -> Optional[tuple[int, int]]:
        """Never called: emitted tokens are never searched for."""
        raise NotImplementedError(f"{self!r} is emitted, never searched for.")


CLIENT_DELIMITER = EmittedToken("client_delimiter", ClientTextSegment)
"""The active delimiter, when it isn't the default one."""
CLIENT_COMMAND_SHORTHAND = EmittedToken("client_command_shorthand", CodeSegment)
"""The short form of a command, such as `\\d`, `\\.` or `\\g`."""
DELIMITER_ARGUMENT = EmittedToken("delimiter_argument", ClientTextSegment)
"""The new delimiter in `DELIMITER $$`, as written."""
SOURCE_FILE_NAME = EmittedToken("source_file_name", ClientTextSegment)
"""The file name in `SOURCE file.sql`, as the client reads it."""
CLIENT_COMMAND_IGNORED = EmittedToken("client_command_ignored", ClientTextSegment)
"""Text on a command's line that the client reads past without using."""
CLIENT_COMMAND_MISREAD = EmittedToken("client_command_misread", ClientTextSegment)
"""Command text the client doesn't read the way it looks. No grammar accepts
it, so it is reported as a parse error."""

# Standard matcher names, which every dialect has.
_WORD = "word"
_WHITESPACE = "whitespace"
_NEWLINE = "newline"
_INLINE_COMMENT = "inline_comment"
_BLOCK_COMMENT = "block_comment"

# Tokens the client reads itself, which add nothing to the statement it is
# collecting: a command at the start of a statement leaves it at the start.
_CLIENT_READ_TOKEN_NAMES = frozenset(
    {
        CLIENT_COMMAND_SHORTHAND.name,
        DELIMITER_ARGUMENT.name,
        SOURCE_FILE_NAME.name,
        CLIENT_COMMAND_IGNORED.name,
    }
)

# What the client's `my_isspace` accepts within a line.
_SPACE = " \t\v\f\r"


class _CommandWord(NamedTuple):
    """A command, and its name or short form as written."""

    command: ClientCommand
    word: str


# What comes next in the script, as the client reads it: one of the classes
# below, as `_Next`.


class _DelimiterCommand(NamedTuple):
    """A command that sets the delimiter (`DELIMITER`), at the start of a line.

    It takes the line.
    """

    found: _CommandWord


class _SourceLine(NamedTuple):
    r"""A command that reads a file (`SOURCE`), at the start of a line.

    The line holds neither the delimiter nor `\g`. The rest of it is the file
    name.
    """

    found: _CommandWord


class _SourceStatement(NamedTuple):
    """A command that reads a file, which the client collects as a statement first."""

    found: _CommandWord


class _Shorthand(NamedTuple):
    r"""The short form of a command, such as `\d`, `\.` or `\g`."""

    found: _CommandWord


class _ActiveDelimiter(NamedTuple):
    """The active delimiter, which ends the statement."""


class _StatementStartComment(NamedTuple):
    """`--` with no whitespace after it, at the start of a statement.

    The client takes it as a comment.
    """


class _Token(NamedTuple):
    """Anything else, for the dialect's matchers."""


_Next = Union[
    _DelimiterCommand,
    _SourceLine,
    _SourceStatement,
    _Shorthand,
    _ActiveDelimiter,
    _StatementStartComment,
    _Token,
]


class _Argument(NamedTuple):
    """A command argument: its text as written, and the value the client reads."""

    raw: str
    value: str


class _NextPlace:
    """Where a text next appears in the script, found again once lexing passes it.

    Each search runs on from the last place found, so the whole script is
    searched about once.
    """

    def __init__(self, needle: str) -> None:
        self._needle = needle
        self._at = 0

    def after(self, text: str, pos: int) -> int:
        """The first place after `pos` where the text appears, or the end of `text`."""
        if self._at <= pos:
            found = text.find(self._needle, pos + 1)
            self._at = found if found >= 0 else len(text)
        return self._at


class ClientScriptLexer:
    """Lexes a script with the state of the client that runs it.

    The state is the active delimiter, whether the client is at the start of a
    statement (nothing but whitespace and comments since the last delimiter),
    and whether it is at the start of a line. Commands are lexed here. All
    other text is lexed by the dialect's matchers, from the text the server
    gets: the statement ends where the client finds the delimiter or a short
    command.
    """

    def __init__(
        self,
        rules: ClientCommandRules,
        matchers: list[LexerType],
        last_resort: LexerType,
    ) -> None:
        self._rules = rules
        self._matchers = matchers
        self._last_resort = last_resort
        by_name = {matcher.name: matcher for matcher in matchers}
        self._word_matcher = by_name[_WORD]
        self._whitespace_matcher = by_name[_WHITESPACE]
        self._inline_comment_matcher = by_name[_INLINE_COMMENT]

    def lex(self, text: str) -> list[LexedElement]:
        """Lex `text` into elements."""
        self._text = text
        self._pos = 0
        self._elements: list[LexedElement] = []
        self._delimiter = self._rules.default_delimiter
        self._delimiter_place = _NextPlace(self._delimiter)
        self._shorthand_places = [
            _NextPlace(command.shorthand)
            for command in self._rules.commands
            if command.shorthand
        ]
        self._statement_start = True
        self._line_start = True

        while self._pos < len(text):
            match self._peek():
                case _DelimiterCommand(found):
                    self._lex_delimiter_command(found)
                case _SourceLine(found):
                    self._lex_source_line(found)
                case _SourceStatement(found):
                    self._lex_source_statement(found)
                case _Shorthand(found):
                    self._lex_shorthand(found)
                case _ActiveDelimiter():
                    self._lex_active_delimiter()
                case _StatementStartComment():
                    self._lex_statement_start_comment()
                case _Token():
                    self._lex_token()
        return self._elements

    def _peek(self) -> _Next:
        r"""What comes next, checked in the order the client checks.

        Long-form commands count only at the start of a statement, and take
        their line unless the client collects it as a statement first (see
        `_line_is_collected`). Short forms count anywhere outside comments and
        strings.
        """
        long = None
        if self._statement_start:
            long = self._long_command(self._rest_of_line())
        if long is not None and self._line_start and not self._line_is_collected(long):
            if long.command.effect is CommandEffect.SET_DELIMITER:
                return _DelimiterCommand(long)
            if long.command.effect is CommandEffect.READ_FILE:
                return _SourceLine(long)
        if self._text.startswith(self._delimiter, self._pos):
            return _ActiveDelimiter()
        command = self._rules.command_starting(self._text, self._pos)
        if command is not None and command.shorthand is not None:
            return _Shorthand(_CommandWord(command, command.shorthand))
        if long is not None and long.command.effect is CommandEffect.READ_FILE:
            return _SourceStatement(long)
        if (
            self._statement_start
            and self._rules.dash_dash_comment_at_statement_start
            and self._text.startswith("--", self._pos)
        ):
            return _StatementStartComment()
        return _Token()

    def _line_is_collected(self, found: _CommandWord) -> bool:
        """Whether the client collects this line as a statement, not as `found`.

        As the client's `find_command`, it does when the line holds the
        collected-line marker, or holds the delimiter and `found` doesn't set
        the delimiter (`DELIMITER ;` holds the delimiter it replaces).
        """
        line = self._rest_of_line()
        marker = self._rules.collected_line_marker
        if marker is not None and marker in line:
            return True
        sets_delimiter = found.command.effect is CommandEffect.SET_DELIMITER
        return not sets_delimiter and self._delimiter in line

    def _lex_delimiter_command(self, found: _CommandWord) -> None:
        """`DELIMITER` and its argument. The rest of the line is ignored."""
        argument = self._rest_of_line()[len(found.word) :]
        self._emit(found.word, self._word_matcher)
        rest = self._delimiter_argument(argument)
        self._emit_ignored(rest)
        # The command took its line, and added nothing to the statement the
        # client is collecting.
        self._statement_start = True

    def _lex_source_line(self, found: _CommandWord) -> None:
        """`SOURCE` and the file name that is the rest of its line."""
        argument = self._rest_of_line()[len(found.word) :]
        self._emit(found.word, self._word_matcher)
        self._file_name(argument)
        # The command took its line, and added nothing to the statement the
        # client is collecting.
        self._statement_start = True

    def _lex_source_statement(self, found: _CommandWord) -> None:
        r"""`SOURCE` that the client collects as a statement before reading it.

        That happens when its line holds the delimiter or `\g`, or when it
        follows a delimiter earlier on the line. The statement runs to the
        delimiter. A short command in it runs as the client reaches it, so it
        is lexed as a command after the text before it: `SOURCE a.sql \g`
        sends `SOURCE a.sql` to the server, and the statement ends there.
        """
        argument = self._rest_of_line()[len(found.word) :]
        self._emit(found.word, self._word_matcher)
        end = self._first_break(argument)
        if end is None:
            # The statement runs on past this line, so the client doesn't
            # open the file this names.
            self._emit_misread(argument)
        elif argument.startswith(self._delimiter, end) and "\\" not in argument[:end]:
            self._file_name(argument[:end])
        else:
            # A short command comes first, or a backslash before the
            # delimiter ran as a command: the client doesn't open the file
            # this names.
            self._emit_misread(argument[:end])

    def _lex_shorthand(self, found: _CommandWord) -> None:
        """A short-form command and its argument."""
        argument = self._rest_of_line()[len(found.word) :]
        self._emit(found.word, CLIENT_COMMAND_SHORTHAND)
        if found.command.effect is CommandEffect.END_STATEMENT:
            self._statement_start = True
        elif found.command.effect is CommandEffect.SET_DELIMITER:
            self._shorthand_delimiter_argument(argument)
        elif found.command.effect is CommandEffect.READ_FILE:
            # `\.` reads the rest of its line as the file name, delimiter and
            # all.
            self._file_name(argument)

    def _lex_active_delimiter(self) -> None:
        """The active delimiter, which ends the statement."""
        if self._delimiter == self._rules.default_delimiter:
            # The default delimiter keeps the dialect's own token for it.
            self._lex_token()
        else:
            self._emit(self._delimiter, CLIENT_DELIMITER)
        self._statement_start = True

    def _lex_statement_start_comment(self) -> None:
        """`--` with no whitespace after it, as a comment."""
        # Up to the newline, as the comment matcher's `[^\n]*` would take it.
        end = self._text.find("\n", self._pos)
        self._emit(
            self._text[self._pos : end if end >= 0 else None],
            self._inline_comment_matcher,
        )

    def _lex_token(self) -> None:
        """One token, lexed by the dialect's matchers.

        The client looks for the delimiter and short commands everywhere but
        in the tokens it scans through (strings and comments). Any other
        token is lexed again from the text the server gets, which ends at the
        next one of those. So `1.go` with `go` active is `1.`, and `--$$`
        with `$$` active is a comment, as `--` at the end of the server's
        input is.
        """
        rest = self._text[self._pos :]
        elements = self._match(rest)
        if elements[0].matcher.name not in self._rules.opaque_token_names:
            end = self._statement_end() - self._pos
            if end < len(rest):
                elements = self._match(rest[:end])
        for element in elements:
            self._emit(element.raw, element.matcher)

    def _match(self, text: str) -> list[LexedElement]:
        for matcher in self._matchers:
            result = matcher.match(text)
            if result.elements:
                return result.elements
        result = self._last_resort.match(text)
        if not result.elements:  # pragma: no cover
            raise SQLLexError(f"Fatal. Unable to lex characters: {text[:10]!r}")
        return result.elements

    def _statement_end(self) -> int:
        """Where the client next finds the delimiter or a short command, after here."""
        places = [self._delimiter_place, *self._shorthand_places]
        return min(place.after(self._text, self._pos) for place in places)

    def _delimiter_argument(self, argument: str) -> str:
        """Lex the argument of `DELIMITER` and set the delimiter from it.

        This follows the client's `get_arg`: whitespace, then either a word
        ending at the next space, in which a backslash escapes the next
        character, or a word in quotes, with no escapes. An empty argument, or
        one with a backslash left in it, is refused and the delimiter kept.
        Returns the text after the argument.
        """
        trimmed = argument.lstrip(_SPACE)
        self._emit(argument[: len(argument) - len(trimmed)], self._whitespace_matcher)
        if not trimmed:
            return ""

        parsed = _parse_argument(trimmed)
        delimiter = self._accepted_delimiter(parsed.value)
        if delimiter is None:
            self._emit(parsed.raw, CLIENT_COMMAND_MISREAD)
        else:
            self._emit(parsed.raw, DELIMITER_ARGUMENT)
            self._delimiter = delimiter
            self._delimiter_place = _NextPlace(delimiter)
        return trimmed[len(parsed.raw) :]

    def _shorthand_delimiter_argument(self, argument: str) -> None:
        r"""Lex the argument of `\d`.

        Once the delimiter is set, the client skips everything after `\d` up
        to and including the first copy of the (new) delimiter, or to the end
        of the line, and goes on lexing from there.
        """
        new_delimiter = self._accepted_delimiter(
            _parse_argument(argument.lstrip(_SPACE)).value
        )
        skip_end = argument.find(new_delimiter or self._delimiter)
        rest = self._delimiter_argument(argument)
        argument_end = len(argument) - len(rest)
        if skip_end < 0:
            self._emit_ignored(rest)
            return
        skip_end += len(self._delimiter)
        if skip_end < argument_end:
            # The client goes on lexing from inside the argument (a quoted
            # delimiter). Nothing sensible follows, so the remainder of the
            # line is misread.
            self._emit_misread(rest)
            return
        self._emit_ignored(rest[: skip_end - argument_end])

    def _accepted_delimiter(self, value: str) -> Optional[str]:
        """The delimiter the client sets from an argument's value.

        `None` if it refuses the value: empty, or with a backslash left in it.
        """
        if not value or "\\" in value:
            return None
        return _cut_to_bytes(value, self._rules.max_delimiter_bytes)

    def _file_name(self, argument: str) -> None:
        r"""Lex the argument of `SOURCE` or `\.`, as the client's `com_source`.

        A space must follow the command. The file name is the rest, from the
        first character that isn't whitespace, with trailing whitespace and
        control characters dropped.
        """
        if not argument.startswith(" "):
            self._emit_misread(argument)
            return
        gap = len(argument) - len(argument.lstrip(_SPACE))
        self._emit(argument[:gap], self._whitespace_matcher)
        name = _strip_trailing(argument[gap:])
        self._emit(name, SOURCE_FILE_NAME)
        self._emit_ignored(argument[gap + len(name) :])

    def _long_command(self, line: str) -> Optional[_CommandWord]:
        """The long-form command that starts `line`.

        The name must be followed by whitespace or the end of the line.
        """
        length = 0
        while length < len(line) and line[length].isascii() and line[length].isalpha():
            length += 1
        if length == 0 or (length < len(line) and line[length] not in " \t"):
            return None
        command = self._rules.command_named(line[:length])
        if command is None:
            return None
        return _CommandWord(command, line[:length])

    def _emit(self, raw: str, matcher: LexerType) -> None:
        """Add an element and update the client's state for it."""
        if not raw:
            return
        self._elements.append(LexedElement(raw, matcher))
        self._pos += len(raw)
        if matcher.name == _NEWLINE:
            self._line_start = True
        elif matcher.name == _BLOCK_COMMENT:
            if not self._rules.line_command_after_block_comment:
                self._line_start = False
        elif matcher.name not in (_WHITESPACE, _INLINE_COMMENT):
            self._line_start = False
            if matcher.name not in _CLIENT_READ_TOKEN_NAMES:
                # The client adds this to the statement it is collecting.
                self._statement_start = False

    def _emit_ignored(self, text: str) -> None:
        """Text the client reads past, between any whitespace around it."""
        content = text.strip(_SPACE)
        if not content:
            self._emit(text, self._whitespace_matcher)
            return
        start = text.index(content[0])
        self._emit(text[:start], self._whitespace_matcher)
        self._emit(content, CLIENT_COMMAND_IGNORED)
        self._emit(text[start + len(content) :], self._whitespace_matcher)

    def _emit_misread(self, text: str) -> None:
        """Text the client misreads, between any whitespace around it."""
        content = text.strip(_SPACE)
        if not content:
            self._emit(text, self._whitespace_matcher)
            return
        start = text.index(content[0])
        self._emit(text[:start], self._whitespace_matcher)
        self._emit(content, CLIENT_COMMAND_MISREAD)
        self._emit(text[start + len(content) :], self._whitespace_matcher)

    def _first_break(self, text: str) -> Optional[int]:
        """Where the client finds the delimiter or a short command in `text`."""
        needles = [self._delimiter]
        needles.extend(
            command.shorthand for command in self._rules.commands if command.shorthand
        )
        found = [
            index for index in (text.find(needle) for needle in needles) if index >= 0
        ]
        return min(found, default=None)

    def _rest_of_line(self) -> str:
        """The text from here to the end of the line, without the line break."""
        end = self._text.find("\n", self._pos)
        line = self._text[self._pos :] if end < 0 else self._text[self._pos : end]
        return line[:-1] if line.endswith("\r") else line


def _parse_argument(text: str) -> _Argument:
    r"""The command argument that starts `text`, as the client's `get_arg` reads it.

    A quoted argument runs to the matching quote, or the end of the text, with
    no escapes. An unquoted one ends at a space, and a backslash in it escapes
    the character after it, which is kept in the value without the backslash,
    so `a\ b` is one argument. A backslash at the very end stays in the value.
    """
    if text[:1] in ("'", '"', "`"):
        close = text.find(text[0], 1)
        if close < 0:
            return _Argument(text, text[1:])
        return _Argument(text[: close + 1], text[1:close])

    value = []
    index = 0
    while index < len(text) and text[index] != " ":
        if text[index] == "\\" and index + 1 < len(text):
            value.append(text[index + 1])
            index += 2
        else:
            value.append(text[index])
            index += 1
    return _Argument(text[:index], "".join(value))


def _cut_to_bytes(value: str, limit: int) -> str:
    """Cut `value` to `limit` bytes of UTF-8, at a character boundary.

    The client cuts at the byte limit even inside a multi-byte character. A
    delimiter ending in part of a character can't match text made of whole
    characters, so the boundary before that character is the nearest
    equivalent.
    """
    encoded = value.encode("utf-8")
    if len(encoded) <= limit:
        return value
    return encoded[:limit].decode("utf-8", errors="ignore")


def _strip_trailing(text: str) -> str:
    """`text` without trailing whitespace or control characters."""
    end = len(text)
    while end > 0 and (text[end - 1] in _SPACE or ord(text[end - 1]) < 0x20):
        end -= 1
    return text[:end]
