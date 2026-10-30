"""Record real artifacts from dbt-labs/dbt#16870 for Python-only regression tests."""

import json
import shutil
import tempfile
from pathlib import Path

from sqlfluff_templater_dbt2.templater import Dbt2Templater

ROOT = Path(__file__).resolve().parents[1]
CASES = {
    "literal": ("select 1\n", {}),
    "expression": ("select {{ var('value') }} as x from t\n", {"value": 42}),
    "branch_true": (
        "{% if var('flag') %}select 1{% else %}select 1{% endif %}\n",
        {"flag": True},
    ),
    "branch_false": (
        "{% if var('flag') %}select 1{% else %}select 1{% endif %}\n",
        {"flag": False},
    ),
    "loop": ("{% for n in [1,2,3] %}select {{ n }} as x;\n{% endfor %}", {}),
    "skipped_loop": (
        "{% for n in [] %}select {{ n }}{% else %}select 0{% endfor %}\n",
        {},
    ),
    "capture": ("{% set query %}select 1{% endset %}{{ query }}\n", {}),
    "inline_macro": (
        "{% macro col() %}lower(a){% endmacro %}select {{ col() }} from t\n",
        {},
    ),
    "external_macro": ("select {{ probe_value(42) }}\n", {}),
    "unicode_crlf": (
        "select 'é😀' as {{ var('column') }}\r\nfrom t\r\n",
        {"column": "café"},
    ),
    "whitespace": ("select {{- ' 1 ' -}}\n", {}),
    "comment": ("{# hidden #}select 1 -- noqa: CP01\n", {}),
    "layout": (
        "select\n{% for col in ['a','b'] %}    {{ col }} as {{ col }}"
        "{% if not loop.last %},{% endif %}\n{% endfor %}from t\n",
        {},
    ),
    "continued": (
        "{% for n in [1, 2] %}{% if n > 0 %}select {{ n }};{% continue %}{% endif %}{% endfor %}select 9\n",
        {},
    ),
    "broken": (
        "{% for n in [1, 2] %}{% if n > 0 %}select {{ n }};{% break %}{% endif %}{% else %}select 0{% endfor %}select 9\n",
        {},
    ),
    "returned": ("select 0 {{ return('select 1') }}\n", {}),
    "block_returned": (
        "select {% block columns %}0{{ return('1') }}{% endblock %} as n\n",
        {},
    ),
}


def main() -> None:
    """Regenerate event data without using Python Jinja to render anything."""
    smoke = ROOT / ".smoke"
    smoke.mkdir(exist_ok=True)
    tempfile.tempdir = str(smoke)
    traces = {}
    with tempfile.TemporaryDirectory(prefix="record-") as temporary:
        project = Path(temporary)
        shutil.copytree(ROOT / "test/fixtures/project", project, dirs_exist_ok=True)
        model = project / "models/probe.sql"
        cases = {**CASES, "project": (model.read_text(encoding="utf-8"), {})}
        for name, (source, context) in cases.items():
            model.write_text(source, encoding="utf-8", newline="")
            trace = Dbt2Templater()._runtime(
                source,
                str(model),
                {
                    "project_dir": str(project),
                    "profiles_dir": str(project),
                    "context": context,
                },
            )
            # Only producer identity is made portable. Source, output, event
            # kinds, ordering and byte offsets are exactly what dbt exported.
            trace["filename"] = trace["source_path"] = "models/probe.sql"
            trace["invocation_id"] = "00000000-0000-4000-8000-000000000001"
            traces[name] = trace
    destination = ROOT / "test/fixtures/traces.json"
    destination.write_text(
        json.dumps(traces, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Recorded {len(traces)} traces in {destination}")


if __name__ == "__main__":
    main()
