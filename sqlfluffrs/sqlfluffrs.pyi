from typing import TYPE_CHECKING, Any, List, Optional, Tuple, Union
from uuid import UUID

if TYPE_CHECKING:
    from sqlfluff.core.config import FluffConfig
    from sqlfluff.core.parser.lexer import StringLexer
    from sqlfluff.core.parser.segments import SourceFix
    from sqlfluff.core.templaters import TemplatedFile

SerializedObject = dict[str, Union[str, int, bool, list["SerializedObject"]]]
TupleSerialisedSegment = tuple[str, Union[str, tuple["TupleSerialisedSegment", ...]]]

class Slice: ...

class RsRawFileSlice:
    raw: str
    slice_type: str
    source_idx: int
    block_idx: int
    tag: Optional[str]

class RsTemplatedFileSlice:
    slice_type: str
    source_slice: Slice
    templated_slice: Slice

class RsTemplatedFile:
    source_str: str
    fname: str
    templated_str: str
    sliced_file: List[RsTemplatedFileSlice]
    raw_sliced: List[RsRawFileSlice]

class RsPositionMarker:
    source_slice: slice
    templated_slice: slice
    templated_file: RsTemplatedFile
    working_line_no: int
    working_line_pos: int

class RsToken:
    raw: str
    pos_marker: RsPositionMarker
    type: str
    uuid: Optional[int]
    source_fixes: Optional[list["SourceFix"]]

    def raw_trimmed(self) -> str: ...
    @property
    def is_templated(self) -> bool: ...
    @property
    def is_code(self) -> bool: ...
    @property
    def is_meta(self) -> bool: ...
    @property
    def source_str(self) -> str: ...
    @property
    def block_type(self) -> str: ...
    @property
    def block_uuid(self) -> Optional[UUID]: ...
    @property
    def cache_key(self) -> str: ...
    @property
    def trim_start(self) -> Optional[tuple[str]]: ...
    @property
    def trim_chars(self) -> Optional[tuple[str]]: ...
    @property
    def quoted_value(self) -> Optional[tuple[str, int | str]]: ...
    @property
    def escape_replacements(self) -> Optional[list[tuple[str, str]]]: ...
    def count_segments(self, raw_only: bool = False) -> int: ...
    def get_type(self) -> str: ...
    def recursive_crawl(
        self,
        seg_type: Tuple[str, ...],
        recurse_into: bool,
        no_recursive_seg_type: Optional[Union[str, List[str]]] = None,
        allow_self: bool = True,
    ) -> List["RsToken"]: ...
    def recursive_crawl_all(self, reverse: bool) -> List["RsToken"]: ...
    @property
    def segments(self) -> List["RsToken"]: ...
    def path_to(self, other: "RsToken") -> List[Any]: ...
    def get_start_loc(self) -> Tuple[int, int]: ...
    def get_end_loc(self) -> Tuple[int, int]: ...
    @property
    def raw_segments(self) -> List["RsToken"]: ...
    def copy(
        self,
        segments: Optional[List["RsToken"]] = None,
        parent: Optional[Any] = None,
        parent_idx: Optional[int] = None,
    ) -> "RsToken": ...
    def edit(
        self,
        raw: Optional[str] = None,
        source_fixes: Optional[List[Any]] = None,
    ) -> "RsToken": ...
    def to_tuple(
        self,
        code_only: Optional[bool] = None,
        show_raw: Optional[bool] = None,
        include_meta: Optional[bool] = None,
    ) -> TupleSerialisedSegment: ...
    def __repr__(self) -> str: ...
    @property
    def instance_types(self) -> List[str]: ...
    @staticmethod
    def template_placeholder_from_slice(
        source_slice: tuple[int, int],
        templated_slice: tuple[int, int],
        block_type: str,
        _source_str: str,
        block_uuid: Optional[str],
        templated_file: "TemplatedFile",
    ) -> "RsToken": ...

class RsSQLLexerError:
    desc: str
    line_no: int
    line_pos: int
    ignore: bool
    warning: bool
    fatal: bool

    def __init__(
        self,
        msg: Optional[str] = None,
        pos: Optional[RsPositionMarker] = None,
        line_no: int = 0,
        line_pos: int = 0,
        ignore: bool = False,
        warning: bool = False,
        fatal: bool = False,
    ) -> None: ...
    def rule_code(self) -> str: ...
    def rule_name(self) -> str: ...
    def source_signature(self) -> Tuple[Tuple[str, int, int], str]: ...
    def to_dict(self) -> SerializedObject: ...
    def ignore_if_in(self, ignore_iterable: list[str]) -> None: ...
    def warning_if_in(self, ignore_iterable: list[str]) -> None: ...

class RsLexer:
    def __init__(
        self,
        config: Optional["FluffConfig"] = None,
        last_resort_lexer: Optional["StringLexer"] = None,
        dialect: Optional[str] = None,
    ): ...
    def _lex(
        self, lex_input: Union[str, "TemplatedFile"]
    ) -> Tuple[List[RsToken], List[Any]]: ...

class RsMatchResult:
    """Result of a Rust parser match operation."""

    matched_slice: tuple[int, int]
    matched_class: Optional[str]
    child_matches: List["RsMatchResult"]
    parse_error: Optional[tuple[str, int]]
    instance_types: Optional[List[str]]
    segment_kwargs: Optional[dict[str, Any]]
    trim_chars: Optional[List[str]]
    casefold: Optional[str]
    quoted_value: Optional[str]
    escape_replacement: Optional[tuple[str, str]]
    insert_segments: Optional[List[tuple[int, str, bool]]]

class RsParser:
    """Rust-based SQL parser."""

    def __init__(
        self,
        dialect: str,
        indent_config: Optional[dict[str, bool]] = None,
    ): ...
    def parse_match_result_from_tokens(
        self, tokens: List[RsToken]
    ) -> RsMatchResult: ...
