"""Consume the experimental render-trace API proposed in dbt-labs/dbt#16870."""

from __future__ import annotations

import json
import logging
import re
import subprocess
import sys
import tempfile
from importlib import metadata
from pathlib import Path
from typing import TYPE_CHECKING, Any

from packaging.version import Version

from sqlfluff.core.errors import SQLFluffUserError, SQLTemplaterError
from sqlfluff.core.templaters.base import RawTemplater, TemplatedFile, large_file_check
from sqlfluff_templater_dbt2.artifacts import RenderArtifacts
from sqlfluff_templater_dbt2.trace import normalize_newlines, trace_to_templated_file

if TYPE_CHECKING:
    from sqlfluff.core import FluffConfig
    from sqlfluff.core.formatter import FormatterInterface

templater_logger = logging.getLogger("sqlfluff.templater")

TRACE_PR = "https://github.com/dbt-labs/dbt/pull/16870"
LEGACY_DBT = (
    "The dbt2 templater requires the Rust dbt v2 runtime. For legacy Python "
    "dbt Core 1.x, install sqlfluff-templater-dbt and set templater = dbt."
)


class Dbt2Templater(RawTemplater):
    """Render through dbt itself and translate its exported execution provenance."""

    name = "dbt2"
    templates_in_worker = False

    def __init__(self, override_context: dict[str, Any] | None = None) -> None:
        super().__init__(override_context=override_context)
        self._batch: RenderArtifacts | None = None
        self._batch_key: str | None = None
        self._batch_paths: set[Path] = set()
        self._batch_error: SQLTemplaterError | SQLFluffUserError | None = None

    @staticmethod
    def _settings(config: FluffConfig | None) -> dict[str, Any]:
        return dict(config.get_section(("templater", "dbt2")) or {}) if config else {}

    def _settings_key(self, settings: dict[str, Any]) -> str:
        return json.dumps(
            [settings, self.override_context], sort_keys=True, default=str
        )

    def sequence_files(
        self,
        fnames: list[str],
        config: FluffConfig | None = None,
        formatter: FormatterInterface | None = None,
    ) -> list[str]:
        """Compile selected files together, retaining artifacts for this pass only."""
        self._batch = None
        self._batch_error = None
        self._batch_key = None
        self._batch_paths = set()
        settings = self._settings(config)
        project = Path(settings.get("project_dir", ".")).expanduser().resolve()
        paths = [
            Path(name).resolve()
            for name in fnames
            if Path(name).is_file() and Path(name).resolve().is_relative_to(project)
        ]
        if paths:
            self._batch_key = self._settings_key(settings)
            self._batch_paths = set(paths)
            try:
                self._batch = self._compile(
                    settings, project, list(dict.fromkeys(paths)), formatter
                )
            except (SQLTemplaterError, SQLFluffUserError) as error:
                # Surface a failed batch through each file's normal render path,
                # rather than aborting the runner while it sequences files.
                self._batch_error = error
            except (
                OSError,
                subprocess.SubprocessError,
                UnicodeError,
                json.JSONDecodeError,
            ) as error:
                self._batch_error = SQLTemplaterError(
                    f"dbt2 trace export failed: {error}"
                )
        return fnames

    @large_file_check
    def process(
        self,
        *,
        in_str: str,
        fname: str,
        config: FluffConfig | None = None,
        formatter: FormatterInterface | None = None,
    ) -> tuple[TemplatedFile, list[SQLTemplaterError]]:
        """Compile on-disk SQL with upstream dbt and consume its trace sidecar."""
        settings = self._settings(config)
        try:
            trace = self._runtime(in_str, fname, settings, formatter)
            return trace_to_templated_file(trace, in_str, fname), []
        except (
            OSError,
            subprocess.SubprocessError,
            UnicodeError,
            json.JSONDecodeError,
        ) as error:
            raise SQLTemplaterError(f"dbt2 trace export failed: {error}") from error

    @staticmethod
    def _execute(command: list[str], timeout: int) -> str:
        result = subprocess.run(
            command,
            capture_output=True,
            encoding="utf-8",
            errors="strict",
            timeout=timeout,
        )
        for stream, output in (("stdout", result.stdout), ("stderr", result.stderr)):
            if output:
                templater_logger.debug("dbt2 %s:\n%s", stream, output.rstrip())
        if result.returncode:
            raise SQLTemplaterError(
                f"dbt exited {result.returncode}:\n"
                f"{result.stderr[-8000:]}\n{result.stdout[-8000:]}\n"
                f"This experimental templater needs the trace API from {TRACE_PR}."
            )
        return result.stdout

    def _command(self, settings: dict[str, Any]) -> list[str]:
        """Use this interpreter's dbt, or an explicitly selected external CLI."""
        if executable := settings.get("runtime_path"):
            command = [str(executable)]
            output = self._execute(
                command + ["--version"], int(settings.get("timeout", 300))
            )
            match = re.search(
                r"(?im)^\s*(?:dbt(?:-oss|-core|-fusion)?\s+|\-\s*installed:\s*)"
                r"(\d+\.\d+[^\s]*)",
                output,
            )
            if not match:
                raise SQLFluffUserError(f"Cannot identify dbt version: {output}")
            version = match.group(1)
        else:
            try:
                version = metadata.version("dbt-core")
            except metadata.PackageNotFoundError:
                raise SQLFluffUserError(
                    "Install a dbt-core v2 build with the render-trace API from "
                    f"{TRACE_PR}. No dbt runtime is bundled with this plugin."
                ) from None
            # Calling cli() explicitly also works when dbt.cli.main has no __main__.
            command = [sys.executable, "-c", "from dbt.cli.main import cli; cli()"]
        if Version(version).major < 2:
            raise SQLFluffUserError(LEGACY_DBT)
        return command

    def _runtime(
        self,
        source: str,
        fname: str,
        settings: dict[str, Any],
        formatter: FormatterInterface | None = None,
    ) -> dict[str, Any]:
        path = Path(fname).resolve()
        if fname == "stdin" or not path.is_file():
            raise SQLTemplaterError("dbt2 requires an existing SQL model file")
        if normalize_newlines(path.read_text(encoding="utf-8")) != normalize_newlines(
            source
        ):
            raise SQLTemplaterError("dbt2 requires the current on-disk source")
        project = Path(settings.get("project_dir", ".")).expanduser().resolve()
        try:
            path.relative_to(project)
        except ValueError as error:
            raise SQLTemplaterError("Model must be inside dbt2 project_dir") from error

        if (
            self._batch_key == self._settings_key(settings)
            and path in self._batch_paths
        ):
            if self._batch_error is not None:
                raise self._batch_error
            if self._batch is not None:
                templater_logger.debug("Using batched dbt2 render trace for %s", path)
                return self._batch.trace_for(path, source)
        return self._compile(settings, project, [path], formatter).trace_for(
            path, source
        )

    def _compile(
        self,
        settings: dict[str, Any],
        project: Path,
        paths: list[Path],
        formatter: FormatterInterface | None = None,
    ) -> RenderArtifacts:
        """Report progress through the CLI's existing output policy."""
        # Compilation headers are an optional extension to FormatterInterface,
        # used by the legacy dbt templater and SQLFluff's CLI formatter.
        dispatch_header = getattr(formatter, "dispatch_compilation_header", None)
        if dispatch_header:
            dispatch_header("dbt2 templater", "Compiling dbt project...")
        templater_logger.debug(
            "Compiling dbt2 project %s for %d selected files", project, len(paths)
        )
        try:
            artifacts = self._compile_project(settings, project, paths)
        except Exception:
            if dispatch_header:
                dispatch_header("dbt2 templater", "Compilation Failed.")
            raise
        templater_logger.debug(
            "Loaded dbt2 render artifacts for %d source files", len(artifacts.traces)
        )
        if dispatch_header:
            dispatch_header("dbt2 templater", "Project Compiled.")
        return artifacts

    def _compile_project(
        self, settings: dict[str, Any], project: Path, paths: list[Path]
    ) -> RenderArtifacts:
        """Invoke dbt once and load all emitted JSON before deleting temporary files."""
        command = self._command(settings)
        with tempfile.TemporaryDirectory(prefix="sqlfluff-dbt2-") as temporary:
            target = Path(temporary) / "target"
            command += [
                "compile",
                "--project-dir",
                str(project),
                "--target-path",
                str(target),
                "--log-path",
                str(Path(temporary) / "logs"),
                "--select",
                *[f"path:{path.relative_to(project).as_posix()}" for path in paths],
                "--feature",
                "write_render_trace",
            ]
            for key in ("profiles_dir", "profile", "target"):
                if settings.get(key):
                    value = str(settings[key])
                    if key == "profiles_dir":
                        value = str(Path(value).expanduser().resolve())
                    command.extend(["--" + key.replace("_", "-"), value])
            context = {**settings.get("context", {}), **self.override_context}
            if context:
                command.extend(["--vars", json.dumps(context)])
            self._execute(command, int(settings.get("timeout", 300)))
            return RenderArtifacts.load(target, project)

    @staticmethod
    def _read_trace(
        target: Path, project: Path, model: Path, source: str
    ) -> dict[str, Any]:
        """Read and validate a single model from a completed invocation."""
        return RenderArtifacts.load(target, project).trace_for(model, source)
