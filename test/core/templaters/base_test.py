"""Tests for templaters."""

import pytest

from sqlfluff.core.templaters import (
    RawTemplater,
    templater_selector,
    PythonTemplater,
    JinjaTemplater,
)


def test__templater_selection():
    """Test template selection by name."""
    assert templater_selector().__class__ is JinjaTemplater
    assert templater_selector("raw").__class__ is RawTemplater
    assert templater_selector("python").__class__ is PythonTemplater
    assert templater_selector("jinja").__class__ is JinjaTemplater
    with pytest.raises(ValueError):
        templater_selector("afefhlsakufe")


def test__templater_raw():
    """Test the raw templater."""
    t = RawTemplater()
    instr = "SELECT * FROM {{blah}}"
    outstr, _ = t.process(instr)
    assert instr == str(outstr)
