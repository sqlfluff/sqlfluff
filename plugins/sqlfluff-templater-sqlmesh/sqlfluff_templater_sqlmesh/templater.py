"""Defines the SQLMesh templater.

NOTE: The SQLMesh python package adds a significant overhead to import.
This module is also loaded on every run of SQLFluff regardless of
whether the SQLMesh templater is selected in the configuration.

The templater is however only _instantiated_ when selected, and as
such, all imports of the SQLMesh libraries are contained within the
SQLMeshTemplater class and so are only imported when necessary.
"""

import logging
import os
import os.path
import re
from functools import cached_property
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Optional,
    TypeVar,
)

from sqlfluff.core.errors import SQLTemplaterError
from sqlfluff.core.templaters.base import (
    RawFileSlice,
    TemplatedFile,
    TemplatedFileSlice,
    large_file_check,
)
from sqlfluff.core.templaters.jinja import JinjaTemplater

if TYPE_CHECKING:  # pragma: no cover
    from sqlfluff.cli.formatters import OutputStreamFormatter
    from sqlfluff.core import FluffConfig

# Instantiate the templater logger
templater_logger = logging.getLogger("sqlfluff.templater")

ERROR_PREAMBLE = "Error received from SQLMesh during project compilation. "

# A source region description: (slice_type, src_start, src_end, tmpl_start, tmpl_end).
Region = tuple[str, int, int, int, int]


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
    strip the context from handled exceptions. That is not reliably possible
    within a context manager for this use case.

    SQLMesh exceptions don't pickle nicely, and python exception context tries
    very hard to make sure that the exception context of any new exceptions
    is preserved. This means that if we want to remove the context from any
    exceptions (so they can be pickled), we need to explicitly catch and
    reraise outside of the context of whatever call made them.
    """

    def decorator(wrapped_method: Callable[..., T]) -> Callable[..., T]:
        def wrapped_method_inner(*args, **kwargs) -> T:
            new_error: Optional[Exception] = None
            try:
                return wrapped_method(*args, **kwargs)
            except Exception as err:
                # If this is a *direct* SQLMesh exception, convert it.
                if is_sqlmesh_exception(err):
                    _detail = _extract_error_detail(err)
                    new_error = error_class(preamble + _detail)

                # If this is a SQLTemplaterError that was raised "from" a
                # SQLMesh exception, convert based on the underlying cause.
                elif isinstance(err, SQLTemplaterError) and is_sqlmesh_exception(
                    err.__cause__
                ):
                    _detail = _extract_error_detail(err.__cause__)
                    new_error = error_class(preamble + _detail)

                # Otherwise, strip any SQLMesh exceptions from the context so
                # the resulting exception can be safely pickled. Rather than
                # mutating the caught exception in place (which can lead to
                # unexpected behaviour), re-raise as a fresh instance of the
                # same type so no SQLMesh context is attached.
                elif is_sqlmesh_exception(err.__cause__) or is_sqlmesh_exception(
                    err.__context__
                ):
                    new_error = type(err)(*err.args)

                # If it's not a SQLMesh exception (or has been cleaned), just
                # re-raise as is.
                else:
                    raise

            assert new_error is not None
            raise new_error from None

        return wrapped_method_inner

    return decorator


class SQLMeshTemplater(JinjaTemplater):
    """A templater using SQLMesh.

    SQLMesh renders models through SQLGlot (AST expansion + re-serialisation)
    rather than by Jinja-style substitution, so the rendered SQL has no
    literal-slice relationship to the source. Rather than reconstruct a map
    from a text diff (which classifies almost everything as "templated" and
    hides violations), the templater dispatches across four tiers, cheapest
    first, so that as much of the file as possible is mapped as real,
    lintable ``literal`` SQL:

    * **T0** - split the ``MODEL (...)`` header (source-only) from the SQL body.
    * **T1** - a body with no ``@`` macros is linted verbatim, with exact
      positions and no SQLMesh context loaded at all.
    * **T2** - a body whose macros all resolve to a single inline expression is
      substituted into the *verbatim* source, so non-macro SQL keeps exact
      positions (this mirrors how the Jinja templater traces substitutions).
    * **T3** - anything else (structural or unresolved macros) is rendered whole
      and mapped as one coarse ``templated`` region. It is suppressed by
      default but, crucially, never collapses positions to the start of file.
    """

    name = "sqlmesh"
    templates_in_worker = False
    # Inherited from JinjaTemplater: max consecutive templating failures before abort.
    sequential_fail_limit = 3

    def __init__(self, override_context: Optional[dict[str, Any]] = None):
        self.sqlfluff_config = None
        self.formatter = None
        self.project_dir = None
        self._context_key: Optional[tuple[Any, Any, Any]] = None
        super().__init__(override_context=override_context)

    def config_pairs(self) -> list[tuple[str, str]]:
        """Returns info about the given templater for output by the cli."""
        return [("templater", self.name), ("sqlmesh", self.sqlmesh_version)]

    def _clear_cached_sqlmesh_context(self) -> None:
        """Clear cached SQLMesh context when runtime configuration changes."""
        self.__dict__.pop("sqlmesh_context", None)

    def _sqlmesh_context_key(
        self, config: Optional["FluffConfig"]
    ) -> tuple[Any, Any, Any]:
        """Inputs that determine the SQLMesh context: (project_dir, config, gateway).

        The context depends only on these, not on the identity of the
        ``FluffConfig`` object. SQLFluff hands each file in a directory lint its
        own child config, so keying the cache on object identity would rebuild
        the (expensive) SQLMesh context for every file.
        """
        project_dir = self._get_project_dir(config)
        cfg_name = gateway = None
        if config is not None:
            cfg_name = config.get_section(
                (self.templater_selector, self.name, "config")
            )
            gateway = config.get_section(
                (self.templater_selector, self.name, "gateway")
            )
        return (project_dir, cfg_name, gateway)

    def _update_runtime_context(
        self,
        *,
        config: Optional["FluffConfig"],
        formatter: Optional["OutputStreamFormatter"],
    ) -> None:
        """Update runtime state for this templating request.

        The cached SQLMesh context is only rebuilt when the inputs that define
        it (project dir, config name, gateway) actually change — not merely
        because SQLFluff passed a different (per-file child) config object.
        """
        new_key = self._sqlmesh_context_key(config)
        if new_key != self._context_key:
            self._clear_cached_sqlmesh_context()
            self._context_key = new_key
        self.sqlfluff_config = config
        self.formatter = formatter
        self.project_dir = new_key[0]

    def _get_project_dir(self, config: Optional["FluffConfig"] = None) -> str:
        """Get the SQLMesh project directory from the configuration.

        Defaults to the working directory.
        """
        resolved_config = config or self.sqlfluff_config
        config_project_dir = None
        if resolved_config is not None:
            config_project_dir = resolved_config.get_section(
                (self.templater_selector, self.name, "project_dir")
            )
        env_project_dir = os.getenv("SQLMESH_PROJECT_DIR")
        cwd = os.getcwd()

        sqlmesh_project_dir = os.path.abspath(
            os.path.expanduser(config_project_dir or env_project_dir or cwd)
        )
        templater_logger.debug(
            "Resolved SQLMesh project_dir to %s (config=%r, env=%r, cwd=%r)",
            sqlmesh_project_dir,
            config_project_dir,
            env_project_dir,
            cwd,
        )

        if not os.path.exists(sqlmesh_project_dir):
            templater_logger.error(
                f"sqlmesh_project_dir: {sqlmesh_project_dir} could not be accessed. "
                "Check it exists."
            )

        return sqlmesh_project_dir

    def _get_config_name(self) -> Optional[str]:
        """Get the SQLMesh config name from the configuration."""
        if self.sqlfluff_config is None:
            return None
        return self.sqlfluff_config.get_section(
            (self.templater_selector, self.name, "config")
        )

    def _get_gateway_name(self) -> Optional[str]:
        """Get the SQLMesh gateway name from the configuration."""
        if self.sqlfluff_config is None:
            return None
        return self.sqlfluff_config.get_section(
            (self.templater_selector, self.name, "gateway")
        )

    def _get_dialect(self) -> Optional[str]:
        """Get the configured SQLFluff dialect (used to seed SQLGlot parsing)."""
        if self.sqlfluff_config is None:
            return None
        try:
            return self.sqlfluff_config.get("dialect")
        except Exception:  # pragma: no cover - defensive
            return None

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
        if self.project_dir is None:
            raise SQLTemplaterError(
                "SQLMesh project_dir is not set. Call process() with a valid config first."
            )
        try:
            from sqlmesh.core.context import Context as SQLMeshContext

            templater_logger.info(
                "Loading SQLMesh context from project: %s", self.project_dir
            )
        except ImportError:
            raise SQLTemplaterError(
                "SQLMesh is not installed. Please install SQLMesh to use the sqlmesh templater: "
                "pip install sqlmesh"
            )

        try:
            context = SQLMeshContext(
                paths=self.project_dir,
                config=self._get_config_name(),
                gateway=self._get_gateway_name(),
            )
            templater_logger.info("Successfully created SQLMesh context")
            return context
        except Exception as err:
            if is_sqlmesh_exception(err) or isinstance(
                err, (OSError, TypeError, ValueError)
            ):
                raise SQLTemplaterError(
                    f"Failed to create SQLMesh context: {err}. "
                    "Check your SQLMesh project configuration."
                ) from None
            raise

    @large_file_check
    @handle_sqlmesh_errors(SQLTemplaterError, ERROR_PREAMBLE)
    def process(
        self,
        *,
        fname: str,
        in_str: Optional[str] = None,
        config: Optional["FluffConfig"] = None,
        formatter: Optional["OutputStreamFormatter"] = None,
    ) -> tuple[TemplatedFile, list[SQLTemplaterError]]:
        """Compile a SQLMesh model and return the compiled SQL.

        Side effects:
            Updates cached runtime state used to initialize the SQLMesh context.

        Args:
            fname: Path to SQLMesh model(s)
            in_str: fname contents using configured encoding
            config: A specific config to use for this
            formatter: The output stream formatter for this run
        """
        self._update_runtime_context(config=config, formatter=formatter)
        fname_absolute_path = os.path.abspath(fname) if fname != "stdin" else fname

        # NOTE: SQLMesh exceptions are caught and handled safely for pickling by the outer
        # `handle_sqlmesh_errors` decorator.
        return self._unsafe_process(fname_absolute_path, in_str, config)

    def _unsafe_process(
        self,
        fname: str,
        in_str: Optional[str] = None,
        config: Optional["FluffConfig"] = None,
    ) -> tuple[TemplatedFile, list[SQLTemplaterError]]:
        """Process a file with SQLMesh, without error handling.

        Implements the T0-T3 dispatch described on the class docstring.
        """
        if in_str is None:
            with open(fname, "r", encoding="utf-8") as f:
                in_str = f.read()

        # T0: separate the MODEL(...) header (source-only) from the SQL body.
        header_end = self._find_model_block_end(in_str)
        body = in_str[header_end or 0 :]

        # T1: a body with no macros is linted verbatim. This needs no SQLMesh
        # context at all, so plain-SQL models (and stdin buffers) "just work".
        macro_spans = self._find_macro_spans(body)
        if not macro_spans:
            return self._passthrough_file(fname, in_str, header_end)

        # Macros are present, so we need the model to resolve them against.
        model = self._resolve_model(fname, self._get_model_name_from_path(fname))
        if model is None:
            # A non-model file (macros/, tests/, ...) that happens to contain an
            # '@'. There is nothing to render it against, so pass it through.
            templater_logger.debug(
                "No SQLMesh model registered for %s; passing through literally.",
                fname,
            )
            return self._passthrough_file(fname, in_str, header_end)

        # Prefer authoritative segmentation: SQLMesh has already parsed this
        # model, so its statements tell us exactly where the query is. This is
        # more robust than the regex header split and, crucially, keeps
        # non-query statements (the MODEL block, ``@DEF`` pre-statements, post
        # statements) out of the SQL SQLFluff parses. Only the query is linted.
        query_span = self._locate_query_span(in_str, model)
        if query_span is not None:
            return self._build_query_file(fname, in_str, model, query_span)

        # Fallback (query text not locatable): use the regex header split and
        # treat the whole body as the query.
        templater_logger.debug(
            "Statement segmentation unavailable for %s; using regex body split.",
            fname,
        )
        replacements = self._resolve_macro_spans(model, body, macro_spans)
        if replacements is not None:
            return self._substitute_file(
                fname, in_str, header_end, macro_spans, replacements
            )
        rendered_sql = self._render_body(model)
        return self._coarse_templated_file(fname, in_str, header_end, rendered_sql)

    def _locate_query_span(
        self, source_str: str, model: Any
    ) -> Optional[tuple[int, int]]:
        """Locate the model's query in the source via SQLMesh's parsed statements.

        Returns ``(start, end)`` source offsets covering the query and any
        trailing whitespace up to the next statement (so file-level rules such
        as the final-newline check still apply), or ``None`` if the file can't
        be segmented this way (the caller then falls back to the regex split).

        Only reachable in tiers 2/3, where the model has already parsed
        successfully — so this never has to cope with a broken file.
        """
        query = getattr(model, "query", None)
        query_meta = getattr(query, "meta", None) if query is not None else None
        if not query_meta or not query_meta.get("sql"):
            return None

        pre = list(getattr(model, "pre_statements", []) or [])
        post = list(getattr(model, "post_statements", []) or [])
        ordered = [*pre, query, *post]

        # Each statement's ``meta['sql']`` is its verbatim source text; recover
        # offsets by locating them in order.
        cursor = 0
        located: list[tuple[int, int, bool]] = []
        for node in ordered:
            meta = getattr(node, "meta", None)
            text = meta.get("sql") if meta else None
            if not text:
                return None
            idx = source_str.find(text, cursor)
            if idx < 0:
                return None
            end = idx + len(text)
            located.append((idx, end, node is query))
            cursor = end

        for i, (start, _end, is_query) in enumerate(located):
            if is_query:
                next_start = (
                    located[i + 1][0] if i + 1 < len(located) else len(source_str)
                )
                return (start, next_start)
        return None

    def _build_query_file(
        self, fname: str, source_str: str, model: Any, span: tuple[int, int]
    ) -> tuple[TemplatedFile, list[SQLTemplaterError]]:
        """Map a segmented file: only the query span is linted.

        Everything before the query (MODEL header, ``@DEF`` pre-statements) and
        after it (post statements) is emitted as a source-only, zero-length
        templated region. The query itself is handled per tier: verbatim when
        it has no macros, macro-substituted when they all resolve inline
        (tier 2), or coarse-rendered otherwise (tier 3).
        """
        qs, qe = span
        qtext = source_str[qs:qe]
        macro_spans = self._find_macro_spans(qtext)

        if not macro_spans:
            query_regions: list[Region] = [("literal", qs, qe, 0, len(qtext))]
            templated = qtext
        else:
            replacements = self._resolve_macro_spans(model, qtext, macro_spans)
            if replacements is not None:
                templater_logger.debug(
                    "Substituting %d macro(s) in the query of %s (tier 2).",
                    len(macro_spans),
                    fname,
                )
                query_regions, templated = self._substitute_regions(
                    source_str, qs, qe, macro_spans, replacements
                )
            else:
                templater_logger.debug(
                    "Coarse templated mapping for the query of %s (tier 3).", fname
                )
                templated = self._render_body(model)
                query_regions = [("templated", qs, qe, 0, len(templated))]

        regions: list[Region] = []
        if qs > 0:
            regions.append(("templated", 0, qs, 0, 0))
        regions.extend(query_regions)
        if qe < len(source_str):
            regions.append(
                ("templated", qe, len(source_str), len(templated), len(templated))
            )
        return self._make_file(fname, source_str, templated, regions)

    # -- Model resolution -----------------------------------------------------

    def _resolve_model(self, fname: str, model_name: Optional[str]) -> Any:
        """Resolve the SQLMesh model for a file, or None if it isn't a model.

        Resolution prefers matching the file path against the loaded models so
        that non-model files (``macros/``, ``tests/``, ``seeds/``, ``audits/``,
        ...) and models whose declared name differs from their path are handled
        correctly. A name-based lookup is used as a fallback for cases where the
        path does not map directly to a registered model file.
        """
        context = self.sqlmesh_context

        try:
            target = os.path.realpath(fname)
        except (OSError, ValueError):
            target = None

        if target is not None:
            for model in context.models.values():
                model_path = getattr(model, "_path", None)
                if not model_path:
                    continue
                try:
                    if os.path.realpath(str(model_path)) == target:
                        return model
                except (OSError, ValueError):
                    continue

        if model_name:
            return context.get_model(model_name, raise_if_missing=False)

        return None

    def _get_model_name_from_path(self, fname: str) -> Optional[str]:
        """Extract the SQLMesh model name from a file path."""
        if self.project_dir is None:
            return None
        try:
            file_path = Path(fname)
            rel_path = file_path.relative_to(self.project_dir)
        except ValueError:
            templater_logger.debug(
                "Skipping SQLMesh model resolution for path outside project: %s",
                fname,
            )
            return None

        try:
            # Remove models/ or audits/ prefix if present.
            for prefix in ("models", "audits"):
                try:
                    rel_path = rel_path.relative_to(prefix)
                    break
                except ValueError:
                    continue

            # Remove file extension and convert separators to dots.
            model_name = ".".join(rel_path.with_suffix("").parts)
            templater_logger.debug(
                "Resolved SQLMesh model %s from path %s", model_name, fname
            )
            return model_name

        except (OSError, ValueError) as err:
            templater_logger.error(
                "Failed to extract model name from %s: %s", fname, err
            )
            return None

    # -- T0: MODEL header detection -------------------------------------------

    @staticmethod
    def _skip_leading_trivia(source: str) -> int:
        """Return the index of the first non-whitespace, non-comment char."""
        i, n = 0, len(source)
        while i < n:
            ch = source[i]
            if ch in " \t\r\n":
                i += 1
            elif ch == "-" and source[i + 1 : i + 2] == "-":
                nl = source.find("\n", i)
                i = n if nl == -1 else nl + 1
            elif ch == "/" and source[i + 1 : i + 2] == "*":
                end = source.find("*/", i + 2)
                i = n if end == -1 else end + 2
            else:
                break
        return i

    @staticmethod
    def _find_model_block_end(source: str) -> Optional[int]:
        """Find the end of the MODEL (...); block in a SQLMesh source file.

        Handles leading comments before the ``MODEL`` DDL (SQLMesh allows them),
        nested parentheses (e.g. INCREMENTAL_BY_TIME_RANGE(...)) and string
        literals within the MODEL block.

        Returns the index just past the MODEL block including any trailing
        whitespace, or None if no MODEL block is found.
        """
        start = SQLMeshTemplater._skip_leading_trivia(source)
        if not re.match(r"MODEL\s*\(", source[start:], re.IGNORECASE):
            return None

        depth = 0
        in_string = False
        string_char = None
        i = start

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

    # -- Macro scanning -------------------------------------------------------

    @staticmethod
    def _skip_string(s: str, i: int) -> int:
        """Return the index just past a string literal starting at ``i``."""
        quote = s[i]
        i += 1
        n = len(s)
        while i < n:
            if s[i] == quote:
                if i + 1 < n and s[i + 1] == quote:  # '' / "" escape
                    i += 2
                    continue
                return i + 1
            i += 1
        return n

    @staticmethod
    def _skip_balanced_parens(s: str, i: int) -> int:
        """Return the index past the ``)`` matching the ``(`` at ``i``."""
        depth = 0
        n = len(s)
        while i < n:
            c = s[i]
            if c in ("'", '"'):
                i = SQLMeshTemplater._skip_string(s, i)
                continue
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0:
                    return i + 1
            i += 1
        return n

    @staticmethod
    def _find_macro_spans(body: str) -> list[tuple[int, int]]:
        """Locate SQLMesh ``@macro`` spans in a SQL body.

        Skips string literals and comments so an ``@`` inside a string (e.g. an
        email literal) is not mistaken for a macro. Recognises ``@name``,
        ``@name(...)`` and ``@{ ... }``.
        """
        spans: list[tuple[int, int]] = []
        i, n = 0, len(body)
        while i < n:
            ch = body[i]
            if ch in ("'", '"'):
                i = SQLMeshTemplater._skip_string(body, i)
            elif ch == "-" and body[i + 1 : i + 2] == "-":
                nl = body.find("\n", i)
                i = n if nl == -1 else nl
            elif ch == "/" and body[i + 1 : i + 2] == "*":
                end = body.find("*/", i + 2)
                i = n if end == -1 else end + 2
            elif (
                ch == "@"
                and i + 1 < n
                and (body[i + 1] == "{" or body[i + 1].isalpha() or body[i + 1] == "_")
            ):
                start = i
                if body[i + 1] == "{":
                    close = body.find("}", i + 2)
                    i = n if close == -1 else close + 1
                else:
                    j = i + 1
                    while j < n and (body[j].isalnum() or body[j] == "_"):
                        j += 1
                    if j < n and body[j] == "(":  # macro call: consume args
                        j = SQLMeshTemplater._skip_balanced_parens(body, j)
                    i = j
                spans.append((start, i))
            else:
                i += 1
        return spans

    # -- T2: positioned macro substitution ------------------------------------

    def _build_macro_evaluator(self, model: Any):
        """Build a MacroEvaluator seeded the way SQLMesh seeds it for a model.

        The model's ``python_env`` carries user-defined variables (via
        ``__sqlmesh__vars__``) and macro definitions; ``date_dict`` supplies the
        temporal macro variables (``@start_ds``, ``@end_ds``, ...). The exact
        time window is irrelevant to linting — only that the tokens resolve to
        literals so the SQL parses and positions map.
        """
        from sqlmesh.core.macros import MacroEvaluator
        from sqlmesh.utils.date import date_dict, to_datetime
        from sqlmesh.utils.metaprogramming import prepare_env

        evaluator = MacroEvaluator(dialect=self._get_dialect() or "")
        prepare_env(dict(getattr(model, "python_env", {}) or {}), evaluator.locals)
        anchor = to_datetime(getattr(model, "start", None) or "1970-01-01")
        evaluator.locals.update(date_dict(anchor, anchor, anchor))
        return evaluator

    def _resolve_macro_spans(
        self, model: Any, body: str, spans: list[tuple[int, int]]
    ) -> Optional[list[str]]:
        """Resolve each macro span to a single inline SQL string.

        Returns replacements aligned with ``spans``, or ``None`` if any span is
        structural (expands to multiple expressions, e.g. ``@EACH``) or cannot
        be resolved — in which case the caller safely defers to tier 3.
        """
        import sqlglot

        try:
            evaluator = self._build_macro_evaluator(model)
        except Exception as err:  # pragma: no cover - defensive
            templater_logger.debug("Could not build a SQLMesh macro evaluator: %s", err)
            return None

        dialect = self._get_dialect()
        replacements: list[str] = []
        for start, end in spans:
            text = body[start:end]
            parsed = None
            for candidate in (dialect, None):
                try:
                    parsed = sqlglot.parse_one(text, dialect=candidate)
                    break
                except Exception:
                    continue
            if parsed is None:
                templater_logger.debug("Macro %r could not be parsed.", text)
                return None
            try:
                out = evaluator.transform(parsed)
            except Exception as err:
                templater_logger.debug("Macro %r did not resolve inline: %s", text, err)
                return None
            # A list/tuple means a structural macro that splices multiple
            # expressions into its parent — not a single-span substitution.
            if out is None or isinstance(out, (list, tuple)) or not hasattr(out, "sql"):
                return None
            replacements.append(out.sql(dialect=dialect) if dialect else out.sql())
        return replacements

    # -- T3: coarse fallback rendering ----------------------------------------

    def _render_body(self, model: Any) -> str:
        """Render a model's own query to a SQL string.

        ``expand=False`` avoids inlining upstream models, whose SQL has no
        source location in this file.
        """
        try:
            rendered = self.sqlmesh_context.render(model, expand=False, no_format=True)
        except Exception as err:
            if is_sqlmesh_exception(err) or isinstance(
                err, (AttributeError, TypeError, ValueError)
            ):
                raise SQLTemplaterError(
                    f"SQLMesh rendering failed for model '{model.name}': {err}. "
                    "Check your SQLMesh model syntax and project configuration."
                ) from None
            raise
        return rendered.sql() if hasattr(rendered, "sql") else str(rendered)

    # -- TemplatedFile assembly -----------------------------------------------

    def _make_file(
        self,
        fname: str,
        source_str: str,
        templated_str: str,
        regions: list[Region],
    ) -> tuple[TemplatedFile, list[SQLTemplaterError]]:
        """Assemble a TemplatedFile from contiguous source/templated regions."""
        raw_sliced: list[RawFileSlice] = []
        sliced_file: list[TemplatedFileSlice] = []
        for stype, s0, s1, t0, t1 in regions:
            raw_sliced.append(
                RawFileSlice(
                    raw=source_str[s0:s1],
                    slice_type=stype,
                    source_idx=s0,
                    block_idx=0,
                )
            )
            sliced_file.append(
                TemplatedFileSlice(
                    slice_type=stype,
                    source_slice=slice(s0, s1),
                    templated_slice=slice(t0, t1),
                )
            )
        return (
            TemplatedFile(
                source_str=source_str,
                templated_str=templated_str,
                fname=fname,
                sliced_file=sliced_file,
                raw_sliced=raw_sliced,
            ),
            [],
        )

    def _passthrough_file(
        self, fname: str, source_str: str, header_end: Optional[int]
    ) -> tuple[TemplatedFile, list[SQLTemplaterError]]:
        """Tiers 0/1: MODEL header (if any) → zero-length templated; body → literal.

        The templated string is the body only, so the DDL header is never parsed
        as SQL and the body keeps exact source positions.
        """
        body_start = header_end or 0
        body = source_str[body_start:]
        regions: list[Region] = []
        if header_end:
            regions.append(("templated", 0, body_start, 0, 0))
        regions.append(("literal", body_start, len(source_str), 0, len(body)))
        return self._make_file(fname, source_str, body, regions)

    def _substitute_regions(
        self,
        source_str: str,
        start: int,
        end: int,
        spans: list[tuple[int, int]],
        replacements: list[str],
    ) -> tuple[list[Region], str]:
        """Splice replacements into ``source_str[start:end]``.

        ``spans`` are offsets relative to that slice. Returns the regions
        (with absolute source offsets) and the resulting templated string.
        Literal runs between macros keep their exact source positions.
        """
        segment = source_str[start:end]
        regions: list[Region] = []
        parts: list[str] = []
        t = 0  # running offset within the templated string
        cursor = 0  # running offset within the segment
        for (s, e), text in zip(spans, replacements):
            if s > cursor:  # literal run preceding this macro
                lit = segment[cursor:s]
                regions.append(("literal", start + cursor, start + s, t, t + len(lit)))
                parts.append(lit)
                t += len(lit)
            regions.append(("templated", start + s, start + e, t, t + len(text)))
            parts.append(text)
            t += len(text)
            cursor = e
        if cursor < len(segment):  # trailing literal
            lit = segment[cursor:]
            regions.append(("literal", start + cursor, end, t, t + len(lit)))
            parts.append(lit)
        return regions, "".join(parts)

    def _substitute_file(
        self,
        fname: str,
        source_str: str,
        header_end: Optional[int],
        spans: list[tuple[int, int]],
        replacements: list[str],
    ) -> tuple[TemplatedFile, list[SQLTemplaterError]]:
        """Tier 2: splice resolved macro text into the verbatim source body."""
        body_start = header_end or 0
        regions, templated = self._substitute_regions(
            source_str, body_start, len(source_str), spans, replacements
        )
        if header_end:
            regions.insert(0, ("templated", 0, body_start, 0, 0))
        return self._make_file(fname, source_str, templated, regions)

    def _coarse_templated_file(
        self,
        fname: str,
        source_str: str,
        header_end: Optional[int],
        rendered_sql: str,
    ) -> tuple[TemplatedFile, list[SQLTemplaterError]]:
        """Tier 3: whole body → one templated region. Safe, never collapses."""
        body_start = header_end or 0
        regions: list[Region] = []
        if header_end:
            regions.append(("templated", 0, body_start, 0, 0))
        regions.append(("templated", body_start, len(source_str), 0, len(rendered_sql)))
        return self._make_file(fname, source_str, rendered_sql, regions)

    def _create_literal_templated_file(
        self,
        fname: str,
        templated_content: str,
        source_content: Optional[str] = None,
        *,
        was_rendered: bool = False,
    ) -> tuple[TemplatedFile, list[SQLTemplaterError]]:
        """Create a TemplatedFile with literal (no templating) content."""
        # Use source_content if provided, otherwise use templated_content for both
        actual_source = (
            source_content if source_content is not None else templated_content
        )

        _slice_type = "templated" if was_rendered else "literal"

        sliced_file = [
            TemplatedFileSlice(
                slice_type=_slice_type,
                source_slice=slice(0, len(actual_source)),
                templated_slice=slice(0, len(templated_content)),
            )
        ]

        raw_sliced = [
            RawFileSlice(
                raw=actual_source,
                slice_type=_slice_type,
                source_idx=0,
                block_idx=0,
            )
        ]

        return (
            TemplatedFile(
                source_str=actual_source,
                templated_str=templated_content,
                fname=fname,
                sliced_file=sliced_file,
                raw_sliced=raw_sliced,
            ),
            [],
        )
