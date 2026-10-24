"""Consume the experimental render-trace API proposed in dbt-labs/dbt#16870."""

from __future__ import annotations

import json
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
from sqlfluff_templater_dbt2.trace import normalize_newlines, trace_to_templated_file

if TYPE_CHECKING:
    from sqlfluff.core import FluffConfig
    from sqlfluff.core.formatter import FormatterInterface

TRACE_PR = "https://github.com/dbt-labs/dbt/pull/16870"
LEGACY_DBT = (
    "The dbt2 templater requires the Rust dbt v2 runtime. For legacy Python "
    "dbt Core 1.x, install sqlfluff-templater-dbt and set templater = dbt."
)


class Dbt2Templater(RawTemplater):
    """Render through dbt itself and translate its exported execution provenance."""

    name = "dbt2"
    templates_in_worker = False

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
        settings = (
            (config.get_section(("templater", self.name)) or {}) if config else {}
        )
        try:
            trace = self._runtime(in_str, fname, settings)
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
        self, source: str, fname: str, settings: dict[str, Any]
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
            relative = path.relative_to(project).as_posix()
        except ValueError as error:
            raise SQLTemplaterError("Model must be inside dbt2 project_dir") from error

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
                f"path:{relative}",
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
            return self._read_trace(target, project, path, source)

    @staticmethod
    def _read_trace(
        target: Path, project: Path, model: Path, source: str
    ) -> dict[str, Any]:
        """Check source and invocation identity before exposing writable mappings."""
        candidates = []
        for artifact in target.rglob("*.render_trace.json"):
            trace = json.loads(artifact.read_text(encoding="utf-8"))
            if not isinstance(trace, dict) or not isinstance(
                trace.get("source_path"), str
            ):
                raise SQLTemplaterError("Invalid dbt2 trace source identity")
            trace_path = Path(trace["source_path"])
            if not trace_path.is_absolute():
                trace_path = project / trace_path
            if trace_path.resolve() == model:
                candidates.append(trace)
        if len(candidates) != 1:
            raise SQLTemplaterError(
                "dbt did not export exactly one render trace for this source file. "
                f"Use a build containing {TRACE_PR}. Disabled models and rewritten "
                "snapshot inputs are not supported by this reference implementation."
            )
        trace = candidates[0]
        manifest_path = target / "manifest.json"
        if not manifest_path.is_file():
            raise SQLTemplaterError("dbt2 trace has no matching invocation manifest")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if not isinstance(manifest, dict) or not isinstance(
            manifest.get("nodes"), dict
        ):
            raise SQLTemplaterError("Invalid dbt2 invocation manifest")
        if not isinstance(trace.get("unique_id"), str):
            raise SQLTemplaterError("Invalid dbt2 model identity")
        node = manifest.get("nodes", {}).get(trace.get("unique_id"), {})
        if (
            not isinstance(node, dict)
            or not isinstance(node.get("original_file_path"), str)
            or not isinstance(manifest.get("metadata"), dict)
            or not trace.get("invocation_id")
            or trace["invocation_id"]
            != manifest.get("metadata", {}).get("invocation_id")
            or Path(node["original_file_path"]).as_posix()
            != model.relative_to(project).as_posix()
        ):
            raise SQLTemplaterError(
                "dbt2 trace model/invocation identity does not match"
            )
        if not isinstance(trace.get("source"), str) or normalize_newlines(
            trace["source"]
        ) != normalize_newlines(source):
            raise SQLTemplaterError("dbt2 source differs from the compiled source")
        return trace
