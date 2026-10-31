"""Load a compilation's manifest and source-indexed render artifacts once."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sqlfluff.core.errors import SQLFluffSkipFile, SQLTemplaterError
from sqlfluff_templater_dbt2.trace import normalize_newlines


@dataclass
class RenderArtifacts:
    """A successful invocation's in-memory artifacts, scoped to one lint pass."""

    project: Path
    manifest: dict[str, Any]
    traces: dict[Path, list[dict[str, Any]]]

    @classmethod
    def load(cls, target: Path, project: Path) -> RenderArtifacts:
        """Read JSON once before disposing of the compilation's temporary output."""
        manifest_path = target / "manifest.json"
        if not manifest_path.is_file():
            raise SQLTemplaterError("dbt2 trace has no matching invocation manifest")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if (
            not isinstance(manifest, dict)
            or not isinstance(manifest.get("nodes"), dict)
            or not isinstance(manifest.get("metadata"), dict)
        ):
            raise SQLTemplaterError("Invalid dbt2 invocation manifest")
        traces: dict[Path, list[dict[str, Any]]] = {}
        for artifact in target.rglob("*.render_trace.json"):
            trace = json.loads(artifact.read_text(encoding="utf-8"))
            if not isinstance(trace, dict) or not isinstance(
                trace.get("source_path"), str
            ):
                raise SQLTemplaterError("Invalid dbt2 trace source identity")
            path = Path(trace["source_path"])
            if not path.is_absolute():
                path = project / path
            traces.setdefault(path.resolve(), []).append(trace)
        return cls(project, manifest, traces)

    def trace_for(self, model: Path, source: str) -> dict[str, Any]:
        """Verify identity and exact source for each file served from the batch."""
        candidates = self.traces.get(model, [])
        if not candidates and self._is_disabled(model):
            raise SQLFluffSkipFile(f"Skipped disabled dbt model: {model}")
        if len(candidates) != 1:
            raise SQLTemplaterError(
                "dbt did not export exactly one render trace for this source file. "
                "Use a build containing https://github.com/dbt-labs/dbt/pull/16870. "
                "Rewritten snapshot inputs are not supported by this reference "
                "implementation."
            )
        trace = candidates[0]
        if not isinstance(trace.get("unique_id"), str):
            raise SQLTemplaterError("Invalid dbt2 model identity")
        node = self.manifest["nodes"].get(trace["unique_id"], {})
        if (
            not isinstance(node, dict)
            or not isinstance(node.get("original_file_path"), str)
            or not isinstance(trace.get("invocation_id"), str)
            or not trace["invocation_id"]
            or trace["invocation_id"] != self.manifest["metadata"].get("invocation_id")
            or Path(node["original_file_path"]).as_posix()
            != model.relative_to(self.project).as_posix()
        ):
            raise SQLTemplaterError(
                "dbt2 trace model/invocation identity does not match"
            )
        if not isinstance(trace.get("source"), str) or normalize_newlines(
            trace["source"]
        ) != normalize_newlines(source):
            raise SQLTemplaterError("dbt2 source differs from the compiled source")
        return trace

    def _is_disabled(self, model: Path) -> bool:
        """Only an explicit disabled manifest entry can explain an absent trace."""
        disabled = self.manifest.get("disabled", {})
        if not isinstance(disabled, dict):
            raise SQLTemplaterError("Invalid dbt2 disabled-node metadata")
        for nodes in disabled.values():
            if not isinstance(nodes, list):
                continue
            for node in nodes:
                if (
                    isinstance(node, dict)
                    and isinstance(node.get("original_file_path"), str)
                    and isinstance(node.get("config"), dict)
                    and node["config"].get("enabled") is False
                    and (self.project / node["original_file_path"]).resolve() == model
                ):
                    return True
        return False
