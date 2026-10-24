"""Select the correct templater before importing incompatible dbt internals."""

from importlib import metadata

import pytest

from sqlfluff.core.errors import SQLFluffUserError
from sqlfluff_templater_dbt.templater import DbtTemplater


@pytest.mark.parametrize("version", ["2.0.0rc9", "2.0.8", "3.0.0"])
def test_dbt2_signpost(version, monkeypatch):
    """A Rust dbt install produces actionable guidance rather than an import failure."""
    monkeypatch.setattr(metadata, "version", lambda _: version)
    with pytest.raises(
        SQLFluffUserError, match="sqlfluff-templater-dbt2 and set templater = dbt2"
    ):
        DbtTemplater()


@pytest.mark.parametrize("version", ["1.4.1", "1.10.15", "1.11.0rc1"])
def test_legacy_dbt_still_constructs(version, monkeypatch):
    """Retain lazy imports and the supported Python dbt initialization path."""
    monkeypatch.setattr(metadata, "version", lambda _: version)
    assert DbtTemplater().name == "dbt"


def test_missing_dbt_keeps_lazy_imports(monkeypatch):
    """Let the existing missing-dbt path handle an absent distribution."""

    def missing(_):
        raise metadata.PackageNotFoundError("dbt-core")

    monkeypatch.setattr(metadata, "version", missing)
    assert DbtTemplater().name == "dbt"
