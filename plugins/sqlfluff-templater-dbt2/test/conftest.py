"""Recorded upstream artifacts keep ordinary tests independent of a dbt install."""

import copy
import json
from pathlib import Path

import pytest


@pytest.fixture
def traces():
    """Load real traces captured by scripts/record_traces.py."""
    path = Path(__file__).parent / "fixtures/traces.json"
    return copy.deepcopy(json.loads(path.read_text(encoding="utf-8")))
