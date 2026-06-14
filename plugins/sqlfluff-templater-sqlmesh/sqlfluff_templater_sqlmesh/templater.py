"""Defines the SQLMesh templater.

NOTE: The SQLMesh python package adds a significant overhead to import.
This module is also loaded on every run of SQLFluff regardless of
whether the SQLMesh templater is selected in the configuration.

The templater is however only _instantiated_ when selected, and as
such, all imports of the SQLMesh libraries are contained within the
SQLMeshTemplater class and so are only imported when necessary.
"""

import difflib
import logging
import os
import os.path
import re
from functools import cached_property
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Optional,
    TypeVar,
)

from sqlfluff.core.errors import SQLTemplaterError
from sqlfluff.core.templaters.base import TemplatedFile, large_file_check
from sqlfluff.core.templaters.jinja import JinjaTemplater

if TYPE_CHECKING:  # pragma: no cover
    from sqlfluff.cli.formatters import OutputStreamFormatter
    from sqlfluff.core import FluffConfig

# Instantiate the templater logger
templater_logger = logging.getLogger("sqlfluff.templater")


def is_sqlmesh_exception(exception: Optional[BaseException]) -> bool:
    """Check whether this looks like a SQLMesh exception."""
    # None is not a SQLMesh exception.
    if not exception:
        return False
    return exception.__class__.__module__.startswith("sqlmesh")


def _extract_error_detail(exception: BaseException) -> str:
    """Serialise an exception into a string for reuse in other messages."""
    return (
        f"{exception.__class__.__module__}.{exception.__class__.__name__}: {exception}"
    )


T = TypeVar("T")


def handle_sqlmesh_errors(
    error_class: type[Exception], preamble: str
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """A decorator to safely catch SQLMesh exceptions and raise native ones.

    NOTE: This looks and behaves a lot like a context manager, but it's
    important that it is *not* a context manager so that it can effectively
    strip the context from handled exceptions. That isn't possible (as far
    as we've tried) within a context manager.

    SQLMesh exceptions don't pickle nicely, and python exception context tries
    very hard to make sure that the exception context of any new exceptions
    is preserved. This means that if we want to remove the context from any
    exceptions (so they can be pickled), we need to explicitly catch and
    reraise outside of the context of whatever call made them.
    """

    def decorator(wrapped_method: Callable[..., T]) -> Callable[..., T]:
        def wrapped_method_inner(*args, **kwargs) -> T:
            try:
                return wrapped_method(*args, **kwargs)
            except Exception as err:
                if is_sqlmesh_exception(err):
                    _detail = _extract_error_detail(err)
                    raise error_class(preamble + _detail)
                # If it's not a SQLMesh exception, just re-raise as is.
                raise

        return wrapped_method_inner

    return decorator


class SQLMeshTemplater(JinjaTemplater):
    """A templater using SQLMesh."""

    name = "sqlmesh"
    sequential_fail_limit = 3

    def __init__(self, override_context: Optional[dict[str, Any]] = None):
        self.sqlfluff_config = None
        self.formatter = None
        self.project_dir = None
        self.working_dir = os.getcwd()
        super().__init__(override_context=override_context)

    def config_pairs(self):
        """Returns info about the given templater for output by the cli."""
        return [("templater", self.name), ("sqlmesh", self.sqlmesh_version)]

    def _get_project_dir(self):
        """Get the SQLMesh project directory from the configuration.

        Defaults to the working directory.
        """
        config_project_dir = self.sqlfluff_config.get_section(
            (self.templater_selector, self.name, "project_dir")
        )
        env_project_dir = os.getenv("SQLMESH_PROJECT_DIR")
        cwd = os.getcwd()

        templater_logger.info(f"Config project_dir: {config_project_dir}")
        templater_logger.info(f"Env SQLMESH_PROJECT_DIR: {env_project_dir}")
        templater_logger.info(f"Current working dir: {cwd}")

        sqlmesh_project_dir = os.path.abspath(
            os.path.expanduser(config_project_dir or env_project_dir or cwd)
        )

        templater_logger.info(f"Final project_dir: {sqlmesh_project_dir}")

        if not os.path.exists(sqlmesh_project_dir):
            templater_logger.error(
                f"sqlmesh_project_dir: {sqlmesh_project_dir} could not be accessed. "
                "Check it exists."
            )

        return sqlmesh_project_dir

    def _get_config_name(self):
        """Get the SQLMesh config name from the configuration."""
        return self.sqlfluff_config.get_section(
            (self.templater_selector, self.name, "config")
        )

    def _get_gateway_name(self):
        """Get the SQLMesh gateway name from the configuration."""
        return self.sqlfluff_config.get_section(
            (self.templater_selector, self.name, "gateway")
        )

    @staticmethod
    def _find_model_block_end(source: str) -> Optional[int]:
        """Find the end of the MODEL (...); block in a SQLMesh source file.

        Handles nested parentheses (e.g. INCREMENTAL_BY_TIME_RANGE(...))
        and string literals within the MODEL block.

        Returns the index just past the MODEL block including any trailing
        whitespace, or None if no MODEL block is found.
        """
        match = re.match(r"\s*MODEL\s*\(", source, re.IGNORECASE)
        if not match:
            return None

        depth = 0
        in_string = False
        string_char = None
        i = match.start()

        while i < len(source):
            ch = source[i]
            if in_string:
                if ch == string_char:
                    # Handle escaped quotes (e.g. '' inside a single-quoted string)
                    if i + 1 < len(source) and source[i + 1] == string_char:
                        i += 1  # Skip the escaped quote
                    else:
                        in_string = False
            elif ch in ("'", '"'):
                in_string = True
                string_char = ch
            elif ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    # Found the closing paren — consume the trailing semicolon.
                    rest = source[i + 1 :]
                    semi_match = re.match(r"\s*;", rest)
                    if semi_match:
                        end_idx = i + 1 + semi_match.end()
                    else:
                        end_idx = i + 1
                    # Consume trailing whitespace/newlines so the SQL body
                    # starts at real content.
                    while end_idx < len(source) and source[end_idx] in (
                        " ",
                        "\t",
                        "\n",
                        "\r",
                    ):
                        end_idx += 1
                    return end_idx
            i += 1

        return None

    @staticmethod
    def _coalesce_diff_opcodes(
        opcodes: list[tuple[str, int, int, int, int]],
    ) -> list[tuple[str, int, int, int, int]]:
        """Merge diff opcodes so that no ``delete`` or ``insert`` stands alone.

        ``difflib.SequenceMatcher`` can split a single macro expansion like
        ``@if(@DEV, 'dev', 'prod')`` into ``delete + equal('dev') + delete``
        because the literal ``'dev'`` is a common substring. Those isolated
        ``delete`` opcodes would produce zero-length template slices that
        confuse SQLFluff's position-mapping logic.

        This method coalesces every run of non-``equal`` opcodes (and any
        ``equal`` opcodes sandwiched between them) into a single ``replace``.
        """
        if not opcodes:
            return opcodes

        result: list[tuple[str, int, int, int, int]] = []
        i = 0
        while i < len(opcodes):
            tag = opcodes[i][0]
            if tag == "equal":
                result.append(opcodes[i])
                i += 1
                continue

            # Start of a non-equal run — accumulate until we find a
            # standalone equal (one not followed by another non-equal).
            _, run_i1, run_i2, run_j1, run_j2 = opcodes[i]
            i += 1
            while i < len(opcodes):
                next_tag = opcodes[i][0]
                if next_tag != "equal":
                    run_i2 = opcodes[i][2]
                    run_j2 = opcodes[i][4]
                    i += 1
                elif (
                    i + 1 < len(opcodes) and opcodes[i + 1][0] != "equal"
                ):
                    # Equal sandwiched between non-equals — absorb both.
                    run_i2 = opcodes[i + 1][2]
                    run_j2 = opcodes[i + 1][4]
                    i += 2
                else:
                    break

            result.append(("replace", run_i1, run_i2, run_j1, run_j2))

        return result

    def _build_source_mapping(
        self,
        source_str: str,
        rendered_sql: str,
    ) -> tuple[list["RawFileSlice"], list["TemplatedFileSlice"]]:
        """Build accurate source-to-rendered position mappings.

        Splits the source at the MODEL block boundary, then uses
        difflib.SequenceMatcher to align the SQL body with the rendered
        output. Returns (raw_sliced, sliced_file) conforming to the
        TemplatedFile contract.
        """
        from sqlfluff.core.templaters.base import RawFileSlice, TemplatedFileSlice

        raw_sliced: list[RawFileSlice] = []
        sliced_file: list[TemplatedFileSlice] = []

        # Identify the MODEL block boundary.
        model_block_end = self._find_model_block_end(source_str)

        if model_block_end:
            model_block = source_str[:model_block_end]
            sql_body = source_str[model_block_end:]
            source_offset = model_block_end

            # MODEL block is source-only (not present in rendered output).
            raw_sliced.append(
                RawFileSlice(
                    raw=model_block,
                    slice_type="block_start",
                    source_idx=0,
                    block_idx=0,
                )
            )
            sliced_file.append(
                TemplatedFileSlice(
                    slice_type="block_start",
                    source_slice=slice(0, model_block_end),
                    templated_slice=slice(0, 0),
                )
            )
        else:
            sql_body = source_str
            source_offset = 0

        # Use difflib to align the SQL body with the rendered SQL, then
        # coalesce so that no delete/insert produces a zero-length slice.
        block_idx = 1 if model_block_end else 0
        matcher = difflib.SequenceMatcher(
            None, sql_body, rendered_sql, autojunk=False
        )
        opcodes = self._coalesce_diff_opcodes(list(matcher.get_opcodes()))

        for tag, i1, i2, j1, j2 in opcodes:
            src_start = i1 + source_offset
            src_end = i2 + source_offset
            source_text = source_str[src_start:src_end]

            if tag == "equal":
                raw_sliced.append(
                    RawFileSlice(
                        raw=source_text,
                        slice_type="literal",
                        source_idx=src_start,
                        block_idx=block_idx,
                    )
                )
                sliced_file.append(
                    TemplatedFileSlice(
                        slice_type="literal",
                        source_slice=slice(src_start, src_end),
                        templated_slice=slice(j1, j2),
                    )
                )
            else:
                # "replace" (including coalesced delete/insert).
                raw_sliced.append(
                    RawFileSlice(
                        raw=source_text,
                        slice_type="templated",
                        source_idx=src_start,
                        block_idx=block_idx,
                    )
                )
                sliced_file.append(
                    TemplatedFileSlice(
                        slice_type="templated",
                        source_slice=slice(src_start, src_end),
                        templated_slice=slice(j1, j2),
                    )
                )

        return raw_sliced, sliced_file

    @cached_property
    def sqlmesh_version(self):
        """Gets the SQLMesh version."""
        try:
            import sqlmesh

            return sqlmesh.__version__
        except ImportError:
            return "not installed"

    @cached_property
    def sqlmesh_context(self):
        """Loads the SQLMesh context."""
        try:
            from sqlmesh.core.context import Context as SQLMeshContext

            templater_logger.info(
                f"Loading SQLMesh context from project: {self.project_dir}"
            )
        except ImportError as e:
            raise SQLTemplaterError(
                "SQLMesh is not installed. Please install SQLMesh to use the sqlmesh templater: "
                "pip install sqlmesh"
            ) from e

        try:
            context = SQLMeshContext(
                paths=self.project_dir,
                config=self._get_config_name(),
                gateway=self._get_gateway_name(),
            )
            templater_logger.info(f"Successfully created SQLMesh context")
            return context
        except Exception as e:
            raise SQLTemplaterError(
                f"Failed to create SQLMesh context: {e}. "
                "Check your SQLMesh project configuration."
            ) from e

    @large_file_check
    @handle_sqlmesh_errors(
        SQLTemplaterError, "Error received from SQLMesh during project compilation. "
    )
    def process(
        self,
        *,
        fname: str,
        in_str: Optional[str] = None,
        config: Optional["FluffConfig"] = None,
        formatter: Optional["OutputStreamFormatter"] = None,
    ) -> tuple[TemplatedFile, list[SQLTemplaterError]]:
        """Compile a SQLMesh model and return the compiled SQL.

        Args:
            fname: Path to SQLMesh model(s)
            in_str: fname contents using configured encoding
            config: A specific config to use for this
            formatter: The output stream formatter for this run
        """
        # Stash the formatter if provided to use in cached methods.
        self.formatter = formatter
        self.sqlfluff_config = config
        self.project_dir = self._get_project_dir()
        fname_absolute_path = os.path.abspath(fname) if fname != "stdin" else fname

        # NOTE: SQLMesh exceptions are caught and handled safely for pickling by the outer
        # `handle_sqlmesh_errors` decorator.
        return self._unsafe_process(fname_absolute_path, in_str, config)

    def _unsafe_process(self, fname, in_str=None, config=None):
        """Process a file with SQLMesh, without error handling."""
        if in_str is None:
            with open(fname, "r", encoding="utf-8") as f:
                in_str = f.read()

        # Get the model name from the file path
        model_name = self._get_model_name_from_path(fname)

        if not model_name:
            raise SQLTemplaterError(
                f"Could not determine SQLMesh model name for {fname}. "
                f"Ensure the file is in the SQLMesh project directory: {self.project_dir}"
            )

        # Use SQLMesh Context.render() to get the rendered SQL
        templater_logger.debug("Rendering SQLMesh model: %s", model_name)

        try:
            rendered_ast = self.sqlmesh_context.render(
                model_name,
                expand=True,
                no_format=True,
            )
            rendered_sql = (
                rendered_ast.sql()
                if hasattr(rendered_ast, "sql")
                else str(rendered_ast)
            )
            templater_logger.debug("Rendered SQL: %r", rendered_sql)

        except Exception as e:
            raise SQLTemplaterError(
                f"SQLMesh rendering failed for model '{model_name}': {e}. "
                "Check your SQLMesh model syntax and project configuration."
            ) from e

        # Build accurate source-to-rendered position mappings.
        raw_sliced, sliced_file = self._build_source_mapping(in_str, rendered_sql)

        return (
            TemplatedFile(
                source_str=in_str,
                templated_str=rendered_sql,
                fname=fname,
                sliced_file=sliced_file,
                raw_sliced=raw_sliced,
            ),
            [],
        )

    def _get_model_name_from_path(self, fname):
        """Extract the SQLMesh model name from a file path."""
        try:
            templater_logger.info(f"Extracting model name from: {fname}")
            templater_logger.info(f"Project directory: {self.project_dir}")

            # Convert absolute path to relative path from project directory
            rel_path = os.path.relpath(fname, self.project_dir)
            templater_logger.info(f"Relative path: {rel_path}")

            # Check if path goes outside project (starts with ..)
            if rel_path.startswith(".."):
                templater_logger.info(f"Path outside project, returning None")
                return None

            # Remove models/ prefix if present
            if rel_path.startswith("models/"):
                rel_path = rel_path[7:]  # Remove "models/"
                templater_logger.info(f"After removing models/ prefix: {rel_path}")

            # Remove file extension
            model_name = os.path.splitext(rel_path)[0]
            templater_logger.info(f"After removing extension: {model_name}")

            # Replace path separators with dots for SQLMesh model naming
            model_name = model_name.replace(os.path.sep, ".")
            templater_logger.info(f"Final model name: {model_name}")

            return model_name

        except Exception as e:
            templater_logger.error(f"Failed to extract model name from {fname}: {e}")
            return None

