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
from functools import cached_property
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Optional,
    TypeVar,
)

from sqlfluff.core.errors import SQLFluffSkipFile, SQLTemplaterError
from sqlfluff.core.templaters.base import TemplatedFile, large_file_check
from sqlfluff.core.templaters.jinja import JinjaTemplater

if TYPE_CHECKING:  # pragma: no cover
    from sqlfluff.cli.formatters import OutputStreamFormatter
    from sqlfluff.core import FluffConfig

# Instantiate the templater logger
templater_logger = logging.getLogger("sqlfluff.templater")

ERROR_PREAMBLE = "Error received from SQLMesh during project compilation. "


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
    """A templater using SQLMesh."""

    name = "sqlmesh"
    templates_in_worker = False
    # Inherited from JinjaTemplater: max consecutive templating failures before abort.
    sequential_fail_limit = 3

    def __init__(self, override_context: Optional[dict[str, Any]] = None):
        self.sqlfluff_config = None
        self.formatter = None
        self.project_dir = None
        self.working_dir = os.getcwd()
        super().__init__(override_context=override_context)

    def config_pairs(self) -> list[tuple[str, str]]:
        """Returns info about the given templater for output by the cli."""
        return [("templater", self.name), ("sqlmesh", self.sqlmesh_version)]

    def _clear_cached_sqlmesh_context(self) -> None:
        """Clear cached SQLMesh context when runtime configuration changes."""
        self.__dict__.pop("sqlmesh_context", None)

    def _update_runtime_context(
        self,
        *,
        config: Optional["FluffConfig"],
        formatter: Optional["OutputStreamFormatter"],
    ) -> None:
        """Update runtime state for this templating request."""
        project_dir = self._get_project_dir(config)
        runtime_changed = (
            config is not self.sqlfluff_config
            or formatter is not self.formatter
            or project_dir != self.project_dir
        )
        self.sqlfluff_config = config
        self.formatter = formatter
        if project_dir != self.project_dir:
            self.project_dir = project_dir
        if runtime_changed:
            self._clear_cached_sqlmesh_context()

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
        """Process a file with SQLMesh, without error handling."""
        if in_str is None:
            with open(fname, "r", encoding="utf-8") as f:
                in_str = f.read()

        # Get the model name from the file path
        model_name = self._get_model_name_from_path(fname)

        if not model_name:
            templater_logger.debug(
                "Could not determine SQLMesh model name for %s. "
                "Falling back to literal templating (no SQLMesh rendering).",
                fname,
            )
            return self._create_literal_templated_file(
                fname, in_str, source_content=in_str
            )

        # Use SQLMesh Context.render() to get the rendered SQL
        templater_logger.debug("Rendering SQLMesh model: %s", model_name)

        try:
            rendered_ast = self.sqlmesh_context.render(
                model_name,
                expand=True,  # Expand all macros and dependencies
                no_format=True,  # Don't format, let SQLFluff handle that
            )
            # Convert SQLGlot AST to SQL string
            rendered_sql = (
                rendered_ast.sql()
                if hasattr(rendered_ast, "sql")
                else str(rendered_ast)
            )
            templater_logger.debug(
                "Successfully rendered SQLMesh model: %s", model_name
            )
            templater_logger.debug("Rendered SQL: %s", rendered_sql)
        except Exception as err:
            if is_sqlmesh_exception(err) or isinstance(
                err, (AttributeError, TypeError, ValueError)
            ):
                raise SQLTemplaterError(
                    f"SQLMesh rendering failed for model '{model_name}': {err}. "
                    "Check your SQLMesh model syntax and project configuration."
                ) from None
            raise

        # Create slice mapping using Jinja templater's slice_file method
        # This handles the complex position mapping for fix suggestions
        def render_func(_: str) -> str:
            """Render function that returns the SQLMesh-rendered SQL."""
            return rendered_sql

        try:
            raw_sliced, sliced_file, templated_sql = self.slice_file(
                in_str,
                render_func=render_func,
                config=config,
            )
            templated_file = TemplatedFile(
                source_str=in_str,
                templated_str=templated_sql,
                fname=fname,
                sliced_file=sliced_file,
                raw_sliced=raw_sliced,
            )
            return templated_file, []
        except (SQLFluffSkipFile, SQLTemplaterError, ValueError) as err:
            templater_logger.warning(
                "Failed to create slice mapping for %s: %s. Using literal mapping.",
                fname,
                err,
            )
            return self._create_literal_templated_file(
                fname,
                rendered_sql,
                source_content=in_str,
                was_rendered=True,
            )

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

    def _create_literal_templated_file(
        self,
        fname: str,
        templated_content: str,
        source_content: Optional[str] = None,
        *,
        was_rendered: bool = False,
    ) -> tuple[TemplatedFile, list[SQLTemplaterError]]:
        """Create a TemplatedFile with literal (no templating) content."""
        from sqlfluff.core.templaters.base import RawFileSlice
        from sqlfluff.core.templaters.slicers.tracer import TemplatedFileSlice

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
