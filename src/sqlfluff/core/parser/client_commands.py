r"""Lexing scripts that are run through a command-line client.

Some SQL is never sent to the server as written. A command-line client reads
the script line by line, splits it into statements itself and handles some of
the text before anything reaches the server: commands that change how the rest
of the script is split (the statement delimiter), commands that take raw text
arguments (a file to read), and comment forms that depend on where they
appear. Lexing such a script correctly needs the same state the client keeps.

The client collects text into a statement, and the delimiter or `\g` sends
it to the server (without the delimiter). A short command such as `\d` runs
wherever the client reaches it, and collecting goes on after it; `\g` sends
the statement collected so far, so collecting starts a new one. Oddly, `\.`
throws the statement away instead, though `\d` leaves it alone. Unlike a
short command, a long-form command such as `DELIMITER` must be the entire
statement: it runs alone on its line at the start of a statement, unless the
line holds `\g` (but, for no apparent reason, not `\G`), or holds the
delimiter and the command isn't `DELIMITER`. Then, or when it follows a
delimiter earlier on its line, the client collects it, and at the delimiter
runs the statement as that command instead of sending it. Oddly again, a
collected `DELIMITER //;` sets `//`, though on its own line it sets `//;`.

A *break* is where the client stops passing text to the server and acts itself:
at the active delimiter or a short command.

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


class ArgumentKind(Enum):
    """What a client command reads after its name."""

    # A new statement delimiter, e.g. `DELIMITER $$`.
    DELIMITER = "delimiter"

    # A script to run, e.g. `SOURCE file.sql`.
    FILE_NAME = "file_name"


class BufferAction(Enum):
    """What a short command does to the statement it appears in."""

    # The statement carries on, e.g. `\d`.
    KEEP = "keep"

    # The statement is sent to the server, as at the delimiter, e.g. `\g`.
    END = "end"

    # The statement is thrown away, e.g. `\.`.
    DISCARD = "discard"


@dataclass(frozen=True)
class LongClientCommand:
    """A long-form command, e.g. `DELIMITER $$`. It must be the entire statement.

    It runs alone on its line at the start of a statement, or as a statement
    collected up to the delimiter. So it never acts on SQL around it.
    """

    # In lower case, matched in any case.
    name: str
    argument: ArgumentKind


@dataclass(frozen=True)
class ShortClientCommand:
    r"""A command that runs wherever it appears outside strings and comments.

    E.g. `\d $$`, which may come in the middle of a statement.
    """

    # Matched in its own case, e.g. `\d`.
    text: str
    buffer_action: BufferAction
    argument: Optional[ArgumentKind] = None


@dataclass(frozen=True)
class ClientCommandRules:
    """How a command-line client splits a script into statements."""

    long_commands: tuple[LongClientCommand, ...]
    short_commands: tuple[ShortClientCommand, ...]
    # Lexer matchers whose text the client doesn't scan: strings, quoted
    # identifiers and comments. The delimiter isn't found inside these.
    opaque_token_names: frozenset[str]
    # Whether a `/* ... */` comment may come before a long-form command that
    # takes its line. A command the client collects as a statement may follow a
    # comment either way.
    line_command_after_block_comment: bool
    # Whether `--` starts a comment at the start of a statement even with no
    # whitespace after it. Elsewhere `--` needs whitespace or the end of the line
    # after it, which is the dialect's comment matcher's job.
    dash_dash_comment_at_statement_start: bool
    # A line holding this text is never a long-form command line: the client
    # collects it as a statement instead. For no apparent reason the mysql
    # client only checks for a lower-case `\g` here, though `\G` ends a
    # statement just the same: `SOURCE x.sql \G` reads a file named `x.sql \G`.
    collected_line_marker: Optional[str]
    default_delimiter: str = ";"
    # If set, longer delimiters are cut to this many bytes, as the client does.
    # `None` for no limit.
    max_delimiter_bytes: Optional[int] = None

    def __post_init__(self) -> None:
        """Check the rules are ones the lexer can work with."""
        # `long_command_named` lowers only the name as typed, so the names here
        # must be in lower case, as in the client's own command table.
        for command in self.long_commands:
            assert command.name == command.name.lower(), (
                f"long command name {command.name!r} must be lower case: {self}"
            )
        # A cut must leave at least one character, which is up to 4 bytes.
        assert self.max_delimiter_bytes is None or self.max_delimiter_bytes >= 4, (
            f"max_delimiter_bytes must be None or at least 4: {self}"
        )
        # The default must be a delimiter the lexer would accept. The lexer
        # relies on it: one with whitespace in it can match before an argument
        # starts, and an empty one matches everywhere.
        delimiter = self.default_delimiter
        assert (
            delimiter
            and "\\" not in delimiter
            and not any(character in _SPACE for character in delimiter)
            and (
                self.max_delimiter_bytes is None
                or len(delimiter.encode("utf-8")) <= self.max_delimiter_bytes
            )
        ), f"default_delimiter {delimiter!r} is not one the client would set: {self}"

    def long_command_named(self, name: str) -> Optional[LongClientCommand]:
        """The long command called `name`, in any case."""
        lowered = name.lower()
        for command in self.long_commands:
            if command.name == lowered:
                return command
        return None

    def short_command_starting(
        self, text: str, pos: int = 0
    ) -> Optional[ShortClientCommand]:
        """The short command that starts at `pos` in `text`."""
        for command in self.short_commands:
            if text.startswith(command.text, pos):
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


# The active delimiter, when it isn't the default one.
CLIENT_DELIMITER = EmittedToken("client_delimiter", ClientTextSegment)
# A short command, such as `\d`, `\.` or `\g`.
CLIENT_SHORT_COMMAND = EmittedToken("client_short_command", CodeSegment)
# The new delimiter in `DELIMITER $$`, as written.
DELIMITER_ARGUMENT = EmittedToken("delimiter_argument", ClientTextSegment)
# The file name in `SOURCE file.sql`, as the client reads it.
SOURCE_FILE_NAME = EmittedToken("source_file_name", ClientTextSegment)
# Text on a command's line that the client reads past without using.
CLIENT_COMMAND_IGNORED = EmittedToken("client_command_ignored", ClientTextSegment)
# A command argument the client rejects, with an error. No grammar accepts it,
# so it is reported as a parse error.
CLIENT_COMMAND_REJECTED = EmittedToken("client_command_rejected", ClientTextSegment)
# Command text the client sends to the server as SQL, not as the command it
# looks like. No grammar accepts it, so it is reported as a parse error.
CLIENT_COMMAND_MISREAD = EmittedToken("client_command_misread", ClientTextSegment)

# Standard matcher names, which every dialect has.
_WORD = "word"
_WHITESPACE = "whitespace"
_NEWLINE = "newline"
_INLINE_COMMENT = "inline_comment"
_BLOCK_COMMENT = "block_comment"


class _Buffer(Enum):
    """What a piece of text does to the statement the client is collecting."""

    # It goes into the statement: SQL.
    APPEND = "append"

    # The statement stays as it is: whitespace, comments, and the client
    # commands the client takes out and runs.
    KEEP = "keep"

    # The statement is sent and a new one starts: the delimiter, `\g`.
    END = "end"

    # The statement is thrown away and a new one starts: `\.`.
    DISCARD = "discard"


_BUFFER_FOR_ACTION = {
    BufferAction.KEEP: _Buffer.KEEP,
    BufferAction.END: _Buffer.END,
    BufferAction.DISCARD: _Buffer.DISCARD,
}

# Matchers whose tokens are non-code: whitespace, newlines and comments. They
# don't change the statement the client is collecting.
_NON_CODE_MATCHERS = frozenset({_WHITESPACE, _NEWLINE, _INLINE_COMMENT, _BLOCK_COMMENT})

# What the client's `my_isspace` accepts within a line.
_SPACE = " \t\v\f\r"


class _CommandWord(NamedTuple):
    """A long command, and its name as written."""

    command: LongClientCommand
    word: str


# What comes next in the script, as the client reads it: one of the classes
# below, as `_Next`.


class _DelimiterLine(NamedTuple):
    """A command that sets the delimiter (`DELIMITER`), at the start of a line.

    It takes the line.
    """

    found: _CommandWord


class _DelimiterStatement(NamedTuple):
    """A command that sets the delimiter, which the client collects first."""

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


class _ShortCommand(NamedTuple):
    r"""A short command, such as `\d`, `\.` or `\g`."""

    command: ShortClientCommand


class _ActiveDelimiter(NamedTuple):
    """The active delimiter, which ends the statement."""


class _StatementStartComment(NamedTuple):
    """`--` with no whitespace after it, at the start of a statement.

    The client takes it as a comment.
    """


class _Token(NamedTuple):
    """Anything else, for the dialect's matchers."""


_Next = Union[
    _DelimiterLine,
    _DelimiterStatement,
    _SourceLine,
    _SourceStatement,
    _ShortCommand,
    _ActiveDelimiter,
    _StatementStartComment,
    _Token,
]


class _Argument(NamedTuple):
    """A command argument: its text as written, and the value the client reads."""

    raw: str
    # `None` for a quote with no closing quote, which is rejected.
    value: Optional[str]


class _NextPlace:
    """Where a text next appears in the script, found again once lexing passes it.

    Each search runs on from the last place found, so the whole script is
    searched about once. The place is only meaningful in the one script, so it
    holds that script.
    """

    def __init__(self, script: str, needle: str) -> None:
        self._script = script
        self._needle = needle
        self._at = 0

    def after(self, pos: int) -> int:
        """The first place after `pos` where the text appears, or the script's end."""
        if self._at <= pos:
            found = self._script.find(self._needle, pos + 1)
            self._at = found if found >= 0 else len(self._script)
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

    def lex(self, script: str) -> list[LexedElement]:
        """Lex `script` into elements."""
        self._script = script
        self._pos = 0
        self._elements: list[LexedElement] = []
        self._delimiter = self._rules.default_delimiter
        self._delimiter_place = _NextPlace(script, self._delimiter)
        self._short_command_places = [
            _NextPlace(script, command.text) for command in self._rules.short_commands
        ]
        self._statement_start = True
        self._line_start = True

        while self._pos < len(script):
            match next_part := self._peek():
                case _DelimiterLine(found):
                    self._lex_delimiter_line(found)
                case _DelimiterStatement(found):
                    self._lex_delimiter_statement(found)
                case _SourceLine(found):
                    self._lex_source_line(found)
                case _SourceStatement(found):
                    self._lex_source_statement(found)
                case _ShortCommand(command):
                    self._lex_short_command(command)
                case _ActiveDelimiter():
                    self._lex_active_delimiter()
                case _StatementStartComment():
                    self._lex_statement_start_comment()
                case _Token():
                    self._lex_token()
                case _:  # pragma: no cover
                    # Without this, a `_Next` kind missing above would loop forever.
                    raise AssertionError(f"Unhandled {next_part!r}")
        return self._elements

    def _peek(self) -> _Next:
        r"""What comes next, checked in the order the client checks.

        Long-form commands count only at the start of a statement, and take
        their line unless the client collects it as a statement first (see
        `_line_is_collected`). Short commands count anywhere outside comments and
        strings.
        """
        long = None
        if self._statement_start:
            long = self._long_command(self._rest_of_line())
        if long is not None and self._line_start and not self._line_is_collected(long):
            if long.command.argument is ArgumentKind.DELIMITER:
                return _DelimiterLine(long)
            if long.command.argument is ArgumentKind.FILE_NAME:
                return _SourceLine(long)
        if self._script.startswith(self._delimiter, self._pos):
            return _ActiveDelimiter()
        command = self._rules.short_command_starting(self._script, self._pos)
        if command is not None:
            return _ShortCommand(command)
        if long is not None:
            if long.command.argument is ArgumentKind.DELIMITER:
                return _DelimiterStatement(long)
            if long.command.argument is ArgumentKind.FILE_NAME:
                return _SourceStatement(long)
        if (
            self._statement_start
            and self._rules.dash_dash_comment_at_statement_start
            and self._script.startswith("--", self._pos)
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
        sets_delimiter = found.command.argument is ArgumentKind.DELIMITER
        return not sets_delimiter and self._delimiter in line

    def _lex_delimiter_line(self, found: _CommandWord) -> None:
        """`DELIMITER` and its argument. The rest of the line is ignored."""
        argument = self._rest_of_line()[len(found.word) :]
        self._emit(found.word, self._word_matcher, _Buffer.KEEP)
        rest = self._delimiter_argument(argument)
        self._emit_ignored(rest)

    def _lex_delimiter_statement(self, found: _CommandWord) -> None:
        r"""`DELIMITER` that the client collects as a statement before running it.

        That happens when it follows a delimiter or `\g` earlier on its line,
        or when its line holds `\g`. At the delimiter the client sees the
        statement starts with `DELIMITER` and runs it, so the new delimiter
        applies from just after the old one. Oddly, the argument then ends at
        the old delimiter: `SELECT 1; DELIMITER //;` sets `//`, though
        `DELIMITER //;` on its own line sets `//;`. If the old delimiter isn't
        on the line, the client collects the lines after it into the statement
        too, and the clients disagree on what they then do with them, so that
        is misread.
        """
        argument = self._rest_of_line()[len(found.word) :]
        self._emit(found.word, self._word_matcher, _Buffer.APPEND)
        end = self._first_break_in(argument)
        if end is None:
            # The statement runs on past this line.
            self._emit_misread(argument, _Buffer.APPEND)
            return
        if not argument.startswith(self._delimiter, end) or "\\" in argument[:end]:
            # A short command comes first, or a backslash before the
            # delimiter ran as a command.
            self._emit_misread(argument[:end], _Buffer.APPEND)
            return
        old_delimiter = argument[end : end + len(self._delimiter)]
        rest = self._delimiter_argument(argument[:end])
        self._emit_ignored(rest)
        self._emit_delimiter(old_delimiter)

    def _lex_source_line(self, found: _CommandWord) -> None:
        """`SOURCE` and the file name that is the rest of its line."""
        argument = self._rest_of_line()[len(found.word) :]
        self._emit(found.word, self._word_matcher, _Buffer.KEEP)
        self._file_name(argument, _Buffer.KEEP)

    def _lex_source_statement(self, found: _CommandWord) -> None:
        r"""`SOURCE` that the client collects as a statement before reading it.

        That happens when its line holds the delimiter or `\g`, or when it
        follows a delimiter earlier on the line. The client then treats it
        almost like SQL, with results that are probably client bugs:
        - `SOURCE a.sql;` still runs the file: at the delimiter the client sees
          the statement starts with `SOURCE` and runs it.
        - `SOURCE a.sql \g` sends `SOURCE a.sql` to the server as SQL, which
          fails: `\g` sends the statement without that check.
        """
        argument = self._rest_of_line()[len(found.word) :]
        self._emit(found.word, self._word_matcher, _Buffer.APPEND)
        end = self._first_break_in(argument)
        if end is None:
            # The statement runs on past this line, so the client doesn't
            # open the file this names.
            self._emit_misread(argument, _Buffer.APPEND)
        elif argument.startswith(self._delimiter, end) and "\\" not in argument[:end]:
            self._file_name(argument[:end], _Buffer.APPEND)
        else:
            # A short command comes first, or a backslash before the
            # delimiter ran as a command: the client doesn't open the file
            # this names.
            self._emit_misread(argument[:end], _Buffer.APPEND)

    def _lex_short_command(self, command: ShortClientCommand) -> None:
        """A short command and its argument."""
        argument = self._rest_of_line()[len(command.text) :]
        self._emit(
            command.text,
            CLIENT_SHORT_COMMAND,
            _BUFFER_FOR_ACTION[command.buffer_action],
        )
        if command.argument is ArgumentKind.DELIMITER:
            self._short_command_delimiter_argument(argument)
        elif command.argument is ArgumentKind.FILE_NAME:
            # `\.` reads the rest of its line as the file name, delimiter and
            # all.
            self._file_name(argument, _Buffer.KEEP)

    def _lex_active_delimiter(self) -> None:
        """The active delimiter, which ends the statement."""
        self._emit_delimiter(self._script[self._pos : self._pos + len(self._delimiter)])

    def _emit_delimiter(self, raw: str) -> None:
        """A delimiter, here, which ends the statement."""
        if raw == self._rules.default_delimiter:
            # The default delimiter keeps the dialect's own token for it.
            for element in self._match(raw):
                self._emit(element.raw, element.matcher, _Buffer.END)
        else:
            self._emit(raw, CLIENT_DELIMITER, _Buffer.END)

    def _lex_statement_start_comment(self) -> None:
        """`--` with no whitespace after it, as a comment."""
        # Up to the newline, as the comment matcher's `[^\n]*` would take it.
        end = self._script.find("\n", self._pos)
        self._emit(
            self._script[self._pos : end if end >= 0 else None],
            self._inline_comment_matcher,
            _Buffer.KEEP,
        )

    def _lex_token(self) -> None:
        """One token, lexed by the dialect's matchers.

        The client cuts the statement at the delimiter or a short command before
        the server sees it, so a token that isn't a string or comment is lexed
        again from the text up to there. With `go` as the delimiter, `1.go` is the
        number `1.`. And, absurdly, with `$$` as the delimiter `--$$` is a
        comment: the client doesn't treat `--` without a space as a comment, but
        the server does at the end of a statement.
        """
        rest = self._script[self._pos :]
        elements = self._match(rest)
        if elements[0].matcher.name not in self._rules.opaque_token_names:
            end = self._first_break_after_pos() - self._pos
            if end < len(rest):
                elements = self._match(rest[:end])
        for element in elements:
            if element.matcher.name in _NON_CODE_MATCHERS:
                self._emit(element.raw, element.matcher, _Buffer.KEEP)
            else:
                self._emit(element.raw, element.matcher, _Buffer.APPEND)

    def _match(self, forward_string: str) -> list[LexedElement]:
        for matcher in self._matchers:
            result = matcher.match(forward_string)
            if result.elements:
                return result.elements
        result = self._last_resort.match(forward_string)
        if not result.elements:  # pragma: no cover
            raise SQLLexError(
                f"Fatal. Unable to lex characters: {forward_string[:10]!r}"
            )
        return result.elements

    def _first_break_after_pos(self) -> int:
        """The first break after here: the next delimiter or short command."""
        places = [self._delimiter_place, *self._short_command_places]
        return min(place.after(self._pos) for place in places)

    def _delimiter_argument(self, argument: str) -> str:
        """Lex the argument of `DELIMITER` and set the delimiter from it.

        This follows the client's `get_arg`: whitespace, then either a word
        ending at the next space, in which a backslash escapes the next
        character, or a word in quotes, with no escapes. An empty argument, or
        one with a backslash left in it, is rejected and the delimiter kept.
        Returns the text after the argument.
        """
        trimmed = argument.lstrip(_SPACE)
        self._emit(
            argument[: len(argument) - len(trimmed)],
            self._whitespace_matcher,
            _Buffer.KEEP,
        )
        if not trimmed:
            return ""

        parsed = _parse_argument(trimmed)
        self._set_delimiter(parsed.raw, self._accepted_delimiter(parsed.value))
        return trimmed[len(parsed.raw) :]

    def _set_delimiter(self, raw: str, delimiter: Optional[str]) -> None:
        """Emit an argument as written, and set the delimiter it gives.

        `None` if the client rejected the argument: the delimiter is kept.
        """
        if delimiter is None:
            self._emit(raw, CLIENT_COMMAND_REJECTED, _Buffer.KEEP)
            return
        self._emit(raw, DELIMITER_ARGUMENT, _Buffer.KEEP)
        self._delimiter = delimiter
        self._delimiter_place = _NextPlace(self._script, delimiter)

    def _short_command_delimiter_argument(self, argument: str) -> None:
        r"""Lex the argument of `\d`.

        The mysql and mariadb clients handle this bizarrely, probably a client
        bug, but both do the same thing: after setting the delimiter, the client
        carries on reading right after the new delimiter's text on the line.
        Normally that's just after the argument: `\d $$ SELECT 1 $$` runs
        `SELECT 1`. But when the argument as typed isn't exactly the delimiter,
        ridiculous stuff happens:
        - `\d '$$'` sets `$$` and carries on inside the quotes, so the closing
          quote is read as SQL.
        - An argument over 15 bytes sets only its first 15 and carries on after
          those, so the rest is read as SQL.
        - `\d \$\$` sets `$$`, which isn't on the line as typed, so it carries
          on after the next `$$` on the line, or discards the rest of the line
          if there's none.

        Text the client skips belongs to the command: the server never sees it,
        even if it looks like SQL. SQL before the `\d` stays in the statement.
        """
        trimmed = argument.lstrip(_SPACE)
        gap = len(argument) - len(trimmed)
        parsed = _parse_argument(trimmed)
        delimiter = self._accepted_delimiter(parsed.value)
        needle = delimiter or self._delimiter
        found = trimmed.find(needle)
        resume = None if found < 0 else gap + found + len(needle)
        argument_end = gap + len(parsed.raw)
        if resume is not None and resume < argument_end:
            # The client goes on from inside the argument. The whole argument
            # still decides the delimiter, but only the text before that point
            # is the command's.
            self._emit(argument[:gap], self._whitespace_matcher, _Buffer.KEEP)
            self._set_delimiter(argument[gap:resume], delimiter)
            return
        rest = self._delimiter_argument(argument)
        if resume is None:
            self._emit_ignored(rest)
        else:
            self._emit_ignored(rest[: resume - argument_end])

    def _accepted_delimiter(self, value: Optional[str]) -> Optional[str]:
        r"""The delimiter the client sets from an argument's value.

        `None` if it rejects the value: empty, with a backslash left in it, or
        from a quote with no closing quote. The client checks these before it
        cuts the value to the byte limit. A delimiter with whitespace in it
        (from quotes or an escaped space, as in `\d a\ b`) is rejected too: the
        client takes it, but then finds it in ordinary SQL, as in `SELECT a b`,
        or only where an invisible space follows, so it is only ever a mistake.
        That is checked after the cut, on the delimiter the client would set.
        """
        if not value or "\\" in value:
            return None
        limit = self._rules.max_delimiter_bytes
        if limit is not None:
            value = _cut_to_bytes(value, limit)
        if any(character in _SPACE for character in value):
            return None
        return value

    def _file_name(self, argument: str, buffer: _Buffer) -> None:
        r"""Lex the argument of `SOURCE` or `\.`, as the client's `com_source`.

        A space must follow the command. The file name is the rest, from the
        first character that isn't whitespace, with trailing whitespace and
        control characters dropped. `buffer` says what the name does to the
        statement: nothing on a command's own line, but a collected `SOURCE`
        is part of the statement until the delimiter.
        """
        if not argument.startswith(" "):
            self._emit_rejected(argument, buffer)
            return
        gap = len(argument) - len(argument.lstrip(_SPACE))
        self._emit(argument[:gap], self._whitespace_matcher, _Buffer.KEEP)
        name = _strip_trailing(argument[gap:])
        self._emit(name, SOURCE_FILE_NAME, buffer)
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
        command = self._rules.long_command_named(line[:length])
        if command is None:
            return None
        return _CommandWord(command, line[:length])

    def _emit(self, raw: str, matcher: LexerType, buffer: _Buffer) -> None:
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
        if buffer is _Buffer.APPEND:
            self._statement_start = False
        elif buffer is not _Buffer.KEEP:
            # END or DISCARD: a new statement starts.
            self._statement_start = True

    def _emit_ignored(self, raw: str) -> None:
        """Text the client reads past, between any whitespace around it."""
        self._emit_between_spaces(raw, CLIENT_COMMAND_IGNORED, _Buffer.KEEP)

    def _emit_rejected(self, raw: str, buffer: _Buffer) -> None:
        """Text the client rejects, between any whitespace around it.

        `buffer` says whether the client puts it into the statement.
        """
        self._emit_between_spaces(raw, CLIENT_COMMAND_REJECTED, buffer)

    def _emit_misread(self, raw: str, buffer: _Buffer) -> None:
        """Text the client misreads, between any whitespace around it.

        `buffer` says whether the client puts it into the statement.
        """
        self._emit_between_spaces(raw, CLIENT_COMMAND_MISREAD, buffer)

    def _emit_between_spaces(
        self, raw: str, matcher: LexerType, buffer: _Buffer
    ) -> None:
        """`raw` as one `matcher` token, with any whitespace around it apart."""
        content = raw.strip(_SPACE)
        if not content:
            self._emit(raw, self._whitespace_matcher, _Buffer.KEEP)
            return
        start = raw.index(content[0])
        self._emit(raw[:start], self._whitespace_matcher, _Buffer.KEEP)
        self._emit(content, matcher, buffer)
        self._emit(raw[start + len(content) :], self._whitespace_matcher, _Buffer.KEEP)

    def _first_break_in(self, text: str) -> Optional[int]:
        """The first break in `text`: the delimiter or a short command."""
        needles = [self._delimiter]
        needles.extend(command.text for command in self._rules.short_commands)
        found = [
            index for index in (text.find(needle) for needle in needles) if index >= 0
        ]
        return min(found, default=None)

    def _rest_of_line(self) -> str:
        """The text from here to the end of the line, without the line break."""
        end = self._script.find("\n", self._pos)
        line = self._script[self._pos :] if end < 0 else self._script[self._pos : end]
        return line[:-1] if line.endswith("\r") else line


def _parse_argument(text: str) -> _Argument:
    r"""The command argument that starts `text`, as the client's `get_arg` reads it.

    A quoted argument runs to the matching quote, with no escapes. With no
    closing quote it has no value: the mysql client reads to the end of the
    line, but that only ever comes from a typo such as `DELIMITER '$$`, and the
    mariadb client rejects it, so it is rejected here. An unquoted argument ends
    at a space, and a backslash in it escapes the character after it, which is
    kept in the value without the backslash, so `a\ b` is one argument. A
    backslash at the very end stays in the value.
    """
    if text[:1] in ("'", '"', "`"):
        close = text.find(text[0], 1)
        if close < 0:
            return _Argument(text, None)
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
